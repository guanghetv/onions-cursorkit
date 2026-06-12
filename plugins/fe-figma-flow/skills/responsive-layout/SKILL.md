---
name: responsive-layout
description: >-
  前端团队通用的响应式布局实现规范（代码编写期）。定义 7 级断点体系
  （默认 375 / <375 vw 缩放 / ≥640×640 放大 / ≥640 / ≥768 / ≥1024 / 手机横屏 height<640）、
  `@mixin default` + `@include default` + `@design-width` / `@design-unit` 的小屏等比缩放写法、
  `--safe-area-top/bottom/left/right` 变量用法、tabbar 底部定位、`min-device-width` 内嵌 WebView 适配。
  触发条件（满足任意一条）：
  (1) 需求或 task 中出现"响应式适配"、"pad 适配"、"平板适配"、"iPad 适配"、"折叠屏适配"、
      "横屏适配"、"多端适配"、"多尺寸适配"、"大屏适配"、"小屏适配"；
  (2) 正在编写或修改含 `@media (min-width: 640px|768px|1024px)`、`@media (max-height: 639px)`、
      `@media (min-device-width: ...)` 的 SCSS/CSS；
  (3) 代码中出现或需要使用 `var(--safe-area-*)`、`@mixin default` / `@include default`、
      `@design-width`、`@design-unit`、`postcss-px-to-viewport`、vw 等比缩放；
  (4) 需要处理 tabbar 底部定位、小屏（<375px）等比缩放、内嵌 WebView (`device-width`) 适配；
  (5) 用户明确提到"7 级断点"、"断点规范"、"safe-area 变量"、"mixin default"。
  不触发：
  - 只是泛泛讨论"什么是 media query / 响应式原理"等通用 CSS 知识；
  - 尚未进入 CSS 编写阶段、仍在分析多份 Figma 断点设计稿 → 改用 `responsive-layout-analysis`。
---

# 前端响应式布局适配规范

## 核心策略

- **放弃**全局 `vw` 等比缩放（`postcss-to-vw`）
- **不再**按横竖屏设备类型判断，而是**按屏幕宽高断点**适配
- **采用**固定 px 尺寸 + 响应式布局 + 断点方案
- 仅在小屏（< 375px）保留 vw 等比缩放

## CSS 断点体系（7 级）

断点有**继承覆盖**效果，媒体查询**必须按以下顺序**书写：

```scss
// 1. 默认样式 — 标准手机竖屏（375px 基准）
@mixin default {
  .element { /* 默认样式 */ }
}
@include default;

// 2. 小屏设备 — 外盖屏、单手模式（< 375px → vw 等比缩放）
@media (max-width: 374px) {
  @design-width 375px;
  @design-unit vw;
  @include default;
}

// 3. 放大尺寸 — pad 尺寸放大（仅调尺寸不调布局）
@media (min-width: 640px) and (min-height: 640px) {
  .element { /* 放大字号、间距、圆角等 */ }
}

// 4. 调整布局 — 折叠屏、pad 竖屏（≥ 640px）
@media (min-width: 640px) {
  .element { /* 布局调整 */ }
}

// 5. 调整布局 — 折叠屏、pad 竖屏（≥ 768px）
@media (min-width: 768px) {
  .element { /* 布局调整 */ }
}

// 6. 调整布局 — pad 横屏（≥ 1024px）
@media (min-width: 1024px) {
  .element { /* 布局调整 */ }
}

// 7. 手机横屏 — 必须放最后，优先级最高
@media (max-height: 639px) and (orientation: landscape) {
  .element { /* 横屏专用布局 */ }
}
```

**关键规则**：
- 断点 3（640×640）仅调尺寸不调布局，布局变化只与宽度相关
- 断点 7 必须放在最后，覆盖所有前面的断点样式
- **禁止 `@media` 内嵌套 `@media`**（会导致 postcss 单位转换失效）。SCSS 选择器内写 `@media` 是允许的（编译后会被提取到顶层）

## 小屏设备适配（< 375px）

使用 `@guanghe-pub/postcss-px-to-viewport@v2.1.0`，推荐 `@mixin` + `@include` 方式避免重复编写：

```scss
@mixin default {
  .element {
    height: 32px;
    font-size: 14px;
  }
}
@include default;

@media (max-width: 374px) {
  @design-width 375px;
  @design-unit vw;
  @include default;
}
```

postcss 配置需开启 `onlyCustomAtRule: true`，详见 [breakpoints-reference.md](breakpoints-reference.md)。

## 安全边距 CSS 变量

客户端注入四方向安全边距，前端通过 CSS 变量使用：

```css
.content {
  padding-top: var(--safe-area-top);
  padding-bottom: var(--safe-area-bottom);
  padding-left: var(--safe-area-left);
  padding-right: var(--safe-area-right);
}
```

**要点**：
- 默认使用 `var(--safe-area-top)` 等（带兜底 0px）
- 需要自定义默认值时用 `var(--safe-area-top-no-default, 20px)`
- 横屏时注意设置左右安全边距（摄像头遮挡）
- 详见 [safe-area-variables.md](safe-area-variables.md)

## 底部定位元素适配

有 tabbar 的页面，底部元素**必须基于 tabbar 高度**定位，不要直接基于屏幕底部：

```scss
.bottom-element {
  margin-bottom: calc(var(--safe-area-bottom) + 66px);

  @media (min-width: 640px) {
    margin-bottom: calc(var(--safe-area-bottom) + 80px);
  }
  @media (min-width: 768px) {
    margin-bottom: calc(var(--safe-area-bottom) + 96px);
  }
  @media (max-height: 450px) {
    margin-bottom: calc(var(--safe-area-bottom) + 56px);
  }
}
```

Tabbar 高度断点：

| 条件 | tabbar 高度 |
|------|------------|
| 默认 | 59px |
| 设备宽 ≥ 640 且高 ≥ 640 | 72px |
| 设备高 < 640 | 36px |

## 内嵌 Web 容器适配

在 APP 内嵌 WebView 场景，用 `device-width`/`device-height` 替代 `width`/`height`：

```scss
@media (min-device-width: 640px) and (min-device-height: 640px) { /* ... */ }
@media (min-device-width: 640px) { /* ... */ }
@media (min-device-width: 768px) { /* ... */ }
@media (min-device-width: 1024px) { /* ... */ }
@media (max-device-height: 639px) and (orientation: landscape) { /* ... */ }
```

## 设计稿对应断点

| 设计稿 | 优先级 | 对应断点 |
|-------|-------|---------|
| 750×1334 iPhone7 | **必出** | width ≥ 375（默认） |
| 1280×2048 华为MatePad11 | **必出** | width ≥ 640 |
| 1424×1598 华为X5折叠屏 | 可选 | width ≥ 640 |
| 1536×2048 iPad竖屏 | 可选 | width ≥ 768 |
| 2048×1280 华为MatePad11横屏 | **必出** | width ≥ 1024 |
| 2048×1536 iPad横屏 | 可选 | width ≥ 1024 |
| 1334×750 iPhone7横屏 | **必出** | height < 640 |

4 套必出设计稿应能覆盖大多数场景，非必要不增加额外设计稿。

## 参考文档

- [断点详细参考](breakpoints-reference.md) — 完整断点体系、设备覆盖矩阵、postcss 配置
- [安全边距变量](safe-area-variables.md) — CSS 变量详解、兼容逻辑、utils 库源码
- [代码示例](examples.md) — 完整的断点适配代码示例
