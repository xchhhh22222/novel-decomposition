"""Verify research sources and archive precise references; no production mutation."""
import hashlib,json,re,sys,subprocess
from pathlib import Path

REPO=Path(__file__).resolve().parents[3]
ROOT=REPO.parents[1]
OUT=Path(__file__).parent
BOOK=OUT.parent
LIB=ROOT/'.runs/emotion-arc-v2-20261009/creative-material-git-blobs/packages/shared-dna-library/v1.0.0'
COMMIT='1e10e6e3ffb70eda94a400073155fd89db724ce9'
sys.path.insert(0,str(REPO/'skills/novel-creation-planner/scripts'))
from search_dna_candidates import verify_shared_dna_package_integrity

def sha(b): return hashlib.sha256(b).hexdigest()
def save(name,value): (OUT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
manifest=json.loads((LIB/'manifest.json').read_text(encoding='utf-8'))
violations=verify_shared_dna_package_integrity(LIB,manifest)
if violations: raise ValueError(violations)
records=json.loads((OUT/'source-records-read.json').read_text(encoding='utf-8'))
byid={r['source_record']['record_id']:r for r in records}
specs=[
 ('02','GF:BOOK_005','/core_formula','ADOPT','PARTIAL','主动试探/现实核验；未采用未来预见，全部回响数值原创'),
 ('02','GF:BOOK_002','/core_formula','REJECT','READY','现金即时换修为使伤后训练与伙伴必要性消失'),
 ('03','WB:BOOK:BOOK_002','/factions/3','ADOPT','READY','商业将战力表现变收入，改为职业测试而非直播学校'),
 ('03','WB:BOOK:BOOK_005','/rule_chains/0','REJECT','PARTIAL','校园觉醒登记解释权容易把职业复出变能力身份悬疑'),
 ('04','CS:BOOK:BOOK_009','/skill_proficiency','ADOPT','READY','获得/练习/验证分离，迁移训练流程，不采用火系器物体系'),
 ('04','CS:BOOK:BOOK_008','/realm_system','REJECT','PARTIAL','欲力/神血/神武强耦合，不适配损伤康复的身体构筑'),
 ('05','CF:BOOK:BOOK_005','/relationship_engines/0','ADOPT','READY','信息不能替代独立执行者，改造为复测/停止权/付费合作'),
 ('05','DA:RELATIONSHIP:BOOK_017:002','','REJECT','READY','高位秘密血脉牵引不适配普通职业合作，避免现有项目秘密女主拓扑'),
 ('06','PL:BOOK:BOOK_009','/plotlines/1','ADOPT','READY','战果先经资源取舍变可部署能力，再开启义务；移除积分清零与训练营'),
 ('06','PL:BOOK:BOOK_007','/plotlines/0','REJECT','PARTIAL','身份逃亡在开篇吞掉公开工作目标'),
 ('07','OP:BOOK:BOOK_002','/selling_point_proof/0','ADOPT','READY','三章内实际操作卖点，用奖金结算和行动后果核验，不借氪金'),
 ('07','OP:BOOK:BOOK_001','/entry/0','REJECT','READY','审讯/能力身份/家庭低位转场会靠近已有临时工与研究救援开局'),
 ('08','AR:BOOK:BOOK_009','/arcs/1','ADOPT','READY','一次表现经正式结果变持续资源，再开启新责任；改为职业合同而非校际选拔'),
 ('08','AR:BOOK:BOOK_002','/arcs/1','REJECT','READY','考试状元认证不是职业服务的多用途成果，也会将全书导向校园'),
 ('09','PM:BOOK:BOOK_012','/mechanisms/6','ADOPT','READY','观察/区分性试探/修正假说，改为真实变招和留退路；不读心'),
 ('09','PM:BOOK:BOOK_016','/mechanisms/2','REJECT','READY','窃取/永久吸收他人天赋破坏只修自己的有限成长'),
]
source_map=[json.loads(line) for line in (LIB/'source-map.jsonl').read_text(encoding='utf-8').splitlines() if line.strip()]
selections=[]
(OUT/'source-row-snapshots').mkdir(exist_ok=True)
for module,rid,pointer,decision,interface,reason in specs:
 entry=byid[rid]; row=entry['source_record']; ref=entry['retrieval_ref']
 payload=(LIB/ref['path']).read_bytes()
 assert sha(payload)==manifest['artifact_sha256'][ref['path']]
 rawline=payload.splitlines()[ref['line']-1]
 assert json.loads(rawline)['record_id']==rid and row['qa_status']=='PASS'
 component=row
 if pointer:
  for token in pointer.strip('/').split('/'):
   component=component[int(token)] if isinstance(component,list) else component[token]
 evidence=[]
 def refs(x):
  if isinstance(x,dict):
   for key,v in x.items():
    if key in ('evidence_refs','direct_evidence_refs') and isinstance(v,list): evidence.extend(v)
    else: refs(v)
  elif isinstance(x,list):
   for v in x: refs(v)
 refs(component)
 if not evidence: evidence.extend(row.get('evidence_refs',[]))
 maps=[s for s in source_map if s.get('record_id')==rid and s.get('package_path')==ref['path'] and s.get('source_line')]
 (OUT/'source-row-snapshots'/f'{module}-{decision.lower()}.jsonl').write_bytes(rawline+b'\n')
 selections.append({'module':module,'decision':decision,'record_id':rid,'book_id':row['book_id'],'book_title':row.get('title'), 'frozen_commit':COMMIT,'package_path':ref['path'],'line':ref['line'],'component_path':pointer or '/', 'package_file_sha256':sha(payload),'git_blob_row_sha256':sha(rawline),'source_map':maps,'evidence_refs':list(dict.fromkeys(evidence)),'source_status':row.get('status'),'SOURCE_QA':'PASS','INTERFACE_READINESS':interface,'CURRENT_COMPATIBILITY':'ADAPTABLE' if decision=='ADOPT' else 'NOT_SELECTED','reason':reason,'original_parameters_not_source_facts':decision=='ADOPT','selected_component_snapshot':component})
save('material-selection.json',selections)
save('source-map-excerpts.json',[s for s in source_map if s.get('record_id') in byid])
save('package-byte-verification.json',{'status':'PASS','checker':'existing verify_shared_dna_package_integrity','frozen_commit':COMMIT,'artifact_count':len(manifest['artifact_sha256']),'violations':violations,'manifest_sha256':sha((LIB/'manifest.json').read_bytes()),'checkout_attempt':'FAIL: CRLF mismatch; retained','archive_attempt':'FAIL: archive EOL conversion; retained','final_export':'existing export_package uses git show bytes; no hash bypass','literary_approval':'NOT_GRANTED'})
stats={}
for number in range(1,4):
 p=BOOK/f'chapter-{number:02d}.md'; text=p.read_text(encoding='utf-8'); count=len(re.findall(r'[\u4e00-\u9fff]',text)); stats[p.name]={'han_count':count,'nonwhitespace_count':len(re.sub(r'\s','',text)),'sha256':sha(p.read_bytes())}; assert 2500<=count<=3500,(p.name,count)
required=['novel-concept.md','material-selection-report.md','emotion-arc-plan.md','chapter-01.md','chapter-02.md','chapter-03.md','chapters-04-10-outline.md','chapters-11-100-plan.md','creative-test-report.md']
assert all((BOOK/f).is_file() and (BOOK/f).stat().st_size>100 for f in required)
for module,_,_ in [(s['module'],s['decision'],s['record_id']) for s in selections]: assert module in ('02','03','04','05','06','07','08','09')
assert {s['module'] for s in selections if s['decision']=='ADOPT'}=={'02','03','04','05','06','07','08','09'}
assert all(json.loads((OUT/'git-blob-retrieval'/f'retrieval-{module}.json').read_text(encoding='utf-8')).get('include_per_book') for module in ('02','03','04','05','06','07','08','09'))
base='9ef17befd7508e69c6b7898206c579b08b86ed11'
changed=subprocess.run(['git','-C',str(REPO),'diff','--name-only',base],capture_output=True,encoding='utf-8',check=True).stdout.splitlines()
assert all(path.startswith('research/urban-high-martial-creative-test-v1/') for path in changed),changed
save('delivery-check.json',{'status':'PASS','scope':'file completeness, source/hash/selection/module resolution, chapter Han counts, changed-path scope only','code_base':base,'material_commit':COMMIT,'required_files':required,'chapters':stats,'adopted_modules':sorted({s['module'] for s in selections if s['decision']=='ADOPT'}),'canonical_schema_rmf_production_changed':False,'semantic_continuity':'manual findings in continuity-audit.md; not machine-proven','quality':'PENDING_INDEPENDENT_REVIEW','formal_planner_validators':'NOT_RUN: no production-schema plan created','legacy_enhanced_blind_comparison':'NOT_RUN'})
print(json.dumps({'sources':len(selections),'package_artifacts':len(manifest['artifact_sha256']),'chapters':stats,'status':'PASS: limited research checks'},ensure_ascii=False,indent=2))
