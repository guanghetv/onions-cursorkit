# Workspace Specflow — 统一工作区多角色协作工作流设计

> 设计确认时间: 2026-04-07

## 1. 背景与目标

### 1.1 现状痛点

当前多仓库、多角色协作的研发模式存在以下通用问题：

- **信息同步延迟**：后端 spec 变更后前端感知滞后，产品需求变更开发侧反应慢
- **重复劳动**：产品写完飞书文档还需手动在各处转述；前后端各自编写类似的 API 契约描述
- **流程割裂**：产品、前端、后端、测试各自有独立工作流（fe-specflow / be-specflow），缺乏统一的进度视图和协作节奏
- **跨仓协作笨重**：`pull-spec` 依赖 GitLab API 跨仓库拉取 spec，产品/测试产出物分散在飞书文档中无法被 Cursor Agent 直接使用

这些问题不局限于某个业务域，而是所有涉及"产品 + 前端 + 后端 + 测试"多角色协作的业务都会遇到的。

### 1.2 目标

1. **统一 spec 真相源**：产品、测试、前后端开发的 spec 产出物在同一工作区内可直接引用
2. **AI 跨端联动**：小需求可由一人配合 AI 完成前后端全部开发，大需求由不同开发各自推进，流程一致
3. **全链路人工门禁**：所有 AI 生成的 spec 文档必须人工确认，AI 不自动修改代码仓库
4. **按业务域划分工作区**：每个业务域一个 specs 仓库 + 对应的前后端代码仓库组成一个工作区
5. **历史知识沉淀**：历史需求文档转为 MD 存入仓库，作为 Cursor Agent 的上下文和影响分析参考
6. **通用可复用**：整套工作流抽象为 Cursor 插件/技能包，可安装到任意业务工作区使用

### 1.3 插件定位

本设计产出为一个通用的 Cursor 插件（暂命名 `workspace-specflow`），与现有 `fe-specflow` / `be-specflow` 同级，安装到 `cursorkit/plugins/` 下。任何业务工作区安装该插件后即可使用完整的多角色协作流程。

**插件与业务工作区的关系**：
- **插件（通用）**：`workspace-specflow` — 提供 skills、commands、rules，不含业务特定内容
- **业务工作区（实例）**：如 `channel-specs`、`ai-classroom-specs` 等 — 包含 `requirements/`、`workspace-repos.json`、`.code-workspace`、`prodspecs/` 等业务数据

### 1.4 试点范围

以渠道业务工作区作为首个试点：

- 工作区：`channel-specs` + 相关 9 个前后端仓库（见 `scripts/workspace-repos.json`）
- 角色：产品同学、测试同学、前端开发、后端开发（全员使用 Cursor IDE）
- 技术栈：后端 Go（部分 Node）、前端 Vue3（部分 Vue2）
- 项目管理：飞书项目看板

后续可扩展到其他业务工作区（如 AI 课堂），只需创建对应的 specs 仓库 + `workspace-repos.json` + `.code-workspace`，安装同一个 `workspace-specflow` 插件即可。

---

## 2. 架构设计

### 2.1 双层架构

采用**需求层 + 执行层**融合共存的架构：

```
┌─────────────────────────────────────────────────────┐
│  需求层（Knowledge Base）                            │
│  <specs-repo>/requirements/                         │
│  角色：产品、测试                                     │
│  生命周期：只增不删，长期存档                           │
│  管理方式：metadata.yaml 状态追踪，不使用 OpenSpec      │
├─────────────────────────────────────────────────────┤
│  执行层（Workflow）                                   │
│  <code-repo>/openspec/changes/                      │
│  角色：前端开发、后端开发                               │
│  生命周期：创建 → 开发 → 归档                          │
│  管理方式：OpenSpec CLI + fe-specflow / be-specflow   │
└─────────────────────────────────────────────────────┘

其中 <specs-repo> 为业务域的规格仓库（如 channel-specs），
<code-repo> 为具体的代码仓库（如 channel、branstark 等）。
```

**设计决策**：
- **需求层不使用 OpenSpec**（决策 D1）：需求层的生命周期极简（pending → confirmed），OpenSpec 的 artifact 机制（proposal → design → tasks → TDD → verify → archive）对纯文档场景是过度设计。`metadata.yaml` 的状态追踪已足够。
- **需求层不做归档**（决策 D2）：需求层是团队的长期知识资产，只增不删。归档概念仅存在于执行层（OpenSpec changes 的 archive）。
- **两层通过 `requirement_ref` 连接**（决策 D3）：执行层的 `proposal.md` 中通过 `requirement_ref` 字段引用需求层路径，这是两层之间的唯一连接点。

### 2.2 信息流向与角色职责

```
飞书需求文档
    │
    ▼
产品 spec（产品同学转换 + 确认）
    │
    ├──► 测试 spec（测试同学基于产品 spec 生成 + 确认）
    │         │
    │         └──► FE/BE 自动化验证阶段（验证依据）
    │
    └──► 开发 spec（开发同学基于产品 spec + 代码现状生成）
           ├──► FE change（fe-specflow）
           └──► BE change（be-specflow）
```

**设计决策**：
- **各角色对自己的产出负责**（决策 D4）：产品出产品 spec，测试出测试 spec，开发出开发 spec。AI 是助手，不替代任何角色。
- **测试 spec 的输入隔离**（决策 D5）：测试 spec 的真相源 = 产品需求文档 + 产品 spec，严禁读取开发 spec。测试验证的是"产品要什么"，不是"开发怎么做的"。
- **产品 spec 只描述需求本质**（决策 D6）：不涉及数据库设计、UI 组件选择、API 字段定义等技术实现细节。除非需求文档中显式强调了某个技术约束（如"需要测试平板性能"）。

