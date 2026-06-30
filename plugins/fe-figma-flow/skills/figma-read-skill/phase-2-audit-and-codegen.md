# 审计记录 + 代码生成 · 详细规则

> **何时阅读**：编排器在执行 Step 4 前 Read 本文件。包含组件识别、样式数据提取、布局分析、设计元素属性、尺寸单位、字体识别、图片识别、动效识别全部规则，以及生成代码前的检查清单（B–G 组）。
>
> **本文件是以下规则的权威源**（SKILL.md 硬阻断段为编排器层速查，本文件如与 SKILL.md 不一致以本文件为准）：
> - 外层命中即停（`OI*` / `icon-*` / `img-*` / `lottie-*` 不下钻） → 见「一、组件识别 · 外层命中即停」
> - `icon-*` 两条落地路径 + 禁止降级清单 → 见「一、组件识别 · 图标识别补充」
> - `img-*` CDN 默认上传 + 失败降级 `assets/` → 见「七、图片识别」
>
> **强前置**：开始本文件任何动作前，必须确认 SKILL.md 的 Step 0c 已经完成（`figma-img-cdn-skill` / `onion-ui-skill` / `design-tokens` 的入口文件已被显式 Read，audit 第 1.1 节已填）。本文件下方任何"按 onion-ui 优先级匹配"、"走 figma-img-cdn-skill 上传"等指令的语义，**完全依赖那 3 个 skill 的内容已经在编排器上下文中**。如果发现 Step 0c 没真正完成，立即停止本文件的执行，回到 SKILL.md Step 0c 补读。
>
> **输入**：编排器上下文中已有的 `get_design_context` 数据 + `get_screenshot` 截图 + `figma-audit.md` 第 1 节（项目上下文，由 Step 3 写入）。
> **输出**：补全 `figma-audit.md` 第 2–6 节 + 写入目标 Vue / SCSS 代码文件。

---

## 核心原则

- **Figma MCP 返回的 React + Tailwind 代码只是参考数据，不是可直接改写的实现方案。**
- 生成业务代码前，必须先完成元素清单（Step 4）→ 组件匹配表（Step 5）→ 样式字段提取表（Step 6）→ 审计记录输出（Step 7），**缺任一项不得开始编辑文件**。

---

## 一、组件识别（强制要求）

> 必须优先使用 onion-ui 组件库中的组件，禁止使用原生 HTML 元素实现已有组件的功能。

### 识别 Figma 组件实例

Figma MCP 返回的节点 ID 格式可以判断元素是否为**组件实例（Component Instance）**：

| ID 格式 | 含义 | 示例 |
|---------|------|------|
| `数字:数字` | 普通图层节点 | `10:45` |
| `I父ID;原始ID` | 组件实例的**内部子节点**（`I` 前缀 + `;` 分隔） | `I43:384;65:6890` |

**判断规则**：当一个节点的**子节点 ID** 带有 `I` 前缀和 `;` 分隔符时，说明该父节点是一个 **Figma 组件实例**。

```
圆形按钮 (43:384)              ← 组件实例（因为子节点带 I 前缀）
  └── 登录 (I43:384;65:6890)   ← 组件内部节点（I + 分号 = 实例子节点）
```

### 外层命中即停（强制规则）

**前置规则**：以下五类节点一旦在外层命中，立即作为整体处理，**禁止下钻识别其内部子节点**：

| 命中条件（`data-name`） | 整体处理方式 | 子节点处理 |
|---|---|---|
| 以 `OI` / `oi-` 开头 | 视为组件实例，匹配 onion-ui 组件 | 子节点不进入元素清单 / 组件匹配表 / 样式提取表 |
| 以 `icon-` 开头 | 视为图标。匹配规则：① `OIIcon` 的 `name` = `data-name` **原值精确匹配**（图层命名本身就是图标名，不做语义提取）；② 图标库无匹配时**只能**用占位块 + 显式提示用户，**不允许任何降级**（不下载切图、不手写 SVG、不 iconfont、不 CSS 自绘） | 内部 Vector / Path / Group **一律忽略** |
| 以 `img-bg-` 开头 | 视为背景切图，CSS `background` | 内部子节点 **一律忽略** |
| 以 `img-` 开头（不含 `img-bg-`） | 视为内容切图，`OIImgLoad` / `<img>` | 内部子节点 **一律忽略** |
| 以 `lottie-` 开头 | 视为 Lottie 动效 | 内部子节点 **一律忽略** |

