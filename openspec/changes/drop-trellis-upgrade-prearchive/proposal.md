# drop-trellis-upgrade-prearchive

## 背景

- Onion SDD 手动入口当前会检查并推荐升级 Trellis，容易让业务开发者介入由专人维护的 CLI 与模板版本。
- 未执行 `/onsf-finish` 时，已完成或绑定 change 已消失的 Trellis task 会残留在活跃树。
- `.onion-sdd/` 是每位开发者的本地运行态；仅追加 `.gitignore` 无法处理此前已被 Git 跟踪的文件。

## 目标

- 移除当前流程中的 Trellis 版本检查与升级推荐，同时保留未安装时的本地安装、`trellis init` 和平台目录忽略。
- 在手动 Tier 2+/3 新任务进入需求接入前确认归档上一轮变更：Trellis 与 OpenSpec 成对；无 Trellis 时只归档上一轮 OpenSpec。
- 所有 Onion SDD 状态写入都确保 `.onion-sdd/` 被忽略；已跟踪文件只从 Git index 移除并保留本地内容。

## 变更

- `full-change` 用遗留变更扫描替换 Trellis 更新检查；Trellis 与 OpenSpec 成对归档；未装 Trellis 时仍确认上一轮 OpenSpec。mini、light 与 `/onsf-auto` 不执行。
- 新开 `/onsf-plan` 时，`current.json` 上一轮 `active_change_id` 视为遗留。用户确认后先归档 OpenSpec 再归档 Trellis；预检失败则整项跳过以保持同步。
- `onion_state.py` 写状态前幂等维护根 `.gitignore`，并通过 `git rm -r --cached --ignore-unmatch -- .onion-sdd` 清理已跟踪状态文件。
- README、USAGE、飞书 wiki、设计补充、`onsf-auto` 与 CHANGELOG 对齐当前行为。

## 影响范围

- 页面/模块: `plugins/onion-sdd/**` 的流程文档、运行态 helper 与测试。
- 数据/API: 无业务数据或 API 变更；仅本地 JSON 状态与 Git index 行为。
- 权限/安全/资金: 无。
- 兼容性: 不改变运行态 JSON 格式和读写优先级；Git 不可用、非仓库或命令失败时仅警告并继续写状态。

## 不做范围

- 不修改 Trellis CLI、Trellis 源码、`.trellis/scripts/**` 或 `.trellis/.runtime/**`。
- 不把本轮明确 continue 的 change 当作遗留，也不为遗留扫描新增 Python helper。
- 不修改 `finish_check.py` 的 hard/soft 门禁。

## 验收

- 当前 skill 与用户文档不再推荐执行 `trellis upgrade` 或 `trellis update`；历史 CHANGELOG 记录可保留。
- 手动 Tier 2+/3 入口列出遗留变更，未经确认不归档；有 Trellis 则成对归档 OpenSpec 与 task，无 Trellis 则只归档上一轮 OpenSpec；失败不阻塞。
- `/onsf-auto` 不安装、不扫描、不归档遗留 Trellis task。
- 自动化测试证明忽略规则幂等、已跟踪文件从 index 清除且本地文件保留、Git 失败不阻断状态写入。
- 插件模板校验与定向 Python 测试通过，且 `.trellis/scripts/**` 无 diff。

## 风险与回滚

- 风险：Git index 清理会产生待提交的删除记录；helper 必须输出明确提示，且命令参数固定、以解析后的 repo root 为工作目录。
- 回滚：还原 Onion SDD 文档、helper 与测试；清 index 不删除本地文件，如确需恢复跟踪由维护者显式 `git add -f`。

## References

- `.trellis/tasks/08-26-onion-sdd-drop-upgrade-pre-archive/prd.md`
- `.trellis/tasks/08-26-onion-sdd-drop-upgrade-pre-archive/design.md`
- `.trellis/tasks/08-26-onion-sdd-drop-upgrade-pre-archive/implement.md`
