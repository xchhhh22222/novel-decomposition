"""Research evidence recorder. Calls the unchanged existing DNA search CLI."""
import hashlib, json, subprocess, sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
ROOT = REPO.parents[1]
FROZEN = ROOT / '.runs/emotion-arc-v2-20261009/creative-material-git-blobs'
LIB = FROZEN / 'packages/shared-dna-library/v1.0.0'
OUT = Path(__file__).parent / 'git-blob-retrieval'
OUT.mkdir(exist_ok=True)
sys.path.insert(0,str(REPO/'skills/novel-creation-planner/scripts'))
from run_emotion_arc_v2_research import export_package
export_package(ROOT/'.runs/emotion-arc-v2-20261009/nova-material-library','1e10e6e3ffb70eda94a400073155fd89db724ce9','packages/shared-dna-library/v1.0.0',FROZEN)
QUERIES = [
 ('02','金手指','逆袭 成本 反馈 修正 训练 消耗'),
 ('03','世界观','压迫 资源 资格 职业 城市 交易'),
 ('04','修炼体系','成长 实战 验证 身体 训练 代价'),
 ('05','人物功能','信任 利益 冲突 独立 合作 选择'),
 ('06','主线','自主 生存 资源 责任 选择'),
 ('07','开篇','紧张 生存 主动 首次 兑现'),
 ('08','篇章结构','反击 代价 兑现 资格 资源'),
 ('09','剧情机制','智斗 验证 反制 利益 风险'),
]
log=[]
for number,module,query in QUERIES:
 cmd=[sys.executable,'-X','utf8',str(REPO/'skills/novel-creation-planner/scripts/search_dna_candidates.py'), '--library',str(LIB),'--query',query,'--modules',module,'--include-per-book','--limit','5','--max-per-book','2','--format','json']
 p=subprocess.run(cmd,capture_output=True,encoding='utf-8')
 dest=OUT/f'retrieval-{number}.json'
 dest.write_text(p.stdout,encoding='utf-8',newline='\n')
 (OUT/f'retrieval-{number}.stderr.txt').write_text(p.stderr,encoding='utf-8',newline='\n')
 log.append({'module':number,'query':query,'argv':cmd,'exit_code':p.returncode,'output':dest.name,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'material_commit':'1e10e6e3ffb70eda94a400073155fd89db724ce9'})
 if p.returncode: print(number,'ERROR',p.stderr,p.stdout[:500]); continue
 data=json.loads(p.stdout)
 print(number, json.dumps(data,ensure_ascii=False)[:650] if not isinstance(data,dict) else 'keys='+str(list(data)))
 rows=data.get('results',data.get('candidates',[])) if isinstance(data,dict) else data
 for row in rows:
  print(json.dumps({k:row.get(k) for k in ('material_id','record_id','book_id','title','score','source_path','component_path','qa_status','summary')},ensure_ascii=False)[:1300])
(OUT/'retrieval-log.json').write_text(json.dumps(log,ensure_ascii=False,indent=2),encoding='utf-8',newline='\n')