### 2.3 异步依赖模型

各角色的产出不是严格串行的，支持异步到达：

| 阶段 | 必须依赖 | 可以没有 |
|------|----------|----------|
| FE/BE 开发启动 | 产品 spec（已确认） | 测试 spec、对方的 spec |
| FE/BE 联调与校准 | 对方的 API 契约 spec | — |
| FE/BE 自动化验证 | 测试 spec（已确认） | — |

**设计决策**：
- **开发不等测试 spec**（决策 D7）：测试 spec 可能后到，开发可先行启动。
- **前后端完全并行**（决策 D8）：前端不强制等后端 spec，前期可口头约定 API，后续 spec 到达后通过 `pull-spec`（workspace-aware）校准。
- **汇合点只有两个**（决策 D9）：联调（需要对方 API 契约）和验证（需要测试 spec）。

### 2.4 需求 → Change 映射

**设计决策**：
- **始终为每个仓库创建独立的 change**（决策 D10）：即使是小需求由一人完成前后端，也分别创建独立的 change。区别只在于"谁坐在 Cursor 前面"，流程不变。
- **change-id 以仓库名为后缀**（决策 D11）：如 `contract-subject-alignment-branstark`、`contract-subject-alignment-channel`，不使用 `-fe` / `-be` 后缀（因为可能有多个前端项目）。
- **不预设版本号**（决策 D12）：change-id 不强制加 `-v1`。后续迭代时，开发根据实际内容自然命名新 change。
- **需求层是产品视角的完整需求，不拆分**（决策 D13）：拆分发生在执行层。一个产品需求可对应多个 change（按仓库和迭代拆分）。

---

## 3. 需求层目录规范

### 3.1 目录结构

**插件约定**：`workspace-specflow` 插件期望工作区的 specs 仓库包含以下目录：

| 目录/文件 | 用途 | 由谁创建 |
|-----------|------|----------|
| `requirements/` | 需求层根目录 | 插件 `/req-new` |
| `_archive/` | 历史需求存档（与 requirements/ 同级） | 手动迁移 |
| `docs/context/` | 业务上下文知识库（产品共享给开发/测试） | 产品手动维护 |
| `scripts/workspace-repos.json` | 仓库路径注册表 | 初始化时手动创建 |
| `*.code-workspace` | VS Code/Cursor 多根工作区文件 | 初始化时手动创建 |
| `prodspecs/` | 交互演示 demo（GitLab Pages） | `/pm-spec` 可选生成 |

**实例化示例**（以渠道业务为例）：

```
channel-specs/                              # specs 仓库（业务域实例）
  requirements/                             # 需求层根目录（扁平结构）
    contract-subject-alignment/             # 需求单元（kebab-case）
      prd.md                                # 产品 PRD（产品撰写 + /pm-spec 增强）
      metadata.yaml                         # 需求元数据
      prototypes/                           # 原型文件（可选，产品自定义子目录结构）
      test/
        test-spec.md                        # 测试 spec
    order-commission-split/
      ...
  _archive/                                 # 历史需求（与 requirements/ 同级）
    2024-contract-management-v1/
      prd.md                                # 自由格式 Markdown，能被 AI 读到即可
    2025-channel-commission-v2/
      prd.md
  prodspecs/                                # 交互演示（GitLab Pages 发布）
    index.html                              # demo 索引页
    contract-subject-alignment/
      index.html                            # 某需求的交互演示
  docs/
    context/                                # 业务上下文知识库
      business-glossary.md                  # 业务术语表（产品维护）
      system-overview.md                    # 系统架构概述
      ...                                   # 任意 Markdown，供 AI 作为上下文
  scripts/
    workspace-repos.json                    # 仓库路径注册表
    git-clone-all.sh                        # 批量克隆脚本
  channel-specs.code-workspace              # 多根工作区文件
```

**设计决策**：
- **requirements/ 扁平结构**（决策 D14a）：需求目录直接放在 `requirements/` 下，不按业务模块分子目录。业务模块信息记录在 `metadata.yaml` 的 `module` 字段中，便于 `/req-status` 按模块过滤。
- **目录名使用 kebab-case 英文**（决策 D14）：与 OpenSpec change-id 风格一致，避免编码问题。中文名存在 `metadata.yaml` 的 `name` 字段中。
- **`_archive/` 与 `requirements/` 同级**（决策 D15）：存放历史需求文档，下划线前缀区分。历史文档**不需要模板格式化**，只需是 Markdown 格式、能被 AI 作为上下文读取即可。目录名建议带年份前缀。
- **`/req-status` 不扫描 `_archive/`**（决策 D16）。

### 3.2 metadata.yaml Schema

```yaml
name: 合同管理-学科学段树与CVS对齐          # 中文显示名
id: contract-subject-alignment              # kebab-case，与目录名一致
module: channel                              # 业务模块
feishu_doc: https://xxx.feishu.cn/docx/xxx  # 飞书需求文档链接
figma: https://www.figma.com/design/xxx     # 可选，设计稿链接
created_at: 2026-04-07

prd:
  status: pending                # pending → confirmed
  confirmed_at: null

test_spec:
  status: pending                # pending → confirmed
  confirmed_at: null

changes:                         # 关联的 OpenSpec changes
  - id: contract-subject-alignment-branstark
    type: frontend               # frontend / backend
    repo: branstark              # 逻辑名称，通过 workspace-repos.json 解析路径
    modules: [MODULE-1]          # 本次 change 覆盖的 MODULE
  - id: contract-subject-alignment-channel
    type: backend
    repo: channel
    modules: [MODULE-1, MODULE-2]
```

