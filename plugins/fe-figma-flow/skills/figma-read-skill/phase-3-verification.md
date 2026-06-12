# 生成后验证 · 详细流程与差异表模板

> **何时阅读**：编排器在执行 Step 9 前 Read 本文件。生成代码后必须按本文件完成 整页对比 → 分模块对比 → computed style 数值核对 三级验证，并用差异表记录与跟踪。
>
> **输入**：`figma-audit.md`（已包含第 1–6 节）+ 编排器上下文中已保存的设计稿截图（Step 2）+ 目标页面 URL（或本地 dev server 地址）。
> **输出**：差异表 + 修正记录，差异全部清空后在 `figma-audit.md` 第 7 节追加「验证结论」。

## 为什么要三级验证

- 模块级的 `gap` / `padding` 偏差 2~4px 在整页截图里肉眼基本看不出来，但跨多模块累计会显著偏差；
- 行高、字距、阴影半径、圆角差异只有对比 computed style 才能发现；
- 只截一张整页图很容易被"大致对齐"的视觉印象欺骗。

## 必须执行的步骤（按顺序）

### Step 1：保留设计稿截图

- 步骤 2 通过 `get_screenshot` 获取的整页截图作为基准；
- 对关键模块（顶栏、主卡片、底部操作区等）额外抓一次设计稿的局部截图，便于逐模块叠加对比；
- 保留到本地或当前会话，命名建议：`figma-{nodeId}-{module}.png`。

### Step 2：启动并打开接管页面

- 启动项目（如 `pnpm dev`）；
- 通过 `cursor-ide-browser` MCP、浏览器 DevTools、或其他可用的截图工具打开对应页面。

### Step 3：整页对比

- 对当前运行页面整页截图；
- 与设计稿整页截图并排 / 叠放对比，定位大块差异（缺失模块、顺序错乱、整体偏色等）。

### Step 4：分模块对比（强制）

- 对每个关键模块（顶栏、表单、卡片、列表、底部操作区等）分别截图；
- 逐模块比对 —— 整页易出现"看起来差不多"误判，**模块级差异必须单独核对**；
- 发现差异定位到模块，进入 Step 5 做数值核对。

### Step 5：关键节点 computed style 核对（强制）

通过浏览器 DevTools 或 `cursor-ide-browser` 的 snapshot / evaluate 能力，读取关键容器的 **computed style**，与 Figma 字段（÷2 后）逐项对照。

**必须核对的节点**：

- 模块根节点（每个主要模块）；
- 按钮、卡片、表单项、标题文本、列表项（每种类型至少抽查 1 个实例）；
- 有阴影 / 毛玻璃 / 渐变背景的容器。

**必须核对的属性**（最小子集）：

```
padding / gap / width / height
font-size / font-weight / line-height / letter-spacing
border-radius / border / box-shadow
opacity / backdrop-filter
```

**当前浏览器 MCP 不支持 evaluate JS 时的降级方案**（如 `cursor-ide-browser` 无 `browser_evaluate` 工具、且 `browser_get_bounding_box` 对装饰性元素返回空时）：

1. **不允许直接跳过 Step 5**；
2. 按以下顺序尝试：
   - **a. 给目标节点加 `aria-label` / `role` / `tabindex="0"` 让其进入 a11y 树**，使 `browser_snapshot` 能返回 ref，再调用 `browser_get_bounding_box`；
   - **b. 用 `browser_highlight` + `browser_take_screenshot` 视觉框选关键节点**，结合截图量取的方式核对位置/尺寸（精度低于 evaluate，仅作兜底）；
   - **c. 终极降级：「样式表 ↔ Figma 字段一一映射」的代码级核对**——逐节点把 Vue/CSS 中写入的 `left/top/width/height/padding/gap/font-size/...` 对照 Figma get_design_context 字段（÷2 后）逐项比对，差异点写入差异表；
3. **必须在 audit 第 7 节明确标注降级原因**："computed style 核对降级为代码级字段映射，原因：浏览器 MCP 不支持 evaluate JS"。
4. 走 c 路径时，由于无运行时数据，差异表里"实现值"列填"代码字面值"，不能直接证明 layout 引擎的最终渲染没有偏差，所以**仍然必须**配合 Step 4 的分模块视觉对比补强。
5. **永远不允许**因为"环境不支持就不做 Step 5"而沉默——降级路径与降级原因必须明确写入 audit。

### Step 6：记录差异表

每项差异按下表模板记录：

| 节点 ID | 属性 | 设计值（÷2 后） | 实现值 | 差值 | 原因推断 |
|---|---|---|---|---|---|
| `12:345` | `padding-top` | 20px | 16px | -4px | 容器 `paddingTop: 40` 未映射，误用默认值 |
| `12:567` | `gap` | 12px | 8px | -4px | 使用了固定 `gap: 8px`，未读 `itemSpacing: 24` |
| `I43:384;65:6890` | `line-height` | 1.5 | 1.2 | -0.3 | `lineHeight: "150%"` 错写成 `line-height: 1.2` |

### Step 7：修正并重复验证

- 按差异表回到代码中，按 token 与字段修正；
- 修正后重复 Step 3 ~ Step 5，直至满足 1:1 还原；
- **差异表完全清空前，不得声明"还原完成"。**

### Step 8：兜底 —— 反复修仍无法对齐

同一处差异修 ≥ 2 次仍无法对齐时，**主动向用户确认**设计意图，不要无限循环猜测：

- 可能原因：
  - 设计稿本身与组件库约束冲突（比如 Figma 要求 `OIButton` 圆角 6px，但组件库固定 8px）；
  - Figma 字段为特殊写法（如 `lineHeight` 单位异常、`strokeAlign: OUTSIDE` 无法用 CSS `border` 还原）；
  - 设计师遗漏 / 设计稿过时；
- 确认话术参考：
  > `{nodeId}` 的 `{属性}` 在设计稿为 `{设计值}`，当前组件库 / CSS 实现值为 `{实现值}`，经 2 次修正仍存在差异。可能原因是 {A/B/C}，请确认按哪个实现。

## 与图片尺寸异常的关系

- **OIImgLoad 尺寸异常**：若未做分模块对比，图片容器的 `width` / `height` / `object-fit` 错误不易暴露；
- 生成后验证时若发现图片与设计稿不一致，应检查对应 class 是否设置 `width`、`height`、`object-fit`（见 `figma-img-cdn-skill`）。

## 验证完成检查清单

- [ ] 是否对运行中的接管页面进行了**整页**截图？
- [ ] **是否对关键模块分别进行了分模块截图与对比？**
- [ ] **是否对关键节点读取了 computed style，并与 Figma 字段（÷2 后）逐项核对？**
- [ ] **如浏览器 MCP 不支持 evaluate JS，是否走了 a/b/c 三档降级方案，并在 audit 第 7 节标注了降级原因？**
- [ ] 差异表是否记录了 `节点 ID | 属性 | 设计值 | 实现值 | 差值 | 原因`？
- [ ] 对比后若存在尺寸 / 布局 / 样式差异，是否已修正并再次验证？
- [ ] 反复修仍无法对齐时，是否已向用户确认设计意图？
- [ ] 差异表是否已全部清空（或剩余项均已获得用户确认）？
