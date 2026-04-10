# Workspace Specflow — 完整协作工作流

> 配套设计文档: `2026-04-07-workspace-specflow-design.md`

---

## 双层架构

整个工作流由两个独立的层组成，通过 `requirement_ref` 连接：

```
┌─────────────────────────────────────────────────────────────────────┐
│  需求层（Requirements Layer）                                       │
│  仓库: specs 仓库（如 channel-specs）                                │
│  插件: workspace-specflow                                           │
│  依赖: Superpowers（brainstorming）                                  │
│                                                                     │
│  职责: 需求管理、产品 spec、测试 spec、进度追踪                       │
│  角色: 产品、测试、开发（发起 /dev-start）                            │
│  产出: requirements/<requirement>/                                   │
│        ├─ prd.md（产品撰写 + /pm-spec 增强，↔ 飞书同步）              │
│        ├─ metadata.yaml                                             │
│        ├─ prototypes/（可选）                                        │
│        └─ test/test-spec.md                                         │
├──────────────── requirement_ref（唯一连接点）────────────────────────┤
│  执行层（Execution Layer）                                          │
│  仓库: 各代码仓库（如 channel, branstark）                           │
│  插件: fe-specflow / be-specflow                                    │
│  依赖: Superpowers（brainstorming）+ OpenSpec（change 生命周期管理）  │
│                                                                     │
│  职责: 技术设计、任务拆分、TDD 开发、联调、验证、归档                 │
│  角色: 前端开发、后端开发                                            │
│  产出: openspec/changes/<change-id>/                                 │
│        ├─ proposal.md（含 requirement_ref）                          │
│        ├─ specs/                                                     │
│        ├─ tasks.md                                                   │
│        ├─ qa-spec.md（从需求层同步）                                  │
│        └─ e2e-report.md                                             │
└─────────────────────────────────────────────────────────────────────┘
```

**插件体系**：三个插件均通过 cursorkit 全局安装，通过 rule 的 `globs` 机制按项目激活

| 插件 | 激活条件 | 依赖 |
|------|----------|------|
| `workspace-specflow` | 项目含 `requirements/` + `workspace-repos.json` | Superpowers |
| `fe-specflow` | 项目含 `.vue` / `.ts` / `openspec/` 等前端文件 | Superpowers + OpenSpec |
| `be-specflow` | 项目含 `.go` / `openspec/` 等后端文件 | Superpowers + OpenSpec |

**向后兼容**：不安装 workspace-specflow 的团队，fe/be-specflow 行为不变。

---

## 角色与工具

| 角色 | 所在层 | 使用的 Skill | 工作上下文 |
|------|--------|-------------|-----------|
| 产品同学 | 需求层 | `/req-new`, `/pm-spec`, `/req-status` | specs 仓库 |
| 测试同学 | 需求层 | `/qa-spec`, `/req-status` | specs 仓库 |
| 开发同学 | 需求层 → 执行层 | `/dev-start`, `/req-status` + 执行层 `pull-spec`（workspace-aware） | specs 仓库 + 代码仓库（多根工作区） |

全员通过 `cursor <path>/<specs-repo>.code-workspace` 打开完整工作区。

---

## 阶段 0：环境准备（一次性）

**TL/负责人**：
1. 创建 specs 仓库（如 `channel-specs`），初始化目录结构：
   - `requirements/` — 需求层根目录（扁平结构，需求目录直接放在下面）
   - `_archive/` — 历史需求文档（与 requirements/ 同级，自由格式 Markdown）
   - `scripts/workspace-repos.json` — 仓库路径注册表
   - `prodspecs/index.html` — 交互演示索引页
   - `.gitlab-ci.yml` — GitLab Pages 发布配置
2. 创建 `.code-workspace` 文件，列出所有相关仓库
3. 创建 `scripts/git-clone-all.sh` 批量克隆脚本
4. 安装 `workspace-specflow` 插件到 specs 仓库

**各团队成员**：
1. `git clone` specs 仓库
2. 执行 `git-clone-all.sh` 克隆所有关联仓库
3. `cursor <path>/<specs-repo>.code-workspace` 打开工作区

---

## 阶段 1：需求发起

**执行者**：产品同学（或 TL）
**工作上下文**：specs 仓库

