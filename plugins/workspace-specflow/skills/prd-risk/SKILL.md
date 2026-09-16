---
name: prd-risk
description: >-
  Use when user mentions: 产品需求风险预检/prd-risk/风险预检/业务方案评审前风险。
  Also run automatically after 5稿 or 9稿 prd.md is written, before AI Review.
  Thin adapter: must Read and follow product-requirement-risk-gate; do not invent rules.
---

# /prd-risk — 产品需求风险预检（工作区薄适配）

在 specs 仓库对目标需求做业务方案评审前风险预检。

## 唯一判定依据（禁止发明）

执行前 **必须 Read**（按顺序，不得跳过）：

1. `../product-requirement-risk-gate/SKILL.md`
2. `../product-requirement-risk-gate/references/input-output.md`
3. `../product-requirement-risk-gate/references/rules.json`

**判定、必填、补问、结论措辞、调整/例外申请包流程，一律以预检包原文为准。**  
本文件只负责：定位需求、落盘路径、metadata 索引、工作区确认门禁码、对话提示强度。

### 禁止自行发明

- **禁止**在适配层另写必填表、判定公式、例外路径；一律打开预检包原文执行
- **禁止**把「待补信息」说成硬阻断、禁止确认、或「风险拦截」；工作区确认门禁仅「需调整」硬拦
- **禁止**把预检包未写成 HIT 的情况伪造成规则命中（含把某字段未定说成来自 `rules.json` 的命中）
- **禁止**因「待补信息」停止 Step 4.5 之后的 AI Review，或拒绝继续 5稿/9稿流程
- **禁止**因「计划上线/执行时间」未定/待定索要日期或判待补（见预检包：该项为非必须）
- **禁止**猜测日期、额度、天数；预检包要求不猜时如实记录
- **禁止**向产品/研发索取接口、日志、实现方案或平台元数据
- **禁止**在报告里写工作区门禁码、Step 编号、AI Review、飞书 sync、`PASS`/`SOFT`/`BLOCK`

口径对齐飞书[使用说明](https://guanghe.feishu.cn/docx/YtfEdHv1toSqanxODkdcjgLYnLc)。`/pm-spec-5`、`/pm-spec` 的 Step 4.5 与手动重跑调用本技能。

## 边界

- `mode=precheck`，`stage=business_pre_review`，`environment=delivery_test`，`provisional=true`
- **不**同步飞书；**不**声称已入库、已调度双周汇总、法务已收到
- 预检通过 **不等于** 技术通过或上线批准

## 流程

### Step 1: 定位需求

扫描 `requirements/`，定位目标需求。需要 `prd.md`。behind remote 时提示 `git pull`。

### Step 2–3: 按预检包抽取事实并扫描规则

**完整按**已 Read 的 `product-requirement-risk-gate/SKILL.md` 执行流程与 `input-output.md` 判定，**不得**在本适配层复述或改写必填表、判定公式、例外路径。

工作区仅叠加一条确认门禁（不是预检包规则）：确认 5稿/9稿时，只有结论为「需调整」才硬拦；「待补信息」软提醒后可确认；禁止把待补说成硬阻断或规则命中。

### Step 4: 写/更新预检报告

同一文件 `prototypes/prd-risk-precheck.md`：

1. 若已存在：先抽出「## 运行历史」旧行，不得丢弃
2. **当前正文**严格按预检包 `input-output.md`「产品正文：可直接转发业务」（评估结论 / 需处理事项 / 下一步 / 请业务回复）
3. 追加本次运行历史行（`checked_at` + 结论）
4. 通过时不写未命中规则表；待补与需调整按预检包写完整需处理事项

元信息头可保留：

```markdown
# 产品需求风险预检报告

- 规则包: V4-r241-business-precheck-1.1.1
- checked_at: <带时区时间，最新一次>
- provisional: true
- precheck_result: 规则预检通过 | 待补信息 | 需调整
```

其后章节标题与内容跟预检包产品正文，**不要**加工作区说明。

文末：

```markdown
## 运行历史
| checked_at | 结论 |
|------------|------|
| <时间> | <规则预检通过 \| 待补信息 \| 需调整> |
```

### Step 5: 回写 metadata（索引，不进报告正文）

```yaml
prd:
  risk_precheck:
    last_result: 规则预检通过 | 待补信息 | 需调整
    last_checked_at: <与报告 checked_at 相同>
    report: prototypes/prd-risk-precheck.md
```

### Step 6: Agent 对话提示（不写入报告）

| 结论 | 对话强度 | 禁止 |
|------|----------|------|
| 需调整 | **显著告警**：报告路径 + 命中摘要；未调整不得确认 5稿/9稿 | — |
| 待补信息 | **软提醒**：缺项 + 报告路径；**明确可继续确认** | 禁止说「阻断」「拦截」「不能确认」 |
| 规则预检通过 | **轻提示**一行：已预检通过 + 报告路径 | 禁止展开规则明细 |

### Step 7: 调整与例外

完全按预检包：改后方案复检；拒绝调整则询问是否制作例外评估申请包；已要求则写到 `prototypes/prd-risk-exception-pack.md`（独立文件），指引「法务助理机器人-业务灰产风险损失评估」；`pending`，不得称已移交。

### Step 8: 返回码（仅供工作区确认门禁，禁止写入预检报告）

| 结论 | 返回 | 5稿/9稿确认 |
|------|------|-------------|
| 规则预检通过 | `PASS` | 允许确认 |
| 待补信息 | `SOFT` | **允许**确认（须软提醒；绝非硬拦） |
| 需调整 | `BLOCK` | 禁止 confirmed 与对应快照 |
| 无报告 / 结论不可读 | `MISSING` | 必须先完成本技能再谈确认 |

## 约束

- 预检包约束（可选≠忽略违规、不得用「安全可控」抵消 HIT、免费活动 7 天不适用原订单漏发补发等）以预检包原文为准，此处不复述改写
- 有疑问时 **重新 Read 预检包**，不要凭适配层记忆发明
