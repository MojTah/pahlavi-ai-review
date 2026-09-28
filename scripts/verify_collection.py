"""Verify retained bytes and build a text-data catalogue. No network requests."""
from collections import Counter, defaultdict
from datetime import datetime, timezone
import json
from pathlib import Path
import re
from urllib.parse import unquote
from collect_public_texts import ROOT, BASE, sha, write_json


def read(path):
    return json.loads(path.read_text('utf-8'))


if __name__=='__main__':
    catalogue=[];checks=[];failures=[];pdf_hashes=defaultdict(list)
    parsig=ROOT/'sources/local/parsig-2026-09-20'
    manifest=read(parsig/'manifest.json')
    for endpoint,item in manifest.items():
        raw=(parsig/item['file']).read_bytes()
        assert len(raw)==item['bytes'] and sha(raw)==item['sha256'],endpoint
    coverage=read(parsig/'exports/coverage.json')
    export=parsig/coverage['export_file']
    assert sha(export.read_bytes())==coverage['export_sha256']
    units=[json.loads(line) for line in export.read_text('utf-8').splitlines()]
    assert len(units)==len({p['id'] for p in units})==4507
    assert all(p['transcription'] for p in units)
    # Real-source regressions: French translations and Persian notes must not be English.
    assert {x['language'] for p in units if p['book_id']=='117' for x in p['additional_layers']}=={'fr'}
    assert all(x['language']=='fa' and x['role']=='commentary' for p in units if p['id']=='parsig:301006010' for x in p['additional_layers'])
    metadata=[];chapter_count=0
    for file in sorted((parsig/'corpus').glob('*.json')):
        book=read(file);bid=book['book_id']
        chapter_count+=len(book['chapters'])
        record={'book_id':bid,'title':book['title'],'responses':{}}
        for language in ['fa','en']:
            for prefix in ['book/bookdetaildata','book/bookdetailhtml']:
                endpoint=f'{prefix}/{bid}/{language}';assert endpoint in manifest
                item=manifest[endpoint];record['responses'][endpoint]={'source':item,'value':read(parsig/item['file'])}
        metadata.append(record)
        catalogue.append({'collection':'parsig','id':bid,'title':book['title'],'role':'source_text_with_offered_translations','file':file.relative_to(ROOT).as_posix(),'sha256':sha(file.read_bytes()),'units':sum(len(c['paragraphs']) for c in book['chapters']),'source_url':'https://parsigdatabase.com/surfing?lang=fa','rights':'Attribution-required research use; individual edition rights retained'})
    assert len(metadata)==len({m['book_id'] for m in metadata})==126
    assert chapter_count==334
    write_json(parsig/'exports/book-metadata.json',metadata)
    checks.append({'collection':'parsig','verified_responses':len(manifest),'nonimage_responses':sum(not e.startswith('book/bookversiongetpic/') for e in manifest),'books':126,'numbered_units':4507,'chapters':334,'translation_units':coverage['additional_field_classified_units'],'farsi_translation_units':coverage['units_with_nonempty_content']['farsi_translation']})
    for folder in sorted(BASE.iterdir()):
        if not folder.is_dir() or not (folder/'manifest.json').exists():continue
        manifest=read(folder/'manifest.json');total=0
        for url,item in manifest.items():
            if item['status']!='ok':
                failure={'collection':folder.name,**item}
                if url=='https://mp.melc.berkeley.edu/exist/apps/OpenAMPD/api/document/MP0003' and read(folder/'coverage.json')['missing']==0:
                    failure['resolution']='Superseded probe; all 152 listed documents obtained through advertised DTS URLs'
                failures.append(failure);continue
            raw=(folder/item['file']).read_bytes();assert len(raw)==item['bytes'] and sha(raw)==item['sha256'],url
            total+=1
            if url.lower().endswith('.pdf'):
                assert raw.startswith(b'%PDF'),url
                pdf_hashes[item['sha256']].append(url)
        documents_file=folder/'documents.json'
        if folder.name in ['titus','avesta','persoaryan']:
            if folder.name=='titus':
                assert not (folder/'collector.lock').exists(),'TITUS collection is still running'
                assert read(folder/'run-status.json')['status']=='complete','TITUS run has not completed'
            assert (folder/'coverage.json').exists(),folder
            documents=read(documents_file)
            pdf_path=folder/'pdf-text-coverage.json'
            pdf_info={p['url']:p for p in read(pdf_path)} if pdf_path.exists() else {}
            for doc in documents:
                assert doc['sha256']==manifest[doc['url']]['sha256'],doc['url']
                if doc.get('text_file'):
                    assert sha((folder/doc['text_file']).read_bytes())==doc['text_sha256']
                entry={'collection':folder.name,'source_url':doc['url'],'title':doc.get('title') or unquote(doc['url'].rsplit('/',1)[-1]),'source_file':(folder/doc['file']).relative_to(ROOT).as_posix(),'sha256':doc['sha256'],'rights':doc['rights'],'role':doc['role']}
                if doc.get('text_file'):
                    entry['text_file']=(folder/doc['text_file']).relative_to(ROOT).as_posix()
                    entry['encoding_needs_review']=doc.get('encoding_needs_review',False)
                if doc['url'] in pdf_info:
                    pdf=pdf_info[doc['url']]
                    entry.update(pdf_pages=pdf.get('pages'),pdf_text_file=(folder/pdf['text_file']).relative_to(ROOT).as_posix(),pdf_pages_with_text=pdf.get('pages_with_at_least_40_letters'))
                    title=pdf.get('metadata',{}).get('/Title','').strip()
                    if title:entry['pdf_metadata_title']=title
                if folder.name=='titus':
                    entry['language_scope']='Middle Persian; mixed Middle Iranian Manichaean collections require passage-level separation' if '/manich/' in doc['url'] else 'Middle Persian; Avestan quotations occur in Zand texts'
                catalogue.append(entry)
            detail=read(folder/'coverage.json')
            assert len(documents)==detail['documents'],folder
            if folder.name in ['titus','avesta']:
                assert len(documents)==total,'Collection still running or catalogue incomplete: '+folder.name
            if folder.name=='titus':
                config=read(ROOT/'sources/titus-collection.json')
                detail['selected_collections']=len(config['roots'])
                expected=set(config.get('supplemental_seeds',[]))
                detail['indexed_pages_expected']=len(expected)
                detail['indexed_pages_missing']=sorted(expected-{d['url'] for d in documents})
                detail['numbered_content_pages']=sum(bool(re.search(r'/[^/]*\d{3}\.htm$',d['url'])) for d in documents)
            pdf_coverage=folder/'pdf-text-coverage.json'
            if folder.name in ['avesta','persoaryan']:
                assert pdf_coverage.exists(),folder
                pdfs=read(pdf_coverage)
                flagged_pages=0;replacement_characters=0
                for p in pdfs:
                    assert p['status']=='extracted',p
                    assert sha((folder/p['text_file']).read_bytes())==p['text_sha256']
                    pages=[json.loads(line) for line in (folder/p['text_file']).read_text('utf-8').splitlines()]
                    assert len(pages)==p['pages']
                    assert [page['pdf_page'] for page in pages]==list(range(1,p['pages']+1))
                    assert p['source_sha256']==manifest[p['url']]['sha256']
                    assert all(page['source_sha256']==p['source_sha256'] and page['source_url']==p['url'] for page in pages)
                    assert sum(sum(c.isalpha() for c in page['text'])>=40 for page in pages)==p['pages_with_at_least_40_letters']
                    flagged_pages+=sum('extraction_note' in page for page in pages)
                    replacement_characters+=sum(page['text'].count('\ufffd') for page in pages)
                detail['pdfs']=len(pdfs);detail['pdf_pages']=sum(p['pages'] for p in pdfs)
                detail['pdf_pages_with_text']=sum(p['pages_with_at_least_40_letters'] for p in pdfs)
                detail['pdf_pages_with_little_or_no_text']=sum(p['pages_with_little_or_no_text'] for p in pdfs)
                detail['pdf_pages_with_extraction_notes']=flagged_pages
                detail['pdf_text_replacement_characters']=replacement_characters
        elif folder.name=='berkeley':
            docs=read(documents_file);assert len(docs)==len({d['id'] for d in docs})==152
            detail=read(folder/'coverage.json')
            for d in docs:
                catalogue.append({'collection':'berkeley','id':d['id'],'title':d['title'],'source_url':d['source']['url'],'source_file':(folder/d['source']['file']).relative_to(ROOT).as_posix(),'sha256':d['source']['sha256'],'layers':[(x['type'],x['language']) for x in d['layers']],'credits':d['credits'],'rights':d['rights']})
        elif folder.name=='invisible-east':
            docs=read(folder/'middle-persian.json');assert len(docs)==len({d['uri'] for d in docs})==158
            assert all(d['primaryLanguage']=='Middle Persian (Pahlavi script)' for d in docs)
            detail=read(folder/'coverage.json')
            for d in docs:
                layers=[k for k in ['transliteration','transcription','translation'] if any(f.get(k) for f in d['folios'])]
                catalogue.append({'collection':'invisible-east','id':d['uri'],'source_url':d['permalink'],'title':d['shelfmark'],'layers':layers,'role':'source_text_with_translation' if layers else 'metadata_only','file':(folder/'middle-persian.json').relative_to(ROOT).as_posix(),'credit':d['principalEditor'],'rights':'Use with source and editor attribution according to IEDC how-to-cite notice; individual edition notices retained'})
        else:
            detail={'retained_files':total,'scope':'Reference repository metadata or grammar feature data; not a parallel corpus'}
        checks.append({'collection':folder.name,'verified_files':total,'coverage':detail})
    duplicate_pdfs=[{'sha256':k,'urls':v} for k,v in pdf_hashes.items() if len(v)>1]
    result={'checked_utc':datetime.now(timezone.utc).isoformat(),'verification':'PASS: byte counts, SHA-256, IDs, core layer coverage and real-source language regression checks','collections':checks,'failed_urls':failures,'exact_duplicate_pdfs':duplicate_pdfs,'catalogue_records':len(catalogue),'limitations':['Source collections overlap; totals are not unique works or aligned sentence pairs.','TITUS pagination and index HTML files are not all text passages.','PDF text extraction is not OCR; low-text pages require separate review.','MPCD browser access works but complete bulk export was not obtained.','UniversalDependencies/UD_Middle_Persian-MPCD master tree had no CoNLL-U files at the inspected commit.','Research collection does not establish reuse rights for a public product or model training.']}
    out=ROOT/'data';out.mkdir(exist_ok=True)
    result['failed_urls_without_recorded_resolution']=sum('resolution' not in f for f in failures)
    with (out/'document-index.jsonl').open('w',encoding='utf-8') as handle:
        for row in catalogue:handle.write(json.dumps(row,ensure_ascii=False)+'\n')
    write_json(out/'collection-status.json',result)
    print(json.dumps({'verification':'PASS','catalogue_records':len(catalogue),'failed_urls':len(failures),'exact_duplicate_pdf_groups':len(duplicate_pdfs),'collections':[{k:v for k,v in c.items() if k!='coverage'} for c in checks]}))
