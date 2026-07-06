# 改造 onsf-finish 实现自动归档 — 设计文档

## 1. 设计目标

让 `/onsf-finish` 在门禁通过后自动完成 OpenSpec 归档，同时保留严格的风险控制和清晰的降级路径。与 Trellis `/trellis:finish-work` 的自动归档行为对齐，但保持 OpenSpec 与 Trellis 的分工边界。

## 2. 改动范围

### 2.1 核心命令文档
- `plugins/onion-sdd/commands/onsf-finish.md`：重写完成标准和收尾行为，定义自动归档流程。

### 2.2 技能文档
- `plugins/onion-sdd/skills/mini-change/SKILL.md`：将「归档提示」改为自动归档。
- `plugins/onion-sdd/skills/verify-change/SKILL.md`：更新归档门禁说明，明确通过后自动归档。
- `plugins/onion-sdd/skills/auto-flow/SKILL.md`：将 `openspec archive` 从「必须停止」移除，允许自动归档。
- `plugins/onion-sdd/skills/full-change/SKILL.md`：更新完成标准中关于归档的描述。
- `plugins/onion-sdd/skills/external-spec/SKILL.md` 与 `pull-yapi/SKILL.md`：保留「冲突未裁决前不要进入归档」的约束，但明确归档由 `/onsf-finish` 自动执行。
- `plugins/onion-sdd/skills/trellis-adapter/SKILL.md`：更新 finish 时的同步时机，归档后把 `current.json` 切到 `idle`。

### 2.3 规则文档
- `plugins/onion-sdd/rules/onion-sdd.mdc`：移除「不自动执行 `openspec archive`」，改为「门禁通过后自动归档，失败时停止」。

### 2.4 其他说明文档
- `plugins/onion-sdd/commands/onsf-auto.md`、`onsf-fix.md`、`onsf-tweak.md`：同步更新。
- `plugins/onion-sdd/README.md`：更新自动化边界和当前不做。
- `plugins/onion-sdd/DESIGN-SUPPLEMENT.md`：更新流程描述。
- `plugins/onion-sdd/docs/feishu-wiki-onion-sdd-usage.md`：更新使用说明，移除「归档仍需你在终端执行」的说法。

## 3. 自动归档流程

```
/onsf-finish 触发
  │
  ▼
定位当前活跃 change
  │
  ▼
执行既有检查：
  - proposal.md / tasks.md / specs 完整性
  - 任务状态（已完成或明确标注不做）
  - 验证证据（Tier 0+/1 定向验证；Tier 2+ e2e-report.md 或等价验收）
  - 带债项评估（可接受 / 不可接受）
  - 外部 spec / YApi 差异是否已处理或记录
  │
  ├── 门禁未通过 ──→ 输出阻塞项，不执行归档，停止
  │
  ▼
门禁通过（或用户明确同意带债归档）
  │
  ▼
执行归档：
  1. 尝试 `openspec archive <change-id>`
     - 成功 ──→ 更新 current.json 为 idle，输出归档成功
     - 失败 ──→ 进入降级路径
  2. 降级路径：CLI 不可用时
     - 手工移动 `openspec/changes/<change-id>/` → `openspec/changes/archive/<YYYY-MM-DD>-<change-id>/`，命名方式与 OpenSpec CLI 归档一致。
     - 成功 ──→ 更新 current.json 为 idle，输出归档成功（降级模式）
     - 失败 ──→ 输出错误，保留 current.json，停止
  │
  ▼
若绑定 Trellis task，提示继续执行 `/trellis:finish-work`
```

## 4. CLI 检测与降级路径

### 4.1 检测方式
Agent 通过 `which openspec` 或执行 `openspec --version` 判断 CLI 是否可用。不可用时不视为 blocker，而是进入降级路径。

### 4.2 降级路径
- 确认 `openspec/changes/<change-id>/` 存在。
- 目标目录 `openspec/changes/archive/<YYYY-MM-DD>-<change-id>/` 不存在或为空（避免覆盖）。
- 使用文件系统移动（或复制后删除）完成等效归档。
- 如果目标目录已存在同名 change，停止并提示用户手动处理冲突。

### 4.3 失败处理
- 任何归档失败都不应回写 success 状态。
- 保留 `.onion-sdd/current.json` 中的 `active_change_id` 和 `phase=finish`，方便用户修复后重试 `/onsf-finish`。
- 输出包含：失败原因、建议的下一步命令、未损坏的现有产物路径。

## 5. 状态同步

归档成功后，`.onion-sdd/current.json` 更新为：

```json
{
  "version": 1,
  "active_change_id": null,
  "tier": null,
  "phase": "idle",
  "last_action": "OpenSpec change <change-id> 已自动归档",
  "last_action_at": "2026-07-06T14:15:00+08:00",
  "upgrade_risk": false,
  "trellis_task": null,
  "metrics": { ... }
}
```

若绑定 Trellis task，`trellis_task` 仍保留引用，便于 `/trellis:finish-work` 继续归档 task；但 `active_change_id` 置为 `null`。

## 6. 与 Trellis 的衔接

- `/onsf-finish` 只负责 OpenSpec 归档；Trellis task 归档仍由 `/trellis:finish-work` 完成。
- OpenSpec 归档成功后，输出中明确提示：
  > OpenSpec 归档完成。当前 change 绑定 Trellis task `<task>`，请继续执行 `/trellis:finish-work` 完成 task 归档。
- 如果 Trellis 不可用，输出中提示用户手动记录任务收尾。

## 7. 风险与回滚

| 风险 | 缓解措施 |
|------|----------|
| 自动归档未通过门禁的 change | 严格保留所有检查项，只有结论为「通过」才执行。带债归档必须用户明确同意。 |
| 用户未安装 OpenSpec CLI 导致归档失败 | 提供手工移动目录的降级路径；若降级也失败，停止并保留状态。 |
| 归档过程中工作区被其他并行修改污染 | 不自动提交 git commit；归档只操作 OpenSpec 目录，不依赖 git 状态。 |
| 多个文档/规则不一致 | 通过 Acceptance Criteria 清单统一检查，确保所有「不自动归档」声明被移除或更新。 |
| 与 `/onsf-auto` 的自动边界冲突 | 明确 `/onsf-auto`  finish-check 阶段可以自动归档，但不可逆操作（git commit、push、PR）仍然停止。 |

## 8. 兼容性

- 已有历史 change 目录结构保持不变。
- 已归档的 change 不受影响。
- 用户仍然可以手动执行 `openspec archive <change-id>`；自动归档是 `/onsf-finish` 的增强行为，不替代 CLI 命令。
