---
name: figma-read-skill
description: >-
  从 Figma 设计稿生成高保真前端代码的核心工作流。
  覆盖 Figma MCP 数据读取、组件实例识别与 onion-ui 组件库匹配、
  Auto Layout → Flex / Grid 映射、完整样式字段提取（布局 / 文本 / 填充 / 描边 / 圆角 / effects / 透明度）、
  design token 映射、2x 设计稿 ÷2 尺寸换算、Lottie 动效处理，
  以及生成后 1:1 截图 + computed style 数值对比验证。
  当用户提供 Figma 链接（figma.com/design、figma.com/file、含 node-id 参数），
  粘贴 Figma 节点 ID（如 `123:456`、`I43:384;65:6890`），
  要求"实现 / 还原 / 开发 / 搭建 / 生成 / 写 / 做"某个页面或组件，
  或提到"设计稿转代码"、"Figma to Code"、"按设计稿开发"、"按图开发"、
  "视觉还原"、"1:1 还原"、"高保真还原"、"设计走查"、"设计稿对比"、"还原度"、
  "pixel perfect"、"get_design_context"、"get_screenshot"、"Figma MCP"
  时触发；若页面涉及响应式适配，须先执行 `responsive-layout-analysis`。
requires:
  - responsive-layout-analysis  # 响应式页面前置分析（必须先于本 skill 执行）
  - responsive-layout            # CSS 断点体系与响应式布局规范
  - figma-img-cdn-skill          # 图片图层识别与 CDN 上传处理
  - onion-ui-skill               # onion-ui 组件库版本确认与组件文档查询
  - design-tokens                # Design Token 接入与 CSS 变量规范
mcp:
  - figma-read-mcp                      # 【主路径】本地 Figma Desktop Dev Mode（127.0.0.1:3845）。get_design_context / get_screenshot 等读设计稿工具
  - figma-write-mcp                     # 【降级路径】Figma 官方在线 MCP（mcp.figma.com）。工具集包含同名 get_design_context / get_screenshot，本地 Dev Mode 未启用时切换到此通道
  - user-@guanghe-pub/yc-cdn-mcp-server  # cdn_compress_and_upload / cdn_batch_compress_and_upload（图片上传）
---

# Figma 设计稿转代码 · 编排器

本 skill 为**单 agent 编排器**。详细规则分布在三个 phase 文件中，按步骤按需 Read 入上下文，避免一次性吞下全部规则导致跳步与幻觉。

> **架构选型说明**：早期版本曾用 Task 工具拆出两个 sub-agent 并行/隔离执行，实测显著变慢（sub-agent 冷启动 + 上下文重建 + `get_design_context` 数据重传 + 串行无并行收益）。当前版本回归"单 agent + phase 文件按需 Read"——`get_design_context` 数据、设计稿截图、项目结构等上下文在编排器内自然复用，不再跨 agent 重传。

## 架构说明

```
本 SKILL.md（编排器，单 agent 全程执行）
  ├─ Step 0a：响应式前置检查（如需要）
  ├─ Step 0b：Figma MCP 通道选择（主：figma-read-mcp / 降级：figma-write-mcp）
  ├─ Step 0c：⛔ Read 全部 5 个 requires skill 入口文件（硬阻断，不读不得继续）
  ├─ Step 1–2：直接执行（Figma MCP 调用，遵循 Step 0b 的通道选择）
  ├─ Step 3：Read phase-1-dependency-check.md → 依赖探查 + Step 3d 加载断言
  ├─ Step 4–8：Read phase-2-audit-and-codegen.md → 审计 + 代码生成
  │           （并按需 Read references/figma-fields-reference / references/auto-layout-to-flex 等子文档）
  └─ Step 9：Read phase-3-verification.md → 三级验证
```

## 目录约定（新增文档前必读）

本 skill 的子文档按"角色"分两类，物理位置不同、链接写法也不同。结构如下：

