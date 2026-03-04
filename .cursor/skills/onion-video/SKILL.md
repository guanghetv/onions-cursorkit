---
name: onion-video
description: 洋葱视频播放能力使用指南。覆盖移动端 App 内（Native 播放）、H5 页面（Vue/React）的集成方式，以及 PC 与 Mobile 场景区分。当用户需要接入或排查视频播放、getVideoAddressApi、YcPlayer、topicVideoV2、simpleVideo 时使用。
---

# Onion Video 使用技能

洋葱视频体系包含：**移动端 Native 播放**（App WebView 内调原生播放器）与 **H5 播放器**（YcPlayer / 封装组件）。接入或修改播放功能时，按下面操作步骤执行：**先判断环境 → 再检查/安装依赖 → 再按环境写具体使用**。

## 何时使用本技能

- 在任何需要接入或修改洋葱视频播放的项目中（移动端 App 内、Vue H5、React H5 等）
- 需要区分：移动端 vs H5、Vue vs React、是否已有项目内封装
- 调用 `getVideoAddressApi`、`bridgeRouter` 或播放器包（YcPlayer / YcPcPlayer）时查阅

---

## 操作步骤

### 步骤一：判断环境

按运行场景确定使用哪套方案（不依赖具体项目名，按技术栈判断）：

| 运行环境 | 方案 | 说明 |
|----------|------|------|
| **App WebView 内** | 移动端 Native 播放 | 用 `bridgeRouter` 调起原生播放器（topicVideoV2 / simpleVideo），不在 H5 里渲染播放器 |
| **浏览器 H5 + Vue 项目** | H5 播放器（Vue） | 使用播放器 npm 包 + 项目内封装（若有）或直接调包 |
| **浏览器 H5 + React 项目** | H5 播放器（React） | 使用播放器 npm 包 + 项目内封装（若有）或直接调包 |
| **PC / Mobile** | 同一套播放器 | 仅布局与尺寸不同，依赖与调用方式一致 |

判断方式：看当前项目是 Vue 还是 React（`package.json`、入口或框架特征）；看页面是否在 App 内（如 `@guanghe-pub/onion-utils` 的 `platform` 或 UA）。在 App 内优先走移动端方案。

### 步骤二：检查播放器包并检查/添加项目封装

**2.1 检查并安装播放器 npm 包（洋葱提供，与项目无关）**

根据步骤一确定的技术栈，检查对应**播放器包**是否已安装；未安装则先安装。

| 技术栈 | 播放器包（二选一或按现有项目约定） | 检查方式 | 未安装时安装命令 |
|--------|-------------------------------------|----------|------------------|
| **移动端（bridgeRouter）** | `@guanghe-pub/onion-utils` | 查看 `package.json` 的 `dependencies` | `pnpm add @guanghe-pub/onion-utils` 或 `npm i @guanghe-pub/onion-utils` |
| **H5 Vue** | `@guanghe/yc-player` 或 `@guanghe/yc-pc-player-vue` | 查看 `package.json` | `pnpm add @guanghe/yc-player` 或 `pnpm add @guanghe/yc-pc-player-vue`（及对应 CSS） |
| **H5 React** | `@guanghe/yc-pc-player-react` | 查看 `package.json` | `pnpm add @guanghe/yc-pc-player-react` 或 `npm i @guanghe/yc-pc-player-react` |

执行：看 `package.json`，若当前技术栈对应的播放器包不存在，先执行上表安装命令，再继续。

**2.2 检查项目是否已有「使用封装」（与包无关，项目内实现）**

- **封装**：指项目内是否有统一组件（如 `VideoPlayer`），内部完成「调 `getVideoAddressApi` → 用 `getAddressList` 转成 `sources` → 把 options 传给播放器包」。
- **检查**：在项目中搜索是否已有类似 `VideoPlayer`、`getVideoAddressApi`、`getAddressList` 的封装（常见路径如 `components/VideoPlayer`、`commonComponents/videoPlayer` 等）。
- **若 H5 没有封装**：
  1. **先询问用户**：是否需要做通用封装（便于多处复用、统一维护）。
  2. **若用户需要通用封装**：在项目内**建立一个 video 的封装组件**，建议包含：
     - 封装组件：如 `VideoPlayer.vue` / `VideoPlayer.tsx`，接收 `videoId`、`topicId`、`autoGetAddress`（或直接传 `sources`）、`onEnd`、`onUplodaProcess` 等 props；
     - 内部调用 `getVideoAddressApi` 获取地址，用 `getAddressList` 转成 `sources`，将 options 传给当前技术栈的播放器包（Vue 用 `@guanghe/yc-player` 或 `@guanghe/yc-pc-player-vue`，React 用 `@guanghe/yc-pc-player-react`）；
     - 配套的 `service`（如 `getVideoAddressApi`）与 `utils`（如 `getAddressList`、`getEnv`、`customDomainObj`）可放在同一目录（如 `components/VideoPlayer/` 或 `commonComponents/videoPlayer/`）。
  3. **若用户不需要封装**：在业务页直接使用播放器包 + 自行调用 `getVideoAddressApi` 并做 address → sources 转换。

