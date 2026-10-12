# 实际素材检索与原创适配

## 检索前冻结（2026-10-12）

本轮是已验收研究的限定创作试验，非从零开书的完整Planner流程。先建立以下需求，再检索、读原记录，最后生成情节与正文；不重新扫榜，不扩原著，不生成正式plan。用户已明确授权三篇研究正文和隔离文件落盘，优先于Skill默认只交候选的范围。

- A读者承诺：必死猎物取得局部控制权，活命后能主动追逼猎人。因果窗口：被追杀→挡住肉身但仍被远击伤→利用地形活着脱离→敌人清除见证/证据→把追杀转为伏击。
- B读者承诺：被夺走的利益真回到手中，并能脱离掠夺者的供应控制。窗口：矿产被吞→阻止装运→取回实物/拿到钱→对方切断销路与加工→联合受损者实际交付。
- C读者承诺：强者不能带走我的亲人，但我的保护也会伤害她的选择。窗口：拦截带人→亲人被救且计划被毁→她另找盟友→主角放弃控制并提供有限战术合作→她亲自完成目标。

槽位：07首危机/可见兑现；09敌人反制/局部能力换用途；05具体利益与独立行动；03势力控制资源及高武环境；04成长/远击能力的真实差距；02有边界能力兼容；06首胜后的目标接力；08第二兑现的状态改变。每槽小批召回，下钻选中组件；不足单列GAP，不捏造素材ID。

共享库候选入口：本地 `nova-material-library-shared-dna/packages/shared-dna-library/v1.0.0`，以manifest及检索器实际完整性门为准。未配置本轮RMF root，三种发动机来自用户要求及已验收研究，不另启动机制库扩展。情绪设计为 ORIGINAL_DESIGN + 已验收研究参考，EMOTION_LIBRARY_ACTIVE=NO；不把EL/EW/MA/AH研究HOLD资产当生产可用素材。

## 冻结包身份及真实命令

实际入口绝对路径：`/home/wxc/1dushigaowu/nova-material-library-shared-dna/packages/shared-dna-library/v1.0.0`。本地共享库HEAD：`ed9227c403d5c85c2f594e3291af2c9eff2441e9`。manifest声明源仓库 `xchhhh22222/nova-material-library`、源分支 `nova-v1.7.0-research-artifacts`、源HEAD `7b7694592c0a6aa6edcedb45fc7d4d174629b34c`。这是包的来源身份，不能与本地HEAD混为一谈。

manifest SHA-256：`0a8d7c64145d7e54c87a81db7449cb03f89a2a87e8e7395d10af1592dd2ea76e`。127项声明文件由现有检索器执行完整性门；八模块成功检索均返回 `library_mode=VERSIONED_PACKAGE / library_status=ACTIVE_SHARED_LIBRARY / package_version=1.0.0`。包内记录仍是 `candidate`，来源QA不等于本次小说质量许可。

执行模板（使用现有脚本，未新增验证程序）：

```bash
python3 skills/novel-creation-planner/scripts/search_dna_candidates.py \
  --library /home/wxc/1dushigaowu/nova-material-library-shared-dna/packages/shared-dna-library/v1.0.0 \
  --query '<下表查询>' --modules '<下表模块>' \
  --include-per-book --max-per-book 2 --limit 4 --format json
```

03另带 `--components faction`，04另带 `--components system`。每次四条、八次有效查询，共32条召回（含同父组件），不是32条精读。原始JSON暂存在本机 `/tmp/nova-retrieval-02.json` 等，不增加提交文件；下表保存可复查的实际召回ID。

| 模块 / 查询 | 实际召回ID（按返回顺序） |
|---|---|
| 07 `opening` / 危机 反转 能力 | `OP:BOOK:BOOK_009`；`OP:BOOK_008`；`OP:BOOK:BOOK_005`；`OP:BOOK:BOOK_001` |
| 09 `plot_mechanism` / 反制 资源 合作 | `PM:BOOK:BOOK_012`；`PM:BOOK_017:001`；`PM:BOOK:BOOK_002`；`PM:BOOK:BOOK_004` |
| 05 `character_function` / 利益 独立 目标 | `HEROINE:BOOK_008:时雨晴`；`DA:RELATIONSHIP:BOOK_017:001`；`HC:BOOK_002:沈清雪`；`HEROINE:BOOK_007:阿加莎` |
| 03 `worldbuilding` / 资源 垄断 家族 | `WB:BOOK:BOOK_001/F5`；同父`F1`；`WB:BOOK:BOOK_002/WB:F5`；`WB:BOOK:BOOK_004/WB:004:F2` |
| 04 `cultivation_system` / 气血 远程 消耗 | `CS:BOOK:BOOK_002/CS:S1`；`CS:BOOK:BOOK_005/CS:SYSTEM:BOOK005:AWAKENED_COMBAT`；`CS:BOOK:BOOK_007/CS:SYSTEM:BOOK007:BLOODLINE`；`CS:BOOK:BOOK_016/CS:SYSTEM:001` |
| 02 `golden_finger` / 限制 战斗 边界 | `GF:BOOK_007`；`GF:BOOK_009`；`GF:BOOK_010`；`GF:BOOK_002` |
| 06 `plotline` / 复仇 资源 生存 | `PL:BOOK:BOOK_013`；`PL:BOOK:BOOK_016`；`PL:BOOK:BOOK_004`；`PL:BOOK:BOOK_007` |
| 08 `arc_structure` / 反转 争夺 代价 | `AR:BOOK:BOOK_003`；`AR:BOOK:BOOK_009`；`AR:BOOK:BOOK_017`；`AR:BOOK:BOOK_007` |