```
figma-read-skill/
├── SKILL.md                              ← 编排器入口（本文件）
│
│   ─────────── [流程主线] 与 SKILL.md 同级，被某个 Step 整段消费 ───────────
│
├── phase-1-dependency-check.md           ← Step 3   整段消费（依赖探查）
├── phase-2-audit-and-codegen.md          ← Step 4–8 整段消费（审计 + 代码生成）
├── phase-3-verification.md               ← Step 9   整段消费（三级验证）
├── implementation-audit-template.md      ← Step 7   填表参照（figma-audit.md 模板权威源）
│
│   ─────────── [按需查表] 在 references/ 下，命中字段 / 场景才 Read ─────────
│
└── references/
    ├── figma-fields-reference.md         ← Figma 字段 → CSS 完整映射
    ├── auto-layout-to-flex.md            ← Auto Layout → Flex / Grid 字段映射
    ├── style-css-examples.md             ← 阴影 / 渐变 / 毛玻璃 / 外描边 CSS 示例
    ├── size-units.md                     ← ÷2 换算 / 非整数像素 / 字号下限
    └── lottie-setup.md                   ← 首次引入 Lottie 的工具文件模板
```

**两类文件的核心差异**：

|  | 流程主线（根目录） | 按需查表（`references/`） |
|---|---|---|
| 与 SKILL.md 关系 | 「主-从」编排，被 Step 整段 Read | 「引用」，单次流程可能完全不 Read |
| 链接写法 | `[xxx.md](xxx.md)` | `[references/xxx.md](references/xxx.md)` |
| 新增文档判定 | Step X 明确写"Read xxx" → 这里 | 仅字段 / 场景查阅 → 这里 |

**链接写法铁律**（历史 bug `cf53224` 就是写错路径导致的，现已由脚本自动守护）：

- 根目录文件之间互相引用 → 路径**不带** `references/`
- 引用 `references/` 下子文档 → 路径**必须带** `references/` 前缀
- 修改下方「参考文档索引」表时，必须同步移动对应文件的物理位置

> **自动守护**：上述三条规则与"链接目标存在性"由 [scripts/check-skill-links.sh](scripts/check-skill-links.sh) 校验。在提交前 / CI 中运行；脚本退出码非 0 即视为路径错位 bug，必须修复后再合并。

**为什么不全部统一进 `references/`**：phase 系列是编排器的"流程主线"，与 SKILL.md 同级；塞进 `references/` 会让"主线"被名字降级为"参考资料"。

## 参考文档索引

> 链接路径已遵循上方「目录约定」。修改本表时务必同步更新对应文件的物理位置，**禁止**只改 SKILL.md 链接而不动文件。

| 文件 | 角色 | 阶段 | 用途 |
|---|---|---|---|
| [phase-1-dependency-check.md](phase-1-dependency-check.md) | 流程主线 | Step 3 | pnpm workspace / 入口文件 / CDN MCP 三步探查 |
| [phase-2-audit-and-codegen.md](phase-2-audit-and-codegen.md) | 流程主线 | Step 4–8 | 组件识别 / 样式提取 / 布局分析 / 尺寸单位 / 图片 / 动效 + 检查清单 B–G |
| [phase-3-verification.md](phase-3-verification.md) | 流程主线 | Step 9 | 三级验证流程 / 差异表 / 兜底话术 |
| [implementation-audit-template.md](implementation-audit-template.md) | 流程主线 | Step 4–8 | 审计记录模板（生成 figma-audit.md 时参照） |
| [references/figma-fields-reference.md](references/figma-fields-reference.md) | 按需查表 | Step 4–8 按需 | Figma 字段 → CSS 映射 |
| [references/auto-layout-to-flex.md](references/auto-layout-to-flex.md) | 按需查表 | Step 4–8 按需 | Auto Layout → Flex 完整映射 |
| [references/style-css-examples.md](references/style-css-examples.md) | 按需查表 | Step 4–8 按需 | box-shadow / 渐变 / 毛玻璃 / 外描边等 CSS 写法 |
| [references/size-units.md](references/size-units.md) | 按需查表 | Step 4–8 按需 | ÷2 换算对照表 / 非整数像素 / 字号下限 |
| [references/lottie-setup.md](references/lottie-setup.md) | 按需查表 | Step 4–8 按需 | 项目首次引入 Lottie 的模板代码 |

