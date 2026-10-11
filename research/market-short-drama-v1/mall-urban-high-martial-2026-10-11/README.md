# NOVA 都市高武商城找书与开篇研究

基准仓库：`xchhhh22222/novel-decomposition`；输入分支`research/short-drama-copyright-dual-benchmark-v1`；基准提交`14fda87479be5dcf2df3d50bc0ec502b7aa9f33c`。交付分支`codex/urban-high-martial-mall-benchmark-v1`。研究日期2026-10-11，时间戳同时保留UTC。依据仓库[研究V2规范](../../../skills/novel-creation-planner/references/market-ip-short-drama-v1.md)。未采用旧版权改编公告，未研究交易。

| 交付 | 内容与质量状态 |
| --- | --- |
| [商城候选池](mall-candidate-pool.jsonl)／[便读核实表](candidate-pool-and-readers.md) | 40部不同小说，实际商城完整书名、作者、详情链接、页次位置和观察证据 |
| [主站原著及在读核实](verified-originals-readers.jsonl) | 40部book_id、作者、都市高武身份确认；32部可见热度，8部UNKNOWN |
| [较热门10本](selected-high-read-10.md) | 从32部已核热度中按公开显示档位选10；商城别名按同ID核对；不声称全商城Top10 |
| [前10章逐章拆解](chapter-01-10-analysis.md) | 10本×10章全部实读，危机／选择／能力／力量／人物／钩子／改编条件；各行连实际公开章节 |
| [横向机制与节奏](cross-book-opening-lessons.md) | 首次效果和第二轮兑现、慢兑现反例、都市质感与视听条件 |
| [02–09素材融合与三案](golden-finger-02-09-bridge.md) | 127冻结文件哈希核验；3组实际召回，10个原记录/结构单元；三案均为候选 |
| [整书候选申请](full-book-research-requests.md) | 推荐5本，模块与待研究问题明确；全书研究未执行 |
| [证据和验证](evidence/) | 浏览器观察、主站搜索、100章来源与本地哈希、素材查询、交付验证；不含原著正文 |

## 采样与证据边界

浏览器保持书籍／都市高武1014。初始类别页第1页及第100页各采前15张共30部，再从当天主站都市高武阅读榜补10个高在读对照并实际回商城搜索、核卡和详情，共40部。主站定向补采有热度选择偏差，页面顺序不作排名；类别分页是分散采样，不是顺序扫完前100页。重复的《时停》搜索命中合并，没有算成第41部。

每部都在主站执行完整原著书名＋作者搜索。部分浏览器文本保留动态字体PUA原始字符，不盲目套阅读页字库。原著SSR页的正常书名、作者、book_id和分类与商城详情ID交叉核对；搜索命中不对应的8部不能借其他结果在读数。主站SSR低档0/1只作取证诊断，不宣称精确0/1人。未满1000保留上界区间，同档不强排。热门10还有主站阅读榜截图对照，榜单页面截止2026-10-10 24:00，搜索观察为10-11；短时变化与显示取整不抹平。

热度表示观察时在读，不是累计阅读、推荐量、改编热度或版权价值。8部未知仍可能有较高热度，故“已核实候选中的较热门10本”不等于40部绝对前十。没有通过低在读控制或因果实验，高热度作品的结构共性仅用于构思假设。

下载调用现有`fanqie-novel-downloader`的info、fetch_chapter与export_txt，限各书实际目录第1—10章；保持TLS校验，使用公开可读页面、顺序请求和原脚本退避重试，未访问登录／付费锁章。时停第6章、提取词条第3章各出现一次HTTP515，正常重试后成功；不是当前缺章。100章均无未解字体字符。完整度检查是长度、目录、锁定状态、字体和哈希检查，加上本次逐章实读；不保证与其他版本逐字相同。

原著文本仅存仓库外`.runs/mall-urban-high-martial-20261011/local-originals/`，本交付只含原创分析、书目、来源指针、元数据和哈希。没有取得原著再分发授权，因此不提交全文。浏览器证据只保留相关书目、热度和筛选信息；动态页面可日后变化。

## 状态

MALL_CATEGORY=VERIFIED_SCREENSHOT

ORIGINAL_IDENTITY=VERIFIED_40_OF_40

MAIN_SITE_READERS=VERIFIED_32_UNKNOWN_8

MALL_HIGH_READ_TEN=VERIFIED（限32部已核热度候选，不声称全商城排名）

CHAPTER_10_ANALYSIS=COMPLETE（100/100）

FROZEN_02_09_RETRIEVAL=VERIFIED_127_HASHES_ALL_8_MODULES

FULL_BOOK_DOWNLOAD=NOT_RUN_PENDING_APPROVAL

PRODUCTION_PROMOTION=NOT_RUN

INDEPENDENT_REVIEW=NOT_RUN_WAITING_GPT_6

STOP_FOR_INDEPENDENT_REVIEW
