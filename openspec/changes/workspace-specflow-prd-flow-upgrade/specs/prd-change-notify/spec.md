# prd-change-notify

`/prd-publish` 在基线写好后发短通知并引导提交代码。群内查询由 `prd-change` 单独执行，产品工作区不把查询当作发布命令。

## ADDED Requirements

### Requirement: 发布短通知

`/prd-publish` 成功后，本地产品 Agent MUST 重新查找项目卡和需求群，不得沿用本会话里上次的查询结果。每一张命中的卡都要读 `group_id`。只有 `oc_` 前缀算有群。可发送群按 `chat_id` 去重。恰好 1 个时 MUST 直接 POST。多于 1 个时 MUST 只展示项目卡名称供产品多选，没有群的卡不可选；对每个选中且去重后的 `chat_id` 各 POST 一次，正文相同。命中多少张卡就读多少张，不得用总次数 3 次截断。用户本轮给出工作项链接，或 metadata 已有工作项 ID 时，MUST 只读这一张已绑定的卡。POST 地址是 `https://multica.yc345.tv/api/webhooks/autopilots/awt_2iYIQNOIX7Ekg5-cqvFjHoYZ7lKKsC4TJRr8owW5WmU`，body 含 `chat_id`、`doc_url`、`change_summary`、`publish_version`、`baseline_revision_id`。MUST NOT 在本机执行 `lark-cli im +messages-send`。找卡和读群 MUST 使用同一次解析出的 `project_key`；没有工作项链接时才用 `ruxiao`。工作项类型 MUST 来自 `workitem meta-types` 里显示名为「迭代需求」的 `type_key`，MUST NOT 把链接路径里的 `tec_prd` 当作类型。MUST NOT 建群，MUST NOT 调用 `notify_spec_published`。没有群、产品不选或 POST 失败时跳过发信，基线仍然有效。发布结果 MUST NOT 打印该 URL。

#### Scenario: 已有需求群

- **WHEN** 飞书项目卡存在且能找到需求群
- **AND** `/prd-publish` 成功
- **THEN** 已向需求更新通知 webhook 提交 `chat_id`、文档地址和更新内容
- **AND** 变更全文仍只在飞书版本表
- **AND** 群消息由葱明发送，本命令不把它说成已经送达

#### Scenario: 多个可发送群

- **WHEN** 同一需求文档命中多张项目卡，且其中至少两张有 `oc_` 群
- **AND** `/prd-publish` 的基线写入已经成功
- **THEN** 只展示项目卡名称，没有群的卡不可选
- **AND** 产品多选后，每个选中的群各提交一次 webhook

#### Scenario: 没有群

- **WHEN** 没有项目卡、命中的卡都没有 `oc_` 群，或产品在多选时不选
- **AND** `/prd-publish` 的基线写入已经成功
- **THEN** 跳过群消息，不建群
- **AND** 发布结果仍为成功

#### Scenario: 发送身份

- **WHEN** 需要发送发布短通知
- **THEN** 本机只 POST webhook
- **AND** 不执行 `lark-cli im +messages-send`

#### Scenario: 不走旧通知

- **WHEN** 本地执行 `/prd-publish`
- **THEN** 不调用 `notify_spec_published`，也不在本机用 bot profile 发群

### Requirement: 知识库地址与 docx 地址是同一文档

系统 MUST 用 `lark-cli wiki +node-get` 把文档地址解开为正文 `obj_token` 和知识库 `node_token`。`metadata.feishu.doc_token` MUST 是 `obj_token`，正文读写只用它。文档在知识库时，`doc_url`、`feishu_doc` 和 `prd.md` 末尾「飞书文档」MUST 写 `/wiki/<node_token>`，并保存 `wiki_token`。不在知识库时展示 docx 地址，`wiki_token` 为空。找项目卡时 MUST 同时匹配 `wiki_token` 与 `doc_token`；只有后者时只匹配 `doc_token`。wiki 地址解析失败或鉴权失败时 MUST 跳过找卡并写明原因，不得猜测 token。

#### Scenario: 项目卡保存知识库链接

- **WHEN** 项目卡「需求文档」是 `/wiki/<node_token>`，本地绑定的正文 token 是同一文档的 `obj_token`
- **THEN** 找卡命中这一张
- **AND** 本地展示地址写成该知识库链接

#### Scenario: 文档不在知识库

- **WHEN** `wiki +node-get` 对 docx 地址失败
- **THEN** 展示地址保持 docx
- **AND** 只用 `doc_token` 找卡

### Requirement: 发布后引导提交代码

`/prd-publish` 成功后，系统 MUST 引导产品把本次需求改动提交到代码仓库。

#### Scenario: 发布成功

- **WHEN** 基线发布成功
- **THEN** 结果中包含提交代码的引导
- **AND** 引导失败不回滚已写好的基线

### Requirement: 群内查询变更

需求群内 `@葱明-multica` 时，查询技能 MUST 用 `chat_id` 找到项目卡和需求文档。消息里已有工作项链接时，MUST 用该链接的 `project_key` 读取 `group_type`，且 `group_id` 必须等于 `chat_id`。没有链接时 MUST 只在 `ruxiao` 按「迭代需求」的 `type_key` 查询一次，MUST NOT 使用 `tec_prd`。0 张、多张或查询失败时 MUST 回复无法匹配，不得翻全空间。版本表最后一行等于已填写版本行数时，它是从 `1` 起的发布序号，MUST NOT 拿它和飞书 `revision_id` 比较；基线回读是 `docs +history-list` 里写入该行的 `revision_id`。最后一行大于已填写行数时，那是旧写法，该数字是追加前序号。查询 MUST 按 `revision_id` 去重，判断基线回读之后是否还有正文编辑。该技能 MUST NOT 发布基线或发送发布通知，也不是产品斜杠命令。

#### Scenario: 只有版本号回写

- **WHEN** 当前 `revision_id` 等于基线回读，或旧写法里等于格子中的追加前序号，或大于基线回读的序号只有一个且当前序号等于这一个
- **THEN** 回复没有未发布改动

#### Scenario: 同一次追加拆成多个序号

- **WHEN** 大于基线回读的序号有多个，且这些历史都是同一次追加版本表
- **THEN** 回复没有未发布改动

#### Scenario: 无法确认多次序号

- **WHEN** 大于基线回读的序号有多个，且看不出是不是只有版本表这一次写入
- **THEN** 回复序号已经向前走，但不能确定是不是只写了版本表
- **AND** 不把当前正文说成已发布需求，也不断言存在未发布正文

#### Scenario: revision 已前进

- **WHEN** 基线回读之后还能看到正文编辑，或当前序号比唯一一个更大的序号还大
- **THEN** 回复存在未发布改动
- **AND** 说明仍以版本表基线为准

#### Scenario: 旧稿次编号

- **WHEN** 版本表最后一行不是纯数字序号
- **THEN** 回复无法判断有没有未发布改动
- **AND** 不把它说成已漂移

#### Scenario: 追问某次变更

- **WHEN** 用户追问某次已发布变更的内容
- **THEN** 先引用版本表对应行
- **AND** 该行不足时才查看飞书历史

#### Scenario: 对不上

- **WHEN** 无法用 `chat_id` 匹配项目卡、需求文档或群
- **THEN** 说明无法匹配
- **AND** 不猜测变更内容
