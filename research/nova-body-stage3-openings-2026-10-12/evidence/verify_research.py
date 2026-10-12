"""Read-only structural/scope verifier; never a semantic or literary quality gate."""
from pathlib import Path
import json,re,hashlib,subprocess
ROOT=Path(__file__).resolve().parents[1]; REPO=ROOT.parents[1]
PREFIX=ROOT.relative_to(REPO).as_posix()
BASE='0f250ea375c61aaa7e9693924a89657a37618a3e'
def digest(raw):return hashlib.sha256(raw).hexdigest()
def j(name):return json.loads((ROOT/'evidence'/name).read_text(encoding='utf8'))
def rows(name):return [json.loads(s) for s in (ROOT/'evidence'/name).read_text(encoding='utf8').splitlines() if s]
def git(*args):return subprocess.run(['git','-C',str(REPO),*args],capture_output=True,check=True).stdout
def verify():
 new=rows('chapter-source-index.jsonl');log=rows('reading-log.jsonl');oldrows=rows('reused-body-1-50-index.jsonl')
 assert [r['chapter'] for r in new]==list(range(51,101))
 assert [r['chapter'] for r in log]==list(range(51,101))
 assert [r['chapter'] for r in oldrows]==list(range(1,51))
 assert len({r['body_sha256'] for r in new})==50
 assert all(r['research_id']=='N8_03' and r['book_id']=='7592279900040465433' for r in new)
 assert all(r['full_body_semantically_read'] and not r['raw_text_published'] for r in log)
 assert all(not r['new_semantic_read_this_run'] for r in oldrows)
 report=(ROOT/'body-51-100.md').read_text(encoding='utf8')
 assert not re.search(r'\{\{\d+\}\}',report)
 for r in new:
  assert f"[第{r['chapter']}章 {r['title']}]({r['evidence_url']})" in report
  assert '718d853c01c165b4caa0bd0cd812311081578fe9' in r['evidence_url']
  assert r['start_line']<r['end_line'] and r['characters']>1000
  assert next(q for q in log if q['chapter']==r['chapter'])['body_sha256']==r['body_sha256']
 frozen=j('old-experiments-freeze.json');raw=(REPO/frozen['path']).read_bytes()
 assert digest(raw)==frozen['file_sha256'] and raw==git('show',BASE+':'+frozen['path'])
 for r in frozen['sections']:
  assert digest('\n'.join(raw.decode().splitlines()[r['start_line']-1:r['end_line']]).encode())==r['section_sha256_lf']
 for r in j('reuse-receipts.json')['report_references']:
  assert digest((REPO/r['path']).read_bytes())==r['sha256']
 changed=git('diff','--name-only',BASE).decode().splitlines()
 untracked=git('ls-files','--others','--exclude-standard').decode().splitlines()
 assert all(p.startswith(PREFIX+'/') for p in changed+untracked)
 for p in ROOT.rglob('*'):
  if not p.is_file():continue
  assert p.suffix in ['.md','.json','.jsonl','.py'],p
  raw=p.read_bytes();text=raw.decode('utf8'); assert b'\r' not in raw and '\ufffd' not in text,p
  if p.suffix=='.json':json.loads(text)
  if p.suffix=='.jsonl': [json.loads(s) for s in text.splitlines() if s]
  if p.suffix=='.md':
   for ref in re.findall(r'(?<!!)\]\(([^)]+)\)',text):
    if re.match(r'^[A-Za-z]+:',ref):continue
    assert (p.parent/ref.split('#')[0]).exists(),(p,ref)
 for r in j('artifact-manifest.json')['files']:
  raw=(ROOT/r['path']).read_bytes();assert len(raw)==r['bytes'] and digest(raw)==r['sha256'],r['path']
 exp=(ROOT/'high-burst-opening-experiments.md').read_text(encoding='utf8')
 assert all('## 新案'+s in exp for s in ['D','E','F'])
 assert exp.count('**一句话卖点**')==3 and exp.count('**前三章强兑现**')==3 and exp.count('**前10章第二次兑现**')==3
 assert exp.count('**情绪因果图**')==3 and 'PENDING_AUTHOR_REVIEW' in exp
 assert '100学院任务刚接受' in (ROOT/'README.md').read_text(encoding='utf8')
 return {'machine_scope_status':'CHECKS_PASSED','semantic_research_acceptance':'PENDING_INDEPENDENT_REVIEW','creative_opening_quality':'PENDING_AUTHOR_REVIEW','new_chapters':50,'new_characters':sum(r['characters'] for r in new),'prior_chapters_reused':50,'old_experiment_sections_unchanged':3,'new_opening_candidates':['D','E','F'],'outside_prefix_changes':[],'raw_source_files_published':0,'material_promotion':'HOLD','full_book_decomposition':'NOT_RUN','limitations':'Structural checks do not establish semantic correctness, reader response, literary quality or full numeric consistency.'}
if __name__=='__main__':print(json.dumps(verify(),ensure_ascii=False,indent=2))
