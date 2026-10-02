"""Offline dependency, failure journal, real-tokenizer and SDK checks; no weights."""
import importlib.util
import json
from pathlib import Path
import sys
import types
import uuid
from datetime import datetime, timedelta, timezone

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('legacy_check', ROOT/'experiments/component-diagnostic-20261001/check_runtime.py')
legacy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(legacy)
runner, hf_component, runtime, torch = legacy.runner, legacy.hf_component, legacy.runtime, legacy.torch
ANALYSIS = 'Tentative analysis: role unknown; deliberately contradictory statement.\nPreserve this exact text.'


class Model(legacy.Model):
    def generate(self, **kw):
        self.calls += 1
        is_first_analysis = self.calls == 2
        assert kw['max_new_tokens'] == 256 and kw['do_sample'] is False
        if is_first_analysis and self.kind == 'fatal': raise RuntimeError('Deliberate fatal model failure')
        if is_first_analysis and self.kind == 'timeout': kw['stopping_criteria'][0].start -= 91
        text = ('' if self.kind == 'empty' else '[UNRESOLVED]' if self.kind == 'abstain' else ANALYSIS) if is_first_analysis else 'mock final'
        ids = tokenizer.encode(text, add_special_tokens=False)
        ids = [7]*256 if is_first_analysis and self.kind == 'cap' else ids+[1]
        return torch.cat((kw['input_ids'], torch.tensor([ids])), dim=1)


