# onion-sdd 安装使用流程

> 与 cursorkit 仓库 `plugins/onion-sdd/USAGE.md` 同步。OpenSpec 为变更正文唯一真相源。


Onion SDD 是一套**通用 Spec-Driven 工作流**，通过 Cursor slash command 把变更按复杂度分层：小改动走轻量流程，标准需求走完整 SDD 闭环。本文档说明**前置安装**与**日常使用**；技术细节见 README.md（见 cursorkit 仓库 onion-sdd 插件） 与 DESIGN-SUPPLEMENT.md（见 cursorkit 仓库 onion-sdd 插件）。



## 1. 它解决什么问题

| 痛点                         | Onion SDD 的做法                                                                 |
| ---------------------------- | -------------------------------------------------------------------------------- |
| 修一个按钮也要走完整设计流程 | Tier 0+/1 只写 mini/light OpenSpec，快速实现                                     |
| 大需求缺少统一门禁           | Tier 2+ 走完整 SDD：需求澄清 → OpenSpec → 外部 spec → E2E → 归档                 |
| 中断后难以恢复               | `/onsf-continue` 从 Trellis task、`.onion-sdd/current.json` 或 OpenSpec 产物恢复 |
| 流程入口不清晰               | 手动命令显式触发；`/onsf-auto` 可无交互自动推断并执行 SDD 流程                  |

**核心原则**：OpenSpec 变更目录是变更正文的唯一真相源；Agent 写 Markdown 产物；OpenSpec CLI 的创建、校验按当前环境与用户授权处理；归档由 `/onsf-finish` 在门禁通过后自动执行。

---

## 2. 前置条件

### 2.1 必装

| 依赖               | 用途                         | 如何确认                  |
| ------------------ | ---------------------------- | ------------------------- |
| **Cursor IDE**     | 运行 slash command 与 Agent  | 已安装并可打开项目        |
| **onion-sdd 插件** | 提供 `/onsf-*` 命令与 skills | 见下方「安装插件」        |
| **OpenSpec CLI**   | 创建/校验/归档 change        | 终端执行 `which openspec` |

OpenSpec 未安装时，Agent 会按降级模式手工维护 `openspec/changes/<change-id>/` 目录结构；归档时由 `/onsf-finish` 自动调用 `openspec archive <change-id>`，CLI 不可用时 Agent 会使用等效手工归档（将目录移动到 `openspec/changes/archive/<YYYY-MM-DD>-<change-id>/`，命名方式与 OpenSpec CLI 归档一致）。

### 2.2 项目内约定

业务仓库通常需要：

```text
openspec/                    # OpenSpec 根目录（与 CLI 配置一致）
openspec/changes/            # 活跃变更目录
.onion-sdd/current.json      # 可选：轻量恢复 hint（见下方说明）
```

若项目使用 Trellis，还会用到 `.trellis/tasks/**/task.json` 中的 `meta.onion` 字段做恢复与同步。

#### 运行态：Trellis 优先，`current.json` 镜像/兜底

| 项 | 现状 |
| --- | --- |
| **脚本** | `scripts/onion_state.py`（读写）、`scripts/finish_check.py`（归档预检） |
| **读** | Trellis `meta.onion` → `.onion-sdd/current.json` → OpenSpec 扫描 |
| **写** | 已绑定 Trellis task：**主写** `meta.onion` 并**镜像** `current.json`；否则**只写** `current.json` |
| **纪律** | 阶段切换必须调用 `onion_state.py`（无 Hook；靠 `/onsf-*` 硬纪律） |
| **finish** | 必须先跑 `finish_check.py`；失败不得 archive；成功后 `set --idle` |

**真相源始终是 OpenSpec** `openspec/changes/<change-id>/`。`current.json` 在有 Trellis 时是镜像与降级兜底，不是主状态源。

### 2.3 可选增强

按需安装，**不装也能跑主流程**：

