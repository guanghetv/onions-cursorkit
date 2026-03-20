---
name: aicr-local
description: AI代码审查技能（本地版）。从Git暂存区或GitLab MR链接获取变更，基于团队规范、业务spec和工作区上下文进行审查，输出极简的问题与建议。使用/cr命令触发。
license: MIT
compatibility: 需要Git环境；暂存区模式需暂存区有内容，MR模式需本地有对应项目
metadata:
  author: AI-CodeReview
  version: "1.1.0"
  source: 基于conf/prompt_templates.yml和团队规范文档
---

# AI代码审查技能（AICR Local）

AI驱动的代码审查工具，集成团队规范、业务需求和上下文分析，提供极简的审查反馈。

## 重要：资源路径说明

**技能内置资源（从技能目录读取，不要在工作区搜索）**：
- `references/frontend_standard.md` - 前端规范（技能目录）
- `references/backend_standard.md` - 后端规范（技能目录）
- `references/review_guidance.md` - 审查维度说明（技能目录）
- `references/troubleshooting.md` - 常见问题（技能目录）
- `assets/prompt_template.yml` - 提示词模板（技能目录）

**工作区资源（从工作区读取）**：
- `openspec/specs/` - 业务需求规格文档（工作区）
- `.cursor/rules/` - 项目规则（工作区）
- 业务代码文件 - 需要审查的代码（工作区）

使用 Read 工具时，明确区分资源位置：
- 技能内置资源：使用相对于技能根目录的路径
- 工作区资源：使用工作区的相对路径或绝对路径

## 何时使用此技能

**手动触发**：通过 `/cr` 命令调用，支持两种输入形式：
- `/cr` — 从 Git 暂存区获取变更（开发自审）
- `/cr <GitLab MR 链接>` — 从 MR 获取变更（MR Review）

适用场景：
- 提交代码前进行快速审查（暂存区模式）
- 对 GitLab MR 进行代码审查（MR 模式）
- 验证代码是否符合团队规范
- 检查实现是否符合业务需求（spec）
- 发现潜在的安全风险和性能问题
- 查找变更的影响范围，避免遗漏修改点

## 前置条件

**暂存区模式**（`/cr`）：Git 暂存区有内容（已执行 `git add`）。

```bash
git add <files>
/cr
```

**MR 模式**（`/cr <MR链接>`）：本地已 clone 该 MR 所在仓库并用 Cursor 打开（无需在 MR 的任何分支上，也无需 `git add`）。

```bash
/cr https://gitlab.yc345.tv/backend/foo/-/merge_requests/123
```

## 审查流程

### 步骤 1: 获取变更

根据触发方式获取变更，统一产出 **diffs_text**（diff 文本）、**file_paths**（变更文件列表）、**input_mode**（`staged` | `mr`）。

#### 无 MR 链接时（暂存区模式，input_mode=staged）

使用 Shell 工具执行 `git diff --cached` 获取暂存区的所有变更内容。

如果暂存区为空，提示："暂存区为空，请先使用 git add 添加需要审查的文件"。

#### 有 GitLab MR 链接时（MR 模式，input_mode=mr）

**1) 解析链接**：从 MR 链接中提取 `host`、`project_path`、`merge_request_iid`。

支持格式：`https://<host>/<group>/<repo>/-/merge_requests/<iid>`（含多级 group，如 `org/sub-group/repo`）。

若链接格式无法识别，提示："无法识别的 MR 链接格式，请提供 GitLab MR 链接（如 `https://gitlab.example.com/group/repo/-/merge_requests/123`）"。

**2) 仓库匹配检查**：执行 `git remote get-url origin`，比对其中的 project_path 与 MR 链接的 project_path。若不一致，输出：

```
⚠️ 当前工作区（<当前 project_path>）与 MR 所属仓库（<MR project_path>）不一致，影响范围分析可能不准确。若后续 fetch 失败，请在 MR 所在仓库目录中重新执行
```

**不阻断**，继续执行。

**3) 获取 source_branch 和 target_branch**：

先检查环境变量 `GITLAB_TOKEN`（或 `GITLAB_PRIVATE_TOKEN`）是否存在：

```bash
test -n "${GITLAB_TOKEN:-$GITLAB_PRIVATE_TOKEN}"
```

- **有 Token** → 调用 GitLab API：
  ```bash
  curl -s --header "PRIVATE-TOKEN: ${GITLAB_TOKEN:-$GITLAB_PRIVATE_TOKEN}" \
    "https://<host>/api/v4/projects/<url_encoded_project_path>/merge_requests/<iid>"
  ```
  从返回 JSON 中提取 `source_branch` 和 `target_branch`。

