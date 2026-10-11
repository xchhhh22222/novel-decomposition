"""Read back the pushed Git tree and every research blob, then save a local receipt."""
import argparse, hashlib, json, subprocess
from pathlib import Path

p=argparse.ArgumentParser()
p.add_argument('--branch',default='codex/urban-high-martial-mall-benchmark-v1')
p.add_argument('--output',required=True,help='Receipt outside Git, since it contains the final commit SHA')
a=p.parse_args()
repo=Path(__file__).resolve().parents[4]
prefix='research/market-short-drama-v1/mall-urban-high-martial-2026-10-11'
def git(*args):
    return subprocess.run(['git','-C',str(repo),*args],capture_output=True,check=True).stdout
head=git('rev-parse','HEAD').decode().strip()
remote=git('ls-remote','origin','refs/heads/'+a.branch).decode().split()[0]
assert head==remote, 'Local and remote commit differ'
git('fetch','origin',a.branch)
fetched=git('rev-parse','refs/remotes/origin/'+a.branch).decode().strip()
assert fetched==remote
files=[]
for entry in git('ls-tree','-r','-z',remote,'--',prefix).split(b'\0'):
    if not entry:continue
    meta,name=entry.split(b'\t',1)
    relative=name.decode('utf-8')
    blob=meta.decode().split()[2]
    local_blob=git('hash-object','--path='+relative,str(repo/relative)).decode().strip()
    assert local_blob==blob,relative
    content=git('show',remote+':'+relative)
    local_commit_content=git('show',head+':'+relative)
    assert content==local_commit_content,relative
    files.append({'path':relative,'blob_sha':blob,'remote_bytes_sha256':hashlib.sha256(content).hexdigest(),'matches_working_tree_with_git_filters':True})
assert len(files)>=39
status=git('status','--porcelain').decode().strip()
assert not status,status
result={'status':'PASS','branch':a.branch,'local_head':head,'remote_head':remote,'fetched_remote_head':fetched,'files_read_back':len(files),'all_content_matches':True,'working_tree_clean':True,'files':files}
output=Path(a.output).resolve()
assert not output.is_relative_to(repo), 'Post-commit receipt must stay outside repository'
output.parent.mkdir(parents=True,exist_ok=True)
output.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k!='files'},ensure_ascii=False))
