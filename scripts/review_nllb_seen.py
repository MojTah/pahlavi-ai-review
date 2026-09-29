"""Local likelihood analysis and blind TRAIN20 review; no model inference or quality promotion."""
import argparse
from collections import Counter
import json
import math
from pathlib import Path
import random
import statistics
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.append(str(ROOT/'resources/local/hf-client-venv/Lib/site-packages'))
from cloud_pilot import nllb_seen as runtime, hf_nllb_seen as pilot
from scripts import review_train_recall as recall, score_blind_dev_assisted as meaning
from scripts.prepare_blind_dev_assisted import require, sha, json_bytes, lines, decode_lines, unique, write_fresh

EXP = ROOT/'experiments/nllb-seen-20260928/execution'
PACKAGE = ROOT/'resources/local/nllb-seen-20260928/package-staging'
PACKAGE_SHA = 'c57c25f27ef023d139ae939d3e9c56f8ec8408ed9586de20dd94dacce9a8195e'
PACKAGE_MANIFEST_SHA = 'e8baa7636bf51ac4e821859e2016178f453afcb9e48eb886bbc08926a954a4a3'
RUNTIME_SHA = '9a582bcb82a771f5f2a0debc4dd823e618d3dc82f8394234f4182a6a4f07763e'
APPROVED_PACKAGES = {PACKAGE_SHA: dict(manifest_sha256=PACKAGE_MANIFEST_SHA, runner_sha256=RUNTIME_SHA)}
APPROVED_PACKAGES['e7a63808e2e081ca053211804512ec6850bf4a4bea957fdfbe9af67f24cd1733'] = dict(
    manifest_sha256='b967694343bf4dddab48ac3c701b9b9ace5eb1cd8ae50b28fdab03e64ceaec4e',
    runner_sha256='0477faeb52b2639e5121afc0e649b3c32bb471f4343b2803967115a37574a585')
SEEDS = {'A': 2026092811, 'B': 2026092812}
SMALL = {'status.json','package-manifest.json','driver.log','seen/run.json','seen/schedule.json',
         'seen/likelihood.jsonl','seen/predictions.jsonl','seen/canary.json'}


def close(a, b):
    return math.isclose(a, b, rel_tol=1e-9, abs_tol=1e-9)


def check_metrics(row, tokens, batch=1):
    counts = dict(supervised_tokens=tokens, content_tokens=tokens-2*batch,
        control_tokens=2*batch, tokens_per_control=batch)
    require(tokens > 2*batch and all(type(row.get(k)) is int and row[k] == v for k,v in counts.items()),
        'Target/content/control denominators differ')
    fields = ('sum_nll','mean_nll','reference_mean_nll','reference_absolute_difference',
        'native_mean_nll','native_absolute_difference','content_sum_nll',
        'content_mean_nll','control_sum_nll','language_tag_sum_nll','eos_sum_nll')
    require(all(type(row.get(k)) in (int,float) and math.isfinite(row[k]) and row[k] >= 0 for k in fields),
        'Nonfinite/negative likelihood metric')
    require(close(row['sum_nll']/tokens,row['mean_nll'])
        and close(row['content_sum_nll']/counts['content_tokens'],row['content_mean_nll'])
        and close(row['sum_nll'],row['content_sum_nll']+row['control_sum_nll'])
        and close(row['control_sum_nll'],row['language_tag_sum_nll']+row['eos_sum_nll'])
        and close(row['native_absolute_difference'],abs(row['mean_nll']-row['native_mean_nll']))
        and close(row['reference_absolute_difference'],abs(row['mean_nll']-row['reference_mean_nll']))
        and row.get('reference_precision') == 'float32_logits'
        and isinstance(row.get('native_loss_dtype'),str) and bool(row['native_loss_dtype'].strip())
        and math.isclose(row['mean_nll'],row['reference_mean_nll'],rel_tol=1e-5,abs_tol=1e-5),
        'Likelihood arithmetic/FP32 reference calibration differs')


