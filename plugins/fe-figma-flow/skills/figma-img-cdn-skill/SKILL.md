---
name: figma-img-cdn-skill
description: >-
  Figma 设计稿中 `data-name` 以 `img-` / `img-bg-` 开头的图片图层处理：
  localhost 资源下载 → CDN MCP 上传（`cdn_compress_and_upload` /
  `cdn_batch_compress_and_upload`）→ 按命名规则生成 CSS background
  或 OIImgLoad / `<img>` 实现；上传失败降级到 `assets/`。
  是 `figma-read-skill` 工作流的必经环节，**跳过会凭印象编出"原型阶段不上 CDN /
  生产化阶段才上 CDN"等不存在的分阶段路径**。

  触发条件：
  (1) 用户提供 Figma URL（含 `figma.com`、`node-id=`、`123:456` 节点 ID 格式），
  或要求"实现 / 还原 / 开发 / 生成 / 写"某个 Figma 页面或组件——必须与
  `figma-read-skill` 同步触发；
  (2) Figma MCP 返回节点 `data-name` 出现 `img-` / `img-bg-` 前缀；
  (3) 任务涉及 `@guanghe-pub/yc-cdn-mcp-server` 的图片上传 / CDN URL 生成。

  不触发：
  (1) 与 Figma 无关的前端图片渲染 / 懒加载逻辑；
  (2) 节点 `data-name` 不以 `img-` 开头（如 `bg-banner` / `pic-avatar` /
  `photo` / `IMAGE`），即便含 `fills.IMAGE` 或 `localhost` 资源也不进入本 skill。
requires:
  - figma-read-skill  # 图片处理是 figma-read-skill 工作流的一部分，其他布局/token/验证规则遵循该 skill
  - onion-ui-skill    # 使用 OIImgLoad 组件时需查阅组件库文档
mcp:
  - figma-read-mcp                      # 【主路径】本地 Figma Desktop Dev Mode，读 img- 资源的 localhost URL
  - figma-write-mcp                     # 【降级路径】Figma 官方在线 MCP，主路径不可用时通过同名工具读取
  - user-@guanghe-pub/yc-cdn-mcp-server  # cdn_compress_and_upload / cdn_batch_compress_and_upload（图片上传 CDN）
---

# Figma 图片资源处理 Skill

识别 Figma 设计稿中 `img-` 开头的图片图层，自动上传 CDN 获取链接，并根据命名规则选择正确的代码实现方式。

> **准入门禁：只有 `data-name` 精确以小写 `img-` 开头的节点才允许进入本 skill 的自动识别、下载、上传 CDN、生成 CDN URL、按 `img-bg-*` / `img-*` 规则生成代码流程。非 `img-` 前缀节点仍可能是真实图片素材，但不属于本 CDN 上传流程；如实现确实需要，可在 `figma-read-skill` 主流程中临时保存到项目 `assets` 目录并本地引用。**

## 命名规则与实现方式

| 命名模式 | 含义 | 实现方式 |
| --- | --- | --- |
| `img-bg-xxx` | 背景图 | CSS `background` 属性 |
| `img-xxx`（不含 `bg-`） | 内容图片 | `OIImgLoad` 组件，降级为 `<img>` 标签 |

## 执行流程（必须按顺序执行）

### Step 1：识别图片图层

在 Figma MCP 返回的设计数据中，先读取节点完整 `data-name`，只筛选 `data-name.startsWith('img-') === true` 的元素进入本 skill。

不满足该条件的节点必须立即排除，禁止执行以下动作：

- 调用 `cdn_compress_and_upload` / `cdn_batch_compress_and_upload`；
- 生成或替换为 CDN URL；
- 按 `img-bg-*` / `img-*` 命名规则决定 `OIImgLoad`、`<img>` 或图片 `background` 实现方式。

反例（均不得进入本 skill 的 CDN 上传流程）：`bg-banner`、`banner-image`、`pic-avatar`、`photo`、`IMAGE`，以及任何名称不是 `img-` 开头但带有 `fills.IMAGE` 或 `localhost` 资源地址的节点。这类素材如页面还原必须使用，可在主流程中临时落到本地 `assets`。

对每个匹配的元素，记录以下信息：
- **完整名称**：`data-name` 的值
- **类型判断**：是否包含 `bg-`（即 `img-bg-` 开头）
- **元素尺寸**：width、height
- **元素位置**：top、left 等布局信息

