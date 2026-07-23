# 详细步骤说明

本文档提供创建Feature分支的详细步骤说明和实现细节。

## 步骤1：验证工作区状态

在开始之前，必须确保工作区干净，没有未提交的变更：

```bash
git status --porcelain
```

**处理逻辑：**
- 如果输出为空：继续下一步
- 如果有输出：**立即停止并提示用户**
  
  提示消息：
  ```
  ⚠️ 检测到未提交的代码变更，无法切换分支。
  请先处理以下变更：
  - 提交变更：git add . && git commit -m "message"
  - 或暂存变更：git stash
  - 或放弃变更：git reset --hard
  ```

## 步骤2：确保在默认基线分支且代码最新（门禁）

**目的**：feature 分支必须从 **`master`** 的最新提交创建；**禁止**在 `develop` 等分支上直接 `git checkout -b`；**禁止**自动改用 `main`（除非用户明确指定以 `main` 为基线）。

```bash
git fetch origin
git checkout master
git pull origin master
```

**门禁（执行下方「步骤7：创建并推送分支」中的 `git checkout -b` 前必须满足；与主文档 `SKILL.md` 的步骤 8 为同一步骤，编号因文档结构不同而不一致）**：默认路径下 `git branch --show-current` 为 `master`。否则禁止执行 `git checkout -b`，回到本步。

**例外**：用户明确写出以某分支为基线（如 `develop`、`main`）时，可 `git checkout` 该分支并 `git pull origin <该分支>`，并在回复中说明基线名。

**MUST NOT**：在仍为 `develop`、`main`（未显式指定时）、`feat/...` 等时按默认路径创建 feature 分支。

**无 master 时**：`git checkout master` 失败则停止，提示用户处理仓库默认分支或显式指定基线；不得自动 `git checkout main`。

## 步骤3：解析飞书需求链接

从用户提供的一个或多个飞书链接中提取工作项ID。

**链接示例：**
```
单个链接：
https://project.feishu.cn/ruxiao/tec_prd/detail/6717631602?parentUrl=...

多个链接（用户可能用空格、换行或逗号分隔）：
https://project.feishu.cn/ruxiao/tec_prd/detail/6717631602
https://project.feishu.cn/ruxiao/tec_prd/detail/6717631603
https://project.feishu.cn/ruxiao/tec_prd/detail/6717631604
```

**提取规则：**
- 使用正则表达式：`/detail/(\d+)`
- 从用户输入中提取所有匹配的飞书链接
- 支持多种分隔符：空格、换行、逗号
- 提取所有工作项ID并保持顺序
- 示例：提取到 `['6717631602', '6717631603', '6717631604']`

**处理逻辑：**
- 如果提取到一个ID：按原有单链接流程处理
- 如果提取到多个ID：
  - 第一个ID用于获取任务名称和迭代信息（作为主任务）
  - 所有ID按顺序拼接到分支名中：`-m-ID1-m-ID2-m-ID3...`
- 如果未提取到任何ID：提示错误

**实现建议：**
```python
# 伪代码示例
import re

user_input = """
https://project.feishu.cn/ruxiao/tec_prd/detail/6717631602
https://project.feishu.cn/ruxiao/tec_prd/detail/6717631603
https://project.feishu.cn/ruxiao/tec_prd/detail/6717631604
"""

# 提取所有工作项ID
pattern = r'/detail/(\d+)'
work_item_ids = re.findall(pattern, user_input)
# 结果: ['6717631602', '6717631603', '6717631604']

# 如果没有提取到任何ID
if not work_item_ids:
    print("❌ 无法解析飞书链接")
    exit()

# 第一个ID作为主任务ID
primary_id = work_item_ids[0]
# 所有ID用于拼接分支名
all_ids = work_item_ids
```

**错误处理：**
如果无法提取ID，提示用户：
```
❌ 无法解析飞书链接，请检查链接格式是否正确。
正确格式示例：https://project.feishu.cn/ruxiao/tec_prd/detail/6717631602...
```

## 步骤4：查询飞书任务详情（CLI 优先，MCP 备选）

查询**第一个**任务的信息（作为主任务）。工具优先级：