def validate_records(run, likelihood, predictions, token_map, canary):
    rows = token_map['rows']; by_id = unique(rows)
    require(len(rows) == 20 and len({r['work_id'] for r in rows}) == 16, 'Fixed TRAIN20/16 works differ')
    schedule = runtime.call_schedule(rows)
    records = likelihood+predictions
    unique(records)
    require(len(likelihood) <= 40 and len(predictions) <= 20
        and (not predictions or len(likelihood) == 40)
        and [r['id'] for r in records] == [c['id'] for c in schedule[:len(records)]], 'First-attempt prefix differs')
    require(run.get('completed_call_ids') == [r['id'] for r in records]
        and run.get('unattempted_call_ids') == [c['id'] for c in schedule[len(records):]], 'Run attempt counters differ')
    require(run.get('completed_likelihood_calls') == len(likelihood)
        and run.get('completed_generation_calls') == len(predictions)
        and run.get('generation_failures') == sum(r['status'] != 'success' for r in predictions), 'Completed counts differ')
    require(run.get('status') in {'completed','incomplete'}, 'Unfinished runtime state')
    complete = run['status'] == 'completed'
    require(run.get('all_first_attempts_recorded') is complete and (not complete or len(records) == 60), 'False completion claim')
    for i,(record,call) in enumerate(zip(records,schedule)):
        target,source = by_id[call['case_id']],by_id[call['source_parent_id']]
        require(all(record.get(k) == v for k,v in call.items()), 'Call identity/condition/order differs')
        bindings = dict(record_id=target['record_id'],work_id=target['work_id'],input_sha256=source['source_sha256'],
            target_sha256=target['target_sha256'],source_record_id=source['record_id'],source_work_id=source['work_id'],
            source_tokens=len(source['input_ids']),target_tokens=len(target['labels']))
        require(all(record.get(k) == v for k,v in bindings.items()), 'Source/target token binding differs')
        require(type(record.get('seconds')) in (int,float) and math.isfinite(record['seconds']) and record['seconds'] >= 0,
            'Invalid record timing')
        recall.first_attempt(record,record['id'])
        require(record.get('status') in {'success','failed'}, 'Unknown execution status')
        if record.get('error_type'):
            require(i == len(records)-1 and not complete and record['status'] == 'failed', 'Output after runtime failure')
        elif call['kind'] == 'likelihood':
            require(record['status'] == 'success', 'Failed likelihood lacks runtime reason')
            check_metrics(record,len(target['labels']))
        else:
            tokens,text = record.get('output_token_ids'),record.get('translation')
            require(isinstance(tokens,list) and 1 <= len(tokens) <= 513
                and all(type(t) is int and 0 <= t < 256215 for t in tokens) and tokens[0] == 2
                and isinstance(text,str), 'Invalid generated tokens/text')
            expected = runtime.generation_result(tokens,text)
            require(all(record.get(k) == v for k,v in expected.items()), 'Generation cap/EOS/empty outcome differs')
    if records:
        require(canary.get('status') == 'passed' and len(canary.get('checks',[])) == 2, 'Scored call without real canaries')
        for actual,(kind,selected) in zip(canary['checks'],runtime.canary_cases(rows)):
            require(actual.get('kind') == kind and actual.get('parent_ids') == [r['id'] for r in selected]
                and actual.get('scored') is False and actual.get('batch_size') == len(selected)
                and actual.get('padded_source_tokens') == max(len(r['input_ids']) for r in selected)
                and actual.get('padded_target_tokens') == max(len(r['labels']) for r in selected), 'Canary identity/shape differs')
            check_metrics(actual,sum(len(r['labels']) for r in selected),len(selected))
    return dict(status=run['status'],all_first_attempts_recorded=complete,scheduled_likelihood=40,
        scheduled_generations=20,recorded_likelihood=len(likelihood),recorded_generations=len(predictions),
        generation_failures=sum(r['status'] != 'success' for r in predictions),
        unattempted_call_ids=run['unattempted_call_ids'],readiness_passed=canary.get('status')=='passed',
        runtime_error={k:run[k] for k in ('error_type','error') if k in run},
        usable_for_translation_review=complete)


