"""One frozen encoder-decoder experiment; executes only within a verified job package."""
import argparse
import gc
import hashlib
import json
import math
import os
from pathlib import Path
import random
import time

MODEL = 'facebook/nllb-200-distilled-1.3B'
REVISION = '7be3e24664b38ce1cac29b8aeed6911aa0cf0576'
WEIGHTS_SHA = '7e40f838a5aad3d60e9254632ab876bda44340386ca7ebad3e099db7432b04e1'
WEIGHTS_BYTES = 5482882236
TRAIN_SHA = '15b13f63b518882fe82697ff27cc1656011f3868a318f910bb9de9e2422925dc'
DEV_SHA = '06ac58310bf67767fae4124d8e935c808d15debcd8daebce07b583937cd97182'
SETTINGS = dict(seed=3407, epochs=5, microbatch=4, effective_batch=16, updates=700,
    lr=3e-5, weight_decay=0.01, warmup_updates=42, max_grad_norm=1.0,
    loss='sum_target_CE/global_update_nonpadding_tokens', label_smoothing=0,
    max_new_tokens=512, do_sample=False, num_beams=1, forced_bos_token_id=256053,
    suppress_tokens=[256204, 256205], parameters_dtype='float32', autocast_dtype='bfloat16')


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(8 * 1024**2), b''):
            digest.update(block)
    return digest.hexdigest()


def read(path):
    return json.loads(Path(path).read_text('utf-8'))


def write(path, value):
    path = Path(path)
    temp = path.with_suffix(path.suffix + '.tmp')
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    os.replace(temp, path)


def emit(phase, **details):
    print(json.dumps(dict(phase=phase, **details)), flush=True)


def remaining(deadline, reserve=0):
    value = deadline - time.monotonic() - reserve
    if value <= 0:
        raise TimeoutError('NLLB computation deadline')
    return value


def schedule(count=2237):
    if count != 2237:
        raise ValueError('Exact qualified corpus required')
    groups = []
    for epoch in range(SETTINGS['epochs']):
        order = list(range(count))
        random.Random(SETTINGS['seed'] + epoch).shuffle(order)
        groups.extend(order[i:i + 16] for i in range(0, count, 16))
    if len(groups) != 700 or sum(map(len, groups)) != 11185:
        raise ValueError('Training exposure schedule changed')
    return groups


def rate(update):
    if not 1 <= update <= 700:
        raise ValueError('Update outside frozen schedule')
    scale = update / 42 if update <= 42 else (700 - update) / (700 - 42)
    return SETTINGS['lr'] * scale


def optimizer_for(model):
    import torch
    decay, no_decay = [], []
    for name, parameter in model.named_parameters():
        if not parameter.requires_grad or parameter.dtype != torch.float32:
            raise ValueError('Full FP32 trainable parameters required')
        (no_decay if name.endswith('.bias') or 'norm' in name.lower() else decay).append(parameter)
    return torch.optim.AdamW([{'params': decay, 'weight_decay': 0.01},
                             {'params': no_decay, 'weight_decay': 0.0}],
                            lr=SETTINGS['lr'], betas=(0.9, 0.999), eps=1e-8)


def token_rows(folder, tokenizer):
    if sha(folder / 'train.jsonl') != TRAIN_SHA or sha(folder / 'dev-inputs.jsonl') != DEV_SHA:
        raise ValueError('Frozen input bytes differ')
    train = [json.loads(s) for s in (folder / 'train.jsonl').read_text('utf-8').splitlines()]
    dev = [json.loads(s) for s in (folder / 'dev-inputs.jsonl').read_text('utf-8').splitlines()]
    if len(train) != 2237 or len({r['id'] for r in train}) != 2237 or len(dev) != 24 or len({r['id'] for r in dev}) != 24:
        raise ValueError('Exact unique input coverage required')
    prepared = []
    for row in train:
        tokens = tokenizer(row['text'], text_target=row['target'], truncation=False)
        for name, tag in (('input_ids', 256214), ('labels', 256053)):
            ids = tokens[name]
            if len(ids) > 512 or ids[0] != tag or ids[-1] != tokenizer.eos_token_id or tokenizer.unk_token_id in ids:
                raise ValueError('TRAIN token boundary, unknown token or length failure: ' + row['id'])
        prepared.append({k: tokens[k] for k in ('input_ids', 'attention_mask', 'labels')})
    for row in dev:
        ids = tokenizer(row['source_text'], truncation=False)['input_ids']
        if len(ids) > 512 or ids[0] != 256214 or ids[-1] != tokenizer.eos_token_id or tokenizer.unk_token_id in ids:
            raise ValueError('DEV token boundary/coverage failure')
    return train, prepared, dev


