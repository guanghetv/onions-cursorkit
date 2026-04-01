## Why

执行「创建 Feature 分支」技能时，大模型有时会跳过切换到默认基线分支，直接在 `develop` 等分支上执行 `git checkout -b`，导致新分支误基于 `develop`。技能文档虽已有「切换到 master」步骤，但缺少可执行的强制门禁与 MUST NOT，约束力不足。需要在技能规范与 OpenSpec 中明确 **基线分支**、**验证步骤** 与 **例外** 规则，使行为可审计、可复现。

## What Changes

- **基线分支**：默认**仅**从 `master` 的最新提交创建 feature 分支；**不**自动根据仓库是否存在 `main` 而改用 `main`；**禁止**在未完成基线检出与 `pull` 前创建分支。
- **门禁验证**：在 `git checkout -b` / `git switch -c` 之前，**必须**满足默认路径下 `git branch --show-current` 为 `master`（或与用户明确指定的基线一致）。
- **MUST NOT**：禁止在 `develop`、`feat/*` 等非基线分支上直接创建 feature 分支；禁止以「当前分支已最新」为由跳过切换基线；**禁止**自动检出 `main` 作为默认基线。
- **无 master 时**：`git checkout master` 失败则停止并提示；用户可**显式**指定以某分支（含 `main`）为基线后再继续。
- **例外**：仅当用户**明确写出**以某分支（如 `develop`、`main`）为基线时，可改用该分支，并在回复中声明基线分支名。
- **文档与清单**：`SKILL.md`、快速执行清单与 `references/DETAILED_STEPS.md` 与上述规则一致；**无**业务应用代码变更。

## Capabilities

### New Capabilities

- `create-feature-branch`：飞书工作项驱动的标准化 feature 分支创建；包含工作区洁净检查、**默认基线分支为 `master` 的检出与更新**、门禁验证、飞书任务查询、分支命名、远程存在性检查、推送与上游追踪；以及 **非默认基线** 的显式用户例外（含用户显式指定 `main`）。

### Modified Capabilities

（无。`openspec/specs/` 中尚无该 capability 的主 spec，本变更为首次纳入能力描述。）

## Impact

- **`.cursor/skills/create-feature-branch/`**：`SKILL.md`、`references/DETAILED_STEPS.md`（及必要时 `EXAMPLES.md`、`TROUBLESHOOTING.md` 中与基线相关的说明）。
- **无**：运行时服务、API、依赖版本变更。
- **无 breaking change**：用户显式指定基线时行为与「例外」条款一致；默认路径仅收紧模型执行顺序，不改变既有分支命名与飞书集成规则。