def load_evidence(execution=EXP, package=PACKAGE):
    execution,package = Path(execution),Path(package)
    raw = {}
    def get(name):
        raw[name] = (execution/name).read_bytes()
        return json.loads(raw[name])
    recovery,launch,manifest = get('recovery.json'),get('execution.json'),get('recovered/manifest.json')
    require(recovery.get('provider_inventory_committed') is True
        and recovery.get('manifest_sha256') == sha(raw['recovered/manifest.json'])
        and recovery.get('run_id') == launch.get('run_id') == manifest.get('run_id')
        and isinstance(launch.get('source_commit'),str) and len(launch['source_commit']) == 40, 'Recovery/launch identity differs')
    package_sha = manifest.get('package_sha256')
    require(package_sha in APPROVED_PACKAGES, 'Unapproved source package identity')
    identity = APPROVED_PACKAGES[package_sha]
    policy = dict(operation='nllb_seen',model=runtime.frozen.MODEL,revision=runtime.frozen.REVISION,
        package_sha256=package_sha,package_manifest_sha256=identity['manifest_sha256'],model_manifest_sha256=runtime.MANIFEST_SHA,
        token_map_sha256=pilot.TOKEN_MAP_SHA,train_sha256=runtime.frozen.TRAIN_SHA,inputs_sha256=runtime.INPUT_SHA,
        source_control_sha256=runtime.CONTROL_SHA,training_performed=False,quality_validated=False)
    require(all(manifest.get(k) == v for k,v in policy.items()), 'Frozen experiment identity differs')
    require(set(manifest['files']) <= SMALL and {'seen/run.json','seen/schedule.json','package-manifest.json','status.json'} <= set(manifest['files']),
        'Small evidence manifest differs')
    require(set(recovery.get('local_sha_verified_files',[])) == set(manifest['files']), 'Incomplete local recovery')
    require(sum(e['bytes'] for e in manifest['files'].values()) <= 16*1024**2, 'Unexpected evidence size')
    prefix = manifest['output_prefix']
    inventory = recovery['provider_inventory']
    require(set(inventory) == {prefix+'/manifest.json',*(prefix+'/'+n for n in manifest['files'])}, 'Provider inventory differs')
    require(inventory[prefix+'/manifest.json']['bytes'] == len(raw['recovered/manifest.json'])
        and bool(inventory[prefix+'/manifest.json']['xet_hash']), 'Uncommitted manifest')
    for name,entry in manifest['files'].items():
        data = (execution/'recovered'/name).read_bytes()
        require(len(data) == entry['bytes'] and sha(data) == entry['sha256']
            and inventory[prefix+'/'+name]['bytes'] == entry['bytes'] and bool(inventory[prefix+'/'+name]['xet_hash']),
            'Recovered artifact differs: '+name)
        raw['recovered/'+name] = data
    package_bytes = raw['recovered/package-manifest.json']
    require(sha(package_bytes) == identity['manifest_sha256']
        and (package.parent/'package-manifest.json').read_bytes() == package_bytes
        and runtime.frozen.sha(package.parent/'package.zip') == package_sha, 'Local/cloud package binding differs')
    package_manifest = json.loads(package_bytes)
    for name,entry in package_manifest['files'].items():
        require(Path(name).name == name, 'Unsafe package member')
        path = package/name
        require(path.stat().st_size == entry['bytes'] and runtime.frozen.sha(path) == entry['sha256'], 'Local package member differs: '+name)
    require(package_manifest['files']['nllb_seen.py']['sha256'] == identity['runner_sha256']
        and runtime.frozen.sha(runtime.__file__) in {v['runner_sha256'] for v in APPROVED_PACKAGES.values()},
        'Frozen scientific runner differs')
    status = json.loads(raw['recovered/status.json'])
    require(all(manifest.get(k) == v for k,v in status.items()), 'Manifest/status contradiction')
    token_map = json.loads((package/'token-map.json').read_bytes())
    raw['token-map.json'] = (package/'token-map.json').read_bytes()
    run = json.loads(raw['recovered/seen/run.json'])
    expected_files = json.loads((package/'model-manifest.json').read_bytes())['files']
    require(run.get('verified_inference_files') == {n:expected_files['nllb/model/'+n] for n in runtime.INFERENCE_FILES}, 'Loaded inference file identity differs')
    run_policy = dict(model=runtime.frozen.MODEL,revision=runtime.frozen.REVISION,trained_step=700,runner_sha256=identity['runner_sha256'],
        generation_settings=runtime.GENERATION,seed=3407,precision='FP32_parameters_BF16_autocast',attention='eager',
        training_performed=False,optimizer_updates=0,quality_validated=False,model_manifest_sha256=runtime.MANIFEST_SHA,
        token_map_sha256=pilot.TOKEN_MAP_SHA,source_files_sha256=token_map['source_files_sha256'],
        scheduled_likelihood_calls=40,scheduled_generation_calls=20)
    require(all(run.get(k) == v for k,v in run_policy.items()), 'Scientific run policy differs')
    require(json.loads(raw['recovered/seen/schedule.json']) == runtime.call_schedule(token_map['rows']), 'Frozen60 schedule differs')
    likelihood = decode_lines(raw.get('recovered/seen/likelihood.jsonl',b''))
    predictions = decode_lines(raw.get('recovered/seen/predictions.jsonl',b''))
    canary = json.loads(raw.get('recovered/seen/canary.json',b'{}'))
    completion = validate_records(run,likelihood,predictions,token_map,canary)
    if completion['all_first_attempts_recorded']:
        pilot.completed_seen(execution/'recovered/seen',package,manifest)
    expected_status = 'complete' if completion['all_first_attempts_recorded'] else 'incomplete'
    require(manifest['diagnostic_status'] == recovery['diagnostic_status'] == expected_status, 'Recovery completion differs')
    return token_map,likelihood,predictions,completion,raw


