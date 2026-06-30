# 后端与工具脚本开发规范

> 本目录面向本仓库中的后端规则资产、Trellis Python 脚本和 Node 校验/同步脚本。这里的“backend”不是业务服务仓库，也没有真实数据库运行时。

## 适用范围

- `.trellis/scripts/**`：Trellis 任务、上下文、journal、归档等 Python 脚本。
- `scripts/*.mjs`：插件市场校验、guardrails 同步等 Node 工具。
- `plugins/backend/**`、`plugins/be-specflow/**`、`plugins/go-cutover-suite/**`：后端相关 Cursor 插件资产。
- `install/**`：安装与同步脚本。

## 指南索引

| 指南 | 内容 | 状态 |
|------|------|------|
| [目录结构](./directory-structure.md) | 工具脚本、插件资产、安装脚本的边界 | 已填充 |
| [数据库与外部状态](./database-guidelines.md) | 本仓库无数据库；如何处理 JSON 状态和文件型数据 | 已填充 |
| [错误处理](./error-handling.md) | Python/Node/规则文档中的错误表达 | 已填充 |
| [质量规范](./quality-guidelines.md) | 校验、提交范围、同步产物和审查要求 | 已填充 |
| [日志规范](./logging-guidelines.md) | CLI 输出、stderr、警告与敏感信息 | 已填充 |

## 开发前检查清单

- 先确认改动类型：Trellis Python 脚本、Node 工具、插件规则资产，还是纯文档。
- 涉及插件市场结构时，阅读 `docs/add-a-plugin.md` 与 `scripts/validate-template.mjs`。
- 涉及 Trellis 自动提交、任务归档、journal 时，阅读 `.trellis/scripts/common/safe_commit.py`，不要扩大 Git staging 范围。
- 修改同步产物前先判断是否来自 `scripts/sync-guardrails.mjs` 管理；同步产物应回源修改，而不是在本仓库手改。

## 质量检查

本仓库没有统一 `package.json` 脚本。按改动选择验证：

```bash
node scripts/validate-template.mjs
python3 ./.trellis/scripts/get_context.py --mode record
python3 ./.trellis/scripts/task.py list
```

如果只改未注册的试点插件，可做局部检查：

```bash
python3 -m json.tool plugins/<plugin>/.cursor-plugin/plugin.json
rg -n "name:|description:" plugins/<plugin>/commands plugins/<plugin>/skills plugins/<plugin>/rules
```

## 语言

面向团队和 AI 的规范、README、命令说明默认使用中文；代码标识、文件路径、命令和专有名词保留英文。
