# three-way-sync

原型、飞书需求文档和 `prd.md` 在用户确认后保持一致。

## ADDED Requirements

### Requirement: 主路径先原型

系统 MUST 以先生成原型、再产出 `prd.md` 和飞书文档作为默认写入口。

#### Scenario: 新需求从原型开始

- **WHEN** 产品按主路径新建需求并要求出文档
- **THEN** 先有原型中的核心页面流程
- **AND** `/pm-spec` 默认只写本地 `prd.md`
- **AND** 飞书只在 `/prd-publish` 时写入。用户说「同步到飞书」就是这条命令，不单独 push

### Requirement: 确认后才改另外两端

任一端先改时，系统 MUST 先给出与另外两端的差异判断，并在用户确认后才写入。

#### Scenario: 先改飞书

- **WHEN** 飞书正文相对 `prd.md` 或原型有未确认差异
- **THEN** Agent 展示差异判断
- **AND** 用户确认前不改 `prd.md` 和原型

#### Scenario: 先改原型

- **WHEN** 原型相对飞书文档或 `prd.md` 有未确认差异
- **THEN** Agent 展示差异判断
- **AND** 用户确认前不改飞书文档和 `prd.md`

#### Scenario: 多轮只改本地

- **WHEN** 产品在 `/pm-spec` 里连续调整需求描述，且没有明确说同步到飞书
- **THEN** 每一轮仍展示原型、飞书文档和 `prd.md` 的差异
- **AND** 只更新本地 `prd.md`
- **AND** 不自动推飞书，也不自动改原型

#### Scenario: 同步到飞书就是发布

- **WHEN** 用户明确说「同步到飞书」或「推到飞书」，或要求 `/prd-feishu-sync push`
- **AND** 当前不在 `/prd-publish` 的写入步骤
- **THEN** 改走 `/prd-publish`
- **AND** 不在 push 之后结束

#### Scenario: 发布中的写入不再发布

- **WHEN** `/prd-publish` 执行到增量写入
- **THEN** 只跑 `/prd-feishu-sync` 的 push 写入步骤
- **AND** 不再调用 `/prd-publish`

#### Scenario: 草稿只是超前

- **WHEN** 飞书和原型都没有当前 `prd.md` 里没有的内容
- **AND** 用户执行 `/prd-publish`
- **THEN** 直接 push 当前 `prd.md`
- **AND** 不再因为本地新于上次同步而追问

#### Scenario: 另一端多了内容

- **WHEN** 飞书或原型有当前 `prd.md` 没有的内容
- **AND** 用户要发布或继续只改本地
- **THEN** 先展示这些差异
- **AND** 用户确认仍按当前 `prd.md` 继续之前，不覆盖这些内容

#### Scenario: 飞书先改贴回工作区

- **WHEN** 产品先在飞书改了文档，再把链接贴进会话并要求更新本地
- **THEN** Agent 先 Read `three-way-sync.md`
- **AND** 用绑定文档做 `docs +fetch`，同时读 `prd.md` 与原型
- **AND** 用户确认前不改本地，也不用旧稿 `push` 盖掉飞书手改
- **AND** 确认写回后把 `consistency.status` 标为 `unknown`，不在本步跑发布检查

### Requirement: 已有飞书文档禁止整篇覆盖

飞书文档已有内容时，系统 MUST NOT 整篇覆盖该文档。

#### Scenario: 增量失败

- **WHEN** 局部更新找不到目标块或 `revision_id` 冲突
- **THEN** 停止并询问重试局部更新或指定块
- **AND** 不执行 `overwrite`、清空重写或整篇替换

#### Scenario: 用户要求整篇重建

- **WHEN** 文档已有正文、表格、画板、评论或人工段落
- **AND** 用户要求整篇重建或全文覆盖
- **THEN** 仍不执行整篇覆盖
- **AND** 改为说明只能局部更新
