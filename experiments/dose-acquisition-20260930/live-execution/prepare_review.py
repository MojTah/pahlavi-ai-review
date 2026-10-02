"""Freeze a jointly blinded comparison under the unchanged semantic rubrics."""
import hashlib
import json
from pathlib import Path
import random

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def rows(path):
    return [json.loads(x) for x in path.read_bytes().splitlines()]


def read(path):
    return json.loads(path.read_bytes())


def save(path, raw):
    if path.exists():
        assert path.read_bytes() == raw, f'Frozen output differs: {path}'
    else:
        path.write_bytes(raw)


def main():
    rec = HERE / 'recovered'
    contract = read(HERE.parent / 'packet-contract.json')
    current = rows(rec / 'dose/evaluation-baseline/predictions.jsonl') + rows(rec / 'dose/evaluation/predictions.jsonl')
    assert [r['id'] for r in current] == contract['evaluation_schedule']
    cached_path = ROOT / 'experiments/nf4-diagnostic-20260930/live-execution/recovered/evaluation/evaluation/predictions.jsonl'
    assert hashlib.sha256(cached_path.read_bytes()).hexdigest() == '84345a9473714373fb87de01b9381e59d900d7694b41e6c32f3829f5ee62bb35'
    cached = [r for r in rows(cached_path) if r['arm'] == 'reference']
    assert len(cached) == 28
    predictions = current + cached
    assert len(predictions) == len({r['id'] for r in predictions}) == 126
    expected = {r['case_id']:r for r in contract['prompt_identities']}
    for p in predictions:
        assert p['status'] == 'success' and not p['hit_output_cap_without_eos'] and p['stop_reason'] is None
        assert hashlib.sha256(p['text'].encode()).hexdigest() == p['output_sha256']
        assert p['rendered_input_ids_sha256'] == expected[p['case_id']]['rendered_input_ids_sha256']
    inputs = {r['case_id']:r for r in rows(HERE.parent / 'inputs.jsonl')}
    diag = {r['case_id']:r for r in rows(ROOT / 'experiments/corrected-learning-diagnosis-20260930/references.jsonl')}
    fixed = {r['id']:r for r in rows(ROOT / 'experiments/dev-diagnostic-20260927/references.jsonl')}
    fixed_rules = {r['id']:r for r in read(ROOT / 'experiments/dev-diagnostic-20260927/assessment-contract.json')['cases']}
    confirm = {r['case_id']:r for r in rows(HERE.parent / 'confirmation/references.jsonl')}
    random.Random(20261001126).shuffle(predictions)
    packet, mapping = [], {}
    for i,p in enumerate(predictions,1):
        case = p['case_id']
        if case in fixed:
            ref = fixed[case]
            rule = fixed_rules[case]
            module = 'fixed_whole' if rule['assessment'] == 'provisional_whole_translation' else 'fixed_constrained'
            evidence = {k:ref[k] for k in ('source_text','translations','edition','notes','expert_adjudicated')}
            evidence['assessment'] = rule['assessment']
            evidence['constraint'] = rule['constraint']
        else:
            ref = diag[case] if case in diag else confirm[case]
            evidence = {k:ref[k] for k in ('learning','expected_training_answer','existing_scoped_qualification','scope_gold','expert_certified') if k in ref}
            ledger = ref.get('qualified_train_ledger',{})
            if ledger:
                evidence['published_qualification'] = {k:ledger[k] for k in ('credit','edition','curation_alignment_scope','expert_status','disposition') if k in ledger}
                review = ledger.get('linguistic_review',{})
                evidence['linguistic_limits'] = {k:review[k] for k in ('qualifications','reason','meaning') if k in review}
            module = {'historical_context_retention':'passage','targeted_sense_applicability':'targeted_passage'}.get(ref.get('module'),ref.get('module'))
            if case in confirm:
                module = 'lexical_task_recall' if ref['task'].startswith('lexical-') else 'inscription_task_recall'
        blind_id = f'B{i:03d}'
        source = inputs[case]
        prompt = source.get('prompt',source.get('messages'))
        assert prompt is not None and module
        packet.append(dict(blind_id=blind_id,module=module,prompt=prompt,evidence=evidence,answer=p['text']))
        mapping[blind_id] = dict(case_id=case,arm=p['arm'],module=p.get('module',ref.get('module')),review_module=module,output_sha256=p['output_sha256'])
    raw = ''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in packet).encode()
    save(HERE / 'blind-packet.jsonl',raw)
    save(HERE / 'blind-mapping.json',(json.dumps(mapping,ensure_ascii=False,indent=2)+'\n').encode())
    print(json.dumps({'records':len(packet),'packet_sha256':hashlib.sha256(raw).hexdigest(),'fresh_outputs':98,'cached_matched_baseline':28}))


if __name__ == '__main__':
    main()