```
/req-new
  │
  ├─ 贴飞书需求文档链接
  │
  ├─ feishu-mcp 自动提取标题和概要
  │
  ├─ 确认：目录名（kebab-case）+ 业务模块
  │
  └─ 产出：
       requirements/<requirement-id>/
         ├─ metadata.yaml        ← prd: pending, test_spec: pending
         ├─ prd.md               ← 空模板（产品后续撰写）
         ├─ prototypes/          ← 空目录（产品可选放入原型）
         └─ test/test-spec.md    ← 空模板
```

**下一步**：产品同学执行 `/pm-spec`

---

## 阶段 2：产品 spec 增强

**执行者**：产品同学
**工作上下文**：specs 仓库
**前置条件**：产品已撰写 prd.md（或通过飞书同步技能生成）

```
/pm-spec
  │
  ├─ Step 1: 定位需求 + 读取 prd.md
  │    ├─ prd.md 已有内容 → 直接读取
  │    └─ prd.md 为空 → 从 feishu_doc 拉取写入
  │
  ├─ Step 2: 扫描前后端仓库
  │    └─ 输出：业务层面影响分析（不涉及技术实现）
  │
  ├─ Step 3: brainstorming（superpowers）
  │    ├─ 基于 prd.md + 原型（如有）+ 影响分析
  │    ├─ 逐个澄清需求模糊点
  │    ├─ 基于系统现状提出可能遗漏的场景
  │    ├─ 讨论 MODULE 划分
  │    └─ 确认优先级和验收标准
  │
  ├─ Step 4: 在 prd.md 上增强为 MODULE 结构
  │    └─ 保留产品原始内容，叠加 MODULE + 验收标准 + 业务规则
  │
  ├─ Step 5: 逐段 review
  │    └─ 产品同学确认/修改每个章节
  │
  ├─ Step 6: 完整性校验
  │    ├─ AI 对照飞书原文，列出未纳入内容
  │    └─ ✅ 确认 → metadata.yaml: prd.status = confirmed
  │
  ├─ Step 7: 可选同步回飞书
  │    └─ 提示产品执行飞书同步技能，将增强内容同步到飞书文档
  │
  └─ Step 8: 可选生成交互演示
       ├─ 读前端仓库样式（只读，不改代码仓库）
       ├─ 生成 prodspecs/<requirement-id>/index.html（资源内联）
       ├─ 更新 prodspecs/index.html 索引
       └─ git commit → GitLab CI 自动发布到 Pages
```

**下一步**：测试同学执行 `/qa-spec`，开发同学可同时执行 `/dev-start`

---

## 阶段 3：测试 spec 编写

**执行者**：测试同学
**工作上下文**：specs 仓库
**前置条件**：prd.status = confirmed
**与阶段 4 的关系**：可并行，开发不等测试 spec

```
/qa-spec
  │
  ├─ Step 1: 定位需求（自动/手动）
  │
  ├─ Step 2: 读取 prd.md
  │    └─ ⛔ 输入隔离：禁止读 openspec/changes/ 下任何开发产出
  │
  ├─ Step 3: 扫描前后端仓库
  │    └─ 输出：可测试的业务行为、入口、多端覆盖
  │
  ├─ Step 4: brainstorming（superpowers）
  │    └─ 设计测试策略：核心场景、边界、多端、数据兼容
  │
  ├─ Step 5: AI 生成 test-spec.md
  │    └─ MODULE 结构与产品 spec 严格一致
  │
  ├─ Step 6: 逐段 review
  │    └─ 测试同学确认/修改
  │
  ├─ Step 7: 覆盖率校验
  │    └─ 对照产品 spec 每条验收标准，标记未覆盖项
  │
  └─ Step 8: 确认
       └─ ✅ metadata.yaml: test_spec.status = confirmed
```

**下一步**：如开发已在进行中，通知开发通过 `pull-spec` 同步测试用例

---

## 阶段 4：开发启动

**执行者**：前端或后端开发同学
**工作上下文**：specs 仓库（多根工作区，代码仓库已加入）
**前置条件**：prd.status = confirmed（不等测试 spec）