1. **首选**：Meegle CLI（`@lark-project/meegle` / `meegle`）
2. **备选**：飞书项目 MCP `get_workitem_brief`（Cursor server 多为 **`FeishuProjectMcp`**；旧称 **`feishu-project-mcp`** 视为同一能力）

### 4a. Meegle CLI（首选）

业务查询前执行授权检查：

```bash
meegle auth status --format json
```

未登录时按 meegle 技能完成 `meegle auth login --host <host>`（飞书项目一般为 `project.feishu.cn`）。可选：

```bash
meegle url decode --url "<用户飞书链接>" --format json
```

从 URL 或 decode 结果取得 `project_key` / `simple_name`（如 `ruxiao`），再查询：

```bash
meegle workitem get \
  --work-item-id "6717631602" \
  --project-key "ruxiao" \
  --fields '["名称","规划迭代","ID"]' \
  --format json
```

字段也可用 field_key（如 `name`）；以能解析出任务名称、规划迭代、工作项 ID 为准。不确定参数时：`meegle inspect workitem.get`（必要时加 `--refresh`）。

### 4b. 飞书项目 MCP（备选）

仅当 CLI 未安装、`auth` 失败且无法完成登录、或 `workitem get` 报错时使用。**CLI 已成功时不得先调 MCP。**

```json
{
  "work_item_id": "6717631602",
  "fields": ["名称", "规划迭代", "ID"]
}
```

**返回数据示例（语义，CLI/MCP 字段形态可能不同）：**
```
工作项名称: 【分账】支持延迟型专项课
规划迭代: [{"工作项 ID":"6688772577","工作项名称":""}]
工作项 ID: 6717631602
```

**重要说明：**
- **只查询第一个任务的详情**，用于获取任务名称和规划迭代信息
- 其他任务的ID将直接用于分支名拼接，不需要查询详情
- 分支名将包含所有任务的ID：`-m-ID1-m-ID2-m-ID3...`

**注意事项：**
- 如果工作项ID无效或无权限访问，会返回错误
- 规划迭代字段通常为数组，包含迭代工作项的ID
- CLI 与 MCP 均失败时停止，**禁止**编造任务名或迭代

**错误处理：**
```
❌ 无法获取飞书任务信息：[错误详情]
请检查：
1. 工作项ID是否正确
2. 是否有该任务的访问权限
3. Meegle CLI：是否已安装、`meegle auth status` 是否已登录
4. 备选：飞书项目 MCP 是否已启用且可调用
```

## 步骤5：获取规划迭代名称

从步骤4获取的规划迭代字段中提取迭代工作项ID，然后查询迭代的实际名称（**通道优先级与步骤4相同**：先 CLI，失败再 MCP）。

**提取迭代工作项ID：**

从规划迭代字段返回的数据中提取（字段名因通道可能为「工作项 ID」或结构化 id）：
```json
[{"工作项 ID":"6688772577","工作项名称":""}]
```

提取出迭代工作项 ID：`6688772577`

**查询迭代详情（首选 CLI）：**

```bash
meegle workitem get \
  --work-item-id "6688772577" \
  --project-key "ruxiao" \
  --fields '["名称"]' \
  --format json
```

**备选 MCP：**

```json
{
  "work_item_id": "6688772577",
  "fields": ["名称"]
}
```

**返回数据示例：**
```
工作项名称: Sprint124
```

**处理逻辑：**
- 如果规划迭代字段为空数组 `[]`：迭代名称使用 `unknown`
- 如果规划迭代字段的工作项 ID 为空：迭代名称使用 `unknown`
- 如果查询迭代详情失败（CLI 与 MCP 皆失败或跳过）：迭代名称使用 `unknown`
- 如果查询成功：使用返回的迭代名称

**错误处理：**
```
⚠️ 无法获取规划迭代名称，将使用 'unknown' 作为迭代标识
原因：[错误详情]
```

## 步骤6：格式化分支名称

根据飞书任务信息生成标准化的分支名称。

**分支命名规则：**
```
单个任务：
feat/<规划迭代>-<飞书卡片名称>-m-<飞书卡片ID>

多个任务：
feat/<规划迭代>-<第一个飞书卡片名称>-m-<ID1>-m-<ID2>-m-<ID3>...
```

**格式化步骤：**

