---
name: prd-risk
description: >-
  Use when user mentions: 产品需求风险预检/prd-risk/风险预检/业务方案评审前风险。
  Also run automatically after 5稿 or 9稿 prd.md is written, before AI Review.
  Runs business-pre-review risk precheck and writes a standalone legal-precheck report.
---

# /prd-risk — 产品需求风险预检

在 specs 仓库对目标需求做**业务方案评审前风险预检**。规则、判定与**报告正文**以同插件内整包 skill 为准，禁止另写一套口径。

## 必读

执行前 **Read**：

1. `../product-requirement-risk-gate/SKILL.md`
2. `../product-requirement-risk-gate/references/input-output.md`
3. `../product-requirement-risk-gate/references/rules.json`

口径对齐飞书[使用说明](https://guanghe.feishu.cn/docx/YtfEdHv1toSqanxODkdcjgLYnLc)。`/pm-spec-5` Step 4.5、`/pm-spec` Step 4.5 及手动重跑必须调用本技能。

## 边界

- `mode=precheck`，`stage=business_pre_review`，`environment=delivery_test`，`provisional=true`
- **不**向产品/研发索取接口、日志、实现方案或完整 PRD 平台元数据
- **不**同步飞书；**不**声称已入库、已调度双周汇总、法务已收到
- 预检通过 **不等于** 技术通过或上线批准
- **报告文档只含预检 skill 的产品正文**（评估结论 / 需处理事项 / 下一步 / 请业务回复）+ 预检运行历史。工作区门禁、AI Review、5稿/9稿步骤、插件路径、工作台 JSON 字段、37 条全量扫描表、later_stage 技术清单等**不得写入** `prd-risk-precheck.md`

## 流程

### Step 1: 定位需求

扫描 `requirements/`，定位目标需求。需要 `prd.md`。

提示 specs 仓 `git pull`（behind remote 时先提示）。

### Step 2: 抽取业务事实

从 `prd.md`（及用户本轮粘贴的补充）抽取业务必填（见预检包「每次必须」七项）。已写内容不再填表。没写清的记待补，**禁止猜日期/额度/天数**。条件必填仅在影响规则判定时补问一次汇总。

### Step 3: 扫描规则

按预检包扫描全部 37 条。多场景取并集，不把普通需求扩成全公司治理项目。

整体结论：

- 任一 HIT → **需调整**
- 无 HIT 但业务必填缺失 → **待补信息**
- 业务必填齐全且无 HIT → **规则预检通过**（即使存在 DEFERRED）

L0 命中即「需调整」（工作区确认门禁跟三类结论，不另设 L0 通道）。

### Step 4: 写/更新预检报告（严格按预检 skill 产品正文）

同一文件 `prototypes/prd-risk-precheck.md`：

1. 若已存在：先抽出「## 运行历史」表中的旧行，不得丢弃
2. **当前正文**按最新扫描整段覆盖，结构必须对齐预检包 `input-output.md`「产品正文：可直接转发业务」
3. 追加本次运行历史行（`checked_at` + 结论）
4. **待补信息**与**需调整**均必须落完整正文；**规则预检通过**不写命中规则表（协议：正文不罗列未命中/不适用规则）

模板（仅此结构；不要加工作区说明）：

```markdown
# 产品需求风险预检报告

- 规则包: V4-r241-business-precheck-1.1.1
- checked_at: <带时区时间，最新一次>
- provisional: true
- precheck_result: 规则预检通过 | 待补信息 | 需调整

## 评估结论
<一句结论 + 主要原因。通过时必须写：规则预检通过，可进入正常方案评审；不等同技术验证或上线批准。辅助预检 / provisional 一句即可>

## 需处理事项
<仅「需调整」：逐条编号 / 名称 / 等级 / 原文 / 判定依据 / 调整要求。
仅「待补信息」：一次性业务必填缺项。
通过：写「无」或省略本节>

## 下一步
<按预检包阶段：补信息 / 调整后复检 / 询问是否制作例外申请包 / 继续正常评审。责任方写业务，不要写 5稿确认或插件命令>

## 请业务回复
<业务可直接回答的问题；没有则省略本节>

## 运行历史
| checked_at | 结论 |
|------------|------|
| <时间> | <规则预检通过 \| 待补信息 \| 需调整> |
```

禁止写入报告的内容：`PASS`/`SOFT`/`BLOCK`、Step 6、AI Review、飞书 sync、`metadata.yaml` 字段说明、工作台 `run_id`/`persistence`、37 条全表、接口/日志等非业务补件。

### Step 5: 回写 metadata（工作区索引，不是报告正文）

更新需求 `metadata.yaml`（没有则创建该段）：

```yaml
prd:
  risk_precheck:
    last_result: 规则预检通过 | 待补信息 | 需调整
    last_checked_at: <与报告 checked_at 相同>
    report: prototypes/prd-risk-precheck.md
```

### Step 6: Agent 对话提示（不写入报告）

| 结论 | 对话强度 |
|------|----------|
| 需调整 | **显著告警**：报告路径 + 命中摘要；未调整不得确认 5稿/9稿 |
| 待补信息 | **显著提醒**：缺项 + 报告路径；确认前须再提醒信息不完整 |
| 规则预检通过 | **轻提示**一行：已预检通过 + 报告路径；不展开规则明细 |

### Step 7: 调整与例外

- 用户提交改后方案 → 复检并更新报告（含历史行与 metadata）
- 只回复「不接受调整」→ 按预检包原句询问是否制作例外评估申请包
- 已要求制作/提交 → 申请包写到 `prototypes/prd-risk-exception-pack.md`（独立文件，不塞进预检报告），指引飞书搜索「法务助理机器人」→「业务灰产风险损失评估」；`pending`，不得称已移交

### Step 8: 返回码（仅供 `/pm-spec-5` / `/pm-spec` 门禁，禁止写入预检报告）

| 结论 | 返回 | 5稿/9稿确认 |
|------|------|-------------|
| 规则预检通过 | `PASS` | 允许确认 |
| 待补信息 | `SOFT` | 软提醒后允许确认 |
| 需调整 | `BLOCK` | 禁止 confirmed 与对应快照 |
| 无报告 / 结论不可读 | `MISSING` | 必须先完成本技能再谈确认 |

## 约束

- 不得把「可选」理解成忽略已明确违规
- 不得用泛泛的「安全可控」抵消具体 HIT
- 免费活动 7 天规则不适用于已明确的原订单漏发补发
