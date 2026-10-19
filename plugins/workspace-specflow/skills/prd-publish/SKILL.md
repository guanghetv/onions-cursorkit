---
name: prd-publish
description: >-
  发布需求基线。用户说「同步到飞书」或「推到飞书」时也走本技能。
  必要时先做风险预检，再增量同步飞书并跑 /prd-check。
  没有 critical 后写入快照、版本表和 revision_id。`warn` 可以发布。第一次成功把 prd.status 设为 confirmed。
  Use when: 同步到飞书、推到飞书、一键发布 PRD、发布到飞书并校验、prd-publish。
---

# /prd-publish — 发布基线

稿次已取消。不接受 `--stage v5|v9` 作为产品阶段。若用户仍传入，忽略并在结果中说明。

## 流程

1. 定位需求目录与 `metadata.yaml`。
2. 发布会把当前 `prd.md` 写到飞书。开始前 Read `../../references/three-way-sync.md` 并读出原型、飞书和 `prd.md`。飞书、原型都没有当前 `prd.md` 里没有的内容时，这是草稿超前，直接进入下一步，不再追问。已有基线且本地正文偏离快照时，在发布结果里写明「相对上一版基线有未发布改动」，只多出版本表那一行不算。飞书或原型有当前 `prd.md` 没有的更新时，先展示差异；用户确认「仍按当前 `prd.md` 发布」后才继续，否则停止。
3. 风险预检：没有 `prototypes/prd-risk-precheck.md`、结论不可读，或 `prd.md` 新于 `prd.risk_precheck.last_checked_at` 时，先 Read 并执行 `/prd-risk`。结论为「需调整」则停止，不 push，不写基线，不发群通知。飞书保持原样。结论为「待补信息」时提醒后可继续。
4. 执行 `/prd-feishu-sync push` 的写入步骤（XML 增量；文档已有内容时禁止整篇覆盖）。这一步已经在发布流程里，禁止再调用 `/prd-publish`。发布第 2 步已经决定要写时，push 不再追问。
5. sync 失败则停止。不跑校验，不写基线，不把状态改成 `confirmed`，不发群通知。飞书可能只写了一部分，结果里写明停在哪个 unit。
6. sync 成功后执行 `/prd-check`。存在 critical 则停止，不写基线，不发群通知。`warn` 可以继续写基线。此时若停下，飞书正文已经是本次 `prd.md`，结果写明「飞书已更新，校验未通过，基线未写」。不要把这次说成发布成功。
7. 没有 critical 时前进基线，按顺序。先回读追加版本行之前的序号 `R1`，写入版本行后再回读 `R2`。`R2` 回读之后不再写飞书：
   1. 复制当前 `prd.md` 到 `snapshots/prd-baseline-<YYYY-MM-DD>.md`。同一天已存在则追加 `-HHMM`。快照是需求正文，不含下面即将追加的版本行。
   2. `lark-cli docs +fetch` 得到 `R1`。此时版本表还没有这一行。
   3. 在飞书和本地 `prd.md` 的版本表追加一行：日期、版本号 `R1`、变更 MODULE、快照路径。追加用局部更新，不整篇覆盖。不用 `5-n` / `9-n`。只追加这一行，不要改写文末「文档状态」，也不要把校验结论重置成未校验。这是本次发布的最后一次飞书写入。飞书追加失败则停止，不写 `R2`，不改 `confirmed`。
   4. 再 `+fetch` 得到 `R2`。写入 `prd.baseline.revision_id = R2`。同时把 `feishu.feishu_revision` 和 `feishu.last_synced_at` 更新为这次回读，`last_synced_stage=current`。manifest 里版本表 unit 的 hash 改成追加后的表。这一行已经在两端，以后的 `/prd-check` 不要把它当成未推送。**到此停止写飞书**，不要把 `R2` 写进版本表，也不要改「文档状态」。
   5. 写入 metadata 其余字段：
      - `prd.baseline.snapshot`
      - `prd.baseline.published_at`
      - `prd.baseline.row_revision_id = R1`（版本表里看见的序号）
      - `prd.status = confirmed`
      - 仅当原来不是 `confirmed` 时写 `prd.confirmed_at`
   6. 若仍有旧字段 `prd.stage` 且取值为 `v5_pending`、`v5_confirmed`、`v9_pending`：改为 `confirmed`。不新增 v5/v9 字段。
8. 基线写好后立刻执行下面的「发短通知」，做完才结束本命令。通知或提交引导失败，不回滚第 7 步，也不把 `prd.status` 改回 `pending`。用户执行本命令即表示同意按模板发到该需求群，不要再追问要不要发。

