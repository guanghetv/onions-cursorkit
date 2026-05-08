# 故障排查

## 问题1：未扫描到匹配项目

现象：
- 命中项目数为 0，流程被阻断。

排查建议：
- 检查需求描述是否包含模块名、页面名、关键文案片段。
- 补充需求上下文后重新执行 `/auto-dev`。
- 如有明确目标，可手动指定项目再触发。

## 问题2：MR 创建失败（Token 缺失）

现象：
- 阶段B（Cursor CLI）创建 MR 时进入 `BLOCKED`，提示缺少 Token。

排查建议：
- 检查本地是否已配置 `GITLAB_TOKEN` 或 `GITLAB_PRIVATE_TOKEN` 环境变量。
- 可在 `~/.zshrc` / `~/.bash_profile` 中添加：`export GITLAB_TOKEN=your_token_here`，然后重启终端。
- 若 Token 存在但 API 返回 401，检查 Token 是否具备 `api` 权限范围。

## 问题3：MR 创建失败（目标分支错误）

现象：
- MR 创建被拒绝或目标分支不是 `develop`。

排查建议：
- 检查 MR API 请求参数中的 target branch。
- 修正为 `develop` 后重试创建。
- 防止在脚本中使用默认分支回退逻辑。

## 问题4：CR 自动修复超过 3 轮

现象：
- 第 3 轮后仍存在 `Critical`。

排查建议：
- 查看阶段B 的 CLI 日志（如 `/tmp/auto-dev-*.cli.log`）定位问题。
- 本地修复后可在对应分支上手动提交，或修正需求后重新触发 `/auto-dev`。
- 若不属于小需求范围，改走常规开发流程。

## 问题5：IDE 内终端不停要求 Run / Allowlist

现象：
- 阶段A、B 拆分前，在 IDE Agent 内执行 `npm run lint` 等会反复弹出终端审批；或对 `agent`、`nohup` 单次弹窗。

排查建议：
- **按当前技能设计**：阶段A **不要**在 IDE 里跑 lint / 大批量改代码；交给阶段B Cursor CLI。
- 阶段B 应由 IDE Agent **Shell 启动** `agent`；若仅弹一次「允许执行」，点允许即可，**不应**改为让用户手动复制整段脚本。
- 若仍需在 IDE 下调试脚本，可参考 [permissions.json](https://cursor.com/docs/reference/permissions) 配置 `terminalAllowlist`，并启用「Auto-Run in Sandbox」（勿与团队策略冲突）。

## 问题6：Agent 只贴了 CLI 脚本，未用 Shell 启动

现象：
- 阶段A 完成后，回复里只有可复制 bash，没有实际执行 `agent`。

排查建议：
- 属 **违反 SKILL MUST**：应要求 Agent 重新按 `CLI_HANDOFF.md` 用 **Shell 执行**启动命令。
- 若模型反复只贴脚本，可在对话中明确引用 SKILL「阶段B 启动方式（硬性）」条文。

## 问题7：未提供飞书卡片链接且无分支名

现象：
- `/auto-dev` 在步骤0 输入校验阶段直接中断。

排查建议：
- 补充可访问的飞书卡片链接后重试；或
- 明确提供开发分支名（例如 `branch=feat/xxx`）后重试。
- 若提供了飞书链接但读取失败，先检查飞书权限或链接有效性。

## 问题8：阶段B 无法启动（`which agent` 为空）

现象：
- 阶段A 建分支成功，但阶段B 无法执行，提示未找到 `agent` 命令。

排查建议：
- 按 [Cursor CLI 安装](https://cursor.com/cn/docs/cli/headless) 安装并确保 `agent` 在 `PATH` 中（重开终端后重试）。
- 需要时配置 `CURSOR_API_KEY` 等环境变量（以官方文档为准）。
