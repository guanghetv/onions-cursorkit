---
name: design-tokens
description: >-
  `@guanghe-pub/design-tokens` 接入与使用规范：CSS 变量查阅
  （`var(--color-*)` / `var(--spacing-*)` / `var(--font-*)` /
  `var(--radius-*)`）、三层命名架构（基础/语义/组件）、Figma 颜色/尺寸/间距 →
  token 映射、新增 token 规范、PAD 多端适配覆盖层。
  是 `figma-read-skill` 工作流的必经环节，**跳过会导致整页只命中 1-2 个 token、
  其余颜色/间距/字号全部硬编码**。

  触发条件：
  (1) 用户提供 Figma URL / 节点 ID（`figma.com` / `node-id=` / `123:456`），
  或要求"实现 / 还原 / 开发 / 生成 / 写"Figma 页面或组件——必须与
  `figma-read-skill` 同步触发；
  (2) 编写或修改任何 SCSS / CSS 样式（写入前必须先查 token）；
  (3) 提到 design token / CSS 变量 / token 规范 / token 命名 / 语义 token /
  组件 token / PAD 适配。

  不触发：
  (1) 已确认目标项目未接入 `@guanghe-pub/design-tokens`；
  (2) 与样式无关的纯逻辑代码 / 文档 / 配置任务。
---

# Design Tokens

## 一、项目接入

### 1. 安装依赖

检查当前项目 `package.json` 是否已声明 `@guanghe-pub/design-tokens`，未安装则执行：

```bash
pnpm add @guanghe-pub/design-tokens
```

### 2. 导入 tokens.css

在入口文件或全局样式中导入（**只需导入一次**）：

```css
@import '@guanghe-pub/design-tokens/lib/tokens.css';
```

### 3. 使用规则

- **所有颜色、间距、尺寸、圆角等属性必须使用 token**，禁止硬编码色值或 px 数字
- 直接引用 CSS 变量：`color: var(--color-gray-50)`、`height: var(--oi-button-size-md)`
- 如遇到 token 中不存在的属性（确认无对应 token 后），才允许硬编码
- 如需了解有哪些可用 token，阅读 `node_modules/@guanghe-pub/design-tokens/lib/tokens.css`

---

## 二、Token 三层架构

| 层级 | 数量参考 | 作用 | 示例（tokens.css 中的变量名） |
|------|----------|------|------|
| 基础 Token | 50~200 | 全局原子变量，定义一次处处复用 | `--size-48`, `--color-yellow-50`, `--spacing-16` |
| 语义 Token | 200~500 | 关联基础 Token，表达用途 | `--oi-icon-size-md`, `--oi-shadow-default`, `--oi-color-mask-layer` |
| 组件 Token | 每个 0~20 | 某组件专用或强绑定的别名 | `--oi-button-size-md`, `--oi-tag-size-md`, `--oi-sheet-header-height` |

**复用优先级**：组件属性优先使用语义 Token → 其次基础 Token，**禁止跳层**。

**本仓库 `component` set 前缀（查阅 `lib/tokens.css`）**：`oi-button-*`、`oi-tag-*`、`oi-option-*`、`oi-dropdown-*`、`oi-error-block-*`、`oi-sheet-*`、`oi-user-header-size-*`。

---

## 三、命名格式（tokens.json 中定义）

### 基础 Token（global set）

```
[类别]-[数值刻度]
```

- 尺寸：`size-16` / `size-20` / `size-24` / `size-48` / `size-72` / `size-96`（Figma 2x 值，构建时自动 ÷2 输出）
- 颜色：`color-yellow-50` / `color-gray-20` / `color-blue-50`
- 间距：`spacing-4` / `spacing-8` / `spacing-16` / `spacing-24`
- 圆角：`border-radius-12` / `border-radius-16` / `border-radius-28` / `border-radius-99`
- 字号：`font-size-20` / `font-size-28` / `font-size-44`（Figma 2x 值，`font-size-44` 为 PAD 大按钮专用）
- 字重：`font-weight-regular` / `font-weight-medium` / `font-weight-bold` / `font-weight-black`（按钮 hg/lg 使用 black）

> **注意**：tokens.json 中使用 Figma 2x 尺寸（如 `48px`），`build-tokens.mjs` 构建时自动 ÷2 输出为代码用的 1x 值（`24px`）。

### 语义 Token（semantic set）

```
oi-[类别]-[属性]-[等级]
```

- 图标尺寸：`oi-icon-size-xxs` / `oi-icon-size-xs` / `oi-icon-size-sm` / `oi-icon-size-md` / `oi-icon-size-lg` / `oi-icon-size-hg`
- 投影 / 边框等：`oi-shadow-default`、`oi-border-light`、`oi-border-dark`
- 蒙层色：`oi-color-mask-layer`（全屏遮罩）

**语义 Token 必须引用基础 Token（alias），不写死值**：

```json
"oi-icon-size-md": { "value": "{size-32}", "type": "sizing" }
```

### 组件 Token（component set）

```
oi-[组件名]-[子分类]-[属性]-[等级]
```

