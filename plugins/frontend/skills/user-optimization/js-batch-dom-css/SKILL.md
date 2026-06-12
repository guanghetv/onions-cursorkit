---
name: js-batch-dom-css
description: 避免强制同步布局，减少性能瓶颈
---

## 避免 layout thrashing

把"修改样式"和"读取布局属性"在同一同步任务里反复交错，浏览器**每次读都被迫立刻重新计算布局**——这就是 layout thrashing。

一次强制同步重排（forced reflow）通常耗 0.几 ~ 几毫秒，**循环里几十~上百次交错读写就足以吞掉一帧（16.7 ms）**，肉眼可见的就是列表渲染卡顿、滚动不跟手、动画掉帧。

> 会触发同步重排的"读"包括：`offsetWidth/Height/Top/Left`、`clientWidth/Height/Top/Left`、`scrollWidth/Height/Top/Left`、`getBoundingClientRect()`、`getComputedStyle()`、`element.focus()`、`scrollIntoView()` 等。完整清单见 [Paul Irish: What forces layout / reflow](https://gist.github.com/paulirish/5d52fb081b3570c81e3a)。

### 何时需要管，何时不必管

只在**循环 / 高频回调（滚动、拖拽、动画、resize）/ 一次性批处理大量 DOM** 这类会重复进入的代码里，layout thrashing 才有可观测影响。单次"写一次 + 读一次"只产生 1 次 reflow，浏览器一定要算的——别为了"看起来分相"去重构无害代码。

### OK：纯写不交错

浏览器会把同一同步任务里的多次写攒到下一次 layout，多写几行不会触发额外 reflow：

```ts
function setBoxStyle(el: HTMLElement) {
  el.style.width = '100px'
  el.style.height = '200px'
  el.style.backgroundColor = 'blue'
  el.style.border = '1px solid black'
}
```

### 反例：循环里读写交错

100 个元素 × 2 次读 = 200 次同步 reflow：

```ts
function thrashing(items: HTMLElement[]) {
  for (const el of items) {
    el.style.width = el.offsetWidth + 10 + 'px'    // 读 → 写
    el.style.height = el.offsetHeight + 10 + 'px'  // 又读 → 又写
  }
}
```

### 正例（首选：用 CSS class 替代 JS 写 style）

绝大多数"按状态切换样式"的场景都不该用 JS 直接改 `element.style.*`：

```css
.highlighted-box {
  width: 100px;
  height: 200px;
  background-color: blue;
  border: 1px solid black;
}
```

```ts
function highlight(el: HTMLElement) {
  el.classList.add('highlighted-box')
}
```

收益不只是少几次 reflow——CSS 表达式可被浏览器解析后缓存、可被 stylesheet 复用、主题/响应式/暗色模式可由 CSS 自己接管，关注点更清晰。能用 CSS class 表达的状态机，就不要散在 JS 里。

### 正例（必须用 JS 时：先批量读，再批量写）

把循环拆成"先读完所有 layout，再写所有 style"——读阶段共享一次 layout，写阶段攒到下一帧：

```ts
function resizeAll(items: HTMLElement[]) {
  // 读阶段：循环里只读不写
  const sizes = items.map(el => ({
    width: el.offsetWidth,
    height: el.offsetHeight,
  }))

  // 写阶段：浏览器把同一同步任务里的多次写攒到下一帧
  items.forEach((el, i) => {
    el.style.width = sizes[i].width + 10 + 'px'
    el.style.height = sizes[i].height + 10 + 'px'
  })
}
```

### 正例（写完只读一次：用 getBoundingClientRect()）

`getBoundingClientRect()` 一次返回 `top/left/right/bottom/width/height/x/y`——避免分别读 `offsetWidth`、`offsetHeight`、`offsetTop` 触发多次 reflow：

```ts
function applyAndMeasure(el: HTMLElement) {
  el.style.width = '100px'
  el.style.height = '200px'
  el.style.backgroundColor = 'blue'

  return el.getBoundingClientRect()  // 1 次 reflow，一次拿齐
}
```

### 正例（高频场景：用 requestAnimationFrame 节流 + 合并读）

滚动 / 拖拽 / resize 等会高频触发的事件，把读放进 `requestAnimationFrame`：rAF 回调在浏览器下一帧的样式重算/布局之前执行，把所有读集中到那里能共享同一次 layout，并天然节流到一帧一次：

```ts
let scheduled = false
function onScroll() {
  if (scheduled) return
  scheduled = true
  requestAnimationFrame(() => {
    scheduled = false
    const top = document.documentElement.scrollTop  // 集中读
    updateHeader(top)                                // 集中写
  })
}
window.addEventListener('scroll', onScroll, { passive: true })
```

> 配合 `client-passive-event-listeners` 的 passive 监听，避免 handler 阻塞滚动。

### Vue 中的体现

#### 反例：onMounted 里循环遍历 DOM，读 → 写 → 读 → 写

```vue
<script setup lang="ts">
import { onMounted, useTemplateRef } from 'vue'

const containerRef = useTemplateRef<HTMLDivElement>('container')

onMounted(() => {
  const container = containerRef.value
  if (!container) return
  const cards = container.querySelectorAll<HTMLElement>('.card')

  // ❌ 每张卡都读一次 offsetHeight，再写 top —— N 张卡 = N 次同步 reflow
  cards.forEach((card, i) => {
    card.style.left = (i % 3) * 200 + 'px'
    const cardHeight = card.offsetHeight
    card.style.top = computeTop(i, cardHeight) + 'px'
  })
})
</script>

<template>
  <div ref="container">
    <div v-for="item in items" :key="item.id" class="card">{{ item.name }}</div>
  </div>
</template>
```

#### 正例 1（首选：能用 CSS 布局就用 CSS 布局）

瀑布流这类规则布局，CSS `columns` / Grid `grid-template-columns` / Flex `flex-wrap` 都能搞定，无需 JS 计算坐标——浏览器自己解决，绝无 thrashing：

```vue
<template>
  <div class="masonry">
    <div v-for="item in items" :key="item.id" class="card">{{ item.name }}</div>
  </div>
</template>

<style scoped>
.masonry {
  columns: 3;
  column-gap: 20px;
}
.masonry .card {
  break-inside: avoid;
  margin-bottom: 20px;
}
</style>
```

#### 正例 2（必须用 JS 时：nextTick + 先读后写）

```vue
<script setup lang="ts">
import { onMounted, nextTick, useTemplateRef } from 'vue'

const containerRef = useTemplateRef<HTMLDivElement>('container')

onMounted(async () => {
  await nextTick() // 等 Vue patch 完，避免在 patch 中途读 layout
  const container = containerRef.value
  if (!container) return
  const cards = Array.from(container.querySelectorAll<HTMLElement>('.card'))

  // 读阶段：所有读发生在任何写之前，共享一次 layout
  const heights = cards.map(c => c.offsetHeight)

  // 写阶段：多次写攒到下一帧再统一布局
  cards.forEach((card, i) => {
    card.style.left = (i % 3) * 200 + 'px'
    card.style.top = computeTop(i, heights[i]) + 'px'
  })
})
</script>
```

`nextTick()` 让 Vue 把 DOM patch 完后再读，且 `getBoundingClientRect()` / `offsetHeight` 都集中在读阶段，整轮只产生 1 次 forced reflow。

### 何时不必优化

- 单次"写一次 + 读一次"的代码：只产生 1 次必要 reflow，无需重构
- 不在循环 / 高频回调里出现的零星读写
- SSR / `<script setup>` 顶层的同步代码——根本接触不到真实布局

### 经验法则

- 优先 CSS class / CSS 布局，让浏览器接管样式状态机
- 必须用 JS 操控 style：**先读完再写、或先写完只读一次**
- 读尺寸用 `getBoundingClientRect()`——一次拿齐 `width/height/top/left/...`，避免逐项读
- Vue 中操作完 DOM 想读尺寸：先 `await nextTick()` 再读
- 滚动 / 拖拽 / 动画：读集中到 `requestAnimationFrame`，并加 `{ passive: true }`
- DevTools Performance 面板里出现紫色的 `Forced reflow` / `Recalculate Style` warning 时，按本规则定位附近的交错读写

参考：

- [Paul Irish: What forces layout / reflow](https://gist.github.com/paulirish/5d52fb081b3570c81e3a)
- [CSS Triggers](https://csstriggers.com/)
- [MDN: Avoid forced synchronous layouts](https://developer.mozilla.org/en-US/docs/Web/Performance/Critical_rendering_path#avoid_forced_synchronous_layouts)
