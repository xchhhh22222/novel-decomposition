# NOVA 市场双池试验 V1 — 番茄都市高武 × 版权/IP改编

> **RESEARCH ONLY / NOT PRODUCTION**。用户目标：同时提升番茄网文可读性与红果等微短剧改编适配性。该目标不等于任何榜单/题材保证签约、流量、授权或改编。2026-10-11 核查：可确认番茄官网新书/阅读榜及作者版权专区；尚未验证稳定、公开、正式命名为“版权榜”的 Top10 接口。不得虚构其存在、名次或前10作品。

## 1. 两个来源独立采样，各最多十名

### Pool A — 版权榜 / 改编结果与IP潜力

用户指定 **“番茄版权榜前10”**。首先查证精确入口：官方产品/APP 展示的榜单名、URL或用户授权的页面截图、更新时间、排名规则、书名与 book_id。只有真的证实它是**排序榜单**、能核实 1–10 名，才能写：

- `pool_id=COPYRIGHT_TOP10`
- `verification=VERIFIED_OFFICIAL_RANKING`
- `rank=1…10`

**如果未核实，必须记** `COPYRIGHT_RANK_UNVERIFIED / NO_RANKS_ASSERTED`，保留空的该榜单候选、已检索的官方链接及精确缺口。允许用户提供榜单截图/链接后人工逐项核验；不得由创作模型凭记忆补10部作品。

可另采集**明确声明的补充观察池**：
- 番茄版权专区公开的已售/合作 IP 事实（存在授权项才可标 `RIGHTS_CONFIRMED`，且可能不是排行）。
- 番茄“巅峰榜”中被声明的IP潜力与传播价值信号（`PEAK_IP_POTENTIAL`，**绝不是 COPYRIGHT_TOP10**）。
- 若经核实存在面向微短剧改编的官方征文/公示作品清单，记 `OFFICIAL_IP_PROGRAM`，不是榜单。

以上三种**不得替代用户指定的正式版权榜 Top10**，不得从“IP潜力”反推出“改编权已经售出”。不同体裁（女频甜宠、现实家庭、男频战神等）仅抽取可迁移的 **情绪引爆、镜头冲突、角色关系、场景成本、转折与点击理由**；不拿题材热度机械套用男频都市高武。

### Pool B — 都市高武榜前10

保持既有可追溯主赛道：番茄**男频 / 都市高武 / 新书榜**前10，作为当前赛道的开篇读者信号。用户后续指定“阅读榜”时显式变更 `ranking=new|reading`；不得在同一快照混排新书与阅读。每本保留榜单URL、时间、rank、书名、作者、book_id、字数/在读等真实公开指标。没有权威样本不补造。

### 原则

- `dual_pool_target=10+10`，两池分开采样、分开统计，并以 `pool_memberships` 标记重合；不是强行“20本互不重合”。
- 两组都要查当前快照和历史变化（若存在真实历史）。**单日绝不是趋势**。
- A 研究“影视化/短剧化表达能力、实际授权证据”；B 研究“都市高武平台阅读表现”。**它们回答不同问题，不能把两个榜的名次加权求一个成功概率。**
- 榜单可达性必须由执行代理在本轮真实检验，报 `verified/partial/unavailable`；规则文档不是实际扫榜证据。
- 版权交易条件、付费、授权范围、改编成片率、流量转化率均未知时必须记 `NOT_VERIFIED`。

## 2. 采集与样本完整度

沿用 `execution-pipeline.md` 的合法取样、下载质量及来源门。指定的 `$fanqie-ranking-scan` 仅运行它**真实支持**的榜型/分类，不给它编造 `--ranking copyright`。对版权池，如果无受支持的采集能力：
1. 优先保存确实存在的公开官方网页元数据（若页可验证）；
2. 若版权榜为仅APP可见或受权限保护，征求用户截图/页面导出，`ingest_mode=user_authorized`，确保来源、日期、rank、book_id真实；
3. 没有则明确 `COPYRIGHT_RANK_UNVERIFIED`，绝不让第三方营销帖冒充官方版权榜。
4. 把失败/部分/用户导入留在manifest中，继续可独立完成的都市高武池；不得静默标记全部20/20完成。