完成 2.1 和 2.2 后再进行步骤三。

### 步骤三：按环境具体使用

根据步骤一的环境与步骤二是否已有封装，按下面对应小节接入或修改代码。

---

## 一、移动端（App 内）— 步骤三之 Native 调起

当**步骤一**判定为 App WebView 内时，使用本小节。通过 `@guanghe-pub/onion-utils` 的 `bridgeRouter` 调起原生播放器，无需在 H5 里渲染播放器。

### 1. 知识点视频（topicVideoV2）

```ts
import { bridgeRouter } from '@guanghe-pub/onion-utils'

bridgeRouter('ycmath://yangcong345.com/topicVideoV2', {
  topicId,
  itemId,
  taskId,
  courseId: courseId || '',
  completeUrl: btoa(`${host}/path/to/completePage?${query}`), // 完成页 URL，按业务替换
  statistics: JSON.stringify({ topicId, taskId, measuringId, itemId }),
  playRangeStart?: number,   // 可选，片段起始秒
  playRangeEnd?: number,     // 可选，片段结束秒
  enableAISummarize?: boolean,
})
```

- `completeUrl` 为完成页 H5 地址的 **Base64**；原生播放器结束后会打开该 URL。

### 2. 简单视频（simpleVideo）

先取播放地址，再调起简单播放器。

```ts
const res = await getSchoolVideoPlayUrlApi(itemId)
const videoUrl = res.url

bridgeRouter('ycmath://yangcong345.com/simpleVideo', {
  itemId,
  taskId,
  videoUrl: base64Encode(videoUrl),
  completeUrl: btoa(`${schoolH5Host}/path/to/completePage?${query}`), // 完成页 URL，按业务替换
  statistics: JSON.stringify({ ... }),
  playRangeStart?: number,
  playRangeEnd?: number,
})
```

- `videoUrl` 需 **Base64 编码** 后传入。

### 3. 旧版知识点视频（topicVideo）

部分学习页仍用 `topicVideo`，参数更少：

```ts
bridgeRouter('ycmath://yangcong345.com/topicVideo', {
  topicId,
  taskId,
  groupId,
  pageFrom: 'video',
})
```

---

## 二、H5 播放器（浏览器内）— 步骤三之 Vue / React

以下为**步骤三**在 H5 场景下的具体用法（环境在步骤一已判定，播放器包与封装在步骤二已检查/安装或添加）。

### 1. Vue 项目

**若项目内已有 VideoPlayer 封装（步骤二已确认）**：直接使用该组件，传入 `topicId`、`videoId`、`autoGetAddress`（或 `sources`）、`onEnd`、`onUplodaProcess` 等即可。封装内部会调 `getVideoAddressApi`、`getAddressList` 并把 options 传给播放器包。

```vue
<template>
  <VideoPlayer
    ref="videoPlayerRef"
    :topic-id="topicId"
    :video-id="videoId"
    :auto-get-address="true"
    :video-subtitle-url="subtitleUrl"
    :need-upload-process="true"
    @end="onEnd"
    @uploda-process="onUploadProcess"
  />
</template>
<script setup>
import VideoPlayer from '@/components/VideoPlayer/index.vue' // 路径以项目为准
</script>
```

**若无封装，直接使用播放器包**：Vue 项目可能使用 `@guanghe/yc-player` 或 `@guanghe/yc-pc-player-vue`。先调用 `getVideoAddressApi` 获取地址，用 `getAddressList` 转成 `sources`，再把 options 传给播放器。

