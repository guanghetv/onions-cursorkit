## Context

`create-feature-branch` 是 Cursor 技能文档（`SKILL.md` + `references/*`），由大模型按步骤执行：飞书工作项 → 分支命名 → `git` 操作。此前文档虽有「切到 master」，但未把 **基线门禁** 写成 MUST/MUST NOT，易出现从 `develop` 直接 `git checkout -b` 的错误。本变更无运行时服务，交付物为 **规范与文档一致性**。

## Goals / Non-Goals

**Goals:**

- 默认基线 **仅** `master`；执行 `git checkout -b` 前须验证当前分支（默认路径下为 `master`）。
- **禁止**自动使用 `main`；无 `master` 时停止并提示，或依赖用户**显式**指定基线（可含 `main`、`develop`）。
- 文档三处一致：`SKILL.md`、快速清单、`references/DETAILED_STEPS.md`；错误场景在 `TROUBLESHOOTING.md` 可复现排查。

**Non-Goals:**

- 不引入脚本、Git 钩子或 CI；不修改飞书 MCP 协议。
- 不强制团队统一仓库默认分支名；仅规定**技能默认**从 `master` 出发。

## Decisions

### 1. 默认基线固定为 `master`

**理由**：与团队既有约定一致，避免模型在 `main`/`master` 间猜测。  
**备选**：自动检测 `origin/HEAD` 指向的分支——**拒绝**，与用户明确要求「不自动用 main」及显式控制冲突。

### 2. 门禁用「当前分支名」而非「merge-base」

**理由**：技能执行者是 LLM + shell，分支名检查（`git branch --show-current`）成本低、可解释；不引入 `merge-base` 与远程解析，减少误用。  
**代价**：若本地 `master` 未跟踪远程且落后，仍可能基于旧 `master` 建分支——由 `git pull origin master` 缓解。

### 3. 显式例外覆盖任意分支名

用户写明基线（含 `main`）时，门禁改为「当前分支 == 用户指定名」，并在回复中声明基线。  
**理由**：覆盖「仅有 `main` 无 `master`」的仓库，且不违反「不自动」原则。

### 4. OpenSpec 与技能双轨

`openspec/changes/.../specs/` 为需求真值；`SKILL.md` 为执行说明。二者冲突时 **以 spec 为准** 并回写技能。

## Risks / Trade-offs

- **[Risk] 仓库无 `master` 时默认流程失败** → **Mitigation**：停止并提示；`TROUBLESHOOTING` 增加「无 master」条目；用户显式指定 `main` 为基线后继续。
- **[Risk] 模型仍跳过步骤** → **Mitigation**：清单 + MUST NOT + 门禁验证小节；Code Review 时对照 spec。

## Migration Plan

- 本仓库：合并变更后，技能立即生效；无需部署。
- 若需将 delta 合并进 `openspec/specs/`：在归档或 `openspec-sync` 流程中执行（另开任务）。

## Open Questions

（无。`main` 仅经显式用户指定，已闭环。）
