---
name: bundle-preload
description: 降低感知延迟

---

## 基于用户意图预加载

`bundle-dynamic-imports` 把重型组件拆出主包之后，**首次**触发它的用户依然要等一段下载/解析时间。**预加载**就是在用户*即将*触发它之前抢跑这次下载——常见的"用户即将触发"信号是：把鼠标移到按钮上、键盘 focus 到入口、链接进入视口、特性开关刚刚被命中——把"第一次点击"的等待拉低到接近零。

> 本规则是 `bundle-dynamic-imports` 的搭档。如果你还没把重组件拆成独立 chunk，先去拆；拆完之后再用本规则把"第一次交互卡顿"抹平。预加载**不减少**总下载量，它只把下载提前到用户感知不到的窗口里。

**反例（重组件已拆，但首次交互必定卡顿）：**

```vue
<script setup lang="ts">
import { defineAsyncComponent, ref } from 'vue'

const MonacoEditor = defineAsyncComponent(() => import('./MonacoEditor.vue'))
const open = ref(false)
</script>

<template>
  <button @click="open = true">打开编辑器</button>
  <MonacoEditor v-if="open" />
</template>
```

用户**点了按钮**才开始下载几百 KB 的 Monaco chunk，骨架屏要转好几秒——交互意图明明早就出现了（hover、focus），却没有被利用。

**正例 1（hover / focus / 触摸时预加载）：**

```vue
<script setup lang="ts">
import { defineAsyncComponent, ref } from 'vue'

const MonacoEditor = defineAsyncComponent(() => import('./MonacoEditor.vue'))
const open = ref(false)

function preload() {
  if (!import.meta.client) return
  void import('./MonacoEditor.vue')
}
</script>

<template>
  <button
    @pointerenter="preload"
    @focus="preload"
    @click="open = true"
  >
    打开编辑器
  </button>
  <MonacoEditor v-if="open" />
</template>
```

要点：

- **`import('./MonacoEditor.vue')` 在打包器/浏览器层面就是去重的**——同一 specifier 的多次 dynamic import 共享同一个 module promise，多次 hover 只会触发一次真实下载，不需要手动加 `loaded.value` 锁。预加载之后用户点击触发的 `defineAsyncComponent` loader 也会复用这个 promise，不会重复拉取。
- **用 `@pointerenter` 而不是 `@mouseenter`**，可以同时覆盖鼠标和触摸输入。`@mouseenter` 在移动端几乎不会触发，导致触摸用户拿不到任何预加载收益。
- **`@focus` 覆盖键盘可达性场景**：用 Tab 走读页面的用户、辅助技术用户也能享受预加载。

**正例 2（feature flag 命中时预加载）：**

```ts
import { watch } from 'vue'
import type { Ref } from 'vue'

interface Flags { editorEnabled: boolean }

export function useFlagsBootstrap(flags: Ref<Flags>) {
  watch(
    () => flags.value.editorEnabled,
    (enabled) => {
      if (enabled && import.meta.client) {
        void import('./monaco-editor').then(mod => mod.init())
      }
    },
    { immediate: true },
  )
}
```

要点：

- **不要用 `watchEffect`**——它会订阅 `flags.value` 上**任何**字段的变化，无关字段抖动也会重跑这段逻辑，可能多次触发 `mod.init()`。改成显式依赖 `() => flags.value.editorEnabled` 的 `watch` 更精确。
- **`{ immediate: true }`** 让"页面打开时 flag 已经为 true"的情形也能预加载，不用等下一次变化。

**适用场景：**

- 已经做了 `defineAsyncComponent` / `next/dynamic` / 路由级懒加载的重组件（编辑器、图表、地图、富文本、3D / Canvas / WebGL）
- 用户路径上的"下一步"——按钮、链接、卡片、菜单项
- 特性开关刚命中、即将渲染对应组件
- 需要键盘可达性的入口（focus 触发预加载）

**不适合 / 慎用此模式：**

- **小组件（< 30KB gzip）**：预加载省下的时间还不够支付额外网络往返的开销，直接打进主包反而更划算。
- **大概率不会被触达的入口**：例如"高级设置"页面深处的按钮，hover 命中率低，预加载等于空耗带宽。
- **流量敏感、弱网场景**：预加载会和首屏关键资源抢占带宽和 HTTP/2 并发槽位，移动端尤其明显。建议结合 `navigator.connection.saveData` / `effectiveType === 'slow-2g' | '2g'` 判断后跳过预加载。
- **极重 chunk（> 1MB）**：考虑 hover 后再延后 100~300ms（用 `setTimeout` + `pointerleave` 取消）再触发，避免短停留误触造成大流量浪费。
- **首屏必现的核心组件**：本来就该同步打进主包，谈不上"预"加载。
