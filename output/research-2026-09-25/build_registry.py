"""Assemble the checked research records; standard library only, no network."""
import json
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
LANES = [
    'academic-resources.json', 'philology-requirements.json',
    'interdisciplinary-methods.json', 'methods-and-models.json',
    'evaluation-evidence.json', 'ancient-additional-records.json',
]
records = []
for filename in LANES:
    rows = json.loads((ROOT / filename).read_text(encoding='utf-8-sig'))
    assert isinstance(rows, list), filename
    for row in rows:
        for key in ('id', 'title', 'category', 'source_url', 'limitations', 'checked_date'):
            assert row.get(key), (filename, key)
        parsed = urlparse(row['source_url'])
        assert parsed.scheme in ('http', 'https') and parsed.netloc, row['id']
        assert row['checked_date'] == '2026-09-25', row['id']
        records.append(dict(row, source_record_file=filename))
assert len({row['id'] for row in records}) == len(records), 'Duplicate record IDs'
database = {
    'schema_version': 1,
    'checked_date': '2026-09-25',
    'purpose': 'Evidence registry for Pahlavi text translation research; not a training corpus.',
    'record_count': len(records),
    'count_interpretation': 'Source/resource records, not independent studies. Several records concern one project or overlapping evidence.',
    'scope': 'Primary research, public code/cards, philology, institutional resources, evaluation and explicitly anecdotal leads.',
    'verification_scope': 'Literature and static inspection; no local model experiment or bulk corpus acquisition.',
    'records': records,
}
(ROOT / 'research-database.json').write_text(json.dumps(database, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
lines = [
    '# Research evidence index', '',
    f'Checked 25 September 2026. **{len(records)} evidence records** across {len(LANES)} source registries.', '',
    'These are records, not a count of independent studies or acquired datasets. Project overlap is intentional: resources, methodology and language requirements can concern the same institution. The JSON retains each source record, evidence, limitations, access notes and originating file.', '',
    '[Decision and hardware summary](FOUNDATIONAL_RESEARCH_CHECKPOINT.md) · [Machine-readable database](research-database.json)', '',
    '## Coverage and detailed reports', '',
    '- [Academic corpora and dictionaries](academic-resources.md)',
    '- [Philology and meaning requirements](philology-requirements.md)',
    '- [Ancient translation methods](deep-ancient-methods.md)',
    '- [Other ancient-text projects and linguistic tools](interdisciplinary-methods.md)',
    '- [Evaluation and citation audit](evaluation-evidence.md)',
    '- [Transfer and augmentation](deep-small-data-transfer.md)',
    '- [Competition code and Reddit leads](deep-practical-evidence.md)',
    '- [Translation-model interfaces and source audit](deep-translation-model-audit.md)', '',
    '## Source records', '',
    '| ID | Record and primary source | Category | Source registry |',
    '|---|---|---|---|',
]
for row in records:
    title = str(row['title']).replace('|', '/')
    category = str(row['category']).replace('|', '/')
    lines.append(f"| {row['id']} | [{title}]({row['source_url']}) | {category} | [{row['source_record_file']}]({row['source_record_file']}) |")
lines += ['', '## Reproducibility and limits', '',
    'The accompanying build_registry.py regenerates this index and JSON from the lane registries using only the Python standard library. Validation checks required fields, unique IDs, URL structure and dates; it does not prove scholarly correctness, live URL availability or model performance.', '',
    'Papers, model cards and repositories can change. Individual notes distinguish live source inspection, pinned source where available, publication results, indexed snapshots and untested artifacts. There is no claim that every repository was executable or that all corpora were downloadable.', '',
    'Priority unresolved questions: Pahlavi expert adjudication; genuinely new aligned pairs after cross-corpus deduplication; public release/reuse scope of MPCD and other editions; modern-language target completeness; model-specific Pahlavi performance; and actual hardware throughput.', '',
    'Earlier translation-ai-handoff.md and deep-research-synthesis.md are retained as research history. The final checkpoint controls the strategic recommendation and resource-first filtering is superseded.', '']
(ROOT / 'EVIDENCE_INDEX.md').write_text('\n'.join(lines), encoding='utf-8')
print(json.dumps({'records': len(records), 'source_registries': len(LANES), 'primary_url_count': len({r['source_url'] for r in records}), 'validation': 'passed'}, indent=2))
