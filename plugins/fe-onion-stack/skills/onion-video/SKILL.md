---
name: onion-video
description: 洋葱视频播放接入与排查。移动端 App：`bridgeRouter` 调原生；须区分智课（topicVideoV2、simpleVideo、topicVideo）与学习工具（ycplayer 用 toBase64、base64param、browserCommonPlayer、studyWithTopicModel，与智课不同约定）。浏览器 H5：YcPlayer 系 npm 或 CDN；getVideoAddressApi、sources、埋点、env。用户提到视频播放、智课、学习工具、ycplayer、toBase64、YcPlayer、bridgeRouter、知识点/校本视频、H5 与 Native、Vue/React、PC/Mobile 布局时使用。
---

# Onion Video

**流程**：判断运行环境 → **（移动端）区分智课 / 学习工具** → 检查 npm 包与项目内 VideoPlayer 封装 → 按环境实现（细节见 [reference.md](reference.md)）。

## 步骤一：判断环境

| 运行环境 | 方案 |
|----------|------|
| App WebView 内 | `bridgeRouter` 调原生（不在 H5 渲染播放器）；见下 **移动端业务线** |
| 浏览器 H5 + Vue | `@guanghe/yc-player` 或 `@guanghe/yc-pc-player-vue` + 可选项目封装 |
| 浏览器 H5 + React | `@guanghe/yc-pc-player-react` + 可选项目封装 |

判断：`package.json` / 框架特征；是否在 App 内（如 `@guanghe-pub/onion-utils` 的 `platform` 或 UA）。**App 内优先 Native。**

### 移动端：先区分智课 vs 学习工具

两者 **bridge 路径与产品约定不同**，接错会导致跳转或参数不匹配。

| 业务线 | 典型场景 | 调起方式（摘要） |
|--------|----------|------------------|
| **智课** | 课内知识点视频、校本 simple 等 | `topicVideoV2`、`simpleVideo`、旧版 `topicVideo` |
| **学习工具** | 学习工具 App 内嵌 H5 | **推荐** `ycplayer`（模块化）；另有 `browserCommonPlayer`、`studyWithTopicModel`（非首选） |

**若从需求/代码无法判断**：向用户确认一句——「当前页面是 **智课** 还是 **学习工具**？」再按 [reference.md 第一节](reference.md) 选表与示例。

智课与学习工具的具体 `bridgeRouter` 第一参数、参数表、`/ycplayer` 飞书说明见 [reference.md](reference.md) 第一节。

## 步骤二：包与封装

**2.1 播放器包**（查 `package.json`，缺则安装）

| 场景 | 包 | 安装示例 |
|------|-----|----------|
| bridge / 平台判断 | `@guanghe-pub/onion-utils` | `pnpm add @guanghe-pub/onion-utils` |
| H5 Vue | `@guanghe/yc-player` 或 `@guanghe/yc-pc-player-vue` | 按需 `pnpm add` 对应包 + CSS |
| H5 React | `@guanghe/yc-pc-player-react` | `pnpm add @guanghe/yc-pc-player-react` |

**2.2 项目封装**：搜索 `VideoPlayer`、`getVideoAddressApi`、`getAddressList`。若有，优先用封装 props（`videoId`、`topicId`、`autoGetAddress` / 历史拼写以仓库为准、`sources`、`onEnd`、进度上报等）。若无：询问是否新建通用封装；否则业务页自行「`getVideoAddressApi` → `getAddressList` → 播放器 options」。

## 步骤三：按环境实现

阅读 [reference.md](reference.md) 中对应小节（文首有目录）：

- **App Native（智课）**：`topicVideoV2`、`simpleVideo`、旧版 `topicVideo`。
- **App Native（学习工具）**：`ycplayer`（优先：`toBase64(JSON.stringify(param))` → `base64param`；见 reference）、`browserCommonPlayer`、`studyWithTopicModel`。
- **H5 Vue/React**：封装与直连播放器包示例。
- **getVideoAddressApi**：URL、header、响应与转 `sources`。
- **YcPlayer 选项、env、CDN、类型**：第四～七节。

## PC 与 Mobile（H5）

同一套播放器与 options；差异主要是布局尺寸（如 PC 固定宽高、Mobile `fluid: true`）。App WebView 仍优先 `bridgeRouter`；仅在不支持或降级时用 H5 播放器。