**设计决策**：
- **不记录 `feishu_task`**（决策 D17）：一个产品需求可能被开发拆分成多个迭代卡片，不是 1:1 映射，记录在这里会误导。
- **不记录 `created_by`**（决策 D18）：git log 已有记录。
- **路径解析通过 `workspace-repos.json`**（决策 D19）：`metadata.yaml` 中的 `repo` 字段存逻辑名称（如 `branstark`），运行时通过 `workspace-repos.json` 解析为相对路径。不同团队成员只需保证相对布局一致（`git-clone-all.sh` 已保证），无需统一绝对路径。

### 3.3 prd.md 模板

prd.md 经历两个阶段：产品撰写（自由格式）→ `/pm-spec` 增强（MODULE 结构化）。增强后的完整结构如下：

```markdown
# <需求标题>

> 来源: <飞书文档链接>
> 确认时间: YYYY-MM-DD

## 需求背景

（业务背景、问题描述、目标——产品原始内容）

## 功能模块

### MODULE-1: <模块名称>
**优先级**: P0/P1/P2
**描述**: （做什么、为什么做）
**用户故事**:
- 作为<角色>，我希望<行为>，以便<价值>
**验收标准**:
- [ ] 标准1
- [ ] 标准2
**业务规则**:
- 规则1
- 规则2

### MODULE-2: <模块名称>
...

## 全局约束

（跨模块共享的约束条件：兼容性、性能、安全、数据迁移等）

## 名词解释

（业务术语定义，确保产品/开发/测试理解一致）
```

**设计决策**：
- **prd.md 就是产品 spec，一个文件两个阶段**（决策 D28）：产品撰写的 PRD 与结构化增强后的产品 spec 是同一文件，避免真相源分裂。
- **飞书文档是展示层，prd.md 是真相源**（决策 D29）：飞书给人讲需求，prd.md 给 AI/开发/测试消费。产品已有飞书同步技能，增强后可选择同步回飞书。
- **产品 spec 必须模块化**（决策 D20）：按 MODULE 拆分功能点，每个 MODULE 是自包含的单元，支持后续开发按 MODULE 精确切片。简单需求可只有一个 MODULE，但仍遵循相同结构。
- **MODULE ID 是稳定的引用锚点**（决策 D21）：开发和测试通过 MODULE ID 精确定位对应内容。

### 3.4 test-spec.md 模板

```markdown
# 测试用例：<需求标题>

> 来源产品 spec: requirements/<requirement>/prd.md
> 确认时间: YYYY-MM-DD

## MODULE-1: <模块名称>

### 场景 1.1: <正常流程描述>
**测试类型**: 功能测试
**覆盖端**: 运营后台
**前置条件**:
- 条件1
**操作步骤**:
1. 步骤1
2. 步骤2
**预期结果**:
- 结果1

### 场景 1.2: <边界情况描述>
**测试类型**: 边界测试
...

## MODULE-2: <模块名称>
...

## 跨模块场景

### 场景 X.1: <跨模块联动测试>
**关联模块**: MODULE-1, MODULE-2
...

## 兼容性 & 回归

### 场景 R.1: <已有数据兼容>
...
```

**设计决策**：
- **MODULE ID 与产品 spec 严格一致**（决策 D22）：测试场景按相同的 MODULE 结构组织，支持按 MODULE 精确提取。
- **测试类型以功能测试和边界测试为主**（决策 D23）：异常测试、性能测试、兼容性测试按需出现，根据产品 spec 内容判断。
- **测试步骤描述业务操作**（决策 D24）：如"点击保存"，不描述技术验证（如"检查 API 返回 200"）。

---

## 4. Skill 体系设计

### 4.1 总览

| # | 命令 | 角色 | 核心职责 |
|---|------|------|----------|
| 1 | `/req-new` | 任何人 | 初始化需求目录 |
| 2 | `/pm-spec` | 产品 | 飞书 → 产品 spec（含可选交互演示） |
| 3 | `/qa-spec` | 测试 | 产品 spec → 测试 spec（+ 可选 XMind 导出） |
| 4 | `/qa-sync-xmind` | 测试 | test-spec.md ↔ XMind 双向转换 |
| 5 | `/dev-start` | 开发 | 桥接需求层 → 启动 dev-workflow |
| 6 | `/req-status` | 任何人 | 查看需求整体进度 |

> **变更说明（D35）**：原 `/dev-sync-test` 和 `/dev-sync-api` 已移除。spec 同步职责统一由执行层的 `pull-spec`（workspace-aware 增强版）承担，详见 Section 5.4。

所有 skill 支持两种定位方式：
- **自动模式**：扫描 + 列出供选择
- **手动模式**：直接指定需求路径或 id（如 `/pm-spec requirements/channel/需求一`）

### 4.2 `/req-new` — 初始化需求目录

**谁用**：产品同学、TL、或任何发起需求的人

**交互流程**：

1. **贴飞书文档链接** — 用户只需提供一个飞书需求文档的 URL
2. **自动提取** — 通过 feishu-mcp 读取文档，自动提取需求标题和概要，生成 kebab-case 目录名
3. **用户确认** — 展示提取结果 + 目录名 + 业务模块（自动识别或手动指定），用户确认或修正
4. **创建目录** — 生成 `metadata.yaml` + 空模板文件
5. **提示下一步** — "需求目录已创建。产品同学可以执行 `/pm-spec` 转换产品 spec。"

