"""Read-only frozen package search. Writes research receipts, never the library."""
import argparse, hashlib, json, subprocess, sys
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('--library', required=True)
a = p.parse_args()
library = Path(a.library).resolve()
out = Path(__file__).resolve().parent
repo = out.parents[3]
manifest = json.loads((library / 'manifest.json').read_text(encoding='utf-8'))
hashes = manifest.get('artifact_sha256', {})
checks = [{'path': name, 'expected': sha, 'actual': hashlib.sha256((library/name).read_bytes()).hexdigest()} for name, sha in hashes.items()]
assert checks and all(x['expected'] == x['actual'] for x in checks), 'Frozen artifact mismatch'
(out/'frozen-material-integrity.json').write_text(json.dumps({'frozen_commit':'1e10e6e3ffb70eda94a400073155fd89db724ce9','package_status':manifest['status'],'artifact_count':len(checks),'checks':checks},ensure_ascii=False,indent=2),encoding='utf-8')
queries = [
 ('A','爽 震撼 反差 认可 验证 反杀','金手指,世界观,修炼体系,开篇'),
 ('B','紧张 智斗 信息 误判 反杀 代价','金手指,人物功能,剧情机制'),
 ('C','燃 团队 合作 认可 资源 成长 兑现','人物功能,主线,篇章结构'),
]
script = repo/'skills/novel-creation-planner/scripts/search_dna_candidates.py'
for name, query, modules in queries:
    result = subprocess.run([sys.executable,'-X','utf8',str(script),'--library',str(library),'--query',query,'--modules',modules,'--include-per-book','--limit','12','--max-per-book','2','--format','json'],capture_output=True,text=True,encoding='utf-8',check=True)
    data = json.loads(result.stdout)
    (out/f'material-search-{name}.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    print(name,[(x['record_id'],x['path']) for x in data['results']])
