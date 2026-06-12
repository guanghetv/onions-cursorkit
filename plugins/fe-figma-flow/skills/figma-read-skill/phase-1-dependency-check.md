# 依赖探查 · 三步核查流程

> **何时阅读**：执行流程 Step 3。在 Figma MCP 调用完成后、建立元素清单前，必须完成本文件的三步探查，并将结论写入 `figma-audit.md` 第 1 节「目标与项目上下文」。
>
> **禁止跳过**：只看子包 `package.json` 就下结论是本 skill 最常见的幻觉来源，已在实际执行中复现两次。

---

## Step 3a：workspace 依赖探查（pnpm monorepo 专项）

当目标目录是 monorepo 子包时（如 `03-prototype/`），必须：

1. 在目标目录及其上级目录中查找 `pnpm-workspace.yaml`，定位 workspace root；
2. 读取 workspace root 的 `package.json`，确认 `@guanghe-pub/*` 是否声明为 workspace-level 依赖；
3. 子包自己的 `package.json` 里通常只有 `vue`/`vue-router` 等框架依赖，`@guanghe-pub/*` 由 workspace root 统一管理。

**判断规则**：

| 情况 | 结论 |
|---|---|
| workspace root `package.json` 包含 `@guanghe-pub/onion-ui` | 已安装，进行 Step 3b 确认是否已 import |
| workspace root `package.json` 不含，子包也不含 | 未安装，执行 `pnpm add @guanghe-pub/onion-ui` |
| 只有子包 `package.json` 包含 | 已安装，进行 Step 3b |

> **典型陷阱**：只读 `03-prototype/package.json`（通常只有 `vue` 和 `vue-router`），误判为「未接入」→ 错误输出「安装 onion-ui」的指令。

---

## Step 3b：入口文件 import 探查

在 workspace 层确认已安装后，还需确认实际是否已 import，避免「已装但未引入」：

1. 读取 `src/main.ts`（或 `main.js`）：
   - 是否已有 `import '@guanghe-pub/onion-ui/lib/base-css.css'`
   - 有 → 字体/基础样式已接入，直接使用
   - 无 → 需在 `main.ts` 顶部补充此 import

2. 读取 `src/styles/global.scss`（或 `index.scss`、`app.scss`、`main.scss`）：
   - 是否已有 `@import '@guanghe-pub/design-tokens/lib/tokens.css'`
   - 有 → design token CSS 变量已注入，直接使用 `var(--xxx)`
   - 无 → 需在样式入口文件顶部补充此 @import

**禁止**：不得凭 `package.json` 单一来源判定接入状态，必须读入口文件二次确认。

---

## Step 3c：CDN MCP 可用性确认

CDN MCP 的可用性**不依赖**子包或 workspace 的 `package.json`，而是看 MCP 服务器配置：

- 检查项目配置目录（如 `.cursor/projects/.../mcps/`）中是否存在 `user-@guanghe-pub/yc-cdn-mcp-server/` 目录
- 该目录存在 = **CDN MCP 已启用，可直接调用 `cdn_compress_and_upload`**
- 不存在 = CDN MCP 不可用，`img-` 图层降级为本地 `assets` 目录

**禁止**：不得因子包 `package.json` 中无此依赖就判定「CDN 不可用」，进而跳过 CDN 上传流程。

---

## Step 3d：依赖 skill 加载断言（硬阻断）

> 前置：编排器 Step 0c 已经强制 Read 了 5 个 `requires` skill。本步骤是在 phase-1 探查完成后做**断言**——校验那 5 个 Read 是否真的完成了，并把它们的"实际产物"落地到 audit 第 1.1 节。

如果 Step 0c 没真正 Read 入口文件而只是"声称读过"，会出现以下硬伤（本 skill 历史失败案例）：

| 跳过的 skill | 典型失败 |
|---|---|
| `figma-img-cdn-skill` | 凭印象编出"原型阶段不上 CDN / 生产化阶段才上 CDN"等不存在的分阶段路径，导致 `img-*` 节点全部本地 assets 化、违反默认规则 |
| `onion-ui-skill` | `icon-*` 节点不查 `OIIcon` 图标库就武断"无匹配"直接降级，缺乏证据 |
| `design-tokens` | 整页只命中 1~2 个 token，其余颜色/间距全部硬编码 |
| `responsive-layout-analysis` | 多断点页面在没做差异分析的情况下直接按单断点写代码 |
| `responsive-layout` | 写了 `@media` 但断点和团队 7 级体系不一致 |

**断言动作**：

1. 复核 audit 第 1.1 节 5 行是否齐全，每行的"已 Read"列是否都为 ✅；
2. 校验"关键产物"列是否为占位文字（如 `vX.X.X`、`...`），如有占位 → Read 没真正发生 → **回到 Step 0c 补读**；
3. 特别校验：
   - `figma-img-cdn-skill` 行必须显式写"CDN 上传为默认动作"——这是防止"原型阶段不上 CDN"这类虚构规则的校验签名；
   - `onion-ui-skill` 行必须写出具体 onion-ui 版本号；
   - `design-tokens` 行必须写出 `tokens.css` 的实际路径。

只有以上 3 项全部满足，才能进入 Step 4。

---

## 探查结论写入 figma-audit.md

完成三步 + 断言后，将结论写入（或追加到）项目目录中的 `figma-audit.md`。

> **单点真理**：第 1 节 / 第 1.1 节的完整字段表（含 `Figma MCP 使用通道` / `CDN MCP 可用` / 第 1.1 节 5 行依赖加载状态等）以 [implementation-audit-template.md](implementation-audit-template.md) 为权威源。下方仅为本阶段填写的速查骨架，**不得**作为完整字段清单使用；若发现速查骨架与权威源不一致，以权威源为准（同步漂移按 fix 处理）。

```markdown
## 1. 目标与项目上下文（速查骨架，完整字段以 implementation-audit-template.md 为准）

| 项 | 结论 |
|---|---|
| Figma nodeId | `[填写]` |
| 目标实现目录 | `[填写]` |
| 技术栈 | `[填写]` |
| 样式体系 | `[填写]` |
| Onion UI 状态 | `已安装 v[版本] / 未安装`（Step 3a 结果） |
| Onion UI base-css 已 import | `是 / 否，需补充`（Step 3b 结果） |
| design-tokens 已 import | `是 / 否，需补充`（Step 3b 结果） |
| CDN MCP 可用 | `是 / 否`（Step 3c 结果） |
| CDN 例外 | `无 / 用户决定不上 CDN，原因：__`（默认必为「无」） |
```

---

## 本阶段检查清单

- [ ] 是否向上查找了 `pnpm-workspace.yaml` 并定位到 workspace root？
- [ ] 是否读取了 **workspace root** 的 `package.json`（而不只是子包自己的）？
- [ ] 是否读取了 `src/main.ts` 确认 `onion-ui/lib/base-css.css` 是否已 import？
- [ ] 是否读取了样式入口文件确认 `design-tokens/lib/tokens.css` 是否已 @import？
- [ ] 是否通过 mcps 配置目录（而非 package.json）确认了 CDN MCP 可用性？
- [ ] 三步结论是否已写入 `figma-audit.md` 第 1 节？
- [ ] **Step 3d 断言通过：5 个 requires skill 全部 Read，且关键产物列无占位、无虚构？**
- [ ] **`figma-img-cdn-skill` 行包含"CDN 上传为默认动作"字样？**
- [ ] **第 1 节「CDN 例外」默认为「无」？写「用户决定」时引用了用户原话？**
