---
name: create-feature-branch
description: 根据飞书需求链接自动创建标准化的feature分支并推送到远程。支持单个或多个飞书链接，多链接时以第一个任务的名称和迭代为主，ID按顺序拼接。当用户提供飞书项目需求链接并需要创建开发分支时使用。Use when user provides Feishu project links or asks to create feature branches from Feishu tasks.
---

# 创建Feature分支

根据一个或多个飞书需求链接自动创建标准化的开发分支并推送到远程仓库。

## 功能特性

- ✅ 支持单个飞书链接：`feat/<迭代>-<任务名称>-m-<ID>`
- ✅ 支持多个飞书链接：`feat/<迭代>-<第一个任务名称>-m-<ID1>-m-<ID2>-m-<ID3>...`
- ✅ 自动从第一个任务获取迭代信息和任务名称
- ✅ 自动检查工作区状态和分支冲突
- ✅ 自动推送并设置远程追踪

## 核心工作流程

### 1. 解析飞书链接

从用户输入中提取所有工作项ID：
- 正则表达式：`/detail/(\d+)`
- 支持多个链接（空格、换行或逗号分隔）
- 第一个ID作为主任务，其他ID按顺序拼接

### 2. 验证Git状态

```bash
# 检查工作区是否干净
git status --porcelain
```

如有未提交变更，立即停止并提示用户处理。

### 3. 切换到默认基线分支并更新（门禁，禁止跳过）

**目的**：`feature` 分支必须从**默认基线分支**的最新提交创建。常见错误是：当前停留在 `develop`（或其它分支）时直接执行 `git checkout -b`，导致新分支误基于 `develop`。本步骤为 **MUST**，不得因「省事」或「以为已是最新」而跳过。

**默认基线分支**：**仅** `master`。**不**根据仓库是否存在 `main` 自动改用 `main`；若 `git checkout master` 失败（无本地/远程 `master`），须停止并提示用户处理（例如将默认分支对齐为 `master`，或见下方「例外」显式指定基线）。

```bash
git fetch origin

# 检出默认基线（禁止在未完成本步前创建 feature 分支）
git checkout master

# 拉取最新代码
git pull origin master
```

**门禁验证（执行下方「### 8. 创建并推送分支」中的 `git checkout -b` 之前必须满足；与 `references/DETAILED_STEPS.md` 的步骤 7 为同一步骤，编号因文档结构不同而不一致）**：

```bash
git branch --show-current
```

在**未**启用「用户指定基线」时，输出必须为 `master`。若为 `develop`、`main`、`feat/...` 或其它分支，**禁止**创建 feature 分支；回到本步或按例外处理。

**MUST NOT（模型必须遵守）**：

- 在未满足门禁时执行 `git checkout -b` / `git switch -c`（默认路径下当前分支必须为 `master`）。
- **自动**检出 `main` 作为默认基线（**禁止**；除非用户明确指定以 `main` 为基线）。
- 以「当前在 develop 且已最新」为由跳过本步。
- 从用户未明确指定的分支（如 `develop`）直接派生 feature 分支。

**例外**：仅当用户**明确写出**以某分支为基线（例如 `develop`、`main`）时，可改用该分支：先 `git checkout <该分支>` 并 `git pull origin <该分支>`，再在回复中说明基线分支名；此时门禁验证为「当前分支名等于用户指定的基线名」。

**权限要求**：`required_permissions: ["network", "git_write"]`

### 4. 查询飞书任务信息

通过**飞书项目 MCP** 调用 `get_workitem_brief` 查询**第一个任务**（Cursor 中 MCP server 标识当前多为 **`FeishuProjectMcp`**；旧文档或配置中的 **`feishu-project-mcp`** 仍指同一能力，以本机 MCP 列表中的实际名称为准）：

```json
{
  "work_item_id": "<第一个ID>",
  "fields": ["名称", "规划迭代", "ID"]
}
```

**强约束（MUST）**：
- 必须显式请求 `fields: ["名称", "规划迭代", "ID"]`，禁止省略 `规划迭代`
- 必须在回复中给出“已获取到的规划迭代原始值”或“为空数组”的证据摘要
- 若本次返回缺少 `规划迭代` 字段，必须先重试一次同参数查询
- 若重试后仍缺少 `规划迭代` 字段，必须中断流程并提示用户排查飞书数据或MCP权限/服务状态

### 5. 获取迭代名称

从规划迭代字段提取迭代工作项ID，再次查询获取迭代名称：

**解析顺序（MUST）**：
1. 从主任务返回体中读取 `规划迭代`
2. 若为数组，取第一个元素中的 `工作项 ID`（若存在多个，只使用第一个）
3. 使用该 `工作项 ID` 再次调用 `get_workitem_brief`（`fields: ["名称"]`）查询迭代名称
4. 将迭代名称（如 `Sprint124`）标准化为迭代编号（如 `124`）

