"""Local six-final blind review; reuse DEV semantic validation, never run models."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import random
import sys

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT/'resources/local/hf-client-venv/Lib/site-packages'))
from cloud_pilot.hf_component import reconcile
from cloud_pilot.dev_assisted import canonical
from scripts import prepare_blind_dev_assisted as shared_review
from scripts import score_blind_dev_assisted as shared_score
from scripts.score_blind_dev_assisted import validate_reviews

CASES = ('KANHERI01', 'AMOL1', 'BERLIN6')
EVIDENCE = ('reference', 'reference_language', 'reference_status', 'scope',
            'supported_meaning', 'uncertainty', 'optional_editorial', 'limit', 'complete_acceptance')
SEEDS = {'a': 2026100201, 'b': 2026100202}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def lines(path):
    return [json.loads(x) for x in path.read_bytes().splitlines()]


def encode(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True) + '\n').encode()


def frozen():
    raw_manifest = (HERE/'packet-manifest.json').read_bytes()
    proposal = json.loads((HERE/'live-execution/proposal.json').read_bytes())
    if sha(raw_manifest) != proposal['packet_manifest_sha256']:
        raise ValueError('Reviewed packet manifest pin differs')
    manifest = json.loads(raw_manifest)
    folder = ROOT/'resources/local/own-analysis-diagnostic-20261002'
    for name, entry in manifest['local_outputs'].items():
        raw = (folder/name).read_bytes()
        if len(raw) != entry['bytes'] or sha(raw) != entry['sha256']:
            raise ValueError('Frozen packet differs: '+name)
    return manifest, {r['id']:r for r in lines(folder/'model-inputs.jsonl')}, lines(folder/'review-constraints.jsonl')


def instructions():
    text = shared_review.instructions().decode().replace('Blind DEV translation review', 'Blind final translation review')
    text = text.replace('all 96 opaque records', 'all 6 opaque records').replace('reviews.jsonl', 'ratings.jsonl')
    text = text.split('\n\nFor constrained_meanings_only')[0]
    return (text+'\n\nFor unavailable records, judgment is not_assessable; categories are uncertain/not_applicable, '
        'supported_span_severity and unknown_span_handling are uncertain. This neutral marker covers failed, capped, '
        'abstaining, skipped, interrupted or missing finals without revealing the workflow. Partial text is preserved; '
        'an empty field means no textual output is available, not a generated placeholder. Never give these an acceptance. '
        'Keep all six records. Assess disputed technical meanings as uncertain rather than guessing. Faithful explicit '
        'uncertainty and preserved opaque terms can satisfy the qualified reference; editorial explanations are optional. '
        'For a successful whole translation, a supported_span_severity of critical_error requires judgment critical_error. '
        'Contradictory fields stop scoring: preserve the submitted ratings and obtain an explicit corrected review, never silently relabel. '
        'Identical evidence/text must receive consistent judgments. Blinding reduces anchoring but does not establish '
        'independent or expert-calibrated measurements.\n').encode()


def packets(predictions, accounting, refs):
    observed = {r['id']:r for r in predictions}
    if len(observed) != len(predictions) or {r['case_id'] for r in refs} != set(CASES) or len(refs) != 3:
        raise ValueError('Duplicate predictions or reference coverage differs')
    for row in predictions:
        if sha(row['text'].encode()) != row['output_sha256']:
            raise ValueError('Raw output hash differs')
        if row['status']=='success' and (not row['text'].strip() or row['text'].strip()=='[UNRESOLVED]'
                or row['hit_output_cap_without_eos'] is not False or row['stop_reason'] is not None
                or row['model_call_started'] is not True):
            raise ValueError('Invalid successful output, including analysis')
    output, mapping = {}, []
    for reviewer, seed in SEEDS.items():
        rng = random.Random(seed)
        order = [(case, arm) for case in CASES for arm in ('D', 'P')]
        rng.shuffle(order)
        packet = []
        for case, arm in order:
            ref = next(r for r in refs if r['case_id'] == case)
            key = case+'-'+arm
            row = observed.get(key)
            text = row['text'] if row else ''
            if row and sha(text.encode()) != row['output_sha256']:
                raise ValueError('Raw final text differs')
            status = accounting['per_output_status'][key]
            available = bool(row and status == 'success' and row['model_call_started'] is True
                and text.strip() and text.strip() != '[UNRESOLVED]'
                and row['hit_output_cap_without_eos'] is False and row['stop_reason'] is None)
            if status == 'success' and not available:
                raise ValueError('Invalid successful final')
            rid = 'r'+format(rng.getrandbits(128), '032x')
            packet.append(dict(review_id=rid, source_text=ref['source'],
                references={k:ref[k] for k in EVIDENCE}, assessment='provisional_whole_translation',
                constraint=ref['complete_acceptance'], execution_status='success' if available else 'unavailable',
                output_text=text, output_sha256=sha(text.encode())))
            mapping.append(dict(reviewer=reviewer, review_id=rid, case_id=case, arm=arm,
                broader_group=ref['broader_group'], prediction_id=key, raw_execution_status=status,
                output_present=row is not None, output_sha256=sha(text.encode())))
        if len({r['review_id'] for r in packet}) != 6:
            raise ValueError('Opaque ID collision')
        output[reviewer] = packet
    return output, mapping


def validate(packet, ratings):
    # Neutral reviewer marker hides dependency skips. Only the reused validator's
    # internal failure branch receives a generic error; raw status stays private.
    normalized = []
    for row in packet:
        if row['execution_status'] not in {'success', 'unavailable'}:
            raise ValueError('Reviewer-visible execution status leaks workflow')
        normalized.append(dict(row, execution_status='error' if row['execution_status']=='unavailable' else 'success'))
    result = validate_reviews(normalized, ratings, expected_count=6)
    duplicates = {}
    for row in packet:
        key = encode({k:row[k] for k in ('source_text', 'references', 'execution_status', 'output_text')})
        label = result[row['review_id']]['judgment']
        if duplicates.setdefault(key, label) != label:
            raise ValueError('Identical evidence/output received inconsistent labels')
    return result


def summarize(all_packets, mapping, all_ratings, accounting):
    result = dict(provisional_ai_review=True, expert_adjudicated=False, unseen_claim=False,
                  promotion_allowed=False, reviewers={}, label_disagreements=[])
    keyed, gains = {}, []
    for reviewer in SEEDS:
        ratings = validate(all_packets[reviewer], all_ratings[reviewer])
        private = [m for m in mapping if m['reviewer']==reviewer]
        if len(private)!=6 or {m['review_id'] for m in private} != set(ratings):
            raise ValueError('Private mapping coverage differs')
        public = {r['review_id']:r for r in all_packets[reviewer]}
        if any(m['output_sha256'] != public[m['review_id']]['output_sha256'] for m in private):
            raise ValueError('Private mapping/output hash differs')
        pairs = {(m['case_id'], m['arm']):ratings[m['review_id']]
                 for m in mapping if m['reviewer'] == reviewer}
        if set(pairs) != {(c,a) for c in CASES for a in ('D','P')}:
            raise ValueError('Exactly three cases per final arm required')
        keyed[reviewer] = pairs
        labels = lambda arm: Counter(pairs[c,arm]['judgment'] for c in CASES)
        new = [c for c in CASES if pairs[c,'D']['judgment']!='accepted' and pairs[c,'P']['judgment']=='accepted']
        lost = [c for c in CASES if pairs[c,'D']['judgment']=='accepted' and pairs[c,'P']['judgment']!='accepted']
        groups = {m['broader_group'] for m in mapping if m['reviewer']==reviewer and m['case_id'] in new}
        signal = (accounting['pipeline_complete'] and len(new)>=2 and len(groups)==2
                  and not lost and labels('P')['critical_error']==0)
        result['reviewers'][reviewer] = dict(arms={a:dict(n=3, labels=dict(labels(a))) for a in ('D','P')},
            newly_accepted_cases=new, regressed_cases=lost, gain_groups=sorted(groups),
            exploratory_continuation_signal=signal,
            paired_labels={c:{a:pairs[c,a]['judgment'] for a in ('D','P')} for c in CASES})
        gains.append(set(new))
    result['joint_newly_accepted_cases'] = sorted(set.intersection(*gains))
    result['larger_confirmation_proposal_signal'] = all(r['exploratory_continuation_signal'] for r in result['reviewers'].values())
    result['decision_rule'] = 'Each assessor needs >=2 gains across both groups; joint case intersection reported separately, not a stronger post-result gate.'
    result['label_disagreements'] = [dict(case_id=c, arm=a, a=keyed['a'][c,a]['judgment'], b=keyed['b'][c,a]['judgment'])
        for c in CASES for a in ('D','P') if keyed['a'][c,a]['judgment'] != keyed['b'][c,a]['judgment']]
    result['technical_accounting'] = accounting
    return result


def prepare(recovered, remote_manifest_sha, output):
    raw = (recovered/'manifest.json').read_bytes()
    if sha(raw) != remote_manifest_sha:
        raise ValueError('Use the independently read-back remote manifest pin')
    remote = json.loads(raw)
    receipt = json.loads((ROOT/'resources/local/own-analysis-diagnostic-20261002/execution-preview-dispatch-repair/prepared-receipt.json').read_bytes())
    proposal = json.loads((HERE/'live-execution/proposal.json').read_bytes())
    preview = ROOT/'resources/local/own-analysis-diagnostic-20261002/execution-preview-dispatch-repair'
    if (sha((preview/'prepared-receipt.json').read_bytes()) != proposal['prepared_receipt_sha256']
            or sha((preview/'job-spec.json').read_bytes()) != proposal['job_spec_sha256']
            or receipt['run_id'] != proposal['run_id']):
        raise ValueError('Reviewed receipt/specification pin differs')
    for key in ('protocol', 'run_id', 'inputs_sha256', 'script_hashes', 'trained_manifest_sha256'):
        if remote.get(key) != receipt[key]:
            raise ValueError('Recovered job identity differs: '+key)
    if remote.get('training_performed') is not False or remote.get('optimizer_updates') != 0:
        raise ValueError('Inference-only job required')
    if sum(entry['bytes'] for entry in remote['files'].values()) > 16*1024**2:
        raise ValueError('Recovered small evidence exceeds existing export bound')
    for name, entry in remote['files'].items():
        path = recovered/name
        if path.is_symlink() or not path.resolve().is_relative_to(recovered.resolve()):
            raise ValueError('Unsafe recovered path')
        data = path.read_bytes()
        if len(data) != entry['bytes'] or sha(data) != entry['sha256']:
            raise ValueError('Recovered artifact differs: '+name)
    manifest, inputs, refs = frozen()
    tokenizer_path = ROOT/'resources/local/cloud-pilot-qualified-20260927/tokenizer'
    for name, checksum in manifest['artifact_sha256'].items():
        if Path(name).parent == tokenizer_path.relative_to(ROOT):
            if sha((ROOT/name).read_bytes()) != checksum:
                raise ValueError('Frozen tokenizer differs')
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_path, local_files_only=True, trust_remote_code=False)
    evaluation = recovered/'evaluation'
    if 'evaluation/run.json' not in remote['files']:
        raise ValueError('No verified execution journal; report technical failure with N=3, do not infer generations')
    accounting = reconcile(evaluation, manifest['schedule'])
    predictions = lines(evaluation/'predictions.jsonl') if (evaluation/'predictions.jsonl').exists() else []
    state = json.loads((evaluation/'run.json').read_bytes())
    expected = dict(protocol='own-analysis-v1', run_id=receipt['run_id'], inputs_sha256=receipt['inputs_sha256'],
        script_hashes=receipt['script_hashes'], optimizer_updates=0, adapter_step=280,
        precision=receipt['precision'], attention='eager', max_new_tokens=256,
        max_generation_seconds=90, context_limit=2048, seed=42, do_sample=False,
        adapter_files={Path(k).name:v for k,v in receipt['retained_files'].items() if k.startswith('training/adapter/')})
    if any(state.get(k)!=v for k,v in expected.items()):
        raise ValueError('Run provenance or numerical recipe differs')
    if predictions and state.get('canary',{}).get('status') != 'passed':
        raise ValueError('No passed prefill evidence before experimental outputs')
    for row in predictions:
        if sha(row['text'].encode()) != row['output_sha256']:
            raise ValueError('Raw output hash differs')
        if 'evaluation/predictions.jsonl' not in remote['files']:
            raise ValueError('Predictions are outside the verified manifest')
        if row['model_call_started']:
            prompt = inputs[row['id']]['prompt']
            if row['condition']=='P':
                analysis = next(r for r in predictions if r['id']==row['case_id']+'-A')
                prompt += analysis['text']
                if f"evaluation/resolved-prompts/{row['id']}.json" not in remote['files']:
                    raise ValueError('Resolved input outside verified manifest')
                resolved = json.loads((evaluation/'resolved-prompts'/f"{row['id']}.json").read_bytes())
                if resolved['prompt'] != prompt or resolved['analysis_output_sha256'] != analysis['output_sha256']:
                    raise ValueError('Resolved first-analysis input differs')
            if row['prompt_sha256'] != sha(prompt.encode()):
                raise ValueError('Actual input differs')
            messages = [{'role':'user','content':prompt}]
            ids = tokenizer.apply_chat_template(messages, tokenize=True, return_dict=False,
                add_generation_prompt=True, enable_thinking=False)
            rendered = tokenizer.apply_chat_template(messages, tokenize=False,
                add_generation_prompt=True, enable_thinking=False)
            rendered_sha = sha(rendered.encode())
            if (row['input_tokens'] != len(ids) or row['rendered_input_ids_sha256'] != sha(canonical(ids))
                    or row['rendered_sha256'] != rendered_sha or len(ids)+256 > manifest['context_limit']):
                raise ValueError('Actual token input differs from frozen tokenizer replay')
            if row['condition']=='P':
                if (resolved['analysis_output_id'] != analysis['id'] or resolved['input_token_ids'] != ids
                        or len(resolved['input_token_ids']) != row['input_tokens'] or resolved['rendered_sha256'] != rendered_sha):
                    raise ValueError('Resolved dependency/token receipt differs')
            elif row['input_tokens'] != inputs[row['id']]['prompt_tokens'] or rendered_sha != inputs[row['id']]['rendered_sha256']:
                raise ValueError('Static frozen token receipt differs')
    packet, mapping = packets(predictions, accounting, refs)
    output.mkdir(parents=True, exist_ok=False)
    files = {}
    for reviewer in SEEDS:
        folder = output/('reviewer-'+reviewer);folder.mkdir()
        files[f'reviewer-{reviewer}/packet.jsonl'] = b''.join(map(encode, packet[reviewer]))
        files[f'reviewer-{reviewer}/INSTRUCTIONS.md'] = instructions()
    files['lead-only-mapping.jsonl'] = b''.join(map(encode, mapping))
    files['accounting.json'] = encode(accounting)
    for name, data in files.items():
        with (output/name).open('xb') as f:f.write(data)
    provenance = dict(remote_manifest_sha256=remote_manifest_sha, preparer_sha256=sha(Path(__file__).read_bytes()),
        shared_preparer_sha256=sha(Path(shared_review.__file__).read_bytes()),
        shared_validator_sha256=sha(Path(shared_score.__file__).read_bytes()),
        reference_packet_sha256=manifest['local_outputs']['review-constraints.jsonl']['sha256'],
        files={name:sha(data) for name,data in files.items()}, final_slots_per_reviewer=6, denominator_per_arm=3,
        workflow_elapsed_seconds=state.get('workflow_elapsed_seconds'),
        known_committed_generated_tokens={arm:sum(r['output_tokens'] for r in predictions
            if r['model_call_started'] and (r['condition']=='D')==(arm=='D')) for arm in ('D','AP')},
        token_counts_are_not_billing=True)
    (output/'provenance.json').write_bytes(encode(provenance))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=('prepare', 'summarize'))
    parser.add_argument('--review', type=Path, required=True)
    parser.add_argument('--recovered', type=Path)
    parser.add_argument('--remote-manifest-sha')
    args = parser.parse_args()
    if args.operation=='prepare':
        if args.recovered is None or args.remote_manifest_sha is None:parser.error('prepare requires recovered and remote manifest pin')
        prepare(args.recovered, args.remote_manifest_sha, args.review)
    else:
        provenance = json.loads((args.review/'provenance.json').read_bytes())
        if provenance['preparer_sha256'] != sha(Path(__file__).read_bytes()) or provenance['shared_preparer_sha256'] != sha(Path(shared_review.__file__).read_bytes()) or provenance['shared_validator_sha256'] != sha(Path(shared_score.__file__).read_bytes()):
            raise ValueError('Review preparation/validation sources changed after freezing')
        for name, checksum in provenance['files'].items():
            if sha((args.review/name).read_bytes()) != checksum:raise ValueError('Frozen review packet differs')
        packet = {k:lines(args.review/f'reviewer-{k}/packet.jsonl') for k in SEEDS}
        ratings = {k:lines(args.review/f'reviewer-{k}/ratings.jsonl') for k in SEEDS}
        result = summarize(packet, lines(args.review/'lead-only-mapping.jsonl'), ratings,
                           json.loads((args.review/'accounting.json').read_bytes()))
        result['provenance'] = provenance
        result['rating_files_sha256'] = {k:sha((args.review/f'reviewer-{k}/ratings.jsonl').read_bytes()) for k in SEEDS}
        with (args.review/'summary.json').open('xb') as f:f.write(encode(result))
    print(json.dumps(dict(status='pass', operation=args.operation, local_only=True, cloud_performed=False)))


if __name__=='__main__':main()
