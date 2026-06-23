---
name: figma-img-cdn-skill
description: >-
  仅识别 data-name 以 img- 开头的 Figma 图层（含合成图层），整层导出为一张图并上传 CDN；
  禁止深层遍历子图层或引用 get_design_context 内子图 localhost 资源。
  按命名规则选择实现方式（img-bg- 用 CSS background，内容图用 OIImgLoad）。
  是 figma-read-skill 工作流的必经环节，**跳过会凭印象编出"原型阶段不上 CDN /
  生产化阶段才上 CDN"等不存在的分阶段路径**。

  触发条件：
  (1) 用户提供 Figma URL（含 figma.com、node-id=、123:456 节点 ID 格式），
  或要求实现 / 还原 / 开发 / 生成 / 写某个 Figma 页面或组件——必须与
  figma-read-skill 同步触发；
  (2) Figma MCP 返回节点 data-name 出现 img- / img-bg- 前缀；
  (3) 任务涉及 @guanghe-pub/yc-cdn-mcp-server 的图片上传 / CDN URL 生成；
  (4) 识别 img- 图层、合成图层切图、或生成图片 URL 映射表。

  不触发：
  (1) 与 Figma 无关的前端图片渲染 / 懒加载逻辑；
  (2) 节点 data-name 不以 img- 开头（如 bg-banner / pic-avatar / photo / IMAGE），
  即便含 fills.IMAGE 或 localhost 资源也不进入本 skill。
requires:
  - figma-read-skill  # 图片处理是 figma-read-skill 工作流的一部分，其他布局/token/验证规则遵循该 skill
  - onion-ui-skill    # 使用 OIImgLoad 组件时需查阅组件库文档
mcp:
  - figma-read-mcp                      # 【主路径】get_metadata / get_screenshot 整层导出
  - figma-write-mcp                     # 【降级/在线】download_assets 整层导出（export.url）
  - user-@guanghe-pub/yc-cdn-mcp-server  # cdn_compress_and_upload / cdn_batch_compress_and_upload（图片上传 CDN）
---

# Figma 图片资源处理 Skill

识别 Figma 设计稿中 `data-name` 以 `img-` 开头的图层，将**整层视觉**导出为一张图片资源，上传 CDN 并生成代码。

> **准入门禁：只有 `data-name` 精确以小写 `img-` 开头的节点才允许进入本 skill 的自动识别、整层导出、上传 CDN、生成 CDN URL、按 `img-bg-*` / `img-*` 规则生成代码流程。非 `img-` 前缀节点仍可能是真实图片素材，但不属于本 CDN 上传流程；如实现确实需要，可在 `figma-read-skill` 主流程中临时保存到项目 `assets` 目录并本地引用。**

## 边界原则（强制，不可违背）

> **一个 `img-` 图层 = 一张图片资源 = 一个 URL。无论图层内部是单图还是蒙版/多图合成，均按此规则处理。**

### 允许

- 遍历节点树，**仅收集** `data-name`（或 `name`）以 `img-` 开头的图层
- 对每个 `img-` 图层记录：`data-name`、`node-id`、宽高、位置
- 以该 `img-` 图层的 `node-id` 整层导出图片（见 Step 2）
- `data-name` 含 `https://` 时，直接提取链接，跳过导出与上传

### 禁止

- **禁止**进入 `img-` 图层内部，识别、下载或上传其子图层/子元素的资源
- **禁止**使用 `get_design_context` 返回代码中的 `const imgX = "http://localhost:3845/..."` 等子图常量
- **禁止**使用 `download_assets` 返回的 `rawImages` 列表映射到 `img-` 图层（只用 `export` 字段）
- **禁止**单独处理子图层内的蒙版 SVG、mask-image 引用、内部 `<img>` src
- **禁止**将子图层 localhost URL 映射到父级 `img-` 图层名
- **禁止**在输出中声称「合成图层无法一对一映射」而改用子图资源
- **禁止**为还原合成效果而在代码中复刻蒙版/翻转/多图叠加（图片阶段只交付整层导出图）

布局与样式还原仍遵循 `figma-read-skill`；**图片资源阶段**只处理 `img-` 整层导出图。

## 命名规则与实现方式

| 命名模式 | 含义 | 实现方式 |
| --- | --- | --- |
| `img-bg-xxx` | 背景图 | CSS `background` 属性 |
| `img-xxx`（不含 `bg-`） | 内容图片 | `OIImgLoad` 组件，降级为 `<img>` 标签 |

## 执行流程（必须按顺序执行）

### Step 1：识别图片图层

1. 调用 `figma-read-mcp` 的 `get_metadata`（主路径不可用时降级 `figma-write-mcp` 同名工具），在节点树中筛选 **`name` 以 `img-` 开头** 的图层（可在任意层级出现，但只认图层自身名称）
2. 对每个匹配图层记录：
   - **完整名称**：`data-name` / `name`
   - **node-id**：用于整层导出
   - **类型**：是否 `img-bg-` 开头
   - **尺寸与位置**：width、height、top、left
