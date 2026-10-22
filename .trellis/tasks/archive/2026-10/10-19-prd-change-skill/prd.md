# 产品变更

## Goal

产品在工作区里只使用 `/prd-publish`。发布成功后由该命令发短通知并引导提交代码。群内查询单独留给葱明-multica。

## Requirements

- `/prd-publish` 写好基线后，用当前登录账号发短消息：版本、文档链接、改了哪些 MODULE。全文留在飞书版本表。
- 没有飞书项目卡或没有需求群时跳过消息，基线发布仍然成功。不调用 Multica。
- 同一次发布引导产品提交代码。引导失败不回滚基线。
- `prd-change` 只处理需求群内 `@葱明-multica` 的查询：用 `chat_id` 找卡和需求文档，版本表最后一行是基线，与当前 `revision_id` 比较。它不发布、不发通知。

## Acceptance Criteria

- [ ] 产品发布路径只有 `/prd-publish`
- [ ] 有群时发出短通知，无群时发布仍成功
- [ ] 群内查询能区分「相对基线无未发布改动」和「有未发布改动」
- [ ] publish 成功后出现提交代码的引导

## Notes

父任务：`10-19-workspace-specflow-prd-flow-upgrade`。
