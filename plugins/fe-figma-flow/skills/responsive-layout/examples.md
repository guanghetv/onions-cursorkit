# 响应式布局代码示例

## 示例 1：搜索栏全断点适配

一个搜索栏组件在不同断点下的完整适配写法：

```vue
<style lang="scss" scoped>
@mixin default {
  .search {
    flex-grow: 1;
    height: 32px;
    min-width: 32px;
    border-radius: 16px;
    box-sizing: border-box;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  .search__input {
    padding: 0 8px;
    width: 100%;
    height: 100%;
    border-radius: 16px;
    flex-grow: 1;
    display: flex;
    align-items: center;
    box-sizing: border-box;
    background: rgba(#fff, 0.3);
  }
  .search__icon {
    width: 18px;
    height: 18px;
    margin-right: 8px;
  }
  .search__text {
    font-size: 14px;
    line-height: 14px;
    color: rgba(255, 255, 255, 0.8);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
}

/* 断点 1：默认样式 */
@include default;

/* 断点 2：小屏等比缩放 */
@media (max-width: 374px) {
  @design-width 375px;
  @design-unit vw;
  @include default;
}

/* 断点 3：pad 尺寸放大 */
@media (min-width: 640px) and (min-height: 640px) {
  .search {
    min-width: 40px;
    height: 40px;
    border-radius: 20px;
  }
  .search__input {
    padding: 0 12px;
    border-radius: 24px;
  }
  .search__icon {
    width: 23px;
    height: 23px;
    margin-right: 12px;
  }
  .search__text {
    font-size: 18px;
    line-height: 18px;
  }
}

/* 断点 6：pad 横屏，固定宽度 */
@media (min-width: 1024px) {
  .search {
    flex-grow: unset;
    width: 200px;
  }
}

/* 断点 7：手机横屏，收缩为图标 */
@media (max-height: 639px) and (orientation: landscape) {
  .search {
    flex-grow: 0;
    width: 32px;
    min-width: unset;
  }
  .search__input {
    justify-content: center;
  }
  .search__icon {
    margin-right: 0;
  }
}
</style>
```

## 示例 2：底部浮动按钮

考虑 tabbar 高度的底部定位：

```scss
.float-button {
  position: fixed;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  margin-bottom: calc(var(--safe-area-bottom) + 66px);

  @media (min-width: 640px) {
    margin-bottom: calc(var(--safe-area-bottom) + 80px);
  }

  @media (min-width: 768px) {
    margin-bottom: calc(var(--safe-area-bottom) + 96px);
  }

  @media (max-height: 450px) {
    margin-bottom: calc(var(--safe-area-bottom) + 56px);
  }
}
```

## 示例 3：页面容器安全边距

```scss
.page-container {
  padding-top: var(--safe-area-top);
  padding-bottom: var(--safe-area-bottom);
  padding-left: var(--safe-area-left);
  padding-right: var(--safe-area-right);
  min-height: 100vh;
  box-sizing: border-box;
}
```

## 示例 4：内嵌 Web 容器断点

在 APP 内嵌 WebView 中使用 device-width/device-height：

```scss
@mixin default {
  .card { padding: 12px; font-size: 14px; }
}
@include default;

@media (max-device-width: 374px) {
  @include default;  // 小屏等比缩放由 postcss 处理
}

@media (min-device-width: 640px) and (min-device-height: 640px) {
  .card { padding: 16px; font-size: 16px; }
}

@media (min-device-width: 640px) {
  .card { display: grid; grid-template-columns: 1fr 1fr; }
}

@media (min-device-width: 1024px) {
  .card { grid-template-columns: 1fr 1fr 1fr; }
}

@media (max-device-height: 639px) and (orientation: landscape) {
  .card { padding: 8px; font-size: 12px; }
}
```

## 示例 5：客户端屏幕旋转配置

```js
// 允许自动旋转
browserJump({
  url: '/study-app/home',
  hideNavigation: false,
  orientation: 'horizontal',  // 旧版兼容
  rotation: 'auto'            // 新版自动旋转
})

// URL 参数方式
browserJump('https://example.com/page?orientation=horizontal&rotation=auto')
```

## 示例 6：vite.config.ts postcss 配置

```ts
import { defineConfig } from 'vite'

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
          onlyCustomAtRule: true,
        }],
      ],
    },
  },
})
```
