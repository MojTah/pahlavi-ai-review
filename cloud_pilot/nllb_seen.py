"""Frozen inference-only TRAIN20 diagnostic of the preserved NLLB step700 model."""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import time

try:
    from . import nllb_train as frozen
except ImportError:
    import nllb_train as frozen

INPUT_SHA = '5a2b29c878b67e05bb1051fab015feae33753e7c23568ab57517af0cf84c233a'
CONTROL_SHA = '3db2398a95b6480ad2522dc2fe30d2d38156564e3a4a72714b43bcc2a54393a0'
MANIFEST_SHA = 'c2ed23f93d72f5958f8a46d1c37b1d187c6eff2a0f9d354c565de3f505ad2349'
RUNNER_SHA = '8a392db05c5a38ad75e7cc767bda05d3dc1218b9d61348d161f64fa757b7708d'
TOKEN_CONTRACT = dict(vocab_size=256215, source_tag=256214, target_tag=256053, eos=2, pad=1, unk=3)
INFERENCE_FILES = ('config.json', 'generation_config.json', 'model.safetensors.index.json',
    'model-00001-of-00002.safetensors', 'model-00002-of-00002.safetensors',
    'tokenizer.json', 'tokenizer_config.json', 'training-state.json')
GENERATION = dict(max_new_tokens=512, num_beams=1, do_sample=False, forced_bos_token_id=256053,
    forced_eos_token_id=None, suppress_tokens=[256204, 256205], use_cache=True)


def require(ok, message):
    if not ok:
        raise ValueError(message)


def digest(value):
    return hashlib.sha256(value.encode('utf-8')).hexdigest()


def lines(path):
    return [json.loads(line) for line in Path(path).read_text('utf-8').splitlines()]


def unique(rows, key):
    result = {r[key]: r for r in rows}
    require(len(result) == len(rows), 'Duplicate ' + key)
    return result


def validate_tokens(ids, tag, tokenizer):
    require(3 <= len(ids) <= 512 and ids[0] == tag and ids[-1] == 2,
            'Untruncated token length/boundary differs')
    require(all(type(x) is int and 0 <= x < len(tokenizer) for x in ids), 'Invalid token ID')
    require(tokenizer.unk_token_id not in ids, 'Unknown token in frozen input or target')


def build_token_map(package_dir, tokenizer):
    """Pure local preparation and runtime reconstruction; no model imports or writes."""
    folder = Path(package_dir)
    hashes = {name: frozen.sha(folder / name) for name in
              ('train.jsonl', 'inputs.jsonl', 'source-control.json', 'model-manifest.json')}
    require(hashes == {'train.jsonl': frozen.TRAIN_SHA, 'inputs.jsonl': INPUT_SHA,
        'source-control.json': CONTROL_SHA, 'model-manifest.json': MANIFEST_SHA}, 'Frozen source bytes differ')
    require(len(tokenizer) == TOKEN_CONTRACT['vocab_size'] and tokenizer.eos_token_id == 2
        and tokenizer.pad_token_id == 1 and tokenizer.unk_token_id == 3
        and tokenizer.src_lang == 'pal_Latn' and tokenizer.tgt_lang == 'pes_Arab'
        and tokenizer.convert_tokens_to_ids('pal_Latn') == 256214
        and tokenizer.convert_tokens_to_ids('pes_Arab') == 256053, 'Tokenizer contract differs')
    train, inputs, control = lines(folder/'train.jsonl'), lines(folder/'inputs.jsonl'), frozen.read(folder/'source-control.json')
    require(len(train) == 2237 and len(inputs) == 20, 'Exact TRAIN2237 and input20 required')
    unique(train, 'id')
    by_record, by_id = unique(train, 'record_id'), unique(inputs, 'id')
    require(control['shift'] == 5 and control['count'] == 20
        and control['source_input_sha256'] == INPUT_SHA and len(control['pairs']) == 20,
        'Frozen source-control contract differs')
    pairs = unique(control['pairs'], 'target_parent_id')
    require(set(pairs) == set(by_id), 'Source-control coverage differs')
    result = []
    for i, row in enumerate(inputs):
        original, mismatch, pair = by_record[row['record_id']], inputs[(i+5) % 20], pairs[row['id']]
        require(row['source_text'] == original['text'] and row['work_id'] == original['work_id']
            and row['source_language'] == original['source_language'] == 'pal'
            and row['target_language'] == original['target_language'] == 'fa', 'TRAIN source binding differs')
        require(row['work_id'] != mismatch['work_id'] and pair == dict(target_parent_id=row['id'],
            target_record_id=row['record_id'], correct_source_sha256=digest(row['source_text']),
            mismatched_source_parent_id=mismatch['id'], mismatched_source_record_id=mismatch['record_id'],
            mismatched_source_sha256=digest(mismatch['source_text'])), 'Fixed cross-work permutation differs')
        tokens = tokenizer(original['text'], text_target=original['target'], truncation=False)
        validate_tokens(tokens['input_ids'], 256214, tokenizer)
        validate_tokens(tokens['labels'], 256053, tokenizer)
        require(tokens['attention_mask'] == [1]*len(tokens['input_ids']), 'Unexpected source padding')
        result.append(dict(id=row['id'], record_id=row['record_id'], work_id=row['work_id'],
            source_sha256=digest(original['text']), target_sha256=digest(original['target']),
            input_ids=tokens['input_ids'], attention_mask=tokens['attention_mask'], labels=tokens['labels'],
            mismatched_source_parent_id=mismatch['id']))
    return dict(schema_version=1, source_files_sha256=hashes, tokenizer_contract=TOKEN_CONTRACT,
        model=frozen.MODEL, revision=frozen.REVISION, trained_step=700, model_manifest_sha256=MANIFEST_SHA, rows=result)


