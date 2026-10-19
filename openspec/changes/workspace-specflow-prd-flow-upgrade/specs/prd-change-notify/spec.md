# prd-change-notify

`/prd-publish` 在基线写好后发短通知并引导提交代码。群内查询由 `prd-change` 单独执行，产品工作区不把查询当作发布命令。

## ADDED Requirements

### Requirement: 发布短通知

`/prd-publish` 成功后，本地产品 Agent MUST 在基线步骤之后立刻用当前登录账号、`lark-cli im +messages-send --as user` 发送短消息。找卡和读群 MUST 使用同一次解析出的 `project_key`；没有工作项链接时才用 `ruxiao`。群 MUST 来自项目卡 `group_type.value.group_id`，且为 `oc_` 前缀。消息只含版本表中的 `R1`、文档链接和变更的 MODULE。MUST NOT 使用 bot，MUST NOT 建群，MUST NOT 调用 `notify_spec_published`。

#### Scenario: 已有需求群

- **WHEN** 飞书项目卡存在且能找到需求群
- **AND** `/prd-publish` 成功
- **THEN** 群内收到短消息
- **AND** 变更全文仍只在飞书版本表

#### Scenario: 没有群

- **WHEN** 没有项目卡、项目卡多于一张，或 `group_id` 不是 `oc_` 前缀
- **AND** `/prd-publish` 的基线写入已经成功
- **THEN** 跳过群消息，不建群
- **AND** 发布结果仍为成功

#### Scenario: 发送身份

- **WHEN** 需要发送发布短通知
- **THEN** 命令包含 `--as user`
- **AND** 不使用 `--as bot`，也不省略 `--as`

#### Scenario: 不调用 Multica

- **WHEN** 本地执行 `/prd-publish`
- **THEN** 不创建 Multica 任务，不调用 Multica 发送通知

### Requirement: 发布后引导提交代码

`/prd-publish` 成功后，系统 MUST 引导产品把本次需求改动提交到代码仓库。

#### Scenario: 发布成功

- **WHEN** 基线发布成功
- **THEN** 结果中包含提交代码的引导
- **AND** 引导失败不回滚已写好的基线

### Requirement: 群内查询变更

需求群内 `@葱明-multica` 时，查询技能 MUST 用 `chat_id` 找到项目卡和需求文档。消息里已有工作项链接时，MUST 用该链接的 `project_key` 读取 `group_type`，且 `group_id` 必须等于 `chat_id`。没有链接时 MUST 只在 `ruxiao` / `tec_prd` 按 `group_type` 查询一次。0 张、多张或查询失败时 MUST 回复无法匹配，不得翻全空间。版本表最后一行记下的是写入该数字之前的序号 `R1`。查询 MUST 用 `docs +history-list` 按 `revision_id` 去重，判断 `R1` 之后是否还有新的文档序号。该技能 MUST NOT 发布基线或发送发布通知，也不是产品斜杠命令。

#### Scenario: 只有版本号回写

- **WHEN** 当前 `revision_id` 等于 `R1`，或大于 `R1` 的序号只有一个且当前序号等于这一个
- **THEN** 回复没有未发布改动

#### Scenario: 同一次追加拆成多个序号

- **WHEN** 大于 `R1` 的序号有多个，且这些历史都是同一次追加版本表
- **THEN** 回复没有未发布改动

#### Scenario: 无法确认多次序号

- **WHEN** 大于 `R1` 的序号有多个，且看不出是不是只有版本表这一次写入
- **THEN** 回复序号已经向前走，但不能确定是不是只写了版本表
- **AND** 不把当前正文说成已发布需求，也不断言存在未发布正文

#### Scenario: revision 已前进

- **WHEN** `R1` 之后还能看到正文编辑，或当前序号比唯一一个更大的序号还大
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
