---
name: prd-publish
description: >-
  发布需求基线。本地文档已经写完，用户第二次确认发布，或单独说「同步到飞书」「推到飞书」时走本技能。
  更新需求、改范围、这条先不做了、从飞书拉回：先写入本地并二次确认，确认前不要进入本技能。
  必要时先做风险预检，再增量同步飞书并跑 /prd-check。
  没有 critical 后写入快照、版本表和 revision_id。`warn` 可以发布。第一次成功把 prd.status 设为 confirmed。
  Use when: 同步到飞书、推到飞书、发布、prd-publish、一键发布 PRD、发布到飞书并校验。
---

# /prd-publish — 发布基线

稿次已取消。不接受 `--stage v5|v9` 作为产品阶段。若用户仍传入，忽略并在结果中说明。

还没有把本轮改动写入本地，或还没有按 `three-way-sync.md` 做文档更新后的二次确认时：不要从本技能开始。先写入本地并停住询问。

## 流程

1. 定位需求目录与 `metadata.yaml`。
2. 发布会把当前 `prd.md` 写到飞书。开始前 Read `../../references/three-way-sync.md`，并读完原型、飞书和 `prd.md`。每个 MODULE 的详细说明必须整格读完。只看到开头和结尾、中间被截掉，或把 `revision_id` 跳号当成插入了图片，都算没读完，停止发布。飞书、原型都没有当前 `prd.md` 里没有的规则句子时，这是草稿超前，直接进入下一步，不再追问。已有基线且本地正文偏离快照时，在发布结果里写明「相对上一版基线有未发布改动」，只多出版本表那一行不算。飞书或原型有一句当前 `prd.md` 没有的规则时，先并列引用两边原句；用户确认「仍按当前 `prd.md` 发布」后才继续，否则停止。进入本命令时的「发布 / 同步到飞书」只表示同意发布本地稿；不能代替这句「仍按当前 `prd.md` 发布」。
3. 风险预检：没有 `prototypes/prd-risk-precheck.md`、结论不可读，或 `prd.md` 新于 `prd.risk_precheck.last_checked_at` 时，先 Read 并执行 `/prd-risk`。结论为「需调整」则停止，不 push，不写基线，不发群通知。飞书保持原样。结论为「待补信息」时提醒后可继续。
4. 执行 `/prd-feishu-sync push` 的写入步骤（XML 增量；文档已有内容时禁止整篇覆盖）。这一步已经在发布流程里，禁止再调用 `/prd-publish`。发布第 2 步已经决定要写时，push 不再追问。
5. sync 失败则停止。不跑校验，不写基线，不把状态改成 `confirmed`，不发群通知。飞书可能只写了一部分，结果里写明停在哪个 unit。
6. sync 成功后执行 `/prd-check`。存在 critical 则停止，不写基线，不发群通知。`warn` 可以继续写基线。此时若停下，飞书正文已经是本次 `prd.md`，结果写明「飞书已更新，校验未通过，基线未写」。不要把这次说成发布成功。
7. 没有 critical 时前进基线，按顺序。先回读追加版本行之前的序号 `R1`，写入版本行后再回读 `R2`。`R2` 回读之后不再写飞书：
   1. 复制当前 `prd.md` 到 `snapshots/prd-baseline-<YYYY-MM-DD>.md`。同一天已存在则追加 `-HHMM`。快照是需求正文，不含下面即将追加的版本行。
   2. `lark-cli docs +fetch` 得到 `R1`。此时版本表还没有这一行。
   3. 在飞书和本地 `prd.md` 的版本表追加一行。日期用当天。版本号是发布序号，不写 `R1`，也不看本步刚复制的那份快照。进入第 7 步之前没有 `prd.baseline.snapshot` 时写 `1`。已有 `prd.baseline.version` 时加 `1`。还没有这个字段、但进入第 7 步之前已经有快照时写 `2`，格子里旧的飞书序号（例如 51）不往上加。PM 留空。序号为 `1` 时变更内容留空。之后对照上一份快照，把规则差异写进变更内容；飞书这一格用 `<span text-color="red">…</span>`，本地 `prd.md` 写同样的句子，不写颜色。不要把「校验：可开工」写进这一格。最后一列写 `snapshots/<文件名>`。追加用局部更新，不整篇覆盖。不用 `5-n` / `9-n`。只追加这一行，不要改写文末「文档状态」，也不要把校验结论重置成未校验。这是本次发布的最后一次飞书写入。飞书追加失败则停止，不写 `R2`，不改 `confirmed`。若本地 `prd.md` 末尾还没有「飞书文档」，先用当前已有地址补上，这一节不写入飞书。展示地址在本步第 7 点解析后再改成知识库链接。
   4. 再 `+fetch` 得到 `R2`。写入 `prd.baseline.revision_id = R2` 和 `prd.baseline.version`（刚写入的发布序号）。同时把 `feishu.feishu_revision` 和 `feishu.last_synced_at` 更新为这次回读，`last_synced_stage=current`。manifest 里版本表 unit 的 hash 改成追加后的表。这一行已经在两端，以后的 `/prd-check` 不要把它当成未推送。**到此停止写飞书**，不要把 `R1` 或 `R2` 写进版本号，也不要改「文档状态」。
   5. 写入 metadata 其余字段：
      - `prd.baseline.snapshot`
      - `prd.baseline.published_at`
      - `prd.baseline.row_revision_id = R1`（追加版本行之前的飞书序号，不出现在版本表）
      - `prd.status = confirmed`
      - 仅当原来不是 `confirmed` 时写 `prd.confirmed_at`
   6. 若仍有旧字段 `prd.stage` 且取值为 `v5_pending`、`v5_confirmed`、`v9_pending`：改为 `confirmed`。不新增 v5/v9 字段。
   7. 按 `prd-feishu-sync` 的「同一文档的 wiki 与 docx」解析当前文档地址，写回 `doc_token`、`wiki_token` 和展示用 `doc_url` / `feishu_doc`。本地 `prd.md` 末尾「飞书文档」改成展示地址。这一节不写入飞书。解析失败按该节处理，不猜 token。
