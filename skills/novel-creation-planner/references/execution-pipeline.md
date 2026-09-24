# 市场执行流水线

本文件只定义扫榜、筛选、合法取样和交接。执行代理不得在这一阶段决定新书的金手指、人物关系或长线剧情。

## 1. 冻结参数

记录：平台、频道、题材、榜单类型、快照日期、Top10固定样本数、第一轮读取章数（1—10）、深拆样本数（3）、深拆目标章数（1—20）、输出目录、用户授权范围与已知限制。

建议把跨书市场样本也放在公共资产目录，而不是某本小说项目中。当前默认运行目录：

```text
<SHARED_ASSET_ROOT>/市场样本/<run_id>/
├─ raw_rankings/
├─ normalized/ranking.jsonl
├─ books/<sample_id>/chapters/
├─ samples.jsonl
├─ opening_cards.jsonl
├─ opening_signal_matrix.json
├─ benchmark_matrix.json
├─ deep_dive_selection.json
├─ deep_dive/<sample_id>/chapter_structure_1_20.jsonl
├─ structural_lessons.json
└─ manifest.json
```

运行产物属于临时证据，不进入素材库。任务结束后按用户要求保留或清理；不得擅自删除用户提供的文件。

## 2. 扫榜阶段门

番茄榜单固定调用 `$fanqie-ranking-scan`，直接读取番茄官网当前榜单版本、分类表和分类榜接口，不经过 `story-scan`、OpenWrite 或浏览器自动化：

```powershell
node "<fanqie-ranking-scan>/scripts/scan_fanqie_rank.mjs" --gender male --ranking new --category "都市高武" --top 100 --outdir "<run-dir>/raw_rankings/fanqie"
```

把该 Skill 生成的 `ranking.jsonl` 复制或登记为 `<run-dir>/normalized/ranking.jsonl`，并在总 `manifest.json` 中记录原始 `manifest.json` 的路径。至少记录：

- 平台、榜单、分类、快照日期与URL；
- 排名、书名、作者、公开热度指标、字数、标签、简介、平台 book_id；
- 采集成功、部分成功、失败或用户导入；
- 单日快照不得称为趋势。

进入筛选门的理想条件是至少20条有效候选。不足时可降级，但必须标注样本偏差。

`$fanqie-ranking-scan` 已直接生成 `ranking.jsonl`，执行代理不得二次猜测或补造缺失指标。每条至少包含：

```json
{
  "platform": "",
  "ranking_name": "",
  "category": "",
  "snapshot_at": "",
  "rank": 1,
  "title": "",
  "author": "",
  "platform_book_id": "",
  "book_url": "",
  "public_metrics": {},
  "word_count": null,
  "tags": [],
  "summary": "",
  "quality_status": "pass",
  "raw_source_path": "raw-ranking.json"
}
```

规范化不得把缺失指标补成零；无法解析时使用 `null` 并保留原始文件路径。

只有 `quality_status=pass` 的记录默认进入筛选；`suspect` 记录可保留用于人工复核。字体哈希变化、残留私有字或分类失败必须沿用扫描清单中的警告。单日快照与官网 `rank_change` 均不得表述成自行验证的历史趋势。其他平台若没有已验证的结构化采集器，应请求用户导入 CSV/JSON，而不是暗中回退到 `story-scan`。

## 3. 新书榜前10基线

用户要根据新书榜开书时，默认样本就是目标频道、目标分类、同一快照的新书榜前10名；不得为了迎合预设结论替换其中某本，也不得只挑看起来容易下载或符合个人偏好的书。逐本记录排名、书名、book_id、公开指标、正文可用性和入选状态。

同作者重复、正文不足3章、锁定或质量失败的样本仍保留在榜单证据中，但正文分析标为 `partial / metadata_only / failed`，不能用榜外书静默顶替。用户需要扩大视野时，可以在前10基线之外另加相邻题材、离群样本或中腰部对照，并明确标为 `supplemental`。

## 4. 合法取样

只允许：公开试读、用户提供文本或用户明确授权的来源。遇到付费墙、登录、验证码、robots、访问限制或权限不明，立刻改为 `metadata_only` 或剔除，不绕过限制。

番茄开篇样本（第1—10章）固定调用 `$fanqie-novel-downloader`。从 `ranking.jsonl` 读取 `platform_book_id` 或 `book_url`，每本书创建独立输出目录：

```powershell
python -X utf8 "<fanqie-novel-downloader>/fanqie_dl.py" info "<book_id|book_url>"
python -X utf8 "<fanqie-novel-downloader>/fanqie_dl.py" download "<book_id|book_url>" --start 1 --end 10 --format txt --out "<run-dir>/books/<sample_id>" --concurrency 2 --delay 1.0
```

