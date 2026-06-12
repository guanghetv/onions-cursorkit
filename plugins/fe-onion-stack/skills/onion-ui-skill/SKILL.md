---
name: onion-ui
description: >-
  `@guanghe-pub/onion-ui` 组件库使用工作流：版本探测、组件 README 链接拼接与查询、
  `OIImgLoad` / `OIButton` / `OIRadio` / `OIIcon` / `OIShareSheet` 等 `OI*`
  组件是否可用及用法判定、用组件库替换原生 HTML。
  是 `figma-read-skill` 工作流的必经环节，**跳过会凭印象判定"OIIcon / OIImgLoad
  无匹配"直接降级，缺乏查询证据**。

  触发条件：
  (1) 用户提供 Figma URL / 节点 ID（`figma.com` / `node-id=` / `123:456`），
  或要求"实现 / 还原 / 开发 / 生成 / 写"Figma 页面或组件——必须与
  `figma-read-skill` 同步触发；
  (2) Figma MCP 返回节点 `data-name` 出现 `OI*` / `oi-*` / `icon-*` 前缀；
  (3) 任务直接涉及 `OIImgLoad` / `OIButton` / `OIRadio` / `OIIcon` /
  `OIShareSheet` 等具体组件名，或要求"用组件库替换原生 HTML 实现"。

  不触发：
  (1) 已确认目标项目未接入 `@guanghe-pub/onion-ui`；
  (2) 与组件库无关的纯 CSS 样式 / 工具函数 / 业务逻辑任务。
---

# Onion UI

## 核心流程

当任务涉及 `@guanghe-pub/onion-ui` 时，按下面顺序执行：

1. 先检测当前项目实际使用的 `@guanghe-pub/onion-ui` 版本。
2. 只在确认版本后，再拼接组件 README 链接。
3. 优先依据 README 判断组件能否使用、如何引入、属性怎么写、事件怎么监听。
4. 先选语义最贴近业务场景的组件，再考虑更底层组件。
5. API 不确定时不要编造，应明确提示需要继续核对 README 或源码。

如果版本无法确认，应明确说明“`不确定当前项目使用的 Onion UI 版本`”，不要假定某个历史版本继续回答。

## 作为其他 Skill 的组件库入口

当其他 Skill 需要“查看组件库”、“查询可用组件”、“确认 `OIImgLoad` / `OIButton` / `OIRadio` 等 `OI*` 组件是否可用”时，也统一通过本 Skill 完成，不要在其他 Skill 中重复维护组件真相。

## 版本确认

优先按下面来源确认版本号：

1. 依赖声明，如业务包 `package.json`、根目录 `package.json`
2. 锁文件
3. `node_modules/@guanghe-pub/onion-ui/package.json`
4. 工作区源码包 `package.json`

不要默认使用固定版本号。

如果当前没有项目上下文：

- 优先让用户提供 `package.json` / 锁文件片段。
- 如果用户没有提供，就明确说明暂时无法确认版本。
- 在未确认版本前，不要给出具体 README 链接或断言某个 API 一定存在。

## README 访问规则

README 链接必须按下面规则拼接：

```text
https://fp.yangcong345.com/library/onion-ui/{detected_onion_ui_version}/{component-kebab-name}/README.md
```

规则：

- 只有已确认版本号后，才能访问对应 README。
- 当 README 直接访问失败、跳转异常或内容不完整时，优先执行：

```bash
curl -L --silent --show-error "<README_URL>"
```

- 组件 README 视为一手说明，优先级高于猜测和经验。
- README 通常包含：组件介绍、引入方式、示例代码、API/Props/Events/Slots。

PascalCase 组件名转 README 路径时，使用 kebab-case：

- `OIShareSheet` -> `share-sheet`
- `OIImgLoad` -> `img-load`
- `OIRadioGroup` -> `radio-group`
- `OINavBar` -> `nav-bar`

当需要查看更多组件清单或不常用组件的 README 路径时，读取 `references/components.md`。

## 场景速查

下面按场景归类列出当前已知组件；这是快速索引，不是能力边界。除历史兼容组件 `Card` 外，业务组件通常都以 `OI` 开头。遇到未在下方显式列举、但名称同样符合 `OI*` 规律的组件，也应继续按“确认版本 -> 拼 README -> 以 README 为准”的流程处理，不要因为速查表里没有就默认不存在。