**业务模块自动识别**：
- `requirements/` 下只有一个模块 → 直接使用
- 多个模块 → 询问选择
- 新模块 → 用户指定名称

### 4.3 `/pm-spec` — 飞书需求文档 → 产品 spec

**谁用**：产品同学

**前置条件**：需求目录已创建，`prd.status` 为 `pending`

**交互流程（7 步）**：

**Step 1: 定位需求 & 拉取飞书文档**
- 选择或指定 pending 的需求，通过 feishu-mcp 拉取文档全文

**Step 2: 扫描前后端服务（业务层面）**
- 从 `workspace-repos.json` 解析所有仓库路径，扫描关键结构
- 识别可能受影响的**业务区域**（不涉及技术实现细节）
- 输出影响范围分析，作为 brainstorming 讨论点

**Step 3: Brainstorming（调用 superpowers:brainstorming）**
- 以飞书文档内容 + 业务影响分析作为输入
- 引导产品同学完善需求：逐个澄清模糊点、基于系统现状提出可能遗漏的场景、讨论 MODULE 划分、确认优先级和验收标准

**Step 4: AI 转换为 spec + 模块化拆分**
- 将 brainstorming 结论在 prd.md 上增强为 MODULE 结构
- 按 MODULE 拆分功能点（简单需求归为一个 MODULE）

**Step 5: 逐段 review**
- 分段展示：需求背景 → MODULE 概览 → 逐个 MODULE 详情 → 全局约束 → 名词解释
- 每段可修改补充

**Step 6: 完整性校验**
- AI 对照飞书原文，列出未纳入 spec 的内容，让产品确认是否需要补充
- 确认后写入 `prd.md`，更新 `metadata.yaml` 状态为 `confirmed`

**Step 7: 可选生成交互演示**
- 询问是否需要生成 demo
- 如果确认：
  - 读取 `prd.md` 功能描述
  - 扫描前端仓库的样式（主题色、组件风格、布局），**只读不改**
  - 生成 `prodspecs/<requirement-id>/index.html`，所有资源内联
  - 自动在 `prodspecs/index.html` 的 `<ul id="demo-index">` 追加索引条目
  - **严禁修改前后端代码仓库的任何文件**
  - 提交后 GitLab CI 自动发布到 Pages

**安全护栏**：
- 产品 spec 只描述需求本质，不涉及技术实现细节（决策 D6）
- 扫描代码只提取业务影响，不提数据库设计、组件选择等
- demo 只写 `channel-specs/prodspecs/`，禁写代码仓库

### 4.4 `/qa-spec` — 产品 spec → 测试 spec

**谁用**：测试同学

**前置条件**：`prd.status` 为 `confirmed`

**交互流程（8 步）**：

**Step 1: 定位需求**
- 列出 prd 已确认且测试 spec 为 pending 的需求

**Step 2: 读取 prd.md**
- 读取 `prd.md` 全文
- **输入隔离**：禁止读取 `openspec/changes/` 下任何开发产出（决策 D5）

**Step 3: 扫描前后端现状（业务层面）**
- 识别可测试的业务行为和边界：现有功能入口、操作路径、多端场景覆盖

**Step 4: Brainstorming（调用 superpowers:brainstorming）**
- 引导测试同学设计测试策略：核心场景、边界情况、多端覆盖、数据兼容性、产品 spec 中强调的特殊约束

**Step 5: AI 生成测试 spec**
- 按 MODULE 结构组织，MODULE ID 与产品 spec 一一对应
- 测试类型以功能测试和边界测试为主，其他类型按需

**Step 6: 逐段 review**
- 按 MODULE 逐个展示测试场景，测试同学可补充修改

**Step 7: 覆盖率校验**
- AI 对照产品 spec 每条验收标准，检查是否都有对应测试场景
- 输出覆盖率报告，标记未覆盖项

**Step 8: 确认 & 写入**
- 写入 `test/test-spec.md`，更新 `metadata.yaml` 状态为 `confirmed`
- 提示："如开发已在进行中，可通知开发同学通过 `pull-spec` 同步测试用例。"

### 4.5 `/dev-start` — 桥接需求层 → 启动开发工作流

**谁用**：前端或后端开发同学

**前置条件**：`prd.status` 为 `confirmed`（测试 spec 不要求）

**定位**：轻量上下文准备 + dev-workflow 启动器。**不创建 change 目录，不包含 brainstorming**。change 目录由 dev-workflow 内部的 `design-to-opsx` 在 brainstorming 结束后创建（与现有工作流一致）。

**与现有 skill 的关系**：
- `/dev-start`（新增）= 上下文准备 + 启动器：读取需求层 → 确定目标仓库和 MODULE → 启动 dev-workflow
- `dev-workflow`（现有，小幅适配）= 执行层：brainstorming → 灰区 → design-to-opsx → tasks → TDD → verify → archive
- `design-to-opsx`（现有，小幅适配）= 创建 change 目录 + 写入 proposal.md（新增 requirement_ref 注入 + metadata.yaml 回写）

**交互流程（5 步）**：

**Step 1: 定位需求**
- 选择或指定需求

