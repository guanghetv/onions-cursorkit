# 依赖安全规范（前端）

> **选型依据**：《现有技术选型》表（xlsx）。**MUST**：生产依赖须在表内已有条目，或经架构/前端负责人审批后纳入；禁止凭个人习惯引入未选型包。表内 **「前端技术选型」为「不符合」** 的包 **禁止** 作为业务依赖使用（见下表及替代方案）。

## 目录

- [原则](#原则)
- [MUST](#must)
- [MUST NOT](#must-not)
- [SHOULD](#should)
- [主业务与构建（选型表摘要）](#主业务与构建选型表摘要)
- [检查方式](#检查方式)
- [例外与审批](#例外与审批)
- [附录：选型表索引（按一级分类）](#附录选型表索引按一级分类)

## 原则

1. **白名单优先**：可维护、可审计、供应链面可控；与团队构建链（Vite / pnpm 等）一致。
2. **最小依赖**：同等能力优先选型表已有包；避免重复工具库（如多个日期库、多个 HTTP 客户端）。
3. **透明供应链**：lockfile 入仓、`npm audit` / SCA 常态化；警惕 `postinstall`、过度子依赖。

---

## MUST

- **lockfile**：`package-lock.json` / `pnpm-lock.yaml` / `yarn.lock` **必须提交**；CI 与本地安装须可复现。
- **包管理器**：新仓库优先 **pnpm**（选型表标注「符合」）；若团队统一 Corepack，按内部方案执行。
- **新增依赖**：须在 [现有技术选型](https://guanghe.feishu.cn/wiki/ZJe3w0s8Gidx93kO2yDc40NXnmh?table=tblylzxgIIYFTV9c&view=vewQDo8nhG) 中有对应 **技术名称**；**无则先走需求/审批** 再添加，不得在 PR 中静默引入大范围未选型依赖。
- **禁止项**：下列 npm 包在选型表中为 **「不符合」**，**MUST NOT** 写入业务 `dependencies`（含间接通过直接依赖固定版本规避——应换直接依赖或审批例外）。

| 技术名称（npm） | 说明 / 推荐替代 |
|-----------------|-----------------|
| `lodash` | 使用 `lodash-es` |
| `lodash-es` | ✅ 符合，按需子路径引入 |
| `rambda` | 不符合，避免 |
| `ramda` | 不符合，避免 |
| `rxjs` | 不符合，避免 |
| `ufo` | 不符合，避免 |
| `less` | 不符合；样式优先 `sass` / UnoCSS / PostCSS 等表内方案 |
| `jszip` | 不符合；**浏览器侧不建议**，换表内方案或后端处理 |
| `qs` | 不符合，避免 |
| `lit` | 不符合（web components 方向） |
| `ant-design-vue` | 不符合；PC toC 用 `naive-ui`，后台用 `element-ui` / `element-plus` 等表内组件库 |
| `nanoid` | 不符合；使用 `@guanghe-pub/onion-utils` 的 `getUUID()` 等内部能力 |

- **已废弃**：`@guanghe-pub/vite-plugin-postcss-px-to-viewport` — 使用 `@guanghe-pub/postcss-px-to-viewport`。

---

## MUST NOT

- 将 **选型「不符合」** 包作为生产依赖（上表）。
- 为绕过审计 **锁定已知恶意版本** 或从非官方 registry 安装未经验证的包（除非内部私服且已治理）。
- 在业务代码依赖中引入 **与选型表重复的同类旗舰库**（例如已有 `axios` 又加未选型的 HTTP 客户端），除非审批。

---

## SHOULD

- 定期执行 **`pnpm audit` / `npm audit`**，高危漏洞在 SLA 内修复或评估例外。
- 升级 **major** 或与构建链相关的包前，在变更说明中注明影响面；Monorepo 可用表内工具（如 `syncpack` / `taze`）保持版本策略一致。
- **内部能力优先**：监控用 `@guanghe-pub/fe-monitor`、`@guanghe-pub/web-track`；通用工具 `@guanghe-pub/onion-utils`；上传/CDN 用表内 `@guanghe-pub/*` OSS、upload 相关包。
- **组件库按场景**：主 App 端内 `@guanghe-pub/onion-ui`；Web 业务 `@guanghe-pub/onion-ui-web` / `onion-business-ui`；移动端端外/教师 App `vant`；PC toC `naive-ui`；后台 `element-ui`（Vue2）/ `element-plus`（Vue3）— 避免混用未选型 UI 框架。

---

## 主业务与构建（选型表摘要）

| 类别 | 表内代表（非穷尽，以 xlsx 为准） |
|------|----------------------------------|
| 主业务框架 | `vue`、`vue-router`、`pinia`、`vue-demi`、`axios`、`@vueuse/core` 等 |
| 打包 | `vite`、`rollup`、`webpack`、`vue-cli`、`tsup`、`turbo`、`nx`、`Rspack` 等 |
| 测试 | `vitest`、`@vue/test-utils`、`happy-dom`、`jsdom` 等 |
| 代码规范 | `eslint`、`prettier`、`stylelint`、`husky`、`lint-staged`、`@guanghe-pub/eslint-config` 等 |
| 组件/图标 | `onion-ui` 系、`vant`、`naive-ui`、`element-ui`、`element-plus`、`@icon-park/vue-next` 等 |
| 多媒体 | `echarts`、`lottie-web`、`pixi.js`、`gsap`、`html2canvas`、`pdfjs`、`three.js`、洋葱播放器系等 |
| 工具 | `dayjs`、`crypto-js`（加密场景注意密钥不落前端）、`zod`、`dexie`、`clsx` 等 |

完整清单以 **《现有技术选型》** 为准；Agent 审查时 **对照 xlsx 或同步后的内部文档**，勿自行扩充「允许列表」。

---

## 检查方式

- [ ] 新增 `dependencies` 是否在选型表中有 **技术名称** 一致或等价的包？
- [ ] 是否出现上表 **不符合** 包或 **废弃** 包？
- [ ] lockfile 是否随 `package.json` 变更一并更新？
- [ ] `npm audit` / `pnpm audit` 是否无未处理的高危项（或已登记例外）？

---

## 例外与审批

- 选型表未覆盖的新包、POC、或必须使用的 **不符合** 类替代方案：**前端架构 / 负责人书面或流程审批** 后落地，并在仓库或文档中留痕。

---

## 附录：选型表索引（按一级分类）

以下与 xlsx **一级分类** 对齐，便于检索；条目以公司内部《现有技术选型》为准。

- **主业务开发框架**：vue、vue-router、pinia、vue-demi、axios、@vue-macros/volar、@vueuse/core、@vueuse/shared、unplugin-vue-macros、vue-global-api 等  
- **CSS 工具**：postcss、autoprefixer、sass、lightningcss、unocss、@guanghe-pub/postcss-px-to-viewport、@guanghe-pub/unocss-preset-px-to-viewport 等  
- **打包工具**：vite、webpack、rollup、vue-cli、各类 vite/rollup 插件、terser、vue-tsc、unbuild、tsup、turbo、nx、Rspack 等  
- **包管理**：pnpm、npm、yarn、corepack、bumpp、changelogen、taze、syncpack、npm-run-all2 等  
- **代码规范**：eslint、prettier、stylelint、husky、lint-staged、simple-git-hooks、commitizen、commitlint、@guanghe-pub/eslint-config、@guanghe-pub/stylelint-config 等  
- **版本管理**：@changesets/cli 等  
- **测试**：vitest、@vitest/coverage-v8、@vue/test-utils、happy-dom、jsdom、vitest-webgl-canvas-mock 等  
- **文档**：storybook 系、vitepress、typedoc、automd、@chromatic-com/storybook 等  
- **组件库**：@guanghe-pub/onion-ui、onion-business-ui、@guanghe-pub/onion-ui-web、vant、naive-ui、element-ui、element-plus、@guanghe-pub/onion-problem-render、@guanghe-pub/onion-business-ui 等  
- **工具函数 / 工具集**：dayjs、clsx、@unhead/vue、unhead、copy-to-clipboard、file-saver、bignumber.js、ua-parser-js、uuid、@guanghe-pub/onion-utils、zod、dexie、utility-types 等  
- **多媒体**：swiper、lottie-web、pixi.js、qrcode、echarts、gifuct-js、gsap、@rive-app/webgl-advanced、html2canvas、modern-screenshot、yc-player、vue3-lottie、svg-path-parser、animate.css、video-animation-player、three.js 等  
- **加密/安全**：crypto-js（注意密钥与敏感逻辑归属后端）  
- **数据库/存储**：dexie  
- **图标**：@iconify-json/material-symbols、@icon-park/vue-next、unplugin-icons  
- **前端监控**：@guanghe-pub/fe-monitor、@guanghe-pub/web-track  
- **CDN 管理**：@guanghe-pub/onion-oss-vite-plugin、@guanghe-pub/onion-oss-webpack-plugin、@guanghe-pub/yc-upload、@guanghe-pub/yc-pc-upload-vue、@guanghe-pub/vite-plugin-cdn-import 等  
- **调试工具**：eruda、@vue/devtools-api  
- **cli**：chalk、inquirer、execa、figlet、@inquirer/prompts 等  
- **运行时**：jiti、regenerator-runtime、workbox-window  
- **web components**：仅表内明确项；`lit` 为不符合  

若 xlsx 与本文冲突，**以最新《现有技术选型》为准**，并建议同步更新本 skill 附录。