06先以 `--modules 主线与支线` 查询返回0；核对别名后改为 `plotline` 返回4，记为已修复的 RETRIEVAL_GAP，不判断库中缺素材。其余未精读候选只列召回，不给予语义QA结论。

## 精读与取舍：来源事实不倒灌到原创

下表路径均相对上述冻结包根；所有列出的来源记录QA均为PASS。括号内为 `component_path` 与实际内部ID。先读JSONL行并定位组件，长父记录输出截断后，再单独完整读取所选嵌套组件；不以截断父输出声称全文精读整本书。source-map的原仓库路径另列在后表。

| 来源记录 / 路径及行 / 覆盖 | 来源事实、可抽象部分 | 本轮使用或拒绝 |
|---|---|---|
| `OP:BOOK_008`；`DNA素材/07_开篇/per_book/BOOK_008.jsonl:1`；1–20（只用7–10） | `selling_point_proof[0] / OP:PROOF:001`、`first_payoff[1] / OP:PAYOFF:002`、`continuation_drivers[2] / OP:DRIVER:003`：被保护者脱离带走结果，但独立战力与共同路线变成新问题；证据CH0007/0008/0010 | C借“救下不等于替她定未来”；A/B借当次结果必须改变下一目标。拒绝预知动画、人气系统、青梅觉醒和原组织事件链 |
| `OP:BOOK:BOOK_009`；`DNA素材/07_开篇/per_book/BOOK_009.jsonl:1`；1–20 | `opening_compression[0] / OP:BOOK_009:COMPRESSION`：多次评级/准备后第10章验证 | **拒绝该节奏**：首轮延期到第10章不适合这次试写；不把首位搜索排名当适配结论 |
| `PM:BOOK:BOOK_012`；`DNA素材/09_剧情机制/per_book/BOOK_012.jsonl:1`；父覆盖1–1358，所用组件依据120/224/230/235 | `mechanisms[7] / PM:MECHANISM:008`：反制须可信、置换物须存在、对方毁灭性目标会使定价失效；读全组件含failure_modes/constraints/outputs | B仅借“暴力不能低成本解决时，现实筹码改变对方行为”。改成有买主、有货、有短供损失的现场；罗承没有因此成为同盟，**不声称完整复用了长期挂账母型**。同记录`mechanisms[0]/[1]`的赌命强制规则/文字漏洞拒绝，不造系统担保 |
| `HEROINE:BOOK_008:时雨晴`；`DNA素材/05_人物功能与标签/derived/heroine/BOOK_008.jsonl:1`；1–86 | `independent_goal`、`key_choices[1] / HC008-C2`：被保护者选择自己反击；证据7–8；完整派生记录已读 | C姐姐原本就有战力与追凶目标；不能“救一次就自动忠诚”。A姚禾转移证据、B梁迟护炉，也需独立利益。不借突然觉醒获得第二外挂 |
| `DA:RELATIONSHIP:BOOK_017:001`；`DNA素材/05_人物功能与标签/derived/relationship_engine_assets.jsonl:13`；证据298/300/910 | `active_choices`、`conflicting_interest`：同盟可保独立信息，有必须各自完成的子目标；完整派生记录已读 | 只借“关系靠实际履约/子目标，不靠情绪表态”。拒绝骗子双簧、神座债、隐秘信息万能解题；C姐姐的路线权不等于共享全部秘密 |
| `WB:BOOK:BOOK_001`；`DNA素材/03_世界观/per_book/BOOK_001.jsonl:1`；所读F5证据109–124 | `factions[4] / F5`：家族控制任务、档案、高阶武者、权限；`actual_interest`过于宽泛 | **不采用具体势力**。卡不能直接支撑盛仓行的炉芯/收购垄断，标INTERFACE_GAP；B供应控制及A私矿/C边军利益均为原创，不宣称由这张卡证明 |
| `CS:BOOK:BOOK_002`；`DNA素材/04_修炼体系/per_book/BOOK_002.jsonl:1`；所选体系证据1/26/32/79/93/126 | `cultivation_systems[0] / CS:S1`：训练/资源→战力→更高门槛；兑换不能包全部技巧；完整体系组件已读 | 三案只借训练资源与技巧分离。拒绝充值修为、一拳跨阶、直播打赏。新候选一阶锻骨/二阶行气/三阶放罡与远击阈值是原创，不冒充来源境界与映射 |
| `GF:BOOK_007`；`DNA素材/02_金手指/per_book/BOOK_007.jsonl:1`；1–124 | 精读`hard_limits / costs / failure_modes / world_dependencies / unknowns`：地图/追击/信息仍约束，重构上限未知 | 仅用作兼容反例：**拒绝血液吸收、不死重构、血奴追踪**。本轮02能力来源是第三阶段F+用户固定句，不从这张卡偷带恢复/定位能力 |
| `PL:BOOK:BOOK_007`；`DNA素材/06_主线与支线/per_book/BOOK_007.jsonl:1`；父1–124，只用1–10 | `plotlines[0] / PL:LINE:BOOK007:01`：局部逃亡结果→新线索→主动追查；组件全读；证据1/3/6/10。部分细字段只回指第1章，精细强度有限 | A采用目标接力的抽象。敌人、目的、能力、地形、筹码、同伴行动全部重设；B/C也须给出首胜后的具体目标，不沿用卷轴/血族身份逃亡 |
| `AR:BOOK:BOOK_007`；`DNA素材/08_篇章结构/per_book/BOOK_007.jsonl:1`；父1–124，只用1–10 | `arcs[0] / AR:ARC:BOOK007:01`：猎物/猎手关系改变后打开主动追查入口；组件全读，证据1/6/10；细字段证据较粗 | A采用阶段“撤退→主动行动”的功能；B第二弧改供给控制，C改决策权。拒绝沿用原反杀→卷轴整链。第二强兑现仍为拟议，不能用来源卡替它授质量PASS |

