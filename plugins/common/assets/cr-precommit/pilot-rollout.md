# AICR 批量改造试点演练

本文用于执行 `tasks 6.6`：在 1-2 个业务仓进行 batch rollout，产出成功率/失败分类/回滚演练记录。

## 前置条件

- 已在本仓完成脚本准备：
  - `migrate-to-bundled-runtime.sh`
  - `batch-rollout.sh`
  - `rollback-bundled-runtime.sh`
- 试点仓库可本地访问，且是 Git 仓库。

## 1. 准备试点仓清单

创建 `repos.txt`（一行一个绝对路径）：

```text
/path/to/repo-a
/path/to/repo-b
```

## 2. dry-run 预演

```bash
MODE=dry-run REPORT_FILE=/tmp/aicr-rollout-preview.csv \
bash "plugins/common/assets/cr-precommit/batch-rollout.sh" --repos-file /tmp/repos.txt
```

检查：

- 每个仓有 `PREVIEW` 或 `FAILED`；
- `FAILED` 的 `reason` 可定位问题；
- 保留日志目录路径（输出中的 `log_dir`）。

## 3. apply 执行

```bash
MODE=apply REPORT_FILE=/tmp/aicr-rollout-apply.csv \
bash "plugins/common/assets/cr-precommit/batch-rollout.sh" --repos-file /tmp/repos.txt
```

检查：

- 目标仓产生 `vendor/aicr-runtime/`；
- `.githooks/pre-commit` 存在且为薄入口；
- `git -C <repo> config core.hooksPath` 输出 `.githooks`。

**升级注意**：若仓库已有旧版 `cr_completed` 事件，升级 runtime 后开发者须对当前暂存区**重新执行 `/cr`**（`diff_fingerprint` 算法已变更）。试点沟通中应明确告知，避免误判为门禁故障。

## 4. 回滚演练（至少 1 个仓）

```bash
bash "plugins/common/assets/cr-precommit/rollback-bundled-runtime.sh" /path/to/repo-a
```

检查：

- 输出包含 `restored from ...`；
- 仓库结构回到迁移前状态（以 backup 为准）。

## 5. 试点记录模板

建议在试点记录中至少包含：

- 试点仓数量
- `UPDATED/UNCHANGED/PREVIEW/FAILED` 计数
- 失败分类明细（`reason`）
- 回滚演练是否通过
- 后续扩面建议与风险项