def likelihood_report(records, token_map):
    by_id = unique(records); pairs = []
    for row in token_map['rows']:
        pair = dict(case_id=row['id'],work_id=row['work_id'],target_sha256=row['target_sha256'])
        correct,mismatch = [by_id.get(row['id']+':'+c) for c in ('correct','mismatched')]
        available = all(r is not None and r['status'] == 'success' for r in (correct,mismatch))
        pair['paired_success'] = available
        if available:
            require(correct['target_sha256'] == mismatch['target_sha256'] == row['target_sha256'], 'Paired targets differ')
            for r in (correct,mismatch): check_metrics(r,len(row['labels']))
            for name,key in (('full_target','mean_nll'),('content_only','content_mean_nll')):
                pair[name] = dict(correct=correct[key],mismatched=mismatch[key],mismatch_penalty=mismatch[key]-correct[key])
        pairs.append(pair)
    def describe(items, metric):
        values = [x[metric]['mismatch_penalty'] for x in items if x['paired_success']]
        return dict(scheduled_parents=len(items),paired_successes=len(values),equal_parent_mean=statistics.mean(values) if values else None,
            median=statistics.median(values) if values else None,range=[min(values),max(values)] if values else None,
            signs=dict(positive=sum(v>0 for v in values),zero=sum(v==0 for v in values),negative=sum(v<0 for v in values)))
    result = {metric:dict(overall=describe(pairs,metric),by_work={w:describe([p for p in pairs if p['work_id']==w],metric)
        for w in sorted({p['work_id'] for p in pairs})}) for metric in ('full_target','content_only')}
    paired=sum(p['paired_success'] for p in pairs)
    status='DESCRIPTIVE_SEEN_TRAIN_LIKELIHOOD' if paired==20 else ('INCOMPLETE_NO_PAIRED_LIKELIHOOD' if paired==0 else 'PARTIAL_SEEN_TRAIN_LIKELIHOOD')
    return dict(status=status,primary='full_target',paired_parent_denominator=20,
        pairs=pairs,**result,limits='Teacher-forced likelihood, not translation merit, accuracy, significance, causal proof or generalization. No reviewer pooling or promotion.')


