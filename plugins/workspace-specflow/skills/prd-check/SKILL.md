---
name: prd-check
description: >-
  发布前一次做完内容质量、本地与飞书对齐、可读性告警。
  Use when: prd-check、一致性校验、AI Review、PRD 自检、能否开工、评审就绪、进开发前自检、prd-consistency-check。
  禁止用对话口头清单代替真跑。不负责推送正文，不写基线。
---

# /prd-check — 发布前一次检查

`/pm-spec` 的改稿循环不调用本技能。`/prd-publish` 在 push 成功后调用。用户单独要求自检时也可以直接跑。

旧命令 `/prd-consistency-check` 和口头「AI Review」都执行本技能，不要再分成两次。

## 执行前必读

按顺序 Read，不得跳过：

1. `../../references/产品组PRD写作规范.md`
2. `../prd-feishu-sync/references/chapter-map.md`
3. `references/ai-review-rubric.md`

写作规范管正文该怎么写。chapter-map 管两端怎么对齐。rubric 管内容阻断、评分和可读性告警。三者冲突时，写作规范优先。

## 硬规则

命中触发词就必须真跑并落盘报告，禁止口头打勾。

本技能不修改 `prd.md` 契约正文，不 push 正文，不写快照，不改 `prd.status`。只写报告、`metadata.consistency`，以及文末「文档状态」的 emoji、底色、边框和校验行。

## 检查什么

一次跑完三类：

| 类 | 来源 | 失败时 |
| --- | --- | --- |
| 内容质量 | rubric 的 P0 | critical，阻断发布 |
| 两端对齐 | 下面的 C1–C7 | critical 阻断；评审前 C5 降为 warning |
| 可读性 | rubric 的文字墙 / 原 W2 | 只 warning，不阻断 |

对齐只比对契约层 unit：

`contract.overview` / `versions` / `background` / `goal` / `scope` / `critical` / `regression` / `features` / `MODULE-N` / `details` / `materials` / `observability`（后几项按需；旧 `design` / `tracking` / `narrative.*` 按 chapter-map 别名兼容）。

定位：unit key → 标题关键词 → 序号兼容。禁止只靠 `3.1` / `3.2` 判断。

| ID | 通过条件 |
| --- | --- |
| C1 | `feishu.doc_token` 可 fetch |
| C2 | 契约 unit / MODULE-N 在飞书与本地按语义对齐 |
| C3 | 每 MODULE 的详细说明含可判断的规则、状态或异常，并有原型锚点或「无原型（原因）」。不要求独立验收清单 |
| C4 | Feature 清单中的 MODULE 列与详情中的 MODULE-N 一致 |
| C5 | 进开发前：各 MODULE 意图一致（允许措辞差）。评审前降为 warning |
| C6 | 契约展示序号未为「补洞」而重排。存在背景与目标章节不是失败 |
| C7 | 相对 last_synced 无未推送契约改动。两端都有、且 `feishu.feishu_revision` 已记到发布回读 `R2` 的版本表基线行，不算未推送 |

`/prd-publish` 里调用时，阶段是进开发前，C5 与 C6 为 critical。单独自检且用户说明仍在评审前时，C5 降为 warning。

## 流程