| 依赖                                                             | 用途                                           | 缺失时的降级                                                                         |
| ---------------------------------------------------------------- | ---------------------------------------------- | ------------------------------------------------------------------------------------ |
| **Trellis**                                                      | task 生命周期、parent/child、journal、工程计划 | 仅用 `.onion-sdd/current.json` + OpenSpec 恢复（见 §8） |
| **user-yapi-common-mcp** + `YAPI_BASE_URL` / `YAPI_GLOBAL_TOKEN` | 拉取 YApi 接口契约                             | 用户粘贴接口文档，Agent 按模板整理                                                   |
| **飞书 MCP**                                                     | 读取飞书需求文档                               | 用户粘贴正文或导出文件                                                               |
| **Figma MCP**                                                    | 读取设计稿（前端 Tier 2+）                     | 用户描述或截图                                                                       |
| **common 插件 `create-feature-branch`**                          | 按飞书卡片创建 feature 分支                    | 提示手动建分支                                                                       |
| **common 插件 `aicr-local`**                                     | check 阶段自动审查本次 change 的暂存区 diff    | Agent 对暂存区自审，不阻塞 check                                                     |
| **Cursor 内置浏览器**                                            | Tier 2+ E2E 自动化                             | 手工验证并写入 `e2e-report.md`                                                       |

---

## 3. 安装插件

### 3.1 团队 Marketplace（推荐）

本插件已注册在 onions-plugins Marketplace（`onion-sdd`）：

1. 打开 Cursor **Settings → Plugins → Team Marketplaces**
2. 添加或选择团队 Marketplace（指向包含 `.cursor-plugin/marketplace.json` 的仓库）
3. 在插件列表中安装 **Onion SDD 工作流**（`onion-sdd`）
4. 重启 Cursor 或重新加载窗口

安装成功后，在 Agent 输入框输入 `/` 应能看到：

- `/onsf-plan`
- `/onsf-auto`
- `/onsf-fix`
- `/onsf-tweak`
- `/onsf-continue`
- `/onsf-finish`

### 3.2 本地调试

开发或试点时，可手动指定插件路径：

```text
plugins/onion-sdd/
```

在 Cursor 插件设置中添加该目录作为本地插件源即可。

### 3.3 安装 OpenSpec CLI

按团队或 OpenSpec 官方文档 安装 CLI，确保业务仓库根目录可执行：

```bash
which openspec
openspec validate   # 可选：确认与项目配置兼容
```

---

## 4. 六个命令怎么用

| 命令                 | 什么时候用                               | 典型 Tier     |
| -------------------- | ---------------------------------------- | ------------- |
| **`/onsf-plan`**     | **主入口**：不确定改多大、该走哪条流程   | 自动判断 0～3 |
| **`/onsf-auto`**     | 无交互自动执行 SDD 流程，直到实现、验证、自审完成 | 自动判断 0～3 |
| **`/onsf-fix`**      | 已确认的小修复、低风险配置、紧急线上故障 | 0+ / 0++      |
| **`/onsf-tweak`**    | 单页面/单组件的轻量体验或行为调整        | 1             |
| **`/onsf-continue`** | 接着上次的 change 做                     | 任意          |
| **`/onsf-finish`**   | 实现和验证做完，检查能否归档             | 任意          |

**纪律**：

- 用 slash command 触发，不要指望 Agent 自动猜流程。
- 希望 Agent 自动跑完整 SDD 流程时，用 `/onsf-auto`；它会在高风险或不可逆节点停止。
- Agent 在 `/onsf-finish` 门禁通过后会**自动** `openspec archive <change-id>`；CLI 不可用时使用等效手工归档。
- Agent 不会自动提交代码 commit（Phase 3.4 前置）；`/onsf-finish` 仅自动提交 openspec 归档移动这一项 scoped chore，不自动 push/PR。

---

## 5. Tier 怎么选（速查）

不确定时一律先 **`/onsf-plan`**。

| Tier    | 场景                                           | 流程                                 | OpenSpec 粒度                   |
| ------- | ---------------------------------------------- | ------------------------------------ | ------------------------------- |
| **0**   | 只问问题、排查、审阅；或纯 lint/类型/文档/配置 | 直接回答或改完说明验证               | 无                              |
| **0+**  | 问题已定位、方案唯一、≤3 文件、验证清晰        | `/onsf-fix` → mini change            | `proposal.md` + `tasks.md`      |
| **0++** | 线上 P0/P1、30 分钟内可修完                    | **先修后补**，24h 内补 mini OpenSpec | 事后补                          |
| **1**   | 单模块小交互/体验，无新接口                    | `/onsf-tweak` → light change         | 上述 + 可选 `specs/**/spec.md`  |
| **2**   | 跨模块、接口契约、权限、支付、E2E 门禁         | `/onsf-plan` → 完整 SDD              | 完整 OpenSpec + 外部 spec + E2E |
| **3**   | 多仓、多阶段、需拆父子任务                     | 先拆分，每子任务走 Tier 2            | parent/child change             |

