# 写作规范落地

## Goal

飞书需求文档和 `prd.md` 都按《产品组 PRD 写作规范》写，测试从需求详情里的规则提取，不再依赖单独的验收章节。

## Requirements

- 以 `plugins/workspace-specflow/references/产品组PRD写作规范.md` 为主。规范正文已在 `6702435`。
- 七章模板、MODULE 内的验收 checklist、AI Review 改为对照新规范。正文不单设验收章节。
- 可测规则写在需求详情的规则、状态、异常里。同一规则只写一处。
- `/qa-spec` 从这些条目提取测试点。
- `/qa-spec` 除读取已确认的 `prd.md` 外，兼容用飞书 CLI 直接读取用户给出的飞书需求文档链接。
- `/qa-spec` 不阻断生成。未确认、一致性失败、无本地基线、版本表没有基线或 revision 已超过基线时，仍生成用例，只提示风险。有本地基线快照且正文已漂移时，用例按上一版快照生成，并提示飞书正文已超前。

## Acceptance Criteria

- [ ] 新生成的飞书正文和 `prd.md` 没有单独验收章
- [ ] AI Review 不再因为缺少验收 checklist 判失败
- [ ] `/qa-spec` 能从需求详情抽出可测规则
- [ ] `/qa-spec` 在给出飞书文档链接、且 revision 与版本表基线一致时，能用飞书 CLI 读取并生成测试 spec
- [ ] 未确认、一致性失败或文档已漂移时，`/qa-spec` 仍生成用例，并在结果里给出提示

## Notes

父任务：`10-19-workspace-specflow-prd-flow-upgrade`。