- **无 Token 或 API 失败** → 提示用户提供 source_branch 和 target_branch（不要裸调 API，GitLab 私有项目未授权会 404）。用户提供后，继续执行下方第 4) 步获取 diff。

**4) 获取 diff**：

```bash
git fetch origin <source_branch> <target_branch>
git diff origin/<target_branch>...origin/<source_branch>
```

若 `git fetch` 失败（exit code ≠ 0），输出：

```
🔴 无法获取 MR 源分支 <source_branch>，请检查 git 凭证或仓库访问权限
```

**终止审查**。

成功后，用 `git diff --name-only origin/<target_branch>...origin/<source_branch>` 获取 file_paths。

**5) 检测当前分支状态**：

```bash
current_branch=$(git branch --show-current)
git status --porcelain
```

若 `current_branch` == `source_branch` 且 `git status --porcelain` 输出为空（无未提交变更），设置 **`on_source_branch = true`**；否则为 `false`。

此标志影响后续步骤：
- 步骤 7：影响范围分析的可靠性
- 步骤 10：报告中文件位置是否可直接点击跳转

### 步骤 2: 判断代码类型

分析变更文件（file_paths）的扩展名，判断代码类型：
- **前端代码**：`.ts`, `.tsx`, `.js`, `.jsx`, `.vue`, `.html`, `.css`, `.scss`
- **后端代码**：`.go`, `.py`, `.java`, `.rs`, `.rb`
- **混合代码**：同时包含前后端文件

### 步骤 3: 加载对应规范文档

**从技能目录读取**（不要在工作区搜索）：

使用 Read 工具根据代码类型加载规范：
- 前端代码（`.ts`, `.tsx`, `.js`, `.jsx`, `.vue` 等）→ 读取技能目录下的 `references/frontend_standard.md`
- 后端代码（`.go`, `.py`, `.java`, `.rs` 等）→ 读取技能目录下的 `references/backend_standard.md`
- 混合代码 → 同时读取技能目录下的两个规范文档
- 原生移动端代码（`.swift`, `.kt`, `.java`[Android], `.ets`[HarmonyOS]）→ 不加载规范文档，直接使用业内推荐规范（如Swift官方风格指南、Kotlin编码规范、Google Java Style等）

**重要**：规范文档位于本技能的 `references/` 目录中，使用相对于技能根目录的路径读取，例如：
- `<技能根目录>/references/frontend_standard.md`
- `<技能根目录>/references/backend_standard.md`

### 步骤 4: 检查是否有 Spec 文档

检查以下情况：
1. 变更（diffs_text / file_paths）中是否包含 `openspec/specs/` 路径的文件
2. 用户在对话中是否使用 @ 引用了 spec 文档
3. 暂存区模式下可选：使用 `git log -5 --name-only` 检查最近5次提交是否包含 `openspec/specs/` 路径

### 步骤 5: 加载 Spec 文档（如果有）

如果发现相关 spec，使用 Read 工具读取**工作区中的** spec 文档完整内容作为业务需求背景。

**注意**：Spec 文档在工作区的 `openspec/specs/` 目录下，不在技能目录中。

**当 input_mode=mr 时**：不搜工作区 `openspec/specs/`、不查 `git log`。仅以下两种来源：
1. MR 的 diff 中包含 `openspec/specs/` 下的文件 → 使用 `git show origin/<source_branch>:<spec_path>` 获取完整 spec 内容作为 spec_content（diff 只含变更片段，不是完整文档）。
2. 用户在对话中通过 @ 引用了 spec 文档 → 使用该文档。

若两者均无，则本轮不注入 spec_content，跳过业务需求审查维度。

### 步骤 6: 加载项目规则

尝试读取**工作区中的** `.cursor/rules/` 目录下的项目规则文件（如果存在）。

**注意**：项目规则在工作区根目录的 `.cursor/rules/` 下，不在技能目录中。

**当 input_mode=mr 时**：仍从当前工作区读取项目规则，但当前分支可能不是 MR 分支，规则可能与 MR 分支不完全一致。

### 步骤 7: 收集工作区上下文

**在工作区中搜索**（不在技能目录中）：

**精准搜索**（使用 Grep 工具）：
- 搜索被修改的函数名、类名的所有引用位置
- 限制搜索范围，避免上下文过载

