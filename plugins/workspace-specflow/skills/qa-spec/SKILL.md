---
name: qa-spec
description: >-
  Use when user mentions: 测试spec/qa-spec/测试用例/生成测试/写测试文档/导出xmind。
  Triggers when prd.status is confirmed and test_spec.status is pending.
---

# /qa-spec — prd.md → 测试 spec（+ 可选 XMind 导出）

## 前置条件

- `metadata.yaml` 中 `prd.status` 为 `confirmed`
- `test_spec.status` 为 `pending`

## 流程

### Step 0: 确保 specs 仓库最新

提示用户在 specs 仓库目录执行 `git pull`，确保 prd.md 是产品团队提交的最新版本。可通过 `git status` 检测是否 behind remote，若 behind 则**必须先提示 pull**。

### Step 1: 定位需求

**自动模式**：扫描 `requirements/` 下 prd 已确认且测试 spec 为 pending 的需求。
**手动模式**：用户直接指定路径。

### Step 2: 读取 prd.md

读取 `prd.md` 全文。

**⛔ 输入隔离（决策 D5）**：禁止读取 `openspec/changes/` 下任何开发产出。唯一输入来源：prd.md + 原型（如有）。

### Step 3: 扫描前后端现状（业务层面）

从 `workspace-repos.json` 解析仓库路径，扫描关键结构，识别可测试的业务行为、操作路径、多端覆盖场景、边界情况。

### Step 4: Brainstorming

调用 `superpowers:brainstorming`，引导测试同学设计测试策略：核心场景、边界与异常、多端覆盖、数据兼容性、特殊约束。

### Step 5: AI 生成测试 spec

**生成原则**：
1. 覆盖 prd.md 中所有功能点，按"页面从上到下、从左到右"划分，不遗漏
2. 仅围绕真实功能点生成，不添加无关用例
3. 预期结果只保留一个成立条件
4. MODULE ID 与 prd.md 严格一致（决策 D22）
5. 测试步骤描述业务操作（决策 D24）
6. **场景不使用编号**，仅使用描述性标题（决策 QA-D9），便于 XMind 编辑后 round-trip 同步

**参考资料**：读取 `references/test-writing-guide.md` 获取十大类功能书写要求（输入类、选择类、点击类、展示类、切换类、表格类、计算类、反馈类、时间日期类、文件导入导出类），按功能点类型补充对应的测试场景。

**输出格式**：

```markdown
# 测试用例：<需求标题>

> 来源产品 spec: requirements/<requirement>/prd.md
> 确认时间: YYYY-MM-DD

## MODULE-MS-01: <模块名称>

### 场景: <正常流程描述>
**测试类型**: 功能测试
**覆盖端**: 运营后台
**前置条件**:
- 条件1
**操作步骤**:
1. 步骤1
**预期结果**:
- 结果1

### 场景: <边界情况描述>
**测试类型**: 边界测试
...
```

测试类型优先级：功能测试 > 边界测试 > 其他按需。
场景标题必须唯一且有描述性，作为 XMind round-trip 时的匹配标识。

### Step 6: 逐段 review

按 MODULE 逐个展示测试场景，测试同学可补充修改。

### Step 7: 覆盖率校验

AI 对照 prd.md 每条验收标准：✅ 已覆盖（标注场景标题）/ ❌ 未覆盖（需补充或标记不适用）。

### Step 8: 确认 & 写入

写入 `test/test-spec.md`，更新 `metadata.yaml`：`test_spec.status = confirmed`。

### Step 9: XMind 导出（可选）

询问是否生成 XMind 文件用于导入飞书项目或在 XMind 中编辑。如果确认，执行 `/qa-sync-xmind export` 流程：

1. 读取 `test/test-spec.md`
2. 按映射规则转换（**参考** qa-sync-xmind 技能的 `references/xmind-mapping.md`）
3. 探测 MCP 工作目录，调用 `create_xmind` 生成到 MCP 工作目录（**不复制到项目目录**）
4. 自动用 `open -a "XMind"` 打开文件
5. 提示：
   - 飞书导入：进入飞书项目 → 测试用例 → 导入 XMind 用例 → 选择"自由模式"，从 MCP 工作目录选取文件
   - XMind 编辑后回写：编辑保存后执行 `/qa-sync-xmind import` 同步回 `test-spec.md`

**注意**：项目目录中不保存 `.xmind` 文件，`test-spec.md` 是唯一真相源。

### Step 10: Case Flow 上传（可选）

询问是否将用例上传至 Case Flow 快速模式执行。如果确认，提示用户执行 **`/qa-execute`**（或在本步直接调用 qa-execute 技能流程）：

1. 读取 `test/test-spec.md`（或当前打开的 `test/*.md`）
2. 自动识别格式：`test-spec` 转换为 6 级嵌套列表，或 Case Flow 嵌套列表直传
3. 上传成功后输出 Session 接力 ID，引导用户在 `https://ai-case-flow.yc345.tv/quick` 底部粘贴进入

**典型顺序**：`/qa-spec` → （可选 `/qa-sync-xmind`）→ **`/qa-execute`**

## 依赖

- `superpowers:brainstorming`（Step 4）
- `mcp-xmind`（Step 9，可选）— MCP Server: `@41px/mcp-xmind`
- Python 3.9+、`curl`（Step 10，可选）— 用于 `/qa-execute` 上传 Case Flow

## 约束

- 输入隔离：绝不读取开发 spec 或 change 目录（决策 D5）
- MODULE ID 与 prd.md 一一对应（决策 D22）
- test-spec.md 是唯一真相源，XMind 是派生产物（决策 QA-D1）
