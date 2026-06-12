---
name: frontend-tech-stack-skill
description: 前端技术选型守卫规范。当 AI 在前端项目中引入新依赖、选择组件库、使用工具函数库、配置打包工具或 CSS 方案时强制触发。确保所有技术选型符合团队标准，禁止引入不符合标记的技术，优先使用 @guanghe-pub/* 内部包。
---

# 前端技术选型守卫

在前端项目中引入、推荐或使用任何第三方库/工具时，必须严格遵循本规范。违反规范的技术选型将导致代码审查不通过。

## 何时使用

- 在前端项目中安装或引入新的 npm 依赖时
- 选择 UI 组件库、工具函数库、CSS 方案、打包工具时
- 用户要求推荐技术方案或对比技术选型时
- 代码中发现使用了禁止的库，需要给出替代方案时
- 创建新项目或初始化项目模板时

## 核心原则（强制遵守）

1. **内部包优先**：存在 `@guanghe-pub/*` 包时，必须使用内部包，禁止用社区包替代
2. **ES Modules 优先**：优先选择支持 ESM 的库版本（如 `lodash-es` 而非 `lodash`）
3. **「符合」标记优先**：标记为「✅ 符合」的技术为推荐选项
4. **禁止引入「❌ 不符合」标记的技术**
5. **不确定时询问**：遇到规范未覆盖的场景，必须询问用户确认，严禁自行决定

## 禁止清单（红线，绝不允许引入）

> **重要：以下技术已被明确禁止，发现使用时必须立即提示替换方案**

| 禁止技术 | 替代方案 | 原因 |
| --- | --- | --- |
| `ant-design-vue` | 按场景选用 `element-plus` / `naive-ui` / `vant` / `onion-ui` | 不符合技术选型 |
| `lodash` | `lodash-es` | 必须使用 ESM 版本 |
| `ramda` / `rambda` | `lodash-es` | 不符合 |
| `rxjs` | - | 不符合 |
| `nanoid` | `@guanghe-pub/onion-utils` 的 `getUUID()` | 不符合 |
| `qs` | `URLSearchParams`（原生 API） | 不符合 |
| `ufo` | - | 不符合 |
| `jszip` | - | 浏览器端不建议使用 |
| `less` | `sass` | 不符合 |
| `lit` | - | Web Components 不符合技术选型 |
| `vuex` | `pinia` | 禁止使用 Vuex |

## 主业务开发框架（必选）

| 技术 | 用途 | 说明 |
| --- | --- | --- |
| `vue` | 主框架 | Vue 3.x |
| `vue-router` | 路由管理 | |
| `pinia` | 状态管理 | 禁止使用 Vuex |
| `axios` | HTTP 请求 | Promise-based HTTP 客户端 |

### 推荐工具

| 技术 | 用途 |
| --- | --- |
| `@vueuse/core` | Vue 组合式 API 工具集 |
| `@vueuse/shared` | VueUse 共享工具函数 |
| `vue-demi` | Vue 2/3 兼容层（仅库开发使用） |
| `unplugin-vue-macros` | Vue 宏语法支持 |
| `@vue-macros/volar` | Vue 宏语法支持插件（用于 Volar） |
| `vue-global-api` | Vue 全局 API 的类型增强工具 |

## 组件库选型规则

> **重要：必须根据项目场景选择对应组件库，不可跨场景混用**

| 场景 | 组件库 | 状态 |
| --- | --- | --- |
| 主 APP 端内 | `@guanghe-pub/onion-ui` | ✅ 符合 |
| Web 端业务 | `@guanghe-pub/onion-ui-web` | ✅ 符合 |
| 业务组件 | `@guanghe-pub/onion-business-ui` | ✅ 符合 |
| 题目渲染 | `@guanghe-pub/onion-problem-render` | ✅ 符合 |
| 移动端/端外/教师APP | `vant` | ✅ 符合 |
| PC 端 toC | `naive-ui` | ✅ 符合 |
| 后台管理（Vue 2） | `element-ui` | ✅ 符合 |
| 后台管理（Vue 3） | `element-plus` | ✅ 符合 |
| 业务组件库 | `onion-business-ui` | ✅ 符合 |

图标按需加载使用 `unplugin-icons`（支持多种图标集）。

## 工具函数库

### 优先使用（内部包）

| 技术 | 用途 |
| --- | --- |
| `@guanghe-pub/onion-utils` | 内部通用工具函数库（**最高优先级**） |
| `@guanghe-pub/onion-utils` 的 `getUUID()` | UUID 生成（禁止使用 `nanoid`） |

### 推荐使用

| 技术 | 用途 |
| --- | --- |
| `lodash-es` | 通用工具函数（ESM 版本） |
| `dayjs` | 轻量级日期处理库（Moment.js 替代品） |
| `zod` | TypeScript 优先的数据模式校验库 |
| `clsx` | 条件类名合并工具 |
| `bignumber.js` | 高精度数学计算库 |
| `uuid` | 符合 RFC 4122 标准的唯一 ID 生成库 |
| `ua-parser-js` | 解析用户代理字符串的工具 |
| `copy-to-clipboard` | 复制文本到剪贴板的工具 |
| `file-saver` | 浏览器端文件保存工具（支持大文件分片） |
| `utility-types` | TypeScript 工具类型集合 |
| `regenerator-runtime` | 生成器函数的运行时垫片 |
| `fs-extra` | 增强版 Node.js 文件系统工具 |
| `@unhead/vue` | Vue 的文档头管理库（动态修改 `<head>`） |
| `unplugin-vue-router` | 基于文件系统的 Vue 路由生成工具 |
| `workbox-window` | Workbox 的运行时库（管理 Service Worker） |
| `brotli-compress` | Brotli 压缩算法实现（交互课预览场景） |

## CSS 工具

### 推荐使用

| 技术 | 用途 |
| --- | --- |
| `unocss` | 原子 CSS 引擎（**优先使用**） |
| `@unocss/reset` | UnoCSS 的默认样式重置集 |
| `@unocss/eslint-plugin` | UnoCSS 的 ESLint 插件 |
| `@guanghe-pub/unocss-preset-px-to-viewport` | px 转换成 vw/vh |
| `sass` | CSS 预处理器 |
| `postcss` | CSS 后处理器 |
| `autoprefixer` | 自动添加 CSS 浏览器前缀 |
| `@guanghe-pub/postcss-px-to-viewport` | px 转换成 vw/vh |
| `lightningcss` | 高性能 CSS 处理工具（Rust 编写） |

### 废弃

| 技术 | 说明 |
| --- | --- |
| `@guanghe-pub/vite-plugin-postcss-px-to-viewport` | 【废弃】禁止在新项目使用 |

## 打包工具

### 构建工具

| 技术 | 用途 | 状态 |
| --- | --- | --- |
| `vite` | 现代前端构建工具 | ✅ 符合（**首选**） |
| `rollup` | ES Modules 打包工具（适合库开发） | ✅ 符合 |
| `webpack` | 主流打包工具 | ✅ 推荐 |
| `vue-cli` | Vue 2.x 官方脚手架 | ✅ 推荐 |
| `turbo` | 高性能 Monorepo 构建工具 | ✅ 推荐 |
| `tsup` | 基于 ESBuild 的 TypeScript 打包工具 | ✅ 推荐 |
| `unbuild` | 通用 JavaScript 构建工具 | ✅ 推荐 |
| `nx` | 全栈项目构建系统 | ✅ 推荐 |
| `terser` | JavaScript 压缩工具 | ✅ 推荐 |
| `Rspack` | Rust 高性能打包工具（兼容 webpack） | ✅ 推荐 |
| `vue-tsc` | Vue SFC 的 TypeScript 类型检查工具 | ✅ 推荐 |

### Vite 插件

| 插件 | 用途 |
| --- | --- |
| `@vitejs/plugin-vue` | Vue 3 SFC 支持 |
| `@vitejs/plugin-vue-jsx` | Vue 3 JSX 支持 |
| `@vitejs/plugin-basic-ssl` | 快速 SSL 证书生成 |
| `@vitejs/plugin-legacy` | 旧版浏览器支持 |
| `vite-plugin-legacy-swc` | 旧版浏览器支持（SWC 编译） |
| `vite-plugin-pwa` | PWA 支持 |
| `vite-plugin-html` | HTML 多页配置 |
| `vite-plugin-pages` | 文件系统路由生成 |
| `vite-plugin-vue-layouts` | Vue 布局系统 |
| `vite-plugin-vue-devtools` | Vue DevTools 集成 |
| `vite-plugin-inspect` | 调试插件（查看中间状态） |
| `vite-plugin-terminal` | 终端日志增强 |
| `vite-plugin-version-mark` | 版本标记（注入构建信息） |
| `vite-plugin-cdn-import` | CDN 依赖引入 |
| `vite-plugin-externals` | 外部依赖声明 |
| `vite-plugin-resolve-externals` | 外部依赖解析 |
| `vite-plugin-handlebars` | Handlebars 模板支持 |
| `vite-plugin-doctest` | 文档测试 |
| `vite-bundle-visualizer` | 打包体积分析 |
| `@guanghe-pub/vite-plugin-cdn-import` | 内部 CDN 依赖自动引入 |
| `@guanghe-pub/onion-oss-vite-plugin` | 内部 OSS 上传集成 |
| `@guanghe-pub/vite-plugin-import-onion-ui` | 组件库 Vite 插件 |

### Rollup 插件

| 插件 | 用途 |
| --- | --- |
| `@rollup/plugin-commonjs` | CommonJS 转 ES Module |
| `@rollup/plugin-json` | JSON 文件解析 |
| `@rollup/plugin-node-resolve` | Node 模块路径解析 |
| `@rollup/plugin-typescript` | TypeScript 编译 |
| `rollup-plugin-esbuild` | ESBuild 加速转换 |
| `rollup-plugin-external-globals` | 外部全局变量声明 |
| `rollup-plugin-uglify` | 代码压缩 |
| `rollup-plugin-visualizer` | 打包体积分析 |

### Webpack / ESBuild 插件

| 插件 | 用途 |
| --- | --- |
| `@guanghe-pub/onion-oss-webpack-plugin` | Webpack OSS 上传集成 |
| `esbuild-plugin-globals` | ESBuild 全局变量注入 |

### 自动导入插件

| 插件 | 用途 |
| --- | --- |
| `unplugin-auto-import` | 自动导入 API |
| `unplugin-vue-components` | 自动按需导入 Vue 组件 |
| `@guanghe-pub/babel-plugin-import-onion-ui` | 按需加载内部 UI 组件 |

## 包管理器

| 技术 | 状态 |
| --- | --- |
| `pnpm` | ✅ 符合（**首选**） |
| `npm` | ✅ 推荐 |
| `yarn` | ✅ 推荐 |
| `corepack` | ✅ 推荐 |

### 版本管理工具

| 技术 | 用途 |
| --- | --- |
| `bumpp` | 交互式版本号升级 |
| `changelogen` | 语义化发布、变更日志生成（单仓库） |
| `@changesets/cli` | 多包仓库版本管理 |
| `@changesets/changelog-git` | Changesets Git 集成 |
| `taze` | 依赖版本更新检查 |
| `syncpack` | 多包仓库依赖版本同步 |

## 测试工具

| 技术 | 用途 |
| --- | --- |
| `vitest` | 单元测试框架（**首选**） |
| `@vue/test-utils` | Vue 组件测试工具 |
| `@vitest/coverage-v8` | V8 覆盖率报告 |
| `happy-dom` | 模拟浏览器 DOM 环境 |
| `jsdom` | 完整浏览器环境模拟 |
| `vitest-webgl-canvas-mock` | WebGL Canvas 模拟环境 |

## 多媒体处理

| 技术 | 用途 |
| --- | --- |
| `lottie-web` | 渲染 After Effects 动画（JSON 格式） |
| `vue3-lottie` | Vue3 Lottie 动画封装 |
| `pixi.js` | 高性能 2D 渲染引擎 |
| `pixi-filters` | Pixi.js 滤镜扩展 |
| `three.js` | 3D 图形渲染 |
| `echarts` | 数据可视化 |
| `gsap` | 专业级动画库 |
| `html2canvas` | 网页截图（Canvas） |
| `modern-screenshot` | 前端截图工具 |
| `pdfjs` | PDF 文件渲染 |
| `animate.css` | CSS 动画关键帧库 |
| `swiper` | 轮播图/滑动组件 |
| `qrcode` | 二维码生成 |
| `gifuct-js` | GIF 解析与生成 |
| `svg-path-parser` | SVG 路径解析器 |
| `@rive-app/webgl-advanced` | 高级 WebGL 动画渲染 |
| `vue-image-crop-upload` | Vue 图片裁剪上传组件 |
| `video-animation-player` | 视频动画播放器 |

### 播放器

| 技术 | 用途 |
| --- | --- |
| `yc-player` / `yc-mobile-player` | 视频播放器 |
| `@guanghe/yc-player` | 播放器手机端版本 |
| `@guanghe/yc-pc-player-vue` | 播放器 PC 浏览器版本 |

## 代码规范工具

### 已内置到工具链（无需单独配置）

| 技术 | 用途 |
| --- | --- |
| `eslint` | JavaScript/TypeScript 代码检查 |
| `prettier` | 代码格式化 |
| `stylelint` | CSS 代码检查 |
| `lint-staged` | Git 暂存区文件检查 |
| `@commitlint/cli` | Git 提交信息规范检查 |
| `@commitlint/config-conventional` | Conventional Commits 配置 |
| `@guanghe-pub/eslint-config` | 内部 ESLint 共享配置 |
| `@guanghe-pub/stylelint-config` | 内部 Stylelint 共享配置 |
| `eslint-plugin-vue` | Vue 模板 ESLint 规则 |

### ESLint 插件

| 技术 | 用途 |
| --- | --- |
| `@stylistic/eslint-plugin` | 代码风格规则 |
| `eslint-plugin-format` | 代码格式化规则 |
| `eslint-plugin-storybook` | Storybook ESLint 规则 |
| `eslint-config-alloy` | 腾讯 AlloyTeam ESLint 配置 |

### Git 钩子管理

| 技术 | 用途 |
| --- | --- |
| `husky` | Git 钩子管理 |
| `simple-git-hooks` | 轻量级 Git 钩子管理 |

### 提交规范

| 技术 | 用途 |
| --- | --- |
| `commitizen` | 交互式 Git 提交信息生成 |
| `cz-conventional-changelog` | Conventional Changelog 适配器 |
| `cz-customizable` | 可定制配置插件 |

## 前端监控与调试

| 技术 | 用途 |
| --- | --- |
| `@guanghe-pub/fe-monitor` | 前端监控 SDK |
| `@guanghe-pub/web-track` | 前端日志发送包 |
| `eruda` | 移动端网页调试工具 |
| `@vue/devtools-api` | Vue DevTools 插件 API |

## 文档工具

| 技术 | 用途 |
| --- | --- |
| `vitepress` | 基于 Vite 的静态站点生成器（技术文档） |
| `storybook` | UI 组件隔离开发环境 |
| `@storybook/addon-essentials` | Storybook 核心插件集合 |
| `@storybook/addon-interactions` | Storybook 交互测试 |
| `@storybook/addon-onboarding` | Storybook 新手引导 |
| `@storybook/blocks` | Storybook 文档块组件 |
| `@storybook/test` | Storybook 轻量级测试 |
| `@storybook/vue3` | Storybook Vue3 适配器 |
| `@storybook/vue3-vite` | Storybook Vite+Vue3 构建器 |
| `@chromatic-com/storybook` | Storybook 可视化测试服务 |
| `typedoc` | TypeScript API 文档生成 |
| `typedoc-plugin-markdown` | Markdown 格式输出 |
| `typedoc-plugin-localization` | 多语言支持 |
| `automd` | 自动生成/更新 Markdown 内容 |

## 其他技术领域

### 加密与安全

| 技术 | 用途 |
| --- | --- |
| `crypto-js` | 多种加密算法（AES、SHA 等） |

### 数据存储

| 技术 | 用途 |
| --- | --- |
| `dexie` | IndexedDB 封装库（Promise 接口） |

### 图标库

| 技术 | 用途 |
| --- | --- |
| `unplugin-icons` | 图标按需加载 |
| `@icon-park/vue-next` | IconPark Vue3 图标库 |
| `@iconify-json/material-symbols` | Material Symbols 图标集 |

### CLI 工具

| 技术 | 用途 |
| --- | --- |
| `chalk` | 终端字符串美化 |
| `figlet` | ASCII 艺术字生成 |
| `inquirer` | 命令行交互工具 |
| `@inquirer/prompts` | 命令行交互插件化实现 |
| `inquirer-autocomplete-standalone` | 自动补全插件 |
| `execa` | Node.js 子进程执行（Promise） |
| `npm-run-all2` | 并行/串行运行 npm 脚本 |

### 运行时

| 技术 | 用途 |
| --- | --- |
| `jiti` | 运行时 TypeScript 和 ESM 加载器 |

### CDN 管理

| 技术 | 用途 |
| --- | --- |
| `@guanghe-pub/onion-oss-vite-plugin` | Vite OSS 上传集成 |
| `@guanghe-pub/onion-oss-webpack-plugin` | Webpack OSS 上传集成 |
| `@guanghe-pub/vite-plugin-cdn-import` | Vite CDN 依赖自动引入 |
| `@guanghe-pub/yc-upload` | CDN 上传底层包 |
| `@guanghe-pub/yc-pc-upload-vue` | CDN 上传 PC 浏览器 Vue 组件版本 |

## 执行检查清单

当 AI 在项目中引入新依赖时，必须按顺序执行以下检查：

- [ ] 该依赖是否在本规范的**禁止清单**中？→ 是则拒绝并给出替代方案
- [ ] 是否存在对应的 `@guanghe-pub/*` 内部包？→ 是则必须使用内部包
- [ ] 该依赖是否有 ESM 版本？→ 是则优先使用 ESM 版本
- [ ] 该依赖是否在本规范的推荐列表中？→ 是则直接使用
- [ ] 该依赖不在规范中？→ 必须询问用户确认后方可引入