def verify_model(folder, manifest_path):
    folder = Path(folder)
    require(frozen.sha(manifest_path) == MANIFEST_SHA, 'Original checkpoint manifest differs')
    manifest = frozen.read(manifest_path)
    require(manifest['model'] == frozen.MODEL and manifest['revision'] == frozen.REVISION
        and manifest['completed_steps'] == 700 and manifest['settings'] == frozen.SETTINGS,
        'Trained checkpoint lineage differs')
    for name in INFERENCE_FILES:
        path, expected = folder/name, manifest['files']['nllb/model/'+name]
        require(path.is_file() and not path.is_symlink() and path.stat().st_size == expected['bytes']
            and frozen.sha(path) == expected['sha256'], 'Inference file verification failed: ' + name)
    require({p.name for p in folder.iterdir()} == set(INFERENCE_FILES), 'Inference directory contains unexpected files')
    index = frozen.read(folder/'model.safetensors.index.json')
    require(set(index['weight_map'].values()) == set(INFERENCE_FILES[3:5]), 'Weight index shard set differs')
    state = frozen.read(folder/'training-state.json')
    require(state['step'] == 700 and state['settings'] == frozen.SETTINGS, 'Step700 training state differs')
    return {name: manifest['files']['nllb/model/'+name] for name in INFERENCE_FILES}


def likelihood_metrics(logits, labels, native_loss, target_tag=256053, eos=2):
    """Independent log-softmax/gather reduction; padding excluded, controls separated."""
    import torch
    require(logits.shape[:2] == labels.shape, 'Logits/target alignment differs')
    valid = labels != -100
    content = valid.clone()
    for i in range(labels.shape[0]):
        positions = valid[i].nonzero().flatten()
        require(len(positions) >= 3 and int(labels[i, positions[0]]) == target_tag
            and int(labels[i, positions[-1]]) == eos, 'Target control boundaries differ')
        require(positions.tolist() == list(range(len(positions))), 'Nonterminal target padding')
        content[i, positions[0]] = content[i, positions[-1]] = False
    token_nll = -torch.log_softmax(logits.float(), dim=-1).gather(-1, labels.clamp_min(0).unsqueeze(-1)).squeeze(-1)
    require(bool(torch.isfinite(token_nll[valid]).all()), 'Nonfinite target likelihood')
    total = float(token_nll[valid].double().sum())
    count = int(valid.sum())
    mean, native = total/count, float(native_loss)
    # CUDA autocast CE can retain BF16 per-token rounding despite an FP32 scalar.
    # Keep that raw value; calibrate the declared FP32 estimand against explicit FP32 CE.
    with torch.autocast(logits.device.type, enabled=False):
        reference = float(torch.nn.functional.cross_entropy(
            logits.float().reshape(-1, logits.shape[-1]), labels.reshape(-1)))
    require(math.isfinite(native) and math.isfinite(reference)
        and math.isclose(mean, reference, rel_tol=1e-5, abs_tol=1e-5),
        f'FP32 reference/independent target loss differs: reference={reference}, independent={mean}, raw_native={native}')
    content_sum, content_count = float(token_nll[content].double().sum()), int(content.sum())
    language_sum = float(token_nll[:, 0].double().sum())
    eos_sum = sum(float(token_nll[i, int(valid[i].sum())-1]) for i in range(labels.shape[0]))
    return dict(sum_nll=total, supervised_tokens=count, mean_nll=mean, native_mean_nll=native,
        native_loss_dtype=str(getattr(native_loss, 'dtype', type(native_loss).__name__)),
        native_absolute_difference=abs(mean-native), reference_mean_nll=reference,
        reference_absolute_difference=abs(mean-reference), reference_precision='float32_logits', content_sum_nll=content_sum,
        content_tokens=content_count, content_mean_nll=content_sum/content_count,
        control_sum_nll=total-content_sum, control_tokens=count-content_count,
        language_tag_sum_nll=language_sum, eos_sum_nll=eos_sum, tokens_per_control=labels.shape[0])


