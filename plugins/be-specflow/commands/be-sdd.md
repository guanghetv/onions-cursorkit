---
name: be-sdd
description: Spec-Driven 门禁：先澄清再落盘。新需求/多源输入时用，禁止跳过 brainstorming。
---

# /be-sdd — Spec-Driven 门禁

本命令激活后，**在本次对话中**你必须按下列顺序执行，**不得**抢跑。

## 必须做的事

1. **读取并遵循** `dev-workflow` 技能中**阶段 1**（设计探索）：仓库扫描 → 采集需求（**多源可组合**：飞书用 feishu-mcp；**GitLab Spec / 仓库内文档**：在**尚无** `openspec/changes/<change-id>/` 时用 `GITLAB_TOKEN`+API 或用户粘贴**只读**拉取正文，**不得**用 **`pull-spec` 落盘**——`pull-spec` 仅用于**已有**变更目录后的契约/QA 写入，见 `dev-workflow` 步骤 1b 与 `pull-spec`；截图/文字/本地文件统一承接；另有 **OpenAPI/Proto/gRPC** 等契约输入则读取并对齐；**不**使用 Figma 作为后端权威来源；MCP 或 token 不可用时须明确提示）→ 合并整理为「需求事实 + 范围边界」后再进入 brainstorming。
2. 需求事实整理完毕后，**必须**调用 **`superpowers:brainstorming`**，完成澄清、方案对齐与用户确认；不得用「先出一版」代替澄清。
3. Brainstorming 确认后，按 `dev-workflow` 执行 **步骤 1e 后端灰区讨论**（可跳过条件见该技能）；再按 **`design-to-opsx`** 落盘 OpenSpec（含 **`design.md` / `plan.md`**，结构与模板见该技能及 `dev-workflow` **强制纪律**阶段 1～2）。

## 在用户明确放行之前，禁止做的事

- 创建或修改 `openspec/changes/**` 下任何文件（含手工 `mkdir` / 写 `proposal.md` / `specs/**` / `design.md` / `plan.md`）
- 提示或代替用户执行 `openspec new change`（除非用户已放行，见下）
- 编写或修改业务功能代码（handler、service、repo、业务逻辑等）

**放行条件（宽松理解）**：用户用自然语言表示**同意进入下一阶段**即可，不必固定措辞。以下均视为放行（示例，非穷举）：

- 明确落盘类：可以落盘、进入 OpenSpec、可以 `design-to-opsx`、写 proposal、建变更目录
- 推进流程类：**继续下一步**、**开始执行**、往下走、接着做、进入下一阶段、可以开始了
- 确认类：确认、就这样、OK、没问题、按这个来、可以了

若语义模糊（例如只说「好」但上下文不清是指确认方案还是确认落盘），**先简短确认一句**再执行禁止项。

## 若用户只提供部分输入（如仅飞书链接）

先完成需求提取与 brainstorming，**不要**同时生成目录结构或代码骨架。用户若一次提供**多源**（飞书 + GitLab Spec + 截图 + 文字 + 本地文件 + 契约链接等），须**逐源采集**、合并为统一需求事实后再进入 brainstorming，**不得**遗漏用户给出的任一来源。
