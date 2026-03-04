# Onion Video 参考

## 一、移动端 bridge 参数

### topicVideoV2

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| topicId | string | 是 | 知识点 ID |
| itemId | string | 是 | 内容项 ID |
| taskId | string | 是 | 任务 ID |
| courseId | string | 否 | 专项课 ID，无则传 '' |
| completeUrl | string | 是 | 完成页 URL 的 Base64 |
| statistics | string | 是 | JSON 字符串，含 topicId/taskId/measuringId/itemId |
| playRangeStart | number | 否 | 片段起始秒 |
| playRangeEnd | number | 否 | 片段结束秒 |
| enableAISummarize | boolean | 否 | 是否开启 AI 总结 |

### simpleVideo

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| itemId | string | 是 | 内容项 ID |
| taskId | string | 是 | 任务 ID |
| videoUrl | string | 是 | 视频地址的 Base64 |
| completeUrl | string | 是 | 完成页 URL 的 Base64 |
| statistics | string | 是 | JSON 字符串 |
| playRangeStart | number | 否 | 片段起始秒 |
| playRangeEnd | number | 否 | 片段结束秒 |

---

## 二、getVideoAddressApi

### 请求（AI 课堂 / padh5 移动端）

- **URL**：`POST ${schoolDomain}/teacher-ai-class/video/addresses`
- **Body**：`{ videoList: [{ videoId: string, custom: Record<string, string> }] }`
- **custom** 常用：`{ topicId }` 或 `{ topicId, ... }`

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

- 地址：用 `videoList[0].address`，H5 常用 `platform === 'mobile' && format === 'hls'`，转成 YcPlayer 的 `sources`（url → src，type 为 `application/x-mpegURL`）。

---

## 三、YcPlayer 选项要点

- **env**：`'production' | 'stage' | 'test'`，与后端域名一致。
- **customDomainObj**：`{ test, stage, production }` 对应 API 域名。
- **sources**：`{ src, type?, clarity }[]`，如 `{ src: url, type: 'application/x-mpegURL', clarity: '高清' }`。
- **videoId**：业务视频 ID，埋点用。
- **buryPointParams**：`{ videoScene, extraParams }` 等，按业务传。
- **textTrack**：外挂字幕 URL（.vtt），需先通过 sign 接口取可访问 URL 再传入。
- 事件：`on('ended' | 'timeupdate' | 'firstplay' | ...)`，销毁前 `off` 并 `dispose()`。

---

## 四、环境与域名

- **getEnv()**：根据项目 `isPROD`、`isStage` 等返回 `production | stage | test`。
- **customDomainObj** 示例：  
  test: `https://schoolcourse-api-test.yangcong345.com`  
  stage: `https://schoolcourse-api-stage.yangcong345.com`  
  production: `https://schoolcourse-api.yangcong345.com`
- PC 与 Mobile 共用同一 env 与域名配置即可。

---

## 五、动态加载 YcPlayer（CDN）

- **JS**：`https://fp.yangcong345.com/middle/1.0.10/yc-player.js`（加载后挂到 `window.YcPcPlayer`）。
- **CSS**：`https://fp.yangcong345.com/middle/1.0.10/yc-player.min.css`。
- 单例：全局只加载一次，后续直接使用 `window.YcPcPlayer`。

---

## 六、类型（yc-player.d.ts 要点）

- **Player**：`dispose`、`on/off`、`play/pause`、`currentTime`、`getPlayingTime`、`duration`、`volume` 等。
- **PlayerOptions**：`env`、`sources`、`videoId`、`customDomainObj`、`buryPointParams`、`textTrack`、`keyPoints`、`startTime`、`guide`、`fullScreenButton` 等。
- **Sources**：`src`、`type`、`clarity`、`default?`。
