"""Freeze cached exposed DEV15 outputs and validate one common blind reassessment.

No generation, training, protected-answer access, or historical record mutation.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import random
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts import prepare_blind_dev_assisted as prep
from scripts import score_blind_dev_assisted as score

OUT = ROOT / 'resources/local/dev-comparability-20261003'
DEV = 'experiments/dev-diagnostic-20260927'
CORRECTED = 'experiments/corrected-review-20260930/lead-only/raw'
DOSE = 'experiments/dose-acquisition-20260930/live-execution/recovered/dose'
IDS = tuple('QUALITYDEV1-' + x for x in
            ('002','003','005','006','007','008','009','010','012','013','014','015','017','020','021'))
SPECS = [(f'original_{a}', DEV + '/predictions.jsonl', 'condition', a, DEV + '/run.json',
          'base' if a in ('D0','D1') else 'step312', 'BF16') for a in ('D0','D1','D2','D3')] + [
    ('step280_plain', CORRECTED + '/gemma280/predictions.jsonl', 'condition', 'plain', CORRECTED + '/gemma280/run.json', 'step280', 'BF16'),
    ('step280_assisted', CORRECTED + '/gemma280/predictions.jsonl', 'condition', 'assisted', CORRECTED + '/gemma280/run.json', 'step280', 'BF16'),
    ('mixed96', CORRECTED + '/mixed96_plain/mixed/evaluation/predictions.jsonl', 'arm', 'candidate', CORRECTED + '/mixed96_plain/mixed/evaluation/run.json', 'step280+mixed96', 'BF16 reload'),
    ('corrected96', CORRECTED + '/corrected96_plain/mixed/evaluation/predictions.jsonl', 'arm', 'candidate', CORRECTED + '/corrected96_plain/mixed/evaluation/run.json', 'step280+corrected96', 'BF16 reload'),
    ('dose_baseline_nf4', DOSE + '/evaluation-baseline/predictions.jsonl', 'arm', 'reference', DOSE + '/run.json', 'step280', 'NF4; nonquantized FP32; BF16 compute/autocast'),
    ('dose384_nf4', DOSE + '/evaluation/predictions.jsonl', 'arm', 'dose384', DOSE + '/run.json', 'step280+dose384', 'NF4; nonquantized FP32; BF16 compute/autocast')]
REF_KEYS = ('translations','edition','notes','reference_screen','expert_adjudicated')

def read(path):
    return json.loads((ROOT / path).read_bytes())

def rows(path):
    return prep.decode_lines((ROOT / path).read_bytes())

def digest(value):
    return prep.sha(prep.json_bytes(value))

def prepare():
    contract = read('experiments/dev-assisted-qualified-20260927/uniform-evaluation-contract.json')
    inputs = prep.unique(rows(DEV + '/inputs.jsonl'))
    refs = prep.unique(rows(DEV + '/references.jsonl'))
    assessments = prep.unique(read(DEV + '/assessment-contract.json')['cases'])
    prep.require(set(IDS) == {k for k,v in assessments.items() if v['assessment']=='provisional_whole_translation'}, 'DEV15 identities changed')
    pins = {}
    for path in (DEV+'/inputs.jsonl', DEV+'/references.jsonl', DEV+'/assessment-contract.json', DEV+'/reviewer-clarification.json'):
        pins[path] = prep.sha((ROOT / path).read_bytes())
        prep.require(pins[path] == contract['source_files_sha256'][path], 'Frozen DEV evidence changed: '+path)
    # Original literal prompts are reconstructed from the run's saved instructions;
    # later literal prompts are saved in its run; recorded token hashes stay distinct.
    later = read(CORRECTED + '/gemma280/run.json')
    saved = prep.unique(later['prompts'])
    dose_messages = {r['case_id']:r['messages'] for r in rows('experiments/dose-acquisition-20260930/inputs.jsonl') if r['case_id'] in IDS}
    groups, members = {}, []
    for arm,path,key,value,runpath,checkpoint,precision in SPECS:
        run = read(runpath)
        for pin in (path,runpath):
            pins[pin] = prep.sha((ROOT / pin).read_bytes())
        selected = [r for r in rows(path) if r.get(key)==value and r['case_id'] in IDS]
        prep.require(len(selected)==15 and {r['case_id'] for r in selected}==set(IDS), 'Arm coverage differs: '+arm)
        for r in selected:
            cid = r['case_id']; ref=refs[cid]; assessment=assessments[cid]
            prep.require(ref['source_text']==inputs[cid]['source_text'], 'Source/reference mismatch')
            text = r['text']; output_sha = prep.sha(text.encode('utf8'))
            prep.require(r['status']=='success' and not r.get('hit_output_cap_without_eos'), 'Noncomplete output: '+r['id'])
            prep.require(r.get('output_sha256',output_sha)==output_sha, 'Output hash mismatch')
            item = {'source_text': inputs[cid]['source_text'], 'references':{k:ref[k] for k in REF_KEYS},
                    'assessment':assessment['assessment'], 'constraint':assessment['constraint'],
                    'execution_status':r['status'],'output_text':text,'output_sha256':output_sha}
            group = digest(item)
            groups.setdefault(group,item)
            if arm.startswith('original_'):
                instruction = run['conditions'][value][1]
                msgs = ([{'role':'user','content':run['training_prompt'].format(text=inputs[cid]['source_text'])}]
                        if instruction=='training' else [{'role':'system','content':run['evaluation_system']},{'role':'user','content':inputs[cid]['source_text']}])
                prompt_kind='original_'+instruction
            else:
                prompt_kind='later_'+('assisted' if value=='assisted' else 'plain')
                p=saved[cid+':'+('assisted' if value=='assisted' else 'plain')]
                prep.require(p['rendered_input_ids_sha256']==r['rendered_input_ids_sha256'], 'Later prompt hash mismatch')
                msgs=p['messages']
                if arm.startswith('dose_') or arm=='dose384_nf4':
                    prep.require(msgs==dose_messages[cid], 'Dose literal messages differ')
            members.append({'arm':arm,'case_id':cid,'record_id':inputs[cid]['record_id'],'work_id':inputs[cid]['work_id'],
                'edition':ref['edition'],'locator':ref['locator'],'reference_sha256':digest(item['references']),
                'constraint_sha256':digest(assessment),'context_output_sha256':group,'output_sha256':output_sha,
                'prediction_file':path,'prediction_id':r['id'],'run_file':runpath,'checkpoint':checkpoint,'precision':precision,
                'model_id':run['model_id'],'model_revision':run['model_revision'],
                'prompt_kind':prompt_kind,'messages':msgs,'messages_sha256':digest(msgs),
                'rendered_input_ids_sha256':r['rendered_input_ids_sha256'],'input_tokens':r['input_tokens'],
                'tokenizer_files':run.get('tokenizer_files',later['tokenizer_files']),
                'generation':{'decoding':'greedy','seed':42,'enable_thinking':False,'max_new_tokens':4096,'max_generation_seconds':1200},
                'runtime':run.get('runtime',run.get('environment')),
                'status':r['status'],'hit_output_cap_without_eos':r.get('hit_output_cap_without_eos',False)})
    prep.require(len(members)==150 and len(groups)==143,'Context-aware deduplication changed')
    files = {'lead-only/members.jsonl':prep.lines(members)}
    mapping=[]
    for reviewer,seed in [('A',2026100301),('B',2026100302)]:
        keys=sorted(groups);random.Random(seed).shuffle(keys)
        packet=[]
        for index,key in enumerate(keys,1):
            rid=f'{reviewer}{index:03d}';packet.append({'review_id':rid,**groups[key]})
            mapping.append({'reviewer':reviewer,'review_id':rid,'context_output_sha256':key})
        files[f'reviewer-{reviewer}/packet.jsonl']=prep.lines(packet)
        instructions=prep.instructions().decode('utf8').replace('all 96 opaque records','all 143 opaque records')
        files[f'reviewer-{reviewer}/INSTRUCTIONS.md']=instructions.encode('utf8')
    files['lead-only/mapping.jsonl']=prep.lines(mapping)
    pins.update({str(Path(prep.__file__).relative_to(ROOT)).replace('\\','/'):prep.sha(Path(prep.__file__).read_bytes()),
                 str(Path(score.__file__).relative_to(ROOT)).replace('\\','/'):prep.sha(Path(score.__file__).read_bytes()),
                 str(Path(__file__).relative_to(ROOT)).replace('\\','/'):prep.sha(Path(__file__).read_bytes())})
    freeze={'status':'frozen_before_review','scope':'exposed DEV15 only; one reassessment; no new generation',
            'case_ids':IDS,'members':150,'unique_context_outputs':143,'whole_work_counts':dict(Counter(inputs[i]['work_id'] for i in IDS)),
            'source_pins':pins,'files':{name:prep.sha(data) for name,data in files.items()},
            'rubric':'unchanged meaning rubric; current critical-consistency validator; historical pins untouched',
            'expert_adjudicated':False,'review_independence':'separate fresh AI contexts; not independent linguistic certification'}
    files['freeze.json']=prep.json_bytes(freeze)
    return files

def check(directory):
    directory=Path(directory); expected=prepare()
    for name,data in expected.items():
        prep.require((directory/name).read_bytes()==data,'Frozen artifact differs: '+name)
    return read_local(directory/'freeze.json')

def read_local(path):
    return json.loads(path.read_bytes())

def summarize(directory):
    directory=Path(directory);freeze=check(directory)
    members=prep.decode_lines((directory/'lead-only/members.jsonl').read_bytes())
    mapping=prep.decode_lines((directory/'lead-only/mapping.jsonl').read_bytes())
    result={'freeze_sha256':prep.sha((directory/'freeze.json').read_bytes()),'reviewers':{},'paired':{},'expert_adjudicated':False}
    by_reviewer={};span_rows=[]
    for reviewer in ('A','B'):
        packet=prep.decode_lines((directory/f'reviewer-{reviewer}/packet.jsonl').read_bytes())
        raw=(directory/f'reviewer-{reviewer}/reviews.jsonl').read_bytes()
        ratings=score.validate_reviews(packet,prep.decode_lines(raw),expected_count=143)
        lookup={m['context_output_sha256']:ratings[m['review_id']] for m in mapping if m['reviewer']==reviewer}
        by_reviewer[reviewer]=lookup
        counts={}
        for arm,*_ in SPECS:
            selected=[m for m in members if m['arm']==arm]
            counts[arm]={'denominator':len(selected),'judgments':dict(Counter(lookup[m['context_output_sha256']]['judgment'] for m in selected))}
        result['reviewers'][reviewer]={'raw_reviews_sha256':prep.sha(raw),'counts':counts}
        packets=prep.unique(packet,'review_id')
        for rid,r in ratings.items():
            span=r['output_span'];start=packets[rid]['output_text'].find(span) if span else None
            span_rows.append({'reviewer':reviewer,'review_id':rid,'output_sha256':r['output_sha256'],'span':span,'start':start,'end':start+len(span) if span else None,'offset_unit':'Unicode code points; first literal occurrence'})
        for a,b in [('original_D0','original_D1'),('original_D0','original_D2'),('original_D1','original_D3'),('original_D2','original_D3'),('step280_plain','step280_assisted'),('step280_plain','mixed96'),('step280_plain','corrected96'),('mixed96','corrected96'),('step280_plain','dose_baseline_nf4'),('dose_baseline_nf4','dose384_nf4')]:
            arms={arm:{m['case_id']:m for m in members if m['arm']==arm} for arm in (a,b)}
            keys=sorted(arms[a].keys() & arms[b].keys())
            transitions=Counter((lookup[arms[a][i]['context_output_sha256']]['judgment'],lookup[arms[b][i]['context_output_sha256']]['judgment']) for i in keys)
            gain=[i for i in keys if lookup[arms[a][i]['context_output_sha256']]['judgment']!='accepted' and lookup[arms[b][i]['context_output_sha256']]['judgment']=='accepted']
            loss=[i for i in keys if lookup[arms[a][i]['context_output_sha256']]['judgment']=='accepted' and lookup[arms[b][i]['context_output_sha256']]['judgment']!='accepted']
            result['paired'][f'{reviewer}:{a}->{b}']={'denominator':len(keys),'transitions':[{'before':x,'after':y,'count':n} for (x,y),n in sorted(transitions.items())],'new_acceptance_ids':gain,'lost_acceptance_ids':loss,'net_acceptance':len(gain)-len(loss),'generation_confounds_not_removed':True}
    result['unique_output_disagreements']=[{'context_output_sha256':k,'A':by_reviewer['A'][k]['judgment'],'B':by_reviewer['B'][k]['judgment']} for k in by_reviewer['A'] if by_reviewer['A'][k]['judgment']!=by_reviewer['B'][k]['judgment']]
    return result,span_rows

def main():
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['prepare','check','summarize']);parser.add_argument('--directory',type=Path,default=OUT)
    args=parser.parse_args()
    if args.action=='prepare':
        for name,data in prepare().items():
            path=args.directory/name;path.parent.mkdir(parents=True,exist_ok=True)
            if path.exists():prep.require(path.read_bytes()==data,'Refusing to replace frozen artifact: '+name)
            else:path.write_bytes(data)
        print('Prepared 150 memberships / 143 unique context outputs for two independent blind reviews')
    elif args.action=='check':
        print(json.dumps(check(args.directory),ensure_ascii=False))
    else:
        result,spans=summarize(args.directory)
        (args.directory/'summary.json').write_bytes(prep.json_bytes(result))
        (args.directory/'span-offsets.jsonl').write_bytes(prep.lines(spans))
        print(json.dumps(result,ensure_ascii=False))

if __name__=='__main__':main()