**Step 2: AI 扫描可能涉及的服务**
- 基于产品 spec 内容，扫描 `workspace-repos.json` 中所有仓库
- 分析可能受影响的服务，分三级展示：
  - `✓` 高度相关（扫描到直接相关的模块/文件）
  - `?` 可能相关（待确认）
  - `✗` 扫描后认为不涉及
- 开发确认选择哪个项目，或补充遗漏的项目

**Step 3: AI 匹配 MODULE**
- 开发用自然语言描述本次迭代范围（如"做学科树对齐的后端接口"）
- AI 自动匹配产品 spec 中的 MODULE，展示匹配结果
- 开发确认（不是手动选择，是确认 AI 匹配是否正确）

**Step 4: 检测工作区**
- 检测目标仓库是否在当前 Cursor 工作区中
- 不在则提示：建议通过 `cursor <path>/<specs-repo>.code-workspace` 打开完整工作区
- 功能不会阻塞（Agent 可通过文件路径直接访问），但体验有差异

**Step 5: 无缝启动 dev-workflow**
- 在同一会话中切换到目标仓库上下文
- 将已读取的产品 spec 内容、匹配的 MODULE、需求层路径作为上下文传递给 dev-workflow
- dev-workflow 检测到上下文中有需求层信息，跳过"询问需求来源"，直接进入 brainstorming
- 后续流程完全由 dev-workflow 接管

**`/dev-start` 不写入任何文件**，所有文件操作（创建 change、写入 proposal、回写 metadata.yaml）由 dev-workflow 内部的 design-to-opsx 完成。

### 4.6 `/req-status` — 查看需求整体进度

**谁用**：任何角色

**两种模式**：

- **无参数**：列出所有活跃需求的概览（产品 spec / 测试 spec 状态 + 各 change 进度）
- **指定需求**：展示详情（MODULE 级别的进度、测试场景编写进度、每个 change 的 tasks 完成情况）

**数据来源**：
- `metadata.yaml` → 产品 spec / 测试 spec 状态
- 各仓库 `openspec status --change <id> --json` → change 进度
- `prd.md` → MODULE 列表
- `test/test-spec.md` → 测试场景编写进度

**设计要点**：纯只读，跨仓库读取，通过 `workspace-repos.json` 解析路径。

---

## 5. 现有 Specflow 适配改造

### 5.1 改造原则

**最小改动、最大复用**。现有 fe-specflow / be-specflow 的改动限于增加"需求层"作为新的数据源路径，不影响已有逻辑。不走新流程时，一切行为与现在完全一致。

### 5.2 `dev-workflow` 适配

**阶段 1（设计探索）**：

```
适配前：
  1b. 询问需求来源（飞书/GitLab/截图/文字/本地文件）

适配后：
  1b. 检测会话上下文中是否有需求层信息（由 /dev-start 传递）
      → 有：直接使用产品 spec 的对应 MODULE 内容，跳过来源询问
      → 无：走原有流程（兼容）
```

**事件 A/B（T1 后 spec 到达）**：

```
适配前：
  "后端/测试 spec 到了" → pull-spec 从 GitLab 拉取

适配后：
  pull-spec（workspace-aware 增强版）统一处理：
    1. 检测是否在工作区（workspace-repos.json 可达目标仓库）
       → 是：workspace-native 读取（git fetch + git show，详见 5.4）
       → 否：走原有 GitLab API 流程
    2. 如有 requirement_ref + modules：自动按 MODULE 切片
    3. 兼容：用户直接提供 URL 时，走原有流程不变
```

**其他阶段（tasks、TDD、verify、archive）**：不变。

**改动量**：`dev-workflow/SKILL.md` 约 15-20 行判断逻辑。

### 5.3 `design-to-opsx` 适配

```
适配前：
  步骤 1: 从 brainstorming 结论生成 change-id
  步骤 2: 创建 change 目录
  步骤 3: 写入 proposal.md

适配后：
  步骤 1: 生成 change-id
          → 如果有需求层上下文，建议使用 <requirement-id>-<repo-name> 格式
  步骤 2: 创建 change 目录（不变）
  步骤 3: 写入 proposal.md
          → 如果有需求层上下文，注入 requirement_ref 字段：
            ---
            requirement_ref: requirements/<requirement>
            requirement_repo: <specs-repo-name>
            modules: [MODULE-1]
            ---
  步骤 5（新增）: 回写 specs 仓库的 metadata.yaml
          → 将本次创建的 change 信息追加到 changes 字段
```

**改动量**：`design-to-opsx/SKILL.md` 约 20-25 行。

### 5.4 `pull-spec` 增强为 workspace-aware（决策 D35/D36）

原有 `/dev-sync-test` 和 `/dev-sync-api`（workspace-specflow 的需求层技能）已移除。spec 同步职责统一由执行层的 `pull-spec` 承担，增强后支持三级读取策略。

**设计原则**：开发者无需关心"我在工作区还是单项目"，`pull-spec` 自动选择最优路径。

**三级读取策略**：

| 优先级 | 策略 | 条件 | 体验 |
|--------|------|------|------|
| 1 | workspace-native | 工作区 + `workspace-repos.json` 可达目标仓库 | 零手动输入 |
| 2 | GitLab API | 用户提供 URL 或 MR 链接 | 给个链接即可 |
| 3 | 用户粘贴 | 上述均不可用 | 兜底 |

**workspace-native 读取流程**（策略 1）：

