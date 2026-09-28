"""Bounded public text acquisition, with exact sources and a resumable hash manifest.

HTML/XML/PDF/text only. No images, assets, login, or executable downloads.
Each job follows only observed links within explicitly selected text collections.
"""
import argparse
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import time
import threading
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'sources/local/public-texts-2026-09-20'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def interrupted_connection(item):
    return any(marker in item.get('error','') for marker in
               ('WinError 10054','UNEXPECTED_EOF_WHILE_READING','RemoteDisconnected:'))


def canonical(url):
    p=urllib.parse.urlsplit(urllib.parse.urldefrag(url)[0])
    return urllib.parse.urlunsplit((p.scheme,p.netloc,urllib.parse.quote(p.path,safe='/%:@'),urllib.parse.quote(p.query,safe='=&%:/,?'),''))


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    temp.replace(path)


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links, self.parts, self.title = [], [], []
        self.skip = 0
        self.in_title = False

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag in ('script', 'style'): self.skip += 1
        if tag == 'title': self.in_title = True
        if tag in ('a', 'frame', 'iframe'):
            href = d.get('href', d.get('src'))
            if href: self.links.append(href)
        if tag in ('p', 'div', 'br', 'tr', 'h1', 'h2', 'h3', 'li'): self.parts.append('\n')

    def handle_endtag(self, tag):
        if tag in ('script', 'style'): self.skip = max(0, self.skip-1)
        if tag == 'title': self.in_title = False
        if tag in ('p', 'div', 'tr', 'h1', 'h2', 'h3', 'li'): self.parts.append('\n')

    def handle_data(self, value):
        if self.in_title: self.title.append(value)
        if not self.skip: self.parts.append(value)

    @property
    def text(self):
        return re.sub(r'\n\s*\n+', '\n\n', ''.join(self.parts)).strip()


def decode(raw, charset=None):
    declared = re.search(br'charset\s*=\s*["\x27]?([\w-]+)', raw[:4000], re.I)
    encoding = declared[1].decode('ascii') if declared else charset or 'utf-8'
    try: return raw.decode(encoding), encoding, False
    except (UnicodeDecodeError, LookupError):
        return raw.decode('cp1252', errors='replace'), 'cp1252-fallback', True


class Archive:
    def __init__(self, name, limit=2000, retry_transport=False):
        self.path = BASE / name
        self.path.mkdir(parents=True, exist_ok=True)
        self.manifest_path = self.path / 'manifest.json'
        self.manifest = json.loads(self.manifest_path.read_text('utf-8')) if self.manifest_path.exists() else {}
        self.limit, self.requests, self.reused = limit, 0, 0
        self.started, self.last = time.monotonic(), 0
        self.state_lock=threading.Lock()
        self.retry_transport=retry_transport

    def get(self, url, retry=False, max_bytes=40_000_000):
        url = canonical(url)
        item = self.manifest.get(url)
        if item and item.get('status') == 'ok':
            raw = (self.path / item['file']).read_bytes()
            if sha(raw) != item['sha256']: raise RuntimeError('Cache checksum failure: '+url)
            with self.state_lock: self.reused += 1
            return raw, item
        if item and not retry:
            if self.retry_transport and 'previous_attempt' not in item and interrupted_connection(item):
                time.sleep(2)
                return self.get(url,retry=True,max_bytes=max_bytes)
            return None, item
        with self.state_lock:
            if self.requests >= self.limit or time.monotonic()-self.started > 3600:
                raise RuntimeError('Run boundary; verified cache is resumable')
            time.sleep(max(0,.55-(time.monotonic()-self.last)))
            self.last=time.monotonic()
            self.requests+=1
        previous = item
        item = {'url':url, 'retrieved_utc':datetime.now(timezone.utc).isoformat()}
        if previous: item['previous_attempt'] = previous
        try:
            req = urllib.request.Request(url, headers={'User-Agent':'MiddlePersianResearchCollection/1.0 (text-only; rate-limited)'})
            with urllib.request.urlopen(req, timeout=35) as response:
                raw = response.read(max_bytes+1)
                item.update(final_url=response.url, content_type=response.headers.get('Content-Type',''), charset=response.headers.get_content_charset())
            if len(raw) > max_bytes: raise ValueError('Response too large')
            if not any(x in item['content_type'].lower() for x in ('text','json','xml','pdf','octet-stream')):
                raise ValueError('Not a text document')
            ext = '.pdf' if raw.startswith(b'%PDF') else '.source'
            target = self.path / 'raw' / (sha(url.encode())+ext)
            target.parent.mkdir(exist_ok=True)
            target.write_bytes(raw)
            item.update(status='ok', file=target.relative_to(self.path).as_posix(), sha256=sha(raw), bytes=len(raw))
        except Exception as exc:
            raw = None
            item.update(status='failed', error=type(exc).__name__+': '+str(exc))
        with self.state_lock:
            self.manifest[url] = item
            write_json(self.manifest_path, self.manifest)
        if raw is None and self.retry_transport and not retry and previous is None and interrupted_connection(item):
            time.sleep(2)
            return self.get(url,retry=True,max_bytes=max_bytes)
        return raw, item


