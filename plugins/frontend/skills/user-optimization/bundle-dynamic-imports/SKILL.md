---
name: bundle-dynamic-imports
description: 重型组件动态导入
---

## 用动态导入拆分重型组件

把首屏不需要的"重型组件"用 `defineAsyncComponent` 懒加载，让它们各自变成独立的 chunk，**不再随主包下发、解析、执行**。这是降低 TTI（Time To Interactive）和 LCP（Largest Contentful Paint）最直接的手段之一。

> **"重型"的判断标准**：单组件 gzip 体积 ≥ 50KB，或带有 Monaco / ECharts / 富文本编辑器 / Canvas+WebGL / PDF 预览 / 大体积静态数据等依赖。低于 ~30KB gzip 的小组件**不要拆**——动态导入引入的额外请求 + chunk 拆分元数据反而会拖慢首屏。

**反例（Monaco 直接打进主 chunk，约 +300KB）：**

```vue
<script setup lang="ts">
import MonacoEditor from './MonacoEditor.vue'
</script>

<template>
  <MonacoEditor :value="code" />
</template>
```

哪怕用户从未触达编辑器，整个 Monaco 也会进入主 bundle，参与 parse / compile / execute，每一步都会阻塞首屏。

**正例（Monaco 按需加载，并交代 loading / error 行为）：**

```vue
<script setup lang="ts">
import { defineAsyncComponent } from 'vue'
import EditorSkeleton from './EditorSkeleton.vue'
import EditorError from './EditorError.vue'

const MonacoEditor = defineAsyncComponent({
  loader: () => import('./MonacoEditor.vue'),
  loadingComponent: EditorSkeleton,
  errorComponent: EditorError,
  delay: 200,        // 200ms 内加载完不显示 loading，避免闪烁
  timeout: 10_000,   // 10s 超时，触发 errorComponent
  onError(error, retry, fail, attempts) {
    if (attempts <= 2) retry()
    else fail()
  },
})
</script>

<template>
  <MonacoEditor :value="code" />
</template>
```

要点：

- **`delay`** 防止快网络下"骨架闪一下立刻消失"的视觉抖动。
- **`onError` + `retry`** 处理偶发的 chunk 加载失败（弱网、CDN 抖动），比让用户看到一个白屏更可靠。
- 把 `loadingComponent` / `errorComponent` 拆成独立组件，避免它们也进懒加载 chunk。

**chunk 命名（便于排查 bundle）：**

给动态 import 加上注释，DevTools / `rollup-plugin-visualizer` 里就能直接看到这个 chunk：

```ts
const MonacoEditor = defineAsyncComponent(
  () => import(/* webpackChunkName: "monaco-editor" */ './MonacoEditor.vue')
)
```

Vite 5+ 也支持等价的 `/* @vite-chunk-name: monaco-editor */`。

**适用场景：**

- 首屏不需要、由用户交互或路由切换才会进入视口的重组件（编辑器、图表、富文本、地图、3D / Canvas）。
- 体积明显大于业务组件、且依赖一长串子模块的"独立功能模块"。
- 仅少数用户/路径会用到的弹窗、设置面板、调试工具等。
- 配合 `bundle-preload` 在 `mouseenter` / `focus` / 路由 prefetch 时**提前**触发 import，可以把首字节延迟降到接近零（推荐组合使用）。

**不适合此模式的场景：**

- 首屏必现的核心组件（Header / 主要内容区 / SEO 关键内容）——拆出去会引入额外网络往返，反而拖慢 LCP。
- gzip 体积 < 30KB 的小组件——chunk 元数据 + 请求开销可能比直接打进主包更贵。
- 同一组件在多个路由都被立即使用——拆完之后命中率高、缓存好，但要注意它已经不算"按需"，可以考虑用普通 import 让它进入共享 vendor chunk。