**升级红线**（出现任一条就不要继续 mini/light，改用 `/onsf-plan`）：

- 接口字段、错误码、数据模型、状态机变更
- 权限、安全、支付、资金、审计
- 跨多个模块/仓库/角色
- 需要后端 spec、QA spec 或 E2E 报告作门禁
- 需求或验收标准一次简短确认仍说不清

---

## 6. 典型使用流程

### 6.1 小修复（Tier 0+）

```text
/onsf-fix 支付按钮在 Safari 17 点击无响应
```

Agent 会：

1. 确认仍为 Tier 0+（否则建议 `/onsf-plan`）
2. 在 `openspec/changes/<change-id>/` 写 mini `proposal.md`、`tasks.md`
3. 实现改动并做定向验证
4. 把验证命令和结果写回产物

你收尾：`/onsf-finish`（自动归档 OpenSpec change）

### 6.2 轻量调整（Tier 1）

```text
/onsf-tweak 搜索框加 300ms 防抖
```

比 mini 多要求：`spec.md`（至少 1 个 Requirement + 场景）、明确的「不做范围」、可复现的验证计划。

### 6.3 标准需求（Tier 2+）

```text
/onsf-plan 用户角色从两种扩展到三种，涉及权限判断
```

完整阶段（由 Agent 按产物推断当前步）：

```text
triage → discover → research → design → openspec → implement → check
  → integrate（后端/QA/YApi spec）→ verify（E2E）→ finish
```

主要产物：

```text
openspec/changes/<change-id>/
├── proposal.md
├── tasks.md
├── specs/<capability>/spec.md
├── backend-*.md / backend-yapi-*.md   # 外部接口 spec
├── qa-*.md                            # 测试 spec
└── e2e-report.md                      # Tier 2+ 验收门禁
```

实现纪律（Tier 2+，详见 `rules/onion-sdd.mdc` 与 `skills/full-change/SKILL.md`）：

- **TDD 红绿循环**：能写自动化测试的任务走 失败用例 → 最小实现 → 通过；不得先实现再补测试。
- **前端分层验证**：L1 契约/mock → L2 行为 Scenario → L3 联调/真实 API → L4 Browser 交叉验证。
- **任务粒度**：`tasks.md` 按**可验证交付物**拆分（不是按代码行数），Tier 2 通常 3-8 个 task，每个 task 有独立可执行验证点。
- **verify 前置门禁**：`verify-change` 先给 TDD/静态验证清单结论，再进入浏览器自动化。
- **需求调整同步**：实现中用户**明确表达**需求/验收口径调整时，暂停实现，按 `openspec-change` 的「已落盘产物的更新协议」回写 `proposal.md` / `specs/**/spec.md` / `tasks.md` 并追加 `## 需求调整记录`，再继续；触发升级红线则回到 `tier-triage`。澄清/补充不触发。

### 6.3.1 自动化执行

```text
/onsf-auto 用户角色从两种扩展到三种，涉及权限判断
```

Agent 会自动推断是新建、继续、验证还是收尾检查，并按 `auto-flow` 执行：

```text
recover → infer → triage → materialize → spec-review
  → implement → diff-review → verify → close
```

自动化策略：

- 低/中风险缺口：写明假设后继续。
- 高风险缺口：停止并输出 blocker。
- 可以自动实现和验证。
- 不自动 commit、push、创建 PR/MR 或 Trellis archive。
- `/onsf-finish` 门禁通过后自动 `openspec archive <change-id>`；CLI 不可用时使用等效手工归档。
- 没有 active Trellis task 时不自动创建；已有 active task 时只同步 `meta.onion`。

可显式指定子模式：

```text
/onsf-auto new
/onsf-auto continue
/onsf-auto verify
/onsf-auto finish-check
```

事件驱动（在 `/onsf-continue` 或对话中说）：

| 你说                    | Agent 做什么                    |
| ----------------------- | ------------------------------- |
| 后端 spec 到了 `<链接>` | `external-spec` 落盘并差异分析  |
| YApi 到了 / re-check    | `re-check` 对齐 mock、类型、API |
| 只拉 YApi / 只落盘契约  | `pull-yapi`，不改业务代码       |
| 测试 spec 到了          | 写入 `qa-*.md`                  |
| 跑 e2e / 浏览器验证     | `verify-change`                 |

