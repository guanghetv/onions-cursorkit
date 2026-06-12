# 尺寸单位换算（2x 设计稿 ÷2 规则）

> **何时阅读**：SKILL.md「五、尺寸单位」的补充查表。所有从 Figma 字段读到的数值写入代码前，都按本文件的对照规则换算。

## 团队硬约定

Figma 设计稿统一为 **2x 尺寸（根 frame 宽度为 750）**，代码中所有尺寸、间距、字号、圆角、阴影偏移 / 模糊半径都必须缩小一倍（÷2）后再写入。

## 倍率换算对照表

| Figma 字段 | 换算 | 说明 |
|---|---|---|
| `width` / `height` | ÷ 2 | |
| `paddingLeft / Right / Top / Bottom` / `itemSpacing` | ÷ 2 | |
| `fontSize` | ÷ 2 | |
| `lineHeight`（px 形式） | ÷ 2 | |
| `lineHeight`（% 形式，如 `150%`） | **保留比例**，写为小数 | 如 `line-height: 1.5` |
| `letterSpacing`（px） | ÷ 2 | |
| `cornerRadius` / `rectangleCornerRadii` | ÷ 2 | |
| `strokeWeight` | ÷ 2 | 1px 细线（如分割线）需保持 1px 时不再折半 |
| `effects.offset.{x, y}` / `radius`(blur) / `spread` | ÷ 2 | |
| `opacity` / `fontWeight` / 颜色值 | **不换算** | |

## 换算示例

| Figma 原值 | 代码值 |
|---|---|
| `width: 750, height: 1334` | `width: 375px; height: 667px` |
| `paddingTop: 40, itemSpacing: 24` | `padding-top: 20px; gap: 12px` |
| `fontSize: 32, lineHeight: 48` | `font-size: 16px; line-height: 24px` |
| `fontSize: 28, lineHeight: "150%"` | `font-size: 14px; line-height: 1.5` |
| `cornerRadius: 24` | `border-radius: 12px` |
| `effects.radius: 24, offset: {0, 8}` | `box-shadow: 0 4px 12px ...` |
| `strokeWeight: 2` | `border-width: 1px` |
| `strokeWeight: 1`（设计稿本就是 1px 分割线） | `border-width: 1px`（保持不折半） |

## 倍率异常处理

### 1. 根 frame 宽度不是 750

如果读到的根 frame 宽度不是 750（例如是 `375`、`1125`、`1440`、`1280` 或其他），说明设计稿不符合团队约定，**必须先向用户确认再决定换算策略**，不得自行选择倍率：

- 常见误配：设计师直接用 1x（375）起稿、或 iOS 设计师用 375 / 414，Android / PAD 用 1440 等；
- 确认话术参考：
  > 读到的 Figma 根 frame 宽度为 `XXXpx`，不是团队约定的 `750`。请确认：
  > (1) 是否按 1x 原值写入代码（常见于 375 起稿）；
  > (2) 还是需要按 `XXX/375` 倍率缩放；
  > (3) 还是更换为 2x 设计稿重新读取？

### 2. 非整数像素

单次换算出非整数时（如 `15px → 7.5px`），保留一位小数；**同一容器内 `gap` / `padding` 必要时取整对齐**，避免累计误差：

- 示例：两个 `itemSpacing: 15` 并排容器，若都写 `gap: 7.5px`，累计 15px 与一个 `gap: 15px` 视觉等价；
- 但若是 `padding-left: 7.5px + width: 340.5px + padding-right: 7.5px`，建议取整为 `padding: 0 8px; width: 339px` 或类似凑整方案，避免小数渲染的亚像素抖动。

### 3. 1px 细线保持原值

- 设计稿中意图是 **1px 的视觉细线**（分割线、卡片底边）通常 Figma 本身就是 `strokeWeight: 1`（即便 2x 设计稿）；
- 这种情况 ÷2 得 0.5px，不同设备显示不一致，应**保持 1px**不折半；
- 判定：看上下文是否是"视觉 hairline 分割线"语义，而不是机械除 2。

### 4. 字号最小值

- 移动端字体最小可读约 10~11px，若 ÷2 后小于此值（如 Figma `fontSize: 18 → 9px`），**向用户确认**是否设计稿有误。
