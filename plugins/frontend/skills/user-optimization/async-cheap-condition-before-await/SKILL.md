---
name: async-cheap-condition-before-await
description: 当同步守卫条件已经不满足时，避免执行不必要的异步操作
---

## 在 await 异步值之前先检查廉价的同步条件

当一个分支既需要通过 `await` 拿到一个异步值（feature flag、远程配置、缓存项、数据库查询……），又需要一个**廉价的同步**条件（本地 props、组件 state、请求元数据、URL 参数、设备类型）才能成立时，应**优先**判断那个廉价条件。否则即使复合判断永远不可能为真，你仍然要为这次异步调用付出代价——网络往返、连接池占用、feature-flag 服务的配额、React `cache` 的命中开销，全都白付。

### 基础形态

**错误示例：**

```typescript
const flag = await getFlag('show-new-banner')

if (flag && route.query.from === 'campaign') {
  trackCampaignImpression()
}
```

只有来自营销活动落地页的用户才会触发埋点，但**每个用户**都白白拉了一次 feature flag。

**正确示例：**

```typescript
if (route.query.from === 'campaign') {
  const flag = await getFlag('show-new-banner')
  if (flag) {
    trackCampaignImpression()
  }
}
```

非营销来源直接跳过，连 flag 请求都不发。

### 业务场景：组件入口的"先看本地、再问远程"

Vue 组件里很常见的一种写法：进来就先 `await` 一个远程状态再判断是否要展示某块内容。

```typescript
// ❌ 不管 isVip 是不是 true，都要等一次接口
async function setup(props: Props) {
  const canUseFeature = await checkFeatureEntitlement(props.userId)
  if (props.isVip && canUseFeature) {
    enableVipFeature()
  }
}

// ✅ 先看 props 上已经存在的 isVip，决定要不要发请求
async function setup(props: Props) {
  if (!props.isVip) return
  const canUseFeature = await checkFeatureEntitlement(props.userId)
  if (canUseFeature) {
    enableVipFeature()
  }
}
```

`props.isVip` 是从父组件直接传下来的同步值，判断成本几乎为零；`checkFeatureEntitlement` 可能涉及一次 HTTP 请求。让前者先短路掉非 VIP 用户，整段逻辑的实际开销就只发生在 VIP 用户身上。

### 变体：`if / else if` 链里的"先 await 再判断"

当多个分支共享一个"先 await 再用"的前置异步调用，但只有少数分支真的会走到时，同样应当把同步分支抽到前面：

```typescript
// ❌ 每次请求都要先拉权限信息，即便 80% 的请求是匿名访客
async function handle(req: Request) {
  const permissions = await fetchPermissions(req.userId)

  if (req.userId == null) return renderPublicPage()
  if (permissions.canEdit) return renderEditor()
  return renderReadOnly()
}

// ✅ 匿名访客根本不需要权限信息
async function handle(req: Request) {
  if (req.userId == null) return renderPublicPage()

  const permissions = await fetchPermissions(req.userId)
  if (permissions.canEdit) return renderEditor()
  return renderReadOnly()
}
```

模式是一样的：**只要某个 `await` 的结果在"前置同步判断已经决定结果"的分支里不会被用到，就把它推后到真正用到的那一支再发**。

### 何时不适用

- **同步条件本身依赖那个异步值**：例如 `someCondition` 是基于 `flag` 计算的，那就只能先 `await`。
- **异步调用是为了产生副作用**：埋点、加锁、缓存预热、审计日志这类，下沉之后副作用就丢了，必须保留原顺序。
- **同步条件命中率极高、异步调用又很便宜**：节省下来的耗时还不抵增加的嵌套层级带来的阅读成本，保持简单写法即可。
- **请求需要更早发起以利用等待时间并行**：如果之后还是要 `await` 这个值、且发起它本身没什么代价，那么"提前发起、按需 await"反而更好。
