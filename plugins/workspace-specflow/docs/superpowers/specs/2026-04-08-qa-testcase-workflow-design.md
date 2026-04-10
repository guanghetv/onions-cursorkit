# 测试用例管理工作流优化设计

> 设计确认时间: 2026-04-08
> 配套设计文档: `2026-04-07-workspace-specflow-design.md`

## 1. 背景与目标

### 1.1 现状痛点

当前测试用例管理流程涉及 5 个环节、4 次手动复制粘贴、3 个外部工具：

```
飞书 PRD ──贴链接──► 测试平台 ──Coze工作流──► Markdown
                                                │
                                          手动复制粘贴①
                                                ▼
                                           XMind APP
                                          (人工调整)
                                                │
                              ┌─── 手动复制粘贴② ──┤── 手动复制粘贴③ ───┐
                              ▼                   │                    ▼
                        飞书项目测试用例            │              Cursor
                        (执行/关联/存档)            │           (生成 spec MD)
                                                  │                    │
                                                  │              手动复制粘贴④
                                                  │                    ▼
                                                  └──────────► 开发自测用
```

具体问题：

- **工具链断裂**：Coze → XMind → 飞书项目 → Cursor，每次切换都需要手动搬运数据
- **Coze 生成质量有限**：单次调用、无代码库上下文、无对话引导，生成的用例主要作为起点，测试同学需要在 XMind 中做大量补充调整
- **真相源分散**：测试用例同时存在于 XMind 文件、飞书项目、Cursor MD 中，无法确定哪个是最新版本
- **开发自测路径冗长**：测试用例要经过多次手动搬运才能到达开发手中

### 1.2 约束条件

| 约束 | 说明 |
|------|------|
| 飞书项目不可替代 | 测试用例在飞书项目中用于执行管理、用例存档、需求/缺陷关联，是全功能使用 |
| 飞书项目导入仅支持 XMind | Excel 导入效果不好（已验证），无公开的测试用例创建 API |
| 飞书项目支持自由模式导入 | 2.4.0+ 版本支持任意层级结构的 XMind 导入，不限制层级 |
| 测试同学对 Cursor 编辑持观望态度 | 习惯了 XMind 可视化方式，需要过渡期 |
| Coze 提示词可迁移 | 内容可控，可直接复用到 Cursor skill 中 |

### 1.3 目标

1. **消除所有手动复制粘贴**：数据流全部自动化
2. **提升 AI 生成质量**：利用代码库扫描、brainstorming 对话、MODULE 结构化等上下文
3. **建立唯一真相源**：`test-spec.md` 是测试用例的唯一真相，所有下游从它派生
4. **保留飞书项目功能不变**：通过自动生成 XMind 文件实现无缝导入
5. **兼容测试同学习惯**：提供纯 Cursor 和 XMind 混合两种工作模式

---

## 2. 目标架构

### 2.1 简化后的流程

```
飞书 PRD
    │ feishu-mcp 自动读取
    ▼
/qa-spec（Cursor 中）
    │ AI 生成 + brainstorming + 代码库扫描
    │ 测试同学逐段 review 确认
    ▼
test-spec.md（唯一真相源）
    │
    ├──► mcp-xmind 自动生成 .xmind ──► 导入飞书项目
    │         ▲                         (执行/关联/存档)
    │         │ 可选：测试同学在 XMind 中额外调整后
    │         └─ mcp-xmind 读取 → 反向同步 test-spec.md
    │
    └──► pull-spec（workspace-aware）──► qa-spec.md ──► 开发自测
```

### 2.2 与 workspace-specflow 的关系

本设计不新增独立系统，而是增强已规划的 `/qa-spec` 技能并新增 XMind Bridge 能力：

| 组件 | workspace-specflow 已有设计 | 本次增强 |
|------|---------------------------|----------|
| `/qa-spec` | 基于 PRD 生成 test-spec.md（8 步流程） | + 吸收 Coze 提示词经验 + 代码库深度扫描 + 更强的 brainstorming 引导 |
| test-spec.md | 已有模板定义（MODULE 结构） | 不变 |
| `pull-spec`（执行层） | 同步 test-spec → qa-spec.md | 增强为 workspace-aware（决策 D35/D36） |
| `/qa-sync-xmind`（新增） | 无 | mcp-xmind 集成，test-spec.md ↔ XMind 双向转换 |

