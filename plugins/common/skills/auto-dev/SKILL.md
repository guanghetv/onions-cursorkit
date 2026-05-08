---
name: auto-dev
description: 小需求自动开发技能。IDE 内完成扫描与建分支，再交本机 Cursor CLI 无头执行改码、CR、提交与提测 MR（target=develop），最后通知 Review。
---

# /auto-dev 小需求自动开发

用于小需求自动化交付：文案改动、新增提示、轻逻辑调整等低复杂度需求。支持单项目与多项目（2-3 项）场景。

**执行分为两阶段**，避免 IDE Agent 内大量 `npm`/`eslint` 终端命令触发逐条「Run / Allowlist」确认，改由本机 **Cursor CLI**（`agent -p --force`）静默改码与提 MR。

## 触发入口

- 命令：`/auto-dev`
- 输入必须包含：
  - 需求详情描述（必填）
  - 飞书卡片链接或明确开发分支名（二选一，至少一个）
- 触发后执行「扫描 → 一次确认 → **阶段A 建分支 → 阶段B CLI 全流程**」

## 适用边界

**小需求白名单（允许自动执行）：**

- 文案改动
- 新增/调整提示语
- 轻量配置调整
- 不改变主业务流程的轻逻辑修正

**非小需求（必须阻断并提示改走常规流程）：**

- 大规模重构
- 跨系统流程重写
- 数据结构或接口契约大改
- 需要复杂联调或迁移脚本的改动

## 强约束（MUST）

1. 执行前必须强制扫描当前工作区项目范围。
2. 命中项目数为 0 时必须阻断，禁止硬改任何项目。
3. 仅允许一次人工确认（确认命中项目范围）。
4. **阶段划分**：**阶段A（IDE）**只做门禁与**各仓库创建并推送 feature 分支**（可用 MCP、少用业务代码改写）。**阶段B（本机 Cursor CLI）**必须用 **Headless Agent**（`agent -p --force`）完成改动、lint、AI CodeReview 自修、提交、创建 MR；**禁止在 IDE Agent 会话内**执行需求相关的批量改码与反复 `npm run lint`（易导致终端审批卡顿）。
5. **阶段B 启动方式（硬性）**：阶段A 完成后，**当前 IDE Agent 必须亲自调用终端（Shell）执行**启动命令（例如 `nohup agent -p --force ... &`，命令全文见 `references/CLI_HANDOFF.md`），将子进程 **PID**、**日志路径** 写入回复。**禁止**仅以聊天文案或「请复制以下命令到终端」作为阶段B 的唯一交付；开发者不应被要求手动粘贴执行才能完成阶段B（若单次终端授权弹窗出现，属于环境策略，Agent 仍须发起执行而非替用户决策不跑）。
6. 每个命中项目必须独立创建 MR，目标分支固定为 `develop`。
7. AI CodeReview 的 `Critical` 问题必须自动修复并复审，最多 3 轮（在阶段B 内完成）。
8. 创建 MR 时必须按 `references/MR_TEMPLATE.md` 生成结构化描述。
9. 若"当前项目"不在命中项目列表中，必须先提示并等待范围确认，禁止在当前项目硬改。
10. 创建 MR 时必须优先读取本地环境变量 `GITLAB_TOKEN` 或 `GITLAB_PRIVATE_TOKEN`；若两者均不存在，阶段B 进入 `BLOCKED` 并提示配置后重试。
11. 若提供飞书卡片链接，必须先尝试查询卡片详情，并以卡片内容优先推断需求详情。
12. 若未提供飞书卡片链接，必须要求开发者提供明确开发分支名，否则中断后续流程。
13. 多项目场景下，所有命中项目必须使用同一个分支名（跨仓同名分支）执行。
14. **阶段B 全部完成后**（或 CLI 日志中已汇总），必须输出醒目的完成通知，包含 MR 链接与改动摘要，告知开发者可以 Review。

## 禁止项（MUST NOT）

- 未扫描完成前进入改动阶段。
- 命中为 0 时仍继续开发。
- 在流程中自动扩容新增项目（仅允许告警，需下次触发重新确认）。
- 将提测 MR 指向非 `develop` 分支。
- 3 轮 CR 仍未通过时继续自动建 MR。
- 缺少"飞书卡片链接 + 明确分支名"两者时继续执行。
- 多项目场景为不同项目生成不同分支名。
- **阶段A 结束后，仍在 IDE Agent 会话内执行业务代码改动与 lint 主流程**（应交给 CLI；阶段A 仅允许建分支所需的 git 与路径校验）。
- **阶段A 完成后，不把 Cursor CLI 启动命令交给用户手动执行**（除非 Shell 执行失败且已输出 BLOCKED 与重试说明）；禁止用「仅贴脚本、让用户自己去终端跑」代替 IDE Agent 的 Shell 调用。

## 主状态机

`SCANNED -> CONFIRMED -> BRANCH_CREATED -> [CLI] CHANGES_APPLIED -> LOCAL_VERIFY_PASSED -> CR_LOOP_PASSED -> COMMITTED -> MR_CREATED -> DONE`

任一关键门禁失败进入 `BLOCKED`，输出阻断原因与恢复建议后停止。

## 标准流程

1. 校验输入门禁（需求详情 + 飞书卡片链接或明确分支名）。
2. 若有飞书卡片链接，先查询卡片详情并推断需求详情。
3. 强制扫描工作区并产生命中证据。
4. 展示命中项目并等待**唯一一次**人工确认。
5. 生成 `run-id`。**阶段A**：在每个目标仓库按 `create-feature-branch` 创建并推送统一分支名。
6. **阶段B**：写入 `/tmp/auto-dev-<run-id>.context.md`，**立即用 Shell 执行**本机 `agent -p --force` 启动命令（详见 `references/CLI_HANDOFF.md`）；由 CLI 子进程完成改动、lint、CR、提交、MR。
7. 根据 CLI 输出或日志汇总，向开发者发出完成通知。

## 确认卡片（全程唯一人工操作）

确认前必须展示：

- 命中项目列表（单/多项目）及命中证据（关键词/路径/模块映射）
- 当前项目是否在命中列表中
- 将使用的分支名
- 可选动作：确认全部 / 排除部分后确认 / 取消

**确认后阶段A 立即建分支；建分支完成后自动进入阶段B（CLI），无需开发者再确认「是否走 CLI」。**

## 两阶段执行要求

| 阶段 | 载体 | 职责 |
|------|------|------|
| A | 当前 Cursor Agent（IDE） | 扫描、确认、飞书、**仅建分支**（git fetch/checkout/push） |
| B | 本机 Cursor CLI `agent -p --force` | 改代码、lint、aicr-local CR 循环、commit、MR；**由 IDE Agent 在阶段A 结束后用 Shell 启动，不得只发脚本** |

- MR Token（阶段B）：优先 `GITLAB_TOKEN`，其次 `GITLAB_PRIVATE_TOKEN`
- **CLI 安装**：`which agent` 为空则阶段B `BLOCKED`，提示安装 Cursor CLI
- 详细脚本与提示词骨架：见 `references/CLI_HANDOFF.md`

## 能力复用

- 分支创建（阶段A）：**必须读取并执行** `../create-feature-branch/SKILL.md`（每个目标仓库 cwd 下）
- 代码审查（阶段B）：**必须读取并执行** `../aicr-local/SKILL.md`（暂存区模式，在 CLI 会话内）

## 参考文档

- `references/DETAILED_STEPS.md`
- `references/CLI_HANDOFF.md`
- `references/EXAMPLES.md`
- `references/TROUBLESHOOTING.md`
- `references/MR_TEMPLATE.md`
