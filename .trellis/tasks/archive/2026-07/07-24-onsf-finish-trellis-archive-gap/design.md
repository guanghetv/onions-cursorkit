# Design

## 方案概览

两个独立交付物，同一任务、同一发版（0.1.3）：

| 交付物 | 改动文件 | 性质 |
|--------|----------|------|
| A: Branch B 提醒强化 | `commands/onsf-finish.md` | command 输出规则，纯文档/行为 |
| B: stale-task 诊断 | `scripts/finish_check.py` | 归档预检新增非致命 WARN |
| 发版 | `CHANGELOG.md`、`.cursor-plugin/plugin.json` | 版本号 |

## A: Branch B 自动归档 Trellis task（返工：原 0.1.3 仅提醒，现改为自动归档）

### 流程顺序变更（根因修复）

旧顺序：`/onsf-finish`（归档 OpenSpec）→ 代码 commit → `/trellis:finish-work`（归档 Trellis task）。两个 finish 夹着一次 commit，故分离。

新顺序：**代码 commit（Phase 3.4）→ `/onsf-finish`（单命令归档两边）**。commit 前置后，`/onsf-finish` 末尾工作区已干净，可一并归档 Trellis task。

### Branch B 新执行序列

1. `finish_check.py`（现有预检，gate）。
2. **工作区干净检查**：`git status --porcelain`，过滤 `.trellis/workspace/`、`.trellis/tasks/`；若仍有脏路径 → bail：「工作区有未提交的本任务代码，先 commit 再跑 `/onsf-finish`」，**不归档任何东西**。
3. `openspec archive <change-id>`（CLI 不可用则手工移动），产生未提交的目录移动。
4. **自动 commit openspec 归档移动**（scoped）：`git add openspec/changes/` + `git commit -m "chore: archive openspec change <change-id>"`。这是 scoped chore 提交（纯文件移动，非代码），与 `task.py archive` / `add_session.py` 的 auto-commit 同性质，不走 AICR。
5. `onion_state.py set --idle`。
6. **委托 `trellis-finish-work` skill**：此时工作区干净（仅步骤 4 的 commit）→ 该 skill 执行 `task.py archive <bound-task>`（auto-commit）+ `add_session.py`（auto-commit journal）。
7. 输出：OpenSpec change 与 Trellis task 均已归档、均已提交；给出最终 commit 序列。

### 约束放宽

`onsf-finish.md` 原「不自动提交 git commit」放宽为：**仅自动提交 openspec 归档移动这一项 scoped chore**；代码 commit 仍由 Phase 3.4 在 `/onsf-finish` 之前完成；不自动 push/PR。

### 边界

- Branch A（无 Trellis）：不变。
- Branch C（未绑定 task）：不变（本就自做 add_session + spec 判断）。
- `/trellis:finish-work` 仍保留，供**纯 Trellis 任务**（无 OpenSpec change）使用；onion-sdd bound change 不再需要它。
- B（stale 诊断）保留为兜底：防纯 Trellis 任务漏归档，以及历史遗留 task 被发现。

### 回滚点

- 出问题：把 Branch B 步骤 3-6 换回「只 OpenSpec 归档 + 建议跑 /trellis:finish-work」即恢复 0.1.3 行为。

## B: stale-task 诊断

### 机制（check_stale_trellis_tasks）

新增 `check_stale_trellis_tasks(repo_root) -> List[str]`，在 `run_check` 末尾（与 convention WARN 同位）调用，结果进 `notes`，不改 exit code。

算法：

1. `tasks_dir = repo_root / ".trellis" / "tasks"`；非目录 → 返回 `[]`（无 Trellis，不诊断）。
2. 遍历 `tasks_dir/*` 的直接子目录（每个一个 task），读 `<dir>/task.json`：
   - `status` 必须为 `in_progress`，否则跳过。
   - 读 `meta.onion.change_id`（缺/非 dict → 跳过：无 onion 绑定，不判 stale）。
3. 对每个候选，判 bound change 是否已归档/缺失：
   - 活跃 change 目录：`openspec/changes/<change_id>/` 存在且**不在** `archive/` 下 → 非 stale。
   - 已归档：`openspec/changes/archive/<date>-<change_id>/` 存在，或 `openspec/changes/<change_id>/` 不存在 → stale。
4. stale 则输出 WARN：
   `WARN: Trellis task <task-dir-name> 仍为 in_progress，但其 bound OpenSpec change <change_id> 已归档/缺失，建议执行 /trellis:finish-work 清理`

### 数据访问边界

- 只读 `.trellis/tasks/*/task.json` 与 `openspec/changes/**` 目录结构；不读 change 正文，不改 `.trellis/scripts/**`。
- 复用 finish_check 现有 `load_json`（已在 onion_state 中，finish_check 已 import onion_state）读 task.json。
- 不依赖 `task.py list` 输出格式（直接扫目录 + 读 JSON），更稳。

### 误报控制

- 仅 `status=in_progress` 且有 `meta.onion.change_id` 才判；无绑定（Branch C 类）不报。
- 已归档判定收窄到「change 目录不存在」或「只在 archive/ 下」；活跃 change 存在不报。
- WARN 非 fatal，即便误报也不阻塞。

### 与现有检查正交

- hard_failures / soft / convention WARN / stale WARN 互不耦合；stale WARN 只 append 到 notes。
- 无 Trellis（`.trellis/` 缺失）→ 直接返回 `[]`，零开销零误报。

## 发版 0.1.3

- CHANGELOG：`[Unreleased]` 下新增 `[0.1.3] - <date>`，Added 记 A/B。
- plugin.json：version `0.1.2` → `0.1.3`。
- marketplace.json：不动。

## 风险

- stale WARN 扫描所有 task 目录：task 数量大时有轻微开销，但仅读 JSON + 目录存在性，可忽略。
- 误报：收窄到 in_progress + 有 change_id + change 已归档/缺失三重条件，且非 fatal，风险可控。
- 不改 Trellis 脚本，无跨系统副作用。
