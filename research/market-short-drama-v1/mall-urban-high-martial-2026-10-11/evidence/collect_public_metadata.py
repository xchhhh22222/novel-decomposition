"""Collect public original-page metadata using the existing downloader parser.

No reader prose, cookies, login, undocumented mall API or redistribution.
"""
import asyncio, hashlib, importlib.util, json, sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = Path(r'C:/Users/wanxincheng/.codex/skills/fanqie-novel-downloader/fanqie_dl.py')
spec = importlib.util.spec_from_file_location('fanqie_dl', SKILL)
dl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dl)

async def main():
    pool = [json.loads(x) for x in (ROOT/'mall-candidate-pool.jsonl').read_text(encoding='utf-8').splitlines()]
    output=[]
    async with dl.aiohttp.ClientSession() as session:
        for r in pool:
            url='https://fanqienovel.com/page/'+r['mall_book_id']
            try:
                html=await dl.fetch(session,url)
                p=dl.parse_initial_state(html)['page']
                categories=json.loads(p.get('categoryV2') or '[]')
                title=dl.require_decoded(p.get('bookName',''),'书名')
                author=dl.require_decoded(p.get('author',''),'作者')
                raw=p.get('readCount')
                row={'pool_id':r['pool_id'],'mall_title':r['mall_title'],'title':title,'author':author,'book_id':str(p.get('bookId','')),'original_url':url,'category_names':[x['Name'] for x in categories],'main_category':[x['Name'] for x in categories if x.get('MainCategory')],'urban_high_martial':any(x.get('ObjectId')==1014 for x in categories),'author_matches_mall':author==r['mall_author'],'same_book_id':str(p.get('bookId',''))==r['mall_book_id'],'original_page_read_count_raw':raw,'read_count_interpretation':'CENSORED_OR_ZERO_DO_NOT_TREAT_AS_EXACT_ZERO' if raw==0 else 'PRIMARY_PUBLIC_ORIGINAL_PAGE_STATE','title_match':title==r['mall_title'],'retrieved_at':datetime.now(timezone.utc).isoformat(),'page_sha256':hashlib.sha256(html.encode()).hexdigest(),'chapter_total':p.get('chapterTotal'),'status':'IDENTITY_VERIFIED' if author==r['mall_author'] and str(p.get('bookId',''))==r['mall_book_id'] else 'UNVERIFIED'}
                print(json.dumps({k:row[k] for k in ['pool_id','title','author','main_category','original_page_read_count_raw','status']},ensure_ascii=False),flush=True)
            except (Exception,SystemExit) as e:
                row={'pool_id':r['pool_id'],'original_url':url,'status':'UNVERIFIED','error':str(e),'retrieved_at':datetime.now(timezone.utc).isoformat()}
            output.append(row)
            (ROOT/'verified-originals-readers.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in output),encoding='utf-8')
            await asyncio.sleep(1)

if __name__=='__main__': asyncio.run(main())
