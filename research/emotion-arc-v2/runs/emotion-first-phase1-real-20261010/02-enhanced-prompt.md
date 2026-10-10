# Independent E2_E3_ENABLED creative pass (RESEARCH ONLY)

Same frozen sparse brief for both passes (SHA-256 canonical JSON: 400ff445aa7ae0b6336a78c022dcd395aff2daeb399ebcb8225474ea86fe3116).

{
  "schema_version": "sparse_emotion_brief_v1",
  "brief_id": "SEB:TRUST_AND_PROTECTION:V1",
  "input_mode": "SPARSE_EMOTION_BRIEF",
  "status": "candidate",
  "genre": [
    "玄幻",
    "高武"
  ],
  "core_reader_expectation": "主角在被亲近之人误解后，通过有代价的行动重建信任，让家人从互相防备转向共同抵御真正的危险",
  "emotion_contour": [
    "DOWN",
    "DOWN",
    "UP"
  ],
  "required_emotion_weaves": [
    "家庭保护的承诺必须形成可见的安全变化",
    "能力成长必须承担可以影响后续选择的代价",
    "家人与主角的关系要能主动改变行动方案",
    "长期势力压力必须由当期决定产生而非空降新敌"
  ],
  "longform_requirement": "本阶段兑现家人的安全与关系变化之前，下一大情绪弧可以留下可信触发，但不可取消原有承诺；先规划50章及后续延续条件",
  "forbidden_prefill": "尚未选择人物姓名、具体敌人、金手指、势力结构、具体故事节点或下一弧主题"
}

You are the SEMANTIC COMPOSER, not the source validator. Produce a standalone JSON
fragment with exactly: schema_version='emotion_story_composer_fragment_v1',
brief_id, mode='E2_E3_ENABLED', status='candidate', semantic_composer={'kind':
'MODEL_AUTHORED_RESEARCH_CANDIDATE','model_family':<truthful model name>,
'literary_approval':'NOT_GRANTED'}, material_profiles, options (at least two).

Each option must meet the EXISTING emotion-story-bridge contract: ≥7 causal nodes,
nine-stage Story Spine, concrete 1–50 chapter phases, 02–09 functional slots, node-local
material effects, independent relationships and realistic costs. Both options must
have substantively different causal engines, not mere names. Use existing bridge
fixtures ONLY as schema examples; never transplant their story premises.

Work with existing 02–09 search tools from material-dispatch.md. Source IDs you
select/reject must really occur in the search results; do not invent. Missing or
incompatible sources become explicit ORIGINAL_DESIGN gaps. Every material has
an actionable role at specified story nodes. Keep candidates HOLD, no prose.

You must create the JSON artifact yourself in the research workspace. The user
must not hand-author a long semantic-composition file.

Every enhanced macro PAID requires `required_settlement_conditions` entries {condition_id, description, witness_node_id}; each witness must occur no later than its PAID transition. Do not use rescue success as proof of later administrative settlement.

