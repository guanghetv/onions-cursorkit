# add-workspace-prd-feishu-sync

工作区 PRD 与飞书文档自动同步及一致性校验。

## 先读

- **[介绍.md](./介绍.md)** — 给人看的一页说明（含流程图、门禁边界、用法）

## 产物

| 文件 | 说明 |
|---|---|
| `介绍.md` | 方案介绍 + Mermaid 流程图（推荐入口） |
| `proposal.md` | 背景、变更、能力、验收 |
| `design.md` | 架构决策与数据流 |
| `tasks.md` | 实现任务清单 |
| `plan.md` | 按 writing-plans 展开的实现计划（逐步可执行） |
| `specs/workspace-specflow-prd-feishu-sync/spec.md` | 同步技能（新增） |
| `specs/workspace-specflow-prd-consistency-check/spec.md` | 一致性校验（新增） |
| `specs/workspace-specflow-prd-publish/spec.md` | 一键编排（新增） |
| `specs/workspace-specflow-prd-template/spec.md` | 9 稿瘦身（修改） |
| `specs/workspace-specflow-pm-spec/spec.md` | 9 稿挂接（修改） |
| `specs/workspace-specflow-pm-spec-5/spec.md` | 5 稿挂接（修改） |

## 关联

- 飞书项目：https://project.feishu.cn/ruxiao/tec_prd/detail/7016921222
- 分支：`feat/135-产研spec流程优化飞书文档自动更新方案调研及实现-m-7016921222`
- 技能实现：`plugins/workspace-specflow/skills/prd-feishu-sync/` 等