**迭代字段门禁（MUST）**：
- 若 `规划迭代` 明确为 `[]`，必须提示开发者补充/关联迭代并**立即中断流程**
- 若 `规划迭代` 首元素存在但 `工作项 ID` 为空，必须提示开发者修复飞书数据并**立即中断流程**
- 若已完成“主任务查询 + 迭代详情查询（含1次重试）”仍失败，必须提示开发者排查飞书/MCP后重试，并**立即中断流程**
- 禁止因为“模型不确定字段结构”伪造迭代值继续流程
- 禁止跳过迭代详情查询直接生成分支名

### 6. 格式化分支名

**分支命名规则：**
- 单任务：`feat/<迭代编号>-<任务名称>-m-<ID>`
- 多任务：`feat/<迭代编号>-<任务名称>-m-<ID1>-m-<ID2>-m-<ID3>...`

**格式化处理：**
1. 迭代：从 `Sprint124` 提取为 `124`
2. 任务名称：移除特殊字符，保留字母、数字、中文
3. ID拼接：每个ID前添加 `-m-` 前缀

### 7. 检查分支是否存在

```bash
git ls-remote --heads origin <分支名>
```

**权限要求**：`required_permissions: ["network"]`

### 8. 创建并推送分支

**前置条件**：已完成步骤 3 的门禁验证，当前分支为 `master`（或用户明确指定的其它基线分支）。详细命令与说明见 `references/DETAILED_STEPS.md` 的「步骤7：创建并推送分支」。

```bash
# 创建并切换到新分支（仅当基线已正确检出时执行）
git checkout -b <分支名>

# 推送到远程并建立追踪关联
git push -u origin <分支名>
```

**关键要求**：
- ⚠️ 必须使用 `required_permissions: ["all"]` 确保追踪关联成功
- ✅ 使用 `-u` 参数建立分支追踪
- ❌ 绝不使用强推（`--force`）

### 9. 验证追踪关联

检查命令输出是否有 "could not write config file" 错误。如有错误，手动设置追踪：

```bash
git branch --set-upstream-to=origin/<分支名> <分支名>
```

### 10. 确认完成

显示分支信息：
- 单任务：显示分支名、任务名、迭代、工作项ID
- 多任务：额外显示所有关联的工作项ID列表

**输出自检（MUST）**：
在最终成功输出前，先做一次自检，至少满足：
- `iteration_source = api`（表示已完成两跳查询）
- 若无法给出上述自检信息，禁止继续执行建分支命令

## 快速执行清单

当用户提供飞书链接时，按此顺序执行：

1. ✅ 提取所有工作项ID（正则：`/detail/(\d+)`）
2. ✅ 检查工作区状态（`git status --porcelain`）
3. ✅ `git fetch` 后 `git checkout master` 并 `git pull origin master`；**禁止**自动改用 `main`；**禁止**停留在 develop 上直接建分支（权限：`["network", "git_write"]`）
4. ✅ 门禁：默认路径下 `git branch --show-current` 为 `master` 后再继续（用户显式指定其它基线时除外）
5. ✅ 查询第一个任务的详情（`FeishuProjectMcp` / `feishu-project-mcp`，见步骤 4）
6. ✅ 查询迭代名称（必须完成两跳查询；若规划迭代为空或重试后仍无有效数据则直接中断）
7. ✅ 格式化分支名（`feat/<迭代>-<名称>-m-<ID1>-m-<ID2>...`）
8. ✅ 检查远程分支是否存在（权限：`["network"]`）
9. ✅ 创建并推送分支（权限：`["all"]`）
10. ✅ 验证追踪关联
11. ✅ 显示成功信息

## 关键注意事项

1. **基线分支**：步骤 3 与门禁验证是防呆设计；若模型跳过，会导致 feature 误基于 `develop`。执行创建分支前务必再读一遍本节与步骤 3 的 MUST NOT。

2. **多链接处理**：
   - 只查询第一个任务的详情
   - 其他任务仅使用ID拼接到分支名
   - 以第一个任务的名称和迭代为准

3. **权限管理**：
   - git pull：`["network", "git_write"]`
   - git ls-remote：`["network"]`
   - git checkout + push：`["all"]`（必须使用完整权限）

4. **错误处理**：
   - 工作区有变更：立即停止
   - 无法解析链接：提示格式错误
   - 迭代字段为空：提示开发者补充规划迭代并立即中断
   - 分支已存在：提示用户处理
   - 追踪关联失败：手动设置
   - `git checkout master` 失败（无 `master`）：停止并说明本技能默认基线为 `master`；请用户调整仓库分支，或**明确指定**以某分支（如 `main`）为基线后再执行

## 参考文档

详细信息请查看以下参考文档：
- `references/DETAILED_STEPS.md` - 每个步骤的详细说明
- `references/EXAMPLES.md` - 完整的使用示例
- `references/TROUBLESHOOTING.md` - 错误处理和故障排查