- 基础动作与展示：`OIButton`、`OIIcon`、`OITag`、`OIBubbleTag`、`OISplitLine`
- 导航与结构：`OINavBar`、`OITabs + OITabItem`、`OISwiper + OISwiperItem`
- 弹层与容器：`OIPopup`、`OISheet`、`OIModal`、`OIModalPlus`、`OIDrawer`
- 分享：`OIShareSheet + OIShareItem`
- 输入与筛选：`OISearch`、`OIDropdown + OIDropdownItem`、`OISwitch`
- 单选：`OIRadioGroup + OIRadio / OIRadioButton`
  默认优先 `OIRadio`；当设计稿明显是按钮块、分段切换或胶囊选项样式时，再优先 `OIRadioButton`
- 多选：`OICheckboxGroup + OICheckbox / OICheckboxButton`
- 进度与加载：`OIProgress`、`OILoading`
- 反馈与状态：`OIToast`、`OIErrorBlock`
- 图片与用户信息：`OIImgLoad`、`OIUserHeader`
- 引导与气泡：`OIGuide`、`OIGuideSimple`、`OIBubble`
- 历史兼容：`Card`

## 生成代码时的优先策略

- 需要图片能力时，优先考虑 `OIImgLoad`，不要直接退回原生 `img`。
- 需要图标时，优先使用 `OIIcon`。
- 需要轻提示时，优先使用 `OIToast`。
- 需要页面异常、空态、错误态时，优先使用 `OIErrorBlock`。
- 需要引导、NPC 对话、局部高亮提示时，优先使用 `OIGuide`、`OIGuideSimple`、`OIBubble`。
- 需要单选/多选交互时，优先使用对应的 Group + Item 模式，不要自己拼装状态逻辑。
- 需要分享能力时，优先使用 `OIShareSheet + OIShareItem`。

## 文档差异与风险点

- 文档并不完全统一，示例与 API 表偶尔会冲突。
- `OITabItem` README 信息较少，使用时应结合 `OITabs` 文档理解。
- `OISwiperItem` README 疑似混入 `OISwiper` 主组件内容，使用时以父组件组合关系为主。
- `Card` 的安装与引入方式偏旧，不要默认它和全部 `OI*` 组件完全一致。
- `OIToast` 的 `icon` 参数规则与普通 `OIIcon` 的传值习惯不同，生成示例时要谨慎。
- 一些 README 存在命名不一致、拼写错误或大小写差异，回答时避免依赖孤例。
- Vue 项目中的 `import`、注册方式、样式引入方式以对应 README 为准，不要套用其他 UI 库习惯。

## 执行要求

- 当用户要实现某个 UI 或交互时，先判断是否已有对应的 Onion UI 组件可直接完成。
- 当某个组件后面提供了 README 文档链接时，把它视为该组件的一手说明，应优先依据该文档理解 API、示例和使用限制。
- 当列举组件名称时，不要把答案收窄成“只有这些组件”；应同时说明这只是高频或当前场景下的组件示例，其他同样以 `OI` 开头的组件也应按统一流程继续核对。
- 当用户只给出模糊场景时，先说明 Onion UI 组件通常以 `OI` 开头，再结合场景推荐最贴近的组件或组件组合。
- 输出示例代码时，尽量给出最小可运行示例，并保持 API 命名与库内文档一致。
- 当用户描述不完整时，优先选择移动端友好、组件库原生能力优先、可维护性更高的方案。
- 当存在多个组件都能解决问题时，优先选择语义最贴近业务场景的组件，而不是最低层原子组件。
- 当不确定某个 API 时，不要编造，应提醒需要进一步核对 README 或源码实现。

## 回答模板

如果需要基于 Onion UI 给出实现方案，优先按下面结构组织：

1. 先说明是否确认到 `@guanghe-pub/onion-ui` 版本。
2. 再说明当前场景优先推荐哪个组件或组件组合，并补一句“Onion UI 业务组件通常以 `OI` 开头，以下只列当前场景最相关的组件，不代表全部组件范围”。
3. 如已确认版本，给出对应 README 链接。
4. 再给出最小可运行示例。
5. 如存在 API 不确定项，单独标注需要继续核对 README 或源码。
