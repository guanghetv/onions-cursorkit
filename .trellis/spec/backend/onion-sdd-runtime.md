# Onion SDD 运行态与 finish 预检

> 适用范围：`plugins/onion-sdd/scripts/**`、相关 commands/skills/rules，以及业务仓中的 `.onion-sdd/current.json` 与 Trellis `task.json.meta.onion`。

## 场景：onion-sdd 运行态 helper + finish 预检

### 1. 范围 / 触发

- 触发：改动 Onion SDD 跨会话恢复、阶段状态写入、`/onsf-finish` 归档门禁，或 `tier0pp_*` 字段。
- 本仓库无业务 DB；状态落在 JSON 文件。不修改 Trellis 源码 / `.trellis/scripts/**`。

### 2. 签名

```bash
# 仓库根执行；本仓开发路径：
SCRIPTS=plugins/onion-sdd/scripts
# 业务仓 marketplace 安装：以 Cursor 插件安装目录下的 scripts/ 为准

python3 "$SCRIPTS/onion_state.py" --repo-root . get
python3 "$SCRIPTS/onion_state.py" --repo-root . set \
  [--change-id ID] [--tier T] [--phase P] [--last-action TEXT] \
  [--trellis-task-dir PATH] [--idle] ...
python3 "$SCRIPTS/onion_state.py" --repo-root . bind-trellis --trellis-task-dir PATH
python3 "$SCRIPTS/onion_state.py" --repo-root . mark-tier0pp [--change-id ID] [--deadline ISO] [--deadline-hours N]
python3 "$SCRIPTS/onion_state.py" --repo-root . clear-tier0pp-pending [--change-id ID]

python3 "$SCRIPTS/finish_check.py" --repo-root . [--change-id ID] [--tier T] [--json]
```

环境：`ONION_SDD_ROOT` 可替代默认 `--repo-root .`。

### 3. 契约

#### 读 / 写优先级（设计决策）

| 方向 | 优先级 |
|------|--------|
| **读** | ① 已绑定且可信的 Trellis `meta.onion` → ② `.onion-sdd/current.json` → ③ OpenSpec 扫描（由 continue/auto 编排） |
| **写** | ① 已绑定 Trellis task：**主写** `meta.onion`，并**镜像** `current.json` → ② 无 Trellis / 未绑定：**只写** `current.json` |

`current.json` 在有 Trellis 时是镜像与降级兜底，不是主状态源。OpenSpec `openspec/changes/<id>/` 仍是变更**正文**唯一真相源。

#### `get` 输出关键字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `source` | `trellis` \| `current` \| `idle` | 读来源 |
| `active_change_id` | string \| null | 当前 change |
| `tier` / `phase` / `last_action` / `last_action_at` | … | 运行态 |
| `tier0pp_deadline` | ISO8601 \| null | 0++ 补档截止 |
| `tier0pp_openspec_pending` | bool | 是否仍待补 mini OpenSpec |
| `trellis_task` | object \| null | `{ task_dir, status? }` |

#### `set` / `mark-*` 结果关键字段

| 字段 | 说明 |
|------|------|
| `primary_write` | `trellis` \| `current` |
| `mirrored_current` | 主写 trellis 时是否已镜像 current |
| `warnings` | 如 meta 写失败已降级 |

#### finish_check hard / soft

| 级别 | 条件 |
|------|------|
| **Hard**（exit ≠ 0，禁止 archive） | 无 change-id/目录；`tasks.md` 未勾选且未命中豁免词；Tier 2+ 缺 `e2e-report.md` 或 `## 验收结论`；0++ `pending` 且已过 `deadline` 且 proposal 无 `## 带债项` |
| **Soft** | `openspec validate`：CLI 不可用则 skip；失败不单独导致 hard fail |

tasks 豁免词表（行内子串，大小写不敏感部分以实现为准）：`不做`、`won't do`、`cancelled`。

### 4. 校验与错误矩阵