## 发短通知

本步是第 8 步的正文，不是可选附录。这条通知不是 `notify_spec_published`，也不走 `multica-feishu-collab-notify`。只借用它读群的方式。发信身份是当前登录的产品用户。不调用 Multica，不创建 Multica 任务，不写 Issue 评论。群内查询不在本命令里做。

禁止：

- `lark-cli im +messages-send --as bot`，以及不写 `--as`（默认就是 bot，群里会显示成飞书 CLI 应用）
- `--profile congming-multica` 或任何 bot profile
- `meegle workitem update` 去建群，包括 `group_type=auto`
- `lark-cli im +chat-create`、`+chat-search`、`+chat-list` 代替项目卡上的群
- 把葱明-multica 或默认飞书 CLI 拉进群
- 消息里写变更全文、测试 spec 链接，或套用「产品 SPEC 已发布 · 可进入技术评审」

`meegle workitem get` 和 `im +messages-send` 各自最多 3 次（含首次）。鉴权失败、工作项不存在、当前用户不在群：立刻停止发消息，不要换参数再试，不要 `sleep`。停止发消息不影响已经写好的基线。

### 1. 找到项目卡

文档地址用 `metadata.feishu.doc_url`。`doc_token` 用 `metadata.feishu.doc_token`，没有则取 URL path 的最后一段。比较前把 host 转成小写，去掉 query 和 fragment。

下面的 `<project_key>` 全程用同一个值。用户本轮给了 `project.feishu.cn` 工作项链接，或 metadata 里已有工作项 ID：从链接解析 `project_key` 和 `work_item_id`，不做下面 1 到 3，直接读群。没有链接时 `project_key` 用 `ruxiao`，再按下面查询。

1. `meegle project search --project-key <project_key>` 确认空间可用。不可用则跳过发消息，写明原因，不要改去搜其它空间。
2. `meegle workitem meta-fields --project-key <project_key> --work-item-type tec_prd` 确认「需求文档」的 `field_key`。历史交叉核对是 `field_38aeca`，以当次显示名为准。
3. 查询：

```bash
meegle workitem query --project-key <project_key> --format json --mql \
  "SELECT \`work_item_id\`, \`name\`, \`<需求文档 field_key>\` FROM \`<project_key>\`.\`tec_prd\` WHERE \`<需求文档 field_key>\` LIKE '%<doc_token>%'"
```

0 张：跳过，结果写「未找到项目卡」。多于 1 张：跳过，列出工作项 ID，不挑一张。恰好 1 张：继续。

### 2. 读取需求群

```bash
meegle workitem get --work-item-id <id> --project-key <project_key> \
  --fields '["group_type"]' --format json
```

从 `work_item_fields` 里 `key=group_type` 的 `value.group_id` 取值。只有 `oc_` 前缀才算有群。空、`auto` 或其它值都算没有群：跳过发消息，结果写「项目卡还没有需求群」。不要补建群。

### 3. 用产品本人发送

先 `lark-cli auth status`。没有 user 登录：跳过，结果写「当前没有产品用户登录」，不要改成 bot。

正文只用这四行，版本号是版本表里的 `R1`：

```text
需求基线已发布
版本：<R1>
文档：<feishu.doc_url>
变更：<本次 MODULE，多项用顿号>
```

```bash
lark-cli im +messages-send \
  --as user \
  --chat-id "<oc_...>" \
  --idempotency-key "prd-baseline-<doc_token>-<R2>" \
  --text $'需求基线已发布\n版本：<R1>\n文档：<url>\n变更：<MODULE>'
```

同一 `R2` 的重试用同一个 idempotency key，避免一条基线发两次。下一次发布 `R2` 变了，才会再发一条。

发送失败：发布仍成功，结果写明 `chat_id`、失败原因和已重试次数。不要改 `--as bot` 重发。

### 4. 引导提交代码

通知步骤结束后，引导产品把当前需求目录和本次基线快照提交到 specs 仓库。不代替用户执行 `git commit`，除非用户在本轮明确要求提交。用户不提交，不回滚基线。

## 约束

- 同步细则以 `prd-feishu-sync` 为准。
- 第一次成功发布后，再次发布不改变 `prd.status`，只替换基线指针。
- 不调用 Multica。
- 发布结束后，当前飞书 `revision_id` 必须等于 `prd.baseline.revision_id`（`R2`）。版本表该行显示 `R1`，这是追加该行之前的序号。群消息和版本表都使用 `R1`。
