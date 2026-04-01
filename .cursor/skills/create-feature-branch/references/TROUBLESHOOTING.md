# 错误处理与故障排查

本文档提供常见错误的处理方法和故障排查指南。

## 错误处理清单

| 场景 | 检测方法 | 处理方式 |
|------|---------|---------|
| 工作区有未提交变更 | `git status --porcelain` 有输出 | 停止流程，提示用户处理变更 |
| 无法解析飞书链接 | 正则匹配失败或未找到任何ID | 提示链接格式错误 |
| 多链接中有无效链接 | 部分链接无法提取ID | 警告提示，继续使用成功提取的ID |
| 飞书API调用失败 | MCP工具返回错误 | 显示错误信息，提示检查权限 |
| 规划迭代字段为空 | 规划迭代数组为空或无工作项ID | 使用 `unknown` 作为迭代标识，继续执行 |
| 获取迭代名称失败 | 查询迭代工作项失败 | 警告提示，使用 `unknown` 作为迭代标识，继续执行 |
| 分支已存在 | `git ls-remote` 或 `git checkout -b` 失败 | 提示分支已存在 |
| 追踪关联失败 | 输出包含 "could not write config file" | 使用 `git branch --set-upstream-to` 手动设置追踪，需要 `required_permissions: ["all"]` |
| Git操作失败 | 命令返回非零退出码 | 显示Git错误信息 |
| 网络问题 | git pull/push 超时 | 提示检查网络连接 |
| 分支名过长 | 多任务导致分支名超长 | Git支持长分支名，但可以警告用户 |
| 无 `master` 或 `git checkout master` 失败 | 远程仅有 `main` 等，本地无 `master` | 停止流程；见「问题11」：创建/跟踪 `master` 或**显式指定**基线（如 `main`）后再执行技能 |

---

## 常见问题与解决方案

### 问题1：工作区有未提交变更

**症状**：
```
⚠️ 检测到未提交的代码变更，无法切换分支。
```

**原因**：当前工作区有未提交的文件修改

**解决方案**：

```bash
# 方案1：提交变更（推荐）
git add .
git commit -m "描述你的变更"

# 方案2：暂存变更
git stash
# 稍后恢复：git stash pop

# 方案3：放弃变更（谨慎使用）
git reset --hard
```

---

### 问题2：无法推送到远程

**症状**：
```
fatal: unable to access 'https://...': Could not resolve host
```

**检查步骤**：

```bash
# 1. 检查远程仓库配置
git remote -v

# 2. 检查网络连接
git ls-remote origin

# 3. 测试SSH连接（如使用SSH）
ssh -T git@github.com
```

**解决方案**：
- 检查网络连接
- 确认仓库地址正确
- 验证SSH密钥或访问令牌
- 检查防火墙设置

---

### 问题3：分支追踪关联失败

**症状**：
```
There is no tracking information for the current branch.
```

**原因**：`git push -u` 时由于权限限制无法写入 `.git/config` 文件

**检查方法**：
```bash
# 查看当前分支的追踪状态
git branch -vv
```

**解决方案1：手动设置追踪关联（推荐）**
```bash
git branch --set-upstream-to=origin/<分支名> <分支名>
```

**解决方案2：使用完整的 git pull 命令**
```bash
git pull origin <分支名>
```

**预防措施**：
确保在执行 `git push -u` 时使用 `required_permissions: ["all"]`

---

### 问题4：分支已存在

**症状**：
```
⚠️ 分支 feat/124-功能名称-m-6717631602 已存在
```

**检查远程分支**：
```bash
git ls-remote --heads origin feat/124-功能名称-m-6717631602
```

**解决方案**：

```bash
# 方案1：切换到现有分支
git checkout feat/124-功能名称-m-6717631602
git pull origin feat/124-功能名称-m-6717631602

# 方案2：使用不同的分支名
# 可以在任务名称后添加后缀
# 例如：feat/124-功能名称-v2-m-6717631602

# 方案3：删除远程分支（谨慎使用）
git push origin --delete feat/124-功能名称-m-6717631602
# 然后重新创建
```

---

### 问题5：无法解析飞书链接

**症状**：
```
❌ 无法解析飞书链接，请检查链接格式是否正确。
```

**检查清单**：
- [ ] 链接包含 `/detail/` 路径
- [ ] 链接包含数字ID
- [ ] 链接格式正确

**正确格式示例**：
```
https://project.feishu.cn/ruxiao/tec_prd/detail/6717631602
https://project.feishu.cn/ruxiao/tec_prd/detail/6717631602?parentUrl=...
```

**错误格式示例**：
```
https://project.feishu.cn/ruxiao/tec_prd/  # 缺少 detail 和 ID
https://project.feishu.cn/detail/          # 缺少 ID
```

---

### 问题6：飞书MCP服务无响应

**症状**：
```
❌ 无法获取飞书任务信息：[错误详情]
```

**检查步骤**：

```bash
# 1. 检查MCP服务状态
# 在Cursor中查看MCP服务是否正常运行

# 2. 验证飞书API认证
# 检查MCP配置文件中的认证信息

# 3. 测试网络连接
ping project.feishu.cn
```

**可能原因**：
- MCP服务未启动
- 飞书API认证失败
- 网络连接问题
- 工作项ID无效
- 无权限访问该工作项

**解决方案**：
1. 重启MCP服务
2. 检查并更新飞书API认证配置
3. 验证工作项ID和访问权限
4. 检查网络连接
5. 在 Cursor MCP 设置中确认飞书项目服务已启用；server 名称可能为 **`FeishuProjectMcp`**（与旧称 `feishu-project-mcp` 兼容，以列表为准）

