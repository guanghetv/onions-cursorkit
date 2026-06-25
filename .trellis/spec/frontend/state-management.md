# 状态管理

## 状态来源

本仓库没有前端全局状态库。状态主要来自文件和工作流产物：

| 状态 | 路径 | 管理方式 |
|------|------|----------|
| 插件市场 | `.cursor-plugin/marketplace.json` | 手工维护，正式插件需注册 |
| 插件 manifest | `plugins/*/.cursor-plugin/plugin.json` | 插件内维护 |
| OpenSpec 变更 | `openspec/changes/**` | OpenSpec CLI + Agent 写 Markdown |
| Trellis 任务 | `.trellis/tasks/**/task.json` | `.trellis/scripts/task.py` |
| Trellis journal | `.trellis/workspace/<developer>/journal-*.md` | `.trellis/scripts/add_session.py` |
| 轻量试点状态 | 如 `.onion-sdd/current.json` 模板 | 插件命令约定维护 |

## OpenSpec 状态

OpenSpec 变更目录是需求/设计/验证状态的主要载体。命令或 skill 如果需要恢复状态，应优先读取：

- `proposal.md`
- `tasks.md`
- `specs/**/spec.md`
- `backend-*.md`
- `qa-*.md`
- `e2e-report.md`

不要把 OpenSpec 产物写到变更目录之外。

## Trellis 状态

Trellis 状态由脚本管理，不要手动编辑 runtime 指针：

- 查看上下文：`python3 ./.trellis/scripts/get_context.py`
- 设置当前任务：`python3 ./.trellis/scripts/task.py start <task>`
- 完成当前任务：`python3 ./.trellis/scripts/task.py finish`
- 归档任务：`python3 ./.trellis/scripts/task.py archive <task>`

如果只是插件自身状态，优先设计插件目录内的模板或说明；不要让插件命令直接依赖 Trellis runtime，除非任务明确是 Trellis 集成。

## Onion SDD Trellis Adapter

### 1. Scope / Trigger

- Trigger: 修改 `plugins/onion-sdd/**` 中涉及 Trellis 恢复、OpenSpec change 状态或 `.onion-sdd/current.json` 的能力。
- Scope: 只允许通过 onion 插件内 skill、command、rule、README 和模板定义 adapter 协议。

### 2. Signatures

- Skill: `plugins/onion-sdd/skills/trellis-adapter/SKILL.md`
- Lightweight state: `.onion-sdd/current.json`
- Trellis metadata field: `.trellis/tasks/<task>/task.json` 的 `meta.onion`

### 3. Contracts

`meta.onion` 只保存 metadata，不保存正文：

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
    "specs": "sha256:..."
  }
}
```

`.onion-sdd/current.json` 可以增加 `trellis_task` 引用：

```json
{
  "trellis_task": {
    "task_dir": ".trellis/tasks/06-25-add-invoice-export",
    "status": "in_progress"
  }
}
```

没有活跃 change 时，使用 idle 状态，不能继续指向已完成或已归档的变更：

```json
{
  "version": 1,
  "active_change_id": null,
  "tier": null,
  "phase": "idle",
  "last_action": "当前无活跃 Onion change",
  "last_action_at": "2026-06-25T18:30:00+08:00",
  "upgrade_risk": false,
  "trellis_task": null
}
```

### 4. Validation & Error Matrix

| 条件 | 行为 |
|------|------|
| Trellis active task 有有效 `meta.onion.change_id` | `/onion-continue` 优先使用该 change |
| Trellis task 指向的 OpenSpec change 不存在 | 标记 stale，fallback 到 `.onion-sdd/current.json` |
| `.onion-sdd/current.json` 指向的 task 不存在 | 忽略 `trellis_task`，保留 `active_change_id` 恢复 |
| `.onion-sdd/current.json` 的 `active_change_id` 为 `null` 或 `phase=idle` | 视为无活跃 change，不恢复上一轮已完成变更，进入 OpenSpec fallback 或请用户指定 change-id |
| `source_hashes` 与文件现状不一致 | 提示 stale，不覆盖 OpenSpec 正文 |
| 需要改 Trellis 源码或 `.trellis/scripts/**` | 停止并向用户确认，不直接实施 |

### 5. Good/Base/Bad Cases

- Good: `OpenSpec proposal/specs/tasks` 保存正文，`meta.onion` 只保存 `change_id`、phase、hash 和摘要。
- Base: 没有 Trellis task metadata 时，用 `.onion-sdd/current.json` 和 OpenSpec fallback 继续。
- Base: 当前没有活跃 change 时，`.onion-sdd/current.json` 使用 `active_change_id: null` 与 `phase: "idle"`。
- Bad: 将 OpenSpec 正文复制到 Trellis task PRD、JSONL、journal 或修改 `.trellis/scripts/**` 来支持 onion-sdd。

### 6. Tests Required

- `python3 -m json.tool plugins/onion-sdd/templates/current.example.json`
- `rg -n "trellis-adapter|meta.onion|trellis_task|source_hashes" plugins/onion-sdd`
- `rg -n "OpenSpec 是变更正文唯一真相源|不复制 OpenSpec 正文" plugins/onion-sdd`
- `rg -n "不做 Trellis adapter|不读写 Trellis workflow-state" plugins/onion-sdd`
- `node scripts/validate-template.mjs`

### 7. Wrong vs Correct

Wrong:

```text
为 onion-sdd adapter 修改 .trellis/scripts/task.py，或把 proposal.md 全文复制进 task.json。
```

Correct:

```text
在 plugins/onion-sdd/skills/trellis-adapter/SKILL.md 定义协议，只在 task.json.meta.onion 保存引用、phase、hash 和摘要。
```

## Metrics 与记录

度量字段可以放入状态 JSON 或验证报告，但 Phase 0 这类试点不应依赖外部指标平台。示例见 `plugins/onion-sdd/templates/current.example.json`。

## 常见错误

- 直接手改 `.trellis/.runtime/`。
- 将运行时状态写入 README 而没有模板或字段说明。
- 在未归档 OpenSpec 变更时跳过 `tasks.md` / `e2e-report.md` 的检查。
