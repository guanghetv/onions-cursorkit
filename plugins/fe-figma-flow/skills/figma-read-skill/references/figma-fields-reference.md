# Figma 节点字段 → CSS 完整映射表

> **何时阅读**：执行 SKILL.md 「二、样式数据完整提取」时，按需查阅本表。生成代码前，节点所有非默认字段都应在本表中找到对应 CSS 映射。

按「布局 / 文本 / 填充 / 描边 / 圆角 / 效果 / 透明度」七类分组。所有数值字段在写入代码前必须按 [size-units.md](size-units.md) 的 2x ÷2 规则换算。

## 1) 布局字段（Auto Layout + 尺寸）

| Figma 字段 | 含义 | 映射到 CSS |
|---|---|---|
| `layoutMode` | `HORIZONTAL` / `VERTICAL` / `NONE` | `flex-direction: row / column` 或非 flex |
| `itemSpacing` | 子元素间距 | `gap` |
| `paddingLeft / Right / Top / Bottom` | 容器内边距 | `padding-*` |
| `primaryAxisAlignItems` | 主轴对齐 | `justify-content` |
| `counterAxisAlignItems` | 交叉轴对齐 | `align-items` |
| `primaryAxisSizingMode` / `counterAxisSizingMode` | `FIXED` / `AUTO`（hug） | 固定尺寸 / 由内容撑开 |
| `layoutAlign` / `layoutGrow` | 子元素在父容器内的对齐与拉伸 | `align-self` / `flex-grow` |
| `width` / `height` | 节点尺寸 | `width` / `height` |
| `constraints` | 相对父容器的约束 | 响应式约束推断 |

> Auto Layout 与 Flex 的完整映射速查（含对齐枚举值）见 [auto-layout-to-flex.md](auto-layout-to-flex.md)。

## 2) 文本字段

| Figma 字段 | 映射 |
|---|---|
| `fontFamily` | 默认由 `@guanghe-pub/onion-ui/lib/base-css.css`（阿里普惠）提供，特殊字体才单独声明 |
| `fontSize` | `font-size` |
| `fontWeight` | `font-weight`（400 / 500 / 600 / 700） |
| `lineHeight`（`px` 或 `%`） | `line-height`（px 直接用，% 转小数，见 [size-units.md](size-units.md)） |
| `letterSpacing` | `letter-spacing` |
| `textAlignHorizontal` | `text-align: left / center / right / justify` |
| `textAlignVertical` | 结合 flex `align-items` 或 `line-height` 实现 |
| `textDecoration` | `text-decoration: underline / line-through` |
| `textCase` | `text-transform: uppercase / lowercase / capitalize` |

## 3) 填充字段（`fills`，数组，按顺序叠加）

| 类型 | 映射 |
|---|---|
| `SOLID` | `background-color`（容器） / `color`（文本） |
| `GRADIENT_LINEAR` | `background: linear-gradient(...)` |
| `GRADIENT_RADIAL` | `background: radial-gradient(...)` |
| `IMAGE` | 走图片流程（见 `figma-img-cdn-skill`） |

多层填充必须按数组顺序叠加；`opacity` 字段独立于 fill 的 alpha，需分别还原。

## 4) 描边字段（`strokes` + `strokeWeight`）

| 字段 | 映射 |
|---|---|
| `strokes` | `border-color` |
| `strokeWeight` | `border-width` |
| `strokeAlign` | `INSIDE` / `OUTSIDE` / `CENTER`；`OUTSIDE` 必要时用 `box-shadow: 0 0 0 N` 模拟 |
| `dashPattern` | `border-style: dashed` |

CSS 写法示例见 [style-css-examples.md](style-css-examples.md)。

## 5) 圆角字段

| 字段 | 映射 |
|---|---|
| `cornerRadius` | `border-radius`（四角相同） |
| `rectangleCornerRadii: [tl, tr, br, bl]` | `border-radius: tl tr br bl`（四角不同） |

## 6) 效果字段（`effects`，多个逗号分隔叠加）

| 类型 | 映射 |
|---|---|
| `DROP_SHADOW` | `box-shadow: x y blur spread color` |
| `INNER_SHADOW` | `box-shadow: inset x y blur spread color` |
| `LAYER_BLUR` | `filter: blur(Npx)` |
| `BACKGROUND_BLUR` | `backdrop-filter: blur(Npx)` + `-webkit-backdrop-filter` |

## 7) 透明度 / 混合模式

| 字段 | 映射 |
|---|---|
| `opacity` | `opacity`（0~1） |
| `blendMode` | `mix-blend-mode`（非 `PASS_THROUGH` / `NORMAL` 时） |
| `visible: false` | 不渲染该节点 |

## 提取铁律（SKILL.md 已强约束，此处仅重复以便查阅）

1. **Auto Layout 容器的 `padding` 与 `gap` 必须直接取 Figma 字段**，严禁从子节点 x/y 反推或目测截图；
2. 节点有 Auto Layout（`layoutMode != NONE`）时，**默认映射为 flex 布局**，不允许退化为整页绝对定位；
3. 所有数值必须按 [size-units.md](size-units.md) 的 ÷2 规则换算后再写入代码；
4. 所有颜色、间距、字号、圆角、阴影值必须优先匹配 `design-tokens` 里的 token，命中即用 token，未命中才写原始值；
5. 多层 `fills` / `strokes` / `effects` 必须按数组顺序完整还原，不能只取第一项。
