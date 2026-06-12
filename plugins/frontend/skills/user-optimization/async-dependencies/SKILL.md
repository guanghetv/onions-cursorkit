---
name: async-dependencies
description: 基于依赖关系的并行化
---

## 让无依赖的请求尽早开始：基于依赖关系的并行化

当一组异步请求**只有部分**互相依赖时，常见的写法是：先 `Promise.all` 把"前置"的几个并行起来，等它们都完成后再去跑"后续"的那个。这种写法在很多场景下就是最优的，但**只要有一个前置请求比另一个慢，且后续请求只依赖那个快的**，就会出现一段被白白等待的时间。

这个 skill 教你识别这类场景，并把不依赖慢请求的后续操作"提前"发出去。

### 什么时候会出现优化空间

考虑这段代码：

```typescript
const [user, config] = await Promise.all([fetchUser(), fetchConfig()])
const profile = await fetchProfile(user.id)
```

依赖关系是：`profile` 只依赖 `user`，`config` 谁都不依赖。

- 总耗时 = `max(user, config) + profile`
- 如果 `config > user`：在 `user` 已经返回之后，`profile` 还得继续等 `config`，这段等待是**纯浪费**。
- 如果 `user ≥ config`：上面这段写法已经是最优解，无需优化。

把"`profile` 不依赖 `config`"这个事实显式表达出来后，总耗时就能压到 `max(config, user + profile)`，省下的时间是 `max(user, config) + profile − max(config, user + profile)`，也就是 `min(config − user, profile)`（仅当 `config > user` 时为正）。

> 经验法则：**当存在不依赖某个慢请求的后续步骤时**，把它提早发出去就有收益；多数业务场景的收益在 10%~50%，极端情况下能接近最慢请求耗时的对折。

### 推荐写法：原生 Promise + `.then`（首选）

不引入任何依赖。先把所有 promise 创建出来，让无依赖部分立刻开始，再用 `Promise.all` 统一收口：

```typescript
const userPromise = fetchUser()
const configPromise = fetchConfig()
const profilePromise = userPromise.then(user => fetchProfile(user.id))

const [user, config, profile] = await Promise.all([
  userPromise,
  configPromise,
  profilePromise,
])
```

要点：

- **`fetchProfile` 在 `userPromise` 一 resolve 就立刻发**，不再被 `config` 拖住。
- **统一在末尾 `await`**，避免出现"创建后没有任何位置 await"的悬空 promise（出错时无人处理 rejection）。
- 通用、零依赖、TS 类型推断天然正确，团队任意成员都能一眼看懂。


### 真实业务场景：先取列表再批量取详情

依赖型并行化最常见的形态之一是「先拉一个 id 列表，再据此批量拉详情」。同时有别的接口完全可以在背景里跑：

```typescript
const idsPromise = fetchOrderIds(userId)
const couponsPromise = fetchCoupons(userId)
const ordersPromise = idsPromise.then(ids =>
  Promise.all(ids.map(id => fetchOrderDetail(id)))
)

const [ids, coupons, orders] = await Promise.all([
  idsPromise,
  couponsPromise,
  ordersPromise,
])
```

`fetchCoupons` 完全独立于订单链路，让它在 `fetchOrderIds` 还没返回时就开始跑，整体页面就快这一段。

### 反例：不要为了"看起来并行"硬塞进 `Promise.all`

```typescript
// ❌ 看似并行，其实 fetchProfile 必须等 user，而 user 又只在 Promise.all 内部 await
const [user, config, profile] = await Promise.all([
  fetchUser(),
  fetchConfig(),
  // 这里拿不到 user.id：上面那个 fetchUser() 的 promise 还没 await 出 user 对象
  // 即便能拿到，写成嵌套 await 也会让控制流难读
])
```

依赖关系本身存在的步骤无法靠"塞进同一个 `Promise.all`"消除——必须通过显式串接（`.then`）。

### 什么时候不适用

- **请求之间完全没有依赖**：直接用 `Promise.all`。
- **某些分支根本不会用到结果**：不要让所有路径都被一个只在少数分支需要的请求拖住。
- **请求之间是严格的因果链**（A 完成才能开始 B，B 完成才能开始 C）：本来就只能串行，没有可优化空间。
- **后续请求成本极低且前置请求都很慢**：节省的时间可以忽略，保持简单写法即可。