1. **处理规划迭代**：
   - 从步骤5获取的迭代名称：`Sprint124` 或 `sprint 124`
   - 处理后：`124`（仅保留数字）
   - 方法：移除 "sprint" 前缀（不区分大小写），去除空格
   - 如果步骤5返回 `unknown`，则直接使用 `unknown`

2. **处理卡片名称**：
   - **使用第一个任务的名称**
   - 移除特殊字符，只保留字母、数字、中文
   - 将空格和其他分隔符替换为单个连字符 `-`
   - 避免连续的连字符
   - 移除首尾的连字符
   - 示例：`axios retry 功能` → `axiosRetry功能`

3. **拼接工作项ID**：
   - 将步骤3提取到的所有工作项ID按顺序拼接
   - 每个ID前添加 `-m-` 前缀
   - 单个ID：`-m-6713554226`
   - 多个ID：`-m-6713554226-m-6713554227-m-6713554228`

4. **拼接分支名**：
   - 格式：`feat/{迭代}-{名称}{ID拼接串}`
   - 单任务示例：`feat/124-axiosRetry功能-m-6713554226`
   - 多任务示例：`feat/124-axiosRetry功能-m-6713554226-m-6713554227-m-6713554228`

**特殊情况处理：**
- 如果规划迭代为空：使用 `unknown` 代替
- 如果卡片名称过长（>50字符）：截断并添加省略标记
- 确保分支名符合Git命名规范（不含空格、特殊字符等）
- 多个ID时，分支名可能较长，但Git支持较长的分支名

## 步骤7：创建并推送分支

（与仓库根目录下技能主文档 `SKILL.md` 的「### 8. 创建并推送分支」一致；本参考文档将「解析链接—飞书—命名—查远程」拆成多步，故此处为步骤 7。）

创建新分支并推送到远程，同时建立追踪关联。

```bash
# 创建并切换到新分支
git checkout -b feat/124-axiosRetry功能-m-6713554226

# 推送到远程并建立追踪关联
git push -u origin feat/124-axiosRetry功能-m-6713554226
```

**重要说明：**
- ✅ 使用 `-u` 参数（`--set-upstream`）建立本地与远程分支的追踪关联
- ✅ 使用正常推送，**绝不使用强推**（`--force` 或 `-f`）
- ✅ 推送后，后续的 `git pull` 和 `git push` 将自动关联到远程分支
- ⚠️ **权限要求**：必须使用 `required_permissions: ["all"]` 来执行 git checkout 和 git push 命令，以确保能够正确写入 `.git/config` 文件来设置追踪关联

**权限说明：**
由于需要修改 git 配置文件来设置分支追踪，必须在执行 `git checkout -b` 和 `git push -u` 时请求完整权限。如果使用受限权限，虽然分支可以推送成功，但追踪关联无法建立，导致后续 `git pull` 时提示没有追踪信息。

**错误处理：**

如果分支已存在：
```bash
# 检查远程分支是否存在
git ls-remote --heads origin feat/124-axiosRetry功能-m-6713554226
```

如果已存在，提示用户：
```
⚠️ 分支 feat/124-axiosRetry功能-m-6713554226 已存在
建议操作：
1. 切换到现有分支：git checkout feat/124-axiosRetry功能-m-6713554226
2. 或使用不同的分支名
```

如果推送成功但追踪关联失败（提示 "could not write config file"）：
```bash
# 手动设置追踪关联
git branch --set-upstream-to=origin/<分支名> <分支名>
```

## 步骤8：确认完成

操作成功后，显示完整的分支信息。

**单任务情况：**
```
✅ 分支创建成功！

📋 分支信息：
  分支名称：feat/124-axiosRetry功能-m-6713554226
  飞书任务：axiosRetry功能
  规划迭代：124
  工作项ID：6713554226
  
🔗 远程分支已创建并关联
💡 你现在可以开始在此分支上进行开发
```

**多任务情况：**
```
✅ 分支创建成功！

📋 分支信息：
  分支名称：feat/124-axiosRetry功能-m-6713554226-m-6713554227-m-6713554228
  飞书任务：axiosRetry功能（主任务）
  规划迭代：124
  关联工作项：
    - 6713554226 (主任务)
    - 6713554227
    - 6713554228
  
🔗 远程分支已创建并关联
💡 你现在可以开始在此分支上进行开发
💡 该分支关联了3个飞书任务
```
