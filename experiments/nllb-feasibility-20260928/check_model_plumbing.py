"""CPU-only random tiny M2M100 check. No pretrained weights, cloud, or quality test."""
import hashlib
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
CACHE = ROOT / 'resources/local/nllb-tokenizer-20260928'


def run():
    for name in ('HF_HUB_OFFLINE', 'TRANSFORMERS_OFFLINE', 'HF_HUB_DISABLE_TELEMETRY',
                 'HF_HUB_DISABLE_IMPLICIT_TOKEN'):
        os.environ[name] = '1'
    sys.path.append(str(ROOT / 'resources/local/hf-client-venv/Lib/site-packages'))
    import torch
    from transformers import AutoTokenizer, DataCollatorForSeq2Seq, M2M100Config, M2M100ForConditionalGeneration
    torch.set_num_threads(2)
    torch.manual_seed(3407)
    evidence = json.loads((OUT / 'result.json').read_bytes())
    assert all(s['unknown_tokens'] == 0 for s in evidence['summary'].values())
    tokenizer = AutoTokenizer.from_pretrained(str(CACHE / 'adapted-language-token'),
        local_files_only=True, token=False, trust_remote_code=False,
        src_lang='pal_Latn', tgt_lang='pes_Arab')
    original_size = evidence['model_config']['vocab_size']
    source_id = tokenizer.convert_tokens_to_ids('pal_Latn')
    target_id = tokenizer.convert_tokens_to_ids('pes_Arab')
    config = M2M100Config(vocab_size=original_size, d_model=8, encoder_layers=1,
        decoder_layers=1, encoder_attention_heads=1, decoder_attention_heads=1,
        encoder_ffn_dim=16, decoder_ffn_dim=16, max_position_embeddings=32,
        dropout=0.0, attention_dropout=0.0, activation_dropout=0.0,
        encoder_layerdrop=0.0, decoder_layerdrop=0.0,
        pad_token_id=tokenizer.pad_token_id, eos_token_id=tokenizer.eos_token_id,
        bos_token_id=tokenizer.bos_token_id, decoder_start_token_id=tokenizer.eos_token_id)
    model = M2M100ForConditionalGeneration(config)
    original = model.get_input_embeddings().weight.detach().clone()
    assert original.shape[0] == original_size and len(tokenizer) > original_size
    model.resize_token_embeddings(len(tokenizer), mean_resizing=False)
    language_names = json.loads((CACHE / 'special_tokens_map.json').read_bytes())['additional_special_tokens']
    language_ids = [tokenizer.convert_tokens_to_ids(name) for name in language_names]
    assert len(language_ids) == len(set(language_ids)) and all(i < original_size for i in language_ids)
    content_mask = torch.ones(original_size, dtype=torch.bool)
    content_mask[[i for i in tokenizer.all_special_ids if i < original_size]] = False
    with torch.no_grad():
        embedding = model.get_input_embeddings().weight
        for char_id in evidence['extension']['train_only_missing_characters'].values():
            assert char_id >= original_size
            embedding[char_id].copy_(original[content_mask].mean(dim=0))
        embedding[source_id].copy_(original[language_ids].mean(dim=0))
    assert torch.equal(embedding[:original_size], original)
    tied = [model.get_output_embeddings().weight, model.model.encoder.embed_tokens.weight,
            model.model.decoder.embed_tokens.weight]
    assert all(w.data_ptr() == embedding.data_ptr() for w in tied)
    rows = [{'input_ids': [source_id, 8, 2], 'attention_mask': [1, 1, 1],
             'labels': [target_id, 9, 2]},
            {'input_ids': [source_id, 8, 10, 2], 'attention_mask': [1, 1, 1, 1],
             'labels': [target_id, 9, 10, 2]}]
    batch = DataCollatorForSeq2Seq(tokenizer, model=model, padding=True,
        label_pad_token_id=-100, return_tensors='pt')(rows)
    assert batch['labels'].tolist() == [[target_id, 9, 2, -100], [target_id, 9, 10, 2]]
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3)
    loss = model(**batch).loss
    assert torch.isfinite(loss)
    loss.backward()
    source_gradient = embedding.grad[source_id].abs().sum().item()
    assert source_gradient > 0 and torch.isfinite(embedding.grad).all()
    optimizer.step()
    optimizer.zero_grad(set_to_none=True)
    model.eval()
    inputs = {k: v for k, v in batch.items() if k in ('input_ids', 'attention_mask')}
    reserved_ids = [tokenizer.convert_tokens_to_ids(t) for t in evidence['extension']['reserved_model_tokens']]
    generation = dict(max_new_tokens=5, forced_bos_token_id=target_id,
                      do_sample=False, suppress_tokens=reserved_ids)
    with torch.no_grad():
        before = model.generate(**inputs, **generation)
    assert (before[:, 1] == target_id).all()
    folder = CACHE / 'random-tiny-model-check'
    model.save_pretrained(folder, safe_serialization=True)
    reloaded = M2M100ForConditionalGeneration.from_pretrained(folder, local_files_only=True,
                                                            token=False).eval()
    with torch.no_grad():
        after = reloaded.generate(**inputs, **generation)
    assert torch.equal(before, after)
    assert reloaded.get_input_embeddings().weight.data_ptr() == reloaded.get_output_embeddings().weight.data_ptr()
    result = {'status': 'PASS_RANDOM_TINY_CPU_ONLY', 'torch': torch.__version__,
              'tokenizer_evidence_sha256': hashlib.sha256((OUT / 'result.json').read_bytes()).hexdigest(),
              'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'original_embedding_rows': original_size, 'final_embedding_rows': len(tokenizer),
              'original_rows_preserved_before_training': True, 'input_output_encoder_decoder_tied': True,
              'source_initialization': 'mean of original language-tag embeddings',
              'character_initialization': 'mean of original non-special embedding rows',
              'source_language_count': len(language_ids), 'finite_loss': loss.item(),
              'source_row_gradient_abs_sum': source_gradient, 'padding_only_mask': True,
              'forced_persian_bos': True, 'save_reload_generation_identical': True,
              'limitations': ['Random tiny CPU model, synthetic token pairs and one update only.',
                  'No pretrained weights, translation quality, real GPU memory or throughput tested.',
                  'New source-row gradient includes the tied output-head contribution; not isolated source conditioning.']}
    (OUT / 'model-check.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    run()