---

## 3. `/qa-spec` 技能增强

### 3.1 输入增强（对比 Coze）

| 维度 | Coze 工作流 | `/qa-spec` 增强版 |
|------|------------|-------------------|
| 需求输入 | 飞书文档链接（单一来源） | prd.md（已经过 `/pm-spec` 结构化增强，MODULE 分明） |
| 代码上下文 | 无 | 扫描前后端仓库，识别可测试的业务行为、入口、多端覆盖 |
| 历史参考 | 无 | `_archive/` 中的历史需求 + 历史测试经验 |
| 交互方式 | 单次调用，无对话 | brainstorming 多轮对话，测试同学可逐步补充策略 |
| 提示词管理 | Coze 平台维护 | Skill 内维护（Git 版本控制，可迭代优化，可 code review） |

### 3.2 交互流程

在 workspace-specflow 已设计的 `/qa-spec` 8 步流程基础上，末尾增加 XMind 导出步骤：

**Step 1-8**：不变（定位需求 → 读取 PRD → 扫描仓库 → brainstorming → AI 生成 → 逐段 review → 覆盖率校验 → 确认写入 test-spec.md）

**Step 9（新增）：XMind 导出**

```
Step 9: XMind 导出
    ├─ 询问："是否需要生成 XMind 文件用于导入飞书项目？"
    │
    ├─ 确认 → 调用 mcp-xmind 的 create_xmind
    │    ├─ 按 MODULE 结构转换为 XMind 层级
    │    └─ 输出到 requirements/<requirement>/test/test-cases.xmind
    │
    └─ 提示：
         "XMind 文件已生成于 test/test-cases.xmind，可直接导入飞书项目。
          如需在 XMind 中调整后同步回来，完成后执行 /qa-sync-xmind import"
```

### 3.3 Coze 提示词迁移策略

Coze 的提示词直接嵌入 `/qa-spec` 的 SKILL.md 中，作为 Step 5（AI 生成测试 spec）的生成指令。同时叠加 workspace-specflow 提供的额外上下文：

- MODULE 结构（从 prd.md 继承）
- 代码库扫描结果（可测试的业务行为和入口）
- brainstorming 结论（测试策略、重点场景、边界情况）

预期质量显著优于 Coze 的单次调用。

---

## 4. XMind Bridge 设计

### 4.1 技术选型

使用 `@41px/mcp-xmind`（v2.1.0）作为 XMind 文件操作的核心组件：

| 属性 | 值 |
|------|-----|
| 协议 | MIT（完全开源免费） |
| 包大小 | 55.1 KB |
| 能力 | 读取 + 创建 XMind 文件 |
| 接口 | MCP 协议，可在 Cursor 中直接调用 |
| 依赖 | 无需 XMind 在线服务或 API key，纯离线操作 |

### 4.2 新增命令：`/qa-sync-xmind`

提供 test-spec.md ↔ XMind 的双向转换能力。

**正向导出（export）**：test-spec.md → XMind

```
/qa-sync-xmind export
    │
    ├─ 定位需求目录（自动 / 手动指定）
    ├─ 读取 test/test-spec.md
    ├─ 按层级映射规则转换为 XMind JSON 结构
    ├─ 调用 mcp-xmind create_xmind
    └─ 输出 test/test-cases.xmind
```

**反向导入（import）**：XMind → test-spec.md

```
/qa-sync-xmind import
    │
    ├─ 定位需求目录
    ├─ 调用 mcp-xmind read_xmind 读取 test/test-cases.xmind
    ├─ 解析层级结构，按映射规则转换为 Markdown
    ├─ 与当前 test-spec.md diff 对比，展示变更摘要
    ├─ 测试同学确认变更
    └─ 覆盖写入 test-spec.md + 更新 metadata.yaml 时间戳
```

