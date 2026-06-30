---
name: re-check
description: 在 YApi 契约到达后，按 Onion SDD 当前 change 范围重新对齐前端 mock、类型、API 层和测试。
---

# Re-check

本技能用于前端 T1 或初版实现完成后，后端 YApi 契约到达或发生更新，需要把已有实现从推断契约、mock 或 placeholder 对齐到真实接口。

## 触发

- “re-check”
- “对齐 YApi”
- “YApi 接口到了”
- “接口文档到了，继续对齐”
- 用户粘贴 YApi URL / interfaceID，且当前存在活跃 Onion change。

如果用户明确说“只拉 YApi”“只落盘接口契约”，只调用 `pull-yapi`，不要修改业务代码。

## 前置

1. 定位当前 `openspec/changes/<change-id>/`。
2. 调用 `pull-yapi` 的 T1 后落盘模式，确保 `backend-yapi-*.md` 已存在。
3. 读取：
   - `proposal.md`
   - `specs/**/spec.md`
   - `tasks.md`
   - `backend-yapi-*.md`
   - 当前分支相对 `main` / `master` / Trellis `base_branch` 的 diff

如果无法定位 change，不要直接改代码；提示用户先用 `/onsf-plan` 创建 change，或在 `/onsf-continue` 中指定 change-id。

如果 `user-yapi-common-mcp` 不可用，按 `pull-yapi` 的降级策略使用用户粘贴内容，但仍需落盘 `backend-yapi-*.md` 后再对齐。

## 范围收敛

只修改当前需求范围内的代码。范围按以下顺序求交集：

1. `proposal.md` frontmatter 的 `modules`（如有）。
2. 当前 feature branch diff。
3. YApi path、method、字段名对应的 API 层、mock、类型和测试。

如果无法收敛范围，只输出对齐表和建议，不自动修改代码。

## 对齐表

开始修改前输出：

```markdown
| 接口 | YApi 文件 | 命中文件 | 改动类型 | 风险 | 是否自动处理 |
|------|-----------|----------|----------|------|--------------|
```

当接口数 >= 3 或命中文件数 >= 5 时，先展示完整对齐表并向用户确认一次，再批量修改。

## 可自动处理

- 新增可选请求/响应字段。
- 补充响应字段到类型定义、mock、fixture。
- mock 值、字段名、错误码与 YApi 明确一致的调整。
- L1 契约/mock 测试和 L2 行为测试中的字段契约更新。

## 必须确认

以下变化可能破坏既有行为，必须先向用户确认：

- 删除或重命名响应字段。
- 字段从可选变为必填，或必填变为可选且影响表单/校验。
- 字段类型变化。
- method/path 变化。
- 错误码、权限语义或业务流程变化。
- 需要跨模块改动或触发 Tier 升级。

## 实施纪律

1. 先补或更新契约测试；没有测试框架时记录静态验证点。
2. 再改 API 层、类型、mock、fixture 和业务使用点。
3. 更新 `proposal.md` 或 `tasks.md` 中的接口契约状态，例如 `contract_source: yapi`。
4. 运行与本次命中文件相关的 lint/type/test；无法运行时说明原因。
5. 如 QA spec 与 YApi 冲突：请求/响应字段按 YApi，验收口径按 QA，冲突写入 `e2e-report.md` 或最终回复。

## 完成摘要

最终输出：

- 已对齐接口数。
- 未绑定或无法自动处理的接口数。
- 修改文件列表。
- 验证命令与结果。
- 仍需用户/后端/QA 裁决的问题。
