---
name: interaction-specifications
description: Use when 编写或改造前端页面代码、Vue 页面代码、列表页、业务数据列表、长列表、分页列表、下拉刷新、加载更多、首屏加载、弹窗、按钮请求、submit/change/click 请求、图片展示、防抖、安全区适配时，需要硬性执行页面交互规范。不要用于纯审查报告、概念解释或不涉及代码改造的讨论.
---

# interaction-specifications

## Mandatory Workflow

当此 skill 被加载后，在编写或修改代码前必须执行：

1. 使用下方检查清单对任务进行分类。
2. 选择所有适用规则，不要只选择其中一条。
3. 在输出代码前，简要说明已命中的规则。
4. 在代码中落实已命中的规则。
5. 在最终回复前，执行交付检查清单。
6. 如果某条规则被有意跳过，必须说明原因。

**列表硬性规则：** 只要需求命中业务数据列表、分页列表、长列表或数据规模不稳定的集合渲染，默认使用 Vue3 `list-view` 虚拟列表，不得使用普通 `v-for` 直接实现业务列表。`tab`、菜单列表、固定少量入口、固定少量权益卡片、静态配置列表不按列表组件处理，可使用普通结构实现。

## 触发与默认动作

| 命中场景 | 默认动作 |
| --- | --- |
| 需求提到“业务数据列表”“列表页”“长列表”“分页列表”“数据列表”“课程列表”“商品列表”“卡片列表”“加载更多”等 | 默认使用 `Vue3` 版本 `list-view` 模板；默认开启虚拟列表 |
| `tab`、菜单列表、固定少量入口、固定少量权益卡片、静态配置列表 | 不需要使用 `list-view`，可使用普通结构实现 |
| 初始进入页面、初始加载、首屏内容依赖接口、初始时通过接口获取任意内容 | 必须接入首屏 `OILoading` |
| 页面出现弹窗，或点击按钮后出现弹窗，分享按钮点击打开分享弹窗 | 必须接入使用utils中方法增加物理返回键 `backStack` |
| 点击按钮发起请求、`change` 请求、`submit` 发起请求、`click`请求 | 必须为异步处理函数外层加 `debounce` |
| 页面出现业务图片、非 `svg` 图片、`img` 标签、图片加载、图片卡片、封面等 | 必须使用 `OIImgLoad` 替换；开启懒加载；添加 `@error="handleError"`；按需求或设计稿图片尺寸直接给失败占位。小 `icon`、CSS 背景图、导入组件内部图片可排除 |

## 列表规范

命中业务列表相关词时，必须执行以下规则：

1. MUST 使用 `Vue3` 版本的 `list-view` 模板。
2. MUST 开启虚拟列表：`isUseVirtual` 必须为 `true`。
3. MUST 设置合理的 `itemHeight`，不能省略，根据设计稿中的大小设定。
4. DO NOT 使用普通 `v-for` 直接渲染业务列表。
5. `tab`、菜单列表、固定少量入口、固定少量权益卡片、静态配置列表不需要使用 `list-view`，可以用普通结构实现。
6. 只有用户明确要求“不使用虚拟列表”或“不使用 list-view”时，才允许在业务数据列表中跳过，并且必须在最终回复中说明原因。
7. 列表项结构统一、存在分页/加载更多/筛选重载、数据规模不稳定、item 结构复杂、滚动卡顿时，都按列表组件处理。

使用模板：

```vue
<ListView :loader="loadData" :isUseVirtual="true" :itemHeight="72">
  <template #default="{ item, index }">
    <ListViewItem :key="item.id || index" :item="item">
      <div>{{ item.title }}</div>
    </ListViewItem>
  </template>
</ListView>
```
- 可以使用list-view相关skill实现这个列表组件
- 引用指向：`@.cursor/skills/list-view/SKILL.md`

## Loading 接入规范

至少命中以下任一条件时，视为需要接入loading：

- **首屏请求**：页面首次渲染存在明显等待。
- **切换行为触发请求**：如 tab 切换、筛选切换、路由切换会重新拉取数据。
- **用户动作有异步过程**：如下拉刷新（顶部）、提交后回流、恢复页面后重拉数据。
- **列表有分页加载**：上拉加载更多时需要明确反馈“正在加载”。
- **空态与加载态混淆**：请求未结束就渲染空态，导致“误判无数据”。

- 可通过在外部容器加样式或直接在上面增加
- 需要响应式字段控制显示和消失
- 如接口返回数据后不展示此组件，展示渲染后的组件

### Loading使用模版

```vue
<script setup lang="ts">
import { OILoading } from '@guanghe-pub/onion-ui'
import { ref } from 'vue'

const loading = ref(true)
</script>

<template>
  <OILoading v-if="loading" style="" />
</template>
```

