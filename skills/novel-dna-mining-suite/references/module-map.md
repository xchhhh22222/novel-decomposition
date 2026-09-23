# 小说 DNA 拆解套件模块映射

| 模块 | 包内入口 | 主要 schema/QA | validator |
| --- | --- | --- | --- |
| 总控与总索引 | `references/core/` | `horizontal-specialist-contract.md`、`integration-and-qa.md`、`library-layout.md` | `scripts/core/validate_chapter_emotions.py`、`build_master_index.py` |
| 章节情绪 | `references/specialists/chapter-emotion-miner/` | `references/core/chapter-emotion-schema.md` + specialist adapter | `scripts/specialists/chapter-emotion-miner/validate_outputs.py` |
| 金手指 | `references/specialists/golden-finger-miner/` | `golden-finger-schema.md`、`clustering-and-qa.md` | `scripts/specialists/golden-finger-miner/validate_outputs.py` |
| 世界观 | `references/specialists/worldbuilding-miner/` | `schema.md`、`clustering-and-qa.md` | 同名 specialist validator |
| 修炼体系 | `references/specialists/cultivation-system-miner/` | `schema.md`、`clustering-and-qa.md` | 同名 specialist validator |
| 人物功能 | `references/specialists/character-function-miner/` | `schema.md`、`clustering-and-qa.md` | 同名 specialist validator |
| 主线与支线 | `references/specialists/plotline-miner/` | `schema.md`、`clustering-and-qa.md` | 同名 specialist validator |
| 开篇 | `references/specialists/opening-miner/` | `schema.md`、`clustering-and-qa.md` | 同名 specialist validator |
| 篇章结构 | `references/specialists/arc-structure-miner/` | `schema.md`、`clustering-and-qa.md` | 同名 specialist validator |
| 剧情机制 | `references/specialists/plot-mechanism-miner/` | `schema.md`、`clustering-and-qa.md` | 同名 specialist validator |

所有路径均相对于 `novel-dna-mining-suite/`，迁移包不依赖当前项目的其它 Skill 或固定绝对路径。