### 6.4 紧急线上故障（Tier 0++）

```text
/onsf-fix P0：线上支付链路挂了，根因是事件绑定写错
```

允许**先修复上线**，24 小时内补 mini OpenSpec（根因、修复内容、验证、回滚方案）。

### 6.5 中断后继续

```text
/onsf-continue
```

恢复优先级：

1. Trellis active task 的 `task.json.meta.onion.change_id`
2. `.onion-sdd/current.json` 的 `active_change_id`
3. 扫描 `openspec/changes/**` 或请你指定 change-id

需求调整恢复路径：如果中断原因是用户表达了需求或验收口径调整（新增、修改、废弃目标/范围/验收场景），`/onsf-continue` 会按 `openspec-change` 的「已落盘产物的更新协议」先同步 `proposal.md`、`specs/**/spec.md`、`tasks.md` 并追加 `## 需求调整记录`，再继续实现；触发升级红线则回到 `tier-triage` 重新分级。用户澄清已有需求、补充细节或回答提问不视为调整。

### 6.6 收尾与归档

```text
/onsf-finish
```

检查任务闭合、验证证据、带债项；通过后自动执行 `openspec archive <change-id>`（CLI 不可用时使用等效手工归档）。

`/onsf-finish` 对绑定 Trellis task 的 change 一并自动归档 task + journal（委托 `trellis-finish-work` skill），无需再跑 `/trellis:finish-work`；纯 Trellis 任务（无 OpenSpec change）仍走 `/trellis:finish-work`。

---

## 7. OpenSpec 与 Agent 分工

| 操作                                                       | 谁来做                                        |
| ---------------------------------------------------------- | --------------------------------------------- |
| 写 `proposal.md`、`specs/`、`tasks.md`、`e2e-report.md` 等 | **Agent**（按 onion skills 模板）             |
| 需求调整时同步 OpenSpec 产物（proposal/specs/tasks + `## 需求调整记录`） | **Agent**（按 `openspec-change` 的「已落盘产物的更新协议」） |
| `openspec new change` / `validate`                       | **你**在终端执行（Agent 可手工创建目录作为降级） |
| `openspec archive`                                       | **Agent** 在 `/onsf-finish` 门禁通过后自动执行；CLI 不可用时等效手工归档 |
| 维护运行态（`meta.onion` / `current.json`）                 | **Agent** 阶段切换必须调用 `onion_state.py`（Trellis 主写 + current 镜像/兜底） |
| check 阶段暂存本次 change 改动 + `/cr` 审查暂存区            | **Agent** 自动执行，无需你输入命令；禁止 `git add -A`，归属存疑的文件会先请你确认 |
| git commit / push                                          | **你**明确要求时 Agent 可协助；暂存区自 check 的 CR 通过后未变化则直接 commit，有任何变化（含新增暂存文件）或无法判定则重新 `/cr` |

---

## 8. Trellis 集成（可选但推荐）

Trellis 负责**任务生命周期、工程计划、分支、journal 和跨会话恢复**；Onion SDD 负责**变更分级、OpenSpec 正文、外部 spec 与 E2E 门禁**。两者通过 `trellis-adapter` 协议衔接，**互不替代**。

没有 Trellis 时，Onion SDD 仍可用 `.onion-sdd/current.json` + OpenSpec 独立运行；接入 Trellis 后恢复更稳、Tier 2+ 大需求更易跟踪。

### 8.1 两者分工