---

### 问题7：分支名包含非法字符

**症状**：
```
fatal: 'feat/...' is not a valid branch name
```

**原因**：飞书任务名称包含Git不支持的特殊字符

**Git分支名规范**：
- 不能包含空格
- 不能包含 `~`, `^`, `:`, `?`, `*`, `[`, `\`
- 不能以 `/` 结尾
- 不能包含连续的 `/`

**解决方案**：
检查格式化逻辑，确保：
- 移除特殊字符
- 空格替换为连字符 `-`
- 移除连续的连字符
- 移除首尾的连字符

**格式化示例**：
```python
# 原始名称：【重要】支付功能 / 优化
# 格式化后：重要-支付功能-优化
```

---

### 问题8：权限不足导致的操作失败

**症状**：
```
Permission denied
fatal: could not write config file
```

**原因**：未使用正确的权限执行Git操作

**权限要求对照表**：

| 操作 | 所需权限 |
|------|---------|
| `git pull origin master` | `["network", "git_write"]` |
| `git ls-remote` | `["network"]` |
| `git checkout -b` | `["all"]` |
| `git push -u` | `["all"]` |

**解决方案**：
确保在执行相应命令时请求正确的权限，特别是创建分支和推送操作必须使用 `required_permissions: ["all"]`

---

### 问题9：网络超时

**症状**：
```
fatal: unable to access 'https://...': Operation timed out
```

**检查步骤**：

```bash
# 1. 测试网络连接
ping github.com
# 或
ping gitlab.com

# 2. 检查代理设置
git config --get http.proxy
git config --get https.proxy

# 3. 增加超时时间
git config --global http.postBuffer 524288000
git config --global http.timeout 300
```

**解决方案**：
- 检查网络连接
- 配置代理（如需要）
- 增加Git超时时间
- 使用SSH代替HTTPS

---

### 问题10：多任务时分支名过长

**症状**：分支名包含多个任务ID，总长度较长

**示例**：
```
feat/124-优化支付模块-m-6717631602-m-6717631603-m-6717631604-m-6717631605-m-6717631606
```

**说明**：
- Git支持较长的分支名（最大255字符）
- 这不是错误，但可能影响可读性

**建议**：
- 如果任务数量过多（>5个），考虑：
  - 将任务分组到不同的分支
  - 使用更通用的分支名
  - 在commit message中详细说明关联的任务

---

### 问题11：无 master 分支或 `git checkout master` 失败

**症状**：

```
error: pathspec 'master' did not match any file(s) known to git
```

或远程无 `master` 分支。

**原因**：本技能**默认**从 `master` 派生 feature 分支；**不会**自动改用 `main` 或其它分支。

**解决方案**（任选其一）：

1. **在仓库中提供 `master`**（例如将 `main` 作为团队约定的基线分支名时，可新增 `master` 指向同一提交，或与团队统一约定后创建远程 `master`）。
2. **显式指定基线**：在对话中说明「以 `main` 为基线（或 `develop` 等）创建分支」，再按技能「例外」路径执行：`git checkout <基线>` → `git pull origin <基线>` → 创建 feature 分支。

---

## 调试技巧

### 1. 查看详细的Git输出

```bash
# 启用详细输出
GIT_TRACE=1 git push -u origin <分支名>
GIT_CURL_VERBOSE=1 git push -u origin <分支名>
```

### 2. 检查分支状态

```bash
# 查看所有分支
git branch -a

# 查看分支追踪关系
git branch -vv

# 查看远程分支
git ls-remote --heads origin
```

### 3. 验证MCP工具

在Cursor中测试MCP工具：
```
使用飞书项目 MCP（FeishuProjectMcp，或配置中的 feishu-project-mcp）的 get_workitem_brief 工具
测试工作项ID：6717631602
```

### 4. 手动测试飞书链接解析

```python
import re
test_input = "你的飞书链接"
pattern = r'/detail/(\d+)'
ids = re.findall(pattern, test_input)
print(f"提取到的ID: {ids}")
```

---

## 紧急恢复

### 如果意外切换了分支

```bash
# 查看最近的分支切换历史
git reflog

# 切换回之前的分支
git checkout <之前的分支名>
```

### 如果意外删除了本地分支

```bash
# 从远程恢复
git checkout -b <分支名> origin/<分支名>

# 或查看reflog找回
git reflog
git checkout -b <分支名> <commit-hash>
```

### 如果推送失败但本地已创建分支

```bash
# 删除本地分支
git branch -D <分支名>

# 重新执行创建流程
```

---

## 预防性措施

1. **执行前检查**：
   - 确保工作区干净
   - 确认当前在正确的分支
   - 验证网络连接正常

2. **使用正确的权限**：
   - 查询操作：默认权限即可
   - Git写操作：使用 `["network", "git_write"]` 或 `["all"]`

3. **错误处理**：
   - 每个步骤都应有错误检查
   - 关键操作失败时立即停止
   - 提供明确的错误提示

4. **备份重要工作**：
   - 切换分支前提交或stash当前工作
   - 定期推送到远程仓库
   - 重要修改及时提交

---

## 联系支持

如果遇到以上方法无法解决的问题：

1. 检查Cursor和MCP服务的版本
2. 查看Cursor的错误日志
3. 在项目仓库中提Issue
4. 联系团队技术支持
