# 数据库与外部状态

## 当前事实

本仓库没有业务数据库、ORM、迁移系统或后端运行时数据表。不要为普通插件/规则开发臆造数据库规范。

实际存在的持久化形态是文件：

- `.cursor-plugin/marketplace.json`：插件市场索引。
- `plugins/*/.cursor-plugin/plugin.json`：插件 manifest。
- `.trellis/tasks/**/task.json`：任务元数据。
- `.trellis/workspace/<developer>/journal-*.md` 与 `index.md`：开发者 journal。
- 试点插件内的模板状态文件，例如 `plugins/onion-sdd/templates/current.example.json`。
- 业务仓运行态（由 onion-sdd 管理，非 Trellis 源码）：
  - `.onion-sdd/current.json`：无 Trellis 时的主写落点；有 Trellis 时为镜像/兜底。
  - `.trellis/tasks/**/task.json` 的 `meta.onion`：有绑定 task 时的主写落点。
  - 统一入口：`plugins/onion-sdd/scripts/onion_state.py`（契约见 [onion-sdd-runtime.md](./onion-sdd-runtime.md)）。

## JSON 文件规范

- JSON 必须能通过标准解析：
  ```bash
  python3 -m json.tool path/to/file.json
  ```
- 写入 JSON 时保持 UTF-8；需要保留中文时使用 `ensure_ascii=False`，参考 `.trellis/scripts/common/task_store.py` 中任务 JSONL seed 写法。
- 不要在 JSON 中加入注释；需要说明语义时放在旁边的 README 或 Markdown。
- 示例 JSON 文件可以使用真实字段但不要放真实 token、邮箱密钥或内部敏感数据。

## 任务与 journal 状态

Trellis 状态由 `.trellis/scripts/` 管理：

- 创建/归档任务通过 `.trellis/scripts/task.py`。
- 会话记录通过 `.trellis/scripts/add_session.py`。
- 上下文读取通过 `.trellis/scripts/get_context.py`。

不要手工移动任务目录来模拟归档；如果脚本因为 Git 权限失败，先检查 `git status`，再只补提交脚本已经移动的路径。

## 插件市场状态

`.cursor-plugin/marketplace.json` 使用 `metadata.pluginRoot: "plugins"`，每个 entry 的 `source` 是相对 `plugins/` 的目录名，例如：

```json
{
  "name": "workspace-specflow",
  "source": "workspace-specflow",
  "description": "Workspace 多角色协作工作流..."
}
```

新增正式插件时要同步 marketplace；试点隔离插件可以暂不注册，但 README 必须说明手动指定路径试用。

## 禁止事项

- 不要新增 SQLite/Postgres/MySQL 规范，除非仓库真的引入业务数据库。
- 不要把 `.trellis/.runtime/`、缓存、备份目录纳入提交。
- 不要把真实密钥、访问 token、MCP 凭证写入 manifest、README 或状态模板。
