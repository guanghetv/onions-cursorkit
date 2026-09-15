# workspace-specflow-prd-risk-precheck

工作区插件内的产品需求风险预检：整包规则 skill、独立报告、手动命令与 5 稿确认硬门禁。

## ADDED Requirements

### Requirement: 预检 skill 包整包保留

系统 MUST 将 `product-requirement-risk-gate` v1.1.1 安装包以相对路径完整放入 `plugins/workspace-specflow/skills/product-requirement-risk-gate/`，并在执行预检时读取该目录内 `SKILL.md`、`references/rules.json` 与 `references/input-output.md`。

#### Scenario: 相对引用可解析

- **WHEN** Agent 执行产品需求风险预检
- **THEN** 不依赖交付者本机 `Downloads` 路径
- **AND** 能打开规则库、输入输出协议、双周协议与验收场景文件

#### Scenario: 不冒充工作台生产门禁

- **WHEN** 插件内预检完成
- **THEN** 报告须标明 `provisional=true`（未接确定性执行器/工作台）
- **AND** 不得声称已入库、已调度双周汇总或法务已收到申请包

### Requirement: 独立预检报告口径

系统 MUST 将每次预检结果单独写入当前需求的 `prototypes/prd-risk-precheck.md`，正文面向业务且严格对齐使用说明。

#### Scenario: 三类结论

- **WHEN** 预检结束
- **THEN** 结论为「规则预检通过」「待补信息」「需调整」三者之一
- **AND** 规则预检通过时须说明可进入正常方案评审，不等同技术验证或上线批准

#### Scenario: 需调整时展示命中规则

- **WHEN** 存在 HIT
- **THEN** 正文直接展示命中规则编号、名称、等级、原文、业务依据与业务可决定的调整要求
- **AND** 同时扫描全部适用规则，不得只展示一条后结束

#### Scenario: 待补只问业务必填

- **WHEN** 缺少影响判定的业务必填
- **THEN** 一次性汇总业务必填缺项
- **AND** 不得向产品或研发索取接口、日志、完整 PRD 元数据等非必须项

#### Scenario: 调整与例外申请包

- **WHEN** 业务接受调整并提交改后方案
- **THEN** 按新方案复检并更新报告
- **WHEN** 业务明确不接受调整且尚未要求申请包
- **THEN** 询问是否需要制作例外评估申请包
- **WHEN** 已明确要求制作或提交
- **THEN** 直接制作申请包并指引提交「法务助理机器人-业务灰产风险损失评估」，未实际接收不得称已移交

#### Scenario: 本期不同步飞书

- **WHEN** 预检报告已写入本地
- **THEN** 系统不得默认创建或更新飞书预检文档，也不得把预检全文同步进 PRD 飞书页

### Requirement: `/prd-risk` 手动重跑

系统 MUST 提供 slash 命令 `/prd-risk`，对当前 specs 仓目标需求执行与 5 稿确认时相同的预检与报告落盘。

#### Scenario: 从 5 稿抽取业务事实

- **WHEN** 执行 `/prd-risk` 且存在 `prd.md`
- **THEN** 优先从本地 PRD 抽取业务必填，已写内容不再向用户重复填表
- **AND** 未写清的业务必填按待补列出，不得臆造日期、额度或天数

#### Scenario: 模拟 10 天会员活动

- **WHEN** 输入为公开新用户体验活动、每人领一次 10 天会员
- **THEN** 报告结论为需调整
- **AND** 命中包含单次活动单账号权益不超过 7 天的规则（R-免费活动-04）

### Requirement: Codex 源同步

系统 MUST 让 Codex `workspace-specflow` 打包从 Cursor 插件 skills 源同步预检 skill，不另维护第二份规则正文。

#### Scenario: pack 包含预检包

- **WHEN** 执行 `pack.py sync` 与 `check`
- **THEN** 产物含 `product-requirement-risk-gate` 与 `prd-risk`（若适配为独立 skill）
- **AND** 源变化会触发漂移检查
