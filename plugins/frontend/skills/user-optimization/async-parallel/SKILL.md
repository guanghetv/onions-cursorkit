---
name: async-parallel
description: 使用 Promise.all() 并行执行相互独立的操作
---

## 使用 Promise.all() 让相互独立的操作并行

如果多个异步操作彼此不依赖对方的结果，连续 `await` 会形成"请求瀑布"（waterfall）：总耗时退化为各请求耗时之和。改用 `Promise.all()` 一次性发出、统一等待，整体耗时就接近其中最慢的那一个。

**错误写法（串行，总耗时 = 三者之和）：**

```typescript
const user = await fetchUser()
const posts = await fetchPosts()
const comments = await fetchComments()
```

**正确写法（并行，总耗时 ≈ 最慢的那一个）：**

```typescript
const [user, posts, comments] = await Promise.all([
  fetchUser(),
  fetchPosts(),
  fetchComments(),
])
```

### 循环里的隐藏 waterfall

`for...of` + `await` 会让循环变成串行，是业务代码里最容易被忽视的场景：

```typescript
// 错误：n 个 id 就要等 n 次
const results = []
for (const id of ids) {
  results.push(await fetchDetail(id))
}

// 正确：先全部发出，再统一等待
const results = await Promise.all(ids.map((id) => fetchDetail(id)))
```

> `array.forEach(async ...)` 不能被外层 `await`，相当于"发出去就不管"，请改用 `.map()` + `Promise.all`。

### 失败语义与限流

- `Promise.all` 是 **fail-fast**：任何一个 reject 都会让整体立即 reject，其它已经在路上的请求结果会被丢弃。如果"一个失败不应该影响其它结果"，改用 `Promise.allSettled`，再分别处理每一项的 `status`。
- 当并发数量可能很大（例如数百个 id 同时发请求）时，**直接 `map` 进 `Promise.all` 会压垮后端或耗尽浏览器连接池**，需要做分批 / 限流（如 `p-limit`、按页分批等）。

### 什么时候不适用

- **请求之间存在依赖**（后一个需要前一个的结果）：参考"基于依赖关系的并行化"（`async-dependencies`），让有依赖的部分尽早开始、无依赖的部分继续并行。
- **某些分支根本用不到结果**（条件提前返回）：参考"在真正需要时再 await"（`async-defer-await`），不要把所有人都拉去等一个只在少数路径上用到的值。