def forward(model, rows, sources, device, autocast=True):
    import torch
    source_max, target_max = max(len(r['input_ids']) for r in sources), max(len(r['labels']) for r in rows)
    batch = dict(input_ids=torch.tensor([r['input_ids']+[1]*(source_max-len(r['input_ids'])) for r in sources], device=device),
        attention_mask=torch.tensor([r['attention_mask']+[0]*(source_max-len(r['input_ids'])) for r in sources], device=device),
        labels=torch.tensor([r['labels']+[-100]*(target_max-len(r['labels'])) for r in rows], device=device))
    model.eval()
    with torch.inference_mode(), torch.autocast(device.type, dtype=torch.bfloat16, enabled=autocast):
        response = model(**batch, use_cache=False)
    return likelihood_metrics(response.logits, batch['labels'], response.loss,
        target_tag=rows[0]['labels'][0], eos=model.config.eos_token_id)


def call_schedule(rows):
    schedule = []
    for i, row in enumerate(rows):
        for condition in (('correct', 'mismatched') if i % 2 == 0 else ('mismatched', 'correct')):
            source = row['id'] if condition == 'correct' else row['mismatched_source_parent_id']
            schedule.append(dict(id=row['id']+':'+condition, kind='likelihood', case_id=row['id'],
                condition=condition, source_parent_id=source))
    schedule.extend(dict(id=r['id']+':trained', kind='generation', case_id=r['id'],
        source_parent_id=r['id']) for r in rows)
    return [dict(sequence=i, **r) for i, r in enumerate(schedule, 1)]


def append(path, row):
    with Path(path).open('a', encoding='utf-8', newline='\n') as stream:
        stream.write(json.dumps(row, ensure_ascii=False, allow_nan=False)+'\n')
        stream.flush()
        os.fsync(stream.fileno())


def generation_result(tokens, text, eos=2, target_tag=256053):
    complete = 2 < len(tokens) < 513 and tokens[0] == 2 and tokens[1] == target_tag and tokens[-1] == eos
    complete = complete and bool(text.strip())
    return dict(status='success' if complete else 'failed', output_token_ids=tokens, translation=text,
        failure=None if complete else 'empty_or_cap_or_time_without_EOS')


def generate_one(model, tokenizer, source, deadline):
    import torch
    device = model.device
    inputs = {k: torch.tensor([source[k]], device=device) for k in ('input_ids', 'attention_mask')}
    with torch.inference_mode(), torch.autocast(device.type, dtype=torch.bfloat16, enabled=device.type == 'cuda'):
        values = model.generate(**inputs, **GENERATION, max_time=min(120, frozen.remaining(deadline)))[0].tolist()
    text = tokenizer.decode(values, skip_special_tokens=True, clean_up_tokenization_spaces=False)
    return generation_result(values, text)