---

## 硬阻断（全流程强制）

> Figma MCP 返回的 React + Tailwind 代码只是参考数据，不是可直接改写的实现方案。

> **本节定位**：编排器级别的"红线索引"——只列出禁令主题与一句话摘要，**完整规则、反例清单、例外说明**全部下沉到下表「单点真理位置」指向的 phase 文件。本节与权威源不一致时，以权威源为准。

| 红线主题 | 一句话禁令（速查） | 单点真理位置 |
|---|---|---|
| 外层命中即停 | `OI*` / `oi-*` / `icon-*` / `img-*` / `lottie-*` 一旦在外层命中，立即作为整体处理，**禁止下钻**识别内部子节点；`img-*` 必须对**外层 node-id** 整层导出（`download_assets.export` 或 `get_screenshot`），**禁止用 get_design_context 子图 localhost / rawImages 拼装还原** | [phase-2-audit-and-codegen.md](phase-2-audit-and-codegen.md) §一 · 外层命中即停 |
| `icon-*` 落地路径 | 只允许两条：① `<OIIcon name="data-name 原值" />` 精确匹配（**禁止**语义裁剪如 `icon-location` → `location`）；② 图标库无匹配 → 占位块 + 在对话中显式提示用户。**任何切图 / 手写 SVG `<path>` / iconfont / CSS 自绘 / Vector 子节点拼装均视为违规** | [phase-2-audit-and-codegen.md](phase-2-audit-and-codegen.md) §一 · 图标识别补充 |
| `img-*` CDN 默认上传 | 仅 `data-name.startsWith('img-') === true` 节点进入 CDN 流程；默认 `cdn_compress_and_upload`，**上传失败才降级 `assets/`**。**严禁虚构「原型阶段不上 CDN / 生产化阶段才上 CDN / v1 本地 v2 CDN」等分阶段路径**；用户明确"暂不走 CDN"必须在 audit 第 1 节引用其原话 | [phase-2-audit-and-codegen.md](phase-2-audit-and-codegen.md) §七 · 图片识别 + `figma-img-cdn-skill` |
| 依赖 skill 强制加载 | 5 个 `requires` skill 必须**显式 Read** 入口文件后才允许进入 Step 1；audit 第 1.1 节 5 行不齐 / 关键产物列含占位（`vX.X.X` / `...`）即视为未完成 | 本文件 Step 0c + [phase-1-dependency-check.md](phase-1-dependency-check.md) §3d |
| `figma-audit.md` 字段表 | 第 1 节 / 第 1.1 节 / 第 2–7 节字段表的合法取值与字段语义 | [implementation-audit-template.md](implementation-audit-template.md) |
| 视觉验证 | 截图对比 + 关键节点 computed style 数值核对未完成前，禁止声明"还原完成"；环境无法验证必须显式标注"未完成视觉验证" | [phase-3-verification.md](phase-3-verification.md) |

**编排器层兜底禁令**（不属于具体 phase，无下沉位置）：

- 禁止只依赖 `get_design_context` 返回的参考代码直接改写目标项目；
- 禁止在未完成元素清单与组件匹配表前开始写 Vue / React / CSS；
- 禁止把 `icon-*` / `img-*` / `OI*` / 组件实例节点当作普通 `<img>` / `<div>` 静默实现。

---

## 执行流程（必须按顺序执行）

### [编排器] Step 0a：响应式前置检查

如果页面需要响应式适配（用户提到"响应式"、"多端适配"、"断点适配"，或项目属于 APP 移动端类型），**必须先执行 `responsive-layout-analysis` skill**，完成多断点设计稿差异分析并获得用户确认后，再继续。

