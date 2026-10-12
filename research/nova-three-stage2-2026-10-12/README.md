# NOVA 都市高武第二阶段研究交付

研究分支：`codex/nova-three-stage2-20261012`。基于用户已验收的第一阶段提交`95ccb616fd7c157c2376b938fb6f8f3ef7fdd0c5`，冻结原著`718d853c01c165b4caa0bd0cd812311081578fe9`。本轮只新增N8_06/N8_01/N8_03第21—50章，90章全部全文实读；另完成此前明确追加的跨书情绪融合。没有新增拆解其他作品、51章以后或重复生成前20章报告。

| 交付 | 文件 / 内容 |
| --- | --- |
| 三本实证研究与完整使用谱系 | [时停](books/N8_06.md)、[别人氪金造神](books/N8_01.md)、[待我拼好身体](books/N8_03.md)：各30章、21—30/31—40/41—50小结、连续图、六组循环（开放段不伪闭环）、前50章累积谱系 |
| 剧情/情绪对照、高潮后疲劳、既有候选裁决、100章建议 | [cross-book-comparison.md](cross-book-comparison.md) |
| 因果接力、多线交织、情绪对冲的来源和反事实；三种不同发动机原创实验 | [cross-book-emotion-fusion.md](cross-book-emotion-fusion.md) |
| A/B/C补证修订、三项融合研究变体、02—09/EL/EW/MA/AH去重兼容 | [fusion-candidate-cards.md](fusion-candidate-cards.md) |
| 冻结输入、90新增来源和60复用来源 | [input-freeze](evidence/input-freeze.json)、[新增来源](evidence/chapter-source-index.jsonl)、[复用来源](evidence/reused-chapter-index.jsonl) |
| 实读记录、素材读取、疑点与校验 | [reading-log](evidence/reading-log.jsonl)、[素材回执](evidence/material-read-receipts.json)、[疑点表](evidence/uncertainty-register.json)、[QA](evidence/qa-report.json)、[验证说明](verification-and-gaps.md) |

研究结论：优先送审N8_03继续100章，N8_06次选，N8_01先暂缓。前者的独立证人/责任转嫁/决定权接力，后者的局部步骤/保密/目标定位有新的研究价值。氪金已有生产—实战—契约—家庭—关系完整样本，但规则豁免、奖励膨胀及秒杀重复削弱追加收益。建议只批准1—2本，是否继续由GPT-6与用户独立验收。

素材结论：CAND-N8-A/B/C均获得新支持并需要修订边界；没有批准通用稳定代价、无限收益或操控必然信任。新发现保持candidate/HOLD，只建议补既有母型证据与变体。三原创实验为独立新故事研究，不改路远/洛清霁项目的事实、章纲、永久能力或关系。

实际读取分层：新增90章是全文语义阅读；前20章事实复用已验收研究和章节索引。因用户特别要求，另外只针对时停15—16章预算相关源行再次检查，确认2018行4分40秒与2174行4分10秒，未发现相邻相关用时记录足以解释差额；没有重新拆这两章。原著全文件字节读取仅用于Git blob/UTF-8/尺寸/SHA256与章节切片，50以后没有语义研究或正文输出。素材库元数据和选定研究卡读取用于查重，不把那些作品加入本轮拆书。

原著片段仅在任务本地隔离读取区，不进入此分支；发布的是原创结构分析、索引、hash、验证脚本和回执。所有章节结论可沿书卡的固定提交行链接查原著，不使用简介/目录/书评推断内容。

`STAGE_2=THREE_BOOKS_TO_CHAPTER_50`

`EMOTION_FUSION=RESEARCH_CANDIDATE`

`MATERIAL_PROMOTION=HOLD / NOT_RUN`

`PRODUCTION=HOLD`

`FULL_BOOK_DECOMPOSITION=NOT_RUN`

`INDEPENDENT_REVIEW=PENDING`

`STOP_FOR_INDEPENDENT_REVIEW`
