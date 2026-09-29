"""Bounded, anonymous tokenizer acquisition and offline census; never load model weights."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import shutil
import sys
import unicodedata
import urllib.request

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
CACHE = ROOT / 'resources/local/nllb-tokenizer-20260928'
BUNDLE = ROOT / 'resources/local/cloud-pilot-qualified-20260927'
MODEL = 'facebook/nllb-200-distilled-1.3B'
REVISION = '7be3e24664b38ce1cac29b8aeed6911aa0cf0576'
FILES = ('config.json', 'generation_config.json', 'tokenizer.json',
         'tokenizer_config.json', 'special_tokens_map.json')
TRAIN_SHA = '15b13f63b518882fe82697ff27cc1656011f3868a318f910bb9de9e2422925dc'
DEV_SHA = '06ac58310bf67767fae4124d8e935c808d15debcd8daebce07b583937cd97182'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def write_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def fetch():
    """Only five public passive assets, fixed revision, no HF login/cache or model files."""
    CACHE.mkdir(parents=True, exist_ok=True)
    receipt_path = OUT / 'asset-receipt.json'
    if receipt_path.exists():
        verify_assets()
        return
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    assets = {}
    for name in FILES:
        url = f'https://huggingface.co/{MODEL}/resolve/{REVISION}/{name}'
        with opener.open(url, timeout=45) as response:
            data = response.read(32 * 1024 * 1024 + 1)
        if len(data) > 32 * 1024 * 1024:
            raise ValueError('Passive asset exceeds size bound: ' + name)
        json.loads(data)
        (CACHE / name).write_bytes(data)
        assets[name] = {'sha256': sha(data), 'bytes': len(data), 'url': url}
        print('fetched', name, len(data), flush=True)
    write_json(receipt_path, {'model': MODEL, 'revision': REVISION,
               'retrieved_utc': datetime.now(timezone.utc).isoformat(),
               'anonymous': True, 'model_weights_downloaded': False, 'files': assets})


def verify_assets():
    receipt = json.loads((OUT / 'asset-receipt.json').read_bytes())
    assert receipt['revision'] == REVISION and set(receipt['files']) == set(FILES)
    for name, expected in receipt['files'].items():
        data = (CACHE / name).read_bytes()
        assert sha(data) == expected['sha256'] and len(data) == expected['bytes'], name
    return receipt


def canonical_text(text):
    return ' '.join(unicodedata.normalize('NFKC', text).split())


def format_spacing(text):
    # Explicit stock-normalizer behavior; original corpus bytes are never rewritten.
    return canonical_text(text.replace('\u200c', ' ').replace('\u200e', ' '))


def text_evidence(tokenizer, text):
    backend = tokenizer.backend_tokenizer
    encoded = backend.encode(text, add_special_tokens=False)
    ids = encoded.ids
    decoded = backend.decode(ids, skip_special_tokens=False)
    unknown = [{'span': text[a:b], 'start': a, 'end': b}
               for token, (a, b) in zip(ids, encoded.offsets)
               if token == tokenizer.unk_token_id]
    markers = '[]{}()<>?*†‡…'
    return {'text_sha256': sha(text.encode()), 'content_tokens': len(ids),
            'tokens_with_language_and_eos': len(ids) + 2,
            'unknown_count': len(unknown), 'unknown_spans': unknown,
            'roundtrip_exact': decoded == text,
            'roundtrip_nfkc_whitespace': canonical_text(decoded) == canonical_text(text),
            'roundtrip_declared_format_spacing': format_spacing(decoded) == format_spacing(text),
            'marker_counts_preserved': {c: canonical_text(text).count(c) for c in markers}
                == {c: canonical_text(decoded).count(c) for c in markers},
            'decoded_sha256': sha(decoded.encode())}


def summarize(records):
    sizes = sorted(r['tokens_with_language_and_eos'] for r in records)
    return {'count': len(records), 'max_tokens': max(sizes),
            'median_tokens': sizes[len(sizes) // 2],
            'p95_tokens': sizes[(len(sizes) * 95 + 99) // 100 - 1],
            'above_512': sum(n > 512 for n in sizes), 'above_1024': sum(n > 1024 for n in sizes),
            'unknown_tokens': sum(r['unknown_count'] for r in records),
            'rows_with_unknown': sum(bool(r['unknown_count']) for r in records),
            'exact_roundtrips': sum(r['roundtrip_exact'] for r in records),
            'nfkc_whitespace_roundtrips': sum(r['roundtrip_nfkc_whitespace'] for r in records),
            'declared_format_spacing_roundtrips': sum(r['roundtrip_declared_format_spacing'] for r in records),
            'rows_with_marker_change': sum(not r['marker_counts_preserved'] for r in records)}


def extend_characters(stock, evidence, config):
    """Append TRAIN-observed missing BPE characters; keep every merge and original ID."""
    from tokenizers import Tokenizer
    doc = json.loads((CACHE / 'tokenizer.json').read_bytes())
    vocab = doc['model']['vocab']
    assert doc['model']['type'] == 'BPE' and set(vocab.values()) == set(range(len(vocab)))
    unknown = Counter(u['span'] for r in evidence if r['split'] == 'train'
                      for side in ('source', 'target') for u in r[side]['unknown_spans'])
    assert unknown and len(unknown) <= 16 and all(len(c) == 1 for c in unknown)
    original_size = len(vocab)
    reserved = []
    # Preserve unrepresented model rows; never shrink the pretrained embedding table.
    while len(vocab) < config['vocab_size']:
        name = f'<reserved_model_{len(vocab)}>'
        vocab[name] = len(vocab)
        reserved.append(name)
    added = {}
    for char in sorted(unknown):
        assert char not in vocab
        added[char] = len(vocab)
        vocab[char] = len(vocab)
    backend = Tokenizer.from_str(json.dumps(doc, ensure_ascii=False))
    # Ordinary AddedToken insertion splits word interiors under Metaspace decoding.
    # Extending the BPE character alphabet preserves that boundary instead.
    for sample in ('pad \u01f0adag ud \u01f0an', '\u00ab\u0633\u0644\u0627\u0645\u00bb', 'a\u2014b'):
        ids = backend.encode(sample, add_special_tokens=False).ids
        assert backend.decode(ids, skip_special_tokens=False) == sample and 3 not in ids
    destination = CACHE / 'extended-tokenizer'
    destination.mkdir(exist_ok=True)
    for name in FILES:
        if name != 'tokenizer.json':
            shutil.copyfile(CACHE / name, destination / name)
    backend.save(str(destination / 'tokenizer.json'))
    return destination, {'train_only_missing_characters': added,
                         'train_unknown_span_counts': dict(unknown),
                         'original_bpe_vocab_size': original_size,
                         'preserved_model_rows': config['vocab_size'],
                         'reserved_model_tokens': reserved,
                         'bpe_merges_and_normalizer_unchanged': True}


def run():
    receipt = verify_assets()
    for key in ('HF_HUB_OFFLINE', 'TRANSFORMERS_OFFLINE', 'HF_HUB_DISABLE_TELEMETRY',
                'HF_HUB_DISABLE_IMPLICIT_TOKEN'):
        os.environ[key] = '1'
    # Reuse the established project dependency fallback; no package installation.
    sys.path.append(str(ROOT / 'resources/local/hf-client-venv/Lib/site-packages'))
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(str(CACHE), local_files_only=True,
                                             trust_remote_code=False, token=False)
    assert tokenizer.is_fast, 'Offset-based unknown inspection requires fast tokenizer'
    train_data = (BUNDLE / 'train.jsonl').read_bytes()
    assert sha(train_data) == TRAIN_SHA
    train = [json.loads(line) for line in train_data.splitlines() if line.strip()]
    assert len(train) == len({r['id'] for r in train}) == 2237
    inputs = {'train': {'sha256': TRAIN_SHA, 'rows': len(train)}}
    all_rows = []
    for row in train:
        assert row['source_language'] == 'pal' and row['target_language'] == 'fa'
        all_rows.append({'id': row['id'], 'work_id': row['work_id'], 'split': 'train',
                         'source': text_evidence(tokenizer, row['text']),
                         'target': text_evidence(tokenizer, row['target'])})
        if len(all_rows) % 500 == 0:
            print('TRAIN rows checked', len(all_rows), flush=True)
    dev_path = ROOT / 'experiments/dev-diagnostic-20260927/inputs.jsonl'
    dev_data = dev_path.read_bytes()
    assert sha(dev_data) == DEV_SHA
    dev = [json.loads(line) for line in dev_data.splitlines() if line.strip()]
    assert len(dev) == len({r['id'] for r in dev}) == 24
    inputs['dev_sources_only'] = {'sha256': sha(dev_data), 'rows': len(dev)}
    assert not ({r['text'] for r in train} & {r['source_text'] for r in dev})
    for row in dev:
        assert 'target' not in row and 'references' not in row
        all_rows.append({'id': row['id'], 'work_id': row['work_id'], 'split': 'dev',
                         'source': text_evidence(tokenizer, row['source_text'])})
    original_vocab = tokenizer.get_vocab()
    original_special_ids = set(tokenizer.all_special_ids)
    stock_summary = {'train_source': summarize([r['source'] for r in all_rows if r['split'] == 'train']),
                     'train_target': summarize([r['target'] for r in all_rows if r['split'] == 'train']),
                     'dev_source': summarize([r['source'] for r in all_rows if r['split'] == 'dev'])}
    config = json.loads((CACHE / 'config.json').read_bytes())
    extended_path, extension = extend_characters(tokenizer, all_rows, config)
    tokenizer = AutoTokenizer.from_pretrained(str(extended_path), local_files_only=True,
                                             trust_remote_code=False, token=False)
    original_size = len(tokenizer)
    assert tokenizer.convert_tokens_to_ids('pes_Arab') != tokenizer.unk_token_id
    assert tokenizer.convert_tokens_to_ids('pal_Latn') == tokenizer.unk_token_id
    tokenizer.add_special_tokens({'extra_special_tokens':
                                  [*extension['reserved_model_tokens'], 'pal_Latn']},
                                  replace_extra_special_tokens=False)
    # The return count also includes existing vocabulary entries newly marked special.
    assert len(tokenizer) == original_size + 1
    current_vocab = tokenizer.get_vocab()
    assert all(current_vocab[t] == i for t, i in original_vocab.items())
    assert original_special_ids <= set(tokenizer.all_special_ids)
    tokenizer.src_lang, tokenizer.tgt_lang = 'pal_Latn', 'pes_Arab'
    sample = train[0]
    serialized = tokenizer(sample['text'], text_target=sample['target'], truncation=False)
    assert serialized['input_ids'][0] == tokenizer.convert_tokens_to_ids('pal_Latn')
    assert serialized['labels'][0] == tokenizer.convert_tokens_to_ids('pes_Arab')
    assert serialized['input_ids'][-1] == serialized['labels'][-1] == tokenizer.eos_token_id
    adapted = CACHE / 'adapted-language-token'
    tokenizer.save_pretrained(adapted)
    reloaded = AutoTokenizer.from_pretrained(str(adapted), local_files_only=True,
                                            trust_remote_code=False, token=False,
                                            src_lang='pal_Latn', tgt_lang='pes_Arab')
    assert reloaded(sample['text'], text_target=sample['target'], truncation=False) == serialized
    assert len(reloaded) == original_size + 1
    reloaded_vocab = reloaded.get_vocab()
    assert all(reloaded_vocab[t] == i for t, i in original_vocab.items())
    assert original_special_ids <= set(reloaded.all_special_ids)
    assert len(reloaded) > config['vocab_size']
    # Recompute every record with the final extended tokenizer; use no held-out labels.
    by_train = {r['id']: r for r in train}
    by_dev = {r['id']: r for r in dev}
    for record in all_rows:
        row = by_train[record['id']] if record['split'] == 'train' else by_dev[record['id']]
        source = row['text'] if record['split'] == 'train' else row['source_text']
        previous = record['source']
        record['source'] = text_evidence(reloaded, source)
        if not previous['unknown_count']:
            assert record['source']['decoded_sha256'] == previous['decoded_sha256']
        if record['split'] == 'train':
            previous = record['target']
            record['target'] = text_evidence(reloaded, row['target'])
            if not previous['unknown_count']:
                assert record['target']['decoded_sha256'] == previous['decoded_sha256']
        for side in ('source', 'target'):
            if side in record:
                assert record[side]['unknown_count'] == 0, record['id']
                assert record[side]['roundtrip_declared_format_spacing'], record['id']
                assert record[side]['marker_counts_preserved'], record['id']
    checks = {'new_source_id': tokenizer.convert_tokens_to_ids('pal_Latn'),
              'persian_target_id': tokenizer.convert_tokens_to_ids('pes_Arab'),
              'original_vocab_size': len(original_vocab), 'adapted_vocab_size': len(reloaded),
              'language_token_save_reload': True,
              'all_original_ids_and_special_tags_preserved': True,
              'model_embedding_resize_and_learning': 'NOT_TESTED'}
    summaries = {'train_source': summarize([r['source'] for r in all_rows if r['split'] == 'train']),
                 'train_target': summarize([r['target'] for r in all_rows if r['split'] == 'train']),
                 'dev_source': summarize([r['source'] for r in all_rows if r['split'] == 'dev'])}
    write_json(OUT / 'result.json', {'status': 'CENSUS_COMPLETE_NOT_TRAINING_ADMISSION',
               'completed_utc': datetime.now(timezone.utc).isoformat(), 'inputs': inputs,
               'asset_receipt_sha256': sha((OUT / 'asset-receipt.json').read_bytes()),
               'script_sha256': sha(Path(__file__).read_bytes()), 'model_config':
               config,
               'versions': {n: importlib.metadata.version(n) for n in
                            ('transformers', 'tokenizers', 'huggingface_hub')},
               'language_serialization': checks, 'extension': extension,
               'stock_summary': stock_summary, 'summary': summaries,
               'model_weights_loaded': False, 'heldout_targets_read': False,
               'rows': all_rows})
    print(json.dumps({'summary': summaries, 'language_serialization': checks}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fetch', action='store_true', help='Fetch five pinned public passive assets')
    args = parser.parse_args()
    if args.fetch:
        fetch()
    run()