```
/dev-start
  │
  ├─ Step 1: 定位需求（自动/手动）
  │
  ├─ Step 2: AI 扫描推荐涉及的服务
  │    ├─ ✓ 高度相关
  │    ├─ ? 可能相关
  │    └─ ✗ 不涉及
  │
  ├─ Step 3: 开发选择目标仓库
  │
  ├─ Step 4: 描述迭代范围 → AI 匹配 MODULE → 确认
  │
  ├─ Step 5: 检测工作区
  │    └─ 目标仓库不在工作区则提示添加
  │
  └─ Step 6: 无缝启动 dev-workflow ──────────────────────────┐
       传递上下文：产品 spec 内容、目标仓库、匹配的 MODULE      │
       /dev-start 本身不写入任何文件                           │
                                                              │
  ┌───────────────────────────────────────────────────────────┘
  │
  │  以下由 dev-workflow（fe-specflow / be-specflow）接管
  │  工作上下文自动切换到目标代码仓库
  ▼
```

**如需为多个仓库创建 change**：在不同会话中分别执行 `/dev-start`，各自独立启动 dev-workflow。

---

## 阶段 5：开发执行

**执行者**：前端或后端开发同学
**工作上下文**：目标代码仓库（由 `/dev-start` 无缝切入）

```
dev-workflow（fe-specflow 或 be-specflow）
  │
  ├─ 阶段 1：设计探索
  │    ├─ 扫描代码结构（目标仓库）
  │    ├─ 需求来源：自动从上下文读取产品 spec（跳过来源询问）
  │    ├─ brainstorming（技术层面设计）
  │    └─ 灰区讨论（前端灰区 / 后端灰区）
  │
  ├─ design-to-opsx（brainstorming 确认后）
  │    ├─ 确定 change-id（建议格式：<requirement-id>-<repo-name>）
  │    ├─ 创建 change 目录 ←── change 在这里创建，不是之前
  │    ├─ 写入 proposal.md（注入 requirement_ref + modules）
  │    ├─ 写入 specs/
  │    └─ 回写 specs 仓库 metadata.yaml 的 changes 字段
  │
  ├─ 阶段 2：任务规划
  │    └─ 生成 tasks.md → 用户确认
  │
  ├─ 阶段 3：T1 开发（TDD）
  │    ├─ 按 task 逐个开发
  │    ├─ git commit（需用户确认）
  │    └─ aicr 代码审查
  │
  │  ┌──── 事件驱动（异步，T1 期间随时可触发）────────────┐
  │  │  由执行层 pull-spec（workspace-aware）统一处理      │
  │  │                                                    │
  │  │  "测试 spec 到了"                                  │
  │  │    └─ pull-spec 自动从 specs 仓库 master 读取      │
  │  │         ├─ 按 MODULE 切片（只取本 change 的部分）   │
  │  │         └─ 写入 qa-spec.md 到 change 目录          │
  │  │                                                    │
  │  │  "后端/前端 spec 到了"                              │
  │  │    └─ pull-spec workspace-native 发现对方分支       │
  │  │         ├─ git fetch + git show（不 checkout）      │
  │  │         ├─ 差异分析（本方假设 vs 对方定义）          │
  │  │         └─ 写入 counterpart-api-spec.md            │
  │  └────────────────────────────────────────────────────┘
  │
  ├─ 阶段 4：验证
  │    ├─ 前置：qa-spec.md 必须已同步（测试 spec 是验证依据）
  │    └─ e2e-verify → 输出 e2e-report.md
  │
  └─ 阶段 5：归档
       └─ openspec archive（用户终端执行）
```

---

## 阶段 6：进度追踪（贯穿全程）

**执行者**：任何角色
**工作上下文**：specs 仓库

```
/req-status
  │
  ├─ 无参数 → 全部活跃需求概览
  │    示例输出：
  │    channel/contract-subject-alignment (合同管理-学科学段树与CVS对齐)
  │      产品 spec: ✓ confirmed (04-07)
  │      测试 spec: ⏳ pending
  │      Changes:
  │        ├ branstark: tasks 3/7
  │        └ channel: tasks 5/8
  │
  └─ 指定需求 → MODULE 级详情
       示例输出：
       MODULE-1: 学科树结构对齐
         产品 spec: ✓  测试 spec: 3 场景
         branstark: tasks 3/7
         channel: tasks 5/8
       MODULE-2: CVS数据补丁
         产品 spec: ✓  测试 spec: 待编写
         channel: tasks 5/8
```