**为什么强制停下钻**：

- 切图 / 图标 / 组件实例的内部 Vector / Group / Clip / Image 是**矢量构造细节**，对前端实现没有价值。把它们各自识别出来会导致：
  - 把一张完整图标拆成"圆形底盘 + 三条线"分别做绝对定位、各自上传 CDN，结果与设计稿对不齐；
  - 漏掉外层 `data-name` 带的语义信息（如 `icon-location`），导致 `OIIcon` 精确匹配失败，最终错误降级为手写 SVG / 切图。
- 外层命中后，元素清单里只记录这一行；其内部节点写一行汇总即可（如 `内部 3 个 Vector → 已并入外层 icon-* 整体处理`），但**不得**为它们各自再开行记录尺寸、颜色、绝对定位。

**例外**：只有当外层节点不带这些前缀（普通 Frame / Group），但其子节点中存在 `icon-*` / `img-*` / `OI*` 时，才向下识别这些子节点；此时新一层的"外层命中即停"规则继续生效。

### 执行步骤

1. **必须先读取 `onion-ui-skill`**：按其流程确认当前项目 `@guanghe-pub/onion-ui` 版本，了解可用组件列表；

2. **识别 Figma 组件实例并与组件库匹配**，按以下优先级：

   **优先级 1：`data-name` 以 `OI` / `oi` 开头** → 直接找到对应名称的组件库组件
   - 示例：`oi-button` → `OIButton`，`oi-radio-unchecked` → `OIRadio`

   **优先级 2：`data-name` 匹配已知前缀模式**
   - `oi-radio-*` / `radio-*` → `OIRadio`（圆形单选框）
   - `oi-checkbox-*` / `checkbox-*` → `OICheckbox`（方形复选框）
   - `btn-*` / `button-*` → `OIButton`
   - `icon-*` → `OIIcon`，**`name` 取 `data-name` 原值精确匹配**（图层命名本身就是图标名/搜索关键字，禁止语义裁剪。例：`icon-location` → `name="icon-location"`，不是 `name="location"`）；图标库无匹配时**只能**用占位块 + 显式提示用户，**不允许任何降级**（详见下方"图标识别补充"）
   - `img-xxx`（不含 `img-bg-`）→ `OIImgLoad`，不可用时才降级为 `<img>`
   - `img-bg-xxx` → CSS `background` 属性，不作为组件识别
   - **注意区分 Radio（圆形）与 Checkbox（方形）**

   **图标识别补充（`icon-*` 强制路径）**：

   > **强前置**：进入 `icon-*` 决策前必须已 Read `onion-ui-skill`。判定"OIIcon 无匹配"必须有"已查询 onion-ui 图标库"的具体证据（查询的图标名 = `data-name` 原值 + 检索结果），**禁止凭印象/凭经验/凭 data-name 含义就声明"无匹配"**。

   **核心规则（只有两条）**：

   #### 规则 ①：精确匹配 = `data-name` 原值

   > **图层命名本身就是图标名，也是图标库的搜索关键字。直接用 `data-name` 原值去 onion-ui 图标库精确查询即可，禁止任何形式的语义提取/裁剪/翻译/猜测。**

   ```vue
   <!-- ✅ 正确：data-name 原值即查询关键字 -->
   <OIIcon name="icon-location" />        <!-- data-name="icon-location" -->
   <OIIcon name="icon-arrow-right" />     <!-- data-name="icon-arrow-right" -->
   <OIIcon name="icon-close-circle" />    <!-- data-name="icon-close-circle" -->

   <!-- ❌ 错误：禁止做任何形式的语义提取/裁剪 -->
   <OIIcon name="location" />             <!-- 把 "icon-location" 裁成 "location" -->
   <OIIcon name="arrow" />                <!-- 把 "icon-arrow-right" 裁成 "arrow" -->
   <OIIcon name="close" />                <!-- 把 "icon-close-circle" 裁成 "close" -->
   ```

   - 查询动作：用 `data-name` 原值（含 `icon-` 前缀）去 onion-ui 图标库精确匹配，**命中即用，不命中即走规则 ②**；
   - 查询动作 + 结果必须写入 audit 第 4 节"匹配依据"列；
   - 尺寸 / 颜色仍按 Figma 字段 + design token 设置，不内联 size 数字。

   #### 规则 ②：图标库无匹配 → **不允许降级，只能占位块 + 用户提示**

   > **凡是规则 ① 没命中的，唯一正确动作是占位块 + 显式提示用户。任何形式的"降级实现"（切图、SVG、iconfont、CSS 自绘）都是错的，一律视为违规。**

   占位块实现（Vue/SCSS）：

   ```vue
   <span class="icon-placeholder">[icon-location]</span>
   ```

   ```scss
   .icon-placeholder {
     display: inline-flex; align-items: center; justify-content: center;
     width: 24px; height: 24px;
     border: 1px dashed var(--color-border-secondary, #ccc);
     color: var(--color-text-secondary, #999);
     font-size: 10px; line-height: 1;
   }
   ```

   - 占位块尺寸按 Figma 字段 ÷2 换算，文字标注缺失的图标名（即 `data-name` 原值）；
   - **必须在对话中向用户显式输出**（写在 audit 里不算）：

     ```
     ⚠️ onion-ui 图标库中不存在图标 `icon-xxx`，已用占位块代替，请补充图标资源后替换。
     ```

   - audit 第 4 节"匹配依据"列必须写：`onion-ui 图标库无 "icon-xxx"，已用占位块 + 用户提示`。

   #### 严禁的"降级"路径（一律视为违规，必须返工）

   图标库无匹配时**唯一**正确动作是规则 ②（占位块 + 用户提示）。以下所有"降级实现"全部禁止：

   | 错误降级路径 | 为什么禁止 |
   |---|---|
   | 下载 Figma 切图（SVG/PNG）放入 `assets/` 或上传 CDN | icon 切图降级路径已彻底禁用，无论本地或 CDN |
   | 复制 / 改写 / 简化 Figma MCP 返回的 SVG 字符串 | 等同于自绘 SVG |
   | 模板内内联 `<svg><path d="…"/></svg>` | 等同于自绘 SVG |
   | `<i class="iconfont">` / 字体图标自定义 | 不在 onion-ui 图标库就是无匹配 |
   | CSS `border` / `clip-path` / `mask` 自绘图标形状 | 自绘等于无匹配 |
   | 拆成多个 Vector 子节点分别绝对定位再拼装 | 违反"外层命中即停" |
   | picsum / 调试占位图临时替换 | 临时方案易遗留到线上 |
   | 凭语义关键字猜图标名（如把 `icon-location` 猜成 `location` 再匹配） | 违反规则 ① 的精确匹配 |
   | 图标库无匹配时静默使用占位块，不在对话中显式提示用户 | 违反规则 ② 的"显式提示"要求 |

   **图片组件识别补充**：`img-`（非 `img-bg-`）开头节点必须优先 `OIImgLoad`，需先查询 `OIImgLoad` 是否存在及用法；宽高、`object-fit` 等样式通过 class 设置，尺寸按 2x 规则换算。

   **优先级 3：子节点 ID 带 `I` 前缀但名称未命中上述规则** → 与 onion-ui 组件库文档进行语义匹配：
   - 对比组件的中文/英文名称、外观描述与组件库功能
   - 组件库中存在功能匹配项（即使名称不同）→ 优先使用
   - 组件库确实无匹配 → 才使用原生 HTML 实现，并写明原因

