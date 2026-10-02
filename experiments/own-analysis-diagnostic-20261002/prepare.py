"""Freeze three source-only direct/own-analysis comparisons; local bytes only."""
import hashlib
import json
from pathlib import Path
import sys
import unicodedata

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUT = ROOT / 'resources/local/own-analysis-diagnostic-20261002'
CASES = ('KANHERI01', 'AMOL1', 'BERLIN6')
ORDERS = ('DAP', 'APD', 'DAP')
ANALYSIS = ('Analyze the following Middle Persian source in scholarly Latin transcription. '
            'In at most120 words, identify supported predicates, participants and their roles, '
            'polarity, time, quantities and unresolved readings. Distinguish obligation from '
            'completed events. Treat unknown readings and alternative meanings as uncertain. '
            'Do not translate, invent missing context or force a confident interpretation.\nSource:\n{text}')
SUFFIX = ('\n\nTentative analysis from your first attempt follows. It may contain mistakes. '
          'Use the original source above to check it; preserve unresolved readings and uncertainty. '
          'Return only the complete Persian translation.\nFirst analysis (verbatim):\n')


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))+'\n').encode('utf8')


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def build():
    sys.path.insert(0, str(ROOT))
    from cloud_pilot.bundle import PROMPT, TOKENIZER_HASHES
    from tokenizers import Tokenizer
    from jinja2.sandbox import ImmutableSandboxedEnvironment
    q = json.loads((HERE/'source-qualification.json').read_bytes())
    pins = dict(q['artifact_sha256'])
    for path, digest in pins.items():
        if sha((ROOT/path).read_bytes()) != digest: raise ValueError('Source changed: '+path)
    if tuple(c['case_id'] for c in q['cases']) != CASES or q['paid_run_admitted'] or q['training_admitted']:
        raise ValueError('Qualification identities/admission changed')
    selected = {}
    for i, line in enumerate((ROOT/q['derived_pairs']).read_bytes().splitlines(), 1):
        r = json.loads(line)
        if r['id'] in {c['pair_id'] for c in q['cases']}:
            if r['id'] in selected: raise ValueError('Duplicate pair')
            selected[r['id']] = (i, r['learning'])
    historical = [json.loads(l) for l in (ROOT/'experiments/train-audit-20260927/qualified-v1/train.jsonl').read_bytes().splitlines()]
    later = {json.loads(l)['id'] for l in (ROOT/'resources/local/training-ready-v2-20260929/data/train.jsonl').read_bytes().splitlines()}
    def normalized(s): return ' '.join(unicodedata.normalize('NFC', s).casefold().split())
    tokroot = ROOT/'resources/local/cloud-pilot-qualified-20260927/tokenizer'
    for name, pin in TOKENIZER_HASHES.items():
        pins[str((tokroot/name).relative_to(ROOT))] = pin
        if sha((tokroot/name).read_bytes()) != pin: raise ValueError('Publisher tokenizer changed')
    tokenizer = Tokenizer.from_file(str(tokroot/'tokenizer.json'))
    template = ImmutableSandboxedEnvironment().from_string((tokroot/'chat_template.jinja').read_text('utf8'))
    config = json.loads((tokroot/'tokenizer_config.json').read_bytes())
    prompts, private = [], []
    for c in q['cases']:
        number, pair = selected[c['pair_id']]
        if number != c['derived_line']: raise ValueError('Pair location changed')
        for field in ('source', 'target'):
            text = pair[field]
            if len(text) != c[field+'_codepoints'] or sha(text.encode()) != c[field+'_sha256']:
                raise ValueError('Qualified span changed')
        source = pair['source']
        direct = PROMPT.format(text=source)
        texts = {'D': direct, 'A': ANALYSIS.format(text=source), 'P': direct+SUFFIX}
        for condition, prompt in texts.items():
            rendered = template.render(messages=[{'role':'user','content':prompt}], add_generation_prompt=True,
                enable_thinking=False, bos_token=config['bos_token'], tools=None)
            ids = tokenizer.encode(rendered, add_special_tokens=False).ids
            # Reserve 256 generated analysis tokens and the 256 final tokens for P;
            # actual dynamic rendering is still a mandatory runtime no-truncation gate.
            reserve = 512 if condition == 'P' else 256
            if len(ids)+reserve > 2048 or tokenizer.token_to_id('<unk>') in ids:
                raise ValueError('Static template capacity failure')
            prompts.append(dict(id=c['case_id']+'-'+condition, case_id=c['case_id'], condition=condition,
                prompt=prompt, prompt_tokens=len(ids), rendered_sha256=sha(rendered.encode()),
                has_unknown_token=False, dependency_id=c['case_id']+'-A' if condition=='P' else None))
        normalized_source = normalized(source)
        hits = [r['id'] for r in historical if normalized_source == normalized(r['text'])
                or (len(normalized_source.split()) >= 6 and
                    ' '+normalized_source+' ' in ' '+normalized(r['text'])+' ')]
        private.append(dict(c, source=source, reference=pair['target'], reference_language=pair['context']['target_language'],
            historical_source_screen=dict(method='NFC whitespace casefold source equality or >=6-word whole-span containment', hits=hits),
            in_later_selected1536=c['pair_id'] in later, step280_exposure='NOT_ESTABLISHED',
            reference_status='PROVISIONAL_NOT_EXPERT_GOLD', complete_acceptance='All supported substantive meaning, with faithful unresolved terms; uncertain adjudication never a pass.'))
    outputs = {'model-inputs.jsonl':b''.join(encoded(p) for p in prompts),
               'review-constraints.jsonl':b''.join(encoded(p) for p in private)}
    for path in (Path(__file__), HERE/'source-qualification.json', HERE/'PROTOCOL.md', ROOT/'cloud_pilot/bundle.py',
                 ROOT/'experiments/dose-acquisition-20260930/live-execution/BLIND-REVIEW.md'):
        pins[str(path.relative_to(ROOT))] = sha(path.read_bytes())
    manifest = dict(protocol='own-analysis-v1', cases=list(CASES), planned_outputs=9, final_denominator_per_arm=3,
        schedule=[c+'-'+a for c,o in zip(CASES,ORDERS) for a in o], input_evidence='SOURCE_ONLY_BOTH_ARMS',
        static_P_is_dynamic_prefix_only=True, dependency_policy='Success nonempty uncapped A only; otherwise journal skipped_dependency P; unexpected exceptions halt; no retries.',
        witnesses=3, conservative_broader_groups=2, artifact_sha256=pins,
        local_outputs={n:dict(bytes=len(b),sha256=sha(b)) for n,b in outputs.items()},
        max_prompt_tokens=max(r['prompt_tokens'] for r in prompts), max_new_tokens=256, context_limit=2048,
        max_P_static_reserved_tokens=max(r['prompt_tokens']+512 for r in prompts if r['condition']=='P'),
        training=False, paid_run_admitted=False, expert_certified=False, unseen_claim_allowed=False,
        planning_status='FROZEN_PACKET_RUNTIME_AND_ASTRA_REVIEW_PENDING')
    return outputs, manifest


def main():
    outputs, manifest = build()
    if sys.argv[1:] == ['--write']:
        if OUT.exists() or (HERE/'packet-manifest.json').exists():
            raise FileExistsError('Freeze once; use --check, never overwrite the packet')
        OUT.mkdir(parents=True)
        for name, raw in outputs.items(): (OUT/name).write_bytes(raw)
        (HERE/'packet-manifest.json').write_bytes(encoded(manifest))
    elif sys.argv[1:] == ['--check']:
        if json.loads((HERE/'packet-manifest.json').read_bytes()) != manifest:
            raise ValueError('Manifest replay differs')
        for name, raw in outputs.items():
            if (OUT/name).read_bytes() != raw: raise ValueError('Output replay differs')
    else: raise ValueError('Use --write once or --check')
    print(json.dumps(dict(status='pass',frozen_cases=3,scheduled_slots=9,
        maximum_static_prompt_tokens=manifest['max_prompt_tokens'],cloud_performed=False,weights_downloaded=False)))


if __name__ == '__main__': main()
