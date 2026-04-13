---
name: qa-sync-xmind
description: >-
  Use when user mentions: 导出xmind/xmind导出/xmind导入/同步xmind/
  qa-sync-xmind/飞书导入/飞书测试用例/同步回来/回写。
  Triggers when test-spec.md exists (export) or MCP workspace has xmind files (import).
---

# /qa-sync-xmind — test-spec.md ↔ XMind 双向转换

## 前置条件

- MCP Server `mcp-xmind`（`@41px/mcp-xmind`）已配置并可用
- `test/test-spec.md` 存在（export）或 MCP 工作目录中存在 `.xmind` 文件（import）

## 用法

```
/qa-sync-xmind export    # test-spec.md → XMind
/qa-sync-xmind import    # XMind → test-spec.md
```

无参数时，询问方向。

## 核心原则

- **`test-spec.md` 是唯一真相源**（决策 QA-D1）
- **项目目录中不存储 `.xmind` 文件**，XMind 仅在 MCP 工作目录中作为临时编辑介质
- **XMind 文件可随时重新生成**（决策 QA-D6）
- **场景不使用编号**（决策 QA-D9），使用描述性标题作为匹配标识

---

## Export 模式：test-spec.md → XMind

### 生成 JSON 前 MUST（未全部满足不得调用 `create_xmind`）

与 `references/xmind-mapping.md` 正向映射一致；细则、MODULE 短名截取与 JSON 示例以该文件为准。

1. **rootTopic**：`structureClass` 必须为 `org.xmind.ui.logic.right`；`title` 与 sheet/用例集标题一致（来自 `# 测试用例：<标题>`）。
2. **MODULE 不得出现为独立节点**：`## MODULE-...` 只用于推导 `【模块短名】`，合并进每个场景对应的一级子节点标题，格式为 `【模块短名】场景描述`，不单独生成 MODULE 分支。
3. **链式嵌套（禁止并列）**：每个用例节点下**仅一条**深度为 4 的链：`用例标题 [功能描述] → 前置条件 [前置条件] → 步骤 [步骤] → 预期结果 [预期结果]`。禁止把「前置条件 / 步骤 / 预期结果」做成同一父节点下的多个并列子节点。
4. **labels**：上述四级节点依次使用 `["功能描述"]`、`["前置条件"]`、`["步骤"]`、`["预期结果"]`。
5. **内容聚合**：多条前置条件、多条预期结果在节点 `title` 中用中文分号 `；` 连接；多步操作在节点 `title` 中用换行 `\n` 分隔（保留 `1. ` `2. ` 等序号行）。
6. **无编号场景**（QA-D9）：场景标题为描述性文本，**不**在标题中加用例序号编号。

自检：生成前在脑中或草稿中核对——飞书导入后层级是否为「用例集 → 需求标题 → 【模块】用例 → 前置条件 → 步骤 → 预期结果」共 5 层（见 mapping 文档「飞书导入后效果」）。

### 流程

1. **定位需求目录**：扫描 `requirements/` 下 `test_spec.status = confirmed` 的需求，或用户指定
2. **读取 test-spec.md**：解析 Markdown 层级结构
3. **探测 MCP 工作目录**：调用 `list_xmind_directory`（无参数），从返回路径提取目录
4. **构建 XMind JSON**：严格按上文 **MUST** 与 `references/xmind-mapping.md` 正向映射转换
5. **调用 `create_xmind`**：生成到 MCP 工作目录（`<xmind-workspace>/<需求短名>-test-cases.xmind`）
6. **自动打开**：执行 `open -a "XMind" <生成路径>` 打开文件
7. **提示后续操作**：
   - 飞书导入：从 MCP 工作目录选取文件，飞书项目 → 测试用例 → 导入 XMind 用例 → 自由模式
   - XMind 编辑后回写：保存后执行 `/qa-sync-xmind import`

---

## Import 模式：XMind → test-spec.md

### 流程

1. **探测 MCP 工作目录**：调用 `list_xmind_directory`（无参数）
2. **定位 XMind 文件**：找到 MCP 工作目录中最近修改的 `.xmind` 文件（若有多个，列出供用户选择）
3. **调用 `read_xmind`**：读取完整 XMind 结构
4. **反向映射为 Markdown**：按 `references/xmind-mapping.md` 中的反向映射和识别规则转换
5. **Diff 对比**：读取当前 `test-spec.md`，与转换结果对比，生成变更摘要
6. **展示变更摘要**：展示新增/修改/删除，等待用户确认
7. **写入**：确认后覆盖 `test/test-spec.md`，更新 `metadata.yaml` 中 `test_spec.confirmed_at` 时间戳

### 变更摘要格式

```markdown
## 变更摘要

### 新增 (N)
+ 【模块名】新增用例标题

### 修改 (N)
~ 【模块名】用例标题
  字段: "旧值" → "新值"

### 删除 (N)
- 【模块名】被删除的用例标题

### 无变更的用例 (N)
（折叠不显示）

确认写入 test-spec.md？
```

### Diff 对比规则

- **场景标题匹配**：按场景描述性标题匹配新旧用例（去除 `【模块名】` 前缀后的文本作为匹配 key）
- **逐字段对比**：对比前置条件、操作步骤、预期结果的文本内容
- **新增检测**：XMind 中有但 test-spec.md 中无的场景标题
- **删除检测**：test-spec.md 中有但 XMind 中无的场景标题
- **修改检测**：标题匹配但内容有差异
- **模糊匹配降级**：若精确匹配未命中，尝试对标题做子串 / 编辑距离相似度匹配（阈值 ≥ 0.8），标记为"疑似修改"供人工确认

**映射规则详情**：读取 `references/xmind-mapping.md`。

## 依赖

- `mcp-xmind` MCP Server（`@41px/mcp-xmind` v2.1.0+，MIT 开源）

## 约束

- test-spec.md 是唯一真相源（决策 QA-D1）
- 项目目录不存储 `.xmind` 文件，XMind 仅在 MCP 工作目录中临时存在
- **Export**：`create_xmind` 前必须满足上文「生成 JSON 前 MUST」全部项
- Import 模式必须展示 diff 并获得人工确认（决策 QA-D8）
- 场景标题必须唯一且具有描述性（决策 QA-D9），作为 round-trip 匹配标识