### 4.3 XMind 层级映射规则

采用飞书项目的**自由模式**导入（2.4.0+），不限制层级结构，兼容性最好：

```
XMind 层级                          test-spec.md 对应
─────────────────────────────────────────────────────
Root（根节点）                       # 测试用例：<需求标题>
  ├─ Level 1（子主题）               ## MODULE-N: <模块名>
  │    ├─ Level 2（子主题）          ### 场景 N.M: <场景描述>
  │    │    ├─ Level 3: 测试类型     **测试类型**: ...
  │    │    ├─ Level 3: 覆盖端       **覆盖端**: ...
  │    │    ├─ Level 3: 前置条件     **前置条件**: ...
  │    │    ├─ Level 3: 操作步骤     **操作步骤**: ...
  │    │    └─ Level 3: 预期结果     **预期结果**: ...
  └─ 跨模块场景                      ## 跨模块场景
       └─ ...                        ### 场景 X.N: ...
```

### 4.4 XMind 文件存放位置

```
requirements/<requirement>/
  ├─ prd.md
  ├─ metadata.yaml
  └─ test/
       ├─ test-spec.md          ← 唯一真相源
       └─ test-cases.xmind     ← 派生产物（可重新生成）
```

`test-cases.xmind` 是 `test-spec.md` 的派生产物，可随时从 test-spec.md 重新生成。Git 中可选择是否跟踪（建议 `.gitignore` 排除，因为二进制文件对 diff 不友好）。

---

## 5. 测试同学工作模式

### 5.1 模式 A：纯 Cursor 模式（推荐，最简）

```
测试同学打开 specs 工作区
    │
    ▼
执行 /qa-spec（AI 生成 + brainstorming 对话 + 逐段 review）
    │
    ▼
在 Cursor 中直接编辑 test-spec.md（增删场景、调整结构、细化步骤）
    │
    ▼
执行 /qa-sync-xmind export（自动生成 .xmind）
    │
    ▼
打开飞书项目 → 导入 XMind 用例 → 完成
```

**步骤数**：3 步（qa-spec → 编辑 → 导出导入）

### 5.2 模式 B：XMind 混合模式（过渡期兼容）

```
测试同学打开 specs 工作区
    │
    ▼
执行 /qa-spec（AI 生成 + brainstorming 对话）
    │
    ▼
执行 /qa-sync-xmind export → 生成 .xmind
    │
    ▼
在 XMind APP 中打开编辑调整
    │
    ├──► 导入飞书项目
    └──► 执行 /qa-sync-xmind import → 反向同步 test-spec.md
```

**步骤数**：4 步（qa-spec → 导出 → XMind 编辑 → 导入 + 反向同步）

### 5.3 对比

| 维度 | 当前流程 | 模式 A（纯 Cursor） | 模式 B（XMind 混合） |
|------|----------|---------------------|----------------------|
| 步骤数 | 5 步 | 3 步 | 4 步 |
| 手动复制粘贴 | 4 次 | 0 次 | 0 次 |
| 外部工具 | Coze + XMind + 飞书 | 飞书（仅导入） | XMind + 飞书 |
| 真相源 | 分散（XMind/飞书/Cursor） | test-spec.md | test-spec.md |
| AI 生成质量 | 一般（Coze 单次调用） | 高（代码库扫描 + brainstorming） | 高 |
| 开发自测路径 | 手动搬运 | 自动（pull-spec workspace-aware） | 自动（pull-spec workspace-aware） |
| 版本控制 | 无 | Git 跟踪 test-spec.md | Git 跟踪 test-spec.md |

### 5.4 过渡策略

1. **Phase 1**：两种模式并存，测试同学自由选择
2. **Phase 2**：收集反馈，优化 Cursor 编辑体验（如 Markdown 预览、结构化补全）
3. **Phase 3**：如果测试同学适应了模式 A → 收敛为纯 Cursor 模式；如果确实需要 XMind → 长期保留模式 B

---

## 6. 实施计划

### 6.1 前置依赖

