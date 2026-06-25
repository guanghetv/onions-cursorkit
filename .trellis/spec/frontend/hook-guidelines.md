# Hooks 与自动注入

## 当前事实

本仓库没有 React hooks。这里的 hook 指 Cursor/Trellis 的上下文注入和自动化脚本。

相关路径：

- `.cursor/hooks.json`
- `.cursor/hooks/*.py`
- `.cursor/commands/trellis-*.md`
- `.cursor/skills/trellis-*/SKILL.md`
- `.trellis/scripts/hooks/*.py`

## Cursor hooks

Cursor hooks 负责在会话或子代理运行时注入 Trellis 上下文。修改时必须保持平台中立：

- 不要依赖单一绝对路径。
- 不要把用户私有环境写死到 hook。
- 输出应可被 AI/用户理解，避免隐式失败。

参考：
- `.cursor/hooks/inject-shell-session-context.py`
- `.cursor/hooks/inject-subagent-context.py`
- `.cursor/hooks/session-start.py`

## Trellis hooks

`.trellis/scripts/task.py` 会在任务 start/finish/archive 等节点调用 hook。新增 hook 行为时：

- 保持幂等。
- 失败时给出清晰错误，不要破坏任务文件。
- 不要自动 stage 整个 `.trellis/`。

参考：
- `.trellis/scripts/task.py`
- `.trellis/scripts/hooks/linear_sync.py`

## 命令与技能同步

`.agents/skills/`、`.cursor/skills/`、`.codex/skills/` 等目录可能承载同一 Trellis skill 的不同平台副本。改 Trellis skill 时要确认目标平台目录，不要只改一个副本后假设所有平台生效。

## 常见错误

- 把 React hook 规范写进本仓库 spec。
- 修改 hook 后没有验证 `python3 ./.trellis/scripts/get_context.py`。
- 在 hook 中输出过多噪音，干扰 AI 上下文。
