---
name: novel-growth-timeline
description: Track long-form web-fiction growth and emotion-payoff cadence across chapters, including distance since the last power increase, visible power proof, strong payoff, romantic/relationship progression, costs, and growth debt. Use before planning or drafting the next chapter, after a chapter is confirmed, or when auditing pacing; it advises but does not draft prose.
metadata:
  short-description: Track power, emotion, and relationship payoff cadence
---

# Novel Growth Timeline

Use this skill as the chapter-to-chapter growth and emotion cadence monitor, not to write prose. The core record is:

`Chapter → State → Gain → Cost → Change → Next Need`

Track growth beyond realm advancement: combat power, skills, equipment, resources, money, attributes, special abilities, identity, reputation, relationships, romantic progress, information, battle experience, plot access, payoff, and foreshadowing.

For urban high-martial fiction, treat two reader-facing engines as especially important without making either mechanical:

1. **Power gain and proof**: the protagonist becomes stronger, then visibly proves the gain against a meaningful standard, opponent, task, ranking, or public result.
2. **Attraction and relationship gain**: an attractive female lead or key woman notices, chooses, trusts, desires, allies with, protects, competes for, or publicly changes her relationship with the protagonist through her own action.

“A beautiful woman appears” is not a relationship payoff. A relationship payoff requires observable movement and must respect the project's single-heroine, multi-heroine, no-harem, or romance-light rules. Female characters retain independent goals and cannot be reduced to trophies.

## Authority and write boundary

- Treat confirmed final prose and confirmed chapter summaries as the source of truth. Do not treat drafts as formal timeline facts.
- In BUILD, establish the timeline from existing confirmed material.
- In UPDATE, analyze only newly confirmed chapters, then update the current-state table and counters.
- In ADVISE, recommend the next chapter's reward based on the timeline, current story phase, and available comparable samples; database patterns are evidence, not rules.
- In AUDIT, inspect the requested recent window (normally 5, 10, or 20 chapters) for pacing anomalies.
- In AUTO-ADVISE, run a compact cadence check before a new chapter is planned or drafted. Report counters and debt; do not require the user to ask “how many chapters since the last upgrade?” every time.
- In DRAFT-PREVIEW, evaluate whether a work draft appears to deliver the intended payoff, but do not write it into the confirmed timeline.
- Do not update a formal record until the user confirms the chapter as final and authorizes the update. When no authorization exists, show a proposed update only.

## Minimal evidence and project fit

Read only the material needed to establish the current state: relevant volume/phase outline, previous confirmed chapter or summary, recent summaries, active foreshadowing/emotion records, and relevant character/ability/location facts. Follow project-level instructions and preserve its setting, power tiers, source-imprint limits, character knowledge boundaries, and single-lead relationship rules.

If a local material database exists, ADVISE should prefer samples matching the same genre, chapter range, protagonist stage, plot phase, and conflict type. Prefer nearby chapters over late-stage examples. Report sample count, observed ratios for realm/skill/equipment/resource/identity/relationship gains, strong-payoff ratio, common gain combinations, median gain chapter, and longest consecutive no-gain stretch when the data is available. Never invent database statistics.

If no formal timeline exists, derive a **provisional dashboard** from recent confirmed summaries or chapters and label every counter provisional. Do not create a formal file automatically. A recommended persistent location is `小说资料/成长与情绪时间线.md`; creating or updating it still requires the user's explicit authorization.

## Per-chapter record

For each analyzed chapter, output:

- Chapter number
- Realm before / after
- Core abilities before / after
- Hard gains: realm, skill, equipment, resources, money, attributes, special ability; use “none” where applicable
- Soft gains: information, identity, reputation, relationship, romantic progress, attraction/recognition, battle experience, plot access; use “none” where applicable
- Costs: resource consumption, injuries, failure, exposure risk, favors/debts, other costs
- Plot change: resolved problem, newly opened problem, fulfilled foreshadowing, added foreshadowing
- Payoff: main payoff, strength (weak / medium / strong / breakout), and type (power increase, power proof, humiliation reversal, treasure, advancement, identity reveal, information gap, counterattack, romantic attraction, relationship choice, public recognition, other)
- Growth flags: realm, combat power, ability, resources, relationship, identity, plot — YES/NO
- Whether the chapter contains an effective gain — YES/NO

