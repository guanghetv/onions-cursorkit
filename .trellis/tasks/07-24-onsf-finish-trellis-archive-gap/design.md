# Design

## 方案概览

两个独立交付物，同一任务、同一发版（0.1.3）：

| 交付物 | 改动文件 | 性质 |
|--------|----------|------|
| A: Branch B 提醒强化 | `commands/onsf-finish.md` | command 输出规则，纯文档/行为 |
| B: stale-task 诊断 | `scripts/finish_check.py` | 归档预检新增非致命 WARN |
| 发版 | `CHANGELOG.md`、`.cursor-plugin/plugin.json` | 版本号 |

## A: Branch B 提醒强化

### 现状

`onsf-finish.md` 分支 B 现写法：「保持现状，输出中给出两段建议 … 2. Trellis：若代码提交完成且工作区干净，提示继续执行 `/trellis:finish-work`」。是「建议」，可被忽略；且未约束「未提示不得宣称完成」。

### 改动

在 Branch B 段补「输出必选项」硬规则：

- OpenSpec 归档成功后，输出**必须**含一条 `Trellis 收尾待办` 行，格式如：
  `- Trellis 收尾待办: task <task-dir> 仍为 in_progress，请执行 /trellis:finish-work 归档（含 task archive 与 journal）`
- 该行为收尾结论必选项：未输出不得在结论宣称「全部完成/已归档」；带债归档同样适用。
- 仍**不**在 `/onsf-finish` 内调用 `/trellis:finish-work`（保留其 Step 2 提交 sanity 门禁）。

### 边界

- Branch A（无 Trellis）/ Branch C（未绑定 task）不变：A 不涉及 Trellis；C 本就无 bound task 可归档。
- 与 B 的 stale WARN 互补：A 提醒「当前 bound task 别忘」，B 提醒「历史遗留 task 该清」。

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