3. **使用组件库组件**：不可私自调整组件样式，只能调整相对位置等布局信息。

---

## 二、样式数据完整提取（强制要求）

> 生成代码前必须从 `get_design_context` 返回的节点数据中把七类字段逐项取出并记录；禁止凭截图目测数值，禁止从子节点坐标反推 Auto Layout 间距。这是间距/属性/布局还原度低的首要原因。

### 七类必提取字段一览

| 类别 | 关键字段 | 去哪里查详细映射 |
|---|---|---|
| 布局 | `layoutMode` / `itemSpacing` / `padding*` / `primaryAxisAlignItems` / `counterAxisAlignItems` / `layoutGrow` / `width` / `height` | [references/figma-fields-reference.md](references/figma-fields-reference.md) + [references/auto-layout-to-flex.md](references/auto-layout-to-flex.md) |
| 文本 | `fontSize` / `fontWeight` / `lineHeight` / `letterSpacing` / `textAlignHorizontal/Vertical` / `textCase` / `textDecoration` | [references/figma-fields-reference.md](references/figma-fields-reference.md) |
| 填充 | `fills`（SOLID / GRADIENT_LINEAR / GRADIENT_RADIAL / IMAGE，数组按顺序叠加） | [references/figma-fields-reference.md](references/figma-fields-reference.md) + [references/style-css-examples.md](references/style-css-examples.md) |
| 描边 | `strokes` / `strokeWeight` / `strokeAlign` / `dashPattern` | [references/style-css-examples.md](references/style-css-examples.md) |
| 圆角 | `cornerRadius` / `rectangleCornerRadii` | [references/style-css-examples.md](references/style-css-examples.md) |
| 效果 | `effects`（DROP_SHADOW / INNER_SHADOW / LAYER_BLUR / BACKGROUND_BLUR） | [references/style-css-examples.md](references/style-css-examples.md) |
| 透明度 / 混合 | `opacity` / `blendMode` / `visible` | [references/figma-fields-reference.md](references/figma-fields-reference.md) |

