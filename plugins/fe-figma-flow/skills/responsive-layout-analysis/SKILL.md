---
name: responsive-layout-analysis
description: >-
  前端团队通用的响应式设计稿前置分析流程（代码生成之前）。收集多断点 Figma 设计稿，
  逐断点读取数据与截图，跨断点对比元素布局/尺寸/可见性变化，产出结构化差异报告，
  并按 `responsive-layout` 的 7 级断点顺序拆解为有序开发 task；确认后交由 `figma-read-skill`
  逐断点生成代码。
  触发条件（满足任意一条）：
  (1) 需求 / task / 对话中出现"响应式适配"、"pad 适配"、"平板适配"、"iPad 适配"、
      "折叠屏适配"、"横屏适配"、"多端适配"、"多尺寸适配"、"大屏适配"，且涉及 Figma 设计稿；
  (2) 用户提供 ≥2 个不同尺寸/命名（手机竖屏 / 平板竖屏 / 平板横屏 / 手机横屏 / 折叠屏）的
      Figma Frame 链接或 node-id；
  (3) 用户提供 1 个 Figma 链接，但明确说明该页面需要上面 (1) 中的任一适配；
  (4) 用户明确要求"分析多断点设计稿"、"对比断点差异"、"拆解响应式 task"、
      "先分析再生成代码"、"响应式开发前置分析"。
  不触发：
  - 只有单一 Figma 设计稿且用户未提任何适配需求 → 直接用 `figma-read-skill`；
  - 已进入 CSS 编写阶段、只需查断点写法 → 用 `responsive-layout`；
  - 纯讨论响应式方案、不涉及具体 Figma 设计稿；
  - 仅实现当前尺寸、用户已声明"不需要响应式"。
requires:
  - figma-read-skill   # 分析完成后，由本 skill 交棒给 figma-read-skill 逐断点生成代码
  - responsive-layout  # 引用其中的 7 级断点体系与设计稿对应断点表
mcp:
  - figma-read-mcp   # 【主路径】本地 Figma Desktop Dev Mode（127.0.0.1:3845）。get_design_context / get_screenshot
  - figma-write-mcp  # 【降级路径】Figma 官方在线 MCP（mcp.figma.com）。主路径不可用时通过同名工具读取断点设计稿
---

# 响应式设计稿分析 · 前置工作流

> **前置依赖**：本 skill 引用 `responsive-layout` 中的断点体系和设计稿对应表。执行前先读取该 skill。

本 skill 是 `figma-read-skill` 的前置阶段，必须在代码生成前完成。流程：本 skill（分析）→ 用户确认 → `figma-read-skill`（逐断点生成代码）+ `responsive-layout`（CSS 断点规则）。

---

## 交互规则

本 skill 包含多个需要用户确认的节点。遵循以下原则：

- **结构化选择**：使用 `AskQuestion` 工具，agent 会自动暂停等待用户选择
- **需要用户输入内容**（如粘贴链接、说明修改点）：输出提示文字后**必须结束当前 turn**，不要调用任何工具，等待用户在下一条消息中回复
- **禁止跳过确认**：阶段 1→2、阶段 3→4 之间的确认节点不可跳过

---

## 执行流程（4 阶段，必须按顺序执行）

### 阶段 1：检测与收集设计稿

#### Step 1.1：识别当前设计稿断点

调用 `figma-read-mcp` 的 `get_design_context` 获取用户提供的 Figma 节点数据（**若 `figma-read-mcp` 不可用，立即降级到 `figma-write-mcp` 的同名工具，并在分析报告里注明使用通道**），读取 Frame 尺寸（width × height），按 `responsive-layout` skill 中的**"设计稿对应断点"**表（设计稿尺寸为 2x，代码尺寸 ÷2）映射到对应断点。4 套必出设计稿：750×1334（默认）、1280×2048（≥640 平板）、2048×1280（≥1024 横屏）、1334×750（手机横屏）。

#### Step 1.2：自动扫描同文件其他断点

使用 `get_metadata` 读取当前 Frame 的父级页面（Page），扫描同级别的其他 Frame，通过以下方式自动发现其他断点设计稿：

**按尺寸匹配**：其他 Frame 的尺寸是否符合设计稿对应断点表中的某个断点

**按命名匹配**：Frame 名称是否包含以下关键词：
- 手机 / iPhone / mobile / phone / 竖屏 / portrait
- 平板 / pad / tablet / iPad / MatePad
- 横屏 / landscape / horizontal
- 折叠 / fold / foldable

