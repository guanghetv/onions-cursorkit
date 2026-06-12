# Auto Layout → CSS Flex / Grid 映射速查

> **何时阅读**：SKILL.md「三、布局分析」中识别到节点带 Auto Layout（`layoutMode != NONE`）时，按本表逐字段映射为 flex 布局。禁止将 Auto Layout 节点写成绝对定位。

## 核心对照表

| Figma Auto Layout | CSS |
|---|---|
| `layoutMode: HORIZONTAL` | `display: flex; flex-direction: row` |
| `layoutMode: VERTICAL` | `display: flex; flex-direction: column` |
| `layoutMode: NONE` | 绝对定位 / 普通文档流 |
| `itemSpacing: N` | `gap: Npx` |
| `paddingLeft / Right / Top / Bottom: N` | `padding-*: Npx` |
| `primaryAxisAlignItems: MIN` | `justify-content: flex-start` |
| `primaryAxisAlignItems: CENTER` | `justify-content: center` |
| `primaryAxisAlignItems: MAX` | `justify-content: flex-end` |
| `primaryAxisAlignItems: SPACE_BETWEEN` | `justify-content: space-between` |
| `counterAxisAlignItems: MIN` | `align-items: flex-start` |
| `counterAxisAlignItems: CENTER` | `align-items: center` |
| `counterAxisAlignItems: MAX` | `align-items: flex-end` |
| `counterAxisAlignItems: BASELINE` | `align-items: baseline` |
| `primaryAxisSizingMode: FIXED` | 写固定 `width` / `height` |
| `primaryAxisSizingMode: AUTO` | 由内容撑开（不写固定宽/高） |
| `counterAxisSizingMode: FIXED` | 写固定交叉轴尺寸 |
| `counterAxisSizingMode: AUTO` | hug 内容 |
| `layoutAlign: STRETCH` | `align-self: stretch` |
| `layoutAlign: MIN / CENTER / MAX` | `align-self: flex-start / center / flex-end` |
| `layoutGrow: 1` | `flex: 1`（该子元素主轴方向充满剩余空间） |
| `layoutGrow: 0` | `flex: 0 0 auto`（保持尺寸不拉伸） |
| `layoutWrap: WRAP` | `flex-wrap: wrap` |
| `itemReverseZIndex` | 反转子元素 DOM 顺序或用 `z-index` 调整 |

所有 `N`（`itemSpacing` / `padding*`）必须按 2x 设计稿的 ÷2 规则换算，见 [size-units.md](size-units.md)。

## 特殊场景

### 混合布局（Auto Layout 里嵌套绝对定位元素）

- Auto Layout 容器内如果存在 `layoutPositioning: ABSOLUTE` 的子节点，该子节点**不参与 flex 排布**；
- 映射：父容器 `position: relative`，该子元素 `position: absolute` 并按坐标定位。

### 由内容撑开的 hug 容器

- `primaryAxisSizingMode: AUTO` + `counterAxisSizingMode: AUTO` → 容器宽高由内容决定，不写显式尺寸；
- 常见于按钮、标签、徽章等随文本长度变化的组件。

### `SPACE_BETWEEN` 且只有一个子元素

- Figma 中 `SPACE_BETWEEN` 即使只有一个子元素也会生效，但在 CSS 中 `justify-content: space-between` 需要至少两个子元素才能看出效果；
- 单个子元素场景实际等价于 `justify-content: flex-start`。

### 二维网格（不是 Auto Layout 但视觉上是网格）

Figma 本身不直接支持 Grid，但设计稿中的**多列卡片 / 多宫格**建议用 CSS Grid 实现，而不是多层 flex 嵌套：

```scss
.grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}
```

判定规则：同一父容器下的子元素**数量固定、尺寸相同、二维排布规则**时优先 Grid；行数 / 列数不定或尺寸差异大时用 flex + `flex-wrap`。

### 粘性底栏 / 固定顶栏

- Figma 中通过 `constraints` 字段表达：`constraints.vertical: BOTTOM` → 底部固定；`constraints.vertical: TOP` → 顶部固定；
- 映射：使用 `position: fixed` / `position: sticky` 而非 Auto Layout。

## Flex ↔ Auto Layout 映射优先级

当 Figma 节点同时具备 Auto Layout 和绝对坐标时，**优先采用 Auto Layout 映射**，忽略绝对坐标；反之当 `layoutMode: NONE` 时，才基于坐标推断布局策略。
