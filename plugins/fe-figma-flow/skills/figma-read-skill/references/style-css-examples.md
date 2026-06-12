# 视觉属性 CSS 写法示例

> **何时阅读**：SKILL.md「四、设计元素属性」中提取到描边、圆角、阴影、模糊等效果字段时，按本文件的对照示例写 CSS。所有数值须按 [size-units.md](size-units.md) 的 ÷2 规则换算，颜色和间距优先使用 `design-tokens` 的 token。

## 阴影

### DROP_SHADOW

Figma 字段：`{ type: "DROP_SHADOW", offset: { x, y }, radius, spread, color }`

```scss
// 单层阴影
box-shadow: 0 4px 12px 0 rgba(0, 0, 0, 0.08);

// 多层阴影（effects 数组多个 DROP_SHADOW 时，逗号分隔叠加）
box-shadow:
  0 2px 4px 0 rgba(0, 0, 0, 0.06),
  0 8px 24px 0 rgba(0, 0, 0, 0.1);
```

### INNER_SHADOW

```scss
box-shadow: inset 0 2px 4px 0 rgba(0, 0, 0, 0.1);

// 与 DROP_SHADOW 共存时一起写
box-shadow:
  inset 0 1px 0 0 rgba(255, 255, 255, 0.1),
  0 4px 12px 0 rgba(0, 0, 0, 0.08);
```

## 模糊

### LAYER_BLUR（元素自身模糊）

```scss
filter: blur(8px);
```

### BACKGROUND_BLUR（背后内容模糊，毛玻璃效果）

```scss
backdrop-filter: blur(12px);
-webkit-backdrop-filter: blur(12px);

// 毛玻璃常与半透明背景共同使用
background: rgba(255, 255, 255, 0.6);
backdrop-filter: blur(20px);
-webkit-backdrop-filter: blur(20px);
```

## 圆角

### 四角相同

```scss
border-radius: 12px;
```

### 四角不同（`rectangleCornerRadii: [tl, tr, br, bl]`）

```scss
// 仅上方圆角（卡片顶部、弹窗顶部）
border-radius: 12px 12px 0 0;

// 对角不同
border-radius: 16px 4px 16px 4px;
```

### 胶囊 / 圆形

```scss
// 胶囊按钮
border-radius: 999px;

// 头像圆形
border-radius: 50%;
```

## 描边

### 实线

```scss
border: 1px solid var(--color-line-primary);
```

### 虚线（`dashPattern` 非空）

```scss
border: 1px dashed var(--color-line-secondary);
```

### 外描边（`strokeAlign: OUTSIDE`）

CSS `border` 默认相当于 `strokeAlign: INSIDE`。若 Figma 使用 `OUTSIDE` 描边且不希望占用内部空间，用 `box-shadow` 模拟：

```scss
// 1px 外描边
box-shadow: 0 0 0 1px var(--color-line-primary);

// 外描边 + 阴影叠加
box-shadow:
  0 0 0 1px var(--color-line-primary),
  0 4px 12px 0 rgba(0, 0, 0, 0.08);
```

### 居中描边（`strokeAlign: CENTER`）

CSS 不原生支持，通常近似为 INSIDE；若视觉差异明显可用 `outline` + `outline-offset: -N/2`。

## 渐变填充

### 线性渐变（`GRADIENT_LINEAR`）

```scss
// 垂直渐变
background: linear-gradient(180deg, #ff6b6b 0%, #ff8787 100%);

// 对角渐变
background: linear-gradient(135deg, var(--color-brand-1) 0%, var(--color-brand-2) 100%);
```

### 径向渐变（`GRADIENT_RADIAL`）

```scss
background: radial-gradient(circle at center, #fff 0%, #f5f5f5 100%);
```

### 多层填充叠加

Figma `fills` 数组多项时按顺序叠加（前者在上）：

```scss
// 顶层半透明遮罩 + 底层图片
background:
  linear-gradient(180deg, rgba(0, 0, 0, 0) 0%, rgba(0, 0, 0, 0.5) 100%),
  url('https://cdn.example.com/bg.jpg') center / cover no-repeat;
```

## 透明度与混合模式

```scss
// 整体透明度（不影响子元素各自的颜色 alpha）
opacity: 0.6;

// 混合模式（仅在 blendMode 非 PASS_THROUGH / NORMAL 时写）
mix-blend-mode: multiply;
```

## 综合示例

半透明毛玻璃卡片，带外描边 + 阴影 + 顶部圆角：

```scss
.card {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-radius: 16px 16px 0 0;
  box-shadow:
    0 0 0 1px rgba(255, 255, 255, 0.3),
    0 -4px 20px 0 rgba(0, 0, 0, 0.08);
}
```