def initialize(model, tokenizer, evidence, languages):
    import torch
    original = model.get_input_embeddings().weight.detach().clone()
    if original.shape[0] != 256206 or len(tokenizer) != 256215:
        raise ValueError('Model vocabulary/resize mismatch')
    model.resize_token_embeddings(len(tokenizer), mean_resizing=False)
    embedding = model.get_input_embeddings().weight
    language_ids = [tokenizer.convert_tokens_to_ids(name) for name in languages]
    if len(language_ids) != 202 or len(set(language_ids)) != 202 or max(language_ids) >= 256206:
        raise ValueError('Source language initialization differs')
    mask = torch.ones(256206, dtype=torch.bool, device=original.device)
    mask[[i for i in tokenizer.all_special_ids if i < 256206]] = False
    with torch.no_grad():
        for char_id in evidence['extension']['train_only_missing_characters'].values():
            if not 256206 <= char_id < 256214:
                raise ValueError('Character extension boundary differs')
            embedding[char_id].copy_(original[mask].mean(dim=0))
        embedding[256214].copy_(original[language_ids].mean(dim=0))
    if not torch.equal(embedding[:256206], original):
        raise ValueError('Original embedding rows altered')
    if not all(w.data_ptr() == embedding.data_ptr() for w in
               (model.get_output_embeddings().weight, model.model.encoder.embed_tokens.weight,
                model.model.decoder.embed_tokens.weight)):
        raise ValueError('Embedding ties differ')


def update(model, optimizer, rows, collator, update_index, device, autocast=True):
    import torch
    import torch.nn.functional as F
    from transformers.models.m2m_100.modeling_m2m_100 import shift_tokens_right
    total = sum(len(r['labels']) for r in rows)
    if total <= 0:
        raise ValueError('No supervised tokens')
    model.train()
    optimizer.zero_grad(set_to_none=True)
    loss_total = 0.0
    for start in range(0, len(rows), SETTINGS['microbatch']):
        batch = {k: v.to(device) for k, v in collator(rows[start:start + SETTINGS['microbatch']]).items()}
        with torch.autocast(device_type=device.type, dtype=torch.bfloat16, enabled=autocast):
            response = model(input_ids=batch['input_ids'], attention_mask=batch['attention_mask'],
                decoder_input_ids=shift_tokens_right(batch['labels'],model.config.pad_token_id,
                                                    model.config.decoder_start_token_id),use_cache=False)
            loss = F.cross_entropy(response.logits.float().reshape(-1, response.logits.shape[-1]),
                                   batch['labels'].reshape(-1), ignore_index=-100, reduction='sum') / total
        if not torch.isfinite(loss):
            raise FloatingPointError('Nonfinite target loss')
        loss.backward()
        loss_total += loss.detach().item()
    norm = torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0, error_if_nonfinite=True)
    for group in optimizer.param_groups:
        group['lr'] = rate(update_index)
    optimizer.step()
    optimizer.zero_grad(set_to_none=True)
    return dict(loss=loss_total, gradient_norm=float(norm), supervised_tokens=total, parents=len(rows), lr=rate(update_index))


def save_state(model, tokenizer, optimizer, folder, step, order_hash):
    import torch
    folder.mkdir(parents=True, exist_ok=False)
    model.save_pretrained(folder, safe_serialization=True, max_shard_size='3GB')
    tokenizer.save_pretrained(folder)
    torch.save(optimizer.state_dict(), folder / 'optimizer.pt')
    torch.save({'cpu': torch.get_rng_state(), 'cuda': torch.cuda.get_rng_state_all() if model.device.type == 'cuda' else []}, folder / 'rng.pt')
    write(folder / 'training-state.json', dict(step=step, settings=SETTINGS, schedule_sha256=order_hash,
        optimizer_parameters_dtype='float32', resume_requires_exact_schedule_and_rng=True))


