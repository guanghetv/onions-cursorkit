---
name: pm-proto
description: >-
  Use when user mentions: 原型/画原型/pm-proto/页面草图/交互示意。
  Triggers when requirements directory exists and PM wants prototype assets.
---

# /pm-proto — 产品原型快速生成

## 前置条件

- 需求目录已创建（`/req-new` 已执行）
- `prototypes/` 目录不存在时自动创建
- 当前工作区可访问 `workspace-repos.json`（用于扫描相关前端项目）

## 核心原则

- 只处理原型资产：`prototypes/` + 可选 `assets/`
- 不修改 `prd.status`，不触发 confirmed
- 原型输出要可被 `prd.md` 引用（路径/锚点稳定）
- 涉及前端页面时，先扫描当前工作区前端项目，复用已有样式规范、页面逻辑与核心交互

## 流程

### Step 0: 扫描当前工作区上下文（必做）

- 扫描 `workspace-repos.json`，识别可用前端项目与相关目录
- 读取目标需求目录上下文（`prd.md`、`prototypes/`、可选 `assets/`）
- 识别是否已有同类页面/流程可参考，作为原型复用输入

### Step 1: 定位需求与原型现状

- 读取目标需求目录
- 判断 `prototypes/index.html` 是否存在
- 判断是“首次生成”还是“增量迭代”

### Step 2: Brainstorming（需求与交互澄清）

- 调用 `superpowers:brainstorming` 与产品同学澄清：
  - 本次原型目标页面与核心路径
  - 关键交互步骤、反馈方式、异常场景
  - 与现有页面/流程保持一致的部分与需要改动的部分
- 形成原型生成前的最小决策清单（避免直接开画后返工）

### Step 3: 扫描当前工作区前端代码（涉及 UI 时必做）

- 从 `workspace-repos.json` 定位当前工作区前端项目目录
- 只读扫描 UI 相关代码、页面逻辑与样式规范（如路由、状态流转、交互处理、设计 token）
- 提取可复用规范：
  - 颜色、字号、间距、圆角、阴影等视觉 token
  - 按钮、表单、卡片、表格等常见组件样式
  - 页面布局栅格、响应式断点、交互状态（hover/disabled/loading）
  - 页面关键业务流程（如筛选、提交、审批、跳转、异常处理）
  - 核心交互链路（打开方式、步骤顺序、反馈机制、空态/错误态处理）
- 在原型输出中尽量贴近现有风格和交互习惯，避免“新造一套视觉体系或交互模型”

### Step 4: 生成或更新原型

- 首次：创建 `prototypes/index.html` 基础骨架
- 增量：按用户描述更新页面与交互说明
- 推荐补充 `assets/`（截图或流程示意），提升后续 PRD 直观性

### Step 5: 添加可引用锚点

为关键模块增加稳定锚点（例如 `#module-1`），便于 `prd.md` 引用。

### Step 6: 输出引用建议

生成后提示可直接粘贴的引用：

- `prototypes/index.html#module-1`
- `assets/<file>.png`（如有截图）

若当前无截图，提示建议补充 1 张关键截图（非阻断），可在 `/pm-spec` 前后补齐。

### Step 7: 提示下一步

提示产品同学：更新 `prd.md` 后执行 `/pm-spec` 完成结构化与 AI Review。

## 约束

- 禁止修改代码仓库文件
- 禁止在本技能内修改 `metadata.yaml` 的 `prd.status`
- 无原型需求可跳过本技能，直接执行 `/pm-spec`
- 扫描前端代码只用于提取页面逻辑与交互规范，不输出技术实现细节到 PRD
