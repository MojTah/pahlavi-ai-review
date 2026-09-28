"""Export source units without inventing translation alignment or language labels."""
from collections import Counter
import json
from pathlib import Path
import re
from collect_public_texts import sha, write_json

ROOT=Path(__file__).resolve().parents[1]
ARCHIVE=ROOT/'sources/local/parsig-2026-09-20'
EN_BOOKS={'101','104','109','110','115','116','119','122','123','130','132','134','137','138','150','302'}
FR_BOOKS={'117','136','152'}


def sections(value):
    if isinstance(value,str): return [value] if value.strip() else []
    if not value: return []
    assert isinstance(value,list)
    return [v['Section'] for v in value if v.get('Section','').strip()]


def classify(book,text):
    # Site introductions explicitly identify the three French editions.
    # Persian commentary is also stored in the misleading EnTranslation field.
    if re.match(r'^\s*یادداشت(?:\s|[:：])',text):
        return 'fa','commentary','explicit Persian note marker'
    letters=[c for c in text if c.isalpha()]
    arabic=sum('\u0600'<=c<='\u06ff' for c in letters)
    if letters and arabic/len(letters)>.45:
        return 'fa','unclassified_note_or_translation','Persian-script majority; review role'
    if book in FR_BOOKS:
        return 'fr','translation','book introduction and inspected French translation samples'
    if book in EN_BOOKS:
        return 'en','translation','inspected English translation samples and edition credits'
    return 'und','unclassified','not inferred from misleading source field name'


if __name__=='__main__':
    inventory=json.loads((ROOT/'sources/parsig-live-inventory.json').read_text('utf-8'))
    records={r['id']:r for g in inventory['groups'] for r in g['records']}
    manifest=json.loads((ARCHIVE/'manifest.json').read_text('utf-8'))
    out=ARCHIVE/'exports';out.mkdir(exist_ok=True)
    counts=Counter();languages=Counter();all_ids=set();books=[]
    with (out/'text-units.jsonl').open('w',encoding='utf-8') as handle:
        for file in sorted((ARCHIVE/'corpus').glob('*.json')):
            book=json.loads(file.read_text('utf-8'));bid=book['book_id'];units=0
            assert sha(file.read_bytes())==records[bid]['collection']['sha256']
            for chapter in book['chapters']:
                endpoint=f"surf/paragraph/{bid}/{chapter['id']}/All"
                source=manifest[endpoint]
                raw=(ARCHIVE/source['file']).read_bytes()
                assert sha(raw)==source['sha256']
                assert json.loads(raw)==chapter['paragraphs']
                for p in chapter['paragraphs']:
                    pid=str(p['Code']);assert pid not in all_ids;all_ids.add(pid)
                    additional=[]
                    for text in sections(p.get('EnTranslation')):
                        lang,role,evidence=classify(bid,text)
                        additional.append({'language':lang,'role':role,'text':text,'classification_evidence':evidence,'source_field':'EnTranslation'})
                    result={'id':'parsig:'+pid,'book_id':bid,'book_title':book['title'],'chapter_id':chapter['id'],'sequence':p['Sequence'],'language_scope':records[bid].get('language_label', 'Middle Persian; quoted Avestan may occur in Zand texts'),'source':source,'original_script_source':sections(p.get('Text')),'transcription':sections(p.get('Transcription')),'farsi_translation':sections(p.get('Translation')),'additional_layers':additional,'notes':sections(p.get('Note')),'raw_source_unit':p,'alignment':'source paragraph association only; headings and colophons retained; not vetted sentence pairs','rights':'Parsig attribution-required research use; underlying edition rights retained'}
                    handle.write(json.dumps(result,ensure_ascii=False)+'\n');units+=1
                    for field in ['original_script_source','transcription','farsi_translation','notes']:
                        counts[field]+=bool(result[field])
                    for key in {(x['language'],x['role']) for x in additional}:languages[':'.join(key)]+=1
            books.append({'id':bid,'units':units,'chapters':len(book['chapters'])})
    assert len(books)==126 and len(all_ids)==4507
    report={'books':len(books),'chapters':sum(b['chapters'] for b in books),'numbered_units':len(all_ids),'units_with_nonempty_content':dict(counts),'additional_field_classified_units':dict(languages),'export_file':'exports/text-units.jsonl','export_sha256':sha((out/'text-units.jsonl').read_bytes()),'per_book':books,'limitations':['EnTranslation is a mixed-language, mixed-role source field.','Legacy original-script strings require the source font; they are not ordinary modern Farsi.','Missing translations remain missing. No automatic translation or alignment was added.','Collected does not mean read, linguistically validated, or trained.']}
    write_json(out/'coverage.json',report)
    write_json(ROOT/'sources/parsig-text-coverage.json',report)
    print(json.dumps({k:v for k,v in report.items() if k!='per_book'},ensure_ascii=False))