def collect(config, limit, workers=1, retry_transport=False):
    archive = Archive(config['id'], limit, retry_transport)
    queue, seen, entries = deque(config['seeds']+config.get('supplemental_seeds',[])), set(), []
    allowed_roots = config['roots']
    with ThreadPoolExecutor(max_workers=workers) as pool:
        while queue:
            batch=[]
            while queue and len(batch)<workers:
                url=canonical(queue.popleft())
                if url not in seen:
                    seen.add(url);batch.append(url)
            for url,(raw,item) in zip(batch,pool.map(archive.get,batch)):
                if raw is None: continue
                entry = dict(item, collection=config['id'], rights=config['rights'], role='source_document_not_aligned_pair')
                if not raw.startswith(b'%PDF'):
                    text, encoding, fallback = decode(raw, item.get('charset'))
                    page = Page(); page.feed(text)
                    txt = archive.path / 'text' / (sha(url.encode())+'.txt')
                    txt.parent.mkdir(exist_ok=True); txt.write_text(page.text, encoding='utf-8')
                    entry.update(title=''.join(page.title).strip(), text_file=txt.relative_to(archive.path).as_posix(), text_sha256=sha(txt.read_bytes()), encoding=encoding, encoding_needs_review=fallback)
                    for link in page.links:
                        target = canonical(urllib.parse.urljoin(item['final_url'],link))
                        target = target.replace('http://www.avesta.org/', 'https://www.avesta.org/').replace('http://titus.uni-frankfurt.de/','https://titus.uni-frankfurt.de/')
                        path = urllib.parse.urlsplit(target).path.lower()
                        if any(target.startswith(root) for root in allowed_roots) and re.search(r'\.(?:html?|txt|xml|pdf)$',path):
                            queue.append(target)
                entries.append(entry)
                if len(entries)%25 == 0: print(json.dumps({'collection':config['id'],'saved':len(entries),'queue':len(queue),'new_requests':archive.requests}),flush=True)
    write_json(archive.path/'documents.json',entries)
    result={'collection':config['id'],'documents':len(entries),'failures':sum(v['status']!='ok' for v in archive.manifest.values()),'requests':archive.requests,'reused':archive.reused,'bytes':sum(e['bytes'] for e in entries)}
    write_json(archive.path/'coverage.json',result)
    print(json.dumps(result),flush=True)


if __name__ == '__main__':
    parser=argparse.ArgumentParser();parser.add_argument('config');parser.add_argument('--limit',type=int,default=2000)
    parser.add_argument('--workers',type=int,choices=[1,2],default=1)
    parser.add_argument('--retry-transport-once',action='store_true')
    args=parser.parse_args();config=json.loads(Path(args.config).read_text('utf-8'))
    folder=BASE/config['id'];folder.mkdir(parents=True,exist_ok=True);lock=folder/'collector.lock'
    run={'pid':os.getpid(),'started_utc':datetime.now(timezone.utc).isoformat(),'status':'running',
         'config':str(Path(args.config).resolve()),'script_sha256':sha(Path(__file__).read_bytes()),
         'request_limit':args.limit,'workers':args.workers,'hard_limit_seconds':3600,
         'config_sha256':sha(Path(args.config).read_bytes()),'retry_transport_once':args.retry_transport_once}
    with lock.open('x',encoding='utf-8') as handle:json.dump(run,handle)
    write_json(folder/'run-status.json',run)
    try:
        collect(config,args.limit,args.workers,args.retry_transport_once)
        run['status']='complete'
    except BaseException as exc:
        run.update(status='stopped' if isinstance(exc,KeyboardInterrupt) else 'failed',error=type(exc).__name__+': '+str(exc))
        raise
    finally:
        run['finished_utc']=datetime.now(timezone.utc).isoformat()
        write_json(folder/'run-status.json',run)
        with (folder/'runs.jsonl').open('a',encoding='utf-8') as handle:handle.write(json.dumps(run)+'\n')
        lock.unlink()