## 弹窗物理返回键规范

页面出现弹窗，或点击按钮后打开弹窗时，默认接入 `backStack`：

1. 重点识别 `OISheet`、`OIShareSheet`、`OIPopup`、`OIModalPlus`、`OIDrawer` 等弹窗组件。
2. 需求中明确说要加入弹窗时，必须使用组件库的弹窗。
3. 打开弹窗时执行 `backStack.push()`。
4. 关闭弹窗时执行 `backStack.pop()`。
5. `push` 回调必须复用统一关闭函数，避免出现两套关闭逻辑。
6. 物理返回键生效必须在 Android 实机或等效移动端容器验证，桌面浏览器不作为最终依据。

```js
//导入弹窗组件
import { OISheet } from '@guanghe-pub/onion-ui'
```

```js
import { backStack } from '@guanghe-pub/onion-utils'

function openPopup() {
  visible.value = true
  backStack.push(closePopup)
}

function closePopup() {
  visible.value = false
  backStack.pop()
}
```

若页面存在多个弹窗，每个弹窗使用独立打开/关闭函数维护自己的 `backStack` 入栈与出栈，避免互相关闭错误。

## 防抖规范

按钮点击、`change`、`submit` 等事件中只要会发起请求，必须加防抖：

1. 识别 `@click`、`@change`、`@submit`、`@confirm`、保存、提交、领取、发送等事件。
2. 事件处理函数中存在 `await`、`Promise`、接口调用、`service.xxx()` 等异步请求时，必须在函数外层使用 `debounce` 包裹。
3. 优先使用 `leading: true, trailing: false`，防止快速连续触发。
4. 防抖窗口默认 `300ms`。
5. 仅纯跳转且不发请求的函数可以不加防抖。

```js
import { debounce } from '@guanghe-pub/onion-utils'

const submit = debounce(
  async () => {
    await submitForm()
  },
  300,
  { leading: true, trailing: false },
)
```
验证时连续快速点击触发按钮，防抖窗口期内应只发起一次请求，且首次点击能立即响应。


## 图片规范

除 `svg`、小 `icon`、CSS 背景图、导入组件内部图片这类不需要页面层接管加载状态的资源外，页面中的业务图片默认使用 `OIImgLoad`：

1. 将普通业务 `img` 标签或图片加载相关都需要使用 `OIImgLoad`组件,头像相关组件使用 `OIUserHeader` 组件。
2. 不额外加背景色与圆角边框
3. 必须开启图片懒加载。
4. 失败状态必须有占位；占位尺寸直接根据需求描述或 Figma 设计稿中的图片大小确定。
5. 图片失败时调用统一 `handleError` 收口，避免页面空白或布局塌陷。
6. 小 `icon`、CSS 背景图、第三方或导入组件内部已经封装的图片不强制替换为 `OIImgLoad`。

`placeholderHeight` 必须按需求或设计稿图片尺寸调整，例如头像使用头像高度，封面图使用封面图高度，卡片图使用卡片图片区域高度。

```vue
<template>
  <OIImgLoad
    :key=" "
    :src="resolvedSrc"
    :style="{ minHeight: `${minHeight}px` }"
    showImgStatus
    fit="fill"
    alt="image"
    lazy
    @error="handleError"
  >
  <template #loading>
    <div>加载中...</div>
  </template>
  <template #error>
    <div>加载失败</div>
  </template>
  </OIImgLoad>
</template>

<script setup lang="ts">
import { OIImgLoad } from '@guanghe-pub/onion-ui'
</script>
```

## 安全边距接入规范

命中任一即判定需要对应安全区适配：

- 页面存在 `tabbar`、底部固定操作栏、底部悬浮交互元素，可能被系统手势条遮挡 -> 需要评估安全底部。
- 页面顶部存在状态栏区域、刘海/摄像头区域、顶部手势滑块 tabbar、顶部 fixed 交互元素 -> 需要评估安全顶部。
- 页面支持横屏，且横屏后左侧存在可点击元素或摄像头/遮挡区域 -> 需要评估安全左侧。
- 页面支持横屏，且横屏后右侧存在可点击元素或摄像头/遮挡区域 -> 需要评估安全右侧。
约束：
- 安全左/右边距只在“页面支持横屏”前提下评估与接入。
- 若页面不支持横屏，不得默认添加安全左/右边距。
  
### 常规安全边距
```css
.content {
  padding-top: var(--safe-area-top);
  padding-bottom: var(--safe-area-bottom);
  padding-left: var(--safe-area-left);
  padding-right: var(--safe-area-right);
}
```

## 交付要求
- 在产出代码前判断以上规范是否有遗漏


