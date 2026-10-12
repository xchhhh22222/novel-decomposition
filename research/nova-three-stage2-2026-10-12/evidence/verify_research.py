"""Read-only, stage-specific content/scope checks; not a production schema or semantic gate."""
from pathlib import Path
import argparse,hashlib,json,re,subprocess

FROZEN='718d853c01c165b4caa0bd0cd812311081578fe9'
BASE='95ccb616fd7c157c2376b938fb6f8f3ef7fdd0c5'
SCOPE={'N8_06','N8_01','N8_03'}
PREFIX='research/nova-three-stage2-2026-10-12/'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def run(repo,*args):return subprocess.run(['git','-C',str(repo),*args],check=True,capture_output=True).stdout
def verify(source_repo=None):
 root=Path(__file__).resolve().parent.parent; repo=root.parent.parent
 rows=[json.loads(x) for x in (root/'evidence/chapter-source-index.jsonl').read_text(encoding='utf8').splitlines()]
 reused=[json.loads(x) for x in (root/'evidence/reused-chapter-index.jsonl').read_text(encoding='utf8').splitlines()]
 log=[json.loads(x) for x in (root/'evidence/reading-log.jsonl').read_text(encoding='utf8').splitlines()]
 assert len(rows)==90 and len(reused)==60 and len(log)==90
 assert {(r['research_id'],r['chapter']) for r in rows}=={(b,c) for b in SCOPE for c in range(21,51)}
 assert {(r['research_id'],r['chapter']) for r in reused}=={(b,c) for b in SCOPE for c in range(1,21)}
 for r,l in zip(rows,log):
  assert r['source_commit']==FROZEN and FROZEN in r['evidence_url']
  assert r['body_sha256']==l['body_sha256'] and l['full_body_semantically_read'] and not l['raw_text_published']
 source_checks=[]
 if source_repo:
  for b in sorted(SCOPE):
   group=[r for r in rows+reused if r['research_id']==b]
   raw=run(source_repo,'show',FROZEN+':'+group[0]['source_path']);lines=raw.decode('utf8',errors='strict').splitlines()
   assert sha(raw)==group[0]['source_file_sha256']
   for r in group:
    title=lines[r['start_line']-1];m=re.match(r'^第\s*(\d+)\s*章\s*(.*)',title.strip())
    assert m and int(m[1])==r['chapter'] and m[2]==r['title']
    body='\n'.join(lines[r['start_line']:r['end_line']]).strip()
    assert sha(body.encode())==r['body_sha256'] and len(body)==r['characters']
   source_checks.append({'book':b,'source_file_sha256':sha(raw),'indexed_chapters_checked':50,'semantic_new_reads':30})
 fields=['来源','初始困境','压力来源','金手指功能','主角行动','翻盘关键','情绪变化','具体兑现','状态变化','下一循环','原创借鉴']
 for b in sorted(SCOPE):
  text=(root/'books'/f'{b}.md').read_text(encoding='utf8')
  chapter_rows=re.findall(r'^\| \[第(\d+)章 .*?\]\(',text,re.M)
  assert list(map(int,chapter_rows))==list(range(21,51)),(b,chapter_rows)
  assert all(f'| {f} |' in text for f in fields)
  assert all(w in text for w in ['21—30','31—40','41—50','flowchart','前50章金手指使用谱系','疲劳','100章'])
  assert 'UNKNOWN' in text
 required=['README.md','cross-book-comparison.md','cross-book-emotion-fusion.md','fusion-candidate-cards.md','verification-and-gaps.md']
 assert all((root/p).is_file() for p in required)
 parsed=[];md_links=0
 for p in root.rglob('*'):
  if '__pycache__' in p.parts:continue
  if not p.is_file():continue
  raw=p.read_bytes();assert b'\r\n' not in raw,str(p)
  if p.suffix in ['.md','.json','.jsonl','.py']:raw.decode('utf8',errors='strict')
  if p.suffix=='.json':json.loads(raw.decode());parsed.append(str(p.relative_to(root)))
  if p.suffix=='.jsonl':
   for line in raw.decode().splitlines():json.loads(line)
   parsed.append(str(p.relative_to(root)))
  if p.suffix=='.md':
   txt=raw.decode();assert not re.search(r'\{\{\d+\}\}|@N8_\d\d:\d+',txt)
   for target in re.findall(r'\]\(([^)]+)\)',txt):
    if target.startswith(('http:','https:')):continue
    path=target.split('#')[0];assert (p.parent/path).exists(),(str(p),target)
    md_links+=1
 assert not list(root.rglob('*.txt')),'raw text files are outside research tree'
 run(repo,'merge-base','--is-ancestor',BASE,'HEAD')
 branch=run(repo,'branch','--show-current').decode().strip();assert branch=='codex/nova-three-stage2-20261012'
 changed=set(run(repo,'diff','--name-only',BASE).decode().splitlines())
 changed.update(run(repo,'ls-files','--others','--exclude-standard').decode().splitlines())
 assert all(p.startswith(PREFIX) for p in changed),sorted(changed)
 return {'deterministic_status':'PASS','new_chapters':90,'new_books':3,'prior_chapters_reused':60,'source_body_index_checks':source_checks,'json_files_parsed':len(parsed),'relative_links_checked':md_links,'scope_only_new_research_directory':True,'branch':branch,'baseline':BASE,'source_commit':FROZEN,'raw_text_published':False,'semantic_review':'SELF_REVIEW_COMPLETED_WITH_EXPLICIT_GAPS','independent_review':'PENDING','material_promotion':'NOT_RUN','production':'HOLD','known_unknowns_do_not_receive_machine_pass':True}
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--source-repo',type=Path);args=parser.parse_args()
 print(json.dumps(verify(args.source_repo),ensure_ascii=False,indent=2))
