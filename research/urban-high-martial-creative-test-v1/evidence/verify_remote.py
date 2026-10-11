"""Read uploaded GitHub blobs into a fresh object database, not local refs."""
import hashlib,json,re,subprocess,tempfile
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

REPO=Path(__file__).resolve().parents[3]
OUT=Path(__file__).parent
PREFIX='research/urban-high-martial-creative-test-v1'
BRANCH='research/urban-high-martial-creative-test-v1'
def git(*args): return subprocess.run(['git','-C',str(REPO),*args],capture_output=True,encoding='utf-8',check=True).stdout.strip()
head=git('rev-parse','HEAD')
origin='https://github.com/xchhhh22222/novel-decomposition.git'
remote=git('ls-remote','--heads',origin,'refs/heads/'+BRANCH).split()[0]
assert remote==head,(head,remote)
fresh=Path(tempfile.mkdtemp(prefix='urban-creative-remote-',dir=str(REPO.parents[1]/'.runs')))
subprocess.run(['git','init','--bare',str(fresh)],capture_output=True,check=True)
subprocess.run(['git','-C',str(fresh),'fetch','--depth=1',origin,'refs/heads/'+BRANCH],capture_output=True,check=True)
def fresh_git(*args): return subprocess.run(['git','-C',str(fresh),*args],capture_output=True,check=True).stdout
assert fresh_git('rev-parse','FETCH_HEAD').decode().strip()==head
required=['README.md','novel-concept.md','material-selection-report.md','emotion-arc-plan.md','chapter-01.md','chapter-02.md','chapter-03.md','chapters-04-10-outline.md','chapters-11-100-plan.md','creative-test-report.md','evidence/material-selection.json','evidence/delivery-check.json','evidence/usage-log.jsonl']
def read_back(name):
 b=fresh_git('show',head+':'+PREFIX+'/'+name); local=(REPO/PREFIX/name).read_bytes()
 assert b==local,(name,'remote/local bytes differ')
 result={'path':name,'git_blob_sha':fresh_git('rev-parse',head+':'+PREFIX+'/'+name).decode().strip(),'byte_length':len(b),'sha256':hashlib.sha256(b).hexdigest(),'remote_read_back':'MATCH','url':f'https://github.com/xchhhh22222/novel-decomposition/blob/{head}/{PREFIX}/{name}'}
 if name.startswith('chapter-0'):
  text=b.decode('utf-8'); lines=[line for line in text.splitlines() if line.strip()]
  result.update({'han_count':len(re.findall(r'[\u4e00-\u9fff]',text)),'opening_read_back':lines[:2],'ending_read_back':lines[-1]})
 return result
with ThreadPoolExecutor(max_workers=4) as pool: files=list(pool.map(read_back,required))
changed=git('diff','--name-only','9ef17befd7508e69c6b7898206c579b08b86ed11',head).splitlines()
assert all(x.startswith(PREFIX+'/') for x in changed)
record={'status':'PASS','verified_content_commit':head,'remote_branch':BRANCH,'remote_ref_sha':remote,'method':'Fresh bare object database; git fetch from GitHub URL without alternates/local objects, git show actual UTF-8 blobs; compare complete bytes','remote_object_database':str(fresh),'failed_attempt':'gh api unavailable: GitHub CLI is not logged in; no token access or login attempted; Git HTTPS credential flow succeeded','files':files,'diff_scope':'research directory only','changed_file_count':len(changed),'quality_approval':'NOT_GRANTED','followup_metadata_commit':'This record may be committed after the verified content commit; final branch tip reported separately to avoid a self-referential SHA.'}
(OUT/'remote-verification.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps({'verified_commit':head,'remote_ref_sha':remote,'files_read':len(files),'chapters':[x for x in files if x['path'].startswith('chapter-0')],'scope':'research only'},ensure_ascii=False,indent=2))