| 职责                              | Onion SDD                                   | Trellis                                     |
| --------------------------------- | ------------------------------------------- | ------------------------------------------- |
| 变更复杂度分级（Tier）            | ✅ `tier-triage`                            | —                                           |
| 需求正文、行为 spec、验收报告     | ✅ OpenSpec `openspec/changes/<change-id>/` | —                                           |
| 产品/验收维度任务清单             | ✅ OpenSpec `tasks.md`                      | —                                           |
| 工程执行计划、验证命令、回滚点    | —                                           | ✅ `implement.md`                           |
| feature 分支、PR 目标分支         | 记录摘要                                    | ✅ `task.json.branch` / `base_branch`       |
| 跨会话恢复 change-id              | ✅ `.onion-sdd/current.json`                | ✅ `task.json.meta.onion`                   |
| 开发者 journal、会话摘要          | 未绑定 Trellis task 时，`/onsf-finish` 归档成功后自动写入 | ✅ 绑定 task 时，`/onsf-finish` 委托 `trellis-finish-work` skill 写入 `.trellis/workspace/<name>/journal-*.md`（无需用户手动跑 `/trellis:finish-work`） |
| spec 经验积累（`.trellis/spec/`） | 未绑定 Trellis task 时，`/onsf-finish` 归档成功后加载 `trellis-update-spec` 判断并按需写入 | ✅ 绑定 task 时，走 workflow.md Phase 3.3（`trellis-update-spec`）写入 |
| parent/child 大任务拆分（Tier 3） | OpenSpec parent/child change                | ✅ Trellis parent/child task tree           |
| OpenSpec 归档                     | ✅ Agent 在 `/onsf-finish` 中自动执行          | —                                           |
| Task 归档                         | —                                           | `/trellis:finish-work` 或 `task.py archive` |

**硬边界**：OpenSpec 是变更正文唯一真相源。Agent **不会**把 `proposal.md` 全文复制到 Trellis `prd.md` 或 journal；`meta.onion` 只存引用（change-id、path、tier、phase、hash）。

### 8.2 Trellis 安装与初始化

Trellis 与 `onion-sdd` 是**两个独立组件**，需分别安装。

#### 第一步：安装 Trellis CLI

```bash
# 全局安装（推荐）
npm install -g @mindfoldhq/trellis

# 或临时使用
npx @mindfoldhq/trellis --help

# 确认可用
trellis --version
```

#### 第二步：在业务仓库初始化 Trellis

在**项目根目录**执行（按你使用的 AI 平台选 flag）：

```bash
cd /path/to/your-project

# Cursor 用户（同时可叠加其它平台）
trellis init -u your-name

# 常见组合示例
# 显式：配置一个或多个平台
trellis init -u your-name --claude
trellis init -u your-name --claude --cursor --opencode
trellis init -u your-name --codex --gemini
trellis init -u your-name --pi
```

`trellis init` 会生成：

```text
.trellis/
├── workflow.md          # 开发阶段与 skill 路由（Plan / Execute / Finish）
├── config.yaml          # 项目级配置
├── spec/                # 编码规范（按 package/layer 组织）
├── scripts/             # task.py、get_context.py 等（勿手改）
├── tasks/               # 活跃任务目录
└── workspace/           # 开发者 journal

.agents/skills/          # Trellis bundled skills（trellis-start、finish-work 等）
```

初始化后还会创建 bootstrap 任务（如 `00-bootstrap-guidelines`），用于熟悉 Trellis 工作流。

#### 第三步：注册开发者身份（首次必做）

```bash
python3 ./.trellis/scripts/init_developer.py <你的名字>
```

生成 `.trellis/.developer`（gitignore）和 `.trellis/workspace/<你的名字>/`。

#### 第四步：安装 onion-sdd 插件

见本文 §3 安装插件。Trellis **不会**自动安装 onion-sdd；需在 Cursor Team Marketplace 或本地路径单独安装。

#### 第五步：确认 OpenSpec 就绪

```bash
which openspec
# 业务仓库应有 openspec/changes/ 目录（与 OpenSpec CLI 配置一致）
```

#### 保持同步

```bash
trellis update    # 升级 bundled skills、脚本模板（不覆盖你已改过的文件）
```

#### 自动询问安装（Tier 2+/3）

以上步骤也可以不用手动跑：**Tier 2+/3 首次触发且检测到 Trellis 未安装时**，Agent 会主动询问是否现在安装并初始化。同意后先探测 `trellis --version`——CLI 已全局安装（只是本项目未 `trellis init`）则跳过安装步骤，否则先 `npm install -g @mindfoldhq/trellis`——再执行 `trellis init -u <name> --<当前平台>`，并把该平台的整目录忽略规则（如 `.cursor/`）追加到根 `.gitignore`（与本仓库现状写法一致）。拒绝或安装失败不会阻塞流程，会按现状"Trellis 不可用"路径继续。该询问只在手动入口（`/onsf-plan` 等）生效，`/onsf-auto` 无交互场景不触发。

### 8.3 前期准备清单

开始 Onion SDD + Trellis 协作前，逐项确认：