def canary_cases(rows):
    """Keep the representative batch padded when both extrema are the same parent."""
    smallest = min(rows, key=lambda r: len(r['input_ids'])+len(r['labels']))
    longest_source = max(rows, key=lambda r: len(r['input_ids']))
    longest_target = max(rows, key=lambda r: len(r['labels']))
    edge = list({r['id']: r for r in (longest_source, longest_target)}.values())
    if len(edge) == 1:
        edge.append(min((r for r in rows if r['id'] != edge[0]['id']),
            key=lambda r: len(r['input_ids'])+len(r['labels'])))
    return [('smallest_real', [smallest]), ('representative_padded_shape', edge)]


def canaries(model, rows, device, output, deadline):
    """Two unscored real forwards; no generation, updates or diagnostic replacements."""
    import torch
    checks = []
    for name, selected in canary_cases(rows):
        frozen.remaining(deadline)
        begin = time.monotonic()
        metrics = forward(model, selected, selected, device)
        torch.cuda.synchronize()
        check = dict(kind=name, parent_ids=[r['id'] for r in selected], scored=False,
            batch_size=len(selected), padded_source_tokens=max(len(r['input_ids']) for r in selected),
            padded_target_tokens=max(len(r['labels']) for r in selected),
            seconds=time.monotonic()-begin, **metrics)
        checks.append(check)
        frozen.write(Path(output)/'canary.json', dict(status='incomplete', checks=checks))
    # Measured forward headroom plus twice the prior trained24 generation time.
    projected = 40*max(c['seconds'] for c in checks)*2 + 2*64.97553294608952 + 30
    require(projected < frozen.remaining(deadline), 'Measured remaining diagnostic projection does not fit')
    frozen.write(Path(output)/'canary.json', dict(status='passed', checks=checks,
        projected_remaining_seconds=projected, remaining_seconds=frozen.remaining(deadline),
        generation_projection_basis='2x prior trained24 observed 64.97553294608952 seconds; not a guaranteed throughput'))


def execute(rows, output, state, deadline, likelihood_call, generation_call):
    """Persist every attempt; structural failures stop without filling missing slots."""
    output = Path(output)
    by_id = unique(rows, 'id')
    schedule = call_schedule(rows)
    frozen.write(output/'schedule.json', schedule)
    state.update(status='running', completed_call_ids=[], unattempted_call_ids=[c['id'] for c in schedule],
        scheduled_likelihood_calls=2*len(rows), scheduled_generation_calls=len(rows),
        completed_likelihood_calls=0, completed_generation_calls=0, generation_failures=0,
        all_first_attempts_recorded=False)
    frozen.write(output/'run.json', state)
    try:
        for call in schedule:
            frozen.remaining(deadline)
            parent, source = by_id[call['case_id']], by_id[call['source_parent_id']]
            record = dict(**call, record_id=parent['record_id'], work_id=parent['work_id'],
                input_sha256=source['source_sha256'], target_sha256=parent['target_sha256'],
                source_record_id=source['record_id'], source_work_id=source['work_id'])
            if 'input_ids' in source:
                record.update(source_tokens=len(source['input_ids']), target_tokens=len(parent['labels']))
            begin = time.monotonic()
            failure = None
            try:
                if call['kind'] == 'likelihood':
                    record.update(status='success', **likelihood_call(parent, source))
                else:
                    state['generation_performed'] = True
                    record.update(generation_call(source))
            except Exception as error:
                failure = error
                record.update(status='failed', error_type=type(error).__name__, error=str(error))
                if call['kind'] == 'generation':
                    record.update(translation='', output_token_ids=[], failure='runtime_error')
            record['seconds'] = time.monotonic()-begin
            append(output/('likelihood.jsonl' if call['kind'] == 'likelihood' else 'predictions.jsonl'), record)
            state['completed_call_ids'].append(call['id'])
            state['unattempted_call_ids'].remove(call['id'])
            state['completed_'+call['kind']+'_calls'] += 1
            if call['kind'] == 'generation' and record['status'] != 'success':
                state['generation_failures'] += 1
            frozen.write(output/'run.json', state)
            frozen.emit('seen_call_recorded', **call, status=record['status'], seconds=record['seconds'])
            if failure is not None:
                raise RuntimeError('Recorded structural/runtime failure; remaining schedule stopped') from failure
        state.update(status='completed', all_first_attempts_recorded=True)
    except Exception as error:
        state.update(status='incomplete', error_type=type(error).__name__, error=str(error))
        raise
    finally:
        frozen.write(output/'run.json', state)


