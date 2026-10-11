"""Use fanqie-novel-downloader core; ten chapters only, sources outside Git.

Default TLS verification is retained. Locked/paid entries are never fetched.
"""
import asyncio, hashlib, importlib.util, json, sys
from pathlib import Path
from datetime import datetime, timezone
ROOT=Path(__file__).resolve().parents[1]
SOURCE=Path(sys.argv[1]).resolve()
spec=importlib.util.spec_from_file_location('fanqie_dl',r'C:/Users/wanxincheng/.codex/skills/fanqie-novel-downloader/fanqie_dl.py')
dl=importlib.util.module_from_spec(spec);spec.loader.exec_module(dl)
async def main():
    rows=[json.loads(x) for x in (ROOT/'verified-originals-readers.jsonl').read_text(encoding='utf-8').splitlines()]
    selected=json.loads((ROOT/'evidence/selected-book-ids.json').read_text(encoding='utf-8'))
    assert len(selected)==10 and all(r.get('readership_status')=='VERIFIED_MAIN_SITE_DISPLAY' for r in selected)
    receipts=[]
    SOURCE.mkdir(parents=True,exist_ok=True)
    async with dl.aiohttp.ClientSession(connector=dl.aiohttp.TCPConnector(limit=2)) as session:
        for r in selected:
            bid=r['book_id'];out=SOURCE/bid;out.mkdir(exist_ok=True)
            info=await dl.get_book_info(session,bid)
            assert info['title']==r['title'] and info['author']==r['author']
            (out/'metadata.json').write_text(json.dumps(info,ensure_ascii=False,indent=2),encoding='utf-8')
            chapters=[];parts=[]
            for c in info['chapters'][:10]:
                receipt={k:c[k] for k in ['item_id','title','order','locked']}
                receipt['source_url']='https://fanqienovel.com/reader/'+c['item_id']
                if c['locked']:
                    receipt['status']='LOCKED_NOT_FETCHED'
                else:
                    try:
                        part=await dl.fetch_chapter(session,c,'')
                        txt=part['content_text']
                        receipt.update(status='COMPLETE' if len(txt)>=500 and not part['empty'] else 'PARTIAL_OR_EMPTY',characters=len(txt),sha256=hashlib.sha256(txt.encode()).hexdigest(),unresolved_pua=dl.count_pua(txt))
                        (out/f"chapter-{c['order']:02d}.txt").write_text(txt,encoding='utf-8')
                        parts.append(part)
                    except (Exception,SystemExit) as e:receipt.update(status='FAILED',error=str(e))
                chapters.append(receipt)
                print(f"{bid} {c['order']:02d} {c['title']} {receipt['status']}",flush=True)
                await asyncio.sleep(1)
            path=dl.export_txt(info,parts,out)
            receipt={'book_id':bid,'title':r['title'],'author':r['author'],'downloaded_at':datetime.now(timezone.utc).isoformat(),'requested_range':[1,10],'chapters':chapters,'complete_chapters':sum(c['status']=='COMPLETE' for c in chapters),'local_only_sample_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'local_source_path':str(out),'raw_prose_committed':False,'decoder_version':dl.PUA_FONT_VERSION,'tls_verification':True}
            receipts.append(receipt)
            (ROOT/'evidence/download-receipts.json').write_text(json.dumps(receipts,ensure_ascii=False,indent=2),encoding='utf-8')
if __name__=='__main__':asyncio.run(main())
