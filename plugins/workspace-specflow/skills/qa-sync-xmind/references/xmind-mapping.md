# XMind ↔ test-spec.md 层级映射规则

适配飞书项目**自由模式**导入（2.4.0+），优化层级深度以确保飞书导入后内容完整可读。

## 设计原则

1. **链式结构**：每个用例采用线性链展开 `用例标题 → 前置条件 → 步骤 → 预期结果`，而非树形分支
2. **MODULE 合并**：MODULE 层级不作为独立节点，而是作为 `【模块名】` 前缀合并到用例标题中
3. **labels 标记**：每个节点使用 XMind labels 标记角色（功能描述/前置条件/步骤/预期结果）
4. **内容聚合**：多条前置条件用 `；` 连接，多步操作用 `\n` 分行，预期结果用 `；` 连接
5. **无编号设计**（决策 QA-D9）：场景不使用序号编号，仅使用描述性标题，以支持 XMind 自由编辑后的 round-trip 同步

## 正向映射：test-spec.md → XMind

### 层级结构

```
test-spec.md 层级                       XMind JSON 结构
─────────────────────────────────────────────────────────────────
# 测试用例：<标题>                       rootTopic.title = "<标题>"
│                                        structureClass = "org.xmind.ui.logic.right"
│
├─ ## MODULE-MS-01: <模块名>            ──────── 不生成独立节点 ────────
│   ├─ ### 场景: <描述>                 children[i].title = "【<模块短名>】<描述>"
│   │                                    children[i].labels = ["功能描述"]
│   │   ├─ **前置条件**:                 children[i].children[0].title = "<条件1>；<条件2>"
│   │   │   - 条件1                      children[i].children[0].labels = ["前置条件"]
│   │   │   - 条件2
│   │   ├─ **操作步骤**:                 children[i].children[0].children[0].title = "1. 步骤1\n2. 步骤2"
│   │   │   1. 步骤1                     children[i].children[0].children[0].labels = ["步骤"]
│   │   │   2. 步骤2
│   │   └─ **预期结果**:                 children[i].children[0].children[0].children[0].title = "<结果1>；<结果2>"
│   │       - 结果1                      children[i].children[0].children[0].children[0].labels = ["预期结果"]
│   │       - 结果2
│   └─ ### 场景: ...                    children[i+1]（同层级，依次排列）
│
├─ ## 回归与兼容性                       模块名提取为"回归兼容"
│   └─ ### 场景: ...                    children[j].title = "【回归兼容】..."
```

### 飞书导入后效果（5 层）

```
用例集 → <标题> → 【模块】用例标题 → 前置条件内容 → 步骤内容 → 预期结果内容
```

### 转换规则详解

#### 1. MODULE 合并规则

| test-spec.md MODULE 标题 | XMind 用例标题前缀 |
|---|---|
| `## MODULE-MS-01: 列表列展示（运营状态后）` | `【列表列展示】` |
| `## MODULE-MS-02: 数据一致性与可追溯` | `【数据一致性】` |
| `## 回归与兼容性` | `【回归兼容】` |

提取规则：取 MODULE 标题中冒号后的内容，截取前 5 个字作为前缀（若无冒号，取前 4 个字）。用 `【】` 包裹。

#### 2. 用例标题生成规则

```
【<模块短名>】<场景描述>
```

示例：
- `### 场景: 运营状态列恢复展示` → `【列表列展示】运营状态列恢复展示`
- `### 场景: 更新时间列空值默认展示` → `【数据一致性】更新时间列空值默认展示`

**注意**：标题中不包含编号，场景描述即为唯一标识。

#### 3. 链式嵌套规则（关键）

每个用例节点内部严格按以下嵌套顺序生成，**不是并列子节点**：

```
用例标题 [功能描述]
  └── 前置条件文本 [前置条件]      ← 用例的唯一直接子节点
      └── 步骤文本 [步骤]          ← 前置条件的唯一直接子节点
          └── 预期结果文本 [预期结果] ← 步骤的唯一直接子节点
```

#### 4. 内容聚合规则

| 字段 | Markdown 格式 | XMind 节点文本 |
|---|---|---|
| 前置条件 | `- 条件A`<br>`- 条件B` | `条件A；条件B` |
| 操作步骤 | `1. 做X`<br>`2. 做Y` | `1. 做X\n2. 做Y` |
| 预期结果 | `- 结果A`<br>`- 结果B` | `结果A；结果B` |

