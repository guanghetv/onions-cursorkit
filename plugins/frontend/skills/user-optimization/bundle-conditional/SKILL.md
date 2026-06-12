---
name: bundle-conditional
description: 仅在需要时才加载大体积数据
---

## 仅在功能启用时才加载模块

只有当某个功能真正被用户开启时，才加载它依赖的大体积数据或模块。把这部分代码留在初始 bundle 里，会让 99% 不开启该功能的用户也付出下载/解析的代价。

**反例（动画帧数据被无条件打进首包）：**

```vue
<script setup lang="ts">
import { frames } from './animation-frames.js' // ❌ ~200KB 永远进首包
import Canvas from './Canvas.vue'

defineProps<{ enabled: boolean }>()
</script>

<template>
  <Canvas v-if="enabled" :frames="frames" />
</template>
```

即便用户从不开启动画，`animation-frames.js` 也会被打进主 chunk 并参与解析，TTI/LCP 都会被拖累。

**正例（按需加载，仅启用时拉取）：**

```vue
<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import type { Frame } from './animation-frames'
import Canvas from './Canvas.vue'
import Skeleton from './Skeleton.vue'

const props = defineProps<{ enabled: boolean }>()
const emit = defineEmits<{ 'update:enabled': [value: boolean] }>()

const frames = ref<Frame[] | null>(null)

async function loadFrames() {
  if (frames.value !== null || !import.meta.client) return
  try {
    const mod = await import('./animation-frames.js')
    frames.value = mod.frames
  } catch (err) {
    console.error('[animation] failed to load frames', err)
    emit('update:enabled', false)
  }
}

onMounted(() => {
  if (props.enabled) loadFrames()
})

watch(() => props.enabled, (enabled) => {
  if (enabled) loadFrames()
})
</script>

<template>
  <template v-if="enabled">
    <Skeleton v-if="frames === null" />
    <Canvas v-else :frames="frames" />
  </template>
</template>
```

要点：

- **`enabled` 为 false 时不渲染任何加载占位**，避免出现"功能没开却一直转圈"的视觉假象。
- **`frames === null` 显式判空**比 `!frames` 更准确，避免把空数组误判为"未加载"。
- **加载失败时输出错误并回退**，既给用户兜底（关掉功能），也给开发者留下排查线索。

**适用场景：**

- 功能开关（A/B 实验、灰度、付费功能）控制下的重型逻辑
- 后台/管理面板等绝大多数用户不会进入的页面模块
- 仅在特定交互路径触发的图表、富文本、地图、Canvas/WebGL 等
- 大体积静态数据（动画帧、字典、规则集、教学步骤）

**不适合此模式的场景：**

- 首屏关键内容、SEO 必需内容（应同步渲染）
- 体量很小（< 10KB gzip）的模块——动态导入的 chunk 拆分与请求开销可能反而更大
- 用户几乎一定会用到的功能——按需加载只会增加一次额外的网络往返