```ts
// 以 @guanghe/yc-player 为例
import YcPlayer, { Player } from '@guanghe/yc-player'
import '@guanghe/yc-player/dist/yc-player.min.css'
// 或 @guanghe/yc-pc-player-vue 时：import YcPcPlayer from '@guanghe/yc-pc-player-vue'

const address = await getVideoAddressApi(videoId, topicId)
const sources = getAddressList(address)
playerRef.value = await YcPlayer(containerEl, {
  env: getEnv(),
  fluid: true,
  videoId,
  sources,
  customDomainObj,
  buryPointParams: { ... },
  keyPoints: [],
  startTime: 0,
})
playerRef.value.on('ended', handleEnd)
// 销毁：playerRef.value?.dispose()
```

### 2. React 项目

**若项目内已有 VideoPlayer 封装（步骤二已确认）**：直接使用该组件，传入 `topicId`、`videoId`、`autoGetAddrss`（或 `sources`）、`buryPointParams`、`onEnd`、`onShut`、`onUplodaProcess` 等。封装内部会调 `getVideoAddressApi`、`getAddressList` 并传 options 给 `@guanghe/yc-pc-player-react`。

```tsx
import VideoPlayer from '@/commonComponents/videoPlayer/index' // 路径以项目为准

<VideoPlayer
  fluid
  autoGetAddrss={true}
  topicId={topicId}
  videoId={videoId}
  sources={sources}
  buryPointParams={buryPointParams}
  videoSubtitleUrl={subtitleUrl}
  needUploadProcess={fromHomework}
  onEnd={(currentTime, playingTime) => onVideoEnd(currentTime, playingTime)}
  onShut={(currentTime, playingTime) => quit(currentTime, playingTime)}
  onUplodaProcess={(currentTime, playingTime, duration, process) => { /* 上报进度 */ }}
/>
```

**若无封装，直接使用播放器包**：安装 `@guanghe/yc-pc-player-react` 后，在页面内先调 `getVideoAddressApi`、`getAddressList` 得到 `sources`，再把 options 传给 `YcPcPlayer`。

```tsx
import YcPcPlayer, { Player } from '@guanghe/yc-pc-player-react'
import '@guanghe/yc-pc-player-react/dist/yc-pc-player.min.css'

const address = await getVideoAddressApi(videoId, topicId)
const videoSources = getAddressList(address)

<YcPcPlayer
  onInit={(player: Player) => { player.on('ended', handleEnd) }}
  options={{
    videoId,
    env: getEnv(),
    fluid: true,
    sources: videoSources,
    customDomainObj,
    buryPointParams: { ...buryPointParams, extraParams: {} },
    keyPoints: [],
    startTime: 0,
  }}
/>
```

### 3. getVideoAddressApi 约定（与项目无关）

- 常见接口：`POST ${apiDomain}/videos/addresses` 或 `.../video/addresses`，body 一般为 `{ videoList: [{ videoId, custom: { topicId } }] }`，部分业务带 header 如 `client-category: 'wisdom' | 'pc'`。
- 返回的 `videoList[0].address` 为清晰度列表，需按 `platform === 'mobile' && format === 'hls'` 等规则过滤，再用 `getAddressList` 转成播放器所需的 `sources`（`src`、`type: 'application/x-mpegURL'`、`clarity` 等）。具体域名与路径以当前项目/业务为准。

---

## 三、PC 与 Mobile 区分（H5）

- **同一套 YcPlayer**：PC 与 Mobile 都用同一 CDN 与同一套 options，区别主要在布局与尺寸（如 PC 用 800x500，Mobile 用 100% 宽 + 固定高度或 `fluid: true`）。
- **在 App 内**：若运行在 App WebView，应优先用 **移动端** 的 `bridgeRouter` 调原生（topicVideoV2 / simpleVideo），体验更好；仅在不支持或降级时才在 H5 里用 YcPlayer。
- **环境**：`getEnv()` 返回 `production | stage | test`，与 `customDomainObj` 的域名一致；不同端可共用一个 `getEnv`，无需按 PC/Mobile 再区分。

---

## 四、参考

- **移动端调起**：`bridgeRouter('ycmath://yangcong345.com/topicVideoV2', params)` / `simpleVideo` 参数见上文「一、移动端」。
- **项目内封装**：若存在，通常在 `components/VideoPlayer` 或 `commonComponents/videoPlayer` 等目录，包含 `getVideoAddressApi`、`getAddressList`、`getEnv`、`customDomainObj` 及对播放器包的调用。
- **播放器类型**：Player、PlayerOptions、Sources 等类型定义见播放器包或项目内 `yc-player.d.ts`。
- 更细的 API 字段、错误处理与埋点约定见 [reference.md](reference.md)。
