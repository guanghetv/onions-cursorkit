---
name: trellis-adapter
description: 在不改造 Trellis 源码的前提下，同步 Onion SDD OpenSpec 状态、轻量 current 状态和 Trellis task metadata。
---

# Trellis Adapter

本技能用于 Onion SDD 与 Trellis task runtime 的状态同步。它只定义和执行插件侧协议：OpenSpec 保存正文，`.onion-sdd/current.json` 保存轻量恢复状态，Trellis task 保存 `meta.onion` metadata、parent/child 关系和 journal 摘要。

## 适用场景

- `/onsf-continue` 需要跨会话恢复当前 change。
- `/onsf-plan` 或 Tier 2+ 流程已创建 Trellis task，需要记录对应 OpenSpec change。
- 外部 spec、QA spec、E2E 报告到达后，需要标记 source hash 和 last action。
- Tier 3 需要将 parent/child change 映射到 Trellis parent/child task tree。

## 硬约束

- OpenSpec 是变更正文唯一真相源。
- 不复制 OpenSpec 正文到 `.trellis/tasks/**/prd.md`、`task.json` 或 journal。
- 不修改 Trellis 源码、`.trellis/scripts/**` 或 `.trellis/.runtime/**`。
- 如果发现必须改 Trellis 才能继续，停止当前实现并向用户确认。
- Trellis metadata 失败时不得阻塞 OpenSpec 正文恢复；回退到 `.onion-sdd/current.json` 和 OpenSpec fallback。

## 数据边界

| 资产 | 责任 | 可写内容 |
|------|------|----------|
| `openspec/changes/<change-id>/` | 变更正文 | `proposal.md`、`tasks.md`、`specs/**/spec.md`、`backend-*.md`、`qa-*.md`、`e2e-report.md` |
| `.onion-sdd/current.json` | 轻量本地状态 | active change、tier、phase、last action、metrics、trellis task 引用 |
| `.trellis/tasks/<task>/task.json` | Trellis runtime metadata | `meta.onion`、status、parent/children |
| `.trellis/workspace/<developer>/journal-*.md` | 会话记忆 | last action 摘要、恢复提示、验证结果摘要 |

Trellis task 的标准字段可承载通用运行态：

| 字段 | 使用方式 |
|------|----------|
| `branch` | feature 分支名；分支创建成功后优先通过 `task.py set-branch <task> <branch>` 写入 |
| `base_branch` | PR 目标分支；如团队有固定目标分支，使用 `task.py set-base-branch` |
| `parent` / `children` | Tier 3 parent/child 关系；使用 Trellis task tree，不在 onion-sdd 里另建依赖系统 |

## `task.json.meta.onion`

建议结构：

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

字段说明：

| 字段 | 来源 | 说明 |
|------|------|------|
| `version` | adapter | metadata 协议版本，当前为 `1` |
| `change_id` | OpenSpec | `openspec/changes/<change-id>` 的目录名 |
| `change_path` | OpenSpec | 相对仓库根目录的 change 路径 |
| `tier` | Onion triage | `0+`、`0++`、`1`、`2`、`3` |
| `phase` | Onion flow | `triage`、`discover`、`design`、`openspec`、`implement`、`integrate`、`verify`、`finish` |
| `last_action` | Onion command | 最近一次可恢复动作摘要 |
| `last_action_at` | Onion command | ISO 8601 时间戳，包含时区 |
| `upgrade_risk` | Onion triage | 是否发现升级红线 |
| `source_hashes` | OpenSpec files | 产物 hash，用于提示 stale，不作为正文真相源 |
| `parent_change_id` | Tier 3 child | 可选，指向 parent change |

`meta.onion` 只放 onion/OpenSpec 专有引用。不要把 `branch`、`base_branch`、任务状态或 parent/child 重复写进 `meta.onion`；这些使用 Trellis 标准字段。

## `.onion-sdd/current.json`

在 Phase 1 中继续保留轻量状态，并增加 `trellis_task` 引用：

