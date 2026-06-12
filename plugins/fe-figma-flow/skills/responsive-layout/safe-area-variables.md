# 安全边距 CSS 变量详解

## 变量一览

客户端通过 JS 注入，前端通过 CSS `var()` 使用。

### 主要变量（推荐使用）

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `--safe-area-top` | 顶部安全边距 | 0px |
| `--safe-area-bottom` | 底部安全边距 | 0px |
| `--safe-area-left` | 左侧安全边距 | 0px |
| `--safe-area-right` | 右侧安全边距 | 0px |

### no-default 变量（特殊场景）

| 变量名 | 说明 |
|--------|------|
| `--safe-area-top-no-default` | 无默认值，支持 var 第二参数 |
| `--safe-area-bottom-no-default` | 无默认值，支持 var 第二参数 |
| `--safe-area-left-no-default` | 无默认值，支持 var 第二参数 |
| `--safe-area-right-no-default` | 无默认值，支持 var 第二参数 |

### 其他变量

| 变量名 | 说明 |
|--------|------|
| `--notch-left-width` | 侧边刘海屏安全距离（默认 0px） |
| `--deviceHeight` | 设备屏幕高度 |
| `--deviceWidth` | 设备屏幕宽度 |

## 使用方式

### 常规安全边距

```css
.content {
  padding-top: var(--safe-area-top);
  padding-bottom: var(--safe-area-bottom);
  padding-left: var(--safe-area-left);
  padding-right: var(--safe-area-right);
}
```

### 需要自定义兜底值

当安全边距为 0 时也想保留间距，使用 no-default 变量：

```css
.resource-badge {
  /* 有安全边距用安全边距，无安全边距时距顶部 20px */
  margin-top: var(--safe-area-top-no-default, 20px);
}
```

### 横屏摄像头遮挡

横竖屏旋转时，横屏可能有摄像头遮挡，需设置左右边距：

```css
.page {
  margin-left: var(--safe-area-left);
  margin-right: var(--safe-area-right);
}
```

## 易错点

### 1. var 默认值陷阱

`var(--safe-area-top)` 的值如果存在但为 0，CSS 认为变量已生效，**不会**走 `var()` 的第二个默认参数：

```css
/* 如果 --safe-area-top 为 0px，结果是 0px，不是 20px */
margin-top: var(--safe-area-top, 20px);

/* 如需兜底，使用 no-default 变量 */
margin-top: var(--safe-area-top-no-default, 20px);
```

### 2. iOS 兼容性

在支持 `env()` 的 iOS 浏览器中，`no-default` 和普通变量实际表现一致，都无法让外部 `var()` 的第二个值生效。请直接使用 `var(--safe-area-top)` 为主。

### 3. 导航栏场景

展示了客户端导航栏时，浏览器高度已被压缩，**无需** `--safe-area-top` 来控制上间距（客户端仍会返回该值，但不应使用）。

## 客户端注入机制

客户端监听屏幕变化（旋转、分屏），通过 WebView 执行 JS 注入：

```js
document.documentElement.style.setProperty('--safeTop', '${height}px');
document.documentElement.style.setProperty('--safeBottom', '${height}px');
document.documentElement.style.setProperty('--safeLeft', '${height}px');
document.documentElement.style.setProperty('--safeRight', '${height}px');
document.documentElement.style.setProperty('--deviceHeight', '${height}px');
document.documentElement.style.setProperty('--deviceWidth', '${width}px');
```

## utils 库兼容逻辑（onion-utils v2.17.0）

取值优先级：
1. **客户端注入**（`--safeTop` 等原生变量）— 最高优先级
2. **URL query 参数**（`tabBarHeight`、`statusBarHeight`、`notchHeight`）
3. **系统 API 兜底**（`env(safe-area-inset-*)` / `constant(safe-area-inset-*)`）

前端引入 utils 库后，直接在 CSS 中使用 `var(--safe-area-top)` 等变量即可，兼容逻辑由库内部处理。

## 三端容器统一规则（v7.98.0+）

- Web 容器**撑满全屏**，不再受状态栏占位影响
- 竖屏：状态栏默认展示，Web 容器撑满全屏
- 横屏：状态栏默认隐藏，Web 容器撑满全屏（iPad 横屏因 iOS 限制无法隐藏状态栏）
- 展示导航栏时：Web 容器撑满导航栏下方
- Tabbar 悬浮在 Web 容器上层，不影响容器空间

### 控制接口

| 功能 | 方式 |
|------|------|
| 控制状态栏+导航栏显隐 | `setBrowserNavHidden` 增强 / `hideNavigation` 路由参数 |
| 控制状态栏文字颜色 | `setBrowserStatusBarWhite(isWhite)` |
| 控制状态栏背景色（仅 Android/鸿蒙） | `setStatusBarColor('#AARRGGBB')` |