def build_files(token_map, likelihood, predictions, completion, raw, material):
    require(completion['all_first_attempts_recorded'],
        'Incomplete schedule: analyze missingness only; do not create a translation-review packet')
    rows,refs,scopes,_audit,consumed = material
    require([r['id'] for r in rows] == [r['id'] for r in token_map['rows']], 'Inherited TRAIN20 order differs')
    for row,tokens in zip(rows,token_map['rows']):
        require(tokens['record_id'] == row['record_id'] and tokens['work_id'] == row['work_id']
            and tokens['source_sha256'] == sha(row['source_text'].encode())
            and tokens['target_sha256'] == sha(refs[row['id']]['reference_fa'].encode()), 'Qualified source/reference differs')
    observed = unique(predictions,'case_id'); files = {'lead-only/raw/'+k:v for k,v in raw.items()}
    mapping,seen = [],set()
    for reviewer,seed in SEEDS.items():
        rng = random.Random(seed); order = list(rows); rng.shuffle(order); packet = []
        for row in order:
            rid = 'r'+format(rng.getrandbits(128),'032x'); require(rid not in seen,'Opaque ID collision'); seen.add(rid)
            pred = observed.get(row['id']); text = pred['translation'] if pred else ''
            status = ('success' if pred['status']=='success' else 'error') if pred else 'unattempted'
            public,private = [],{}
            for aid,clean in scopes[row['id']]:
                sid='s'+format(rng.getrandbits(128),'032x'); require(sid not in seen,'Scope ID collision'); seen.add(sid)
                public.append(dict(scope_id=sid,**clean)); private[sid]=aid
            ref=refs[row['id']]; ledger=ref['qualified_train_ledger']
            packet.append(dict(review_id=rid,source_text=row['source_text'],references=dict(translation_fa=ref['reference_fa'],
                edition=ledger['edition'],credit=ledger['credit'],qualifications=ledger['linguistic_review']['qualifications'],
                expert_adjudicated=False,qualification='Provisional paragraph witness, not expert gold; use uncertain where evidence cannot decide.'),
                scopes=public,execution_status=status,output_text=text,output_sha256=sha(text.encode())))
            mapping.append(dict(reviewer=reviewer,review_id=rid,case_id=row['id'],record_id=row['record_id'],work_id=row['work_id'],
                condition='trained',prediction_id=row['id']+':trained',scope_mapping=private,source_sha256=sha(row['source_text'].encode()),
                output_sha256=sha(text.encode()),execution_status=status,raw_failure=None if pred is None else
                {k:pred[k] for k in ('failure','error_type','error') if k in pred}))
        require(len(packet)==20 and sum(len(p['scopes']) for p in packet)==28,'Fixed20/28 packet coverage differs')
        files[f'reviewer-{reviewer}/packet.jsonl']=lines(packet)
        files[f'reviewer-{reviewer}/INSTRUCTIONS.md']=recall.instructions().replace(b'all40',b'all20')
    files['lead-only/mapping.jsonl']=lines(mapping)
    files['lead-only/likelihood-analysis.json']=json_bytes(likelihood_report(likelihood,token_map))
    files['lead-only/provenance.json']=json_bytes(dict(purpose='SEEN_TRAIN_RECALL_ONLY',source_files_sha256=consumed,
        completion=completion,seeds=SEEDS,scopes_are_merit=False,expert_adjudicated=False,
        preparer_sha256=sha(Path(__file__).read_bytes()),reused_material_sha256=sha(Path(recall.__file__).read_bytes()),
        reused_meaning_validator_sha256=sha(Path(meaning.__file__).read_bytes()),files={n:sha(d) for n,d in files.items()}))
    return files


def validate_reviews(packet,reviews):
    require(len(packet)==len(reviews)==20,'Fixed20 review coverage differs')
    pp,rr=unique(packet,'review_id'),unique(reviews,'review_id')
    require(pp.keys()==rr.keys(),'Review IDs differ')
    projected,ratings=[],[]
    for rid,row in pp.items():
        rating=rr[rid]
        require(set(row)==recall.PACKET_FIELDS and set(rating)==recall.FIELDS|{'local_details'},'Recall schema differs')
        projected.append({k:v for k,v in row.items() if k!='scopes'}|dict(assessment='provisional_whole_translation',constraint=''))
        ratings.append({k:v for k,v in rating.items() if k!='local_details'})
        details=rating['local_details']; require(isinstance(details,list),'Local details must be an array')
        require(set(unique(details,'scope_id'))=={s['scope_id'] for s in row['scopes']},'Local scope coverage differs')
        for detail in details:
            require(set(detail)=={'scope_id','status','reason','output_span'} and detail['status'] in recall.LOCAL_STATES
                and isinstance(detail['reason'],str) and detail['reason'].strip(),'Invalid local finding')
            span=detail['output_span']
            require(isinstance(span,str) and (not span or span in row['output_text']),'Local span is not exact output')
            require(detail['status']=='unassessable' or span.strip(),'Local finding needs output span')
            if row['execution_status']!='success': require(detail['status']=='unassessable','Local merit on failed execution')
    meaning.validate_reviews(projected,ratings,expected_count=20)
    return rr