### 提取铁律

1. **Auto Layout 容器的 `padding` 与 `gap` 必须直接取 Figma 字段**，严禁从子节点 x/y 反推或目测截图；
2. 节点有 Auto Layout（`layoutMode != NONE`）时，**默认映射为 flex 布局**，不允许退化为整页绝对定位；
3. 所有数值必须按「五、尺寸单位」的 ÷2 规则换算后再写入代码；
4. 所有颜色、间距、字号、圆角、阴影值必须优先匹配 `design-tokens` 里的 token，命中即用 token，未命中才写原始值；
5. 多层 `fills` / `strokes` / `effects` 必须按数组顺序完整还原，不能只取第一项。

---

## 三、布局分析（强制要求）

> 读取 Figma 设计稿时，必须主动分析页面布局方式、模块层级关系与跨断点响应式规则，先分析再实现，禁止跳过结构分析直接写代码。

- 以手机端 `375x667` 为基准代码视口（对应 2x 设计稿 `750x1334`）；
- 如果页面需要响应式适配，必须先执行 `responsive-layout-analysis`，完成多断点差异分析后再进入代码实现；
- **Auto Layout → Flex 的完整映射速查表见 [references/auto-layout-to-flex.md](references/auto-layout-to-flex.md)**。

### Step 1：主动识别页面模块结构

读取 Figma 节点树时，先从整体拆分模块，再分析模块内元素关系，至少识别：

- 页面层：page / frame / section 的整体结构
- 模块层：banner、表单区、卡片区、列表区、底部操作区等
- 容器层：模块内的包裹容器、卡片容器、分组容器、滚动容器
- 元素层：标题、正文、按钮、图片、角标、装饰元素等

必须明确：谁是父容器 / 谁是兄弟节点、哪些元素属于同一功能模块、模块间是堆叠 / 并列 / 覆盖。

### Step 2：识别布局方式

> 强约束：Auto Layout 容器的 `padding` / `gap` / 对齐方式，必须直接取 `get_design_context` 返回字段；禁止从子节点 x/y 反推；节点有 Auto Layout 时必须映射为 flex，不允许默认退化为绝对定位。

**固定宽度 vs 自适应宽度**：

- 自适应宽度：`left + width + right ≈ 页面宽度` → 用左右边距实现

  ```scss
  // 错误
  .card { left: 21px; width: 332px; }
  // 正确
  .card { left: 21px; right: 21px; }
  ```

**定位策略**：

- 节点带 Auto Layout（`layoutMode != NONE`）→ **必须用 Flex 布局**，按 [references/auto-layout-to-flex.md](references/auto-layout-to-flex.md) 逐字段映射
- 规则二维排布、多列卡片、多宫格 → 优先 **Grid 布局**
- 装饰浮层、角标、遮罩、背景叠层、跨模块覆盖 → 才使用 **绝对定位**
- 不要因为元素在 Figma 中有坐标就默认写绝对定位

### Step 3：识别层级与覆盖关系

> Figma 数据中元素的出现顺序代表绘制顺序，不要根据视觉位置推断层级。

