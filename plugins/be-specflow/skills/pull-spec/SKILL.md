---
name: pull-spec
description: >-
  Use when frontend contract or QA spec arrives from another GitLab repository
  (backend repo context). Triggered by "前端契约到了", "前端spec到了",
  "测试spec到了" plus GitLab URL or path. Requires existing
  openspec/changes/<change-id>/ with proposal.md; for GitLab-only requirement
  intake before any change dir exists, use read-only fetch per dev-workflow
  step 1b (do not write via this skill). Fetches via GITLAB_TOKEN.
---

# 拉取外部 Spec（后端仓库）

从 GitLab 拉取**前端契约**、**其它团队的后端 spec 片段**或**测试/QA spec**到当前 OpenSpec 变更目录：先定位 `change-id` → 拉取或接收粘贴内容 → 按命名写入 `openspec/changes/<change-id>/` → 执行**步骤 4** 的后端视角差异分析（见下）。

## 与「仅有 GitLab 需求、尚无变更目录」的区别

- **需求探索阶段**（尚无 `openspec/changes/<change-id>/`）：用 **`GITLAB_TOKEN` + API** 或用户粘贴，在对话中完成需求事实；**不要**调用本技能写入（见 **`dev-workflow`** 步骤 1b）。
- **本技能**：仅在目标目录**已存在**且含 **`proposal.md`** 时，将外部契约/spec **落盘**到 `frontend-*.md` / `qa-*.md` / `backend-*.md`。

## 前后端与 QA 的复用方式（目录规范一致）

- **团队约定**：**前端仓库**与**后端仓库**针对**同一需求**使用**同一 `change-id`**，外部拉取的文件落在 **`openspec/changes/<change-id>/`**（与 `proposal.md` 同级）。
- **测试/QA spec**：`qa-*.md`；**前端契约**（OpenAPI 片段、对齐说明、由前端维护的契约文档）：建议命名为 **`frontend-*.md`**，与后端仓库内已有 **`proposal.md` 中的服务端 API 契约**对照使用。
- **其它来源的后端说明**：若拉取的是兄弟后端的共享文档，可命名为 `backend-<描述性名称>.md`（与团队既有命名习惯一致即可）。
- **GitLab 源文件**为共享真相；落地路径在前后端各自仓库中**结构相同**。

## 输入

用户提供以下任一形式：

1. **GitLab 文件 URL**（首选）
2. **直接粘贴内容**（降级）

## 定位目标变更

拉取前**必须**先确定写入哪个变更目录。

```bash
find openspec/changes -maxdepth 2 -name proposal.md 2>/dev/null
```

| 场景 | 处理方式 |
|------|---------|
| 仅 1 个变更目录 | 自动选定 |
| 多个变更目录 | 列出所有 change-id，请用户选择 |
| 用户触发语中包含 change-id | 直接使用 |
| 无变更目录 | **拒绝执行**，提示用户先完成设计探索（阶段 1）创建变更 |

## 流程

### 步骤 1：识别来源类型

若用户提供 **GitLab 文件 URL**：使用 **`GITLAB_TOKEN`** 调用 GitLab API 获取文件内容。否则进入**粘贴模式**，直接使用用户提供的正文。

### 步骤 2：拉取内容

GitLab 模式：用 `curl`（或等价方式）请求 API/Raw URL，请求头携带 **`PRIVATE-TOKEN: <GITLAB_TOKEN>`**。粘贴模式：跳过网络请求，校验正文非空即可进入写入步骤。

### 步骤 3：写入本地

**命名规范**（按拉取内容类型选择）：

| 类型 | 文件名模式 |
|------|-----------|
| 前端契约 / 前端 OpenAPI / 对齐用说明 | `frontend-<描述性名称>.md` |
| 测试 / QA 验收 spec | `qa-<描述性名称>.md` |
| 其它后端团队共享 spec | `backend-<描述性名称>.md` |

**文件头部**（自动注入）：

```markdown
<!-- pull-spec metadata -->
<!-- source: <GitLab URL 或 "user-paste"> -->
<!-- commit: <commit hash 或 "N/A"> -->
<!-- pulled_at: <YYYY-MM-DD HH:mm> -->
<!-- WARNING: 此文件为外部 spec 副本，实现以源仓库为准 -->
```

**写入路径**：`openspec/changes/<change-id>/`（与 `proposal.md` 同级）。

**路径约束**：写入前验证目标目录存在 `proposal.md`；写入后 `ls` 确认。

### 步骤 4：差异分析（后端视角）

拉取完成后自动执行：

**若本次写入的是 `frontend-*.md`（前端契约到达）**：

1. 读取 `proposal.md` 中 **API 契约（服务端对外）** 段落
2. 读取 `design.md` / `specs/*/spec.md` 中与接口相关的 Requirements（如有）
3. 读取拉取的前端契约
4. 对比并输出：
   - **一致**：服务端设计与前端契约吻合
   - **差异**：路径、方法、字段、错误码、分页、枚举等
   - **增量**：前端新增字段或场景，后端尚未覆盖
5. 给出**代码与测试**调整建议（handler、DTO、错误映射、`go test` 范围）

**若本次写入的是 `qa-*.md`（测试 spec 到达）**：

1. 读取 `qa-*.md` 中的验收场景
2. 读取 `specs/*/spec.md` 中的 Scenario
3. 标记增量/盲区，供 **`e2e-verify`** 与补充测试使用

**若本次写入的是 `backend-*.md`**：

1. 与当前变更的 `proposal.md`、`specs/*/spec.md` 对照
2. 列出冲突与需统一的口径

## 归档注意

归档时须随变更目录保留所有 `frontend-*.md`、`backend-*.md` 和 `qa-*.md` 文件。
