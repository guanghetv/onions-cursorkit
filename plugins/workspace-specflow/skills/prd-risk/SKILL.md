---
name: prd-risk
description: >-
  Use when user mentions: 产品需求风险预检/prd-risk/风险预检/业务方案评审前风险。
  Runs business-pre-review risk precheck for a specs-repo requirement and writes a standalone report.
---

# /prd-risk — 产品需求风险预检

在 specs 仓库对目标需求做**业务方案评审前风险预检**。规则与流程以同插件内整包 skill 为准，不得简化成口头清单。

## 必读

执行前 **Read**：

1. `../product-requirement-risk-gate/SKILL.md`
2. `../product-requirement-risk-gate/references/input-output.md`
3. `../product-requirement-risk-gate/references/rules.json`

口径对齐飞书[使用说明](https://guanghe.feishu.cn/docx/YtfEdHv1toSqanxODkdcjgLYnLc)。`/pm-spec-5` Step 6 必须调用本技能，禁止另写一套判定。

## 边界

- `mode=precheck`，`stage=business_pre_review`，`environment=delivery_test`，`provisional=true`
- **不**向产品/研发索取接口、日志、实现方案或完整 PRD 平台元数据
- **不**同步飞书；**不**声称已入库、已调度双周汇总、法务已收到
- 预检通过 **不等于** 技术通过或上线批准

## 流程

### Step 1: 定位需求

扫描 `requirements/`，定位目标需求（用户指定或当前对话需求）。需要 `prd.md`。

提示 specs 仓 `git pull`（behind remote 时先提示）。

### Step 2: 抽取业务事实

从 `prd.md`（及用户本轮粘贴的补充）抽取业务必填：

- 方案目的及目标指标
- 计划上线/执行时间
- 正常业务规模
- 权益及操作总上限
- 是否公开传播、是否可分享
- 单个操作主体允许次数
- 单次权益或操作内容

已写在需求里的内容不要再填一遍。没写清的记待补，**禁止猜日期/额度/天数**。

条件必填仅在影响规则判定时补问一次汇总。

### Step 3: 扫描规则

按预检包执行全部 37 条扫描。多场景取并集，不把普通需求扩成全公司治理项目。

判定：`MET` / `HIT` / `UNKNOWN` / `DEFERRED` / `NOT_APPLICABLE`。整体：

- 任一 HIT → **需调整**
- 无 HIT 但业务必填缺失 → **待补信息**
- 业务必填齐全且无 HIT → **规则预检通过**（即使存在 DEFERRED）

L0 命中硬阻断；L1 默认调整。

### Step 4: 写独立报告

覆盖写入 `prototypes/prd-risk-precheck.md`（相对需求目录）。结构：

```markdown
# 产品需求风险预检报告

- 规则包: V4-r241-business-precheck-1.1.1
- checked_at: <带时区时间>
- provisional: true
- precheck_result: 规则预检通过 | 待补信息 | 需调整

## 结论
<使用说明三类措辞；通过时必须写：可进入正常方案评审；不等同技术验证或上线批准>

## 命中规则
<无则写「无」。有则每条：编号 / 名称 / 等级 / 原文 / 业务依据 / 调整要求>

## 必要业务补件
<没有则省略本节>

## 下一步
<补信息 / 提交调整后复检 / 例外申请包 / 继续正常评审>
```

对话中向用户展示结论与报告路径，不要只说「好的」。

### Step 5: 调整与例外

- 用户提交改后方案 → 复检并更新报告
- 只回复「不接受调整」→ 问是否需要制作例外评估申请包
- 已要求制作/提交 → 生成申请包到 `prototypes/prd-risk-exception-pack.md`，指引飞书搜索「法务助理机器人」→「业务灰产风险损失评估」；状态 pending，不得称已移交

### Step 6: 返回码（供 `/pm-spec-5`）

| 结论 | 返回 |
|------|------|
| 规则预检通过 | `PASS`：允许 5 稿确认与快照 |
| 待补信息 / 需调整 | `BLOCK`：禁止 `prd.v5.status=confirmed`、禁止版本表追加、禁止写 `snapshots/prd-v5-*.md` |

## 约束

- 不得把「可选」理解成忽略已明确违规
- 不得用泛泛的「安全可控」抵消具体 HIT
- 免费活动 7 天规则不适用于已明确的原订单漏发补发