def run(package, model_dir, output, deadline):
    package, model_dir, output = Path(package), Path(model_dir), Path(output)
    require(math.isfinite(deadline), 'Finite monotonic deadline required')
    output.mkdir(parents=True, exist_ok=False)
    state = dict(status='preparing', model=frozen.MODEL, revision=frozen.REVISION, trained_step=700,
        runner_sha256=frozen.sha(__file__), generation_settings=GENERATION, seed=3407,
        precision='FP32_parameters_BF16_autocast', attention='eager', optimizer_updates=0,
        training_performed=False, generation_performed=False,
        scheduled_likelihood_calls=40, scheduled_generation_calls=20,
        completed_likelihood_calls=0, completed_generation_calls=0,
        generation_failures=0, all_first_attempts_recorded=False,
        quality_validated=False, model_manifest_sha256=MANIFEST_SHA)
    frozen.write(output/'run.json', state)
    try:
        frozen.remaining(deadline)
        require(frozen.sha(package/'inputs.jsonl') == INPUT_SHA, 'Frozen input20 differs')
        planned = lines(package/'inputs.jsonl')
        planned = [dict(r, mismatched_source_parent_id=planned[(i+5)%20]['id']) for i, r in enumerate(planned)]
        schedule = call_schedule(planned)
        state.update(completed_call_ids=[], unattempted_call_ids=[c['id'] for c in schedule])
        frozen.write(output/'schedule.json', schedule)
        frozen.write(output/'run.json', state)
        require(frozen.sha(frozen.__file__) == RUNNER_SHA, 'Frozen helper runner differs')
        state['verified_inference_files'] = verify_model(model_dir, package/'model-manifest.json')
        for key in ('HF_HUB_OFFLINE', 'TRANSFORMERS_OFFLINE', 'HF_HUB_DISABLE_IMPLICIT_TOKEN'):
            os.environ[key] = '1'
        import torch
        from transformers import AutoTokenizer, M2M100ForConditionalGeneration
        require(torch.cuda.is_available(), 'CUDA runtime required')
        require(torch.cuda.is_bf16_supported(), 'BF16 CUDA support required')
        torch.set_num_threads(8)
        torch.manual_seed(3407)
        torch.cuda.manual_seed_all(3407)
        tokenizer = AutoTokenizer.from_pretrained(model_dir, local_files_only=True, token=False,
            trust_remote_code=False, src_lang='pal_Latn', tgt_lang='pes_Arab')
        token_map = build_token_map(package, tokenizer)
        require(token_map == frozen.read(package/'token-map.json'), 'Exact frozen token map differs')
        rows = token_map['rows']
        state.update(token_map_sha256=frozen.sha(package/'token-map.json'), source_files_sha256=token_map['source_files_sha256'])
        frozen.write(output/'run.json', state)
        frozen.remaining(deadline)
        device = torch.device('cuda')
        model = M2M100ForConditionalGeneration.from_pretrained(model_dir, local_files_only=True, token=False,
            trust_remote_code=False, dtype=torch.float32, attn_implementation='eager').to(device)
        model.eval().requires_grad_(False)
        require(all(p.dtype == torch.float32 for p in model.parameters()), 'FP32 model parameters required')
        require(model.config.vocab_size == 256215 and model.config.decoder_start_token_id == 2
            and model.config.eos_token_id == 2 and model.config.pad_token_id == 1, 'Model token configuration differs')
        embedding = model.get_input_embeddings().weight
        require(all(w.data_ptr() == embedding.data_ptr() for w in (model.get_output_embeddings().weight,
            model.model.encoder.embed_tokens.weight, model.model.decoder.embed_tokens.weight)), 'Model embedding ties differ')
        canaries(model, rows, device, output, deadline)
        execute(rows, output, state, deadline,
            lambda parent, source: forward(model, [parent], [source], device),
            lambda source: generate_one(model, tokenizer, source, deadline))
    except Exception as error:
        state.update(status='incomplete', error_type=type(error).__name__, error=str(error))
        frozen.write(output/'run.json', state)
        raise


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', required=True, type=Path)
    parser.add_argument('--model', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--deadline', required=True, type=float)
    args = parser.parse_args()
    run(args.package, args.model, args.output, args.deadline)