Do not count an event as meaningful payoff merely because the protagonist killed, leveled, won, or received an item. Require observable reaction, public result, relationship movement, information advantage, cost echo, or an internal choice that validates the gain.

## Current-state table and counters

After every authorized UPDATE, maintain: current chapter, realm, combat-power position, skills, equipment, core resources, important identity, important relationships, known information, current goal, current risks, and unfulfilled foreshadowing.

Maintain chapter distances since the latest:

- realm increase;
- new core skill;
- clear combat-power increase;
- visible proof of the latest power gain;
- important equipment;
- important resource;
- identity increase or public revaluation;
- romantic attraction/interest made observable;
- important relationship choice or state change;
- female lead/key woman taking an active relationship-defining action;
- strong payoff;
- major foreshadowing payoff.

Count from the latest confirmed event; do not reset a counter for a minor variation, repeated flirtation, generic admiration, another effortless win, or an item that has not changed the protagonist's options.

Assign growth/emotion debt per dimension (realm, combat proof, skill, equipment, resources, identity, romantic attraction, relationship choice, plot, payoff) from ★ to ★★★★★. Debt means that dimension has been unchanged for too long relative to the current phase; it does not force an immediate reward. Balance it against causality, setup, difficulty, and the protagonist's current construction. Always report the raw chapter distance alongside the star rating so the user can judge the recommendation.

## ADVISE output

Use this compact structure:

```text
当前章节：
当前主角状态：
最近一次境界提升：
距上次明确战力提升：
距上次战力可见验证：
最近一次技能获得：
最近一次重要资源：
距上次恋爱/吸引力兑现：
距上次关键关系选择：
最近一次强爽点：
成长欠债最高项：
数据库相似样本：

【节奏判断】正常 / 偏慢 / 成长真空 / 奖励过密

【下一章建议】
主要目标：
建议收益：
建议强度：
是否建议升级：
是否建议获得新技能：
是否建议获得资源：
是否建议兑现伏笔：

【原因】
只解释与当前时间线、故事阶段和数据库证据有关的原因。

【警告】
指出奖励重复、升级过密、伏笔积压、装备/技能久未验证或成长停滞。
```

AUTO-ADVISE additionally returns a compact dashboard:

| Dimension | Last confirmed chapter | Distance | Debt | Suggested payoff window | Required visible evidence |
| --- | ---: | ---: | --- | --- | --- |
| Power increase | | | | | |
| Power proof | | | | | |
| Skill/equipment/resource | | | | | |
| Identity/public recognition | | | | | |
| Romantic attraction | | | | | |
| Relationship choice | | | | | |
| Strong payoff | | | | | |

Do not force every dimension into one chapter. Recommend a primary payoff and at most one supporting payoff, then explain which debt remains open.

Do not say “chapter X must level up.” Instead state the present risk, observed nearby-sample pattern, preferred reward, alternatives, and tradeoffs. Avoid granting realm, skill, and equipment as three simultaneous major rewards unless the confirmed plot requires it.

## AUDIT checks

Flag: consecutive chapters with no effective gain; only information gains for too long; overly rapid advancement without process; many untested skills; equipment or skills not demonstrated after acquisition; power gains never receiving visible proof; accumulating foreshadowing without payoffs; attractive women appearing without relationship choices; repeated flirtation that does not change the relationship; expanding relationships without changes; repeated breakout payoffs; major advancement without matching difficulty or cost; resource inflation; duplicated rewards.

Conclude with `PASS`, `PASS WITH TODO`, or `FAIL` only when reviewing against explicit project constraints. A timeline recommendation is not permission to change formal story facts.
