"""Assemble and validate this research delivery; no network or library mutation."""
import argparse, hashlib, json, re, subprocess
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--library', required=True)
parser.add_argument('--library-git', required=True)
parser.add_argument('--originals', required=True)
args = parser.parse_args()
ev = Path(__file__).resolve().parent
root = ev.parent
library = Path(args.library).resolve()
originals = Path(args.originals).resolve()
freeze = '1e10e6e3ffb70eda94a400073155fd89db724ce9'
package = 'packages/shared-dna-library/v1.0.0/'
manifest_bytes = (library/'manifest.json').read_bytes()
git_manifest = subprocess.run(['git','-C',args.library_git,'show',freeze+':'+package+'manifest.json'],capture_output=True,check=True).stdout
assert git_manifest == manifest_bytes, 'Export manifest does not equal frozen Git manifest'
integrity = json.loads((ev/'frozen-material-integrity.json').read_text(encoding='utf-8'))
integrity['manifest_sha256'] = hashlib.sha256(manifest_bytes).hexdigest()
integrity['manifest_frozen_git_blob'] = subprocess.run(['git','-C',args.library_git,'rev-parse',freeze+':'+package+'manifest.json'],capture_output=True,text=True,check=True).stdout.strip()
integrity['manifest_equals_frozen_git'] = True
(ev/'frozen-material-integrity.json').write_text(json.dumps(integrity,ensure_ascii=False,indent=2),encoding='utf-8')

choices = [
 ('A,C','02_金手指','BOOK_015','', 'FULL_ROW'),
 ('A','03_世界观','BOOK_005','/rule_chains/1','PARENT_CONTEXT_AND_RULE_CHAINS'),
 ('A','04_修炼体系','BOOK_009','','FULL_ROW'),
 ('A','07_开篇','BOOK_004','/selling_point_proof/0','OPENING_RELEVANT_FIELDS'),
 ('B','02_金手指','BOOK_005','','FULL_ROW'),
 ('B','05_人物功能与标签','BOOK_005','/relationship_engines/0','FULL_SELECTED_UNIT_WITH_PARENT_QA_UNKNOWN'),
 ('B','09_剧情机制','BOOK_012','/mechanisms/6','FULL_SELECTED_UNIT_WITH_PARENT_QA_UNKNOWN'),
 ('C','05_人物功能与标签','BOOK_008','/relationship_engines/0','FULL_SELECTED_UNIT_WITH_PARENT_QA_UNKNOWN'),
 ('C','06_主线与支线','BOOK_002','/plotlines/1','FULL_SELECTED_UNIT_WITH_PARENT_QA_UNKNOWN'),
 ('C','08_篇章结构','BOOK_009','/arcs/2','FULL_SELECTED_UNIT_WITH_PARENT_QA_UNKNOWN'),
]
receipts=[]
for concepts,module,book,pointer,scope in choices:
    relative=f'DNA素材/{module}/per_book/{book}.jsonl'
    raw=(library/relative).read_bytes()
    data=json.loads(raw.decode('utf-8').splitlines()[0])
    selected=data
    for key in pointer.strip('/').split('/') if pointer else []:
        selected=selected[int(key)] if isinstance(selected,list) else selected[key]
    assert data['qa_status']=='PASS' and data['status']=='candidate'
    refs=selected.get('evidence_refs',[])
    if not refs and 'arc_identity' in selected: refs=selected['arc_identity']['evidence_refs']
    receipts.append({'concepts':concepts,'record_id':data['record_id'],'path':relative,'line':1,'json_pointer':pointer or '/', 'read_scope':scope,'file_sha256':hashlib.sha256(raw).hexdigest(),'selected_unit_sha256':hashlib.sha256(json.dumps(selected,ensure_ascii=False,sort_keys=True).encode()).hexdigest(),'qa_status':data['qa_status'],'status':data['status'],'evidence_refs':refs,'parent_unknowns':data.get('unknowns',[]),'source_url':f'https://github.com/xchhhh22222/nova-material-library/blob/{freeze}/{package}{relative}'})
(ev/'material-read-receipts.json').write_text(json.dumps({'frozen_commit':freeze,'module_count':8,'record_count':10,'records':receipts},ensure_ascii=False,indent=2),encoding='utf-8')

