# 使用示例

本文档提供完整的使用示例，展示单个和多个飞书链接的处理流程。

## 示例1：单个飞书链接

### 用户输入

```
https://project.feishu.cn/ruxiao/tec_prd/detail/6717631602?parentUrl=%2Fruxiao%2FworkObjectView%2Ftec_prd%2FopR6hO3nR%3Fscope%3Dworkspaces%26node%3D1487604&scope=workspaces&node=1487604&openScene=4
```

### 执行过程

1. **提取ID**：`['6717631602']`
2. **检查工作区**：✓ 干净
3. **当前分支**：master ✓
4. **拉取代码**：✓ 已是最新（使用 `required_permissions: ["network", "git_write"]`）
5. **查询飞书任务**：获取到任务信息
   - 名称：axiosRetry功能优化
   - 规划迭代工作项ID：6688772577
   - 任务ID：6717631602
6. **查询迭代详情**：工作项ID `6688772577`
   - 迭代名称：Sprint124
7. **格式化分支名**：`feat/124-axiosRetry功能优化-m-6717631602`
8. **检查远程分支**：✓ 不存在（使用 `required_permissions: ["network"]`）
9. **创建并推送分支**：✓（**必须使用 `required_permissions: ["all"]`**）
10. **验证追踪关联**：✓ 成功

### 输出结果

```
✅ 分支创建成功！

📋 分支信息：
  分支名称：feat/124-axiosRetry功能优化-m-6717631602
  飞书任务：axiosRetry功能优化
  规划迭代：Sprint124 (迭代编号: 124)
  工作项ID：6717631602
  
🔗 远程分支已创建并关联
💡 你现在可以开始在此分支上进行开发
```

### 执行的Git命令

```bash
# 检查工作区
git status --porcelain

# 检查并切换分支
git branch --show-current
git checkout master

# 更新代码
git pull origin master

# 检查远程分支
git ls-remote --heads origin feat/124-axiosRetry功能优化-m-6717631602

# 创建并推送分支
git checkout -b feat/124-axiosRetry功能优化-m-6717631602
git push -u origin feat/124-axiosRetry功能优化-m-6717631602
```

---

## 示例2：多个飞书链接

### 用户输入

```
https://project.feishu.cn/ruxiao/tec_prd/detail/6717631602
https://project.feishu.cn/ruxiao/tec_prd/detail/6717631603
https://project.feishu.cn/ruxiao/tec_prd/detail/6717631604
```

### 执行过程

1. **提取ID**：`['6717631602', '6717631603', '6717631604']`
2. **检查工作区**：✓ 干净
3. **当前分支**：master ✓
4. **拉取代码**：✓ 已是最新（使用 `required_permissions: ["network", "git_write"]`）
5. **查询飞书任务**：获取到**第一个任务**的信息
   - 名称：优化支付模块
   - 规划迭代工作项ID：6688772577
   - 任务ID：6717631602
6. **查询迭代详情**：工作项ID `6688772577`
   - 迭代名称：Sprint125
7. **格式化分支名**：`feat/125-优化支付模块-m-6717631602-m-6717631603-m-6717631604`
8. **检查远程分支**：✓ 不存在（使用 `required_permissions: ["network"]`）
9. **创建并推送分支**：✓（**必须使用 `required_permissions: ["all"]`**）
10. **验证追踪关联**：✓ 成功

### 输出结果

```
✅ 分支创建成功！

📋 分支信息：
  分支名称：feat/125-优化支付模块-m-6717631602-m-6717631603-m-6717631604
  飞书任务：优化支付模块（主任务）
  规划迭代：Sprint125 (迭代编号: 125)
  关联工作项：
    - 6717631602 (主任务)
    - 6717631603
    - 6717631604
  
🔗 远程分支已创建并关联
💡 你现在可以开始在此分支上进行开发
💡 该分支关联了3个飞书任务
```

### 执行的Git命令

```bash
# 检查工作区
git status --porcelain

# 检查并切换分支
git branch --show-current
git checkout master

# 更新代码
git pull origin master

# 检查远程分支
git ls-remote --heads origin feat/125-优化支付模块-m-6717631602-m-6717631603-m-6717631604

# 创建并推送分支
git checkout -b feat/125-优化支付模块-m-6717631602-m-6717631603-m-6717631604
git push -u origin feat/125-优化支付模块-m-6717631602-m-6717631603-m-6717631604
```

### 关键说明

- 只查询了第一个任务（6717631602）的详情
- 其他任务（6717631603、6717631604）仅使用ID拼接到分支名
- 分支名使用第一个任务的名称和迭代信息
- 所有任务ID按顺序拼接，格式：`-m-ID1-m-ID2-m-ID3`

---

## 示例3：混合输入格式

用户可能以不同方式提供多个链接：

### 用户输入（用逗号分隔）

```
https://project.feishu.cn/ruxiao/tec_prd/detail/6717631602, https://project.feishu.cn/ruxiao/tec_prd/detail/6717631603
```

### 用户输入（混合分隔）

```
https://project.feishu.cn/ruxiao/tec_prd/detail/6717631602

https://project.feishu.cn/ruxiao/tec_prd/detail/6717631603, https://project.feishu.cn/ruxiao/tec_prd/detail/6717631604
```

以上所有格式都应该能正确提取ID：`['6717631602', '6717631603', '6717631604']`

---

## 示例4：无规划迭代的情况

### 场景

飞书任务没有关联规划迭代。

### 执行过程

1-5. 同上
6. **查询迭代详情**：规划迭代字段为空 `[]`
   - 迭代名称：`unknown`
7. **格式化分支名**：`feat/unknown-优化支付模块-m-6717631602`

### 输出结果

```
⚠️ 无法获取规划迭代名称，将使用 'unknown' 作为迭代标识

✅ 分支创建成功！

📋 分支信息：
  分支名称：feat/unknown-优化支付模块-m-6717631602
  飞书任务：优化支付模块
  规划迭代：未关联迭代
  工作项ID：6717631602
  
🔗 远程分支已创建并关联
💡 你现在可以开始在此分支上进行开发
```

---

## 常见使用场景

### 场景1：单个任务开发

适用于：独立的功能开发、Bug修复

**操作**：提供单个飞书链接

**结果**：`feat/124-功能名称-m-6717631602`

### 场景2：多任务联动开发

适用于：一个功能涉及多个飞书任务、关联需求一起开发

**操作**：提供多个飞书链接（第一个为主任务）

**结果**：`feat/124-主任务名称-m-6717631602-m-6717631603-m-6717631604`

**优势**：
- 分支名清晰标识所有关联任务
- 便于代码评审时理解完整上下文
- 方便追溯多任务的开发历史

### 场景3：紧急修复

适用于：生产环境Bug、紧急需求

**注意事项**：
- 确保工作区干净（可使用 `git stash` 暂存当前工作）
- 从最新的 master 分支创建
- 修复完成后立即合并
