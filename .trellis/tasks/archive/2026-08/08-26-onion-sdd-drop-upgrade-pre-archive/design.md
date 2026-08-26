# Design: onion-sdd 去掉升级推荐 + 开任务前确认归档遗留 Trellis task

## Boundaries

- **改**：`plugins/onion-sdd/**` 的 skill、command、运行态 helper、测试、用户文档与 CHANGELOG。
- **不改**：`.trellis/scripts/**`、`.trellis/.runtime/**`、Trellis 源码、`plugins/common/**`、其它插件。
- **不新增脚本**：遗留扫描是 Agent 读 `task.json` + `openspec/changes/` 的步骤，对标现有「更新检查」（同样无 helper）。

OpenSpec 仍是变更正文真相源；本需求不改 `onion_state.py` 读写优先级，只扩展写入前的 `.onion-sdd/` 本地状态治理。

## Flow (manual Tier 2+/3)

```
Trellis 检测
  ├─ 不可用 → 询问安装 + init + gitignore（不变）→ 成功则视为可用
  └─ 可用 → 【删除】更新检查
         → 【新增】遗留变更扫描（OpenSpec + Trellis 成对）
         → task 绑定询问
         → 需求接入
  不可用且拒绝安装 → 遗留变更扫描（仅 OpenSpec）→ 需求接入
```

`/onsf-auto`：不走安装询问、不走遗留扫描。

## Leftover scan contract

手动新开任务前扫描。**成对**：有 Trellis 必归档对应 OpenSpec。**无 Trellis**：只扫上一轮 OpenSpec。

OpenSpec 来源：优先 `current.json.active_change_id`；无 Trellis 且 idle 时列出 `openspec/changes/` 未归档目录。有 Trellis 时不要把未绑定 onion 的其它 OpenSpec 一律当遗留。

Trellis 来源：`completed` 未入库，或 stale（bound OpenSpec 已不在）。与 OpenSpec 按 `change_id` 去重合成一项。

排除：本轮明确 continue 的 change。新 `/onsf-plan` 时上一轮 `active_change_id` 算遗留。

确认后：先 `finish_check` + `openspec archive`，再 `task.py archive`。OpenSpec 失败则整项跳过。

无候选不问。失败不阻塞新任务。

## Compatibility

- `finish_check.check_stale_trellis_tasks` 保留：收尾预检仍 WARN。开任务前询问是前移清理，不是替换门禁。
- gitignore 规则与 `07-07-onion-trellis-auto-install` 一致，只删升级支路。

## `.onion-sdd/` local-state contract

`onion_state.py` 每次写状态前继续调用 `ensure_onion_gitignored(repo_root)`，并增加幂等的 Git 跟踪清理：

1. 确保根 `.gitignore` 有 `.onion-sdd/` 或等价规则。
2. 在 Git 仓库中用 `git ls-files -- .onion-sdd` 检测已跟踪文件。
3. 有命中时执行只清 index 的 `git rm -r --cached --ignore-unmatch -- .onion-sdd`；不得删除工作区文件。
4. Git 不可用、非仓库或命令失败时写 stderr 警告，不阻断 `current.json` 写入。

测试用临时 Git 仓库证明：忽略规则幂等、本地文件保留、index 跟踪清零。

## Trade-offs

- **Skill 步骤 vs 新 Python 扫描器**：选 skill，避免动 scripts 与测试面；漏扫风险用明确表格约束 Agent。
- **成对归档 vs 只收 task**：选成对，避免 Trellis 与 OpenSpec 分裂。无 Trellis 时只收上一轮 OpenSpec。

## Rollback

还原 `full-change`「更新检查」小节并撤回文档 diff；`onion_state.py` 跟踪清理可独立回退。清 index 不删除本地数据，回滚后如需重新跟踪由维护者显式 `git add -f`。