def summarize(mapping,packets,reviews,completion):
    require(len(unique(mapping,'review_id'))==len(mapping)==40,'Mapping coverage differs')
    def report(items):
        return dict(denominator=len(items),meaning_and_execution_counts=dict(Counter(x['judgment'] if x['execution_status']=='success'
            else x['execution_status'] for x in items)),failed_categories=dict(Counter(k for x in items for k,v in x['categories'].items() if v=='fail')),
            unknown_span_handling=dict(Counter(x['unknown_span_handling'] for x in items)),
            local_scope_findings_not_merit=dict(Counter(d['status'] for x in items for d in x['local_details'])))
    result={}
    for reviewer in SEEDS:
        rr=validate_reviews(packets[reviewer],reviews[reviewer]); pp=unique(packets[reviewer],'review_id')
        mm=[m for m in mapping if m['reviewer']==reviewer]
        require(len(mm)==20 and {m['review_id'] for m in mm}==set(rr)
            and len({m['case_id'] for m in mm})==20,'Private reviewer coverage differs')
        items=[]
        for m in mm:
            p=pp[m['review_id']]
            require(m['condition']=='trained' and m['source_sha256']==sha(p['source_text'].encode())
                and m['output_sha256']==p['output_sha256'] and m['execution_status']==p['execution_status']
                and set(m['scope_mapping'])=={s['scope_id'] for s in p['scopes']},'Private mapping differs')
            items.append(rr[m['review_id']]|m)
        result[reviewer]=report(items)|dict(by_work={w:report([x for x in items if x['work_id']==w]) for w in sorted({x['work_id'] for x in items})},cases=items)
    return dict(status='TWO_SEPARATE_SEEN_TRAIN20_REVIEWS',reviewers=result,execution_completion=completion,
        expert_adjudicated=False,scopes_are_merit=False,
        limits='Seen TRAIN only; no pooled merit, DEV/PALREF comparison, generalization, significance, improvement screen or automatic promotion.')


def prepare(execution,package,output):
    evidence=load_evidence(execution,package)
    files=build_files(*evidence,recall.load_material())
    write_fresh(output,files)
    return dict(status='BLIND_SEEN_TRAIN20_PREPARED',packets=2,slots_per_packet=20)


def score(packet_dir,review_a,review_b,output,execution=EXP,package=PACKAGE):
    folder=Path(packet_dir)
    files=build_files(*load_evidence(execution,package),recall.load_material())
    for name,data in files.items(): require((folder/name).read_bytes()==data,'Frozen packet/evidence changed: '+name)
    require(Path(review_a).resolve()!=Path(review_b).resolve(),'Separate reviewer files required')
    raw={'A':Path(review_a).read_bytes(),'B':Path(review_b).read_bytes()}
    packets={r:decode_lines(files[f'reviewer-{r}/packet.jsonl']) for r in SEEDS}
    summary=summarize(decode_lines(files['lead-only/mapping.jsonl']),packets,{r:decode_lines(b) for r,b in raw.items()},
        json.loads(files['lead-only/provenance.json'])['completion'])
    summary['review_files_sha256']={r:sha(b) for r,b in raw.items()}
    summary['packet_provenance_sha256']=sha(files['lead-only/provenance.json'])
    write_fresh(output,{'summary.json':json_bytes(summary),**{f'reviewer-{r}/reviews.jsonl':b for r,b in raw.items()}})
    return summary


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='command',required=True)
    for command in ('analyze','prepare','score'):
        p=sub.add_parser(command)
        p.add_argument('--execution',type=Path,default=EXP); p.add_argument('--package',type=Path,default=PACKAGE)
        p.add_argument('--output',type=Path,required=True)
        if command=='score':
            for name in ('packet-dir','review-a','review-b'): p.add_argument('--'+name,type=Path,required=True)
    a=parser.parse_args()
    if a.command=='prepare': value=prepare(a.execution,a.package,a.output)
    elif a.command=='score': value=score(a.packet_dir,a.review_a,a.review_b,a.output,a.execution,a.package)
    else:
        token_map,likelihood,_predictions,completion,_raw=load_evidence(a.execution,a.package)
        value=likelihood_report(likelihood,token_map)|dict(execution_completion=completion)
        write_fresh(a.output,{'likelihood-analysis.json':json_bytes(value)})
    print(json.dumps({'status':value['status']}))


if __name__=='__main__': main()