试验模式并行保存：
```text
market_ip_dual_v1/
  manifest.json
  ranking_urban_new_top10.jsonl
  ranking_copyright_top10.jsonl  # only VERIFIED; otherwise empty with status
  supplementary_ip_references.jsonl
  opening_cards_urban.jsonl
  opening_cards_ip.jsonl
  dual_pool_structure_matrix.md
  short_drama_transfer_lessons.md
  evidence/
```
快照字段 `pool_id / rank / ranking_name / official_url / captured_at / book_id / access_boundary / source_status / rights_fact_level / actual_chapters_analyzed / extraction_method / evidence_locations`；无rank不能放入ranked top10，`null`不等于0。

原 V1.2 `market_benchmark.json` 的 `top10` **严格只接受10条**。**禁止将20条塞入旧字段来绕过验证器**。本试验使用**研究侧车证据包**，原 `validate_v12_artifacts.py benchmark` 和生产 Schema 原封不动。正式支持双榜前，旧baseline和新dual不能冒充同一种`complete`。

## 3. 两种市场信号怎么读

**都市高武池**：金手指第一次被观众感知的时点、战力尺度的可见事实、开篇冲突和选择、目标和首次兑现、1–3章及4–10章钩子。分类特殊性优先。

**版权/IP池**：核实的是榜单或权利事实，不预设版权作品均是成功短剧。仅在真实读到获授权的合法公开章节、合法公开改编成片内容或宣传资料后，观察：
- 可用一句话解释的能力/身份/利益冲突，主角当下必须做什么；
- 首个**可拍**场景、可见行为、情绪强度、谁掌握现场主动权；
- 角色的失控与冲动：羡妒/恐惧/偏爱/利益护持、但必须有内在动机和代价；
- 反转前后的观众已知事实，避免全靠旁白；
- 一次小兑现后立即开启下一难题；不是毫无因果地每30秒硬反转；
- 场景/制作成本：主要景别、可控场地、人数、异兽/CG需求，分别标**真人微短剧**、**AI漫剧/动画**可行性；
- 真实授权/IP潜力/阅读热度三项**分开**报证据。

所有开篇结构判断必须引用真正读过的章节/合法素材，不能仅凭书名、简介、版权新闻猜正文结构。跨池高频模式与类型差异分开汇总，并包含失败/难改编案例防止幸存者偏差。

## 4. 双池总结与开书输出

完成研究报告时分别答：

- B（赛道）：番茄都市高武近期读者对能力、强度、情绪兑现的具体期待是什么？实际支持这个判断的样本是哪几章？
- A（改编）：哪些已确认的小说 / IP 节目样本中，存在可以视听化的冲突、关系及反转？现有资料能否独立证明短剧改编，而不是仅有“IP潜力”？
- 交叉：保留都市高武能力爽感，同时让矛盾可见、人物有可拍摄的行动；不要把“高武玄幻”写成低武职场剧。
- 商业未知：签约资格、版权合同、平台风控/推荐机制、改编机会和收益不会因为符合榜单形态而自动获得。

**Stop/Status：**
`URBAN_TOP10=VERIFIED|PARTIAL|UNAVAILABLE`；
`COPYRIGHT_TOP10=VERIFIED|PARTIAL|COPYRIGHT_RANK_UNVERIFIED`；
`RIGHTS_ADAPTATION_SIGNAL=EVIDENCE_BOUND|UNVERIFIED`；
`DUAL_BENCHMARK=RESEARCH_PARTIAL|RESEARCH_COMPLETE`（只有两池实际完成才可complete）；
`IP_SIGNING_PREDICTION=NOT_ESTABLISHED`；
`PRODUCTION_PROMOTION=NOT_RUN`。

参考入口（不是实时版权排名证据）：
- 番茄排行：https://fanqienovel.com/rank
- 番茄作者版权专区：https://fanqienovel.com/writer/zone/copyright
- 巅峰榜（具有IP潜力维度，≠版权榜）：番茄APP书城-推荐-排行榜-巅峰榜；官网动态位置需现场核验。