8. 基线写好后立刻执行下面的「发短通知」，做完才结束本命令。通知或提交引导失败，不回滚第 7 步，也不把 `prd.status` 改回 `pending`。用户执行本命令即表示同意按模板发到该需求群，不要再追问要不要发。

## 发短通知

本步是第 8 步的正文，不是可选附录。找群仍在本命令。找到群之后不在本机发信，改为 POST Multica Autopilot「需求更新通知」的 webhook，由葱明发送。不走 `notify_spec_published`，不走 `multica-feishu-collab-notify`，不写 Issue 评论。群内查询不在本命令里做。

禁止：

- `lark-cli im +messages-send`（含 `--as user`、`--as bot`，以及省略 `--as`）
- `--profile congming-multica` 或任何本机 bot profile 发这封通知
- webhook 失败后改用当前用户重发
- `meegle workitem update` 去建群，包括 `group_type=auto`
- `lark-cli im +chat-create`、`+chat-search`、`+chat-list` 代替项目卡上的群
- 把葱明-multica 或默认飞书 CLI 拉进群
- 在发布结果里打印 webhook URL 或 token
- 消息里写变更全文、测试 spec 链接，或套用「产品 SPEC 已发布 · 可进入技术评审」

`meegle workitem get` 最多 3 次（含首次）。鉴权失败、工作项不存在：立刻停止发通知，不要换参数再试，不要 `sleep`。停止发通知不影响已经写好的基线。

### 1. 找到项目卡

找卡前先完成第 7 步第 7 点的地址解析。展示地址是 `metadata.feishu.doc_url`。正文 token 是 `doc_token`。知识库节点是 `wiki_token`，没有则为空。群消息里的 `doc_url` 用展示地址。

下面的 `<project_key>` 全程用同一个值。用户本轮给了 `project.feishu.cn` 工作项链接，或 metadata 里已有工作项 ID：从链接解析 `project_key` 和 `work_item_id`，不做下面 1 到 4，直接读群。没有链接时 `project_key` 用 `ruxiao`，再按下面查询。wiki 地址解析失败，或鉴权、网络失败：跳过下面 1 到 4，结果写明原因。docx 地址不在知识库时继续，只用 `doc_token`。

