---
name: prd-change
description: >-
  需求群内查询飞书需求文档相对已发布基线有没有未发布改动。
  只给葱明-multica 在群里被 @ 时使用。产品在工作区插件里不使用本技能，发布走 /prd-publish。
---

# 需求变更查询

本技能不是产品工作区命令。产品只使用 `/prd-publish` 发布基线、发短通知并得到提交代码的引导。

本技能只回答需求群里的查询。不发发布通知，不引导提交代码，不调用 Multica，不前进基线。

## 查询

触发：需求群内有人 `@葱明-multica` 询问需求是否变更。

1. 取当前会话的 `chat_id`（`oc_` 前缀）。消息里已有 `project.feishu.cn` 工作项链接时，解析 `project_key` 和 `work_item_id`，执行：

```bash
meegle workitem get --work-item-id <id> --project-key <project_key> \
  --fields '["group_type"]' --format json
```

`value.group_id` 等于这个 `chat_id` 才算匹配。不相等就回复无法匹配，不改去查别的卡。

2. 没有工作项链接时，只查一次。`project_key` 用 `ruxiao`：

```bash
meegle workitem query --project-key ruxiao --format json --mql \
  "SELECT \`work_item_id\`, \`name\`, \`group_type\` FROM \`ruxiao\`.\`tec_prd\` WHERE \`group_type\` LIKE '%<chat_id>%'"
```

0 张、多于 1 张，或这次查询因为字段不能筛选而失败：回复无法匹配。不翻全空间，不换查询条件再试，不猜测变更内容。恰好 1 张：用同一个 `project_key` 再 `workitem get`，确认 `value.group_id` 仍等于 `chat_id`。

3. 匹配到唯一项目卡后，按显示名读取「需求文档」。历史交叉核对 key=`field_38aeca`，以当次字段为准。没有可用文档链接：回复无法匹配，不猜测。
4. 用 `lark-cli docs +fetch` 读取版本表最后一行和当前 `revision_id`。
5. 最后一行的版本号不是纯数字（空着、`待回读`，或 `5-n` / `9-n` 这类旧稿次编号）：回复无法判断有没有未发布改动。不要把它说成已漂移，也不要猜测改了什么。等这次需求用 `/prd-publish` 写出数字序号后再查。
6. 最后一行是纯数字时，它是 `R1`，表示追加这一行之前的文档序号。真实基线是追加之后的回读，不在这个单元格里。执行 `lark-cli docs +history-list --doc <文档> --page-size 20`。同一 `revision_id` 可能有多条历史，按 `revision_id` 去重，不要按条数计数。当前序号大于 `R1`、已拉取的历史里还没有这个当前序号、且 `has_more=true` 时，继续翻页。没看到当前序号之前，不得判定为无未发布改动。
7. 无未发布改动，满足任一条即可：
   - 当前 `revision_id` 等于 `R1`
   - 大于 `R1` 的 `revision_id` 只有一个，且当前 `revision_id` 等于这一个。这一次就是追加版本表行
   - 大于 `R1` 的 `revision_id` 有多个，但这些历史紧挨同一次追加版本表，能看到的变更只有版本表这一行
8. 大于 `R1` 的序号有多个，又看不出是不是只有版本表这一次写入：回复序号已经向前走，但不能确定是不是只写了版本表。不把当前正文说成已发布需求，也不断言存在未发布正文。
9. 能看到 `R1` 之后还有正文编辑，或当前序号比「唯一一个更大的序号」还大：回复存在未发布改动，仍以版本表最后一行为已发布基线。
10. 本技能只看飞书文档，不读本地 `prd.md`。工作区里的开发仍用 `prd.baseline.revision_id` 判断漂移。
11. 用户追问某次已发布变更：先引用版本表对应行。该行不够时才看飞书历史正文。历史不够或对不上行时，说明看不到具体句子，不编造。
