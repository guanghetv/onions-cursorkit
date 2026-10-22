# agent-hard-rules Specification

## Purpose
TBD - created by archiving change workspace-specflow-prd-flow-upgrade. Update Purpose after archive.
## Requirements
### Requirement: 写作禁令始终生效

插件启用时，系统 MUST 注入写作禁令。禁令来自《产品组 PRD 写作规范》的执行底线，至少包括：不把需求写成功能名摘要，不因精简删除状态与异常，不编造未确认方案，不把视觉参数和接口字段写入正文，不用「由 AI 判断」或「同上」代替可判断规则。

#### Scenario: 写需求正文

- **WHEN** Agent 生成或更新飞书需求文档或 `prd.md`
- **THEN** 按 `rules/agent-hard-rules.mdc` 的写作禁令执行
- **AND** 不能只引用规范文件而不执行禁令

### Requirement: 评论删除须二次确认

更新需求飞书文档时，系统 MUST NOT 删除已有评论、回复、reaction 或评论锚点，除非用户对这次删除作出第二次明确确认。

#### Scenario: 普通更新

- **WHEN** Agent 局部更新已有需求文档
- **THEN** 已有评论仍在

#### Scenario: 需要删除评论内容

- **WHEN** 已有评论或其锚定正文确实要删除
- **THEN** Agent 先说明删除对象和原因
- **AND** 用户第二次明确确认前不删除

### Requirement: 查询实现先用 CodeWiki

产品询问现有功能或代码实现时，以及 `/pm-proto`、`/pm-spec` 开始扫描工作区或写正文之前，系统 MUST 先调用 `user-codewiki-mcp` 的 `search_wiki`，再结合 Cursor 当前工作区。

#### Scenario: 查询功能

- **WHEN** 产品询问某个功能或现有实现
- **THEN** 回答前已经调用 `search_wiki`，`query` 为所问功能
- **AND** 若当前是 Cursor 且工作区已打开，调用完成后再查看该工作区

#### Scenario: 画原型或写需求

- **WHEN** 执行 `/pm-proto` 或 `/pm-spec`，准备扫描工作区或写正文
- **THEN** 扫描或写正文前已经调用 `search_wiki`，`query` 为本轮页面、功能或现有流程
- **AND** 工作区扫描不能代替这次调用

#### Scenario: 调用失败

- **WHEN** `search_wiki` 调用失败
- **THEN** 说明失败原因后再查当前工作区
- **AND** 不把失败说成没有该功能

