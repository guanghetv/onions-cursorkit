# 错误处理

## Python CLI 脚本

Trellis Python 脚本采用“返回退出码 + stderr/彩色提示”的 CLI 风格。

参考：
- `.trellis/scripts/task.py`
- `.trellis/scripts/common/task_store.py`
- `.trellis/scripts/common/safe_commit.py`

约定：

- 参数缺失或无法解析时打印明确错误并返回非零退出码。
- 用户可恢复的问题用提示和 hint 说明下一步，例如 task 不存在时提示可用 task name 或完整路径。
- 写 Git 索引、自动提交等失败时不得吞掉错误；要输出失败原因并要求用户检查 `git status`。
- 不要用裸 `except:` 静默失败；只有明确的降级路径才可以捕获后继续。

示例模式：

```python
if not full_path.is_dir():
    print(colored(f"Error: Task not found: {task_input}", Colors.RED))
    print("Hint: Use task name or full path")
    return 1
```

## Node 校验/同步脚本

`scripts/validate-template.mjs` 使用集中收集 `errors` / `warnings` 的方式，最后统一输出并 `process.exit(1)`。

新增校验规则时遵循：

- 能继续检查就继续收集错误，避免只报第一个问题。
- 错误信息必须包含插件名、字段名或相对路径。
- 警告用于可选能力缺失，例如无 `hooks/hooks.json` 或 `mcp.json`。

`scripts/sync-guardrails.mjs` 遇到上游格式不符合要求时应 fail fast，避免生成半正确的同步产物。

## 插件文档中的错误处理

commands/skills 里描述失败路径时，要写清：

- 何时停止当前流程。
- 是否需要升级到更重流程。
- 哪些验证失败会阻断归档。
- 哪些问题可以记录为带债项。

参考：
- `plugins/onion-sdd/commands/onion-finish.md`
- `plugins/onion-sdd/skills/tier-triage/SKILL.md`

## 常见错误

- 不要把所有失败都写成“请重试”；要说明原因和恢复方式。
- 不要在脚本里自动使用危险补救命令，例如 `git add -f .trellis/`。
- 不要把本应阻断的校验失败降级成 warning。