**语义搜索**（使用 SemanticSearch）：
- 查找与变更相关的代码文件
- 重点关注可能受影响的模块

**策略**：优先收集直接相关的内容，按需加载，避免超出上下文限制。

**当 input_mode=mr 时**：
- 若 `on_source_branch = true`：工作区与 MR 源分支一致且无本地变更，影响范围分析结论可靠，无需额外注明。
- 若 `on_source_branch = false`：工作区可能不在 MR 源分支上，影响范围分析结论仅供参考。若审查产出了影响范围结论，在报告末尾注明："以上影响范围分析基于当前工作区，当前分支可能非 MR 源分支，结论仅供参考"。

#### MR 模式与暂存区模式的步骤 4–7 差异

| 步骤 | 暂存区模式（staged） | MR 模式（mr） |
|------|----------------------|---------------|
| 4–5 Spec | 搜工作区 openspec + @ + git log | 仅 diff 内 spec 或用户 @ |
| 6 规则 | 工作区 .cursor/rules | 同左，可能非 MR 分支 |
| 7 影响范围 | 工作区 = 被审分支 | on_source_branch=true 时可靠；否则仅供参考 |

### 步骤 8: 加载提示词模板

**从技能目录读取**（不要在工作区搜索）：

从本技能的 `assets/prompt_template.yml` 读取提示词模板。

**重要**：使用相对于技能根目录的路径：`<技能根目录>/assets/prompt_template.yml`

### 步骤 9: 构建完整审查提示词

组合以下内容：
- system_prompt：审查目标、输出格式要求
- user_prompt：file_paths、diffs_text
- team_standards：前后端规范文档
- spec_content：业务需求规格（如果有）
- project_rules：项目规则（如果有）
- context：工作区相关代码（精简后）

### 步骤 10: 执行审查并输出报告

基于构建的提示词进行审查，输出极简报告。

## 三维度审查逻辑

### 1. 基础规范审查

检查代码是否符合团队规范。

**规范文档位置**（从技能目录读取）：
- 前端：`<技能根目录>/references/frontend_standard.md`
- 后端：`<技能根目录>/references/backend_standard.md`

核心关注点：命名规范、代码格式、错误处理、类型使用、数据库和缓存使用、并发安全等。

### 2. 业务需求审查

当存在 spec 文档时，验证实现是否符合 spec 要求：

**检查项**：
- ✅ 是否实现了所有 Requirements
- ✅ 是否覆盖了所有 Scenarios
- ✅ 业务逻辑是否与 spec 描述一致
- ✅ 接口契约是否符合 spec 定义
- ✅ 边界条件和错误场景处理是否正确

**如何识别 spec**：
1. 变更中包含 `openspec/specs/` 路径的文件
2. 用户使用 @ 引用了 spec 文档
3. 暂存区模式下：使用 `git log -5 --name-only` 检查最近提交（可选）
4. MR 模式下：仅第 1、2 项，不搜工作区、不查 git log

**注意**：Spec文档在工作区的 `openspec/specs/` 目录，不在技能目录中。

### 3. 影响范围审查

检查变更对工作区其他部分的影响，避免遗漏修改点：

**检查项**：
- ✅ 被修改函数/类的所有调用位置是否已适配
- ✅ API签名变更是否影响其他模块
- ✅ 数据结构变更是否需要迁移脚本
- ✅ 是否引入了循环依赖
- ✅ 配置变更是否需要更新文档

**审查策略**：
- 使用 Grep 精确搜索函数名、类名
- 使用 SemanticSearch 查找相关模块
- 限制范围，优先关注高频调用和关键路径

### 4. 安全风险检测

特别关注可能导致安全问题的代码模式。

详见技能目录下的 `references/review_guidance.md` 完整说明。

**XSS 风险关键词（前端）**：
- `innerHTML`、`outerHTML`
- `document.write`、`eval()`
- `v-html`、`dangerouslySetInnerHTML`

**SQL 注入风险（后端）**：
- 字符串拼接 SQL
- 未使用参数化查询

**敏感信息**：
- 密码、密钥明文存储
- 根域名直接使用（如 `yangcong345.com`）

## 审查报告格式

### 极简主义原则

**只输出问题，不说废话。符合规范的内容不要提及。**

仅当发现以下情况时才输出：
- 🔴 严重问题（安全风险、规范违反、功能缺陷）
- 🟠 改进建议（可优化的点）

如果代码没有任何问题或建议，输出：
```markdown
✅ 无明显问题
```