1. 确认需求目录。按 `../../references/three-way-sync.md` 区分草稿超前和另一端多出来的内容。另一端多出来的内容写进检查结果，不因为本地只是超前就先停下来。无 token → C1 fail，提示先 `/prd-feishu-sync create`。
2. 完整读本地 `prd.md`。`lark-cli docs +fetch` 读飞书，每个 MODULE 详细说明整格读完。优先 user；失败则标明，进开发前视为未通过。中间被截掉、只剩开头和结尾，C2 失败，不得写成通过。某一句规则和本地不同，C2 失败，报告里并列两边原句。本地末尾「飞书文档」不参与对齐。版本表「对应 spec / demo」只在本地，飞书没有这一列不算不对齐。
3. 按写作规范看内容质量，按 chapter-map 做两端对齐，并扫描文字墙。
4. 缺少旧式验收 checklist，但需求详情里的规则可判断时，不得因此判失败。用户没有明确保留时，残留未确认的 `[待定]` 视为阻断。
5. 写入 `prototypes/prd-check-YYYY-MM-DD.md`（同日覆盖）。报告含 rubric 要求的评审范围、可开工结论、总分、可读性告警明细，以及逐条 C/W 证据。证据写 unit key 和命中标题。
6. 更新 `metadata.consistency`：`status`（`pass` / `warn` / `fail`）/ `checked_at` / `report_path` / `source_commit`。这个字段就是 `/prd-check` 的结论，名字保持 `consistency`，兼容已有需求目录。不要另写 `prd.check`。只读时若旧目录没有该字段，视为 `unknown`。
7. 用 XML 局部更新文末那一块「文档状态」。emoji、底色、边框、校验行按选定的一态一起改。心跳码仍是 `prd-sync:check:v1`。同步绑定行和 `prd-sync:status:v1` 保留。禁止整篇覆盖。若仍是「同步绑定」「校验」两块，或还有 `prd-sync:readability:v1`、`prd-sync:consistency:v1`，先合并成这一块再写结论。

| 结论 | 属性 | 校验行 | `consistency.status` |
|---|---|---|---|
| 无 critical，且无未跳过 warning | `emoji="✅" background-color="light-green" border-color="green"` | ✅ · YYYY-MM-DD · prototypes/prd-check-YYYY-MM-DD.md | `pass` |
| 仅 warning | `emoji="⚠️" background-color="light-orange" border-color="orange"` | ⚠️ · YYYY-MM-DD · 可读性约 N 处 · prototypes/prd-check-YYYY-MM-DD.md | `warn` |
| 有 critical | `emoji="❌" background-color="light-red" border-color="red"` | ❌ · YYYY-MM-DD · prototypes/prd-check-YYYY-MM-DD.md | `fail` |

告警的摘要写可读性约 N 处和报告路径，不在飞书逐条罗列。写飞书失败时本地不得伪造成 `pass`。

块内结构固定。开标签用上表选中的那一行，不要把通过态抄到告警或失败上。通过态：

```xml
<callout emoji="✅" background-color="light-green" border-color="green">
  <p><b>文档状态</b></p>
  <p><b>同步绑定</b> <code>prd-sync:status:v1</code></p>
  <p>{原同步绑定行}</p>
  <p><b>校验</b> <code>prd-sync:check:v1</code></p>
  <p>✅ · YYYY-MM-DD · prototypes/prd-check-YYYY-MM-DD.md</p>
</callout>
```

告警开标签改为 `emoji="⚠️" background-color="light-orange" border-color="orange"`，校验行改为 `⚠️ · YYYY-MM-DD · 可读性约 N 处 · prototypes/prd-check-YYYY-MM-DD.md`。失败开标签改为 `emoji="❌" background-color="light-red" border-color="red"`，校验行改为 `❌ · YYYY-MM-DD · prototypes/prd-check-YYYY-MM-DD.md`。

8. 对话给紧凑摘要。有 critical 时明确阻断 `/prd-publish` 写基线。`/qa-spec` 仍生成用例，只提示未通过。

## 报告不要漏的字段

- 需求目录、阶段、飞书 URL、时间、commit
- 评审范围、可开工结论、总分
- 可读性告警的位置和拆分建议
- 逐条 ID / 等级 / 状态 / 摘要 / 证据
- 已跳过的 warning
- 风险预检只引用已有结论和 `prototypes/prd-risk-precheck.md` 路径；本技能不重跑预检

## 协作

| 命令 | 关系 |
| --- | --- |
| `/pm-spec` | 改稿循环不自动调用 |
| `/prd-feishu-sync` | 只推正文。push 不写 ✅/⚠️/❌，重置时 emoji 也回到 📎 |
| `/prd-publish` | push 成功后调用本技能。没有 critical 才写基线，`warn` 可以写 |
| `/qa-spec` | 读 `consistency.status`。`fail`、缺失或 `unknown` 只提示 |