def reload_state(folder, device, step, order_hash):
    import torch
    from transformers import M2M100ForConditionalGeneration
    state = read(folder / 'training-state.json')
    if state['step'] != step or state['settings'] != SETTINGS or state['schedule_sha256'] != order_hash:
        raise ValueError('Checkpoint schedule identity differs')
    model = M2M100ForConditionalGeneration.from_pretrained(folder, local_files_only=True, token=False,
        dtype=torch.float32, attn_implementation='eager', trust_remote_code=False).to(device)
    optimizer = optimizer_for(model)
    optimizer.load_state_dict(torch.load(folder / 'optimizer.pt', map_location=device, weights_only=True))
    for state in optimizer.state.values():
        for key in ('exp_avg', 'exp_avg_sq'):
            if state[key].dtype != torch.float32 or not torch.isfinite(state[key]).all():
                raise ValueError('Invalid optimizer moment precision/values')
    rng = torch.load(folder / 'rng.pt', map_location='cpu', weights_only=True)
    torch.set_rng_state(rng['cpu'])
    if device.type == 'cuda':
        torch.cuda.set_rng_state_all(rng['cuda'])
    embedding = model.get_input_embeddings().weight
    if not all(w.data_ptr() == embedding.data_ptr() for w in (model.get_output_embeddings().weight,
            model.model.encoder.embed_tokens.weight, model.model.decoder.embed_tokens.weight)):
        raise ValueError('Reload broke shared embeddings')
    return model, optimizer


def probe(model, tokenizer, text):
    import torch
    model.eval()
    inputs = tokenizer(text, return_tensors='pt', truncation=False).to(model.device)
    with torch.inference_mode(), torch.autocast(model.device.type, dtype=torch.bfloat16, enabled=model.device.type == 'cuda'):
        return model.generate(**inputs, max_new_tokens=5, do_sample=False, num_beams=1,
            forced_bos_token_id=256053, suppress_tokens=[256204, 256205], use_cache=True)[0].tolist()


def mark_verified(folder, step):
    files = {p.name: dict(bytes=p.stat().st_size, sha256=sha(p)) for p in folder.iterdir() if p.is_file()}
    write(folder / 'checkpoint-verified.json', dict(step=step, files=files,
        reload_and_generation_verified=True, training_state_sha256=sha(folder / 'training-state.json')))


def edge_check(model, optimizer, prepared, collator, device):
    """Zero-update worst-shape backward; restore RNG and discard diagnostic gradients."""
    import torch
    cpu_rng, gpu_rng = torch.get_rng_state(), torch.cuda.get_rng_state_all()
    begin = time.monotonic()
    try:
        model.train()
        optimizer.zero_grad(set_to_none=True)
        indices = {max(range(len(prepared)), key=lambda i: len(prepared[i][field])) for field in ('input_ids','labels')}
        rows = ([prepared[i] for i in sorted(indices)] * 4)[:4]
        batch = {k: v.to(device) for k, v in collator(rows).items()}
        with torch.autocast('cuda', dtype=torch.bfloat16):
            loss = model(**batch, use_cache=False).loss
        if not torch.isfinite(loss): raise FloatingPointError('Nonfinite representative loss')
        loss.backward()
        norm = torch.nn.utils.clip_grad_norm_(model.parameters(),1.0,error_if_nonfinite=True)
        torch.cuda.synchronize()
        return dict(seconds=time.monotonic()-begin, loss=loss.item(), gradient_norm=float(norm),
                    optimizer_updates=0, populated_optimizer=bool(optimizer.state))
    finally:
        optimizer.zero_grad(set_to_none=True)
        torch.set_rng_state(cpu_rng)
        torch.cuda.set_rng_state_all(gpu_rng)


def generate(model, tokenizer, rows, arm, output, deadline):
    import torch
    model.eval()
    start = time.monotonic()
    for index, row in enumerate(rows, 1):
        remaining(deadline)
        record = dict(id=row['id'] + ':' + arm, case_id=row['id'], arm=arm, record_id=row['record_id'],
            work_id=row['work_id'], input_sha256=hashlib.sha256(row['source_text'].encode()).hexdigest(), sequence=index)
        begin = time.monotonic()
        try:
            inputs = tokenizer(row['source_text'], return_tensors='pt', truncation=False).to(model.device)
            with torch.inference_mode(), torch.autocast('cuda', dtype=torch.bfloat16):
                tokens = model.generate(**inputs, max_new_tokens=512, num_beams=1, do_sample=False,
                    forced_bos_token_id=256053, forced_eos_token_id=None, suppress_tokens=[256204, 256205], use_cache=True,
                    max_time=min(120, remaining(deadline)))
            values = tokens[0].tolist()
            complete = 2 < len(values) < 513 and values[1] == 256053 and values[-1] == tokenizer.eos_token_id
            translation=tokenizer.decode(values, skip_special_tokens=True, clean_up_tokenization_spaces=False)
            complete = complete and bool(translation.strip())
            record.update(status='success' if complete else 'failed', output_token_ids=values,
                translation=translation, failure=None if complete else 'empty_or_cap_or_time_without_EOS')
        except Exception as error:
            record.update(status='failed', translation='', error_type=type(error).__name__, error=str(error))
        record['seconds'] = time.monotonic() - begin
        with (output / 'predictions.jsonl').open('a', encoding='utf-8') as stream:
            stream.write(json.dumps(record, ensure_ascii=False) + '\n')
            stream.flush()
        emit('generation_case_recorded', arm=arm, completed=index, scheduled=24, status=record['status'], seconds=record['seconds'])
        if record.get('error_type'):
            raise RuntimeError('Generation runtime failure; first attempt recorded')
    return time.monotonic() - start


