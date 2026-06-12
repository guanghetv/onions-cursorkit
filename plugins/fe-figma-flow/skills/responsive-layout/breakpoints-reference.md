# 断点详细参考

## 完整断点定义

### 断点 1：默认样式（标准手机竖屏）

- **条件**：无媒体查询，直接写样式
- **设备**：iPhone7 等标准手机竖屏（≥ 375px）
- **设计稿**：750×1334（2x）
- **说明**：基准样式，所有元素使用固定 px

### 断点 2：小屏设备缩放（< 375px）

- **条件**：`@media (max-width: 374px)`
- **设备**：外盖屏、单手模式等
- **方案**：通过 `postcss-px-to-viewport` 将 px → vw 等比缩放
- **注意**：需配合 `@design-width 375px` 和 `@design-unit vw` 自定义规则

### 断点 3：pad 尺寸放大（≥ 640px 且 ≥ 640px 高）

- **条件**：`@media (min-width: 640px) and (min-height: 640px)`
- **设备**：所有 pad 尺寸设备（不区分横竖屏、折叠/非折叠）
- **说明**：**仅调整尺寸**（字号、间距、圆角等），**不调整布局**
- **设计稿**：1280×2048 华为MatePad11

### 断点 4：折叠屏/pad 竖屏布局（≥ 640px 宽）

- **条件**：`@media (min-width: 640px)`
- **设备**：折叠屏、pad 竖屏
- **说明**：调整布局结构（如网格列数、flex 方向等）

### 断点 5：较大折叠屏/pad 竖屏（≥ 768px 宽）

- **条件**：`@media (min-width: 768px)`
- **设备**：iPad 竖屏等较大屏幕
- **设计稿**：1536×2048 iPad 竖屏

### 断点 6：pad 横屏（≥ 1024px 宽）

- **条件**：`@media (min-width: 1024px)`
- **设备**：iPad 横屏、华为MatePad11 横屏
- **设计稿**：2048×1280 / 2048×1536

### 断点 7：手机横屏（高度 < 640px + landscape）

- **条件**：`@media (max-height: 639px) and (orientation: landscape)`
- **设备**：标准手机横屏
- **设计稿**：1334×750 iPhone7 横屏
- **必须放在最后**：优先级最高，覆盖前面所有断点

## 设备覆盖矩阵

```
                375(宽)    640(宽)    667(宽)    768(宽)    1024(宽)
1024(高)  │            │ 最小平板  │ 平板     │ 平板     │ 其他大屏
 768(高)  │            │          │          │          │ 平板横屏
 667(高)  │ 标准手机竖  │ 折叠屏    │ 折叠屏   │ 手机横屏  │ 三折叠
          │            │          │          │ 折叠屏    │
 640(高)  │ 小手机竖    │ 小折叠屏  │ 小折叠屏  │ 手机横屏  │ 最小平板横屏
 375(高)  │ 外盖屏      │ 小手机横  │ 标准手机  │ 手机横屏  │
          │ (等比缩放)  │          │ 横屏     │          │
```

## postcss-px-to-viewport 配置

### 方式一：自定义 @规则（推荐）

```ts
// vite.config.ts
export default defineConfig({
  css: {
    postcss: {
      plugins: [
        ['@guanghe-pub/postcss-px-to-viewport', {
          unitType: 'px',
          viewportWidth: 375,
          viewportUnit: 'vw',
          fontViewportUnit: 'vw',
          landscapeViewportWidth: 375,
          landscapeUnit: 'vh',
          landscapeFontViewportUnit: 'vh',
          unitPrecision: 5,
          allowedProperties: ['*'],
          excludedProperties: [],
          selectorBlacklist: ['.ignore', '.hairlines'],
          minPixelValue: 1,
          allowMediaQuery: true,
          replaceRules: true,
          excludeFiles: [],
          includeFiles: [],
          enableLandscape: true,
          enableCustomAtRule: true,
          onlyCustomAtRule: true   // 仅自定义 @规则生效
        }],
      ],
    },
  },
})
```

### 方式二：mini-css.scss 文件方案

为每个页面单独创建 `mini-css.scss`，postcss 仅对该文件生效：

```ts
// vite.config.ts
export default defineConfig({
  css: {
    postcss: {
      plugins: [
        ['@guanghe-pub/postcss-px-to-viewport', {
          // ...同上配置...
          includeFiles: [/\/mini-css.scss/],
          enableCustomAtRule: true,
          // 注意：不设置 onlyCustomAtRule
        }],
      ],
    },
  },
})
```

```scss
// mini-css.scss
@media (max-width: 374px) {
  .element {
    height: 32px;
    font-size: 14px;
  }
}
```

## 禁止事项

1. **禁止 `@media` 内嵌套 `@media`** — 导致 postcss 单位转换失效。SCSS 选择器内写 `@media` 是允许的（编译后提取到顶层）：

```scss
// ❌ 错误：@media 嵌套 @media
@media (max-width: 374px) {
  @design-width 375px;
  @design-unit vw;
  .element {
    height: 32px;
    @media (min-height: 640px) {  // 嵌套！转换失效
      height: 40px;
    }
  }
}

// ✅ 正确：SCSS 选择器内写 @media（编译后自动提取到顶层）
.element {
  height: 32px;
  @media (min-width: 640px) {
    height: 40px;
  }
}
```

2. **禁止打乱断点顺序** — 断点有覆盖关系，顺序错误会导致样式异常

3. **非必要不增加设计稿** — 4 套必出设计稿应足够，每增加一套会大量增加开发、测试、验收成本

## 响应式设计思路

1. **先考虑宽度变化**带来的布局调整
2. **再考虑高度变化**带来的动态调整
3. 不能只考虑目标设计稿的 4 个设备，需考虑各种中间尺寸
4. 尽量通过弹性布局（flex/grid）自适应，减少硬编码断点样式

## 项目分类适用范围

| 项目类型 | 适配方案 |
|---------|---------|
| 活动营销类 | 维持全局等比缩放，不开启屏幕旋转 |
| PC 网站类 | 维持全局等比缩放 |
| APP 移动端（主 APP） | 逐步启用新响应式方案 |
| 入校等子 APP | 暂维持等比缩放，后续跟进 |
| 客户端 | 统一固定 px + 断点适配 tabbar |

## 客户端屏幕旋转

通过路由参数 `rotation` 控制（v7.98.0+）：

```js
browserJump({
  url: navigateTarget,
  hideNavigation: false,
  orientation: 'horizontal',  // 旧版兼容
  rotation: 'auto'            // 新版：auto | vertical | horizontal
})
```

## 开发升级清单

1. 升级 `onion-utils` 至最新版
2. 升级 UI 组件库至最新版
3. 升级 `@guanghe-pub/postcss-px-to-viewport` 至最新版，更新配置
4. 按页面逐步适配
