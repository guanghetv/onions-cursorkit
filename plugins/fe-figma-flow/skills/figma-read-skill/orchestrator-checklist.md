# 编排器检查清单（A 组 + H 组）

> **何时阅读**：每个 Step 完成时勾选对应项。本文件是 SKILL.md 流程主线的"逐步勾选清单"，覆盖 Step 0a–3 的前置 A 组与跨 phase 切换的 H 组；Step 4–8 的 B–G 组在 [phase-2-audit-and-codegen.md](phase-2-audit-and-codegen.md) 末尾，Step 9 的验证 checklist 在 [phase-3-verification.md](phase-3-verification.md) 末尾。
>
> **使用约定**：复制本清单到执行上下文（或 audit 草稿），逐项勾选；A 组任一项未勾选 → 不得进入 Step 4；H 组阶段切换前的 Read 漏掉一次 → 立即补 Read。

---

## A 组：前置（Step 0a–3）

### Step 0a · 响应式前置

- [ ] 如需响应式适配，是否已完成 `responsive-layout-analysis` 多断点分析并获得用户确认？

### Step 0b · Figma MCP 通道选择

- [ ] 是否按 Step 0b 完成了 Figma MCP 通道选择，并将主路径 / 降级路径结果写入 `figma-audit.md` 第 1 节「Figma MCP 使用通道」一行？

### Step 0c · 依赖 skill 强制加载（硬阻断）

- [ ] **是否 Read 了全部 5 个 `requires` skill 入口文件？**（缺一即硬阻断）
  - [ ] `responsive-layout-analysis` Read 完成 / 已记录"不适用"理由
  - [ ] `responsive-layout` Read 完成 / 已记录"不适用"理由
  - [ ] `figma-img-cdn-skill` Read 完成
  - [ ] `onion-ui-skill` Read 完成
  - [ ] `design-tokens` Read 完成
- [ ] **`figma-audit.md` 第 1.1 节「依赖 skill 加载状态」5 行是否齐全？**

### Step 1–2 · MCP 调用

- [ ] 是否调用了 `get_design_context` 获取精确数据？
- [ ] 是否调用了 `get_screenshot` 保存设计稿截图？

### Step 3 · 依赖探查（含 3a/3b/3c/3d）

- [ ] 是否 Read 了 `phase-1-dependency-check.md` 并完成四步探查？
- [ ] **是否向上查找了 `pnpm-workspace.yaml` 并读取 workspace root 的 `package.json`？**（Step 3a）
- [ ] **是否读取了 `src/main.ts` 和样式入口文件确认实际 import 状态？**（Step 3b）
- [ ] **是否通过 mcps 目录（而非 package.json）确认了 CDN MCP 可用性？**（Step 3c）
- [ ] 三步探查结论是否已写入 `figma-audit.md` 第 1 节？
- [ ] **`figma-audit.md` 第 1 节「CDN 例外」是否为「无」？写「用户决定」时是否引用了用户原话？**
- [ ] **Step 3d 断言通过：5 个 `requires` skill 全部 Read 且关键产物列无占位（`vX.X.X` / `...`）？`figma-img-cdn-skill` 行显式写了"CDN 上传为默认动作"？**（断言不过须回 Step 0c 补读）

---

## B–G 组：审计 + 代码生成（Step 4–8）

> 完整逐项 checklist 见 [phase-2-audit-and-codegen.md](phase-2-audit-and-codegen.md) 末尾「生成代码前检查清单（B–G 组）」。在 Step 8 写入任何代码文件前必须全部勾选完毕。

---

## H 组：阶段切换

- [ ] 进入 Step 4 前，是否 Read 了 `phase-2-audit-and-codegen.md`？
- [ ] Step 4–8 完成后、进入 Step 9 前，是否 Read 了 `phase-3-verification.md`？
- [ ] Step 9 完成后，是否在 `figma-audit.md` 第 7 节追加了验证结论？
