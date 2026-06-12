---
name: async-defer-await
description: 避免阻塞未使用的代码路径
---

## 在真正需要时再 await

如果一个异步结果**只在部分分支**会被用到，就不要在函数入口就 `await` 它，否则用不到它的分支也得一起白等。

这种"按需 await"有两种做法，区别在于**请求本身要不要也跟着推迟**：

1. **整体推迟**：把请求和 `await` 一起下沉到真正用到结果的分支。适合"启动请求"本身就有代价的场景（占连接池、消耗用户配额、触发对方限流）。
2. **提前发起，按需 await**：请求立刻发出去，但只在真正会用到时才 `await`。适合多数远程请求——发起几乎免费，等待才贵。

### 做法 1：整体推迟

**错误写法（两个分支都被阻塞）：**

```typescript
async function handleRequest(userId: string, skipProcessing: boolean) {
  const userData = await fetchUserData(userId)

  if (skipProcessing) {
    // 立刻返回，但已经白白等了一次 fetchUserData
    return { skipped: true }
  }

  return processUserData(userData)
}
```

**正确写法：**

```typescript
async function handleRequest(userId: string, skipProcessing: boolean) {
  if (skipProcessing) {
    return { skipped: true }
  }

  const userData = await fetchUserData(userId)
  return processUserData(userData)
}
```

当 `skipProcessing` 命中率较高、或 `fetchUserData` 本身较慢时，收益最明显。

### 做法 2：提前发起，按需 await

如果"发请求"本身没什么成本，更好的写法是**先把 promise 起出来**，再决定要不要等：

```typescript
async function handleRequest(userId: string, skipProcessing: boolean) {
  const userDataPromise = fetchUserData(userId) // 立刻发起，不阻塞

  if (skipProcessing) {
    return { skipped: true } // 冷分支零等待
  }

  const userData = await userDataPromise // 热分支也几乎没多等
  return processUserData(userData)
}
```

这样冷分支完全不等，热分支也利用了 `if` 判断那段时间继续在网络上跑请求。多数场景下做法 2 都比做法 1 更优。

> **注意 unhandled rejection**：如果冷分支真的没人 `await` 那个 promise，它一旦 reject 就成了未捕获的拒绝（部分 Node 严格模式、Jest 等会报错）。最简单的兜底是挂一个 `.catch(() => {})`，或者用 `void promise.catch(...)` 显式表明"知道它可能失败，但这条路径不关心"。

### 做法 1 在"提前返回 + 多条件校验"里的典型用法

```typescript
// 错误：无论资源是否存在，都白拉了 permissions
async function updateResource(resourceId: string, userId: string) {
  const permissions = await fetchPermissions(userId)
  const resource = await getResource(resourceId)

  if (!resource) return { error: 'Not found' }
  if (!permissions.canEdit) return { error: 'Forbidden' }

  return updateResourceData(resource, permissions)
}

// 正确：先看资源存不存在，再决定要不要继续往下
async function updateResource(resourceId: string, userId: string) {
  const resource = await getResource(resourceId)
  if (!resource) return { error: 'Not found' }

  const permissions = await fetchPermissions(userId)
  if (!permissions.canEdit) return { error: 'Forbidden' }

  return updateResourceData(resource, permissions)
}
```

> ⚠️ 上面"正确写法"在 **两个请求都必须发出** 的 happy path 上变成了**串行**——比 `Promise.all` 慢一点。 真实选型要看分布：
>
> - **早退分支命中率高**（多数请求会 Not Found / Forbidden）→ 用上面这种纯下沉写法。
> - **两者命中率相近**且 `fetchPermissions` 启动廉价 → 用做法 2：`const permissionsPromise = fetchPermissions(userId)` 先发出去，等 `resource` 验完再决定要不要 `await`。

### 何时不适用

- **所有分支最终都会用到结果**：与其推迟，不如尽早发起、并行执行。
- **该异步调用本身就是为了副作用**（埋点、加锁、缓存预热、审计日志、权限校验副效应等）：下沉之后副作用就跟着丢了，必须保留原顺序。
- **跳过分支命中率非常低、且 `await` 本身很便宜**：节省下来的耗时还没增加的阅读复杂度大。
- **做法 2 的反例**：如果"发起请求"本身就有显著代价（占用本地连接池、消耗用户配额、触发对方限流计数），那就用做法 1，确认要用了再发。