先运行 `info` 核对书名、作者、章节总数和前几章标题；再下载公开可读的第1—10章。不得提高默认并发或缩短请求间隔。

第一轮 Top10 仍只取第1—10章。只有完成结构横评并选出3本深拆样本后，才把这3本扩展到第11—20章；按现有能力边界，超过第10章时优先改用 `$fanqie-desktop-operator` 或其它已验证、合法授权的读取路径。不得为了凑20章自动登录、绕过付费、复现私有接口或使用权限不明来源。

该下载器实际落盘为 `<run-dir>/books/<sample_id>/<书名>.txt`，一个文件包含元数据和所请求的连续章节，不会生成逐章文件。执行代理必须按实际文件登记，不得假定存在 `chapters/` 目录：记录合并 TXT 的绝对路径和 SHA-256，并从正文中核对请求范围内的章节标题、顺序和非空内容。不得跨书或跨来源拼接。

非番茄来源不调用 `$fanqie-novel-downloader`；只有用户明确把其他平台纳入样本时，才选择对应的已验证采集方式并单独记录接口差异。

## 5. 下载质量门

逐本检查：合并 TXT 是否存在、书名作者是否与榜单匹配、UTF-8、第1—10章标题与顺序、每章非空长度、占位页、乱码/私有字符、文件 SHA-256、跨书重复哈希和空章节数。过短、乱码、重复、缺章、锁定无正文或疑似占位的文本标为 `suspect`。

失败处理：

- 单榜失败：先核验 `$fanqie-ranking-scan` 的 `manifest.json` 与官网结构；需要改榜型或分类时保留失败快照并重新运行；
- Browser-CDP 不可用：尝试公开SSR数据或请用户导入CSV/JSON/截图；
- 下载失败：先以 `info` 核对 book_id、公开章节和页面结构；仍失败则把该书降级为 `metadata_only`，不得为了凑数切换到权限不清的第三方正文源；
- 合格正文样本少于6本：允许 `partial handoff`，但必须标注偏差，不能补造正文结论。

## 6. 交接格式

`samples.jsonl` 每条至少包含：

```json
{
  "sample_id": "S01",
  "title": "",
  "author": "",
  "platform_book_id": "",
  "platform_url": "",
  "content_source_url": "",
  "source_domain": "",
  "captured_at": "",
  "access_boundary": "public_preview",
  "ranking_refs": [],
  "selection_score": 0,
  "selection_evidence": [],
  "rights_status": "public_preview",
  "preview_scope": {
    "requested_chapters": 10,
    "actual_chapters": 10,
    "storage_mode": "combined_txt",
    "content_file": "books/S01/<书名>.txt",
    "chapter_titles": [],
    "chapter_files": []
  },
  "quality": {
    "status": "pass",
    "missing_chapters": [],
    "short_chapters": [],
    "hashes": {}
  },
  "handoff": "eligible"
}
```

`rights_status` 仅允许 `public_preview / user_authorized / unknown / blocked`；`access_boundary` 仅允许 `public_preview / user_authorized / metadata_only`；`handoff` 仅允许 `eligible / metadata_only / failed`。思考代理只接收结构化清单和最小必要章节，不接收执行代理的创作结论。

## 7. 正文分析交接门

下载完成不等于完成取样。执行代理必须逐本读取实际下载的第1—10章正文并生成 `opening_cards.jsonl`，每条至少记录：`sample_id / analyzed_chapters / first_scene / protagonist_problem / protagonist_first_choice / golden_finger_timing / chapter_emotions / visible_payoffs / relationship_entry / world_interface / chapter_4_10_loop / hooks / evidence_locations / quality_status`。

随后生成 `opening_signal_matrix.json`，把跨书结论分成高频共识、有效变体、离群信号、风险模式和暂不能判断；每条结论必须引用 sample_id 与章节范围。没有这两个分析产物，不得宣称完成了市场开篇横评；仍可依据已核验的素材库提出明确标为“市场未验证”的候选，不能根据书名、简介或榜单排名捏造正文结论。

至少6本具有完整第1—10章正文和 `quality_status=pass`，才能将市场开篇横评标为充分；不足时标 `partial`，不给出冒充前十本正文研究的结论，但素材库驱动的初步剧情候选不因此停工。


## 8. V1.2 深拆交接

第一轮 Top10 前10章完成后，结构选择与第二轮取样必须遵守 `market-benchmark.md`。

执行代理只负责保留 Top10、获取合法正文、核验章数与文件质量，以及根据思考代理给出的3个 sample_id 扩展第11—20章。

“哪3本最值得学”由思考层依据结构矩阵决定，执行层不得按简介或个人喜好预选。

第11—20章获取失败时，必须保留原 sample_id 并把 `deep_dive_status` 标为 partial/failed；不得静默换成第4本掩盖失败，除非用户明确允许重新选样本。
