"""Read back uploaded research text via GitHub; records content, not quality."""
import base64,hashlib,json,re,subprocess
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

REPO=Path(__file__).resolve().parents[3]
OUT=Path(__file__).parent
PREFIX='research/urban-high-martial-creative-test-v1'
BRANCH='research/urban-high-martial-creative-test-v1'
def git(*args): return subprocess.run(['git','-C',str(REPO),*args],capture_output=True,encoding='utf-8',check=True).stdout.strip()
def api(endpoint): return json.loads(subprocess.run(['gh','api',endpoint],capture_output=True,encoding='utf-8',check=True).stdout)
head=git('rev-parse','HEAD')
remote=api('repos/xchhhh22222/novel-decomposition/git/ref/heads/'+BRANCH)['object']['sha']
assert remote==head,(head,remote)
required=['README.md','novel-concept.md','material-selection-report.md','emotion-arc-plan.md','chapter-01.md','chapter-02.md','chapter-03.md','chapters-04-10-outline.md','chapters-11-100-plan.md','creative-test-report.md','evidence/material-selection.json','evidence/delivery-check.json','evidence/usage-log.jsonl']
def read_back(name):
 data=api(f'repos/xchhhh22222/novel-decomposition/contents/{PREFIX}/{name}?ref={head}')
 b=base64.b64decode(data['content']); local=(REPO/PREFIX/name).read_bytes()
 assert b==local,(name,'remote/local bytes differ')
 result={'path':name,'git_blob_sha':data['sha'],'byte_length':len(b),'sha256':hashlib.sha256(b).hexdigest(),'remote_read_back':'MATCH','url':data['html_url']}
 if name.startswith('chapter-0'):
  text=b.decode('utf-8'); lines=[line for line in text.splitlines() if line.strip()]
  result.update({'han_count':len(re.findall(r'[\u4e00-\u9fff]',text)),'opening_read_back':lines[:2],'ending_read_back':lines[-1]})
 return result
with ThreadPoolExecutor(max_workers=4) as pool: files=list(pool.map(read_back,required))
changed=git('diff','--name-only','9ef17befd7508e69c6b7898206c579b08b86ed11',head).splitlines()
assert all(x.startswith(PREFIX+'/') for x in changed)
record={'status':'PASS','verified_content_commit':head,'remote_branch':BRANCH,'remote_ref_sha':remote,'method':'GitHub contents API read actual UTF-8 payload; compare complete bytes, not filenames only','files':files,'diff_scope':'research directory only','changed_file_count':len(changed),'quality_approval':'NOT_GRANTED','followup_metadata_commit':'This record may be committed after the verified content commit; final branch tip reported separately to avoid a self-referential SHA.'}
(OUT/'remote-verification.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps({'verified_commit':head,'remote_ref_sha':remote,'files_read':len(files),'chapters':[x for x in files if x['path'].startswith('chapter-0')],'scope':'research only'},ensure_ascii=False,indent=2))
