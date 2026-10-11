import json, re
from urllib.parse import quote
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
# Browser searches actually performed on 2026-10-11. These eight full-name +
# author searches returned unrelated books in the first three visible results;
# no unrelated result's reader count is assigned to the requested original.
NOT_MATCHED={'M02','M03','M05','M07','M11','M13','M16','M17'}
DISPLAY={'M06':'1万人在读','M09':'4314人在读','M10':'4542人在读','M12':'3.6万人在读','M23':'5933人在读','M31':'181.7万人在读','M32':'121.7万人在读','M33':'106.5万人在读','M34':'75.2万人在读','M35':'67.1万人在读','M36':'63.6万人在读','M37':'95.9万人在读','M38':'96万人在读','M39':'71.8万人在读','M40':'70.4万人在读'}
rows=[json.loads(x) for x in (ROOT/'verified-originals-readers.jsonl').read_text(encoding='utf-8').splitlines()]
searches=[]
for r in rows:
    query=r['title']+' '+r['author']
    r['main_site_search_query']=query
    r['main_site_search_url']='https://fanqienovel.com/search/'+quote(query)
    r['search_performed_in_browser']=True
    r['main_site_readers_display']=None if r['pool_id'] in NOT_MATCHED else DISPLAY.get(r['pool_id'],'未满1000人在读')
    r['readership_status']='UNKNOWN_SEARCH_IDENTITY_NOT_MATCHED' if r['pool_id'] in NOT_MATCHED else 'VERIFIED_MAIN_SITE_DISPLAY'
    r['readership_interval']=[None,None] if r['pool_id'] in NOT_MATCHED else ([None,1000] if r['pool_id'] not in DISPLAY else None)
    r['read_count_interpretation']='DIAGNOSTIC_ONLY_NOT_USED_FOR_HEAT' if r['pool_id'] in NOT_MATCHED else ('CENSORED_LT_1000_NO_WITHIN_BAND_RANK' if r['pool_id'] not in DISPLAY else 'DISPLAY_VERIFIED_PUBLIC_COUNT')
    searches.append({k:r[k] for k in ['pool_id','main_site_search_query','main_site_search_url','search_performed_in_browser','main_site_readers_display','readership_status']})
(ROOT/'verified-originals-readers.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in rows),encoding='utf-8')
(ROOT/'evidence/main-site-search-log.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in searches),encoding='utf-8')
def observed_heat(r):
    text=r['main_site_readers_display']
    return float(re.search(r'[0-9.]+',text)[0])*(10000 if '万' in text else 1)
selected=sorted([r for r in rows if r['readership_status']=='VERIFIED_MAIN_SITE_DISPLAY' and r['pool_id'] in DISPLAY],key=observed_heat,reverse=True)[:10]
header='''# 主站在读核实后的热门10本

采样日期：2026-10-11。40部商城实际候选，30部来自类别第1/100页各前15张，10部为当天主站都市高武阅读榜的补充对照，再实际回商城查卡及详情。该补充样本有明确热度偏向，不是商城随机样本；不声称全商城穷尽排名。

所有入选书都实际在商城找到，且详情ID与主站book_id、作者一致。商城别名按ID桥接，不凭文字近似。按主站公开在读展示档位筛选；同档不强排。“未满1000人在读”保留区间；8部搜索未匹配者热度未知，不用商城数据填补。原著页公共状态数值保留作取证，低档数值不作精确热度宣称。

| 顺位 | 原著完整书名／作者 | 主站在读展示 | 商城书名 | 主站／商城 |
| --- | --- | --- | --- | --- |
'''
for i,r in enumerate(selected,1):
    header+=f"| {i} | 《{r['title']}》／{r['author']} | {r['main_site_readers_display']} | {r['mall_title']} | [原著]({r['original_url']})／[商城](https://mall.fanqiecopyright.com/pc/detail/{r['book_id']}) |\n"
header+='\n筛选边界：从32部已核热度候选中筛选。8部热度未知仍可能较热门，不声称40部绝对前十。在读衡量当前消费热度，不能证明开篇结构导致该热度；长篇积累、作者、更新、推广、完结状态均可能影响结果。主站分类1014含现代异能、架空高武、神域经营等，拆解另行评估现代都市质感，不以标签代替正文判断。\n\nMALL_HIGH_READ_TEN=VERIFIED（限已核热度候选）。FULL_BOOK_DOWNLOAD=NOT_RUN_PENDING_APPROVAL。\n'
(ROOT/'selected-high-read-10.md').write_text(header,encoding='utf-8')
print('40 identities; 32 readership displays verified; 8 unknown; 10 selected')