### 原仓库路径映射

包内行和source-map原行分别保留，尤其05关系派生合并后行号不同。

| 来源ID | `nova-material-library` 源路径及行 |
|---|---|
| `GF:BOOK_007` | `books/BOOK_007/02_金手指/per_book/BOOK_007.jsonl:1` |
| `WB:BOOK:BOOK_001` | `books/BOOK_001/03_世界观/per_book/BOOK_001.jsonl:1` |
| `CS:BOOK:BOOK_002` | `books/BOOK_002/04_修炼体系/per_book/BOOK_002.jsonl:1` |
| `HEROINE:BOOK_008:时雨晴` | `books/BOOK_008/05_人物功能/derived/heroine/BOOK_008.jsonl:1` |
| `DA:RELATIONSHIP:BOOK_017:001` | `books/BOOK_017/05_人物功能与标签/derived/relationship_engine_assets.jsonl:1`（包内13） |
| `PL:BOOK:BOOK_007` | `books/BOOK_007/06_剧情线/per_book/BOOK_007.jsonl:1` |
| `OP:BOOK_008` | `books/BOOK_008/07_开篇/per_book/BOOK_008.jsonl:1` |
| `AR:BOOK:BOOK_007` | `books/BOOK_007/08_篇章结构/per_book/BOOK_007.jsonl:1` |
| `PM:BOOK:BOOK_012` | `books/BOOK_012/09_剧情机制/per_book/BOOK_012.jsonl:1` |

## 已验收研究的复用及融合落点

基准已包含第一阶段 `95ccb616fd7c157c2376b938fb6f8f3ef7fdd0c5`、第二阶段 `0f250ea375c61aaa7e9693924a89657a37618a3e`、第三阶段 `c809816aecffb0c9cf76b9516fe17bab794ed208`。不重新阅读原著，不扩101章以后；正式卡覆盖到后期只是卡片元数据与既有抽象，不是本轮新增拆书。