1. `meegle project search --project-key <project_key>` 确认空间可用。不可用则跳过发消息，写明原因，不要改去搜其它空间。
2. `meegle workitem meta-types --project-key <project_key> --format json`，取显示名为「迭代需求」的 `type_key`。链接路径里的 `tec_prd` 不是类型。历史交叉核对是 `62a00a85830291949c117b1c`，以当次列表为准。列表里没有这个显示名：跳过发消息，不要改用 `tec_prd`。
3. 用这个 `type_key` 调 `meegle workitem meta-fields --project-key <project_key> --work-item-type <type_key> --page-num 1`，确认「需求文档」的 `field_key`。历史交叉核对是 `field_38aeca`，以当次显示名为准。
4. 查询。`FROM` 使用上面的 `type_key`，不得写 `tec_prd`：

有 `wiki_token` 时两个 token 都匹配。没有时只匹配 `doc_token`，不要写空的 `LIKE '%%'`。

```bash
# 有 wiki_token
meegle workitem query --project-key <project_key> --format json --mql \
  "SELECT \`work_item_id\`, \`name\`, \`<需求文档 field_key>\` FROM \`<project_key>\`.\`<type_key>\` WHERE \`<需求文档 field_key>\` LIKE '%<wiki_token>%' OR \`<需求文档 field_key>\` LIKE '%<doc_token>%'"

# 没有 wiki_token
meegle workitem query --project-key <project_key> --format json --mql \
  "SELECT \`work_item_id\`, \`name\`, \`<需求文档 field_key>\` FROM \`<project_key>\`.\`<type_key>\` WHERE \`<需求文档 field_key>\` LIKE '%<doc_token>%'"
```

0 张：跳过，结果写「未找到项目卡」。多于 1 张：跳过，列出工作项 ID，不挑一张。恰好 1 张：继续。

### 2. 读取需求群

```bash
meegle workitem get --work-item-id <id> --project-key <project_key> \
  --fields '["group_type"]' --format json
```

从 `work_item_fields` 里 `key=group_type` 的 `value.group_id` 取值。只有 `oc_` 前缀才算有群。空、`auto` 或其它值都算没有群：跳过发消息，结果写「项目卡还没有需求群」。不要补建群。

### 3. 调用需求更新通知 webhook

找到群后直接 POST 这个地址，不要改地址，也不要先查环境变量：

`https://multica.yc345.tv/api/webhooks/autopilots/awt_2iYIQNOIX7Ekg5-cqvFjHoYZ7lKKsC4TJRr8owW5WmU`

`change_summary`：第一次发布写「首次发布」；之后用本行变更内容的纯文本，不带颜色标记。

```bash
curl -sS -X POST "https://multica.yc345.tv/api/webhooks/autopilots/awt_2iYIQNOIX7Ekg5-cqvFjHoYZ7lKKsC4TJRr8owW5WmU" \
  -H "Content-Type: application/json" \
  -d '{"chat_id":"<oc_...>","doc_url":"<feishu.doc_url>","change_summary":"<更新内容>","publish_version":"<发布序号>","baseline_revision_id":"<R2>"}'
```

HTTP 2xx：结果写「已提交需求更新通知，由葱明发群」。不要写成群里已经收到。非 2xx 或网络失败：发布仍成功，结果写明状态码或失败原因。不要改用本机 `im +messages-send` 重发。同一 `R2` 的重试可以再 POST 一次，幂等由葱明按 `baseline_revision_id` 处理。

### 4. 引导提交代码

通知步骤结束后，引导产品把当前需求目录和本次基线快照提交到 specs 仓库。不代替用户执行 `git commit`，除非用户在本轮明确要求提交。用户不提交，不回滚基线。

## 约束

- 同步细则以 `prd-feishu-sync` 为准。
- 第一次成功发布后，再次发布不改变 `prd.status`，只替换基线指针。
- 不在本机发群。短通知只 POST「需求更新通知」webhook，由葱明发送。
- 发布结束后，当前飞书 `revision_id` 必须等于 `prd.baseline.revision_id`（`R2`）。版本表和群消息使用发布序号 `1`、`2`、`3`。`R1` 只留在 `prd.baseline.row_revision_id`。