```
触发："后端 spec 到了" / "测试 spec 到了"

Step 1: 判断来源类型
  ├─ "测试 spec" → 从 specs 仓库 master 直接读取 test/test-spec.md
  └─ "对方 API spec" → 需要跨仓库发现分支

Step 2: 跨仓库分支发现（仅对方 API spec 场景）
  a. 从当前 change 的 proposal.md 读取 requirement_ref → 得到需求 ID
  b. 推导对方 change-id: <requirement-id>-<repo-name>（决策 D37）
  c. 从 workspace-repos.json 解析对方仓库本地路径
  d. git fetch + 分支发现（决策 D38，token 优化命令）:
     git -C <repo-path> fetch origin --quiet
     git -C <repo-path> log --all --remotes --source --format=%S -1 \
       -- openspec/changes/<change-id>/proposal.md
     # 输出：仅一行 ref 名（如 refs/remotes/origin/feat/S29-xxx-m-222）
  e. 如无结果：降级到策略 2（询问 URL）

Step 3: 读取文件（不 checkout，不影响对方仓库工作状态）
  git -C <repo-path> show <ref>:<file-path>

Step 4: MODULE 切片（如适用）
  如 proposal.md 有 modules 字段 → 按 MODULE 过滤测试场景

Step 5: 写入 change 目录
  - 测试 spec → qa-spec.md
  - 对方 API → counterpart-api-spec.md（含差异分析）
```

**token 优化要点**（决策 D38）：
- `git fetch --quiet`：静默执行，无输出消耗
- `--format=%S -1`：仅输出一行 ref 名，而非完整 git log
- `git show` 直接读文件内容：产出即所需，无多余信息
- 分支发现总 token 开销：约 1 行（ref 名）

**新增能力**（从原 `/dev-sync-*` 继承）：
- **MODULE 切片**：按 `proposal.md` 的 `modules` 字段精确过滤测试场景
- **差异分析**：读取对方 API 契约后，与本方 proposal 对比输出差异报告
- **MR URL 解析**：支持 GitLab MR 链接作为输入（自动提取 source branch）

### 5.5 其他组件

| 组件 | 改动 |
|------|------|
| `e2e-verify` | 不变（读取的 `qa-spec.md` 由增强版 `pull-spec` 写入，来源透明） |

---

## 6. 插件结构设计

### 6.1 插件文件布局

`workspace-specflow` 插件安装到 `cursorkit/plugins/` 下，与 `fe-specflow` / `be-specflow` 同级，通过 cursorkit marketplace 全局安装：

```
cursorkit/plugins/
  fe-specflow/          # 现有：前端开发工作流
  be-specflow/          # 现有：后端开发工作流
  workspace-specflow/   # 新增：多角色协作工作流
    .cursor-plugin/
      plugin.json       # 插件清单
    README.md
    rules/
      workspace-awareness.mdc  # 激活守卫 Rule（globs 匹配 specs 仓库特征文件）
    commands/
      req-new.md           # /req-new
      pm-spec.md           # /pm-spec
      qa-spec.md           # /qa-spec
      qa-sync-xmind.md     # /qa-sync-xmind
      dev-start.md         # /dev-start
      req-status.md        # /req-status
    skills/
      req-new/SKILL.md
      pm-spec/SKILL.md
      qa-spec/SKILL.md
        references/test-writing-guide.md
      qa-sync-xmind/SKILL.md
        references/xmind-mapping.md
      dev-start/SKILL.md
      req-status/SKILL.md
```

### 6.2 激活守卫机制

workspace-specflow 虽然全局安装，但通过 rule 的 `globs` 字段实现**按项目激活**：

```yaml
# workspace-awareness.mdc
---
description: 当前工作区是一个 specs 仓库，启用 workspace-specflow 多角色协作工作流。
globs:
  - "requirements/**"
  - "**/workspace-repos.json"
---
```

**两层守卫**：
1. **Rule 层**：`globs` 匹配 `requirements/**` — 只有 specs 仓库中 Agent 才收到工作流上下文
2. **Skill 描述层**：每个 skill 的 description 包含 specs 相关触发词 — 在纯代码项目中不会被自然联想

**效果**：
- 纯前端项目 → 无 `requirements/` → rule 不激活 → Agent 不知道 workspace-specflow 的存在
- specs 多根工作区 → rule 激活 → Agent 获得完整工作流指引，同时各代码仓库的 fe/be-specflow 也正常生效

### 6.3 与 fe-specflow / be-specflow 的关系

三个插件**可以共存**，各有分工：

| 插件 | 所在层 | 依赖 | 职责 |
|------|--------|------|------|
| `workspace-specflow` | 需求层 | Superpowers | 多角色协作：需求管理、spec 转换、桥接、进度视图（不含 spec 同步，由执行层 pull-spec 统一处理） |
| `fe-specflow` | 执行层 | Superpowers + OpenSpec | 前端开发执行：brainstorming → design → tasks → TDD → verify → archive |
| `be-specflow` | 执行层 | Superpowers + OpenSpec | 后端开发执行：同上 |

**依赖关系**：
- **需求层**（workspace-specflow）依赖 **Superpowers** 插件提供 brainstorming 能力（`/pm-spec`、`/qa-spec` 中使用）
- **执行层**（fe/be-specflow）依赖 **Superpowers** 插件提供 brainstorming 能力 + **OpenSpec** 提供 change 生命周期管理（创建、归档等）
- 三个插件均**不自带** brainstorming 和 OpenSpec，依赖用户环境已安装

**向后兼容**：
- 不安装 workspace-specflow 的团队 → fe/be-specflow 行为完全不变
- fe/be-specflow 的适配改动（requirement_ref 感知）为条件判断 → 无上下文时走原有流程

---

