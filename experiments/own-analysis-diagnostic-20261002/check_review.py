"""Synthetic local review checks; no semantic ratings, model, provider or weights."""
import copy
import importlib.util
import json
from pathlib import Path
import sys
import uuid

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('own_review', HERE/'review.py')
review = importlib.util.module_from_spec(spec)
spec.loader.exec_module(review)


def rejected(call):
    try:call()
    except (ValueError, KeyError, FileNotFoundError, FileExistsError):return
    raise AssertionError('Invalid mutation admitted')


def ratings(packet, accepted):
    output = []
    for p in packet:
        available = p['execution_status']=='success'
        label = ('accepted' if p['source_text'] in accepted else 'meaning_error') if available else 'not_assessable'
        output.append(dict(review_id=p['review_id'], output_sha256=p['output_sha256'], judgment=label,
            categories={k:('pass' if label=='accepted' else 'fail' if available else 'uncertain')
                        for k in review.shared_review.CATEGORIES},
            supported_span_severity='none' if label=='accepted' else 'meaning_error' if available else 'uncertain',
            unknown_span_handling='appropriately_uncertain' if available else 'uncertain',
            reason='Synthetic validator fixture; not an assessment.', output_span=p['output_text'] if available else ''))
    return output


def main():
    contract, inputs, refs = review.frozen()
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(review.ROOT/'resources/local/cloud-pilot-qualified-20260927/tokenizer',local_files_only=True,trust_remote_code=False)
    receipt = json.loads((review.ROOT/'resources/local/own-analysis-diagnostic-20261002/execution-preview-dispatch-repair/prepared-receipt.json').read_bytes())
    records, files = [], {}
    for sequence, key in enumerate(contract['schedule'],1):
        case, arm = key.rsplit('-',1)
        text = 'Synthetic analysis, uncertain.' if arm=='A' else 'فقط نمونهٔ مصنوعی برای آزمون نرم‌افزار '+arm
        prompt = inputs[key]['prompt']
        dependency = next((r for r in records if r['id']==case+'-A'),None) if arm=='P' else None
        if dependency:
            prompt += dependency['text']
        messages=[{'role':'user','content':prompt}]
        ids=tokenizer.apply_chat_template(messages,tokenize=True,return_dict=False,add_generation_prompt=True,enable_thinking=False)
        rendered=tokenizer.apply_chat_template(messages,tokenize=False,add_generation_prompt=True,enable_thinking=False)
        if dependency:
            files[f'evaluation/resolved-prompts/{key}.json'] = review.encode(dict(prompt=prompt,
                analysis_output_id=dependency['id'],analysis_output_sha256=dependency['output_sha256'],
                input_token_ids=ids,rendered_sha256=review.sha(rendered.encode())))
        records.append(dict(id=key, case_id=case, condition=arm, sequence=sequence,
            identity_sha256='0'*64, status='success', text=text, output_sha256=review.sha(text.encode()),
            prompt_sha256=review.sha(prompt.encode()), model_call_started=True,
            input_tokens=len(ids),rendered_input_ids_sha256=review.sha(review.canonical(ids)),rendered_sha256=review.sha(rendered.encode()),
            hit_output_cap_without_eos=False, stop_reason=None, output_tokens=8,
            analysis_output_id=dependency['id'] if dependency else None,
            analysis_output_sha256=dependency['output_sha256'] if dependency else None))
    state = dict(protocol='own-analysis-v1', run_id=receipt['run_id'], inputs_sha256=receipt['inputs_sha256'],
        script_hashes=receipt['script_hashes'], optimizer_updates=0, adapter_step=280,
        precision=receipt['precision'], attention='eager', max_new_tokens=256,
        max_generation_seconds=90, context_limit=2048, seed=42, do_sample=False,
        adapter_files={Path(k).name:v for k,v in receipt['retained_files'].items() if k.startswith('training/adapter/')},
        canary={'status':'passed'}, identity_sha256='0'*64, status='completed', schedule=contract['schedule'],
        scheduled_outputs=9, attempted_outputs=9, recorded_outputs=9, model_calls_started=9,
        active_output_id=None, unattempted_output_ids=[], adapter_unchanged_after_inference=True)
    files['evaluation/run.json'] = review.encode(state)
    files['evaluation/predictions.jsonl'] = b''.join(map(review.encode,records))
    root = review.ROOT/'resources/local'/('own-review-check-'+uuid.uuid4().hex)
    recovered = root/'recovered';recovered.mkdir(parents=True)
    for name,data in files.items():
        path=recovered/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
    manifest = dict(receipt, training_performed=False, optimizer_updates=0,
        files={name:dict(bytes=len(data),sha256=review.sha(data)) for name,data in files.items()})
    raw=review.encode(manifest);(recovered/'manifest.json').write_bytes(raw)
    review.prepare(recovered,review.sha(raw),root/'review')
    rejected(lambda:review.prepare(recovered,review.sha(raw),root/'review'))
    rejected(lambda:review.prepare(recovered,'0'*64,root/'wrong-pin'))
    # Changed transport pins cannot conceal inconsistent actual token/dependency evidence.
    for kind in ('D-token','P-token','P-dependency'):
        mutated=copy.deepcopy(files)
        if kind=='D-token':
            bad_records=copy.deepcopy(records);bad_records[0]['input_tokens']=999
            mutated['evaluation/predictions.jsonl']=b''.join(map(review.encode,bad_records))
        else:
            name='evaluation/resolved-prompts/KANHERI01-P.json';bad_receipt=json.loads(mutated[name])
            bad_receipt['input_token_ids' if kind=='P-token' else 'analysis_output_id']=[-99] if kind=='P-token' else 'AMOL1-A'
            mutated[name]=review.encode(bad_receipt)
        mutated_manifest=dict(manifest,files={name:dict(bytes=len(data),sha256=review.sha(data)) for name,data in mutated.items()})
        for name,data in mutated.items():(recovered/name).write_bytes(data)
        bad_raw=review.encode(mutated_manifest);(recovered/'manifest.json').write_bytes(bad_raw)
        rejected(lambda:review.prepare(recovered,review.sha(bad_raw),root/kind))
    for name,data in files.items():(recovered/name).write_bytes(data)
    (recovered/'manifest.json').write_bytes(raw)
    accounting = review.reconcile(recovered/'evaluation',contract['schedule'])
    packets,mapping = review.packets(records,accounting,refs)
    assert all(len(p)==6 for p in packets.values()) and len(mapping)==12
    assert {m['arm'] for m in mapping}=={'D','P'}
    for p in packets.values():
        assert all(set(r)==review.shared_review.PACKET_FIELDS for r in p)
        assert all('Synthetic analysis' not in r['output_text'] for r in p)
    sources={r['case_id']:r['source'] for r in refs}
    # Different two-case gain sets satisfy the frozen per-rater rule; intersection is only one.
    rr={}
    for who,other in (('a','AMOL1'),('b','BERLIN6')):
        rr[who]=ratings(packets[who],set())
        for row,m in zip(rr[who],[m for m in mapping if m['reviewer']==who]):
            if m['arm']=='P' and m['case_id'] in {'KANHERI01',other}:
                replacement=ratings([next(p for p in packets[who] if p['review_id']==row['review_id'])],{sources[m['case_id']]})[0]
                row.update(replacement)
    result=review.summarize(packets,mapping,rr,accounting)
    assert result['larger_confirmation_proposal_signal'] and result['joint_newly_accepted_cases']==['KANHERI01']
    assert all(v['arms']['P']['n']==3 for v in result['reviewers'].values())
    # A critical supported finding cannot hide behind a milder whole label.
    critical=copy.deepcopy(rr)
    for who in review.SEEDS:
        failed_p=next(m for m in mapping if m['reviewer']==who and m['arm']=='P'
            and next(r for r in critical[who] if r['review_id']==m['review_id'])['judgment']=='meaning_error')
        row=next(r for r in critical[who] if r['review_id']==failed_p['review_id'])
        row['supported_span_severity']='critical_error'
        rejected(lambda:review.validate(packets[who],critical[who]))
    rejected(lambda:review.summarize(packets,mapping,critical,accounting))
    for who in review.SEEDS:
        row=next(r for r in critical[who] if r['supported_span_severity']=='critical_error')
        row['judgment']='uncertain';row['categories']={k:'uncertain' for k in review.shared_review.CATEGORIES}
        rejected(lambda:review.validate(packets[who],critical[who]))
        row['judgment']='critical_error';row['categories']={k:'fail' for k in review.shared_review.CATEGORIES}
    assert not review.summarize(packets,mapping,critical,accounting)['larger_confirmation_proposal_signal']
    for who in review.SEEDS:
        (root/f'review/reviewer-{who}/ratings.jsonl').write_bytes(b''.join(map(review.encode,rr[who])))
    original_argv=sys.argv
    try:
        sys.argv=['review.py','summarize','--review',str(root/'review')]
        review.main()
    finally:sys.argv=original_argv
    saved=json.loads((root/'review/summary.json').read_bytes())
    assert saved['larger_confirmation_proposal_signal'] and saved['promotion_allowed'] is False
    broken=copy.deepcopy(records);broken[1]['hit_output_cap_without_eos']=True
    rejected(lambda:review.packets(broken,accounting,refs))
    broken=copy.deepcopy(records);broken[0]['text']='Changed raw output'
    rejected(lambda:review.packets(broken,accounting,refs))
    partial=copy.deepcopy(accounting);partial['pipeline_complete']=False
    partial['per_output_status']['KANHERI01-P']='skipped_dependency'
    pp,mm=review.packets([r for r in records if r['id']!='KANHERI01-P'],partial,refs)
    assert all(sum(r['execution_status']=='unavailable' for r in p)==1 for p in pp.values())
    assert all('skipped_dependency' not in json.dumps(p) for p in pp.values())
    missing={who:ratings(p,{r['source'] for r in refs}) for who,p in pp.items()}
    assert not review.summarize(pp,mm,missing,partial)['larger_confirmation_proposal_signal']
    bad=copy.deepcopy(missing['a']);target=next(r for r in pp['a'] if r['execution_status']=='unavailable')
    next(r for r in bad if r['review_id']==target['review_id'])['judgment']='accepted'
    rejected(lambda:review.validate(pp['a'],bad))
    leaked=copy.deepcopy(packets['a']);leaked[0]['condition']='P'
    rejected(lambda:review.validate(leaked,rr['a']))
    bad=copy.deepcopy(rr['a']);bad[0]['output_sha256']='0'*64
    rejected(lambda:review.validate(packets['a'],bad))
    rejected(lambda:review.summarize(packets,mapping+[mapping[0]],rr,accounting))
    print(json.dumps(dict(status='pass',synthetic_only=True,cloud_gpu_exercised=False,
        checks='manifest/run/prompt pins, exclusive creation, six-slot blinding, failed/missing denominator, false acceptance/leak/hash/duplicate rejection and unchanged per-rater continuation rule')))


if __name__=='__main__':main()