```json
{
  "version": 1,
  "active_change_id": "add-invoice-export",
  "tier": "2",
  "phase": "verify",
  "last_action": "qa spec 已接入，待执行 verify-change",
  "last_action_at": "2026-06-25T18:30:00+08:00",
  "upgrade_risk": false,
  "trellis_task": {
    "task_dir": ".trellis/tasks/06-25-add-invoice-export",
    "status": "in_progress"
  }
}
```

`trellis_task` 只是恢复提示。若 task 不存在或已归档，忽略该字段，继续使用 `active_change_id` 和 OpenSpec 产物恢复。

没有活跃 change 时，允许使用空闲状态，避免 `/onsf-continue` 误恢复上一轮已完成变更：

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

## 同步时机

| 时机 | 写 OpenSpec | 写 current | 写 Trellis metadata / journal |
|------|-------------|------------|-------------------------------|
| Tier 判断完成 | 无或创建 change 前准备 | `tier`、`phase`、`upgrade_risk` | `meta.onion.tier`、`phase` |
| OpenSpec 落盘 | proposal/specs/tasks | `active_change_id`、`phase` | `change_id`、`change_path` |
| tasks 更新 | `tasks.md` | `last_action`、`phase` | `last_action`、`last_action_at` |
| 外部 spec 接入 | `backend-*.md` / `qa-*.md` | `phase=integrate` | `source_hashes.backend` / `source_hashes.qa` |
| 验证完成 | `e2e-report.md` | `phase=finish` | `source_hashes.e2e`、journal 摘要 |
| finish | 归档判断 | `metrics.finished_at` | journal 写恢复/归档摘要 |

## 恢复优先级

`/onsf-continue` 按以下顺序恢复：

1. Trellis active task：读取当前 task 的 `task.json.meta.onion.change_id`。如果 `change_path` 存在，则使用该 change。
2. `.onion-sdd/current.json`：当 Trellis task 缺失、stale 或没有 onion metadata 时，读取 `active_change_id`；若 `active_change_id` 为 `null` 或 `phase=idle`，表示无活跃 change，继续走 OpenSpec fallback。
3. OpenSpec fallback：扫描 `openspec/changes/**`，根据产物推断阶段；多个候选时列出并请用户选择。

冲突处理：

- Trellis 与 current 指向不同 change：提示冲突，默认以 Trellis active task 为准；用户明确指定 change-id 时用用户指定值。
- Trellis 指向的 OpenSpec change 不存在：标记 stale，fallback 到 current/OpenSpec。
- current 指向的 Trellis task 不存在：忽略 `trellis_task`，继续按 `active_change_id` 恢复。
- current 为 idle：不恢复上一轮 change，列出 OpenSpec 候选或请用户指定 change-id。
- `source_hashes` 与文件现状不一致：提示 stale，不自动覆盖正文。

## Tier 3 映射

- parent Trellis task 对应 parent OpenSpec change 或总览 change。
- child Trellis task 对应一个独立可归档 child change。
- child 的 `meta.onion.parent_change_id` 指向 parent。
- child 的 `CHARTER.md` 或 proposal 说明 parent、依赖 child 和独立归档条件。
- 使用 Trellis 现有 `task.py create --parent` 建立任务树；不新增 Trellis 脚本。

## 输出格式

执行同步或恢复判断后，输出：

```markdown
## Trellis Adapter 状态

- 恢复来源: <Trellis active task | current.json | OpenSpec fallback>
- change-id: <id>
- Trellis task: <task dir / 无>
- phase: <phase>
- stale: <无 / source_hashes 不一致 / task 指向缺失>
- 下一步: <读取哪个 onion skill 或等待用户确认>
```

## 回滚策略

- Adapter metadata 写坏或不可信时，忽略 `meta.onion`。
- 保留 OpenSpec change 目录，不删除正文产物。
- 保留 `.onion-sdd/current.json`，必要时手动清空 `trellis_task` 引用。
- 不通过 Trellis adapter 自动归档、自动提交或自动修改 `.trellis/scripts/**`。