| 条件 | 行为 |
|------|------|
| `--repo-root` 不存在 | exit 2，stderr 报错 |
| `get` 无状态 | exit 0，`source=idle` |
| meta 写失败（task 缺失/不可写） | 警告 + 降级只写 current，不阻塞 |
| finish 无 active change 且无 `--change-id` | hard fail |
| finish hard fail | exit ≠ 0；stdout 列 hard failures；**不得** archive |
| naive ISO deadline | 按本地时区补齐后再与 aware `now` 比较（避免 TypeError） |

### 5. 好 / 基线 / 坏用例

- **Good**：绑定 Trellis 后 `set` → `primary_write=trellis` 且 `mirrored_current=true`；`get` → `source=trellis`。
- **Base**：无 Trellis → 只写/读 `current.json`，`primary_write=current`。
- **Bad**：手写 JSON 绕过 helper（破坏写优先级）；`/onsf-finish` 不跑 `finish_check` 直接 archive；0++ 逾期无带债项仍归档。

### 6. 所需测试

- Fixture：仅 current 读写；bind + meta 主写镜像；meta 不可写降级。
- Fixture：finish pass；未完成 tasks fail；Tier2 缺 e2e fail；0++ 逾期 fail；有 `## 带债项` 放行。
- 无活跃 change 时 finish_check 明确报错，不误删文件。
- Assertion：`primary_write` / `source` / exit code / hard failure 文案。

### 7. 错误 vs 正确

#### 错误

```bash
# 手改 current.json，有 Trellis 时不同步 meta.onion
# /onsf-finish 直接 openspec archive，跳过 finish_check.py
```

#### 正确

```bash
python3 plugins/onion-sdd/scripts/onion_state.py --repo-root . set \
  --change-id demo --tier 2 --phase implement --last-action "tasks 2/5"
python3 plugins/onion-sdd/scripts/finish_check.py --repo-root . --change-id demo --tier 2
# exit 0 后再 openspec archive；成功后：
python3 plugins/onion-sdd/scripts/onion_state.py --repo-root . set --idle \
  --last-action "OpenSpec change demo 已自动归档"
```

## 设计决策：Trellis 主写 + current 镜像/兜底

**背景**：恢复协议早已是 meta → current → OpenSpec；若 helper 主写 current、可选 sync-meta，读/写优先级不一致。

**决策**：有绑定 task 时主写 `meta.onion` 并镜像 `current.json`；无 Trellis 只写 current。

**未采纳**：只写 meta（无 Trellis 会话恢复变差）；始终主写 current（与「优先用 Trellis」不符）。

## 约定：阶段切换必须调 helper

`/onsf-*` 与 `trellis-adapter` / `auto-flow` / `full-change` / `mini-change` 将阶段切换写成硬纪律；无 Cursor Hook。归档前必须 `finish_check.py`。

## 约定：提交前 AICR 与 trellis-check 分工

**What**：用户明确授权 `git commit` 后，先暂存目标文件，再审查最终暂存 diff。优先 `/cr`（`aicr-local`）；slash command 不可用时按该 Skill；未安装则 Agent 自审暂存区。修复后重新暂存并复审；暂存 diff 未变不重复审。

**Why**：`trellis-check` 负责实现后的 lint/typecheck/测试/Spec 与跨层；`aicr-local` 只审提交物。二者不互相替代。`/onsf-auto` 的 `diff-review` 不暂存、不调用 `/cr`。

**Related**：`plugins/onion-sdd/rules/onion-sdd.mdc`「提交前审查」；`plugins/common/skills/aicr-local/`。

## 陷阱

> **警告**：Agent 漏调 `onion_state.py` 时，中间阶段状态可能 stale；finish 预检只能兜底归档门禁，不能自动补写历史 phase。
>
> **警告**：tasks「不做」靠词表子串匹配，措辞含「不做」可能误放行；未用词表词可能误拦截——以预检列出的未完成项人工确认。

## 相关文件

- `plugins/onion-sdd/scripts/onion_state.py`
- `plugins/onion-sdd/scripts/finish_check.py`
- `plugins/onion-sdd/skills/trellis-adapter/SKILL.md`
- `plugins/onion-sdd/commands/onsf-finish.md`
- `plugins/onion-sdd/templates/current.example.json`
