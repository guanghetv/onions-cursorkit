# Design Token 命名示例

> **与本仓库的关系**：下文「基础 / 语义 / 组件」中带虚构 `--oi-*` 刻度的 CSS 片段仅用于说明**分层与 var 链**；本 monorepo 真实包为 `@guanghe-pub/design-tokens`：**global 变量无前缀**（如 `--size-48`、`--spacing-8`），**语义 / 组件**以 `tokens.json` 为准。**按钮**与 Figma 的对照见 `packages/design-tokens/docs/button-token-analysis.md`；**Tag / Option / Dropdown / Error block / Sheet** 等组件变量以 `packages/design-tokens/lib/tokens.css` 与 `src/tokens.json` 为准。

## 基础 Token 定义示例

```css
/* tokens/base.css */
:root {
  /* 尺寸刻度 */
  --oi-size-2: 2px;
  --oi-size-4: 4px;
  --oi-size-8: 8px;
  --oi-size-12: 12px;
  --oi-size-16: 16px;
  --oi-size-20: 20px;
  --oi-size-24: 24px;
  --oi-size-28: 28px;
  --oi-size-32: 32px;
  --oi-size-40: 40px;
  --oi-size-48: 48px;
  --oi-size-56: 56px;

  /* 间距刻度 */
  --oi-spacing-2: 2px;
  --oi-spacing-4: 4px;
  --oi-spacing-8: 8px;
  --oi-spacing-12: 12px;
  --oi-spacing-16: 16px;
  --oi-spacing-20: 20px;
  --oi-spacing-24: 24px;

  /* 颜色原色 */
  --oi-color-blue-50: #e6f4ff;
  --oi-color-blue-400: #4096ff;
  --oi-color-blue-600: #1677ff;
  --oi-color-blue-700: #0958d9;
  --oi-color-gray-50: #fafafa;
  --oi-color-gray-100: #f5f5f5;
  --oi-color-gray-200: #e8e8e8;
  --oi-color-gray-600: #595959;
  --oi-color-gray-900: #141414;
  --oi-color-white: #ffffff;

  /* 圆角刻度 */
  --oi-radius-2: 2px;
  --oi-radius-4: 4px;
  --oi-radius-6: 6px;
  --oi-radius-8: 8px;
  --oi-radius-full: 9999px;

  /* 字体刻度 */
  --oi-font-size-12: 12px;
  --oi-font-size-14: 14px;
  --oi-font-size-16: 16px;
  --oi-font-size-18: 18px;
  --oi-font-weight-regular: 400;
  --oi-font-weight-medium: 500;
  --oi-font-weight-bold: 600;
}
```

## 语义 Token 定义示例

```css
/* tokens/semantic.css */
:root {
  /* 颜色语义 */
  --oi-color-bg-primary: var(--oi-color-blue-600);
  --oi-color-bg-primary-hover: var(--oi-color-blue-700);
  --oi-color-bg-secondary: var(--oi-color-gray-100);
  --oi-color-bg-page: var(--oi-color-white);
  --oi-color-text-primary: var(--oi-color-gray-900);
  --oi-color-text-secondary: var(--oi-color-gray-600);
  --oi-color-text-inverse: var(--oi-color-white);
  --oi-color-border-default: var(--oi-color-gray-200);
  --oi-color-brand: var(--oi-color-blue-600);

  /* 尺寸等级语义 */
  --oi-size-xs: var(--oi-size-24);
  --oi-size-sm: var(--oi-size-28);
  --oi-size-md: var(--oi-size-40);
  --oi-size-lg: var(--oi-size-48);
  --oi-size-xl: var(--oi-size-56);

  /* 圆角语义 */
  --oi-radius-sm: var(--oi-radius-2);
  --oi-radius-md: var(--oi-radius-4);
  --oi-radius-lg: var(--oi-radius-8);

  /* 间距语义 */
  --oi-spacing-xs: var(--oi-spacing-4);
  --oi-spacing-sm: var(--oi-spacing-8);
  --oi-spacing-md: var(--oi-spacing-16);
  --oi-spacing-lg: var(--oi-spacing-16);

  /* 阴影语义 */
  --oi-shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
  --oi-shadow-md: 0 4px 12px rgba(0, 0, 0, 0.1);

  /* 字体语义 */
  --oi-font-size-body: var(--oi-font-size-14);
  --oi-font-size-label: var(--oi-font-size-12);
  --oi-font-size-heading: var(--oi-font-size-16);
}
```

## 组件 Token 定义示例

