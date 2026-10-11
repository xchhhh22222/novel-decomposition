"""Read-only verification of this isolated research bundle and eight pinned source blobs."""
import argparse, collections, hashlib, json, re, subprocess
from pathlib import Path

p=argparse.ArgumentParser();p.add_argument('--source-repo',required=True);a=p.parse_args()
root=Path(__file__).resolve().parent.parent
source=Path(a.source_repo).resolve()
commit='718d853c01c165b4caa0bd0cd812311081578fe9'
files=json.loads((root/'evidence/source-verification.json').read_text(encoding='utf8'))
versions=json.loads((root/'evidence/version-comparison.json').read_text(encoding='utf8'))
index=[json.loads(x) for x in (root/'evidence/chapter-source-index.jsonl').read_text(encoding='utf8').splitlines()]
assert len(files)==8 and len(index)==160 and len(versions)==8
assert [v['research_id'] for v in files]==[f'N8_{n:02d}' for n in range(1,9)]
checked=[]
for v in files:
    raw=subprocess.run(['git','-C',str(source),'show',commit+':'+v['path']],capture_output=True,check=True).stdout
    assert len(raw)==v['size'] and hashlib.sha256(raw).hexdigest()==v['sha256']
    assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==v['sha']
    text=raw.decode('utf-8-sig',errors='strict');lines=text.splitlines()
    heads=[(n,m) for n,s in enumerate(lines) if (m:=re.match(r'^第\s*(\d+)\s*章\s*(.*)',s.strip()))]
    nums=[int(m.group(1)) for _,m in heads];counts=collections.Counter(nums)
    assert len(heads)==v['chapter_count'] and max(nums)==v['max_printed_chapter'] and nums[-1]==v['last_printed_chapter']
    assert sorted(set(range(1,max(nums)+1))-set(nums))==v['missing_chapters']
    assert [n for n,c in counts.items() if c>1]==v['duplicate_numbers']
    assert text.count('\ufffd')==v['replacement_characters']
    assert sum(0xe000<=ord(c)<=0xf8ff for c in text)==v['private_use_characters']
    all_hashes=collections.defaultdict(list)
    for k,(start,m) in enumerate(heads):
        end=heads[k+1][0] if k+1<len(heads) else len(lines)
        body='\n'.join(lines[start+1:end]).strip();digest=hashlib.sha256(body.encode()).hexdigest()
        all_hashes[digest].append(int(m.group(1)))
        if k>=20:continue
        x=next(x for x in index if x['research_id']==v['research_id'] and x['ordinal']==k+1)
        assert x['chapter']==k+1==int(m.group(1)) and x['title']==m.group(2)
        assert x['start_line']==start+1 and x['end_line']==end and x['body_sha256']==digest
        assert x['source_file_sha256']==v['sha256'] and x['source_blob_sha']==v['sha'] and x['source_commit']==commit
        if k<10:
            normalized=re.sub(r'\s+','',re.sub(r'^章节更新时间：.*$','',body,flags=re.M))
            old=next(z for z in versions if z['research_id']==v['research_id'])['first_ten_checks'][k]
            assert hashlib.sha256(normalized.encode()).hexdigest()==old['new_normalized_sha256']
    assert [z for z in all_hashes.values() if len(z)>1]==v['exact_duplicate_bodies']
    doc=(root/'books'/f"{v['research_id']}.md").read_text(encoding='utf8')
    assert '{{' not in doc
    for n in range(11,21):assert f'[第{n}章 ' in doc
    for field in ['来源','初始困境','压力来源','金手指功能','主角行动','翻盘关键','情绪变化','具体兑现','状态变化','下一循环','原创借鉴','疲劳风险']:
        assert f'| {field} |' in doc,(v['research_id'],field)
    checked.append(v['research_id'])
for name in ['README.md','source-verification.md','comparison.md','candidates-and-dedup.md']:
    assert (root/name).is_file()
for doc in root.rglob('*.md'):
    for link in re.findall(r'\]\(([^)]+)\)',doc.read_text(encoding='utf8')):
        if link.startswith(('https://','http://','#')):continue
        assert (doc.parent/link.split('#')[0]).resolve().exists(),(str(doc),link)
assert sum(x['equal_content_chapters'] for x in versions)==79
assert all(len(x['first_ten_checks'])==10 for x in versions)
assert len(json.loads((root/'evidence/material-read-receipts.json').read_text(encoding='utf8'))['reads'])==12
assert all(p.suffix in {'.md','.json','.jsonl','.py','.txt'} for p in root.rglob('*') if p.is_file())
assert not any(p.name.startswith('original.') or re.match(r'chapter-\d+',p.name) for p in root.rglob('*') if p.is_file())
print(json.dumps({'status':'STRUCTURAL_AND_SOURCE_CHECKS_PASS','books':checked,'source_blobs':8,'chapter_index_rows':160,'new_chapter_rows':80,'normalized_equal_first_ten':79,'semantic_independent_review':'PENDING'},ensure_ascii=False))