def run(folder, output, deadline, program_start, resume=None):
    import torch
    from transformers import AutoTokenizer, DataCollatorForSeq2Seq, M2M100ForConditionalGeneration
    from huggingface_hub import hf_hub_download
    import shutil
    output.mkdir(parents=True, exist_ok=True)
    state = dict(status='incomplete', step=0, model=MODEL, revision=REVISION, settings=SETTINGS,
        train_sha256=TRAIN_SHA, dev_sha256=DEV_SHA, runner_sha256=sha(__file__), quality_validated=False)
    write(output / 'run.json', state)
    torch.set_num_threads(8)
    torch.manual_seed(3407)
    torch.cuda.manual_seed_all(3407)
    device = torch.device('cuda')
    tokenizer = AutoTokenizer.from_pretrained(folder / 'tokenizer', local_files_only=True,
        token=False, trust_remote_code=False, src_lang='pal_Latn', tgt_lang='pes_Arab')
    train, prepared, dev = token_rows(folder, tokenizer)
    groups = schedule()
    order_hash = hashlib.sha256(json.dumps([[train[i]['id'] for i in group] for group in groups]).encode()).hexdigest()
    write(output / 'schedule.json', dict(sha256=order_hash, parent_ids=[[train[i]['id'] for i in group] for group in groups],
        total_supervised_tokens=sum(sum(len(prepared[i]['labels']) for i in g) for g in groups)))
    collator = DataCollatorForSeq2Seq(tokenizer, padding=True, label_pad_token_id=-100, return_tensors='pt')
    if resume is None:
        emit('base_download_started', bytes=WEIGHTS_BYTES, destination='server_ephemeral_only')
        base = folder.parent / 'base'
        base.mkdir()
        weights = Path(hf_hub_download(MODEL, 'pytorch_model.bin', revision=REVISION, token=False, local_dir=base))
        if weights.stat().st_size != WEIGHTS_BYTES or sha(weights) != WEIGHTS_SHA:
            raise ValueError('Pretrained weight identity mismatch')
        for name in ('config.json', 'generation_config.json'): shutil.copyfile(folder/name,base/name)
        model = M2M100ForConditionalGeneration.from_pretrained(base, local_files_only=True, token=False,
            use_safetensors=False, weights_only=True, trust_remote_code=False, dtype=torch.float32, attn_implementation='eager')
        initialize(model, tokenizer, read(folder/'tokenizer-evidence.json'), read(folder/'special_tokens_map.json')['additional_special_tokens'])
        model.to(device)
        optimizer = optimizer_for(model)
        initial_rows = model.get_input_embeddings().weight[256206:].detach().cpu().clone()
        emit('base_initialized',parameters=sum(p.numel() for p in model.parameters()),vocabulary=len(tokenizer))
        edge_check(model,optimizer,prepared,collator,device)
        baseline_seconds = generate(model,tokenizer,dev,'initialized',output,deadline)
        torch.manual_seed(3407)
        torch.cuda.manual_seed_all(3407)
        start_step = 0
    else:
        canary_record = read(resume/'nllb/canary.json')
        for name in ('predictions.jsonl','training.jsonl','canary.json'):
            shutil.copyfile(resume/'nllb'/name,output/name)
        baseline_seconds = canary_record['baseline_seconds']
        model,optimizer = reload_state(resume/'nllb/model',device,20,order_hash)
        start_step = 20
        projection=canary_record['max_steady_update_seconds']*1.5*680+baseline_seconds*1.5+canary_record['save_reload_seconds']*2+120
        if projection > remaining(deadline): raise TimeoutError('Recovered canary projection does not fit continuation')
        emit('continuation_admitted',start_step=20,projected_seconds=projection,remaining_seconds=remaining(deadline))
    os.environ['HF_HUB_OFFLINE']='1'
    os.environ['TRANSFORMERS_OFFLINE']='1'
    model.config.use_cache=False
    durations = []
    model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={'use_reentrant': False})
    for step, group in enumerate(groups, 1):
        if step <= start_step: continue
        remaining(deadline)
        begin = time.monotonic()
        metrics = update(model, optimizer, [prepared[i] for i in group], collator, step, device)
        torch.cuda.synchronize()
        durations.append(time.monotonic() - begin)
        state.update(step=step, elapsed_seconds=time.monotonic() - program_start)
        write(output / 'run.json', state)
        with (output / 'training.jsonl').open('a', encoding='utf-8') as stream:
            stream.write(json.dumps(dict(step=step, seconds=durations[-1], **metrics)) + '\n')
        if step <= 20 or step % 10 == 0:
            emit('training_update', step=step, total=700, seconds=durations[-1], **metrics)
        if step == 20:
            before_reload = time.monotonic()
            edge = edge_check(model,optimizer,prepared,collator,device)
            embedding=model.get_input_embeddings().weight
            deltas=(embedding[256206:].detach().cpu()-initial_rows).abs().sum(dim=1)
            moments=optimizer.state[embedding]['exp_avg'][256206:]
            if not torch.isfinite(deltas).all() or not (deltas>0).all() or not torch.isfinite(moments).all():
                raise ValueError('Appended rows did not receive finite updates')
            del embedding,moments
            canary = folder.parent / 'canary-state'
            expected_probe = probe(model, tokenizer, train[0]['text'])
            expected_rows = model.get_input_embeddings().weight[256206:].detach().cpu().clone()
            save_state(model, tokenizer, optimizer, canary, step, order_hash)
            del optimizer, model
            gc.collect()
            torch.cuda.empty_cache()
            model, optimizer = reload_state(canary, device, step, order_hash)
            if (probe(model, tokenizer, train[0]['text']) != expected_probe
                    or not torch.equal(model.get_input_embeddings().weight[256206:].detach().cpu(), expected_rows)):
                raise ValueError('Canary save/reload changed generation or appended rows')
            mark_verified(canary,20)
            model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={'use_reentrant': False})
            reload_seconds = time.monotonic() - before_reload
            canary_record = dict(status='passed', completed_step=20, remaining_updates=680,
                max_steady_update_seconds=max(durations[5:]), remaining_seconds=remaining(deadline),
                baseline_seconds=baseline_seconds, save_reload_seconds=reload_seconds,
                gpu_peak_bytes=torch.cuda.max_memory_allocated(), source_gradient_not_isolated=True,
                appended_row_abs_deltas=deltas.tolist(), representative_with_optimizer=edge)
            write(output / 'canary.json', canary_record)
            canary.rename(output/'model')
            state.update(status='canary_complete',step=20,elapsed_seconds=time.monotonic()-program_start)
            write(output/'run.json',state)
            emit('canary_complete_pending_cloud_recovery',**canary_record)
            return
    final = folder.parent / 'final-state'
    expected_probe = probe(model, tokenizer, train[0]['text'])
    save_state(model, tokenizer, optimizer, final, 700, order_hash)
    del optimizer, model
    gc.collect()
    torch.cuda.empty_cache()
    model, optimizer = reload_state(final, device, 700, order_hash)
    del optimizer
    if probe(model, tokenizer, train[0]['text']) != expected_probe:
        raise ValueError('Final model generation changed after reload')
    mark_verified(final,700)
    final.rename(output/'model')
    generate(model, tokenizer, dev, 'trained', output, deadline)
    state.update(status='completed', step=700, completed_parent_exposures=11185,
        baseline_seconds=baseline_seconds, elapsed_seconds=time.monotonic() - program_start,
        gpu_peak_bytes=torch.cuda.max_memory_allocated())
    write(output / 'run.json', state)
    emit('scientific_run_complete', **state)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--deadline', required=True, type=float)
    parser.add_argument('--program-start', required=True, type=float)
    parser.add_argument('--resume',type=Path)
    args = parser.parse_args()
    run(args.package, args.output, args.deadline, args.program_start,args.resume)