| #   | 检查项                    | 如何确认                           |
| --- | ------------------------- | ---------------------------------- |
| 1   | Trellis CLI 已安装        | `trellis --version`                |
| 2   | 项目已 `trellis init`     | 存在 `.trellis/workflow.md`        |
| 3   | 开发者身份已注册          | 存在 `.trellis/.developer`         |
| 4   | onion-sdd 插件已安装      | 输入 `/` 能看到 `/onsf-plan` 等    |
| 5   | OpenSpec CLI 可用         | `which openspec`                   |
| 6   | 变更目录存在              | `openspec/changes/` 可写           |
| 7   | （Tier 2+ 前端）可选 MCP  | 飞书 / Figma / YApi 按需配置       |
| 8   | （需要分支时）Common 插件 | `create-feature-branch` skill 可选 |

**首次进入项目建议**：在 Agent 中执行 `/trellis:start`（或加载 `trellis-start` skill），让 Agent 跑 `get_context.py` 加载 workflow、当前 task 和规范索引。

### 8.4 在流程里何时用 Trellis

| 场景                   | 是否建 Trellis task | 说明                                                             |
| ---------------------- | ------------------- | ---------------------------------------------------------------- |
| Tier 0 纯问答/排查     | 否                  | 直接回答，无 OpenSpec                                            |
| Tier 0 内部修正/纯文档 | 可选                | 通常不需要                                                       |
| Tier 0+ / 0++ mini fix | 可选                | 小修复可只走 OpenSpec；团队要求审计时可建轻量 task               |
| Tier 1 light change    | 可选                | 同上                                                             |
| **Tier 2+ 标准需求**   | **推荐**            | Agent 会在规划阶段询问是否创建 Trellis task                      |
| **Tier 3 拆分任务**    | **必须**            | parent task + 多个 child task，映射 OpenSpec parent/child change |

创建 task 的典型命令（Agent 或你手动执行）：

```bash
python3 ./.trellis/scripts/task.py create "<任务标题>" [--slug <目录名>]
python3 ./.trellis/scripts/task.py start <目录名>     # 设为当前 active task
python3 ./.trellis/scripts/task.py set-branch <目录名> <feature-branch>   # 分支创建后
```

Tier 2+ 进入实现前，Trellis 侧通常还需要：

- `prd.md` — 轻量任务摘要（**不是** OpenSpec 全文复制）
- `design.md` + `implement.md` — 复杂任务的工程计划
- `task.py start` — 用户确认规划后，status 从 `planning` → `in_progress`

Onion 侧同步写入 `task.json.meta.onion`（由 Agent 通过 `trellis-adapter` 维护）：

```json
{
  "version": 1,
  "change_id": "add-invoice-export",
  "change_path": "openspec/changes/add-invoice-export",
  "tier": "2",
  "phase": "implement",
  "last_action": "tasks.md 第 2 项完成，待 trellis-check",
  "last_action_at": "2026-06-25T18:30:00+08:00",
  "upgrade_risk": false,
  "source_hashes": { "proposal": "sha256:...", "tasks": "sha256:..." }
}
```

### 8.5 命令对照：Onion vs Trellis

两套 slash command **各管一段**，不要混用职责：

| 你的意图                                       | 用 Onion                    | 用 Trellis                 |
| ---------------------------------------------- | --------------------------- | -------------------------- |
| 判断变更该走 mini/light/完整流程               | `/onsf-plan`                | —                          |
| 小修复 / 轻量调整                              | `/onsf-fix` / `/onsf-tweak` | —                          |
| **恢复 OpenSpec change 上下文**                | **`/onsf-continue`**        | —                          |
| 恢复 Trellis task 阶段（plan/implement/check） | —                           | **`/trellis:continue`**    |
| 新会话加载项目上下文                           | —                           | `/trellis:start`           |
| 检查并自动归档 OpenSpec change                 | `/onsf-finish`              | —                          |
| 归档 Trellis task + 写 journal                 | `/onsf-finish`（绑定 task 时自动委托） | **`/trellis:finish-work`**（纯 Trellis 任务） |
| 实现前读规范                                   | —                           | `trellis-before-dev`       |
| 实现后质量审查（check 第 1 步）                | —                           | `trellis-check`            |
| check 阶段代码审查（第 3 步，审暂存区）        | 编排内自动调用 `/cr`        | —                          |
| 需求探索（Tier 2+ discover）                   | 编排内调用                  | `trellis-brainstorm`       |

**恢复优先级**（`/onsf-continue`）：

