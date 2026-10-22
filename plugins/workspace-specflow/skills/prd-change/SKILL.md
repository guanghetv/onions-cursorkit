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

2. 没有工作项链接时，只查一次。`project_key` 用 `ruxiao`。先 `meegle workitem meta-types --project-key ruxiao --format json`，取显示名为「迭代需求」的 `type_key`。历史交叉核对是 `62a00a85830291949c117b1c`，以当次列表为准。不得使用链接路径里的 `tec_prd`。列表失败或没有这个显示名：回复无法匹配。

```bash
meegle workitem query --project-key ruxiao --format json --mql \
  "SELECT \`work_item_id\`, \`name\`, \`group_type\` FROM \`ruxiao\`.\`<type_key>\` WHERE \`group_type\` LIKE '%<chat_id>%'"
```

0 张、多于 1 张，或这次查询因为字段不能筛选而失败：回复无法匹配。不翻全空间，不换查询条件再试，不猜测变更内容。恰好 1 张：用同一个 `project_key` 再 `workitem get`，确认 `value.group_id` 仍等于 `chat_id`。

3. 匹配到唯一项目卡后，按显示名读取「需求文档」。历史交叉核对 key=`field_38aeca`，以当次字段为准。没有可用文档链接：回复无法匹配，不猜测。字段里的地址可能是 `/wiki/<node_token>`。先 `lark-cli wiki +node-get --node-token "<url>" --format json`，用返回的 `obj_token` 读正文。命令失败且地址本身是 `/docx/` 或 `/doc/` 时，用 path 最后一段。wiki 地址解析失败：回复无法匹配，不猜测。
4. 用 `lark-cli docs +fetch --doc <obj_token>` 读完版本表最后一行和当前 `revision_id`。版本表被截断时不得判断。
5. 最后一行的版本号不是纯数字（空着、`待回读`，或 `5-n` / `9-n` 这类旧稿次编号）：回复无法判断有没有未发布改动。不要把它说成已漂移，也不要猜测改了什么。等这次需求用 `/prd-publish` 写出数字序号后再查。
6. 最后一行是纯数字时，先分清它是什么。数出版本表里已经填了版本号的行数，记为 N。最后一行等于 N：它是发布序号，不是飞书 revision。最后一行大于 N：旧写法，格子里的数字是追加该行之前的飞书序号。
7. 发布序号：执行 `lark-cli docs +history-list --doc <文档> --page-size 20`，找到写入「版本号等于这个数字」的那次 `revision_id`，记为基线回读。同一 `revision_id` 去重。当前序号还没出现在已拉取历史里且 `has_more=true` 时继续翻页。没看到当前序号，或找不到写入那一行的历史：不得判定为无未发布改动；找不到那一行时回复无法判断。
8. 旧写法：格子里的数字仍是追加前序号。当前序号等于它，也算还没有正文超出这次发布。基线回读取大于它、且属于同一次追加版本表的那些序号里最大的一个。历史里还没有当前序号且 `has_more=true` 时继续翻页。
9. 基线回读确定后，无未发布改动，满足任一条即可：
   - 当前 `revision_id` 等于基线回读
   - 旧写法里当前 `revision_id` 等于格子中的追加前序号
   - 大于基线回读的序号都紧挨同一次追加版本表，能看到的变更只有版本表这一行
10. 大于基线回读的序号有多个，又看不出是不是只有版本表这一次写入：回复序号已经向前走，但不能确定是不是只写了版本表。不把当前正文说成已发布需求，也不断言存在未发布正文。
11. 能看到基线回读之后还有正文编辑，或当前序号比「唯一一个更大的序号」还大：回复存在未发布改动，仍以版本表最后一行为已发布基线。
12. 本技能只看飞书文档，不读本地 `prd.md`。工作区里的开发仍用 `prd.baseline.revision_id` 判断漂移。版本号单元格不参与这个比较。
13. 用户追问某次已发布变更：先引用版本表对应行。该行不够时才看飞书历史正文。历史不够或对不上行时，说明看不到具体句子，不编造。