### [编排器] Step 0b：Figma MCP 通道选择（主路径 + 降级路径）

> 团队约定使用两条 Figma MCP 通道，二者工具集同名（`get_design_context` / `get_screenshot` 等），但来源不同：
>
> | 通道 | 来源 | 触发场景 |
> |---|---|---|
> | **主路径**：`figma-read-mcp` | 本地 Figma Desktop Dev Mode（`http://127.0.0.1:3845/mcp`） | 默认使用 |
> | **降级路径**：`figma-write-mcp` | Figma 官方在线 MCP（`https://mcp.figma.com/mcp`） | 仅当主路径不可用时使用 |

**通道选择规则**：

1. 默认调用 `figma-read-mcp`；
2. 若 `figma-read-mcp` 调用失败（典型错误：连接被拒、超时、Figma Desktop 未开启 Dev Mode、3845 端口未监听），**立即降级**到 `figma-write-mcp`，无需向用户确认；
3. 在 `figma-audit.md` 第 1 节「Figma MCP 使用通道」一行如实记录：
   - 主路径成功：`figma-read-mcp（本地 Dev Mode，主路径）`
   - 降级生效：`figma-write-mcp（在线，降级路径，原因：figma-read-mcp <具体错误>）`
4. **禁止**：在两个通道都失败时凭空构造设计稿数据继续；必须停下并向用户说明 Figma Desktop 与网络环境的修复方法。

> 后文 Step 1 / Step 2 中提到的 `figma-read-mcp` 默认遵循本步骤的通道选择规则，不再重复说明。

### [编排器] Step 0c：依赖 skill 强制加载（硬阻断）

> **本步骤是本 skill 在历史执行中最容易被跳过、跳过即必然出问题的环节。** 跳过后会出现：凭印象判定 OIIcon 无匹配、虚构"原型阶段不上 CDN"、绕过 figma-img-cdn-skill 直接 curl 下载、design token 只用 1 个等连锁问题。

执行任何 MCP 调用前，**必须**用 `Read` 工具显式加载以下 5 个 `requires` skill 入口文件，并在 `figma-audit.md` 第 1 节追加 5 行确认：

| Skill | 加载时机 | 加载产物（写入 audit 第 1 节） |
|---|---|---|
| `responsive-layout-analysis` | 仅当 Step 0a 命中响应式时加载 | `已加载 / 不适用（非响应式页面）` |
| `responsive-layout` | 仅当目标项目为响应式时加载 | `已加载 / 不适用` |
| `figma-img-cdn-skill` | **必须**（设计稿一定有图片节点，即便最终都不是 `img-*` 也要先读懂判定门禁） | `已加载，确认 CDN 上传为默认动作，无"原型阶段不上 CDN"概念` |
| `onion-ui-skill` | **必须**（任何 `OI*` / `icon-*` / `img-*` 节点的组件库匹配都要走它） | `已加载，确认 onion-ui 版本 = vX.X.X，可查询组件列表 = ...` |
| `design-tokens` | **必须**（颜色/间距/字号/圆角等都要先尝试 token 命中） | `已加载，token 来源 = node_modules/.../tokens.css` |

**禁止跳过任何一项。** 即使本次"自认为不需要"，也必须 Read 一次入口文件确认其覆盖范围。Read 后若判定"本次不适用"，必须在 audit 第 1 节写明判断依据，**禁止"沉默地不读"**。

### [编排器] Step 1：获取设计稿信息

调用 `figma-read-mcp` 的 `get_design_context`，获取设计稿节点数据。失败时按 **Step 0b** 的通道选择规则降级到 `figma-write-mcp` 的同名工具，并将通道选择结果写入 `figma-audit.md` 第 1 节。

### [编排器] Step 2：获取设计稿截图

调用与 Step 1 相同通道的 `get_screenshot`，保存截图用于后续对比。

### [编排器] Step 3：依赖探查