1. Trellis active task 的 `meta.onion.change_id`
2. `.onion-sdd/current.json` 的 `active_change_id`
3. 扫描 `openspec/changes/**` 或请你指定 change-id

若 Trellis 与 `current.json` 指向不同 change，默认以 **Trellis active task** 为准。

### 8.6 典型协作流程（Tier 2+）

```text
1. 新需求
   └─ /onsf-plan <需求描述>
        ├─ Tier 判断 → 确认 Tier 2
        ├─ Agent 询问：是否创建 Trellis task？ → 你确认「是」
        ├─ task.py create + trellis-brainstorm 澄清需求
        └─ openspec-change 落盘 proposal / specs / tasks

2. 进入实现
   └─ task.py start <task>          # Trellis: planning → in_progress
   └─ trellis-before-dev            # 读 .trellis/spec 相关规范
   └─ 按 OpenSpec tasks.md 实现
   └─ check 四步（Agent 自动，无需输入命令）
        ├─ trellis-check            # lint / typecheck / 测试 / .trellis/spec 对齐
        ├─ 暂存本次 change 改动      # 禁止 git add -A
        ├─ /cr 审查暂存区            # 团队规范 / 安全风险 / 影响范围
        └─ 修复 → 回跑受影响门禁 → 重新暂存 → 复审

3. 外部 spec / YApi 到达
   └─ /onsf-continue（或对话中说「后端 spec 到了」）
   └─ external-spec / pull-yapi / re-check

4. 验收
   └─ verify-change → e2e-report.md
   └─ /onsf-finish                   # 检查 OpenSpec 归档条件并自动归档

5. 收尾（顺序重要，0.1.4 起）
   └─ 用户确认提交 → 暂存区自 check 的 CR 通过后未变化则直接 commit；有变化或无法判定则重新 `/cr` 再 commit（Phase 3.4，工作区须干净）
   └─ /onsf-finish                     # 自动归档 OpenSpec change +（绑定 task 时）自动归档 Trellis task + journal
```

**单命令收尾（0.1.4 起）**：先 OpenSpec 验收通过 → 用户确认提交 → 按提交门禁判断是否复审（暂存区自 check 的 CR 通过后未变化则直接提交；有任何变化，含新增暂存文件，或无法判定则重新 `/cr`）→ 代码 commit（Phase 3.4，工作区须干净）→ `/onsf-finish`（自动归档 OpenSpec change；绑定 Trellis task 时一并自动归档 task + journal，无需再跑 `/trellis:finish-work`）。CR 已在 check 阶段完成，常规路径下同一份代码只审一遍。未安装或无法使用 `aicr-local` 时，降级为 Agent 自审暂存区。OpenSpec 未通过时，**不要**执行 `/onsf-finish`。纯 Trellis 任务（无 OpenSpec change）仍走 `/trellis:finish-work`。

### 8.7 Tier 3：父子任务

大需求拆分时：

```bash
# Parent
python3 ./.trellis/scripts/task.py create "发票导出总览" --slug 06-25-invoice-export

# Children
python3 ./.trellis/scripts/task.py create "后端 API" --slug 06-25-invoice-api --parent 06-25-invoice-export
python3 ./.trellis/scripts/task.py create "前端页面" --slug 06-25-invoice-ui --parent 06-25-invoice-export
```

OpenSpec 侧对应 parent change + 多个 child change；child 的 `meta.onion.parent_change_id` 指向 parent。每个 child 独立走 Tier 2 流程、独立归档。

### 8.8 Trellis 相关 FAQ

**Q：只装 onion-sdd，不装 Trellis 可以吗？**  
A：可以。mini/light 和小型 fix 通常不需要 Trellis；你会失去 task 树、journal 和 `meta.onion` 恢复能力。

**Q：只装 Trellis，不装 onion-sdd 可以吗？**  
A：可以走 Trellis 原生 workflow，但没有 Tier 分级、OpenSpec 专项门禁和 `/onsf-*` 命令。

**Q：OpenSpec 和 Trellis task 必须一一对应吗？**  
A：Tier 2+ 推荐 1:1；Tier 0+/1 可以只有 OpenSpec 无 task。`meta.onion.change_id` 是绑定键。

**Q：Agent 会自动创建 Trellis task 吗？**  
A：复杂任务会先**询问你**是否创建（Trellis workflow-state 约定）；你确认后才会 `task.py create`。

