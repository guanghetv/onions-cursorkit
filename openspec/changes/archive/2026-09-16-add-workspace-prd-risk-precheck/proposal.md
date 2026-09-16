# add-workspace-prd-risk-precheck

## 背景

- 业务方案进入评审前需要按法务规则做风险预检；现有安装包 `product-requirement-risk-gate` v1.1.1 与飞书[使用说明](https://guanghe.feishu.cn/docx/YtfEdHv1toSqanxODkdcjgLYnLc)已定义结论、补问、调整与例外申请包流程。
- 产研工作区插件在 5 稿确认时尚未接入该预检，产品可能带着未过规则的方案进入交互评审。
- 需求来源：飞书工作项 `7115444521`，分支 `feat/139-产研工作区插件新增产品需求风险预检Skill-m-7115444521`。

## 目标

- 将 skill 安装包尽量原样迁入 `workspace-specflow`。
- 在 `/pm-spec-5` **Step 4 写出 5稿之后、Step 5 AI Review 之前**自动触发预检，并支持 `/prd-risk` 手动重跑。
- 独立报告 `prototypes/prd-risk-precheck.md`：正文严格按预检 skill 产品正文；需调整与待补写完整口径；多次预检更新同一文件并记录每次时间点与结论；通过时不展开命中明细。工作区门禁不写入该报告。
- `/pm-spec-5` 与 `/pm-spec` 均在写出后自动预检；确认时方案 C；无报告或结论过期必须先跑预检。

## 变更

- 新增 vendored skill 目录 `plugins/workspace-specflow/skills/product-requirement-risk-gate/`（整包保留相对路径）。
- 新增工作区适配 skill + slash `/prd-risk`：定位需求、从 `prd.md` 抽取业务事实、调用预检、写报告。
- 修改 `/pm-spec-5` 与 `/pm-spec`：写出后 Step 4.5 自动预检；AI Review 只嵌结论；确认按方案 C，无报告不得当通过。
- 文档与 `workspace-awareness` 增加命令入口。
- Codex 插件经现有 `pack.py` 从源 skills 同步，不另维护第二份正文。

## 影响范围

- 页面/模块: `workspace-specflow`（Cursor 插件 + Codex pack 源）
- 数据/API: 无业务 HTTP API；不接工作台库表与法务机器人发送接口
- 权限/安全/资金: 预检可命中资金/权益类规则；本插件只产出报告与门禁，不做法务损失计算或发布批准
- 兼容性: 未跑预检的旧需求不回填历史；5稿/9稿确认路径在无报告或结论过期时必须先预检；仅「需调整」硬阻断

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
| 5稿触发点 | Step 4 后 / Review 前自动跑；支持 `/prd-risk` 手动重跑 | 产品修订：产出5稿后 |
| HIT 门禁 | 方案 C：需调整硬阻断；待补软提醒可确认；通过可确认 | 用户选 C |
| 报告落盘 | 同一文件 `prototypes/prd-risk-precheck.md`；待补也写；复检更新并记录时间与结论 | 用户确认 |
| 手动重跑入口 | `/prd-risk` + `/pm-spec-5` 自动调用 | 用户选 A + `/prd-risk` |
| 飞书同步 | 本期不同步飞书 | 用户选 no_sync |
| 接入方案 | 整包 vendoring + 薄适配；Codex 走 `pack.py` | 用户选 vendor_adapter |
| 设计确认 | 同意进入 OpenSpec 落盘 | 用户选 approve |

## 验收

- 安装包关键文件（`SKILL.md`、`references/*`、`agents/openai.yaml`、接入/核验说明）在插件内相对路径可解析。
- `/prd-risk` 对模拟「新用户领 10 天会员」产出独立报告，结论为需调整，并展示规则编号/名称/等级/原文/依据/调整要求。
- `/pm-spec-5` 与 `/pm-spec`：写出后自动预检；无报告或 `prd.md` 已改必须先预检；需调整禁止确认；待补可确认但须提醒。
- 预检报告正文仅为预检 skill 产品正文 + 运行历史，不含工作区门禁字段。
- `metadata.yaml` 的 `prd.risk_precheck` 记录最近结论与时间。
- AI Review（v5 / 9稿）含「风险预检」结论小节，明细不内嵌。
- 本期报告不写入飞书。
- `python3 codex-plugins/workspace-specflow/scripts/pack.py check` 在 sync 后可通过（含新 skill）。

## 风险与回滚

- 风险: Agent 误把技术细节当业务补件；适配 skill 必须遵循原包「只问业务必填」。
- 风险: 5 稿待定字段导致「待补」；方案 C 允许确认，产品须知信息不完整。
- 回滚: 移除 vendored 目录、`/prd-risk` 与 Step 4.5/6 门禁即可恢复旧 5 稿确认行为。

## 需求调整记录

- 2026-09-16：产品要求 5稿**产出后**自动预检（非确认时）。无风险不在 Agent 展开风险明细、不写命中报告正文；有风险才显著提示并落完整报告。AI Review 只展示结论并引导看独立报告。
- 2026-09-16：待补信息**需要报告**；多次预检**更新同一报告**，并记录每次预检时间点与结论。Step 6 采用方案 C（需调整硬阻断 / 待补可确认 / 通过可确认）。
- 2026-09-16：修复门禁漏洞——无报告/结论不可读/`prd.md` 已改必须先预检；9稿同等触发与方案 C；报告正文严格按预检 skill 产品正文，工作区门禁与非预检内容不写入报告；`metadata.yaml` 仅作索引。
- 2026-09-16：`prd-risk` 改为薄适配，判定唯一来源为 `product-requirement-risk-gate`；禁止发明必填/硬拦；禁止把「待补」或上线日未定说成阻断或规则命中。
- 2026-09-16：预检包修订——「计划上线/执行时间」从每次必填改为非必须；未定不得判待补、不得索要日期。

## References

- 飞书工作项：https://project.feishu.cn/ruxiao/tec_prd/detail/7115444521
- 使用说明：https://guanghe.feishu.cn/docx/YtfEdHv1toSqanxODkdcjgLYnLc
- skill 包：`/Users/lige/Downloads/product-requirement-risk-gate/`
- 规则框架来源：https://guanghe.feishu.cn/docx/LlQldNdLpoatWWx4QOMcSoa8nod
