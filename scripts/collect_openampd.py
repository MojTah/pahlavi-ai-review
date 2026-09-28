"""Collect all documents enumerated by Berkeley's public DTS endpoint."""
import json
import xml.etree.ElementTree as ET
from collect_public_texts import Archive, write_json, sha

HOST='https://mp.melc.berkeley.edu'
BASE=HOST+'/exist/apps/OpenAMPD/'
NS={'tei':'http://www.tei-c.org/ns/1.0'}
XML='{http://www.w3.org/XML/1998/namespace}'

if __name__=='__main__':
    ar=Archive('berkeley',limit=200)
    listing=json.loads(ar.get(BASE+'api/dts/collection?id=documents&per-page=200')[0])
    members=listing['member']
    assert len(members)==listing['totalItems']==len({m['@id'] for m in members})
    documents=[]
    for m in members:
        url=HOST+m['dts:passage']
        assert url.startswith(BASE+'api/dts/document?')
        raw,item=ar.get(url)
        if raw is None: continue
        root=ET.fromstring(raw)
        assert root.tag=='{'+NS['tei']+'}TEI'
        layers=[]
        for div in root.findall('tei:text/tei:body/tei:div',NS):
            layers.append({'type':div.get('type'),'language':div.get(XML+'lang'),'text':' '.join(''.join(div.itertext()).split()),'xml':ET.tostring(div,encoding='unicode')})
        credits=[{'name':''.join(r.find('tei:persName',NS).itertext()),'role':''.join(r.find('tei:resp',NS).itertext())} for r in root.findall('.//tei:respStmt',NS) if r.find('tei:persName',NS) is not None and r.find('tei:resp',NS) is not None]
        documents.append({'id':root.get(XML+'id'),'title':m['title'],'source':item,'rights':'OpenAMPD website CC BY-NC-SA 4.0; preserve edition-level attribution and restrictions','credits':credits,'layers':layers,'alignment':'source document; original line and paragraph IDs retained in XML; no inferred sentence alignment'})
        if len(documents)%25==0:print(json.dumps({'saved_documents':len(documents),'total':len(members)}),flush=True)
    write_json(ar.path/'documents.json',documents)
    summary={'listed':len(members),'saved':len(documents),'missing':len(members)-len(documents),'layers':{}}
    for d in documents:
        for x in d['layers']:
            key=str(x['type'])+':'+str(x['language']);summary['layers'][key]=summary['layers'].get(key,0)+1
    write_json(ar.path/'coverage.json',summary);print(json.dumps(summary),flush=True)