- F出处：`research/nova-body-stage3-openings-2026-10-12/high-burst-opening-experiments.md` → 新案F；保留原一句话能力及可绕端/远击边界，放弃救援岗位/考核骨架。
- 因果接力：`research/nova-three-stage2-2026-10-12/cross-book-emotion-fusion.md` → 因果接力R组（时停27/35、氪金29/32–35、拼身体30/43–49）。A活命保铜片触发清除见证；B取回货与失单触发封炉；C保护导致潜入失败与另组联盟。这些新事件不是原作事实。
- 多线交织：同文件W组，尤其W3自主证言改变他人调查行动；A姚禾决定不逃使许砚回头，B老杜验箱得罪管事使买主可下单，C沈棠独立情报与温芸撤人要求共同决定开线时点。
- 情绪对冲：同文件E组，尤其E3一个主体的快意成为另一个主体的未知负担。C弟弟人留住/姐姐机会丢；B陈川能开炉/同盟矿工受伤失收入，先付成本改变合作能否继续；A许砚要铜片/矿卫先撤人，让他放弃抢私矿时机。
- 第三阶段 `emotion-arc-contracts.md` 的EC2/EC4：当次救人不能抵销未来决定权，局部战胜不能自动支付全链问责。C第9章抓当前凶手、第10章公开下一站，但不把整网清剿或关系全部修复判完成。
- `obligations-and-findings.md`、`usage-lineage-1-100.md`：采用“新增产物不伪装旧能力新用”“局部结果与未付义务分账”。三案不加睡眠豁免、锁精神值、吞噬强化或精准预知。

未新增EL/EW/MA/AH查询或伪造其ID；本轮情绪依据上述已验收文本接口与原创动作，不自称完成新的情绪库召回。既有情绪研究资产HOLD保持不变。

## 来源、接口与当前组合：三个判断分开

来源：检索gate及所选行定位可核验；不等于原作全章语义重审。接口：07结果接关系行动、05独立子目标、06/08状态接力为可理解抽象；04现金接口与F不兼容、03具体垄断资料不足；02血液机制直接拒绝。

| 来源输出→本轮所需输入 | 当前判定与原创桥（均非原书规则） |
|---|---|
| 07救下/05独立行动→C既要救人又要选择权 | ADAPTABLE：姐姐已有追凶计划，救下毁计划；代价是机会/信任，改变她的合作人；因而第二轮必须由她再提出借线请求 |
| 06局部脱困/08猎手逆转→A反猎资格 | ADAPTABLE：铜片与活见证保留，敌人主动清除证据；主角付腿伤/丢工具，同伴提供位置及同阶战力；无F的杀伤升级 |
| 09可信反制与可置换利益→B被夺货变议价权 | ADAPTABLE（局部）：阻装运、箱印、时限及现场买主组成现实筹码；代价是暴露能力与后续封炉，输出是本批钱/货归属变化；不靠神规则强制履约 |
| 04训练/资源→F守线者成长 | ADAPTABLE：普通矿产售款用于治疗与淬骨、真训练提升移动避击；F不兑换现金为实力、不自涨线长。新三阶放罡可远击，仍威胁主角 |
| 03泛控制权限→B具体炉芯/收购控制 | HOLD为来源接口；原创实现明确是私商连锁供给和排他预购。保留INTERFACE_GAP，不谎报直接适配 |
| 02血液重构/追踪→F划线 | HARD_CONFLICT，拒绝接入；F没有回血、敌意识别或远程定位 |

各案普通资源与阶段目标分开：A治疗/锻骨耗矿款，阶段目标是活见证及追杀者；B现金/炉芯支撑生产，阶段目标是可独立交付的首炉；C补给/疗伤维持武力，阶段目标是姐姐本人完成追凶，不拿关系权限当修炼输入。

同源风险：02/06/08的兼容反例和结构记录集中BOOK_007，但其具体世界、能力、成长体系与高潮包装全部拒绝；不组装来源书“身份逃亡→反杀→卷轴”连续内容。07/05集中BOOK_008，C若又改青梅、突然觉醒、官方招募即会拉近原型，本轮保持成年姐弟、既有枪技、主动诱饵、计划被破坏四项差异。人物、世界利益、能力、任务、奖励/后果与场景均重设；原创距离仍交作者判断。

精确缺口：`INTERFACE_GAP`＝03现卡不足以证明商业供给细节，未声称来源库不存在；`ADAPTATION_REQUIRED`＝04训练门与F、09局部议价都需上述原创桥；`CREATIVE_OPEN_CHOICE`＝F三米/两米/三米高限制、觉醒来源、第二轮强度及C姐姐愿冒死是否讨喜，待作者。完整武道终局与十章后的细纲本轮不提供，不冒充已经设计。

停止原因：八模块已真实检索，关键抽象来源可定位，缺口已有明示原创实现或HOLD；继续同义召回不解决正文质量。没有生成正式plan或emotion_draft，未运行该类计划validator，也不声称完整Planner机器包验收；本轮只做用户要求的八份研究文件及正文/来源/范围验证。
