# Onion Video 参考

面向按需加载：实现细节、完整示例与参数表。`SKILL.md` 只保留决策流程时阅读本节对应小节。

## 目录

- [一、移动端 bridgeRouter（智课 / 学习工具）](#一移动端-bridgerouter智课--学习工具)
- [二、H5：Vue / React 示例](#二h5vue--react-示例)
- [三、getVideoAddressApi](#三getvideoaddressapi)
- [四、YcPlayer 选项要点](#四ycplayer-选项要点)
- [五、环境与域名](#五环境与域名)
- [六、动态加载 YcPlayer（CDN）](#六动态加载-ycplayercdn)
- [七、类型（yc-player.d.ts 要点）](#七类型yc-playerdts-要点)

---

## 一、移动端 bridgeRouter（智课 / 学习工具）

通过 `@guanghe-pub/onion-utils` 的 `bridgeRouter` 调起原生能力，H5 内不渲染播放器。**智课与学习工具不是同一套地址与约定**，接错会跳转失败或参数不匹配。

### 0. 先定业务线（不确定则让用户选）

| 业务线 | 说明 |
|--------|------|
| **智课** | 课内知识点、校本 simple 等，见下「智课」三套路由 |
| **学习工具** | 学习工具 App 内场景，见下「学习工具」；**优先用 `ycplayer` 模块化** |

若仓库、需求、路由均无法判断：先问用户 **「当前是智课还是学习工具？」** 再写 `bridgeRouter` 第一参数与入参。

以下示例里 `ycmath://yangcong345.com/...` 为与既有智课一致的写法；**若项目里已有 bridge 常量（含学习工具专用前缀或 path），以仓库为准**。

---

### 1. 智课

包含：`topicVideoV2`、`simpleVideo`、旧版 `topicVideo`。

#### topicVideoV2

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| topicId | string | 是 | 知识点 ID |
| itemId | string | 是 | 内容项 ID |
| taskId | string | 是 | 任务 ID |
| courseId | string | 否 | 专项课 ID，无则传 `''` |
| completeUrl | string | 是 | 完成页 URL 的 Base64 |
| statistics | string | 是 | JSON 字符串，含 topicId/taskId/measuringId/itemId |
| playRangeStart | number | 否 | 片段起始秒 |
| playRangeEnd | number | 否 | 片段结束秒 |
| enableAISummarize | boolean | 否 | 是否开启 AI 总结 |

```ts
import { bridgeRouter } from '@guanghe-pub/onion-utils'

bridgeRouter('ycmath://yangcong345.com/topicVideoV2', {
  topicId,
  itemId,
  taskId,
  courseId: courseId || '',
  completeUrl: btoa(`${host}/path/to/completePage?${query}`),
  statistics: JSON.stringify({ topicId, taskId, measuringId, itemId }),
  playRangeStart?: number,
  playRangeEnd?: number,
  enableAISummarize?: boolean,
})
```

#### simpleVideo

先取播放地址，再调起；`videoUrl` 需 Base64。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| itemId | string | 是 | 内容项 ID |
| taskId | string | 是 | 任务 ID |
| videoUrl | string | 是 | 视频地址的 Base64 |
| completeUrl | string | 是 | 完成页 URL 的 Base64 |
| statistics | string | 是 | JSON 字符串 |
| playRangeStart | number | 否 | 片段起始秒 |
| playRangeEnd | number | 否 | 片段结束秒 |

```ts
const res = await getSchoolVideoPlayUrlApi(itemId)
const videoUrl = res.url

bridgeRouter('ycmath://yangcong345.com/simpleVideo', {
  itemId,
  taskId,
  videoUrl: base64Encode(videoUrl),
  completeUrl: btoa(`${schoolH5Host}/path/to/completePage?${query}`),
  statistics: JSON.stringify({ /* ... */ }),
  playRangeStart?: number,
  playRangeEnd?: number,
})
```

#### topicVideo（旧版）

参数较少，部分学习页仍在使用。

```ts
bridgeRouter('ycmath://yangcong345.com/topicVideo', {
  topicId,
  taskId,
  groupId,
  pageFrom: 'video',
})
```

---

### 2. 学习工具

路径名（path）与智课不同；**同一业务线内优先使用模块化 `ycplayer`**，其余为兼容/旧方案。

#### 2.1 `/ycplayer`（模块化播放器，推荐）

**参数约定**：业务参数先组装为对象 → `JSON.stringify` → `toBase64`（来自 `@guanghe-pub/onion-utils`），再通过 **`base64param`** 传给原生。

**两种调用方式（二选一，与项目现有封装一致即可）**：
```ts
// 方式一：统一走 bridgeRouter，第一参数为 bridgeRouter 能力
import { bridgeRouter, toBase64 } from '@guanghe-pub/onion-utils'

const param = {
  businessModules: {
    name: 'simple',
    param: {
      videoId,
    },
  },
  videoBuildParam: {
    pluginConfigs: {
      isUseSubtitle: true,
    },
  },
}
const encstr = toBase64(JSON.stringify(param))
bridgeRouter('ycmath://yangcong345.com/bridgeRouter', { base64param: encstr })
```

```ts
// 方式二：直接调原生能力名 ycplayer（若 `callNative` 由项目内其它模块导出，则改 import 路径）
import { callNative, toBase64 } from '@guanghe-pub/onion-utils'

const param = {
  businessModules: {
    name: 'simple',
    param: {
      videoId,
    },
  },
  videoBuildParam: {
    pluginConfigs: {
      isUseSubtitle: true,
    },
  },
}
const encstr = toBase64(JSON.stringify(param))
callNative('ycplayer', { base64param: encstr })
```

- **字段说明（摘要）**：`businessModules` 表示业务模块与子参；`videoBuildParam.pluginConfigs` 等用于播放器构建（如字幕开关）。完整字段与可选 `name` 取值见飞书文档。
- **注意**：`toBase64`、第一参数 URL、是否使用 `callNative` 均以 **App / H5 仓库内既有实现** 为准；新页面应对照同仓库其它 `ycplayer` / `bridgeRouter` 调用处。

- **说明文档**：[学习工具 ycplayer 模块化播放器](https://guanghe.feishu.cn/docx/K32Cd2YCWo1XBexwLkOcnwHLngb)（飞书）；**更多模块名、`businessModules` 形态以飞书与仓库为准**。

#### 2.2 `/browserCommonPlayer`（简单播放器，不推荐）

通用「直给 URL」类播放；参数如下（类型以客户端实现为准，必要时对仓库内调用处）。

| 参数 | 说明 |
|------|------|
| `problemId` | 问题 id |
| `videoScene` | 视频场景 |
| `nextStepUrl` | 播放完成后跳转下一页的 URL |
| `courseId` | 课程 id |
| `statistics` | 统计参数 |
| `videoURL` | 视频地址 |
| `videoId` | 视频 id；**播放加密视频时必传** |
| `videoTitle` | 视频标题 |
| `videoType` | 视频类型 |
| `showBackTitle` | 是否显示返回按钮 |
| `showStatusBar` | 是否显示状态栏 |
| `showJumpButton` | 是否显示跳过按钮 |
| `supportPopup` | 弹窗相关 |
| `startPosition` | 续播时间（秒） |

```ts
import { bridgeRouter } from '@guanghe-pub/onion-utils'

bridgeRouter('ycmath://yangcong345.com/browserCommonPlayer', {
  problemId,
  videoScene,
  nextStepUrl,
  courseId,
  statistics: JSON.stringify({ /* ... */ }),
  videoURL,
  videoId,
  videoTitle,
  videoType,
  showBackTitle,
  showStatusBar,
  showJumpButton,
  supportPopup,
  startPosition,
})
```

#### 2.3 `/studyWithTopicModel`（知识点播放器，不推荐）

- **入参**：章节/知识点相关视频信息对象（字段以业务与客户端约定为准，常见为「章节视频信息」结构）。
- **示例占位**（具体 key 以项目为准）：

```ts
bridgeRouter('ycmath://yangcong345.com/studyWithTopicModel', {
  // 章节视频信息等，与产品/客户端对齐
})
```

---

## 二、H5：Vue / React 示例

先确认项目内是否已有 `VideoPlayer` 封装（搜索 `getVideoAddressApi`、`getAddressList`）。有则优先用封装；无则按下述直接接播放器包。

### Vue（含封装示例）

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
import VideoPlayer from '@/components/VideoPlayer/index.vue'
</script>
```

无封装时二选一：

- **`@guanghe/yc-player`**：命令式，在容器 DOM 上 `YcPlayer(el, options)`。
- **`@guanghe/yc-pc-player-vue`**：声明式组件，`options` 形状与 React 版 `@guanghe/yc-pc-player-react` 的 `options` 一致；官方示例里初始化事件为 **`@Init`（大写 I）**，回调入参可能是 `Player` 或 `Promise<Player>`，建议 `const p = await Promise.resolve(player)` 再 `p.on('ended', ...)`。

`@guanghe/yc-player` 示例：

```ts
import YcPlayer, { Player } from '@guanghe/yc-player'
import '@guanghe/yc-player/dist/yc-player.min.css'

const address = await getVideoAddressApi(videoId, topicId)
const sources = getAddressList(address)
playerRef.value = await YcPlayer(containerEl, {
  env: getEnv(),
  fluid: true,
  videoId,
  sources,
  customDomainObj,
  buryPointParams: { /* ... */ },
  keyPoints: [],
  startTime: 0,
})
playerRef.value.on('ended', handleEnd)
// playerRef.value?.dispose()
```

`@guanghe/yc-pc-player-vue` 示例（`options` 在拉到地址后再赋值，避免首屏无 `sources`）：

```vue
<template>
  <YcPcPlayer
    v-if="playerOptions"
    :options="playerOptions"
    @Init="onPlayerInit"
  />
</template>

<script setup>
import { ref, onMounted } from 'vue'
import YcPcPlayer from '@guanghe/yc-pc-player-vue'
import '@guanghe/yc-pc-player-vue/dist/yc-pc-player.min.css'

const videoId = '...'
const topicId = '...'
const playerOptions = ref(null)

async function onPlayerInit(player) {
  const p = await Promise.resolve(player)
  p.on('ended', handleEnd)
}

onMounted(async () => {
  const address = await getVideoAddressApi(videoId, topicId)
  playerOptions.value = {
    env: getEnv(),
    fluid: true,
    videoId,
    sources: getAddressList(address),
    customDomainObj,
    buryPointParams: { /* ... */ },
    keyPoints: [],
    startTime: 0,
  }
})
</script>
```

### React（含封装示例）

部分仓库里封装 prop 名为历史拼写 `autoGetAddrss` / `onUplodaProcess`，**以当前项目代码为准**。

```tsx
import VideoPlayer from '@/commonComponents/videoPlayer/index'

<VideoPlayer
  fluid
  autoGetAddress={true}
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

无封装时：

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

---

## 三、getVideoAddressApi

### 请求（AI 课堂 / padh5 移动端）

- **URL**：`POST ${schoolDomain}/teacher-ai-class/video/addresses`
- **Body**：`{ videoList: [{ videoId: string, custom: Record<string, string> }] }`
- **custom** 常用：`{ topicId }`

### 请求（PC / 智慧学习）

- **URL**：`POST ${secondHostDomain}/teacher-ee/v2/video/addresses`
- **Body**：同上
- **Header**：`client-category: 'pc' | 'wisdom'` 等

### 响应结构

```ts
{
  videoList: [{
    address: Array<{ clarity, format, platform, url, ... }>,
    custom: { authorization: boolean, videoId?: string },
    videoId?: string
  }],
  playerVersion?: string
}
```

H5 常用过滤：`platform === 'mobile' && format === 'hls'`，再经 `getAddressList` 转为 `sources`（`url` → `src`，`type: 'application/x-mpegURL'` 等）。具体域名与路径以当前项目为准。

---

## 四、YcPlayer 选项要点

- **env**：`'production' | 'stage' | 'test'`，与后端域名一致。
- **customDomainObj**：`{ test, stage, production }` 对应 API 域名。
- **sources**：`{ src, type?, clarity }[]`。
- **videoId**：业务视频 ID，埋点用。
- **buryPointParams**：`{ videoScene, extraParams }` 等。
- **textTrack**：外挂字幕（.vtt），需先经 sign 等接口得到可访问 URL。
- 事件：`on('ended' | 'timeupdate' | 'firstplay' | ...)`；销毁前 `off` 并 `dispose()`。

---

## 五、环境与域名

- **getEnv()**：根据项目 `isPROD`、`isStage` 等返回 `production | stage | test`。
- **customDomainObj** 示例：  
  test: `https://schoolcourse-api-test.yangcong345.com`  
  stage: `https://schoolcourse-api-stage.yangcong345.com`  
  production: `https://schoolcourse-api.yangcong345.com`  
- PC 与 Mobile 共用同一 env 与域名配置即可。

---

## 六、动态加载 YcPlayer（CDN）

- **JS**：`https://fp.yangcong345.com/middle/1.0.10/yc-player.js`（`window.YcPcPlayer`）。
- **CSS**：`https://fp.yangcong345.com/middle/1.0.10/yc-player.min.css`。
- 全局只加载一次，后续复用 `window.YcPcPlayer`。

---

## 七、类型（yc-player.d.ts 要点）

- **Player**：`dispose`、`on/off`、`play/pause`、`currentTime`、`getPlayingTime`、`duration`、`volume` 等。
- **PlayerOptions**：`env`、`sources`、`videoId`、`customDomainObj`、`buryPointParams`、`textTrack`、`keyPoints`、`startTime`、`guide`、`fullScreenButton` 等。
- **Sources**：`src`、`type`、`clarity`、`default?`。