#### Step 1.3：判断缺失断点并提示用户

根据检测结果分场景处理：

**场景 A — 自动找到全部必出设计稿（4 套）**：

向用户展示检测结果，使用 `AskQuestion` 工具确认：

```
AskQuestion:
  prompt: |
    在当前 Figma 文件中检测到完整的响应式设计稿：
      ✅ 默认 375    — Frame "首页-手机" (750×1334)
      ✅ ≥640 平板   — Frame "首页-Pad" (1280×2048)
      ✅ ≥1024 横屏  — Frame "首页-Pad横屏" (2048×1280)
      ✅ 手机横屏    — Frame "首页-手机横屏" (1334×750)
    是否开始跨断点差异分析？
  options:
    - id: "confirm"
      label: "确认，开始分析"
    - id: "adjust"
      label: "需要调整（补充/移除断点）"
```

用户确认后进入阶段 2。若选择"调整"，按用户补充的信息更新设计稿列表。

**场景 B — 找到部分设计稿**：

列出已找到和缺失的设计稿，使用 `AskQuestion` 工具让用户选择处理方式：

```
AskQuestion:
  prompt: |
    检测到当前设计稿为手机竖屏 (750×1334)。
    在文件中还找到了平板竖屏设计 (1280×2048)，但以下必出设计稿缺失：
      ✅ 默认 375          — 已提供
      ✅ ≥640 平板竖屏     — 已在文件中找到: Frame "首页-Pad"
      ❌ ≥1024 平板横屏    — 缺失
      ❌ 手机横屏          — 缺失
  options:
    - id: "provide"
      label: "我来提供缺失断点的 Figma 链接"
    - id: "skip"
      label: "缺失断点暂不适配，先分析已有的"
    - id: "cancel"
      label: "暂停，等设计稿补齐后再分析"
```

若用户选择"提供链接"，输出文字提示用户粘贴链接，**然后结束当前 turn 等待用户回复**。收到链接后继续。

**场景 C — 仅有单个设计稿，无法自动发现其他断点**：

使用 `AskQuestion` 工具询问是否需要响应式适配：

```
AskQuestion:
  prompt: "当前设计稿尺寸为 750×1334（手机竖屏）。该页面是否需要响应式布局适配？"
  options:
    - id: "yes"
      label: "是，需要响应式适配（我来提供其他断点设计稿）"
    - id: "partial"
      label: "是，但部分断点暂无设计稿（先分析已有的）"
    - id: "no"
      label: "否，仅实现当前尺寸"
```

- 用户选"yes" → 输出以下提示文字，**然后结束当前 turn 等待用户粘贴链接**：

> 请提供以下必出设计稿的 Figma Frame 链接（右键 Frame → "Copy link"）：
> 1. 平板竖屏 1280×2048
> 2. 平板横屏 2048×1280
> 3. 手机横屏 1334×750
>
> 如有可选断点（768 iPad / 折叠屏）也请一并提供。

- 用户选"partial" → 进入 Step 1.4 降级流程
- 用户选"no" → 跳过本 skill，直接使用 `figma-read-skill` 生成代码

**场景 D — 用户明确提到响应式但只给了一个链接**：

直接进入场景 C 的"yes"分支，请求补充设计稿。

#### Step 1.4：灵活降级

如果用户无法提供全部设计稿（如设计师尚未完成），仍可继续：

- 仅分析已提供的断点
- 缺失断点在报告中标注为 **"⚠️ 待设计，暂按默认样式处理"**
- 给出基于已有断点变化趋势的**建议性方案**（明确标注为推测）
- 支持后续补充设计稿时增量更新分析报告

---

### 阶段 2：逐断点读取与数据采集

对每个已收集的断点设计稿，执行以下操作：

#### Step 2.1：获取结构化数据

对每个断点的设计稿 Frame，调用 `get_design_context` 获取完整节点树，记录每个元素的：
- `data-name`（用于跨断点元素匹配的唯一标识）
- 位置：`x`, `y`, `width`, `height`
- 布局属性：`layoutMode`（flex/grid）, `gap`, `padding`, `constraints`
- 样式属性：`fontSize`, `fontWeight`, `lineHeight`, `borderRadius`, `fills`, `opacity`
- 可见性：`visible`, 是否存在于该断点

#### Step 2.2：获取截图

对每个断点调用 `get_screenshot`，保存截图用于后续视觉对比。

#### Step 2.3：建立元素映射表