| 依赖项 | 状态 | 说明 |
|--------|------|------|
| workspace-specflow 插件骨架 | 待开发（Phase 0） | 本设计依赖的 `/qa-spec` 基础框架 |
| `/pm-spec` 产出 prd.md | 待开发（Phase 1） | `/qa-spec` 的输入来源 |
| mcp-xmind 安装 | 可立即安装 | `npm install @41px/mcp-xmind`，加入 Cursor MCP 配置 |

### 6.2 开发任务

本设计的开发任务嵌入 workspace-specflow 的分阶段计划中：

**随 Phase 1 交付**（workspace-specflow 的产品和测试 Skill）：

| # | 任务 | 工作量 | 说明 |
|---|------|--------|------|
| 1 | Coze 提示词迁移到 `/qa-spec` SKILL.md | ~0.5 天 | 提取 Coze 提示词，适配 MODULE 结构输入 |
| 2 | `/qa-spec` Step 9 XMind 导出 | ~0.5 天 | 在确认写入后调用 mcp-xmind 生成 .xmind |
| 3 | `/qa-sync-xmind` export 命令 | ~0.5 天 | test-spec.md → XMind 正向转换 |
| 4 | `/qa-sync-xmind` import 命令 | ~0.5 天 | XMind → test-spec.md 反向转换 + diff 展示 |
| 5 | 层级映射规则调试 | ~0.5 天 | 验证生成的 XMind 能通过飞书项目自由模式导入 |
| 6 | mcp-xmind 环境配置文档 | ~0.5 天 | 安装和配置指南 |

**合计**：约 **3 天**（在 workspace-specflow Phase 1 的 `/qa-spec` 基础上新增约 1.5 天用于 XMind Bridge 相关任务）

### 6.4 风险项

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| mcp-xmind 生成的 XMind 文件不被飞书项目自由模式接受 | 阻塞飞书导入路径 | 任务 5 专门调试验证；如不行可退回 xmind-sdk 直接生成 |
| 测试同学不接受 Markdown 编辑 | 模式 A 无法推广 | 模式 B 作为长期兼容方案，不强制切换 |
| mcp-xmind 项目停止维护 | 长期可用性 | MIT 协议可 fork；核心逻辑简单（JSON → ZIP），必要时可自研替代 |

### 6.3 验证节点

| 节点 | 验证标准 |
|------|----------|
| 提示词迁移 | `/qa-spec` 生成的测试用例质量 ≥ Coze 工作流 |
| XMind 导出 | 生成的 .xmind 可被飞书项目自由模式成功导入，用例结构正确 |
| XMind 反向同步 | XMind 中的调整能正确反映到 test-spec.md |
| 端到端 | 测试同学完成一个真实需求的完整流程（模式 A 或 B） |

---

## 7. 设计决策

| ID | 决策 | 理由 |
|----|------|------|
| QA-D1 | test-spec.md 是唯一真相源，XMind 是派生产物 | 避免多份副本导致的版本混乱；Markdown 可 Git 跟踪和 diff |
| QA-D2 | 使用 mcp-xmind（MIT 开源）而非自研 XMind 生成 | 成熟的 MCP 协议实现，读写能力完整，免费无依赖 |
| QA-D3 | 采用飞书项目自由模式导入 | 不限制 XMind 层级结构，兼容性最好，降低格式适配复杂度 |
| QA-D4 | 提供两种工作模式（纯 Cursor / XMind 混合） | 尊重测试同学的工具偏好，用体验赢得信任而非强制切换 |
| QA-D5 | Coze 提示词嵌入 SKILL.md 而非外部维护 | Git 版本控制，可迭代优化，可 code review |
| QA-D6 | XMind 文件建议 .gitignore | 二进制文件对 Git diff 不友好，可从 test-spec.md 随时重新生成 |
| QA-D7 | `/qa-sync-xmind` 是独立命令而非 `/qa-spec` 的一部分 | 职责分离：`/qa-spec` 负责生成测试 spec，`/qa-sync-xmind` 负责格式转换 |
| QA-D8 | 反向同步需人工确认 diff | 防止 XMind 中的误操作覆盖已确认的 test-spec.md 内容 |