**禁止输出**：
- ❌ "整体评价"、"代码质量优秀"等总结性评价
- ❌ "✅ 符合规范"、"✅ 一致性良好"等肯定性描述
- ❌ "命名：符合XX规范"、"TypeScript：符合规范"等分类总结
- ❌ "总分"、"评分"或任何形式的打分
- ❌ 已经做对的内容（除非是为了对比说明问题）
- ❌ **输出"✅ 无明显问题"后的任何内容（必须立即停止）**

### 格式规范

- **严重问题**：🔴 + 极简描述 + 文件位置
- **改进建议**：🟠 + 极简描述 + 文件位置
- **无问题**：输出 "✅ 无明显问题"

### 文件位置格式（可点击）

使用 Cursor 可识别的格式，点击即可跳转到对应行：

**推荐格式**：
```
相对路径:行号
例：src/utils/helper.ts:42
```

**或 Markdown 链接**：
```
[相对路径:行号](相对路径#L行号)
例：[src/utils/helper.ts:42](src/utils/helper.ts#L42)
```

**可选列号**：
```
相对路径:行号:列号
例：src/utils/helper.ts:42:10
```

**MR 模式文件位置行为**：
- **`on_source_branch = true`**（当前在 MR 源分支且无本地变更）：报告中的文件位置使用上述可点击格式，行号与本地文件一致，点击可直接跳转到对应行。
- **`on_source_branch = false`**（当前不在 MR 源分支或有本地变更）：报告中仍使用 `相对路径:行号` 格式，但在报告末尾追加提示：

```
💡 当前工作区非 MR 源分支，文件位置行号对应 MR 源分支，点击跳转可能不准确。可切换到源分支（git checkout <source_branch>）后重新审查以获得准确跳转。
```

### 输出示例

**有问题时（只输出问题和建议）**：
```markdown
🔴 使用innerHTML存在XSS风险 — src/components/UserProfile.tsx:42
🟠 建议使用const替代let — src/utils/helper.ts:15
🟠 函数命名应使用camelCase — src/services/api.go:88
```

或使用可点击链接：
```markdown
🔴 使用innerHTML存在XSS风险 — [src/components/UserProfile.tsx:42](src/components/UserProfile.tsx#L42)
🟠 建议使用const替代let — [src/utils/helper.ts:15](src/utils/helper.ts#L15)
```

**无问题时**：
```markdown
✅ 无明显问题
```

**注意**：不要输出"整体评价"、"代码质量优秀"、"✅ 符合规范"等肯定性内容。

## 常见问题

常见问题和解决方案详见技能目录下的 `references/troubleshooting.md`。

快速参考：
- **暂存区为空**：先执行 `git add <files>`
- **审查结果过于简短**：极简输出是设计的，只关注核心问题
- **可以审查未暂存的文件吗**：不可以，必须先 `git add`
- **MR 模式行号对应哪个分支**：对应 MR 源分支。若检测到当前在源分支且无本地变更（`on_source_branch = true`），文件位置可直接点击跳转；否则行号可能与当前分支不一致，报告末尾会有提示
- **MR 模式提示权限错误**：检查 git 凭证（SSH key 或 credential）是否有该仓库的访问权限

## 使用步骤

### 暂存区模式

1. 添加文件到暂存区：`git add src/components/UserProfile.tsx`
2. 在 Cursor Agent 中输入：`/cr`
3. 查看审查报告，点击文件位置跳转到对应行。
4. 修复后重新审查：`git add <fixed-files>` → `/cr`

### MR 模式

1. 在 Cursor 中打开 MR 所在项目。
2. 在 Cursor Agent 中输入：`/cr https://gitlab.yc345.tv/backend/foo/-/merge_requests/123`
3. 查看审查报告。若当前在 MR 源分支且无本地变更，报告中的文件位置可直接点击跳转；否则行号对应 MR 源分支，点击可能不准确。

## 维护说明

### 文档来源

- `references/frontend_standard.md` ← `conf/frontend_code_standard_zh.md`
- `references/backend_standard.md` ← `conf/backend_code_standard_zh.md`
- `assets/prompt_template.yml` ← 改编自 `conf/prompt_templates.yml`

### 更新策略

当团队规范或提示词模板更新时，需要手动同步到 skills 内部，确保审查标准与团队保持一致。

### 版本历史

- v1.0.0 (2026-02-10): 初始版本，支持三维度审查、极简输出、可点击链接
- v1.1.0 (2026-03-18): 支持 `/cr <GitLab MR 链接>` MR 模式；在源分支上时报告文件位置可点击跳转