## 7. 路径解析机制

### 7.1 `workspace-repos.json` 作为路径注册表

需要为 `workspace-repos.json` 增加 `name` 字段：

```json
{
  "repos": [
    { "name": "channel", "path": "../channel", "remote": "git@gitlab.yc345.tv:backend/channel.git" },
    { "name": "branstark", "path": "../branstark", "remote": "git@gitlab.yc345.tv:teacher/fe/branstark.git" },
    ...
  ]
}
```

### 7.2 解析流程

1. `metadata.yaml` 中 `repo: branstark`（逻辑名称）
2. Skill 从 `workspace-repos.json` 找到 `name: branstark` → `path: ../branstark`
3. 基于 `channel-specs` 位置解析为绝对路径

### 7.3 一致性保证

- 所有仓库相对 `channel-specs` 的位置由 `git-clone-all.sh` 保证一致
- 不同团队成员的绝对路径可以不同（引用均为相对路径）
- 推荐通过 `cursor <path>/channel-specs.code-workspace` 打开完整工作区

---

## 8. 历史需求文档转换

### 8.1 价值

- **影响范围分析**：新需求 brainstorming 时搜索历史 spec，识别潜在冲突
- **设计参考**：复用历史设计思路，避免方案不一致
- **业务知识图谱**：随时间积累，成为渠道业务的完整知识库
- **新人 onboarding**：通过 spec 快速了解系统全貌

### 8.2 实施方式

- 存放于 `_archive/` 目录（与 `requirements/` 同级）
- 历史需求只需转为 Markdown 格式，**不需要按 prd.md 模板严格格式化**，也不需要 `metadata.yaml`
- 核心目的是让 AI 能读到历史需求作为上下文，用于影响分析和设计参考
- 目录名建议带年份前缀（如 `2024-contract-management-v1/`）
- 前期手动挑选 3-5 个核心历史需求转换为 Markdown
- 后续可开发 `/pm-batch-convert` skill 批量转换（优先级低于主流程）

---

## 9. 分阶段实施计划

### 开发策略：本地先行 → cursorkit 分发

```
开发阶段                              分发阶段
┌──────────────────────────┐         ┌──────────────────────────┐
│ ~/.cursor/plugins/       │         │ cursorkit/plugins/       │
│   workspace-specflow/    │  稳定   │   workspace-specflow/    │
│     skills/              │ ──────► │     skills/              │
│     commands/            │  迁移   │     commands/            │
│     rules/               │         │     rules/               │
│                          │         │                          │
│ 本地快速迭代、即时生效     │         │ 团队统一分发              │
└──────────────────────────┘         └──────────────────────────┘
```

**本地开发阶段**：
- 在 `~/.cursor/plugins/workspace-specflow/` 创建插件
- 改完即生效，无需发版
- 使用 `channel-specs` 工作区做真实场景验证

**迁移分发阶段**（Phase 0-3 全部验证通过后）：
- 将 `~/.cursor/plugins/workspace-specflow/` 迁移到 `cursorkit/plugins/workspace-specflow/`
- fe/be-specflow 的适配改动同步提交到 cursorkit
- 通过 cursorkit marketplace 发布，团队成员自动获取

### Phase 0：基础设施（~1 天）

**交付物**：
- `~/.cursor/plugins/workspace-specflow/` 插件骨架（`.cursor-plugin/plugin.json`、目录结构、`workspace-awareness.mdc`）
- `requirements/` 目录结构规范（本文档）
- `metadata.yaml` schema 定义
- `prd.md` / `test-spec.md` 模板
- `workspace-repos.json` 增加 `name` 字段
- 试点工作区（`channel-specs`）初始化 `requirements/` 目录
- 手动转换 3-5 个核心历史需求，验证模板

**可验证节点**：插件骨架创建完成，在 specs 工作区中 rule 正确激活，目录结构和模板可用

### Phase 1：产品和测试的 Skill（~2-3 天）

**交付物**：`/req-new`、`/pm-spec`、`/qa-spec`、`/req-status`

**技术风险**：
- feishu-mcp 拉取文档的富文本 → Markdown 转换质量
- spec 模板结构需要反复调优

**可验证节点**：产品同学完成一个真实需求的 spec 转换 + 测试同学生成测试用例

### Phase 2：开发桥接 Skill（~2 天）

**交付物**：`/dev-start`

**技术风险**：
- 多根工作区中跨仓库上下文切换的可靠性
- dev-workflow 接收需求层上下文的传递方式

**可验证节点**：开发执行 `/dev-start`，从产品 spec 出发，无缝衔接 dev-workflow 进入 brainstorming，design-to-opsx 创建 change 并自动回写 metadata.yaml

### Phase 3：现有 Specflow 适配 + 同步 Skill（~1-2 天）

**交付物**：
- `dev-workflow` 阶段 1 适配（本地 `~/.cursor/plugins/fe-specflow/` 和 `be-specflow/` 中验证）
- `design-to-opsx` 适配（requirement_ref 注入 + metadata.yaml 回写）
- `pull-spec` workspace-aware 增强（三级读取策略 + MODULE 切片 + 差异分析）

**可验证节点**：
- dev-workflow 自动从需求层读取产品 spec
- 测试 spec 到达后通过增强版 `pull-spec` 自动从 specs 仓库读取，验证阶段正常使用
- 对方 API spec 到达后通过 `pull-spec` workspace-native 模式自动发现分支并读取

**迁移节点**：Phase 3 验证通过后，将本地改动统一迁移到 cursorkit 仓库提交