### Step 2：获取图片资源文件

仅对 Step 1 命中的 `img-` 节点获取图片资源文件。Figma MCP 返回的图片资源通常以 `localhost` URL 形式提供。

1. 如果 `data-name` 中直接包含 `https://` 链接（如 `img-https://xxx.com/pic.png`），提取该链接直接作为图片地址使用，**跳过 Step 3 的 CDN 上传**
2. 如果 Figma MCP 返回了 `localhost` 形式的资源地址，先将文件下载到本地临时位置
   - **注意**：下载图片时默认获取 **2x 分辨率的 PNG 格式**，在后续使用时需考虑实际显示尺寸为原始设计尺寸（即图片物理像素为显示尺寸的 2 倍）
3. 根据资源内容判断文件格式（SVG / PNG / JPEG / WebP 等）

### Step 3：上传 CDN

对需要上传的本地图片文件，调用 `@guanghe-pub/yc-cdn-mcp-server` MCP 的 `cdn_compress_and_upload` 工具：

```
cdn_compress_and_upload(
  filePath: "<图片文件的绝对路径>",
  bucket: "fp",
  fileNameType: 2
)
```

**参数说明：**
- `filePath`：必填，图片文件的绝对路径
- `bucket`：使用 `fp`（图片/小文件加速）
- `fileNameType`：使用 `2`（原名称 + 文件 hash，避免缓存问题）

**多张图片时**：如果同一组件/页面有多张需要上传的图片，可以将它们放在同一个临时目录下，使用 `cdn_batch_compress_and_upload` 批量上传：

```
cdn_batch_compress_and_upload(
  folderPath: "<临时目录的绝对路径>",
  bucket: "fp",
  fileNameType: 2
)
```

**上传成功**：使用返回的 CDN URL 作为图片地址，然后**删除本地临时文件/临时目录**，避免残留。

**上传失败（降级处理）**：
1. 将文件保存到当前项目的 `assets` 目录下
2. 文件名从 `data-name` 中提取（去掉 `img-` 或 `img-bg-` 前缀）
3. 根据文件实际格式保存为对应后缀：`.svg`、`.png`、`.jpeg`、`.webp` 等
4. 在代码中使用相对路径引用

**降级保存示例：**
- `img-bg-banner` → `assets/banner.png`
- `img-avatar` → `assets/avatar.png`
- SVG 格式资源 → `assets/xxx.svg`

### Step 4：根据命名规则生成代码

#### 4a. 背景图（`img-bg-` 开头）

当 `data-name` 以 `img-bg-` 开头时，该元素是背景图，必须使用 CSS `background` 属性实现。

**CDN 链接可用时：**

```scss
.banner {
  background: url('https://fp.yangcong345.com/xxx/banner.png') no-repeat center / cover;
}
```

**降级到本地文件时：**

```scss
.banner {
  background: url('@/assets/banner.png') no-repeat center / cover;
}
```

**注意事项：**
- 背景图容器必须设置明确的宽高（从 Figma 数据中获取，注意尺寸缩小一倍）
- 根据设计稿选择合适的 `background-size`：`cover`（铺满）、`contain`（完整显示）或具体尺寸
- 根据设计稿选择合适的 `background-position`

#### 4b. 内容图片（`img-` 开头，不含 `bg-`）

当 `data-name` 以 `img-` 开头但不包含 `bg-` 时，优先使用 `OIImgLoad` 组件。

**第一步：查询组件库**

读取 `onion-ui-skill`，按其中的版本确认与 README 访问规则，查询 `OIImgLoad` 组件是否存在及其用法。

**如果 OIImgLoad 组件存在：**

> **重要：OIImgLoad 的宽高等样式必须通过 class 设置，禁止使用内联 props 或 style 设置尺寸**

> **防止尺寸异常**：为 OIImgLoad 的 class 必须同时设置 **width、height、object-fit**（如 `contain` 或 `cover`），否则图片可能按原始尺寸显示导致溢出或比例错误。尺寸来自 Figma 元素且需缩小一倍。

```vue
<template>
  <OIImgLoad
    :src="imgUrl"
    class="img-avatar"
  />
</template>

<script setup lang="ts">
import { OIImgLoad } from '@guanghe-pub/onion-ui'

const imgUrl = 'https://fp.yangcong345.com/xxx/avatar.png'
</script>
```

