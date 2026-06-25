# 技术设计

## 决策

Adapter 第一版采用 **onion 插件内 skill + 文档协议**，不修改 `.trellis/scripts/**`。理由：

- `task.json.meta` 已是可扩展字段，可承载 onion metadata。
- `task.py create --parent` 已支持 Tier 3 parent/child 任务树。
- `add_session.py` 已支持 journal 写入。
- OpenSpec 正文仍由 `openspec/changes/<change-id>/` 管理，Trellis 不需要新增正文存储能力。

硬约束：整个 onion-sdd × Trellis 方案默认不改造 Trellis 源码或本仓库 `.trellis/scripts/**`。如果后续发现必须改 Trellis，必须先停止实现并与用户确认。

## 目标结构

```text
plugins/onion-sdd/
  skills/
    trellis-adapter/SKILL.md       # 新增：adapter 协议入口
  commands/
    onion-continue.md              # 更新：Trellis-aware 恢复优先级
  rules/
    onion-sdd.mdc                  # 更新：OpenSpec / Trellis 边界
  templates/
    current.example.json           # 更新：记录 trellis_task 字段示例
  README.md                        # 更新：adapter 使用方式和不做范围
  DESIGN-SUPPLEMENT.md             # 更新：字段映射表
```

## 数据边界

| 资产 | 角色 | 写入内容 |
| --- | --- | --- |
| `openspec/changes/<change-id>/` | 唯一变更正文 | proposal、specs、tasks、backend/qa/e2e |
| `.onion-sdd/current.json` | 轻量本地状态 | 当前 change、tier、phase、last_action、metrics、trellis_task |
| `.trellis/tasks/<task>/task.json` | 运行时 metadata | `meta.onion` 字段、parent/children、status |
| `.trellis/workspace/<dev>/journal-*.md` | 会话记忆 | last_action 摘要、提交、恢复提示 |

## 字段映射

`task.json.meta.onion` 建议结构：

```json
{
  "version": 1,
  "change_id": "add-invoice-export",
  "change_path": "openspec/changes/add-invoice-export",
  "tier": "2",
  "phase": "verify",
  "last_action": "qa spec 已接入，待执行 verify-change",
  "last_action_at": "2026-06-25T18:30:00+08:00",
  "upgrade_risk": false,
  "source_hashes": {
    "proposal": "sha256:...",
    "tasks": "sha256:...",
    "specs": "sha256:...",
    "backend": "sha256:...",
    "qa": "sha256:...",
    "e2e": "sha256:..."
  }
}
```

`.onion-sdd/current.json` 增加 `trellis_task` 字段：

```json
{
  "trellis_task": {
    "task_dir": ".trellis/tasks/06-25-add-invoice-export",
    "status": "in_progress"
  }
}
```

## 同步时机

| Onion 事件 | OpenSpec | Trellis |
| --- | --- | --- |
| Tier 判断完成 | change 策略确定 | 写 `meta.onion.tier` |
| OpenSpec 落盘 | proposal/specs/tasks | 写 `change_id`、`change_path`、phase |
| tasks 更新 | `tasks.md` | 更新 phase / last_action |
| 外部 spec 接入 | `backend-*.md` / `qa-*.md` | 更新 `source_hashes` |
| 验证完成 | `e2e-report.md` | phase = finish / verified |
| finish | 归档判断 | `add_session.py` 写 journal |

## 恢复优先级

`/onion-continue` 的恢复顺序：

1. Trellis active task：若 `task.json.meta.onion.change_id` 指向存在的 OpenSpec change，则使用它。
2. `.onion-sdd/current.json`：若 task 不存在或 stale，使用轻量状态。
3. OpenSpec fallback：扫描 `openspec/changes/**`，按产物推断阶段。

冲突处理：

- Trellis 与 current 指向不同 change：提示冲突，默认以 Trellis active task 为准；用户可指定 change-id 覆盖。
- Trellis 指向的 change 不存在：标记 stale，fallback 到 current/OpenSpec。
- current 指向的 task 不存在：忽略 `trellis_task`，但保留 change 恢复。

## Tier 3

Tier 3 使用 Trellis parent/child task tree：

- parent task 对应 parent OpenSpec change 或总览 change。
- 每个 child task 对应一个独立可归档 OpenSpec child change。
- child 的 `meta.onion.parent_change_id` 指回 parent。
- child 的 `CHARTER.md` / proposal 中说明依赖关系和独立归档条件。

## 回滚

- Adapter 协议失败时，删除或忽略 `meta.onion`，回到 `.onion-sdd/current.json` + OpenSpec fallback。
- 不修改 Trellis 核心脚本，因此不会影响普通 Trellis task 流。
- `source_hashes` 只用于提示 stale，不作为阻塞性真相源。