### Phase 4（P1）：飞书看板联动（~3-5 天）

**交付物**：飞书项目卡片状态变化 → 自动触发归档或通知

**建议路径**：先用 Cursor 内轮询（定时检查飞书卡片状态 + 对比 metadata.yaml）验证价值，确认有用再投入 webhook 方案。

### 总成本

| 阶段 | 工作量 | 优先级 | 开发位置 |
|------|--------|--------|----------|
| Phase 0 | ~1 天 | P0 | 本地 `~/.cursor/plugins/` |
| Phase 1 | ~2-3 天 | P0 | 本地 `~/.cursor/plugins/` |
| Phase 2 | ~2 天 | P0 | 本地 `~/.cursor/plugins/` |
| Phase 3 | ~1-2 天 | P0 | 本地 `~/.cursor/plugins/` → cursorkit 迁移 |
| Phase 4 | ~3-5 天 | P1 | cursorkit |

Phase 0-3 合计约 **6-8 天**（AI 辅助开发 skill 的工作量，skill 本质是 Markdown 指令文档）。

---

## 10. 设计决策索引

| ID | 决策 | 理由 |
|----|------|------|
| D1 | 需求层不使用 OpenSpec | 生命周期太简单，OpenSpec 是过度设计 |
| D2 | 需求层不做归档 | 知识资产只增不删，归档仅在执行层 |
| D3 | 两层通过 requirement_ref 连接 | 唯一连接点，解耦两层生命周期 |
| D4 | 各角色对自己的产出负责 | AI 是助手不是替代者 |
| D5 | 测试 spec 输入隔离 | 独立验证原则，测试验证需求不是实现 |
| D6 | 产品 spec 只描述需求本质 | 不越界到技术实现 |
| D7 | 开发不等测试 spec | 异步到达，开发可先行 |
| D8 | 前后端完全并行 | 前期口头约定，后续 spec 到达再校准 |
| D9 | 汇合点只有联调和验证 | 最小化阻塞 |
| D10 | 每个仓库独立创建 change | 结构一致，灵活分配 |
| D11 | change-id 以仓库名为后缀 | 支持多前端项目场景 |
| D12 | 不预设版本号 | 按实际内容自然命名 |
| D13 | 需求层不拆分 | 拆分发生在执行层 |
| D14 | 目录名 kebab-case 英文 | 与 OpenSpec 一致，避免编码问题 |
| D15 | _archive/ 存放历史需求 | 下划线前缀区分活跃/历史 |
| D16 | req-status 不扫描 _archive | 避免历史数据干扰 |
| D17 | 不记录 feishu_task | 产品需求与开发卡片不是 1:1 |
| D18 | 不记录 created_by | git log 已有 |
| D19 | 路径通过 workspace-repos.json 解析 | 逻辑名称 + 运行时解析，支持不同本地路径 |
| D20 | 产品 spec 必须模块化 | 支持开发按 MODULE 精确切片 |
| D21 | MODULE ID 是稳定引用锚点 | 开发和测试通过 MODULE ID 定位内容 |
| D22 | 测试 MODULE ID 与产品一致 | 支持按 MODULE 精确提取测试用例 |
| D23 | 测试类型以功能和边界为主 | 其他类型按需出现 |
| D24 | 测试步骤描述业务操作 | 不描述技术验证 |
| D25 | 全局安装 + rule 守卫激活 | 分发方式与 fe/be-specflow 一致；globs 按项目激活避免污染 |
| D26 | 需求层依赖 Superpowers，执行层依赖 Superpowers + OpenSpec | 需求层无 change 生命周期，不需要 OpenSpec |
| D27 | 本地先行开发，稳定后迁移 cursorkit | 快速迭代验证，Phase 3 通过后统一迁移分发 |
| D28 | prd.md 就是产品 spec | 一个文件两个阶段（产品撰写 + /pm-spec 增强），避免真相源分裂 |
| D29 | 飞书文档是展示层，prd.md 是真相源 | 飞书给人讲需求，prd.md 给 AI/开发/测试消费 |
| D30 | /pm-spec 增强而非覆盖 | 保留产品原始内容，叠加 MODULE 结构 |
| D31 | 业务线按 specs 仓库拆分 | 渠道+运营后台是一个 specs 仓库，AI 课堂是另一个 |
| D32 | 产品已有飞书同步技能继续使用 | workspace-specflow 不重复造轮子，增强后提示产品同步 |
| D33 | 开发禁止修改 requirements/ | 唯一例外：design-to-opsx 回写 metadata.yaml 的 changes 字段 |
| D34 | prd.md 增量更新暂不支持 | confirmed 后需修改时手动编辑重新确认，差异比对能力后续迭代 |
| D35 | spec 同步职责归执行层 pull-spec，移除 /dev-sync-test 和 /dev-sync-api | workspace-specflow 只管需求层，不越界到执行层的 spec 同步；统一入口避免开发者困惑 |
| D36 | pull-spec 增强为 workspace-aware，三级读取策略 | 工作区 `git show`（自动发现）→ GitLab API（URL）→ 用户粘贴；开发者无需关心环境差异 |
| D37 | change-id 可推导（`<requirement-id>-<repo-name>`），用于自动发现对方 spec | 无需手动输入 URL 或分支名，工作区场景下实现零配置 spec 同步 |
| D38 | 分支发现使用 `git log --source --format=%S -1`，单行输出 | token 优化：分支发现仅消耗约 1 行输出；`git show` 不 checkout 不影响对方仓库状态 |
