# Brainstorm: add-workspace-prd-risk-precheck

## 已确认决策

| 决策点 | 结论 | 来源 |
|--------|------|------|
| 需求目标 | 在产研工作区插件 `workspace-specflow` 接入「产品需求风险预检」；5稿阶段就要触发；单独出一份预检报告；skill 安装包尽量全部保留进插件 | 用户需求 |
| 行为口径 | 严格参考飞书使用说明（结论三类、补问/调整/例外申请包、法务助理机器人交接、预检≠上线批准） | 用户 + [使用说明](https://guanghe.feishu.cn/docx/YtfEdHv1toSqanxODkdcjgLYnLc) |
| skill 包来源 | 本地包 `/Users/lige/Downloads/product-requirement-risk-gate/`（v1.1.1）尽量原样迁入 | 用户指定 |
| 遗留 Codex Trellis | 暂不归档 `08-26-workspace-specflow-codex-plugin`，仅切走绑定 | 用户选 B |
| 本需求协作账本 | 拒绝新建 Trellis task；运行态只写 `.onion-sdd/current.json`；脑暴记忆用本文件 | 用户拒绝 |
| change-id | `add-workspace-prd-risk-precheck` | Agent 按 OpenSpec 命名 |
| 5稿触发点 | `/pm-spec-5` Step 6：用户明确确认 5稿时、写入快照之前自动跑预检；同时支持手动重新跑 | 用户选 C + 手动重跑 |
| HIT 门禁 | 硬阻断：结论为 HIT（需调整）或待补信息时，禁止完成 5稿确认与快照；须调整/补信息后复检通过才能确认 | 用户选 hard_block |
| 报告落盘 | 需求目录：`requirements/<需求>/prototypes/prd-risk-precheck.md`（与 5稿 AI Review 报告并列） | 用户选 req_prototypes |
| 手动重跑入口 | 独立 slash `/prd-risk` + `/pm-spec-5` 确认时自动调用同一 skill | 用户选 A + `/prd-risk` |
| 飞书同步 | 本期不同步飞书，只写本地 `prototypes/prd-risk-precheck.md` | 用户选 no_sync |
| 接入方案 | 整包 vendoring 到 `plugins/workspace-specflow/skills/product-requirement-risk-gate/`；薄适配 `/prd-risk` + `/pm-spec-5` Step6 硬门禁；Codex 经现有 `pack.py` 同步 | 用户选 vendor_adapter |
| 设计确认 | 同意方案 1 设计，进入 OpenSpec 落盘 | 用户选 approve |

## 开放问题

- 无

