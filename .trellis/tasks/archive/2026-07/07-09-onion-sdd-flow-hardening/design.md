# Design: onion-sdd flow hardening

## Overview

在 `plugins/onion-sdd` 内补齐「可执行薄运行时」：状态 helper + finish 预检，并把 0++ deadline 与文档权威分层接到现有 `/onsf-*` 命令与 skills。不改 Trellis 源码，不引入 Hook，不做 Multica。

## Boundaries

| In | Out |
|----|-----|
| `plugins/onion-sdd/scripts/**` 新脚本 | Trellis `.trellis/scripts/**` / 源码 |
| `templates/current.example.json` 字段扩展 | Cursor Hook |
| commands / skills / rules / README / USAGE / DESIGN / feishu wiki 关键点 | Multica、metrics 聚合、0++ 周频审计 |
| Agent 调用脚本的硬纪律 | 自动 git commit / `--force` archive |

## Contracts

### 1. 状态 helper（建议：`scripts/onion_state.py`）

职责：按「Trellis 优先、current.json 镜像/兜底」统一读写运行态。不改 Trellis 源码，只读写 `task.json.meta.onion` 与 `.onion-sdd/current.json`。

#### 读 / 写优先级

| 方向 | 优先级 |
|------|--------|
| **读** | ① 已绑定且可信的 Trellis active task `meta.onion` → ② `.onion-sdd/current.json` → ③ OpenSpec 扫描（由 continue/auto 编排，helper `get` 覆盖 ①②） |
| **写** | ① 已绑定 Trellis task：**主写** `meta.onion`，并**镜像** `current.json` → ② 无 Trellis / 未绑定：**只写** `current.json` |

`current.json` 在有 Trellis 时是镜像与降级兜底，不是主状态源。

建议子命令：

| 子命令 | 行为 |
|--------|------|
| `get` | 按读优先级合并输出状态（JSON），并标注 `source: trellis \| current \| idle`；缺失时 exit 0 + idle 语义 |
| `set` | 按写优先级落盘（`--change-id`、`--tier`、`--phase`、`--last-action`、`--upgrade-risk`、`--trellis-task-dir`、`--idle` 等）；有 task 则主写 meta + 镜像 current |
| `bind-trellis` | 记录/更新 `trellis_task.task_dir` 绑定，便于后续主写 meta |
| `mark-tier0pp` | 设置 `tier: "0++"`，写入 `tier0pp_deadline`（默认 now+24h），`tier0pp_openspec_pending: true`（同样走写优先级） |
| `clear-tier0pp-pending` | 补档完成后清除 pending（保留 deadline 历史可选） |

字段扩展（`current.json` / example / `meta.onion` 对齐）：

```json
{
  "tier0pp_deadline": "2026-07-10T12:00:00+08:00",
  "tier0pp_openspec_pending": true
}
```

规则：

- OpenSpec 正文唯一真相源；helper 只写引用与阶段 hint。
- 不创建/启动/归档 Trellis task；只更新已存在 task 的 `meta.onion`。
- `set --idle`：清空 active（meta 与/或 current 同步），`phase=idle`，清理 pending 语义（归档成功路径使用）。
- meta 写失败（task 不存在/不可写）：警告并降级为只写 `current.json`，不阻塞流程。
- 写 `current.json` 前确保 `.onion-sdd/` 存在；原子写（写临时文件再 replace）优先。

### 2. finish 预检（建议：`scripts/finish_check.py`）

输入：`--change-id`，或按读优先级从 `meta.onion` / `current.json` 解析 `active_change_id`；可选 `--tier`（否则从状态 / proposal 推断）。

Hard fail（exit ≠ 0，禁止 archive）：

1. 找不到 change 目录。
2. `tasks.md` 存在未勾选项，且该项未标注「不做」类豁免（约定：行内含 `不做` / `won't do` / `cancelled` 等，实现时定一份小词表）。
3. Tier 2+：缺少 `e2e-report.md`，或缺少 `## 验收结论` 标题。
4. Tier 0++ 且 `tier0pp_openspec_pending` 仍为 true，且当前时间 > `tier0pp_deadline`，且 `proposal.md` **没有**可接受的 `## 带债项` 章节（转 follow-up 例外必须落盘）。

Soft（报告中标明，不单独导致失败）：

- `openspec validate`：CLI 可用则执行并记录结果；不可用则 `skipped: openspec CLI unavailable`。

输出：stdout 人类可读摘要 + 可选 `--json` 机器可读；exit 0 仅当无 hard fail。