```css
/* tokens/components/button.css */
:root {
  /* 按钮尺寸 */
  --oi-button-height-xs: var(--oi-size-xs);
  --oi-button-height-sm: var(--oi-size-sm);
  --oi-button-height-md: var(--oi-size-md);
  --oi-button-height-lg: var(--oi-size-lg);

  /* 按钮内边距（组件独有的横向/纵向比例） */
  --oi-button-padding-x-sm: var(--oi-spacing-sm);
  --oi-button-padding-x-md: var(--oi-spacing-md);
  --oi-button-padding-x-lg: var(--oi-spacing-lg);
  --oi-button-padding-y: var(--oi-spacing-xs);

  /* 按钮颜色变体 */
  --oi-button-primary-bg: var(--oi-color-bg-primary);
  --oi-button-primary-bg-hover: var(--oi-color-bg-primary-hover);
  --oi-button-primary-text: var(--oi-color-text-inverse);
  --oi-button-default-border: var(--oi-color-border-default);
  --oi-button-default-text: var(--oi-color-text-primary);

  /* 按钮圆角（复用语义层） */
  --oi-button-radius: var(--oi-radius-md);

  /* 按钮独有属性（无法共享，才放组件层） */
  --oi-button-loading-duration: 0.3s;
  --oi-button-font-weight: var(--oi-font-weight-medium);
}

/* tokens/components/input.css */
:root {
  --oi-input-height-sm: var(--oi-size-sm);
  --oi-input-height-md: var(--oi-size-md);
  --oi-input-height-lg: var(--oi-size-lg);
  --oi-input-border-color: var(--oi-color-border-default);
  --oi-input-border-focus-color: var(--oi-color-brand);  /* 输入框独有 */
  --oi-input-radius: var(--oi-radius-md);
  --oi-input-padding-x: var(--oi-spacing-md);
}
```

## PAD 模式覆盖示例

与本仓库一致：**媒体查询**输出覆盖（非 `data-mode`）。示意：

```css
/* 与本包 build-tokens.mjs 行为一致：pad set → 媒体查询内 :root */
@media (min-width: 640px) and (min-height: 640px) {
  :root {
    --oi-button-height-sm: var(--oi-size-32);
    --oi-button-height-md: var(--oi-size-48);
    --oi-button-height-lg: var(--oi-size-56);
    --oi-input-height-md: var(--oi-size-48);
    --oi-spacing-md: var(--oi-spacing-16);
    --oi-font-size-body: var(--oi-font-size-16);
  }
}
```

## 组件使用示例

```css
/* components/button.css */
.oi-button {
  height: var(--oi-button-height-md);
  padding: var(--oi-button-padding-y) var(--oi-button-padding-x-md);
  border-radius: var(--oi-button-radius);
  font-weight: var(--oi-button-font-weight);
  font-size: var(--oi-font-size-body);
}

.oi-button--primary {
  background: var(--oi-button-primary-bg);
  color: var(--oi-button-primary-text);
  border: none;
}

.oi-button--primary:hover {
  background: var(--oi-button-primary-bg-hover);
}

.oi-button--sm {
  height: var(--oi-button-height-sm);
  padding: var(--oi-button-padding-y) var(--oi-button-padding-x-sm);
}
```

## Token Studio Figma 分层 Set 结构

```
Token Studio Sets（概念）:
├── global          # 基础 Token
├── semantic        # 跨组件语义
├── component       # 组件专用（如按钮、oi-sheet-*、oi-user-header-size-*）
└── pad             # PAD 仅写需覆盖的同名 token

本仓库 $metadata.tokenSetOrder（解析优先级）:
pad → component → semantic → global
```

## 本仓库 `@guanghe-pub/design-tokens` 命名对照（节选）

| 层级 | tokens.json set | CSS 示例 | 说明 |
|------|-----------------|----------|------|
| 基础 | `global` | `--color-gray-50`, `--size-20`, `--spacing-8` | 无前缀 `oi-` |
| 语义 | `semantic` | `--oi-icon-size-xs`, `--oi-shadow-default`, `--oi-color-mask-layer` | 用途别名 |
| 组件 | `component` | `--oi-button-size-md`, `--oi-tag-size-md`, `--oi-option-button-height-md`, `--oi-dropdown-item-font-size`, `--oi-error-block-font-size-title`, `--oi-sheet-header-height`, `--oi-user-header-size-sm` | 各组件前缀：`oi-button-*`、`oi-tag-*`、`oi-option-*`、`oi-dropdown-*`、`oi-error-block-*`、`oi-sheet-*`、`oi-user-header-*` |
| PAD | `pad` | 媒体查询内覆盖上述同名变量 | 断点 3：≥640×640 |