**读取 [phase-1-dependency-check.md](phase-1-dependency-check.md)**，严格按四步完成：

- **Step 3a**：pnpm workspace 依赖探查（向上查 `pnpm-workspace.yaml` 并读 workspace root `package.json`）
- **Step 3b**：入口文件 import 探查（`src/main.ts` / 样式入口）
- **Step 3c**：CDN MCP 可用性确认（看 `.cursor/mcp.json` 与 mcps 目录，非 package.json）
- **Step 3d**：依赖 skill 加载断言（**硬阻断**，复核 Step 0c 的 5 个 Read 是否真发生、关键产物列无占位）

3a / 3b / 3c 结论写入 `figma-audit.md` 第 1 节；3d 校验失败时回到 Step 0c 补读。

> 本步骤是幻觉高发区：只看子包 `package.json` 必然误判「未接入 onion-ui」；Step 3d 跳过会让 Step 0c 的「依赖 skill 加载」沦为口头声明。phase-1 文件中有完整的防误规则。

### Step 4–8：审计记录 + 代码生成

**Read [phase-2-audit-and-codegen.md](phase-2-audit-and-codegen.md)**，然后按文件中"一～八"章节顺序执行：

输入：
- 编排器在 Step 1 已获得的 `get_design_context` 返回数据（直接复用上下文，无需重调）
- 编排器在 Step 2 已保存的 `get_screenshot` 截图
- `figma-audit.md` 第 1 节（项目上下文，由 Step 3 写入）

执行顺序：

4. **元素清单**：逐节点记录 `data-node-id` / `data-name` / 视觉角色 / 父子关系；严格执行"外层命中即停"——`img-*` / `icon-*` / `OI*` / `oi-*` / `lottie-*` 命中外层后不得展开内部 Vector / Group / Image 子节点
5. **组件匹配表**：按 onion-ui 优先级匹配，标注使用 onion-ui / 项目组件 / 原生实现的依据；`icon-*` 必须以 `data-name` 原值精确匹配 `OIIcon`（如 `icon-location` → `<OIIcon name="icon-location" />`），图标库无匹配时**只能降级为占位块并显式提示用户**，**严禁下载切图 / 手写 SVG `<path>` 还原**
6. **样式字段提取表**：七类字段（布局 / 文本 / 填充 / 描边 / 圆角 / effects / 透明度）逐项从 Figma 数据取值，禁止目测截图数值，禁止从子节点 x/y 反推 padding/gap；按需 Read [figma-fields-reference.md](references/figma-fields-reference.md) / [auto-layout-to-flex.md](references/auto-layout-to-flex.md) / [style-css-examples.md](references/style-css-examples.md) / [size-units.md](references/size-units.md)
7. **审计记录**：填充 `figma-audit.md` 第 2–6 节（按 [implementation-audit-template.md](implementation-audit-template.md) 的格式）；**Step 7 输出前禁止开始编辑任何代码文件**
8. **生成代码**（Vue 3 + SCSS，写入用户指定目标目录）；写入前严格按 phase-2 文件末尾的检查清单 B–G 逐项核对；如涉及 Lottie，按需 Read [lottie-setup.md](references/lottie-setup.md)

阻断点：根 Frame 宽度不是 750 时，必须先向用户确认缩放策略后再继续。

### Step 9：生成后验证

代码写入完成后，**Read [phase-3-verification.md](phase-3-verification.md)**，然后按其 Step 1–8 顺序完成三级验证：

- Step 1–2：复用 Step 2 已保存的设计稿截图；启动 dev server，通过 `cursor-ide-browser` MCP 打开页面
- Step 3：整页截图对比
- Step 4：**分模块截图对比（强制，不可跳过）**
- Step 5：**关键节点 computed style 数值核对（强制）**
- Step 6：差异表（节点 ID | 属性 | 设计值 | 实现值 | 差值 | 原因）
- Step 7：修正后重复 Step 3–5，直至差异表清空
- Step 8：同一差异修 ≥2 次仍无法对齐时，按 phase-3 的兜底话术向用户确认设计意图