---

## 完整时序图

```
时间 →

产品    ──/req-new──/pm-spec────────────────────────────────────────────────
                        │
测试    ────────────────├──/qa-spec────────────────────────────────────────
                        │                │
后端    ────────────────├──/dev-start──dev-workflow──pull-spec──verify──archive
                        │     │              │            ↑
                        │     │         design-to-opsx    │
                        │     │         (创建change+回写)  │
前端    ────────────────└──/dev-start──dev-workflow───────┤
                               │              │           │
                               │         design-to-opsx   │
                               │                          │
                               └──── pull-spec ───────────┘
                                     (workspace-aware 联调校准)
```

### 关键节点说明

| 节点 | 触发条件 | 阻塞关系 |
|------|----------|----------|
| `/req-new` | 飞书需求文档就绪 | 无 |
| `/pm-spec` | 需求目录已创建，prd.md 已有内容或有飞书链接 | 无 |
| `/qa-spec` | prd = confirmed | 不阻塞开发 |
| `/dev-start` | prd = confirmed | 不等测试 spec |
| design-to-opsx | brainstorming 确认 | 必须先完成 brainstorming |
| pull-spec（测试 spec） | test_spec = confirmed + 有活跃 change | 阻塞验证阶段 |
| pull-spec（对方 API） | 对方 change 有 proposal | 不强制，联调时使用 |
| e2e-verify | qa-spec.md 已同步 | 归档的前置条件 |

### 并行关系

```
                    ┌─ /qa-spec ─────────────────────────────┐
prd confirmed ──────┤                                       ├─ 验证阶段（汇合点）
                    ├─ /dev-start (BE) → dev-workflow ───────┤
                    └─ /dev-start (FE) → dev-workflow ───────┘
```

- 测试 spec 与 FE/BE 开发**完全并行**
- FE 与 BE 开发**完全并行**
- 验证阶段是**唯一的强汇合点**（需要 qa-spec.md）
- 联调是**弱汇合点**（需要对方 API 契约，但不强制等待）

---

## 数据流向总图

```
┌─────────────────── specs 仓库 ───────────────────┐
│                                                    │
│  requirements/<requirement>/                       │
│    ├─ metadata.yaml ◄──── /req-new 创建           │
│    │       ▲                                       │
│    │       │ 回写 changes 字段                     │
│    │       │                                       │
│    ├─ prd.md ◄── 产品撰写 + /pm-spec 增强           │
│    │       │                                       │
│    │       ├──读取──► /qa-spec                     │
│    │       └──读取──► /dev-start                   │
│    │                                               │
│    └─ test/test-spec.md ◄── /qa-spec 写入          │
│            │                                       │
│            └──读取──► pull-spec（workspace-aware）  │
│                                                    │
│  prodspecs/<requirement-id>/ ◄── /pm-spec 可选生成  │
│                                                    │
└────────────────────────────────────────────────────┘
         │ 读取产品 spec            │ 读取测试 spec
         ▼                         ▼
┌──────── 代码仓库 ────────────────────────────────┐
│                                                    │
│  openspec/changes/<change-id>/                     │
│    ├─ proposal.md ◄── design-to-opsx 写入          │
│    │     (含 requirement_ref)                      │
│    ├─ specs/ ◄── design-to-opsx 写入               │
│    ├─ tasks.md ◄── dev-workflow 阶段 2             │
│    ├─ qa-spec.md ◄── pull-spec 写入                 │
│    ├─ counterpart-api-spec.md ◄── pull-spec 写入    │
│    └─ e2e-report.md ◄── e2e-verify                │
│                                                    │
│  src/ (业务代码) ◄── dev-workflow 阶段 3 (TDD)     │
│                                                    │
└────────────────────────────────────────────────────┘
```

**信息隔离规则**：
- 产品 spec → 测试 spec：✅ 允许
- 产品 spec → 开发 spec：✅ 允许
- 开发 spec → 测试 spec：⛔ 禁止
- 代码仓库 → specs 仓库：仅 metadata.yaml 的 changes 字段回写