- 按钮尺寸与样式：`oi-button-size-md`、`oi-button-color-bg-yellow`、`oi-button-color-text-dark`、`oi-button-color-border` 等（**颜色类**统一为 `oi-button-color-*`）
- 标签：`oi-tag-size-md`、`oi-tag-color-bg-default-gray` 等
- 选项：`oi-option-size-sm`、`oi-option-button-height-md`、`oi-option-button-multiline-font-size-title` 等
- 下拉：`oi-dropdown-padding-x`、`oi-dropdown-item-font-size` 等
- 错误块：`oi-error-block-image-width`、`oi-error-block-font-size-title` 等
- 底部弹层：`oi-sheet-header-height`、`oi-sheet-title-font-size`、`oi-sheet-z-index` 等（蒙层背景请用 `var(--oi-color-mask-layer)`）
- 头像尺寸：`oi-user-header-size-sm` / …

```json
"oi-button-size-md": { "value": "{size-56}", "type": "sizing" }
```

---

## 四、PAD 多端适配

### 原则：媒体查询驱动，非 data-mode 属性

本项目用**媒体查询**驱动 Token 覆盖（与响应式规范断点体系对齐），无需 JS 注入属性。

**PAD Token 覆盖对应断点 3**（仅调整尺寸，不调布局）：

```css
/* 默认：由 global / semantic / component 合并输出到 :root */
:root { --oi-button-size-md: 28px; }

/* PAD 覆盖（自动生成，无需手动维护） */
@media (min-width: 640px) and (min-height: 640px) {
  :root { --oi-button-size-md: 36px; }
}
```

### 在 tokens.json 中新增 PAD 覆盖

在 `pad` set 中**只写需要调整的 token**，未覆盖的自动继承默认值：

```json
{
  "component": { "oi-button-size-md": { "value": "{size-56}", "type": "sizing" } },
  "pad": { "oi-button-size-md": { "value": "{size-72}", "type": "sizing" } },
  "$metadata": {
    "tokenSetOrder": ["pad", "component", "semantic", "global"]
  }
}
```

本仓库 `packages/design-tokens/src/tokens.json` 中 **`$metadata.tokenSetOrder`** 即为上列顺序，供 Token Studio 与工具链解析；修改时需与 Figma 侧 Set 优先级保持一致。

`build-tokens.mjs` 会自动将 `pad` set 输出到 `@media (min-width: 640px) and (min-height: 640px)` 块。

### 构建别名与验收

解析 `{...}` 别名时，脚本将 **pad** set 与默认各 set **放在同一轮映射**中。若 **pad** 与 **semantic** 存在**同名** token，可能影响默认 `:root` 下依赖该语义名的派生变量（例如部分 `--oi-button-icon-size-*`）。**对接设计稿与 Code Review 时以 `lib/tokens.css` 中 `:root` 与 `@media` 的实际输出为准**，勿仅凭「默认 set 手算」假设数值。

---

## 五、新增 / 修改 Token 规范

**新增流程（设计&研发共同评审）**：

1. 确认是否已有语义 Token 可复用（禁止重复定义通用属性）
2. 确认属于哪一层：基础 / 语义 / 组件（组件独有才放组件层）
3. 按命名格式命名，更新 `tokens.json`
4. 运行 `pnpm build`（在 `packages/design-tokens/` 下），验证 `lib/tokens.css` 输出正确
5. 同步更新 Figma 变量，保持 1:1 对齐
6. 禁止单方面修改，需双方确认后同步更新

**以下属性属于语义层（共享），禁止各组件单独定义**：
颜色、间距（padding/margin/gap）、圆角、阴影、字体大小/字重、透明度、边框宽度、尺寸等级

---

## 六、禁止事项

| 禁止行为 | 后果 |
|---------|------|
| 组件样式中直接写 `#FFF9E0` / `40px` 等原始值 | 全局改动时需逐个修改，容易漏 |
| 跳过语义层，直接用基础 Token（如 `--size-48`）写组件属性 | 全局改主色/尺寸时无法一键同步 |
| 把颜色/通用圆角等共享属性放进组件 Token | 组件 Token 爆炸，全局一致性失效 |
| 语义 Token 命名表达"值"而非"用途"（如 `--yellow-bg`） | 换主色时命名与值矛盾 |
| 为 PAD 新增一套 Token 命名 | Token 数量翻倍，维护成本爆炸 |
| 单方面新增/修改 Token 不经过双端确认 | 设计稿与代码不同步，体系失效 |

---

## 七、Figma 设计端对齐

- Figma 变量命名必须与 `tokens.json` 中的 token 名**完全一致**
- 语义 Token 必须引用基础 Token（不写死值），与研发端引用关系保持一致
- 所有元素 100% 绑定 Token，不允许游离的原始值
- PAD 模式：在 Token Studio 中新增 `pad` set，只修改需要调整的属性值，token 名不变
- Token Studio Set 优先级顺序（本仓库）：`pad → component → semantic → global`（见源文件 `$metadata.tokenSetOrder`）

详细示例见 [examples.md](examples.md)