3. **到此为止**：不得再读取该图层下任何子节点的名称或资源

不满足 `data-name.startsWith('img-') === true` 的节点必须立即排除，禁止执行 CDN 上传、生成 CDN URL、按 `img-*` 命名规则生成代码。

可选校验：用 `get_design_context` 获取布局时，只提取带 `data-name="img-*"` 的**节点本身**的 node-id 与尺寸，**不得**解析其 JSX/HTML 子树中的图片常量。

### Step 2：整层导出图片资源（禁止用子图 URL）

对每个 `img-` 图层，**只导出该图层节点自身的渲染结果**：

1. **名称含 `https://`**（如 `img-https://xxx.com/pic.png`）→ 提取链接直接使用，跳过 Step 3
2. **其余图层** → 按优先级整层导出（**只取导出结果，忽略 `rawImages`**）：
   - **优先**：`figma-write-mcp` 的 `download_assets`：
     ```
     download_assets(
       fileKey: "<设计稿 fileKey>",
       nodeId: "<img-图层的 node-id>",
       defaultFormat: "png",
       defaultScale: 2
     )
     ```
     使用返回的 **`export.url`** 下载到本地临时文件（建议 `/tmp/figma-img/<data-name去img前缀>.png`），再进入 Step 3
   - **备选**：`figma-read-mcp` 的 `get_screenshot(nodeId: "<img-图层的 node-id>")`，将返回图片保存到上述临时路径
3. **不得**改用 `get_design_context` 内子图层的 `localhost:3845` 地址作为该 `img-` 图层的资源来源

**尺寸说明**：设计稿为 2x，导出图物理像素通常为显示尺寸的 2 倍；代码中容器宽高仍按 Figma 图层尺寸 **÷2** 设置。

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

**多张图片时**：将同一批 `img-` 整层导出文件放在同一临时目录，使用 `cdn_batch_compress_and_upload` 批量上传：

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
get_metadata 筛选 name 以 img- 开头的图层（不读子图层资源）
        │
        ├── 名称含 https://？
        │       └── 是 → 直接提取链接（跳过导出与 CDN）
        │
        └── 否 → 对每个 img- 图层 node-id 整层导出
                        │   download_assets.export.url（优先）
                        │   或 get_screenshot（备选）
                        │
                        ├── cdn_compress_and_upload / batch 上传
                        │       ├── 成功 → 一个 img- 图层对应一个 CDN URL
                        │       └── 失败 → 保存到 assets（文件名来自 data-name）
                        │
                        ├── img-bg-xxx → CSS background
                        └── img-xxx → OIImgLoad（降级 <img>）
```

## 映射表输出格式

生成本地 URL 或 CDN 映射表时，**每行只对应一个 `img-` 图层**：

| data-name | node-id | 宽×高（代码尺寸 ÷2） | URL |
|-----------|---------|---------------------|-----|

不得出现「子图层素材 URL」「蒙版 SVG URL」「rawImages URL」或「同一 URL 映射多个 img- 图层（除非用户明确要求复用）」。

## 注意事项

1. **前缀是本 CDN 流程的唯一准入条件**：不得因为节点包含图片填充、资源 URL 或视觉上像图片，就绕过 `img-` 命名门禁上传 CDN
2. **一个 img- 图层一个资源**：合成图层必须整层导出，不得拆子图
3. **尺寸缩小一倍**：代码中图片容器宽高 = Figma 图层尺寸 ÷ 2
4. **不要硬编码 CDN 地址为常量文件**：直接在使用处引用，除非同一张图多处复用
5. **上传前确认**：临时文件来自整层导出（`export.url` / `get_screenshot`），非子图 localhost 下载
6. **保持与 figma-read-skill 一致**：本 skill 的图片资源规则优先于 `figma-read-skill` 中的「切图识别」章节，其他规则（布局、组件、token 等）仍遵循 `figma-read-skill`

## 检查清单

- [ ] 是否仅识别 `name`/`data-name` 以 `img-` 开头的图层？
- [ ] 是否确认非 `img-` 前缀图片没有进入本 skill 的 CDN 上传和 CDN URL 生成流程？
- [ ] **是否未进入子图层下载或映射任何子图 / rawImages 资源？**
- [ ] **是否未使用 `get_design_context` 中的子图 localhost 常量？**
- [ ] 每个 `img-` 图层是否通过 `download_assets.export` 或 `get_screenshot(nodeId)` 整层导出？
- [ ] 映射表中是否「一行一个 img- 图层、一个 URL」？
- [ ] 是否区分了 `img-bg-` 背景图和 `img-` 内容图片？
- [ ] 是否尝试通过 CDN MCP 上传？
- [ ] 上传失败时是否降级保存到 assets（文件名来自 data-name）？
- [ ] 背景图是否使用 CSS `background`？内容图是否优先 `OIImgLoad`？
- [ ] 图片容器尺寸是否 ÷2？OIImgLoad class 是否设 width、height、object-fit？
- [ ] **生成后是否对接管页面截图并与设计稿 1:1 对比？（见 figma-read-skill）**