pool=[json.loads(x) for x in (root/'mall-candidate-pool.jsonl').read_text(encoding='utf-8').splitlines()]
verified=[json.loads(x) for x in (root/'verified-originals-readers.jsonl').read_text(encoding='utf-8').splitlines()]
downloads=json.loads((ev/'download-receipts.json').read_text(encoding='utf-8'))
assert len(pool)==len(verified)==40
assert len({x['book_id'] for x in verified})==40
assert all(x['same_book_id'] and x['author_matches_mall'] and x['urban_high_martial'] and x['status']=='IDENTITY_VERIFIED' and x['search_performed_in_browser'] for x in verified)
known=[x for x in verified if x['readership_status']=='VERIFIED_MAIN_SITE_DISPLAY']
unknown=[x for x in verified if x['readership_status'].startswith('UNKNOWN')]
assert (len(known),len(unknown))==(32,8)
assert len(downloads)==10
chapter_rows=[]
combined=['# 热门10本前10章逐章实读\n','CHAPTER_10_ANALYSIS=COMPLETE；共100章，全部为本轮实际公开正文。表格是原创结构分析，非原著全文。每行章号链接到实际reader页面，章节名、item_id、下载时间、完整度与本地正文SHA256见[下载回执](evidence/download-receipts.json)。不以书名、简介、目录或后文记忆补开篇事实。\n','统计与首次兑现比较见[横向研究](cross-book-opening-lessons.md)。数字排序为主站公开在读档位，原始样本和未知值见[核实表](candidate-pool-and-readers.md)。\n']
for n,(file,book) in enumerate(zip(sorted((root/'analyses').glob('*.md')),downloads),1):
    content=file.read_text(encoding='utf-8')
    assert book['book_id'] in content, (file,book['book_id'])
    assert len(book['chapters'])==10
    for chapter in book['chapters']:
        order=chapter['order']
        assert chapter['status']=='COMPLETE' and not chapter['locked'] and chapter['unresolved_pua']==0
        local=originals/book['book_id']/f'chapter-{order:02}.txt'
        raw=local.read_bytes()
        decoded=local.read_text(encoding='utf-8')
        assert hashlib.sha256(decoded.encode('utf-8')).hexdigest()==chapter['sha256'],local
        # Idempotent: first cell may already contain the source link.
        pattern=rf'^\| (?:{order}|\[{order}\]\([^\n]+?\)) \|'
        replacement=f"| [{order}]({chapter['source_url']}) |"
        content,count=re.subn(pattern,lambda m:replacement,content,flags=re.M)
        assert count==1,(file,order,count)
        row=next(x for x in content.splitlines() if x.startswith(replacement))
        assert len(row.split('|'))==8,(file,order,'table columns')
        chapter_rows.append({'book_id':book['book_id'],'book_title':book['title'],'chapter_order':order,'chapter_title':chapter['title'],'item_id':chapter['item_id'],'source_url':chapter['source_url'],'analysis_file':'analyses/'+file.name,'text_sha256':chapter['sha256'],'text_hash_definition':'decoded UTF-8, LF newlines','local_file_sha256':hashlib.sha256(raw).hexdigest(),'analysis_status':'READ_AND_ANALYZED','complete':True})
    file.write_text(content,encoding='utf-8')
    combined.append('\n---\n\n'+content.replace('# ','## ',1))
(root/'chapter-01-10-analysis.md').write_text('\n'.join(combined),encoding='utf-8')
(ev/'chapter-analysis-evidence.jsonl').write_text('\n'.join(json.dumps(x,ensure_ascii=False) for x in chapter_rows)+'\n',encoding='utf-8')
selected_by_id={x['book_id']:x for x in known}
selected=[selected_by_id[x['book_id']] for x in downloads]
assert all(x['readership_status']=='VERIFIED_MAIN_SITE_DISPLAY' for x in selected)
def public_heat(row):
    display=row['main_site_readers_display']
    return float(re.search(r'[0-9.]+',display)[0]) * (10000 if '万' in display else 1)
assert selected==sorted(known,key=public_heat,reverse=True)[:10], 'Selection must use public display heat'
(ev/'selected-book-ids.json').write_text(json.dumps(selected,ensure_ascii=False,indent=2),encoding='utf-8')

table=['# 商城40部候选与主站在读核实表\n','各书都执行主站“完整原著书名＋作者”搜索并核对原著页。未知不计0、不借商城热度；未满1000不细排。30部分散分页采样＋10部主站高在读定向补采的偏向见[方法](README.md)。分类40部均核对都市高武1014。\n','| ID | 商城完整书名／链接 | 主站完整原著／作者／book_id | 主站在读 | 结论 |\n| --- | --- | --- | --- | --- |']
for x in verified:
    table.append(f"| {x['pool_id']} | [{x['mall_title']}](https://mall.fanqiecopyright.com/pc/detail/{x['book_id']}) | [{x['title']}]({x['original_url']})／{x['author']}／{x['book_id']} | {x['main_site_readers_display'] or '未知'} | {'已核实身份与热度' if x in known else '身份已核实；热度未知，搜索前三项未匹配'} |")
table += ['\n可见在读无法确定的8部保留在候选池；他们可能比已核实作品热，不声称已排全40部的绝对前十。机器完整记录含分类、来源时间、页哈希和搜索URL：[verified-originals-readers.jsonl](verified-originals-readers.jsonl)。']
(root/'candidate-pool-and-readers.md').write_text('\n'.join(table),encoding='utf-8')
summary={'status':'PASS_STRUCTURAL_AND_PROVENANCE_CHECKS','semantic_review':'SELF_REVIEW_COMPLETE_INDEPENDENT_REVIEW_PENDING','candidate_count':40,'identity_verified':40,'reader_display_verified':32,'reader_display_unknown':8,'selected_books':10,'read_and_analyzed_chapters':len(chapter_rows),'local_text_hashes_match':100,'material_modules':8,'material_records':10,'frozen_artifacts_hashes_match':len(integrity['checks']),'frozen_manifest_equals_git':True,'full_book_download':'NOT_RUN_PENDING_APPROVAL','original_prose_in_delivery':False}
(ev/'delivery-validation.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False))
