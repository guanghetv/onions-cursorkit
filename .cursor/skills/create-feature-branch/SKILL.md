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

### 3. 切换到master并更新

```bash
# 确保在master分支
git checkout master

# 拉取最新代码
git pull origin master
```

**权限要求**：`required_permissions: ["network", "git_write"]`

### 4. 查询飞书任务信息

通过**飞书项目 MCP** 调用 `get_workitem_brief` 查询**第一个任务**（Cursor 中 MCP server 标识当前多为 **`FeishuProjectMcp`**；旧文档或配置中的 **`feishu-project-mcp`** 仍指同一能力，以本机 MCP 列表中的实际名称为准）：

```json
{
  "work_item_id": "<第一个ID>",
  "fields": ["名称", "规划迭代", "ID"]
}
```

### 5. 获取迭代名称

从规划迭代字段提取迭代工作项ID，再次查询获取迭代名称：
- 如果迭代字段为空或查询失败，使用 `unknown`

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

```bash
# 创建并切换到新分支
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

## 快速执行清单

当用户提供飞书链接时，按此顺序执行：

1. ✅ 提取所有工作项ID（正则：`/detail/(\d+)`）
2. ✅ 检查工作区状态（`git status --porcelain`）
3. ✅ 切换到master并拉取最新代码（权限：`["network", "git_write"]`）
4. ✅ 查询第一个任务的详情（`FeishuProjectMcp` / `feishu-project-mcp`，见步骤 4）
5. ✅ 查询迭代名称（如失败使用 `unknown`）
6. ✅ 格式化分支名（`feat/<迭代>-<名称>-m-<ID1>-m-<ID2>...`）
7. ✅ 检查远程分支是否存在（权限：`["network"]`）
8. ✅ 创建并推送分支（权限：`["all"]`）
9. ✅ 验证追踪关联
10. ✅ 显示成功信息

## 关键注意事项

1. **多链接处理**：
   - 只查询第一个任务的详情
   - 其他任务仅使用ID拼接到分支名
   - 以第一个任务的名称和迭代为准

2. **权限管理**：
   - git pull：`["network", "git_write"]`
   - git ls-remote：`["network"]`
   - git checkout + push：`["all"]`（必须使用完整权限）

3. **错误处理**：
   - 工作区有变更：立即停止
   - 无法解析链接：提示格式错误
   - 迭代字段为空：使用 `unknown` 继续
   - 分支已存在：提示用户处理
   - 追踪关联失败：手动设置

## 参考文档

详细信息请查看以下参考文档：
- `references/DETAILED_STEPS.md` - 每个步骤的详细说明
- `references/EXAMPLES.md` - 完整的使用示例
- `references/TROUBLESHOOTING.md` - 错误处理和故障排查