**Q：`/onsf-continue` 和 `/trellis:continue` 选哪个？**  
A：要接着 OpenSpec change（spec、tasks、E2E）→ `/onsf-continue`；要接着 Trellis 工程阶段（plan/implement/check/commit）→ `/trellis:continue`。Tier 2+ 常两者交替使用。

**Q：`.onion-sdd/current.json` 会自动更新吗？**  
A：阶段切换须由 Agent 调用 `onion_state.py` 更新（有 Trellis 时主写 `meta.onion` 并镜像 current；无 Trellis 时只写 current）。无 Hook。`/onsf-continue` 优先 `onion_state.py get`。没有 `current.json` 也能继续（可指定 change-id 或扫 OpenSpec）。

**Q：Trellis metadata 写坏了怎么办？**  
A：忽略 `meta.onion`，用 `.onion-sdd/current.json` + OpenSpec 目录恢复；OpenSpec 正文不会被删。

---

## 9. 常见问题

**Q：必须装 fe-specflow / be-specflow 吗？**  
A：不必。onion-sdd 是独立流程，不依赖其他 SDD 插件。

**Q：可以用自然语言说「继续」「归档」吗？**  
A：手动流程仍建议使用明确 slash command。需要 Agent 自动推断 new/continue/verify/finish-check 时，使用 `/onsf-auto`；`/onsf-finish` 门禁通过后会自动归档，但不会自动提交。

**Q：mini change 的 proposal 写多细？**  
A：至少包含：可复现的背景、根因（不只现象）、影响文件路径、别人能照着做的验证步骤。见 `skills/mini-change/SKILL.md` 质量自检。

**Q：Tier 2 没有 E2E 能归档吗？**  
A：默认不能；除非有等价验收证据且用户在 `e2e-report.md` 中确认。

**Q：两个 change 改同一文件怎么办？**  
A：`/onsf-plan` 会扫描活跃 change 并警告冲突；需你确认是否协调或合并。

**Q：YApi MCP 不可用？**  
A：粘贴接口文档即可；Agent 按 `pull-yapi` 模板整理，并在输出中说明降级。

---

## 10. 一张图看全流程

```text
                    ┌─────────────────┐
                    │   /onsf-plan    │  ← 不确定时从这里开始
                    └────────┬────────┘
                             │ Tier 判断
         ┌───────────────────┼───────────────────┐
         ▼                   ▼                   ▼
    Tier 0/0++           Tier 0+/1            Tier 2/3
    直接答/先修后补    /onsf-fix            完整 SDD
                       /onsf-tweak          (full-change 编排)
         │                   │                   │
         └───────────────────┴───────────────────┘
                             │
                    ┌────────▼────────┐
                    │ /onsf-continue  │  ← 中断恢复
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  /onsf-finish   │  ← 验收与自动归档
                    └────────┬────────┘
                             │
              自动执行: openspec archive <change-id>
              (绑定 Trellis task 时) 一并 task.py archive + add_session（自动）
```

有 Trellis 时，完整链路（0.1.4 起，commit 前置于 /onsf-finish）：

```text
/onsf-plan → Trellis task 创建 → OpenSpec 落盘 → 实现
  → check 四步（trellis-check → 暂存本次 change → /cr 审暂存区 → 修复复审）
  → 外部 spec → verify-change → commit（Phase 3.4，暂存区未变化则不复审）
  → /onsf-finish（自动归档 OpenSpec + 绑定 task + journal）
```

---

## 11. 进一步阅读

| 文档                                           | 内容                                       |
| ---------------------------------------------- | ------------------------------------------ |
| README.md（见 cursorkit 仓库 onion-sdd 插件）                       | 能力清单、目录结构、Trellis adapter 协议   |
| DESIGN-SUPPLEMENT.md（见 cursorkit 仓库 onion-sdd 插件） | Tier 决策树、带债归档、Revert、Tier 3 占位 |
| `skills/tier-triage/SKILL.md`                  | Tier 判定完整规则                          |
| `skills/full-change/SKILL.md`                  | Tier 2+ 阶段编排                           |
| `templates/current.example.json`               | 运行时状态文件示例                         |
| `skills/trellis-adapter/SKILL.md`              | OpenSpec ↔ Trellis metadata 同步协议       |
| `.trellis/workflow.md`                         | Trellis 开发阶段与 skill 路由（项目内）    |
