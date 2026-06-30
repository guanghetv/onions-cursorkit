# 日志与 CLI 输出

## 输出通道

本仓库的脚本多为 CLI 工具，输出应区分：

- stdout：正常结果、可被用户阅读或脚本消费的信息。
- stderr：错误、警告、状态提示。

参考：
- `.trellis/scripts/common/task_store.py` 中创建任务、归档任务的 stderr 提示。
- `.trellis/scripts/common/safe_commit.py` 中 Git 忽略路径的 warning。
- `scripts/sync-guardrails.mjs` 中 `[sync-guardrails]` 前缀。

## 日志内容

应该记录：

- 操作对象：task 名称、插件名、文件路径、source 路径。
- 失败原因：JSON 解析失败、frontmatter 缺失、路径不存在、Git add 失败。
- 可恢复建议：下一步命令、应检查的配置、不要执行的危险命令。

不应该记录：

- 访问 token、MCP 凭证、私有 cookie。
- 大段文件正文。
- 无法行动的泛泛日志，例如“发生错误”但没有路径或字段。

## 脚本风格

Python 侧使用 `.trellis/scripts/common/log.py` 的 `colored` 和 `Colors` 时，保持提示简短。Node 侧可使用清晰前缀：

```js
const log = (msg) => console.log(`[sync-guardrails] ${msg}`);
const warn = (msg) => console.warn(`[sync-guardrails][warn] ${msg}`);
```

## 与 AI 协作

当脚本输出包含安全边界时，要写得足够具体，因为 AI 会读取日志并采取行动。例如 `safe_commit.py` 明确写了不要执行：

```text
Do NOT use `git add -f .trellis/`
```

新增类似防护时，必须给出具体反例和安全替代方案。
