# add-workspace-prd-risk-precheck

## 背景

- 业务方案进入评审前需要按法务规则做风险预检；现有安装包 `product-requirement-risk-gate` v1.1.1 与飞书[使用说明](https://guanghe.feishu.cn/docx/YtfEdHv1toSqanxODkdcjgLYnLc)已定义结论、补问、调整与例外申请包流程。
- 产研工作区插件在 5 稿确认时尚未接入该预检，产品可能带着未过规则的方案进入交互评审。
- 需求来源：飞书工作项 `7115444521`，分支 `feat/139-产研工作区插件新增产品需求风险预检Skill-m-7115444521`。

## 目标

- 将 skill 安装包尽量原样迁入 `workspace-specflow`。
- 在 `/pm-spec-5` Step 6（用户确认 5 稿、写快照前）自动触发预检，并支持 `/prd-risk` 手动重跑。
- 单独落盘预检报告；正文口径严格对齐使用说明（通过 / 待补 / 需调整、调整复检、例外申请包、法务助理机器人指引）。
- HIT 或待补信息时硬阻断 5 稿确认与快照。

## 变更

- 新增 vendored skill 目录 `plugins/workspace-specflow/skills/product-requirement-risk-gate/`（整包保留相对路径）。
- 新增工作区适配 skill + slash `/prd-risk`：定位需求、从 `prd.md` 抽取业务事实、调用预检、写报告。
- 修改 `/pm-spec-5` Step 6：快照前调用同一适配；未通过则停止确认。
- 文档与 `workspace-awareness` 增加命令入口。
- Codex 插件经现有 `pack.py` 从源 skills 同步，不另维护第二份正文。

## 影响范围

- 页面/模块: `workspace-specflow`（Cursor 插件 + Codex pack 源）
- 数据/API: 无业务 HTTP API；不接工作台库表与法务机器人发送接口
- 权限/安全/资金: 预检可命中资金/权益类规则；本插件只产出报告与门禁，不做法务损失计算或发布批准
- 兼容性: 未跑预检的旧需求不回填历史报告；新的 5 稿确认路径新增硬门禁

## 不做范围

- 本期不同步飞书预检报告。
- 不接工作台数据库、双周定时汇总、法务机器人真实移交接口。
- 不把预检通过当作技术评审或上线批准。
- 不归档遗留 Trellis `08-26-workspace-specflow-codex-plugin`。
- 不为本需求新建 Trellis task。

## 已确认决策

| 决策点 | 结论 | 来源 |
|--------|------|------|
| 需求目标 | 工作区插件接入产品需求风险预检；5稿触发；独立报告；skill 包尽量全量保留 | 用户需求 |
| 行为口径 | 严格参考飞书使用说明 | 用户 + 使用说明 |
| skill 包来源 | `/Users/lige/Downloads/product-requirement-risk-gate/` v1.1.1 尽量原样迁入 | 用户指定 |
| 遗留 Codex Trellis | 暂不归档，仅切走绑定 | 用户选 B |
| 本需求协作账本 | 拒绝新建 Trellis；只用 `current.json` + OpenSpec | 用户拒绝 |
| change-id | `add-workspace-prd-risk-precheck` | Agent |
| 5稿触发点 | Step 6 确认时、快照前自动跑；支持手动重跑 | 用户选 C + 手动重跑 |
| HIT 门禁 | HIT 或待补则禁止确认与快照 | 用户选 hard_block |
| 报告落盘 | `requirements/<需求>/prototypes/prd-risk-precheck.md` | 用户选 req_prototypes |
| 手动重跑入口 | `/prd-risk` + `/pm-spec-5` 自动调用 | 用户选 A + `/prd-risk` |
| 飞书同步 | 本期不同步飞书 | 用户选 no_sync |
| 接入方案 | 整包 vendoring + 薄适配；Codex 走 `pack.py` | 用户选 vendor_adapter |
| 设计确认 | 同意进入 OpenSpec 落盘 | 用户选 approve |

## 验收

- 安装包关键文件（`SKILL.md`、`references/*`、`agents/openai.yaml`、接入/核验说明）在插件内相对路径可解析。
- `/prd-risk` 对模拟「新用户领 10 天会员」产出独立报告，结论为需调整，并展示规则编号/名称/等级/原文/依据/调整要求。
- `/pm-spec-5` 确认路径：预检未通过时不写 `prd.v5.status=confirmed`、不追加版本表、不写 v5 快照。
- 预检通过后才允许完成 Step 6 快照与 metadata 更新。
- 本期报告不写入飞书。
- `python3 codex-plugins/workspace-specflow/scripts/pack.py check` 在 sync 后可通过（含新 skill）。

## 风险与回滚

- 风险: Agent 误把技术细节当业务补件；适配 skill 必须遵循原包「只问业务必填」。
- 风险: 5 稿待定字段导致「待补」阻断确认；这是刻意门禁，产品需补业务信息或说明无法提供。
- 回滚: 移除 vendored 目录、`/prd-risk` 与 Step 6 门禁即可恢复旧 5 稿确认行为。

## References

- 飞书工作项：https://project.feishu.cn/ruxiao/tec_prd/detail/7115444521
- 使用说明：https://guanghe.feishu.cn/docx/YtfEdHv1toSqanxODkdcjgLYnLc
- skill 包：`/Users/lige/Downloads/product-requirement-risk-gate/`
- 规则框架来源：https://guanghe.feishu.cn/docx/LlQldNdLpoatWWx4QOMcSoa8nod