`/onsf-finish` 纪律：必须先跑预检；非 0 则停止，不调用 `openspec archive`，不手工移动归档目录。

### 3. 0++ 生命周期

```text
判定 0++ → mark-tier0pp（deadline=now+24h, pending=true）
  → 先修后补
  → 补 mini OpenSpec 后 clear-tier0pp-pending
  → 正常 finish_check → archive

若逾期仍 pending：
  plan/continue/fix/auto-recover → 硬提示
  finish_check → hard fail
  例外：proposal 已有 ## 带债项（follow-up）→ hard 解除该条，可走带债归档（仍须用户在对话中同意带债，与现有 onsf-finish 一致）
```

「已补 mini OpenSpec」判定：pending 已 clear，或 change 目录存在合格 mini `proposal.md`+`tasks.md` 且 Agent 调用 `clear-tier0pp-pending`。预检以 **pending 标志 + deadline + 带债项** 为主，避免对 proposal 质量做 NLP。

### 4. Skill / 命令接线

必须更新（硬纪律 + 调用示例）：

- `skills/trellis-adapter/SKILL.md`：同步时机改为「必须调用 helper」；删除「不保证写入」。
- `rules/onion-sdd.mdc`：状态写入与 finish 预检门禁。
- `commands/onsf-finish.md`：预检为归档前置。
- `commands/onsf-continue.md` / `onsf-plan.md` / `onsf-fix.md` / `onsf-auto.md`：阶段切换写状态；0++ 逾期扫描。
- `skills/auto-flow/SKILL.md`、`full-change/SKILL.md`、`mini-change/SKILL.md`：阶段结束调用 `onion_state.py`。
- `templates/current.example.json`：新字段示例。

### 5. 文档权威分层

| 文档 | 角色 |
|------|------|
| `skills/tier-triage/SKILL.md` | Tier 判定唯一权威 |
| `README.md` | 能力清单、脚本入口、协议索引 |
| `USAGE.md` | 用户主路径：只教 `/onsf-*`；Trellis 为附录 |
| `DESIGN-SUPPLEMENT.md` | 标「已实现 / 未做」；去掉与现状矛盾的 Phase 0 口吻 |
| `docs/feishu-wiki-onion-sdd-usage.md` | 与 USAGE 关键点对齐 |

不把 auto/手动差异写成缺陷。

## Data flow

```text
/onsf-* 阶段切换
  → onion_state.py set|mark-tier0pp|...
       ├─ 有绑定 Trellis task → 主写 meta.onion + 镜像 current.json
       └─ 无 Trellis / 未绑定 → 只写 current.json
  → OpenSpec 正文仍只在 openspec/changes/<id>/

/onsf-continue|auto recover
  → onion_state.py get（source=trellis|current|idle）
  → 再必要时 OpenSpec 扫描

/onsf-finish
  → finish_check.py（读优先级同 get）
  → pass → openspec archive → onion_state.py set --idle
  → fail → stop
```

## Compatibility & rollout

- 无 Trellis、无 `current.json`：`get` 返回 idle；continue 仍可 OpenSpec fallback；首次 `set` 创建 `current.json`。
- 有 Trellis 无 `current.json`：主写 meta 时一并创建镜像 `current.json`。
- 旧 `current.json` / 旧 `meta.onion` 无 0++ 字段：视为非 pending，不误伤存量 change。
- meta 与 current 冲突：读以 Trellis 为准（与现有 continue 协议一致）；写以本次 `set` 为准并镜像对齐。
- 脚本用 Python 3 stdlib only，与仓库现有 `python3 ./.trellis/scripts/*` 习惯一致。
- 插件内路径：Agent 从业务仓库根调用时，需能定位脚本（文档写清相对 `plugins/onion-sdd/scripts/` 或经 symlink/拷贝策略——**推荐文档约定：业务仓若以 marketplace 安装插件，脚本路径以 Cursor 插件安装目录为准；cursorkit 本仓开发时用 `plugins/onion-sdd/scripts/`**）。设计实现时在 README 给一条探测/调用约定，避免写死绝对路径。

## Rollback

- 删除或停用 `scripts/` 调用纪律即可回退到纯文档协议；OpenSpec 正文不受影响。
- 字段向前兼容：忽略未知字段即可。

## Risks

- Agent 仍可能忘记调脚本 → 用 rules + 各 command 步骤清单 + finish 预检兜底（至少归档前能拦住）。
- 「不做」词表误判 → 词表保守 + 预检输出未完成项列表供人工确认。
- 插件安装路径不一致 → README 明确调用约定与开发/安装两种路径。