## 反向映射：XMind → test-spec.md

### 层级识别

```
XMind 层级                              test-spec.md 输出
─────────────────────────────────────────────────────────────────
Root                                    # 测试用例：<root.title>
├─ Level 1（label=功能描述）            ### 场景: <从title提取描述>
│   └─ Level 2（label=前置条件）        **前置条件**:\n- <按；拆分>
│       └─ Level 3（label=步骤）        **操作步骤**:\n<按\n拆分>
│           └─ Level 4（label=预期结果） **预期结果**:\n- <按；拆分>
```

### 识别规则

- Level 1 节点 label 含 `功能描述` → 用例标题，提取 `【xxx】` 前缀还原 MODULE 分组，`【】` 之后的部分即为场景描述
- Level 2 节点 label 含 `前置条件` → 映射为 `**前置条件**`，内容按 `；` 拆为多个 `- ` 列表项
- Level 3 节点 label 含 `步骤` → 映射为 `**操作步骤**`，内容按 `\n` 拆为有序列表
- Level 4 节点 label 含 `预期结果` → 映射为 `**预期结果**`，内容按 `；` 拆为多个 `- ` 列表项

**无 label 时的降级识别**（兼容飞书编辑后 label 丢失）：
- Level 2 标题不以数字序号开头 → 推断为前置条件
- Level 3 标题以数字序号开头 → 推断为步骤
- Level 4（链尾节点） → 推断为预期结果

### MODULE 还原规则

从用例标题中的 `【xxx】` 前缀提取模块短名，相同前缀的用例归入同一 MODULE。

```
【列表列展示】运营状态列恢复展示    →  ## MODULE-MS-01: 列表列展示
【列表列展示】更新时间列初始展示        （同一 MODULE）
【数据一致性】更新时间列空值默认展示 →  ## MODULE-MS-02: 数据一致性
【回归兼容】原有列不受影响          →  ## 回归与兼容性
```

MODULE ID 还原策略：
- 若当前 `test-spec.md` 已存在该模块，**沿用原 MODULE ID**
- 若为新增模块（XMind 中编辑新增），按已有 MODULE 最大序号递增

### 新增节点推断

- Level 1 新增 → 新场景（从 `【】` 前缀判断归属 MODULE）
- Level 2~4 新增 → 新前置条件/步骤/预期

## mcp-xmind 调用流程

### 路径探测（必须先执行）

`create_xmind` 的 `path` 受 MCP Server 配置的工作目录限制，不同用户的路径不同。执行前**必须先探测可用目录**：

1. 调用 `list_xmind_directory`（无参数），从返回的文件路径中提取 MCP Server 的工作目录
2. 将该目录作为 `<xmind-workspace>` 用于后续 `create_xmind` 和 `read_xmind` 的 path 参数
3. XMind 文件仅在 MCP 工作目录中存在，**不复制到项目目录**（项目中不保留 `.xmind` 文件）

```json
// Step 1: 探测工作目录
{ "name": "list_xmind_directory", "arguments": {} }
// → 从返回路径提取目录，如 /Users/xxx/xmindDoc/

// Step 2: 若目录下无文件，可尝试直接用项目路径写入
// 若报 Access denied，则改用探测到的工作目录
```

### Export（create_xmind）

```json
{
  "name": "create_xmind",
  "arguments": {
    "path": "<xmind-workspace>/<filename>.xmind",
    "overwrite": true,
    "sheets": [{
      "title": "<需求标题>",
      "rootTopic": {
        "title": "<需求标题>",
        "structureClass": "org.xmind.ui.logic.right",
        "children": [
          {
            "title": "【模块短名】用例描述",
            "labels": ["功能描述"],
            "children": [{
              "title": "前置条件1；前置条件2",
              "labels": ["前置条件"],
              "children": [{
                "title": "1. 步骤1\n2. 步骤2",
                "labels": ["步骤"],
                "children": [{
                  "title": "预期结果1；预期结果2",
                  "labels": ["预期结果"]
                }]
              }]
            }]
          }
        ]
      }
    }]
  }
}
```

生成后执行 `open -a "XMind" <xmind-workspace>/<filename>.xmind` 自动打开。

### Import（read_xmind）

```json
{
  "name": "read_xmind",
  "arguments": {
    "path": "<xmind-workspace>/<filename>.xmind"
  }
}
```

直接从 MCP 工作目录读取（XMind 编辑保存后文件已在此目录中）。