```scss
.img-avatar {
  width: 48px;
  height: 48px;
  object-fit: contain; /* 或 cover，与设计稿一致 */
}
```

**如果 OIImgLoad 组件不存在（降级为 `<img>` 标签）：**

```vue
<template>
  <img
    :src="imgUrl"
    class="img-avatar"
    alt="avatar"
  />
</template>

<script setup lang="ts">
const imgUrl = 'https://fp.yangcong345.com/xxx/avatar.png'
</script>
```

```scss
.img-avatar {
  width: 48px;
  height: 48px;
  object-fit: cover;
}
```

**降级到本地文件时：**

```vue
<script setup lang="ts">
import avatarImg from '@/assets/avatar.png'
</script>

<template>
  <OIImgLoad :src="avatarImg" class="img-avatar" />
  <!-- 或降级 -->
  <img :src="avatarImg" class="img-avatar" alt="avatar" />
</template>
```

```scss
.img-avatar {
  width: 48px;
  height: 48px;
  object-fit: contain; /* 或 cover */
}
```

## 完整处理流程图

```
读取完整 data-name
        │
        ├── 以 img- 开头？
        │       ├── 否 → 退出本 skill，不上传 CDN；必要时由主流程临时保存到 assets
        │       └── 是 → 进入图片资源流程
        │               │
        │               ├── 名称中包含 https:// 链接？
        │               │       ├── 是 → 直接提取链接使用（跳过 CDN 上传）
        │               │       └── 否 → 下载 Figma localhost 资源到本地
        │               │                       │
        │               │                       ├── 调用 cdn_compress_and_upload 上传
        │               │                       │       ├── 成功 → 使用 CDN URL
        │               │                       │       └── 失败 → 保存到 assets 目录，使用本地路径
        │               │
        │               ├── img-bg-xxx？
        │               │       └── 是 → 使用 CSS background 属性
        │               │
        │               └── img-xxx（非 bg-）？
        │                       └── 是 → 查询 OIImgLoad 组件
        │                               ├── 存在 → 使用 OIImgLoad
        │                               └── 不存在 → 降级使用 <img> 标签
```

## 注意事项

1. **前缀是本 CDN 流程的唯一准入条件**：不得因为节点包含图片填充、资源 URL 或视觉上像图片，就绕过 `img-` 命名门禁上传 CDN
2. **尺寸缩小一倍**：Figma 设计稿是 2 倍尺寸，代码中图片容器的宽高需要除以 2
3. **不要硬编码 CDN 地址为常量文件**：直接在使用处引用，除非同一张图多处复用
4. **SVG 特殊处理**：如果图片资源是 SVG 格式且需要动态变色，优先保存为 `.svg` 文件并使用内联方式引入，而非作为普通图片
5. **上传前确认**：调用 CDN 上传前，确保文件已完整下载且格式正确，且来源节点 `data-name` 以 `img-` 开头
6. **保持与 figma-read-skill 一致**：本 skill 的图片处理逻辑优先级高于 figma-read-skill 中的「切图识别」章节，其他规则（布局、组件、token 等）仍遵循 figma-read-skill

## 检查清单

- [ ] 是否正确识别了所有 `img-` 开头的图层？
- [ ] 是否确认所有进入本 skill 自动识别 / CDN 上传 / CDN URL 生成流程的节点，`data-name` 都以 `img-` 开头？
- [ ] 是否确认非 `img-` 前缀图片没有进入本 skill 的 CDN 上传和 CDN URL 生成流程？
- [ ] 是否区分了 `img-bg-` 背景图和 `img-` 内容图片？
- [ ] 是否尝试通过 CDN MCP 上传图片？
- [ ] 上传失败时是否正确降级保存到 assets 目录？
- [ ] 背景图是否使用了 CSS `background` 属性？
- [ ] 内容图片是否优先使用了 `OIImgLoad` 组件？
- [ ] `OIImgLoad` 不可用时是否降级为 `<img>` 标签？
- [ ] 图片尺寸是否缩小了一倍？
- [ ] **OIImgLoad 的 class 是否同时设置了 width、height、object-fit（contain/cover）？**
- [ ] **生成后是否对接管页面截图并与设计稿 1:1 对比验证？（见 figma-read-skill 生成后验证步骤）**