以 `data-name` 为主键，建立跨断点的元素映射。同一个元素在不同断点可能：
- 名称完全相同 → 直接匹配
- 名称相似（如 `search` vs `search-mini`）→ 语义匹配
- 仅存在于部分断点 → 标记为条件显隐

---

### 阶段 3：跨断点差异分析

#### Step 3.1：逐元素对比

对映射表中的每个元素，对比所有断点的数据，分析以下维度：

**布局结构变化**：
- flex-direction 是否改变（如 row → column）
- grid 列数是否变化（如 2列 → 3列）
- 定位方式是否变化（如 relative → absolute → fixed）
- 容器嵌套结构是否变化

**尺寸变化**：
- width / height 在各断点的具体值
- 是固定值还是自适应（flex-grow / 百分比）
- padding / margin / gap 的变化
- border-radius 的变化

**字体变化**：
- font-size / line-height / font-weight 在各断点的值

**可见性变化**：
- 元素在某些断点存在、某些断点不存在 → `display: none` 或条件渲染
- 元素形态变化（如搜索框 → 搜索图标按钮）

**图片/资源变化**：
- 图片尺寸是否变化
- 是否使用不同的图片资源

#### Step 3.2：截图视觉对比

将各断点截图并排对比，验证数据分析的准确性：
- 数据对比结论是否与视觉表现一致
- 是否有数据未覆盖的视觉变化（如背景色、阴影等）
- 确认元素对应关系是否正确

#### Step 3.3：产出分析报告

严格按照 [analysis-report-template.md](analysis-report-template.md) 模板产出结构化报告。输出报告后，使用 `AskQuestion` 工具请求确认：

```
AskQuestion:
  prompt: "以上是跨断点差异分析报告，请确认是否准确。"
  options:
    - id: "confirm"
      label: "确认，进入 task 拆解"
    - id: "revise"
      label: "有问题，需要修改（我会说明）"
```

用户选"revise"时，**结束当前 turn 等待用户说明修改点**，修正后重新确认。

---

### 阶段 4：task 拆解与开发计划

用户确认分析报告后，拆解为有序的开发 task：

#### Task 拆解规则

按 `responsive-layout` skill 的 7 级断点顺序，每个断点对应一个 Task。CSS 写法遵循该 skill 的断点体系规范。

| Task | 对应断点 | 要点 |
|------|---------|------|
| 1 | 默认（375 基准） | 调用 `figma-read-skill` 生成基础代码，固定 px，`@mixin default` 包裹 |
| 2 | 小屏缩放（< 375px） | 复用 `@include default`，postcss 自动转 vw |
| 3 | pad 尺寸放大（≥640×640） | 仅调尺寸（字号、间距、圆角），不调布局 |
| 4 | 布局调整（≥640 宽） | flex/grid 结构变化、元素显隐 |
| 5 | 布局调整（≥768 宽） | 如有设计稿，增量添加差异 |
| 6 | pad 横屏（≥1024 宽） | 宽屏布局策略（固定宽度、多列） |
| 7 | 手机横屏（height < 640） | 必须放最后，处理横屏收缩/隐藏 |
| 8 | 验证 | 各断点截图对比设计稿 |

#### 输出格式

输出 task 列表后，使用 `AskQuestion` 工具请求确认：

```
AskQuestion:
  prompt: "以上是响应式开发 task 列表，确认后将按顺序逐个执行。"
  options:
    - id: "confirm"
      label: "确认，开始执行"
    - id: "adjust"
      label: "需要调整 task 内容/顺序"
```

确认后使用 `TodoWrite` 工具记录 task 进度，逐个执行，每完成一个标记完成。

---

## 注意事项

### 尺寸转换

设计稿为 2x 尺寸，分析报告中的属性值必须转换为 1x（÷2）后再记录。

### 断点顺序

分析报告和 task 拆解必须遵循 `responsive-layout` skill 中定义的 7 级断点顺序，不可打乱。

### 禁止跳过分析

当检测到页面需要响应式适配时，**禁止跳过本分析流程直接生成代码**。跳过分析是导致断点样式遗漏、布局错乱的主要原因。

### 增量更新

如果用户后续补充了新的断点设计稿，支持增量更新：
- 仅需对新断点执行阶段 2 的数据采集
- 在现有分析报告中补充新断点的列
- 更新 task 列表，添加新断点的实现 task

## 参考文档

- [分析报告模板](analysis-report-template.md) — 结构化报告的完整模板和填写说明
- `responsive-layout` skill — CSS 断点体系、安全边距变量、设计稿对应关系
- `figma-read-skill` — Figma 设计稿转代码的核心工作流
