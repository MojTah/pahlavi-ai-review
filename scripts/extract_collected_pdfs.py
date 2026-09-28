"""Extract page-labelled text from collected PDF editions, without OCR."""
import argparse
import json
from pathlib import Path
from pypdf import PdfReader
from collect_public_texts import BASE, sha, write_json

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('collection',choices=['avesta','persoaryan'],nargs='?',default='avesta')
    root=BASE/parser.parse_args().collection
    manifest=json.loads((root/'manifest.json').read_text('utf-8'))
    folder=root/'pdf-text';folder.mkdir(exist_ok=True)
    prior_path=root/'pdf-text-coverage.json'
    prior={p['url']:p for p in json.loads(prior_path.read_text('utf-8'))} if prior_path.exists() else {}
    report=[]
    for url,item in manifest.items():
        if item['status']!='ok' or not item['file'].endswith('.pdf'):continue
        path=root/item['file'];assert sha(path.read_bytes())==item['sha256']
        target=folder/(path.stem+'.jsonl')
        previous=prior.get(url)
        if previous and previous['status']=='extracted' and previous['source_sha256']==item['sha256'] and target.exists() and sha(target.read_bytes())==previous['text_sha256']:
            report.append(previous);continue
        try:
            reader=PdfReader(path)
            counts=[]
            with target.open('w',encoding='utf-8') as handle:
                for number,page in enumerate(reader.pages,1):
                    text=page.extract_text() or ''
                    row={'source_url':url,'source_sha256':item['sha256'],'pdf_page':number,'text':text,'method':'pypdf embedded-text extraction; no OCR or linguistic correction'}
                    if any(0xD800<=ord(c)<=0xDFFF for c in text):
                        row['raw_extracted_text_escaped']=text.encode('unicode_escape').decode('ascii')
                        text=text.encode('utf-16-le','surrogatepass').decode('utf-16-le','replace')
                        row.update(text=text,extraction_note='Surrogate code units from the PDF font mapping decoded as UTF-16; unpaired units become replacement characters. Raw escaped extraction retained for review.')
                    counts.append(sum(c.isalpha() for c in text))
                    handle.write(json.dumps(row,ensure_ascii=False)+'\n')
            entry={'url':url,'source_sha256':item['sha256'],'pages':len(counts),'pages_with_at_least_40_letters':sum(n>=40 for n in counts),'pages_with_little_or_no_text':sum(n<40 for n in counts),'text_file':target.relative_to(root).as_posix(),'text_sha256':sha(target.read_bytes()),'status':'extracted','metadata':{str(k):str(v) for k,v in (reader.metadata or {}).items()}}
        except Exception as exc:
            entry={'url':url,'status':'failed','error':str(exc)}
        report.append(entry);print(json.dumps({k:v for k,v in entry.items() if k not in ['metadata','url']}),flush=True)
    write_json(root/'pdf-text-coverage.json',report)