## Evidence inventory (candidate/HOLD only; NOT approved templates)
{
  "schema_version": "emotion_arc_library_retrieval_v1",
  "status": "candidate",
  "qa_status": "HOLD",
  "production_promotion": "NOT_RUN",
  "brief_id": "SEB:TRUST_AND_PROTECTION:V1",
  "library": {
    "package_name": "book001-derived",
    "source_book_id": "BOOK_001",
    "source_commit_sha": "1e10e6e3ffb70eda94a400073155fd89db724ce9",
    "package_status": "candidate",
    "semantic_review": "PENDING_INDEPENDENT_REVIEW"
  },
  "query_dimensions": [
    {
      "dimension_id": "FAMILY_PROTECTION",
      "source_requirement": "家庭保护的承诺必须形成可见的安全变化",
      "derived_search_terms": [
        "家庭",
        "家人",
        "保护",
        "安全",
        "照护",
        "资源"
      ],
      "derivation_status": "PLANNER_WORKING_HYPOTHESIS_NOT_USER_STORY_FACT"
    },
    {
      "dimension_id": "GROWTH_COST",
      "source_requirement": "能力成长必须承担可以影响后续选择的代价",
      "derived_search_terms": [
        "成长",
        "力量",
        "能力",
        "代价",
        "限制",
        "资源",
        "验证"
      ],
      "derivation_status": "PLANNER_WORKING_HYPOTHESIS_NOT_USER_STORY_FACT"
    },
    {
      "dimension_id": "RELATIONSHIP_AGENCY",
      "source_requirement": "家人与主角的关系要能主动改变行动方案",
      "derived_search_terms": [
        "关系",
        "伙伴",
        "家人",
        "选择",
        "互助",
        "共同",
        "边界"
      ],
      "derivation_status": "PLANNER_WORKING_HYPOTHESIS_NOT_USER_STORY_FACT"
    },
    {
      "dimension_id": "LONG_TERM_FACTION_PRESSURE",
      "source_requirement": "长期势力压力必须由当期决定产生而非空降新敌",
      "derived_search_terms": [
        "势力",
        "制度",
        "压力",
        "权限",
        "责任",
        "公开",
        "位置"
      ],
      "derivation_status": "PLANNER_WORKING_HYPOTHESIS_NOT_USER_STORY_FACT"
    }
  ],
  "line_matches": [
    {
      "record_id": "EL:BOOK_001:001",
      "record_role": "SINGLE_EMOTION_LINE",
      "similarity_score": 12,
      "similarity_reason": "matched source mechanisms/expectations: 家庭, 家人, 保护, 安全, 照护, 资源; matched source mechanisms/expectations: 能力, 资源; matched source mechanisms/expectations: 家人, 选择",
      "reader_expectation": "江云能把新获得的武者能力转化为叔叔治疗、妹妹生活和家庭安全的实际改善",
      "transferable_parts": {
        "causal_generator": "家庭医疗与生计缺口持续把修炼、接单和人情资源转成必须作出的选择",
        "payoff_mechanism": "叔叔治疗、妹妹生活或家庭安全出现可见且可持续的阶段改善",
        "lifecycle_shape": "PARTIALLY_PAID"
      },
      "limits": [
        "candidate/HOLD research record; not a production-approved template",
        "semantic similarity and transferability require independent review",
        "Long-term safety after martial society becomes public remains open.",
        "武道公开后家人的长期安全",
        "父亲旧敌对家庭的后续风险"
      ],
      "provenance": {
        "source_book_id": "BOOK_001",
        "source_commit_sha": "1e10e6e3ffb70eda94a400073155fd89db724ce9",
        "record_file": "emotion-lines.jsonl",
        "record_line": 1,
        "record_line_sha256": "69c2837044dfb66ba7a454115961a40b4ae9cb433811cbdf6000911a5fc9f294",
        "source_publication_status": "RESEARCH_NOT_ACTIVE",
        "source_text_audit": "REVIEWED_R3"
      },
      "matched_dimensions": [
        "FAMILY_PROTECTION",
        "GROWTH_COST",
        "RELATIONSHIP_AGENCY"
      ]
    },
    {
      "record_id": "EL:BOOK_001:002",
      "record_role": "SINGLE_EMOTION_LINE",
      "similarity_score": 12,
      "similarity_reason": "matched source mechanisms/expectations: 资源; matched source mechanisms/expectations: 成长, 力量, 能力, 代价, 资源, 验证; matched source mechanisms/expectations: 选择, 边界; matched source mechanisms/expectations: 制度, 公开",
      "reader_expectation": "江云能否把功法、点数和实战反馈稳定转化为经得起任务验证的力量",
      "transferable_parts": {
        "causal_generator": "资源稀缺和任务危险迫使江云在消耗点数、改造功法与实战验证之间持续选择",
        "payoff_mechanism": "新能力通过陌生任务、对手反应或明确境界变化得到验证，同时保留代价与上限",
        "lifecycle_shape": "PARTIALLY_PAID"
      },
      "limits": [
        "candidate/HOLD research record; not a production-approved template",
        "semantic similarity and transferability require independent review",
        "The long-term limit and ethical cost of the point-growth loop remain unresolved.",
        "点数循环的长期边界",
        "异常底蕴公开后的制度后果"
      ],
      "provenance": {
        "source_book_id": "BOOK_001",
        "source_commit_sha": "1e10e6e3ffb70eda94a400073155fd89db724ce9",
        "record_file": "emotion-lines.jsonl",
        "record_line": 2,
        "record_line_sha256": "9a4a567a978aff2cf54af97e8a48c8129c729060a1ed130776ab552d939d544a",
        "source_publication_status": "RESEARCH_NOT_ACTIVE",
        "source_text_audit": "REVIEWED_R3"
      },
      "matched_dimensions": [
        "FAMILY_PROTECTION",
        "GROWTH_COST",
        "RELATIONSHIP_AGENCY",
        "LONG_TERM_FACTION_PRESSURE"
      ]
    },
    {
      "record_id": "EL:BOOK_001:005",
      "record_role": "SINGLE_EMOTION_LINE",
      "similarity_score": 12,
      "similarity_reason": "matched source mechanisms/expectations: 家庭, 资源; matched source mechanisms/expectations: 代价, 资源, 验证; matched source mechanisms/expectations: 关系, 伙伴, 选择, 互助, 共同, 边界",
      "reader_expectation": "陆滔与江云的临时合作能否变成可靠但保有利益边界的伙伴与资源通道",
      "transferable_parts": {
        "causal_generator": "任务交接、药物渠道、共同行动与私人仇怨让双方必须在互利、风险和边界间反复选择",
        "payoff_mechanism": "陆滔在共同风险或资源选择中作出可见投入，江云也明确互助边界与代价",
        "lifecycle_shape": "PARTIALLY_PAID"
      },
      "limits": [
        "candidate/HOLD research record; not a production-approved template",
        "semantic similarity and transferability require independent review",
        "Long-term partnership after the strength gap remains outside this window.",
        "陆滔的完整长期意图",
        "双方资源人情如何结算"
      ],
      "provenance": {
        "source_book_id": "BOOK_001",
        "source_commit_sha": "1e10e6e3ffb70eda94a400073155fd89db724ce9",
        "record_file": "emotion-lines.jsonl",
        "record_line": 5,
        "record_line_sha256": "41b47006600b4dbb5e59bb0b5080a93f38b4c89b7b0260afd576ab5a66739f35",
        "source_publication_status": "RESEARCH_NOT_ACTIVE",
        "source_text_audit": "REVIEWED_R3"
      },
      "matched_dimensions": [
        "FAMILY_PROTECTION",
        "GROWTH_COST",
        "RELATIONSHIP_AGENCY"
      ]
    },
    {
      "record_id": "EL:BOOK_001:003",
      "record_role": "SINGLE_EMOTION_LINE",
      "similarity_score": 10,
      "similarity_reason": "matched source mechanisms/expectations: 选择, 边界; matched source mechanisms/expectations: 制度, 权限, 责任, 公开, 位置",
      "reader_expectation": "江云能否在不失去自主边界的前提下取得合法武者身份、任务权限与公共认可",
      "transferable_parts": {
        "causal_generator": "登记规则、临时任务、官方行动和舆论问责不断迫使江云选择进入制度多深",
        "payoff_mechanism": "江云获得可识别的合法权限与公共信用，并为其选择承担制度后果",
        "lifecycle_shape": "PARTIALLY_PAID"
      },
      "limits": [
        "candidate/HOLD research record; not a production-approved template",
        "semantic similarity and transferability require independent review",
        "Public-era governance and the protagonist's durable formal role remain unresolved.",
        "公开时代江云的正式权限与责任",
        "个人自主和国家任务的长期边界"
      ],
      "provenance": {
        "source_book_id": "BOOK_001",
        "source_commit_sha": "1e10e6e3ffb70eda94a400073155fd89db724ce9",
        "record_file": "emotion-lines.jsonl",
        "record_line": 3,
        "record_line_sha256": "b2cca1c84f9789d9018ac063588d6019c7b0b7f2e4d5bc0bda3f41152d5628b2",
        "source_publication_status": "RESEARCH_NOT_ACTIVE",
        "source_text_audit": "REVIEWED_R3"
      },
      "matched_dimensions": [
        "RELATIONSHIP_AGENCY",
        "LONG_TERM_FACTION_PRESSURE"
      ]
    },
    {
      "record_id": "EL:BOOK_001:006",
      "record_role": "SINGLE_EMOTION_LINE",
      "similarity_score": 6,
      "similarity_reason": "matched source mechanisms/expectations: 家庭; matched source mechanisms/expectations: 制度, 权限, 位置",
      "reader_expectation": "父亲遗产、青云山与灵气潮汐之间被隐藏的关系将如何改变江云对家庭和自身位置的理解",
      "transferable_parts": {
        "causal_generator": "真元探查揭示叔叔身份后，家庭口述、权限失败、父母遗信与国家档案持续迫使江云追查父辈真相",
        "payoff_mechanism": "父亲遗产、国家档案和潮汐关系得到可核验信息，并迫使江云作出改变家庭或制度位置的选择",
        "lifecycle_shape": "PARTIALLY_PAID"
      },
      "limits": [
        "candidate/HOLD research record; not a production-approved template",
        "semantic similarity and transferability require independent review",
        "The father's final fate, complete enemy chain, and tide mechanism remain unresolved.",
        "江山是否真正死亡",
        "删除档案与多方仇家的完整链条",
        "灵气潮汐的真实机制"
      ],
      "provenance": {
        "source_book_id": "BOOK_001",
        "source_commit_sha": "1e10e6e3ffb70eda94a400073155fd89db724ce9",
        "record_file": "emotion-lines.jsonl",
        "record_line": 6,
        "record_line_sha256": "ff5265abbb0cd94bbcd92754efb9db97532a9f2780797632c38b60ad2156b42e",
        "source_publication_status": "RESEARCH_NOT_ACTIVE",
        "source_text_audit": "REVIEWED_R3"
      },
      "matched_dimensions": [
        "FAMILY_PROTECTION",
        "LONG_TERM_FACTION_PRESSURE"
      ]
    },
    {
      "record_id": "EL:BOOK_001:004",
      "record_role": "SINGLE_EMOTION_LINE",
      "similarity_score": 4,
      "similarity_reason": "matched source mechanisms/expectations: 力量, 代价; matched source mechanisms/expectations: 制度, 压力",
      "reader_expectation": "江云在力量、收益与生死压力面前能否维持可辨认的处置边界",
      "transferable_parts": {
        "causal_generator": "悬赏目标、点数来源、战场救援和私人冲突不断给出更省事但代价更高的替代路径",
        "payoff_mechanism": "在能获利或更快解决问题时，江云仍作出有代价的边界选择并产生他人或制度可见的后果",
        "lifecycle_shape": "ACTIVE"
      },
      "limits": [
        "candidate/HOLD research record; not a production-approved template",
        "semantic similarity and transferability require independent review",
        "The long-term boundary between punishment, point reward, and public force remains open.",
        "恶狱点来源会否反过来侵蚀处置边界"
      ],
      "provenance": {
        "source_book_id": "BOOK_001",
        "source_commit_sha": "1e10e6e3ffb70eda94a400073155fd89db724ce9",
        "record_file": "emotion-lines.jsonl",
        "record_line": 4,
        "record_line_sha256": "91b3990f5b337a91e2b169c9ed2bd946de991cdc1ccfbd0b8848e91646fe3c6e",
        "source_publication_status": "RESEARCH_NOT_ACTIVE",
        "source_text_audit": "REVIEWED_R3"
      },
      "matched_dimensions": [
        "GROWTH_COST",
        "LONG_TERM_FACTION_PRESSURE"
      ]
    }
  ],
  "weave_matches": [
    {
      "record_id": "EW:BOOK_001:005",
      "similarity_score": 12,
      "similarity_reason": "links retrieved lines ['EL:BOOK_001:003', 'EL:BOOK_001:004', 'EL:BOOK_001:005']; matched terms none",
      "limits": [
        "candidate/HOLD research record; not a production-approved template",
        "semantic similarity and transferability require independent review"
      ],
      "provenance": {
        "source_book_id": "BOOK_001",
        "source_commit_sha": "1e10e6e3ffb70eda94a400073155fd89db724ce9",
        "record_file": "emotion-weaves.jsonl",
        "record_line": 5,
        "record_line_sha256": "b59cc7b25b39fa28855e0e14c443637c6c922f01cd0b0f4524ab662df9692a27",
        "source_publication_status": "RESEARCH_NOT_ACTIVE",
        "source_text_audit": "REVIEWED_R3"
      },
      "record_role": "OBSERVED_WEAVE_CANDIDATE",
      "relation_type": "CO_PAYOFF",
      "member_line_ids": [
        "EL:BOOK_001:003",
        "EL:BOOK_001:004",
        "EL:BOOK_001:005"
      ],
      "transferable_parts": {
        "relation_type": "CO_PAYOFF",
        "causal_bridge_shape": "",
        "before_after_shape": {
          "before": "行动结果、处置价值与队伍可靠性都仍承受战场压力",
          "after": "救援产生公开后果，功劳边界得到处理，合作经共同风险验证"
        }
      }
    },
    {
      "record_id": "EW:BOOK_001:007",
      "similarity_score": 12,
      "similarity_reason": "links retrieved lines ['EL:BOOK_001:001', 'EL:BOOK_001:002', 'EL:BOOK_001:006']; matched terms none",
      "limits": [
        "candidate/HOLD research record; not a production-approved template",
        "semantic similarity and transferability require independent review",
        "Family access is a supporting condition; the relative causal weight still needs independent semantic review."
      ],
      "provenance": {
        "source_book_id": "BOOK_001",
        "source_commit_sha": "1e10e6e3ffb70eda94a400073155fd89db724ce9",
        "record_file": "emotion-weaves.jsonl",
        "record_line": 7,
        "record_line_sha256": "a913457e85c4c7ab4fd767f94661d652979ff311d060196183868ab212a9bd57",
        "source_publication_status": "RESEARCH_NOT_ACTIVE",
        "source_text_audit": "REVIEWED_R3"
      },
      "record_role": "OBSERVED_WEAVE_CANDIDATE",
      "relation_type": "ENABLES_CHOICE",
      "member_line_ids": [
        "EL:BOOK_001:002",
        "EL:BOOK_001:001",
        "EL:BOOK_001:006"
      ],
      "transferable_parts": {
        "relation_type": "ENABLES_CHOICE",
        "causal_bridge_shape": "成长线的后天突破提供真元探查能力，直接改变信息获取条件；家庭线提供接触、照护与信任场景，但家庭保护的阶段兑现本身不是秘密开启原因",
        "before_after_shape": {
          "before": "江云只知道叔叔是病人，缺少验证隐藏武者身份的手段",
          "after": "真元探查发现异常，江岩承认后天身份并交代父亲遗产线索"
        }
      }
    },
    {
      "record_id": "EW:BOOK_001:010",
      "similarity_score": 12,
      "similarity_reason": "links retrieved lines ['EL:BOOK_001:001', 'EL:BOOK_001:003', 'EL:BOOK_001:004']; matched terms none",
      "limits": [
        "candidate/HOLD research record; not a production-approved template",
        "semantic similarity and transferability require independent review"
      ],
      "provenance": {
        "source_book_id": "BOOK_001",
        "source_commit_sha": "1e10e6e3ffb70eda94a400073155fd89db724ce9",
        "record_file": "emotion-weaves.jsonl",
        "record_line": 10,
        "record_line_sha256": "ec755b0631b467912c8114d0af4077e234ff5a0a175f79382030872c1f2bfe49",
        "source_publication_status": "RESEARCH_NOT_ACTIVE",
        "source_text_audit": "REVIEWED_R3"
      },
      "record_role": "OBSERVED_WEAVE_CANDIDATE",
      "relation_type": "CO_PAYOFF",
      "member_line_ids": [
        "EL:BOOK_001:001",
        "EL:BOOK_001:003",
        "EL:BOOK_001:004"
      ],
      "transferable_parts": {
        "relation_type": "CO_PAYOFF",
        "causal_bridge_shape": "",
        "before_after_shape": {
          "before": "外部行动和家庭隐瞒都未收束",
          "after": "任务得到结果，家庭秩序同时被迫重排"
        }
      }
    },
    {
      "record_id": "EW:BOOK_001:001",
      "similarity_score": 8,
      "similarity_reason": "links retrieved lines ['EL:BOOK_001:001', 'EL:BOOK_001:003']; matched terms none",
      "limits": [
        "candidate/HOLD research record; not a production-approved template",
        "semantic similarity and transferability require independent review"
      ],
      "provenance": {
        "source_book_id": "BOOK_001",
        "source_commit_sha": "1e10e6e3ffb70eda94a400073155fd89db724ce9",
        "record_file": "emotion-weaves.jsonl",
        "record_line": 1,
        "record_line_sha256": "bebd059b9818f8f617e9e0553d2cdb4c6b9877e888bd6cce79541887ef1a1e3b",
        "source_publication_status": "RESEARCH_NOT_ACTIVE",
        "source_text_audit": "REVIEWED_R3"
      },
      "record_role": "OBSERVED_WEAVE_CANDIDATE",
      "relation_type": "CAUSES_PRESSURE",
      "member_line_ids": [
        "EL:BOOK_001:001",
        "EL:BOOK_001:003"
      ],
      "transferable_parts": {
        "relation_type": "CAUSES_PRESSURE",
        "causal_bridge_shape": "家庭医疗需求不是同章背景，而是江云选择受监管高风险任务入口的直接压力来源",
        "before_after_shape": {
          "before": "家庭缺钱但江云只有备案身份，没有可用任务权限",
          "after": "他进入官方临时任务，家庭目标开始承担制度风险"
        }
      }
    },
    {
      "record_id": "EW:BOOK_001:002",
      "similarity_score": 8,
      "similarity_reason": "links retrieved lines ['EL:BOOK_001:001', 'EL:BOOK_001:003']; matched terms none",
      "limits": [
        "candidate/HOLD research record; not a production-approved template",
        "semantic similarity and transferability require independent review"
      ],
      "provenance": {
        "source_book_id": "BOOK_001",
        "source_commit_sha": "1e10e6e3ffb70eda94a400073155fd89db724ce9",
        "record_file": "emotion-weaves.jsonl",
        "record_line": 2,
        "record_line_sha256": "72daaed72f1e7a197b5a477c2933425c95536b4a2a8fd953908e186c2603ee9e",
        "source_publication_status": "RESEARCH_NOT_ACTIVE",
        "source_text_audit": "REVIEWED_R3"
      },
      "record_role": "OBSERVED_WEAVE_CANDIDATE",
      "relation_type": "ENABLES_CHOICE",
      "member_line_ids": [
        "EL:BOOK_001:003",
        "EL:BOOK_001:001"
      ],
      "transferable_parts": {
        "relation_type": "ENABLES_CHOICE",
        "causal_bridge_shape": "制度入口产生的人脉和任务交接实际扩展了家庭治疗可选路径",
        "before_after_shape": {
          "before": "家庭线有治疗需求但缺少可信武者资源接口",
          "after": "合法任务关系提供了向陆滔询药并继续求医的可行选择"
        }
      }
    },
    {
      "record_id": "EW:BOOK_001:003",
      "similarity_score": 8,
      "similarity_reason": "links retrieved lines ['EL:BOOK_001:001', 'EL:BOOK_001:005']; matched terms none",
      "limits": [
        "candidate/HOLD research record; not a production-approved template",
        "semantic similarity and transferability require independent review"
      ],
      "provenance": {
        "source_book_id": "BOOK_001",
        "source_commit_sha": "1e10e6e3ffb70eda94a400073155fd89db724ce9",
        "record_file": "emotion-weaves.jsonl",
        "record_line": 3,
        "record_line_sha256": "81ed8e943c632000f74e44aed5e733acf2172f2adb63f6db7c674f5ebafa3a0c",
        "source_publication_status": "RESEARCH_NOT_ACTIVE",
        "source_text_audit": "REVIEWED_R3"
      },
      "record_role": "OBSERVED_WEAVE_CANDIDATE",
      "relation_type": "CO_PAYOFF",
      "member_line_ids": [
        "EL:BOOK_001:001",
        "EL:BOOK_001:005"
      ],
      "transferable_parts": {
        "relation_type": "CO_PAYOFF",
        "causal_bridge_shape": "",
        "before_after_shape": {
          "before": "家庭缺药且陆滔合作意图尚未被实际证明",
          "after": "药物资源进入治疗安排，陆滔也成为可验证的资源协作者"
        }
      }
    },
    {
      "record_id": "EW:BOOK_001:004",
      "similarity_score": 8,
      "similarity_reason": "links retrieved lines ['EL:BOOK_001:002', 'EL:BOOK_001:003']; matched terms none",
      "limits": [
        "candidate/HOLD research record; not a production-approved template",
        "semantic similarity and transferability require independent review"
      ],
      "provenance": {
        "source_book_id": "BOOK_001",
        "source_commit_sha": "1e10e6e3ffb70eda94a400073155fd89db724ce9",
        "record_file": "emotion-weaves.jsonl",
        "record_line": 4,
        "record_line_sha256": "d42203e6b825c7d61985816f571c9c0b01ee52e815b93d16c9e50fb473c958b8",
        "source_publication_status": "RESEARCH_NOT_ACTIVE",
        "source_text_audit": "REVIEWED_R3"
      },
      "record_role": "OBSERVED_WEAVE_CANDIDATE",
      "relation_type": "CAUSES_PRESSURE",
      "member_line_ids": [
        "EL:BOOK_001:002",
        "EL:BOOK_001:003"
      ],
      "transferable_parts": {
        "relation_type": "CAUSES_PRESSURE",
        "causal_bridge_shape": "快速成长的可见结果改变了组织如何看待江云，因此成长兑现直接加重制度身份风险",
        "before_after_shape": {
          "before": "成长主要解决即时战斗缺口，制度线仍是有限临时工身份",
          "after": "战力优势本身成为身份来源与组织关系的新压力"
        }
      }
    },
    {
      "record_id": "EW:BOOK_001:006",
      "similarity_score": 8,
      "similarity_reason": "links retrieved lines ['EL:BOOK_001:001', 'EL:BOOK_001:005']; matched terms none",
      "limits": [
        "candidate/HOLD research record; not a production-approved template",
        "semantic similarity and transferability require independent review"
      ],
      "provenance": {
        "source_book_id": "BOOK_001",
        "source_commit_sha": "1e10e6e3ffb70eda94a400073155fd89db724ce9",
        "record_file": "emotion-weaves.jsonl",
        "record_line": 6,
        "record_line_sha256": "ecfdf2a717be54ae4af2d096eceb5cbd96b004b5a1fcb899b3bee073438f2d08",
        "source_publication_status": "RESEARCH_NOT_ACTIVE",
        "source_text_audit": "REVIEWED_R3"
      },
      "record_role": "OBSERVED_WEAVE_CANDIDATE",
      "relation_type": "ENABLES_CHOICE",
      "member_line_ids": [
        "EL:BOOK_001:005",
        "EL:BOOK_001:001"
      ],
      "transferable_parts": {
        "relation_type": "ENABLES_CHOICE",
        "causal_bridge_shape": "伙伴关系的积累实际产生家庭保护选择，并带来新的关系债务",
        "before_after_shape": {
          "before": "合作已有任务证明但家庭仍缺资源渠道",
          "after": "陆滔关系提供新的家庭解决方案，同时形成待结算人情"
        }
      }
    },
    {
      "record_id": "EW:BOOK_001:008",
      "similarity_score": 8,
      "similarity_reason": "links retrieved lines ['EL:BOOK_001:003', 'EL:BOOK_001:006']; matched terms none",
      "limits": [
        "candidate/HOLD research record; not a production-approved template",
        "semantic similarity and transferability require independent review",
        "No source evidence says the father investigation was cancelled; only priority pressure and route change are claimed."
      ],
      "provenance": {
        "source_book_id": "BOOK_001",
        "source_commit_sha": "1e10e6e3ffb70eda94a400073155fd89db724ce9",
        "record_file": "emotion-weaves.jsonl",
        "record_line": 8,
        "record_line_sha256": "3e78d0c6ef230b01ca0a4cbbf91be7baa88ff99172d66bc2c1bc727fb7add84a",
        "source_publication_status": "RESEARCH_NOT_ACTIVE",
        "source_text_audit": "REVIEWED_R3"
      },
      "record_role": "OBSERVED_WEAVE_CANDIDATE",
      "relation_type": "CAUSES_PRESSURE",
      "member_line_ids": [
        "EL:BOOK_001:003",
        "EL:BOOK_001:006"
      ],
      "transferable_parts": {
        "relation_type": "CAUSES_PRESSURE",
        "causal_bridge_shape": "已证实的是第32章起国家任务占用时间与权限；第31章通知本身不是执行，也没有取消父辈调查",
        "before_after_shape": {
          "before": "第31章只有两小时内到场的通知，国家任务尚未执行",
          "after": "第32章实际到场并进入强制安排，私人目标开始受到行动优先级压力"
        }
      }
    },
    {
      "record_id": "EW:BOOK_001:009",
      "similarity_score": 8,
      "similarity_reason": "links retrieved lines ['EL:BOOK_001:003', 'EL:BOOK_001:006']; matched terms none",
      "limits": [
        "candidate/HOLD research record; not a production-approved template",
        "semantic similarity and transferability require independent review",
        "Canonical chapter-34 substantive fields contradict the frozen source text; R3 raw-text audit controls this research interpretation."
      ],
      "provenance": {
        "source_book_id": "BOOK_001",
        "source_commit_sha": "1e10e6e3ffb70eda94a400073155fd89db724ce9",
        "record_file": "emotion-weaves.jsonl",
        "record_line": 9,
        "record_line_sha256": "9b83e808a72f10e259b44f85cd6157819d5e481a437c7808c005ecd28d17e7d7",
        "source_publication_status": "RESEARCH_NOT_ACTIVE",
        "source_text_audit": "REVIEWED_R3"
      },
      "record_role": "OBSERVED_WEAVE_CANDIDATE",
      "relation_type": "CAUSES_PRESSURE",
      "member_line_ids": [
        "EL:BOOK_001:003",
        "EL:BOOK_001:006"
      ],
      "transferable_parts": {
        "relation_type": "CAUSES_PRESSURE",
        "causal_bridge_shape": "制度权限上限为父辈线制造真实延迟压力；口头消息不能等同于正式档案访问",
        "before_after_shape": {
          "before": "第33章提出正式请求，但访问能力尚未验证",
          "after": "第34章确认权限不足，父辈调查被延后且正式档案仍不可读"
        }
      }
    },
    {
      "record_id": "EW:BOOK_001:011",
      "similarity_score": 8,
      "similarity_reason": "links retrieved lines ['EL:BOOK_001:002', 'EL:BOOK_001:006']; matched terms none",
      "limits": [
        "candidate/HOLD research record; not a production-approved template",
        "semantic similarity and transferability require independent review",
        "The letter does not prescribe the immediate training order; only resource/option enablement is retained."
      ],
      "provenance": {
        "source_book_id": "BOOK_001",
        "source_commit_sha": "1e10e6e3ffb70eda94a400073155fd89db724ce9",
        "record_file": "emotion-weaves.jsonl",
        "record_line": 11,
        "record_line_sha256": "8277a374d2a739c2911ca0f4e5349e04e37219baad0ee635239e97d9f6fbf31c",
        "source_publication_status": "RESEARCH_NOT_ACTIVE",
        "source_text_audit": "REVIEWED_R3"
      },
      "record_role": "OBSERVED_WEAVE_CANDIDATE",
      "relation_type": "ENABLES_CHOICE",
      "member_line_ids": [
        "EL:BOOK_001:006",
        "EL:BOOK_001:002"
      ],
      "transferable_parts": {
        "relation_type": "ENABLES_CHOICE",
        "causal_bridge_shape": "父辈遗赠提供新的成长输入与选择空间，不构成父亲规定弄影步、后天后期顺序的证据",
        "before_after_shape": {
          "before": "父辈线只有口述与打不开的正式档案",
          "after": "江云获得直接书信与成长资源，但练功顺序仍由自己决定"
        }
      }
    },
    {
      "record_id": "EW:BOOK_001:012",
      "similarity_score": 8,
      "similarity_reason": "links retrieved lines ['EL:BOOK_001:003', 'EL:BOOK_001:006']; matched terms none",
      "limits": [
        "candidate/HOLD research record; not a production-approved template",
        "semantic similarity and transferability require independent review"
      ],
      "provenance": {
        "source_book_id": "BOOK_001",
        "source_commit_sha": "1e10e6e3ffb70eda94a400073155fd89db724ce9",
        "record_file": "emotion-weaves.jsonl",
        "record_line": 12,
        "record_line_sha256": "0afd2a044c1fbd6b27456ef1d822bbee9b7b3cb1b6481a39ac2d3da39e134864",
        "source_publication_status": "RESEARCH_NOT_ACTIVE",
        "source_text_audit": "REVIEWED_R3"
      },
      "record_role": "OBSERVED_WEAVE_CANDIDATE",
      "relation_type": "ENABLES_CHOICE",
      "member_line_ids": [
        "EL:BOOK_001:003",
        "EL:BOOK_001:006"
      ],
      "transferable_parts": {
        "relation_type": "ENABLES_CHOICE",
        "causal_bridge_shape": "制度授权实际改变信息可得性；原文没有证明这是江云战果兑换的本人权限",
        "before_after_shape": {
          "before": "第34章正式查询失败，父亲档案仍受权限限制",
          "after": "吴成取得查阅权限，第54章能够实际展示档案"
        }
      }
    },
    {
      "record_id": "EW:BOOK_001:013",
      "similarity_score": 8,
      "similarity_reason": "links retrieved lines ['EL:BOOK_001:001', 'EL:BOOK_001:003']; matched terms none",
      "limits": [
        "candidate/HOLD research record; not a production-approved template",
        "semantic similarity and transferability require independent review"
      ],
      "provenance": {
        "source_book_id": "BOOK_001",
        "source_commit_sha": "1e10e6e3ffb70eda94a400073155fd89db724ce9",
        "record_file": "emotion-weaves.jsonl",
        "record_line": 13,
        "record_line_sha256": "4e2c65c3970557fb9553420d27adfa55d226a9054a7a8a7c6fc6e8c60654b6f3",
        "source_publication_status": "RESEARCH_NOT_ACTIVE",
        "source_text_audit": "REVIEWED_R3"
      },
      "record_role": "OBSERVED_WEAVE_CANDIDATE",
      "relation_type": "CAUSES_PRESSURE",
      "member_line_ids": [
        "EL:BOOK_001:003",
        "EL:BOOK_001:001"
      ],
      "transferable_parts": {
        "relation_type": "CAUSES_PRESSURE",
        "causal_bridge_shape": "制度公开改变家庭保护的社会条件，而不是只提供新闻背景；该解释不依赖 canonical 中错误的江岩出关叙述",
        "before_after_shape": {
          "before": "家庭仍可被隔离在秘密武者世界之外",
          "after": "公开确认使家人更难保持局外人状态并增加照护压力"
        }
      }
    }
  ],
  "macro_matches": [
    {
      "record_id": "MA:BOOK_001:001",
      "similarity_score": 20,
      "similarity_reason": "links retrieved lines ['EL:BOOK_001:001', 'EL:BOOK_001:002', 'EL:BOOK_001:003', 'EL:BOOK_001:004', 'EL:BOOK_001:005']; matched terms none",
      "limits": [
        "candidate/HOLD research record; not a production-approved template",
        "semantic similarity and transferability require independent review",
        "Sustainable family safety after public exposure remains open.",
        "Jiang Yun still lacks a stable formal institutional position and continues to use temporary or personal interfaces.",
        "Chapter 34 did not grant archive access or show Jiang Yun performing the depicted rescue."
      ],
      "provenance": {
        "source_book_id": "BOOK_001",
        "source_commit_sha": "1e10e6e3ffb70eda94a400073155fd89db724ce9",
        "record_file": "macro-emotion-arcs.jsonl",
        "record_line": 1,
        "record_line_sha256": "1bc6be502a0af983bb790b171542b9c04a126ab3bf3c3c0db5373de5fb0f58d8",
        "source_publication_status": "RESEARCH_NOT_ACTIVE",
        "source_text_audit": "REVIEWED_R3"
      },
      "record_role": "OBSERVED_MACRO_ARC_CANDIDATE",
      "member_line_ids": [
        "EL:BOOK_001:001",
        "EL:BOOK_001:002",
        "EL:BOOK_001:003",
        "EL:BOOK_001:004",
        "EL:BOOK_001:005"
      ],
      "transferable_parts": {
        "macro_promise_shape": "江云能否把突然获得的武者力量转化为家人可见的保护与社会中可持续的合法位置，同时不丢掉处置边界",
        "settlement_contract_shape": "家庭安全获得可持续改善，力量得到外部任务验证，江云取得可持续的合法社会位置，并以可见处置边界承担公共后果",
        "organization_shape": "家庭缺口、成长验证与制度入口已形成跨章互相制约的阶段承诺。"
      }
    },
    {
      "record_id": "MA:BOOK_001:002",
      "similarity_score": 16,
      "similarity_reason": "links retrieved lines ['EL:BOOK_001:001', 'EL:BOOK_001:002', 'EL:BOOK_001:003', 'EL:BOOK_001:006']; matched terms none",
      "limits": [
        "candidate/HOLD research record; not a production-approved template",
        "semantic similarity and transferability require independent review",
        "The father's final fate, complete enemy chain, and tide explanation remain unresolved.",
        "Chapter 34 is an access failure with oral hearsay, not formal archive access.",
        "Narrative dominance transfer from MA1 is not proven by chapter 60."
      ],
      "provenance": {
        "source_book_id": "BOOK_001",
        "source_commit_sha": "1e10e6e3ffb70eda94a400073155fd89db724ce9",
        "record_file": "macro-emotion-arcs.jsonl",
        "record_line": 2,
        "record_line_sha256": "7be5c879f5122483e10fb37efaa57e5b45e608510ddf8cee72c73af5a1517a10",
        "source_publication_status": "RESEARCH_NOT_ACTIVE",
        "source_text_audit": "REVIEWED_R3"
      },
      "record_role": "OBSERVED_MACRO_ARC_CANDIDATE",
      "member_line_ids": [
        "EL:BOOK_001:001",
        "EL:BOOK_001:002",
        "EL:BOOK_001:003",
        "EL:BOOK_001:006"
      ],
      "transferable_parts": {
        "macro_promise_shape": "江云能否查清父亲遗产、青云山与潮汐背后的关系，并决定这段真相如何改变家庭责任和制度立场",
        "settlement_contract_shape": "父亲遗产、国家档案和潮汐关系获得可核验的阶段证据，并实质改变江云的成长、家庭或制度选择",
        "organization_shape": "到第48章，父辈期待已跨真元探查、家庭口述、征召压力、权限失败、遗物和父母书信持续运行，并开始实际改变家庭与成长资源；第34章本身不足以完成这一资格证明。"
      }
    }
  ],
  "handoff_matches": [
    {
      "record_id": "AH:BOOK_001:001",
      "similarity_score": 4,
      "similarity_reason": "links retrieved lines none; matched terms none",
      "limits": [
        "candidate/HOLD research record; not a production-approved template",
        "semantic similarity and transferability require independent review",
        "Temporal overlap is observed, but MA1 remains partially paid and a completed narrative-dominance transfer is not proven.",
        "observed overlap does not prove narrative-dominance transfer",
        "must remain CANDIDATE_UNVERIFIED when reused"
      ],
      "provenance": {
        "source_book_id": "BOOK_001",
        "source_commit_sha": "1e10e6e3ffb70eda94a400073155fd89db724ce9",
        "record_file": "arc-handoffs.jsonl",
        "record_line": 1,
        "record_line_sha256": "a08cad96272712fdb11b28241428f7a1240f5635a11466ebfc5294a93861771b",
        "source_publication_status": "RESEARCH_NOT_ACTIVE",
        "source_text_audit": "REVIEWED_R3"
      },
      "record_role": "UNVERIFIED_HANDOFF_REFERENCE_ONLY",
      "from_macro_id": "MA:BOOK_001:001",
      "to_macro_id": "MA:BOOK_001:002",
      "transferable_parts": {
        "overlap_shape": "第28章父辈期待启动时MA1尚未完成；第32–42章两者同时运行，第48章MA2才达到宏弧组织候选门槛，第54章取得档案阶段兑现。",
        "old_contract_preservation": "MA2的信息、遗产和父母去向合同不能替代MA1的家庭安全与合法位置合同"
      },
      "observed_overlap": true,
      "handoff_conclusion": "CANDIDATE_UNVERIFIED"
    }
  ],
  "retrieval_interpretation": "deterministic source resolution and similarity hints only; semantic composer chooses and adapts"
}

Use actual retrieved EL/EW/MA/AH IDs; select relevant patterns and record similarity_reason, transferable_part, reuse_limit. `options[*].mode` must be `E2_E3_ENABLED`; include source-backed emotion_source_uses, independent payoff contracts and honest overlapping macro structure. Never turn AH001 into verified dominance transfer.
