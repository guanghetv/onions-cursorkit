## Why

Onion SDD 跨会话恢复依赖运行态，但此前 `.onion-sdd/current.json` / `meta.onion` 仅有协议、无可靠写入；`/onsf-finish` 门禁全靠 Agent 软检查。需要可执行 helper、finish 预检、0++ 超时可见，并收敛文档口径（用户只学 `/onsf-*`；Trellis 主写 + current 镜像/兜底）。

## What Changes

- 新增 `plugins/onion-sdd/scripts/onion_state.py`：统一读写运行态（读 meta→current；写有 task 主写 meta+镜像 current，否则只写 current）。
- 新增 `plugins/onion-sdd/scripts/finish_check.py`：归档前置预检（tasks / Tier2 e2e / 0++ 逾期为 hard；`openspec validate` 为 soft）。
- 扩展 `tier0pp_deadline` / `tier0pp_openspec_pending`；逾期未补档默认不可归档，除非 proposal 落盘 `## 带债项`。
- 接线 `/onsf-*`、skills、rules：阶段切换必须调 helper；finish 预检失败禁止 archive。
- 文档权威分层：README / USAGE / DESIGN / 飞书 wiki 对齐；删除「无自动写入」陈旧表述。
- 明确文档语言规范：`.trellis/spec/**`（含 guides）正文使用中文；并将既有英文 Thinking Guides 改为中文。

## Capabilities

### New Capabilities

- `onion-sdd-runtime-state`: 运行态 helper 与读写优先级契约。
- `onion-sdd-finish-precheck`: finish 可执行预检与 0++ 逾期门禁。

### Modified Capabilities

- Onion SDD 命令/skill 纪律：状态写入与 finish 归档前置。

## Impact

- `plugins/onion-sdd/scripts/**`（新增）
- `plugins/onion-sdd/commands/**`、`skills/**`、`rules/onion-sdd.mdc`、`templates/current.example.json`
- `plugins/onion-sdd/README.md`、`USAGE.md`、`DESIGN-SUPPLEMENT.md`、`docs/feishu-wiki-onion-sdd-usage.md`
- `.trellis/spec/backend/onion-sdd-runtime.md`（code-spec 沉淀）
- 不修改 Trellis 源码 / `.trellis/scripts/**`；无 Multica 交付
