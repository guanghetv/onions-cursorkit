# workspace-native 读取策略详解

本文件为 `pull-spec` 技能（后端仓库上下文）的参考文档，描述策略 1（workspace-native）的完整实现细节。

## 前置检查

1. **定位 specs 仓库**：在多根工作区的各个 workspace root 中查找 **specs 仓库根**（通常含 `requirements/`），且能在该根下解析到注册表文件：**`workspace-repos.json`（仓库根）** 或 **`scripts/workspace-repos.json`（常用）**；也可用 `**/workspace-repos.json` 在候选目录下定位后再确认上下文。`workspace-repos.json` 列出的是**代码**仓库路径，specs 仓库自身不在该 JSON 的条目列表中——它是**包含**该 JSON 文件的仓库。
2. 读取当前变更的 `proposal.md`，检查是否有 `requirement_ref` 前置字段

## 子场景 A：测试 spec（从 specs 仓库读取）

测试 spec 存放在 specs 仓库的 `requirements/<requirement>/test/test-spec.md`。

```bash
# 1. 从 workspace-repos.json 解析 specs 仓库路径（通常是当前工作区根仓库）
# 2. 从 proposal.md 的 requirement_ref 得到需求路径
# 3. 先 fetch 确保远程 ref 最新
git -C <specs-repo-path> fetch origin --quiet
# 4. 优先从远端默认分支读取（顺序尝试，任一成功即得到内容）
git -C <specs-repo-path> show origin/main:requirements/<requirement>/test/test-spec.md
# 若上一条失败 → 再试传统默认分支名：
git -C <specs-repo-path> show origin/master:requirements/<requirement>/test/test-spec.md
# 5. 若仍失败（QA 可能在 feature 分支上提交，尚未合并到默认分支）→ 分支发现
git -C <specs-repo-path> log --all --remotes --source --format=%S -1 \
  -- requirements/<requirement>/test/test-spec.md
# 6. 有结果 → 用发现的 ref 读取；无结果 → 降级到策略 2 或 3
```

## 子场景 B：对方 API spec（跨仓库分支发现）

对方仓库（前端）的 API spec 在其 feature 分支的 `openspec/changes/<change-id>/proposal.md` 中：

```bash
# 1. 从 proposal.md 的 requirement_ref 提取需求 ID（如 contract-subject-tree-v1）
#
# 2. 确定对方仓库（优先 metadata.yaml，降级遍历）：
#    a) 从 specs 仓库读取 requirements/<requirement>/metadata.yaml 的 changes 字段
#       → 过滤掉当前仓库，剩余即为对方仓库列表
#    b) 若 metadata.yaml 无 changes 字段或不可读 → 遍历 workspace-repos.json 中所有非当前仓库
#
# 3. 推导对方 change-id: <requirement-id>-<对方 repo-name>
# 4. 从 workspace-repos.json 解析对方仓库本地路径
# 4. git fetch + 分支发现（token 优化：仅输出一行 ref 名）
git -C <repo-path> fetch origin --quiet
git -C <repo-path> log --all --remotes --source --format=%S -1 \
  -- openspec/changes/<change-id>/proposal.md
# 输出示例：refs/remotes/origin/feat/S29-xxx-m-222

# 5. 如无结果 → 降级到策略 2（询问 URL）或策略 3（粘贴）

# 6. 读取文件（不 checkout，不影响对方仓库工作状态）
git -C <repo-path> show <ref>:openspec/changes/<change-id>/proposal.md
# 如需更多文件（如 specs/*/spec.md），按相同方式逐个读取：
# git -C <repo-path> show <ref>:openspec/changes/<change-id>/specs/<cap>/spec.md
```

> **读取范围**：优先读取 `proposal.md`（含 API 契约段落）作为差异分析主依据；如需对方完整 spec（如 Scenario 级别对照），可按相同 `git show` 方式补充读取 `specs/*/spec.md`。

## 降级路径

- 无法解析 `workspace-repos.json`（仓库根与 `scripts/` 下均无）→ 提示用户提供 URL 或粘贴
- 对方仓库本地不存在 → 提示用户提供 URL 或粘贴
- `git log` 未发现分支 → 提示「未在对方仓库发现相关分支，请提供 GitLab URL 或粘贴 spec 内容」

## MODULE 切片

如果当前变更的 `proposal.md` 中有 `modules` 字段（由 `design-to-opsx` 注入），在读取测试 spec 时按 MODULE 过滤：

1. 读取 `proposal.md` frontmatter 中的 `modules` 列表（如 `[MODULE-1, MODULE-3]`）
2. 解析测试 spec 中的 MODULE 标记
3. 仅提取与 `modules` 匹配的测试场景
4. 保留完整的公共部分（如测试环境说明、通用前置条件）

若 `modules` 为空或未设置，不做切片，保留完整内容。

## token 优化要点

- `git fetch --quiet`：静默执行，无输出消耗
- `--format=%S -1`：仅输出一行 ref 名，而非完整 git log
- `git show` 直接读文件内容：产出即所需，无多余信息
- 分支发现总 token 开销：约 1 行（ref 名）
