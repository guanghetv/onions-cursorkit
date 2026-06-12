---
name: rerender-transitions
description: 保持 UI 响应流畅
---

## 非紧急更新使用节流/防抖或 idle 调度

**"高频、非紧急的更新不要阻塞主线程"**——在 Vue 里完全可以做到，只是组合用的工具不一样：

- **`requestAnimationFrame`**：让更新与浏览器渲染节奏对齐，每帧最多一次
- **`requestIdleCallback`**：浏览器空闲时再执行非关键任务
- **节流（throttle）**：高频事件按时间间隔批处理，对应 VueUse `useThrottleFn` / `refThrottled`
- **防抖（debounce）**：连续触发后只执行最后一次，对应 VueUse `useDebounceFn` / `refDebounced`

下面按"事件回调级"和"响应式派生级"两条线给出落地方式。两条线可以叠加：在事件入口做一层节流，在派生 ref 上再做一层防抖。

### 反例（scroll 监听里没有任何节流）

```vue
<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

const scrollY = ref(0)

function onScroll() {
  scrollY.value = window.scrollY
}

onMounted(() => window.addEventListener('scroll', onScroll, { passive: true }))
onUnmounted(() => window.removeEventListener('scroll', onScroll))
</script>
```

`{ passive: true }` 解决了"handler 阻塞滚动"，但**每次 scroll 事件仍然会同步写一次 ref**——快速滚动时一帧内可能触发 5~10 次响应式更新，订阅 `scrollY` 的组件都会跟着重渲染，主线程瞬间被打满。

### 正例 1（与渲染节奏对齐：requestAnimationFrame）

`ticking` 锁保证一帧内只排一次 RAF；卸载时取消挂起的回调，避免组件已经销毁还触发一次脏写。事件监听用

```vue
<script setup lang="ts">
import { ref, onUnmounted } from 'vue'
import { useEventListener } from '@vueuse/core'

const scrollY = ref(0)
let ticking = false
let rafId = 0

useEventListener(window, 'scroll', () => {
  if (ticking) return
  ticking = true
  rafId = requestAnimationFrame(() => {
    scrollY.value = window.scrollY
    ticking = false
  })
}, { passive: true })

onUnmounted(() => cancelAnimationFrame(rafId))
</script>
```

### 正例 2（推荐：VueUse 内置滚动/指针 hook）

VueUse 的 `useScroll` / `useMouse` / `useElementBounding` 内部已经做了 RAF/节流，组件层不用再手写：

```vue
<script setup lang="ts">
import { useScroll } from '@vueuse/core'

const { y: scrollY } = useScroll(window, { throttle: 100 })
</script>
```

业务里 90% 的滚动/指针/尺寸订阅都该走这条路，只有 VueUse 没覆盖的事件才需要回到正例 1。

### 正例 3（事件回调节流/防抖：useThrottleFn / useDebounceFn）

`useThrottleFn` / `useDebounceFn` 把任意函数包装成节流/防抖版，常用于"事件入口本身就该控制频率"的场景，例如滚动埋点、自动保存草稿：

```vue
<script setup lang="ts">
import { ref } from 'vue'
import { useEventListener, useThrottleFn, useDebounceFn } from '@vueuse/core'
import { sendAnalytics } from '@/lib/analytics'
import { api } from '@/lib/api'

const draft = ref('')

const reportScroll = useThrottleFn(() => {
  sendAnalytics({ scrollY: window.scrollY })
}, 200)

const saveDraft = useDebounceFn((value: string) => {
  return api.saveDraft(value)
}, 500)

useEventListener(window, 'scroll', reportScroll, { passive: true })
</script>

<template>
  <textarea v-model="draft" @input="saveDraft(draft)" />
</template>
```

`useThrottleFn` 适合"按固定节奏均匀触发"（埋点、节流刷新）；`useDebounceFn` 适合"等用户停下来再触发"（保存、搜索请求）。

### 正例 4（idle 时间分批处理：requestIdleCallback）

大列表初始化、批量埋点上报、本地索引构建这类**完全可以晚一点做**的工作，放到 `requestIdleCallback` 里，让首屏交互优先：

```vue
<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import type { Item } from './types'

const props = defineProps<{ allItems: Item[] }>()

const visible = ref<Item[]>([])
let idleId = 0

function scheduleBatch(rest: Item[]) {
  const run = (deadline?: IdleDeadline) => {
    while (rest.length && (!deadline || deadline.timeRemaining() > 4)) {
      visible.value.push(rest.shift()!)
    }
    if (rest.length) scheduleBatch(rest)
  }
  // Safari 老版本无 requestIdleCallback，降级到 setTimeout
  idleId = window.requestIdleCallback
    ? window.requestIdleCallback(run)
    : (window.setTimeout(() => run(), 16) as unknown as number)
}

onMounted(() => scheduleBatch([...props.allItems]))
onUnmounted(() => {
  window.cancelIdleCallback?.(idleId)
  window.clearTimeout(idleId)
})
</script>
```

要点：每批用 `deadline.timeRemaining() > 4` 判断是否继续，避免占满空闲帧；卸载时同时取消 idle 回调和 setTimeout，避免回调在已销毁组件上写 ref。

### 何时使用

- 高频指针/滚动/resize 事件 → 优先 VueUse 内置 hook，否则手写 RAF
- 用户输入触发的请求/上报 → `useDebounceFn`
- 用户输入触发的派生重渲染 → `refDebounced`（见 use-deferred-value）
- 列表分批渲染、批量埋点上报、本地索引构建 → `requestIdleCallback`

### 何时不要使用

- 动画关键帧、跟手交互（拖拽、缩放、绘制）→ 必须每帧都同步更新，不能节流/延迟
- 表单校验后的提交、关键的状态切换（登录态、权限）→ 这是"紧急更新"，不要 debounce
- 已经被 VueUse 内部节流过的 hook（如 `useScroll`/`useMouse`）→ 不要在外面再叠一层 throttle，会出现"晚两拍"的视觉滞后

### 注意事项

- `requestAnimationFrame` / `requestIdleCallback` / `setTimeout` 必须在 `onUnmounted` 中**取消挂起的句柄**，否则回调可能在组件销毁后触发，造成脏写或报错
- `useDebounceFn` 卸载时不会自动取消已排队的最后一次调用——如果回调里会发请求，注意业务上要么允许"组件没了请求还在路上"，要么手动 `flush()` 或 `cancel()`
- `watch` 的 `flush: 'post'` 是另一种调度手段：让回调推迟到 DOM 更新之后执行，适合需要读最新 DOM 尺寸的场景，不要和节流混为一谈

### 参考

- [VueUse: useThrottleFn](https://vueuse.org/shared/useThrottleFn/)
- [VueUse: useDebounceFn](https://vueuse.org/shared/useDebounceFn/)
- [VueUse: useScroll](https://vueuse.org/core/useScroll/)
- [MDN: requestIdleCallback](https://developer.mozilla.org/en-US/docs/Web/API/Window/requestIdleCallback)