- 先出现的在下层（z-index 较小），后出现的在上层（z-index 较大）
- 示例：Figma 顺序 `角色图片 → 白色卡片`，则角色在卡片**下方**（先绘制）

### Step 4：多断点响应式规则提炼

如果页面需要响应式适配，结合 `responsive-layout-analysis` 主动对比多断点设计稿，分析：

- 模块是否从单列变双列、纵向变横向
- 模块顺序、重组、拆分、合并
- 元素在不同断点是否显隐切换
- 容器宽度、间距、字号、圆角、图片尺寸是否随断点变化

### Step 5：代码实现采用响应式布局方案

遵循 `responsive-layout` 的断点体系：先实现 375 基准 → `max-width: 374px` 用 vw 等比缩放 → `min-width: 640 / 768 / 1024px` 按分析结果增量调整 → 手机横屏（`max-height: 639px` 且横屏）最后覆盖。

---

## 四、设计元素属性

所有颜色、间距、尺寸、圆角、阴影等属性必须使用 design token，禁止硬编码色值或 px 数字。详见 `design-tokens` skill。

快速接入（如项目尚未接入）：

```bash
pnpm add @guanghe-pub/design-tokens
```

```css
@import '@guanghe-pub/design-tokens/lib/tokens.css';
```

- 查阅可用 token：`node_modules/@guanghe-pub/design-tokens/lib/tokens.css`
- token 中确实不存在的属性，才允许硬编码
- **描边 / 圆角 / 阴影 / 毛玻璃 / 渐变等 CSS 写法示例** → [references/style-css-examples.md](references/style-css-examples.md)

---

## 五、尺寸单位（强制规则）

> 团队硬约定：Figma 设计稿统一为 2x 尺寸（根 frame 宽度为 750）。代码中所有尺寸、间距、字号、圆角、阴影偏移 / 模糊半径都必须缩小一倍（÷2）后再写入。

常用换算速查：

- `width / height / padding* / itemSpacing / fontSize / cornerRadius / effects.*` → **÷ 2**
- `lineHeight: "150%"`（百分比）→ **保留比例**，写为 `line-height: 1.5`
- `opacity / fontWeight / 颜色值` → **不换算**
- 1px 视觉细线（分割线等）→ 保持 1px，不机械折半

**根 frame 宽度不是 750 时，必须先向用户确认缩放策略，不得自行选择。**

> 完整换算对照表、非整数像素处理、字号下限校验等详见 [references/size-units.md](references/size-units.md)。

---

## 六、字体识别

在入口文件中导入组件库基础样式（已包含阿里普惠字体，无需额外定义字体）：

1. 确保项目已安装 `@guanghe-pub/onion-ui`
2. 在 `main.ts` 或入口文件中导入：
   ```typescript
   import '@guanghe-pub/onion-ui/lib/base-css.css'
   ```

---

## 七、图片识别（强制要求）

> **强前置**：进入本节任何决策前必须已 Read `figma-img-cdn-skill` 入口文件。本节是该 skill 在 figma-read-skill 主流程中的引用点，不读 figma-img-cdn-skill 就执行本节，会出现"凭印象编出原型/生产分阶段路径"等历史故障。
>
> **明令禁止**：禁止虚构以下任何分阶段说法——"原型阶段不上 CDN"、"生产化阶段才上 CDN"、"v1 用本地 v2 上 CDN"、"DEMO 阶段降级到 assets"、"先本地后续再迁 CDN"。`figma-img-cdn-skill` 与本 skill 中均无任何"按阶段切换 CDN"概念。`img-*` 节点的默认动作是 `cdn_compress_and_upload` 上传 CDN，仅在上传失败时才降级到 `assets/`。如用户明确要求"暂不走 CDN"，必须在 audit 第 1 节「CDN 例外」一行引用用户原话，否则视为违规。

> `data-name` 精确以小写 `img-` 开头的图层，才进入本章节的图片识别、CDN 上传和命名规则处理流程。

| 命名模式 | 含义 | 实现方式 |
| --- | --- | --- |
| `img-bg-xxx` | 背景图 | CSS `background` 属性 |
| `img-xxx`（不含 `bg-`） | 内容图片 | 优先 `OIImgLoad`，降级为 `<img>` |
| `img-https://...` | 名称中直接包含链接 | 提取链接直接使用，跳过 CDN 上传 |

识别规则：

