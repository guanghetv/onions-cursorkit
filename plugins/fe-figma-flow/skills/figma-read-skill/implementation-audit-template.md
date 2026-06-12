# Figma 实现审计记录模板

> **何时使用**：完成 `get_design_context` + `get_screenshot` 后、编辑任何代码前必须填写并对用户可见输出。表格允许按页面复杂度裁剪行数，但不得省略栏目；无对应字段写 `N/A`，不得留空。

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
| Figma MCP 使用通道 | `figma-read-mcp（本地 Dev Mode，主路径）/ figma-write-mcp（在线，降级路径，原因：__）`（Step 0c / Step 1 写入） |
| **CDN 例外** | `无 / 用户决定不上 CDN，原因：__`（Step 3 写入；默认必为「无」，写「用户决定」时必须有用户原话引用） |

### 1.1 依赖 skill 加载状态（Step 0c 写入，缺一行即视为未完成 Step 0c）

| Requires Skill | 已 Read | 适用性结论 / 关键产物 |
|---|---|---|
| `responsive-layout-analysis` | ☐ | `已加载 / 不适用（理由）` |
| `responsive-layout` | ☐ | `已加载 / 不适用（理由）` |
| `figma-img-cdn-skill` | ☐ | `已加载，CDN 上传为默认动作` |
| `onion-ui-skill` | ☐ | `已加载，onion-ui = vX.X.X，可查询组件 / 图标库` |
| `design-tokens` | ☐ | `已加载，token 文件 = ...` |

## 2. Frame 与倍率判断

| 项 | 设计稿值 | 处理结论 |
|---|---:|---|
| 根 Frame 宽度 | `待填写` | `750 按 2x ÷2 / 非 750 已询问 / 用户指定 1:1` |
| 根 Frame 高度 | `待填写` | `待填写` |
| 代码基准视口 | `待填写` | `待填写` |

> 根 Frame 宽度不是 750 时，必须先向用户确认缩放策略；除非用户明确说按当前像素 1:1 实现。

## 3. 元素清单

| 节点 ID | data-name | 视觉角色 | 节点类型 | 父子 / 层级关系 | 特殊前缀 |
|---|---|---|---|---|---|
| `待填写` | `待填写` | `容器 / 按钮 / 图标 / 图片 / 文本 / 装饰` | `Frame / Group / Vector / Text / Instance / Image` | `待填写` | `OI* / icon-* / img-* / lottie-* / N/A` |

要求：
- **外层命中即停**：当节点 `data-name` 命中 `OI* / oi- / icon- / img- / img-bg- / lottie-` 任一前缀时，本表只记录该外层节点一行；其内部 Vector / Group / Clip / Image 子节点**不得**单独开行（可在视觉角色或备注里写"内部 N 个子节点已并入外层切图"）。
- 反例：`img-menu` 命中后又把 `circle bg` / `Menu-outline` / 三条 `Vector` 各开一行 → ❌
- 正例：`img-menu` 命中后只占一行，备注说明"内部为汉堡菜单图形，整体作为一张切图" → ✅

## 4. 组件匹配表

| 节点 ID | data-name | 匹配实现 | 选择依据 | 需要查阅的文档 / 结果 |
|---|---|---|---|---|
| `待填写` | `待填写` | `OIIcon / OIImgLoad / OIButton / 其他 onion-ui 组件 / 项目已有组件 / 原生实现 / CSS 绘制 / 占位块（图标库无匹配）` | `待填写` | `README 已确认 / 已查询 onion-ui 图标库 + 查询结果 / 无匹配原因` |

要求：
- `OI*`、`icon-*`、`img-*`、组件实例节点必须逐项说明；
- onion-ui 存在语义匹配组件时优先使用；
- 使用原生实现时必须写明为什么组件库不适用；
- **`icon-*` 节点的「匹配实现」字段只允许填以下两种取值之一**（图标库无匹配时不允许任何降级）：
  - `OIIcon（name = "<data-name 原值>"，已通过 onion-ui-skill 查询确认存在）`；
  - `占位块（onion-ui 图标库无 "<data-name 原值>"，已在对话中显式提示用户）`。
- **`icon-*` 的「选择依据」必须包含**：
  - **规则 ①**：使用 `data-name` 原值精确匹配（图层命名本身就是图标名，不做语义提取/裁剪/翻译）；
  - **规则 ②**：已用 `data-name` 原值查询 onion-ui 图标库的具体动作 + 结果（命中即用 OIIcon；未命中即占位块 + 显式提示用户，无其他选项）。
- **禁止出现**："手写 SVG"、"内联 `<path>`"、"CSS 自绘"、"iconfont"、"占位图"、"picsum"、"Figma 切图（CDN）"、"Figma 切图（assets/）"等字样（icon 库无匹配时不允许任何降级路径）；如出现，必须先返工再继续。

## 5. 样式字段提取表

| 节点 ID | 布局字段 | 文本字段 | 填充 | 描边 | 圆角 | 效果 | 透明度 / 混合 |
|---|---|---|---|---|---|---|---|
| `待填写` | `layoutMode / width / height / padding / gap / N/A` | `fontSize / fontWeight / lineHeight / N/A` | `fills / N/A` | `strokes / N/A` | `cornerRadius / N/A` | `effects / N/A` | `opacity / blendMode / N/A` |

要求：
- Auto Layout 节点必须记录 `layoutMode`、`itemSpacing`、`padding*`、对齐方式；
- 文本节点必须记录字号、字重、行高、字距、对齐；
- 多层 `fills` / `strokes` / `effects` 必须完整记录；
- 不得用截图目测值替代 Figma 字段。

## 6. 资源处理计划

| 节点 ID | data-name | 资源来源 | 是否命中 `img-` 门禁 | 处理方式 | 备注 |
|---|---|---|---|---|---|
| `待填写` | `待填写` | `localhost / https / SVG / Vector / N/A` | `是 / 否` | `CDN / 本地 assets / OIIcon / OIImgLoad / CSS background / CSS 绘制 / N/A` | `待填写` |

要求：
- 只有 `data-name.startsWith('img-') === true` 才能走 CDN 上传和 `img-*` 命名规则；
- `img-` 内容图片优先 `OIImgLoad`，不可用时说明原因后降级；
- 非 `img-` 节点即使包含 `localhost` 资源，也不得自动上传 CDN；
- **`icon-*` 节点禁止走切图路径**（无论 CDN 还是本地 `assets/`）：图标库无匹配时只能用占位块 + 显式提示用户，本表"处理方式"字段写 `占位块（图标库无匹配）`，不得出现 `Figma 切图` 字样。

## 7. 生成后验证计划

| 验证项 | 计划 |
|---|---|
| 整页截图对比 | `待填写` |
| 分模块截图对比 | `待填写` |
| computed style 核对节点 | `待填写` |
| 失败兜底 | `同一差异修正 >= 2 次仍无法对齐时向用户确认` |