def main():
    global tokenizer
    inputs = ROOT/'resources/local/own-analysis-diagnostic-20261002/model-inputs.jsonl'
    job, receipt = hf_component.prepare(inputs, run_id='0123456789abcdef0123456789abcdef', protocol='own-analysis-v1')
    restored = legacy.sdk_spec(json.loads(json.dumps(job, default=lambda x:x.to_dict())))
    assert restored['timeout'] == '60m' and [v.read_only for v in restored['volumes']] == [True, True, False]
    rows = runner.read_inputs(inputs, receipt['inputs_sha256'], 'own-analysis-v1')
    order = runner.schedule('own-analysis-v1')
    assert len(order) == 9 and receipt['schedule'] == order
    tokenizer = legacy.AutoTokenizer.from_pretrained(ROOT/'resources/local/cloud-pilot-qualified-20260927/tokenizer', local_files_only=True, trust_remote_code=False)
    prepared = runner.prepare_prompts(rows, tokenizer)
    assert max(map(len, prepared.values())) == 239
    root = ROOT/'resources/local'/('own-analysis-check-'+uuid.uuid4().hex)
    root.mkdir()
    for kind in ('success', 'cap', 'timeout', 'empty', 'abstain', 'fatal'):
        output, remote = root/kind, root/(kind+'-mount')
        output.mkdir()
        state = dict(identity_sha256='0'*64, status='running', schedule=order, scheduled_outputs=9,
            attempted_outputs=0, recorded_outputs=0, successful_outputs=0, model_calls_started=0,
            active_output_id=None, unattempted_output_ids=order, last_result=None)
        model = Model(kind)
        deadline = (datetime.now(timezone.utc)+timedelta(minutes=30)).isoformat()
        try: runner.generate(model, tokenizer, rows, prepared, output, remote, state, deadline, device='cpu')
        except RuntimeError:
            assert kind == 'fatal'
            state['status'] = 'incomplete'
            runtime.write_json(output/'run.json', state)
        records = [json.loads(l) for l in (output/'predictions.jsonl').read_bytes().splitlines()]
        n = 2 if kind == 'fatal' else 9
        assert len(records) == state['recorded_outputs'] == n
        assert model.calls == state['model_calls_started'] == (9 if kind=='success' else 2 if kind=='fatal' else 8)
        assert len(list(remote.glob('*/manifest.json'))) == 2*n
        state['adapter_unchanged_after_inference'] = True  # Mock-only flag, never GPU proof.
        runtime.write_json(output/'run.json', state)
        accounting = hf_component.reconcile(output, order)
        assert accounting['committed_model_calls'] == model.calls
        assert accounting['pipeline_complete'] is (kind == 'success')
        assert len(accounting['per_output_status']) == 9
        if kind != 'fatal':
            assert set(state['workflow_elapsed_seconds']) == {'KANHERI01','AMOL1','BERLIN6'}
            assert all(set(v) == {'D','AP'} and all(x > 0 for x in v.values())
                       for v in state['workflow_elapsed_seconds'].values())
        if kind == 'success':
            p = json.loads((output/'resolved-prompts/KANHERI01-P.json').read_bytes())
            assert p['prompt'] == next(r['prompt'] for r in rows if r['id']=='KANHERI01-P')+ANALYSIS
            assert p['analysis_output_sha256'] == records[1]['output_sha256']
            assert p['input_token_ids'] == tokenizer.apply_chat_template([{'role':'user','content':p['prompt']}], tokenize=True, return_dict=False, add_generation_prompt=True, enable_thinking=False)
            assert (remote/'attempt-03-done/resolved-prompt.json').read_bytes() == (output/'resolved-prompts/KANHERI01-P.json').read_bytes()
            raw = (output/'predictions.jsonl').read_bytes()
            for position in (0, 2):  # D dispatch forgery; P forgery bypassing dependency validation.
                forged = [dict(r) for r in records]
                forged[position]['model_call_started'] = False
                if position == 2: forged[position]['analysis_output_id'] = 'AMOL1-A'
                (output/'predictions.jsonl').write_bytes(b''.join(runner.canonical(r)+b'\n' for r in forged))
                runtime.write_json(output/'run.json', dict(state, model_calls_started=state['model_calls_started']-1))
                try: hf_component.reconcile(output, order)
                except ValueError: pass
                else: raise AssertionError('Undispatched successful output admitted')
            (output/'predictions.jsonl').write_bytes(raw)
            runtime.write_json(output/'run.json', state)
        elif kind == 'fatal':
            assert accounting['unavailable_dependencies_for_unattempted_slots'] == {'KANHERI01-P':'KANHERI01-A'}
        else:
            assert records[2]['status'] == 'skipped_dependency' and records[2]['output_tokens'] == 0
            assert not records[2]['model_call_started'] and not (output/'resolved-prompts/KANHERI01-P.json').exists()
        bad_state = dict(state, model_calls_started=state['model_calls_started']+2)
        runtime.write_json(output/'run.json', bad_state)
        try: hf_component.reconcile(output, order)
        except ValueError: pass
        else: raise AssertionError('Corrupted model-call counts admitted')
        runtime.write_json(output/'run.json', state)
        try: runner.generate(model, tokenizer, rows, prepared, output, remote, state, deadline, device='cpu')
        except FileExistsError: pass
        else: raise AssertionError('Retry/overwrite admitted')
    row = next(r for r in rows if r['id'] == 'KANHERI01-P')
    analysis = dict(id='KANHERI01-A', status='success', text=ANALYSIS,
        output_sha256=runner.sha(ANALYSIS.encode()), hit_output_cap_without_eos=False)
    overflow = types.SimpleNamespace(unk_token_id=-1, apply_chat_template=lambda *a,**k: [7]*1793 if k['tokenize'] else 'overflow')
    try: runner.dependent_prompt(row, analysis, overflow)
    except ValueError: pass
    else: raise AssertionError('Dynamic overflow admitted')
    bad = dict(analysis, output_sha256='0'*64)
    try: runner.dependent_prompt(row, bad, tokenizer)
    except ValueError: pass
    else: raise AssertionError('Changed analysis accepted')
    # Durable interrupted slot remains in the denominator without invented output.
    state.update(status='running', attempted_outputs=3, recorded_outputs=2, active_output_id=order[2], unattempted_output_ids=order[3:])
    runtime.write_json(output/'run.json', state)
    accounting = hf_component.reconcile(output, order)
    assert accounting['per_output_status'][order[2]] == 'interrupted_output_unknown'
    short = root/'short'; short.mkdir()
    try: runner.generate(Model(), tokenizer, rows, prepared, short, root/'short-mount', state,
        (datetime.now(timezone.utc)+timedelta(seconds=30)).isoformat(), device='cpu')
    except TimeoutError: pass
    else: raise AssertionError('Insufficient full-panel time admitted')
    assert not (short/'predictions.jsonl').exists()
    # Compatibility is for actual old shape, not a downgrade of a new journal.
    legacy_dir = root/'legacy-accounting'; legacy_dir.mkdir()
    legacy_order = runner.schedule('components-v1')
    legacy_records = [dict(id=k, case_id=k.rsplit('-',1)[0], condition=k[-1], sequence=i+1,
        identity_sha256='0'*64, status='success') for i,k in enumerate(legacy_order)]
    legacy_state = dict(schedule=legacy_order, scheduled_outputs=12, attempted_outputs=12,
        recorded_outputs=12, active_output_id=None, unattempted_output_ids=[],
        identity_sha256='0'*64, status='completed', adapter_unchanged_after_inference=True)
    (legacy_dir/'predictions.jsonl').write_bytes(b''.join(runner.canonical(r)+b'\n' for r in legacy_records))
    runtime.write_json(legacy_dir/'run.json', legacy_state)
    assert hf_component.reconcile(legacy_dir, legacy_order)['pipeline_complete'] is True
    runtime.write_json(legacy_dir/'run.json', dict(legacy_state, model_calls_started=0))
    try: hf_component.reconcile(legacy_dir, legacy_order)
    except ValueError: pass
    else: raise AssertionError('New dispatch-accounted journal downgraded to old unflagged shape')
    print(json.dumps(dict(status='pass', scheduled_slots=9, dependency_scenarios=6,
        real_tokenizer=True, SDK_serialization=True, immutable_snapshots=True,
        dynamic_capacity_and_hash_checks=True, no_retries=True, cloud_gpu_exercised=False)))


if __name__ == '__main__': main()