1. 只筛选 `data-name.startsWith('img-') === true` 的元素进入本章节流程；
2. 非 `img-` 前缀节点**禁止**执行 CDN 上传、生成 CDN URL；
3. **`img-` 图层一旦在外层命中，立即停止下钻**（与第一节"外层命中即停"一致）：内部子元素不再单独做图片识别 / 元素清单 / 组件匹配 / 样式提取 / 资源下载；
   - 反例：`img-menu` 命中后，又把内部 `circle bg`、`Menu-outline` 容器、三条 `Vector` 各自作为独立图层处理 → ❌ 违反规则；
   - 反例：从 `get_design_context` 代码常量或 `download_assets.rawImages` 取子图 URL 映射到 `img-*` 图层 → ❌ 违反规则；
   - 正例：`img-menu` 命中后，对**该外层 node-id** 整层导出一张图，单一节点一个 URL → ✅ 正确；
4. 每个命中的 `img-` 节点，记录 `data-name`、`node-id`、元素尺寸、位置信息（外层一行即可，不展开内部）。

**一个 `img-` 图层 = 一张整层导出图 = 一个 URL**（单图与蒙版/多图合成图层均适用）。

非 `img-` 图片处理边界：

- `bg-banner`、`banner-image`、`pic-avatar`、`photo`、`IMAGE` 等名称不进入 CDN 上传流程；
- Figma MCP 返回了 `localhost` 资源地址，但节点名称不是 `img-` 开头时，不上传 CDN；如页面还原必须使用，可临时保存到项目 `assets` 目录并本地引用。

资源获取与上传：对通过准入门禁的 `img-` 节点，**禁止**使用 `get_design_context` 内子图 `localhost` 常量；必须对该 `img-` 图层的 `node-id` **整层导出**后再上传 CDN：

- **优先**：`figma-write-mcp` 的 `download_assets` → 仅用 **`export.url`**（忽略 `rawImages`）下载到临时目录；
- **备选**：`figma-read-mcp` 的 `get_screenshot(nodeId)` 保存整层截图；
- 再通过 `@guanghe-pub/yc-cdn-mcp-server` 的 `cdn_compress_and_upload` / `cdn_batch_compress_and_upload` 上传；成功后删除临时文件，失败则降级 `assets/`。

> **再次强调**：上传 CDN 是默认动作，与"原型 / 生产 / 阶段"无关。用子图层 localhost / rawImages 替代整层导出是历史故障路径，本次必须避免。

> 完整图片处理流程详见 `figma-img-cdn-skill`。

---

## 八、动效识别

当 `data-name` 以 `lottie-` 开头时处理 Lottie 动效（链接格式和代码模板详见 [references/lottie-setup.md](references/lottie-setup.md)）：

1. **查询项目中 lottie 使用情况**：搜索 `drawLottie`、`loadLottie` 等，学习已有引入方式；
2. **若项目中尚未使用过 lottie**：按 [references/lottie-setup.md](references/lottie-setup.md) 创建公用工具文件，安装 `@guanghe-pub/onion-utils`。

---

## 生成代码前检查清单（B–G 组）

### B. 组件