阻断点：差异表未清空前禁止声明"还原完成"；清空后在 `figma-audit.md` 追加「验证结论」节。

---

## figma-audit.md 产物格式

`figma-audit.md` 是流程产物文档，按 Step 顺序累积写入：Step 0c / Step 3 写入第 1 节，Step 4–7 写入第 2–6 节，Step 9 追加第 7 节。

> **单点真理**：第 1 节 / 第 1.1 节 / 第 2–7 节的字段表以 [implementation-audit-template.md](implementation-audit-template.md) 为权威源。下方仅为编排器层快速预览第 1 节结构，**第 2–7 节填表细节、字段语义和「合法取值」请以 implementation-audit-template.md 为准**；本节若与权威源不一致，以权威源为准（同步漂移按 fix 处理）。

```markdown
# figma-audit.md

## 1. 目标与项目上下文（Step 0c + Step 3 写入）
| 项 | 结论 |
|---|---|
| Figma nodeId | `待填写` |
| 目标实现目录 | `待填写` |
| 技术栈 | `Vue / React / ...` |
| 样式体系 | `SCSS / CSS Modules / ...` |
| Onion UI 状态 | `已安装 vX.X.X / 未安装`（Step 3a） |
| Onion UI base-css 已 import | `是 / 否，需补充`（Step 3b） |
| design-tokens 已 import | `是 / 否，需补充`（Step 3b） |
| CDN MCP 可用 | `是 / 否`（Step 3c） |
| **CDN 例外** | `无 / 用户决定不上 CDN，原因：__`（Step 3 写入；默认必为「无」，写「用户决定」时必须有用户原话引用） |

### 1.1 依赖 skill 加载状态（Step 0c 写入，缺一行即视为未完成 Step 0c）

| Requires Skill | 已 Read | 适用性结论 / 关键产物 |
|---|---|---|
| `responsive-layout-analysis` | ☐ | `已加载 / 不适用（理由）` |
| `responsive-layout` | ☐ | `已加载 / 不适用（理由）` |
| `figma-img-cdn-skill` | ☐ | `已加载，CDN 上传为默认动作` |
| `onion-ui-skill` | ☐ | `已加载，onion-ui = vX.X.X，可查询组件 / 图标库` |
| `design-tokens` | ☐ | `已加载，token 文件 = ...` |

## 2. Frame 倍率（Step 4 写入）
## 3. 元素清单（Step 4 写入）
## 4. 组件匹配表（Step 5 写入）
## 5. 样式字段提取表（Step 6 写入）
## 6. 资源处理计划（Step 7 写入）
## 7. 验证结论（Step 9 写入）
```

---

## 编排器检查清单（全流程）

> 编排器在每个 Step 完成时勾选对应项。**逐项 checklist 已下沉到独立文件**，避免本入口文件被勾选项淹没：
>
> | 组 | 覆盖范围 | 文件位置 |
> |---|---|---|
> | A 组（前置 Step 0a–3） + H 组（阶段切换） | Step 0a 响应式 / Step 0b 通道 / Step 0c 强制加载 / Step 1–3 探查 + 跨 phase Read 确认 | [orchestrator-checklist.md](orchestrator-checklist.md) |
> | B–G 组（审计 + 代码生成 Step 4–8） | 组件 / 样式 / 布局 / 视觉属性 / 倍率 / 其他 | [phase-2-audit-and-codegen.md](phase-2-audit-and-codegen.md) 末尾 |
> | 验证组（Step 9） | 三级验证 / 差异表 / 兜底话术 | [phase-3-verification.md](phase-3-verification.md) 末尾 |
>
> **使用约定**：每个 Step 完成时复制对应组的清单到执行上下文逐项勾选；A 组任一项未勾选不得进入 Step 4，B–G 组任一项未勾选不得在 Step 8 写入代码。