- [ ] 是否根据节点 ID 格式（`I前缀;` 子节点）识别了 Figma 组件实例？
- [ ] 是否建立了逐节点元素清单（`data-node-id` / `data-name` / 视觉角色 / 节点类型 / 父子关系）？
- [ ] 是否输出了逐节点组件匹配表，并说明使用 onion-ui / 项目组件 / 原生实现的依据？
- [ ] 是否将组件实例与 onion-ui 组件库进行了语义匹配？
- [ ] 是否根据 `data-name` 正确区分相似组件（Radio 圆形 vs Checkbox 方形）？
- [ ] **是否对 `img-*` / `icon-*` / `OI*` / `oi-*` / `lottie-*` 严格执行了"外层命中即停"——元素清单只记录外层节点，不为内部 Vector / Group / Image 子节点单独开行？**
- [ ] **当 Figma MCP 仅返回外层节点的内部子资源、未直接给出外层组合切图时，是否调用了 `get_screenshot(<外层 nodeId>)` 拉一张外层整体切图？是否避免了"组装内部子资源还原外层"？**
- [ ] **【规则 ①·精确匹配】所有 `icon-*` 节点的 `OIIcon` `name` 是否都是 `data-name` 原值（含 `icon-` 前缀）？没有出现把 `icon-location` 裁成 `location`、把 `icon-arrow-right` 裁成 `arrow` 等语义提取/裁剪？**
- [ ] **【规则 ①·查询证据】判定"OIIcon 无匹配"是否有"已用 `data-name` 原值查询 onion-ui 图标库"的具体证据（查询的图标名 + 检索结果），而非凭印象？**
- [ ] **【规则 ②·只能占位块】图标库无匹配的 `icon-*` 节点是否全部走了占位块路径？没有走任何降级路径（切图 / 手写 SVG / 内联 `<svg><path>` / iconfont / CSS 自绘 / Vector 子节点拼装 / picsum）？**
- [ ] **【规则 ②·显式提示】每个走占位块的图标，是否都在对话中向用户显式输出了「⚠️ onion-ui 图标库中不存在图标 `icon-xxx`，已用占位块代替」？audit 第 4 节是否记录了缺失图标名？**
- [ ] **本次没有为任何 `icon-*` 节点下载 Figma 切图（SVG/PNG）/ 上传 CDN / 放入 `assets/`？没有新增 / 修改任何带有 `<path d="…">` 的本地 SVG 图标文件？**
- [ ] `img-*` 内容图片是否优先使用了 `OIImgLoad`，且 `img-bg-*` 没有被误识别为图片组件？
- [ ] **`img-*` 默认走 `cdn_compress_and_upload` 上传 CDN？没有出现"原型阶段不上 CDN"等虚构分阶段？**
- [ ] 是否优先使用组件库组件，仅在无匹配时用原生 HTML？

### C. 样式数据提取

- [ ] **是否提取了 Auto Layout 字段：`layoutMode` / `itemSpacing` / `padding*` / `primaryAxisAlignItems` / `counterAxisAlignItems` / `layoutGrow`？**
- [ ] **是否提取了文本字段：`fontSize` / `fontWeight` / `lineHeight` / `letterSpacing` / `textAlignHorizontal/Vertical` / `textCase` / `textDecoration`？**
- [ ] 是否提取了 `fills`（含渐变、多层叠加）？
- [ ] 是否提取了 `strokes` / `strokeWeight` / `strokeAlign` / `dashPattern`？
- [ ] 是否提取了 `cornerRadius` / `rectangleCornerRadii`（四角不同的情况）？
- [ ] 是否提取了 `effects`（DROP_SHADOW / INNER_SHADOW / LAYER_BLUR / BACKGROUND_BLUR）？
- [ ] 是否提取了 `opacity` / `blendMode` / `visible`？

### D. 布局

- [ ] 是否先按页面层 / 模块层 / 容器层 / 元素层识别结构关系？
- [ ] **Auto Layout 容器是否映射为 flex 布局（而非绝对定位）？**
- [ ] **`padding` / `gap` 是否直接取 Figma 字段，而非从子节点坐标反推？**
- [ ] 是否根据 Figma 数据出现顺序正确设置元素层级（z-index）？
- [ ] 如需响应式适配，是否结合多断点设计稿分析了响应式变化规则？是否遵循 `responsive-layout` 断点体系？

### E. 视觉属性

- [ ] 所有颜色是否优先使用 design token？
- [ ] 所有间距 / 字号 / 圆角 / 阴影是否优先使用 design token？
- [ ] 字体是否通过导入 `@guanghe-pub/onion-ui/lib/base-css.css` 接入？
- [ ] 是否只有 `data-name` 以 `img-` 开头的节点进入了图片识别和 CDN 上传流程？
- [ ] 是否确认非 `img-` 前缀图片没有被上传 CDN？必要时仅作为本地 `assets` 临时引用？
- [ ] 图片是否按 `img-bg-*` / `img-*` 命名规则分别实现？

### F. 倍率

- [ ] **设计稿根 frame 宽度是否为 750（2x）？若不是，是否已向用户确认换算策略？**
- [ ] **所有 width / height / padding / gap / fontSize / radius / shadow 偏移与模糊半径是否都除以 2？**
- [ ] `lineHeight` 的 px / % 两种形态是否分别正确处理（px ÷2，% 转小数）？

### G. 其他

- [ ] lottie 依赖是否已在当前项目 package.json 中声明并安装？
