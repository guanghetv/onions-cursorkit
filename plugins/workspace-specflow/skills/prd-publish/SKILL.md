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
4. 执行 `/prd-feishu-sync push` 的写入步骤（XML 增量；文档已有内容时禁止整篇覆盖）。这一步已经在发布流程里，禁止再调用 `/prd-publish`。发布第 2 步已经决定要写时，push 不再追问。契约正文按纯文本比较后增量写入。文字没变的块不要改，已有红色留在原处。改写带红色的片段之前，先记下该片段里已经标红的句子。替换时，片段里没改的红句必须把 `<span text-color="red">` 一起写回，禁止用纯文本把旧红色洗掉。本次相对上一份基线新改的句子先按纯文本写入，红色在第 7 步补上。
5. sync 失败则停止。不跑校验，不写基线，不把状态改成 `confirmed`，不发群通知。飞书可能只写了一部分，结果里写明停在哪个 unit。
6. sync 成功后执行 `/prd-check`。存在 critical 则停止，不写基线，不发群通知。`warn` 可以继续写基线。此时若停下，飞书正文已经是本次 `prd.md`，结果写明「飞书已更新，校验未通过，基线未写」。不要把这次说成发布成功。
7. 没有 critical 时前进基线，按顺序。先按下面「版本更新标红」更新飞书，再回读追加版本行之前的序号 `R1`，写入版本行后再回读 `R2`。`R2` 回读之后不再写飞书：
   1. 复制当前 `prd.md` 到 `snapshots/prd-baseline-<YYYY-MM-DD>.md`。同一天已存在则追加 `-HHMM`。快照是需求正文，不含下面即将追加的版本行，也不含颜色。
   2. 按「版本更新标红」更新飞书。没有上一份基线快照则跳过。失败则停止，不取 `R1`，不追加版本行，不写 `R2`，不改 `confirmed`。然后 `lark-cli docs +fetch` 得到 `R1`。此时版本表还没有这一行。
   3. 在飞书和本地 `prd.md` 的版本表追加一行。日期用当天。版本号是发布序号，不写 `R1`，也不看本步刚复制的那份快照。进入第 7 步之前没有 `prd.baseline.snapshot` 时写 `1`。已有 `prd.baseline.version` 时加 `1`。还没有这个字段、但进入第 7 步之前已经有快照时写 `2`，格子里旧的飞书序号（例如 51）不往上加。PM 留空。序号为 `1` 时变更内容留空。之后对照上一份快照，把规则差异写进变更内容；飞书这一格用 `<span text-color="red">…</span>`，本地 `prd.md` 写同样的句子，不写颜色。不要把「校验：可开工」写进这一格。正文里的红色已在取 `R1` 之前写完，本步不要改那些句子的颜色，也不要改掉旧版本行里已经标红的变更内容。本地 `prd.md` 这一行的最后一列「对应 spec / demo」写 `snapshots/<文件名>`。飞书版本表没有这一列，不写快照路径。飞书表里若已有「对应 spec / demo」，这次追加时删掉该列（表头和已有格子一起删）。追加用局部更新，不整篇覆盖。不用 `5-n` / `9-n`。只追加这一行，不要改写文末「文档状态」，也不要把校验结论重置成未校验。这是本次发布的最后一次飞书写入。飞书追加失败则停止，不写 `R2`，不改 `confirmed`。若本地 `prd.md` 末尾还没有「飞书文档」，先用当前已有地址补上，这一节不写入飞书。展示地址在本步第 7 点解析后再改成知识库链接。
   4. 再 `+fetch` 得到 `R2`。写入 `prd.baseline.revision_id = R2` 和 `prd.baseline.version`（刚写入的发布序号）。同时把 `feishu.feishu_revision` 和 `feishu.last_synced_at` 更新为这次回读，`last_synced_stage=current`。manifest 里版本表 unit 的 hash 改成追加后的表。这一行已经在两端，以后的 `/prd-check` 不要把它当成未推送。**到此停止写飞书**，不要把 `R1` 或 `R2` 写进版本号，也不要改「文档状态」。
   5. 写入 metadata 其余字段：
      - `prd.baseline.snapshot`
      - `prd.baseline.published_at`
      - `prd.baseline.row_revision_id = R1`（追加版本行之前的飞书序号，不出现在版本表）
      - `prd.status = confirmed`
      - 仅当原来不是 `confirmed` 时写 `prd.confirmed_at`
   6. 若仍有旧字段 `prd.stage` 且取值为 `v5_pending`、`v5_confirmed`、`v9_pending`：改为 `confirmed`。不新增 v5/v9 字段。
   7. 按 `prd-feishu-sync` 的「同一文档的 wiki 与 docx」解析当前文档地址，写回 `doc_token`、`wiki_token` 和展示用 `doc_url` / `feishu_doc`。本地 `prd.md` 末尾「飞书文档」改成展示地址。这一节不写入飞书。解析失败按该节处理，不猜 token。
8. 基线写好后立刻执行下面的「发短通知」，做完才结束本命令。通知或提交引导失败，不回滚第 7 步，也不把 `prd.status` 改回 `pending`。每次发布都重新查项目卡和群，不得沿用本会话里上次的查询结果。只有一个可发送群时直接发，不要再追问要不要发。有多个可发送群时，只请产品按项目卡名称多选。

## 版本更新标红

校验已经通过、还没有取 `R1` 时执行。红色只增不洗：只给相对上一份已发布基线新出现或改写的规则句子加红色。已经标红的历史句子保持红色，不要因为它们和版本 1 相同、或不是这一次的变更，就把红色去掉。不整篇覆盖，也不要按相对版本 1 的累计差异把整篇再涂一遍。本地 `prd.md` 和快照不写颜色。

不在这里改版本表和文末「文档状态」。图示、图片、原型链接、未改表头不标红。旧版本行里已经标红的变更内容保持红色。

没有上一份基线快照（第一次发布）：跳过。不要把当时的全文标红。上一份快照文件读不到：停止，不取 `R1`，不追加版本行。不要改去和版本 1 比。

对照底稿是进入第 7 步之前 `prd.baseline.snapshot` 指向的上一份快照。用它对比本步刚复制的新快照。不要拿新文件和自己比，也不要拿版本 1 的快照当这次的对照。两边比纯文本时先去掉 `<span text-color="red">` 和对应 `</span>`，只用来判断句子变没变，不用来决定去掉红色。范围是需求概述、背景与目标、本次范围、需求详情（含 `MODULE-N` 和状态表）、关键关注、回归范围、Feature、关联材料、数据观察。标红不改 manifest 的正文哈希，哈希仍按去掉 span 后的纯文本。

- 相对上一份快照新出现或改写了的规则句子：飞书用 `<span text-color="red">这句</span>` 包住整句。
- 相对上一份快照没有变化的句子：不改颜色。原来是红色的保持红色，原来不是红色的不要新涂。
- 这次新增的 MODULE、表格行、列表项：其中的规则文字标红。同一处没改的旧行不要再涂。
- 只删除、正文里已经没有的句子：不另找相邻文字涂红。删掉的差异写在版本表这一行。

句子按编号项、单元格里的一条说明，或独立段落。不把半句拆开标红，也不要因为一句变了就把整格或整张表标红。

用 `str_replace` 或单元格级 `block_replace` 写入 XML。第 4 步若已把没改的红句写成纯文本，这一步按改写前记下的句子把红色补回。定位失败就停止，不改成整篇覆盖。写完再读一遍上述章节：这一次相对上一份快照的新句子是红色，改动前已经是红色的句子仍是红色，这次没改、原来也不是红色的句子仍是默认色，图片还在原格。禁止把「标红」写进需求句子。

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

每张卡的 `meegle workitem get` 失败时，这一张可以再试，同一张最多 3 次（含首次）。鉴权失败、工作项不存在：立刻停止发通知，不要换参数再试，不要 `sleep`。停止发通知不影响已经写好的基线。命中多少张就读多少张，不要因为总次数到达 3 就停。

### 1. 找到项目卡

找卡前先完成第 7 步第 7 点的地址解析。展示地址是 `metadata.feishu.doc_url`。正文 token 是 `doc_token`。知识库节点是 `wiki_token`，没有则为空。群消息里的 `doc_url` 用展示地址。

下面的 `<project_key>` 全程用同一个值。用户本轮给了 `project.feishu.cn` 工作项链接，或 metadata 里已有工作项 ID：只读这一张卡，不做下面 1 到 4 的全文检索。这是按已绑定的卡发通知，不表示同一文档上的其它卡也要通知。没有链接、也没有已保存的工作项 ID 时，`project_key` 用 `ruxiao`，再按下面查询。wiki 地址解析失败，或鉴权、网络失败：跳过下面 1 到 4，结果写明原因。docx 地址不在知识库时继续，只用 `doc_token`。

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

0 张：跳过，结果写「未找到项目卡」。命中之后对每一张卡读群，不要只读第一张。

### 2. 读取需求群

对每一张命中的卡：

```bash
meegle workitem get --work-item-id <id> --project-key <project_key> \
  --fields '["group_type"]' --format json
```

从 `work_item_fields` 里 `key=group_type` 的 `value.group_id` 取值。只有 `oc_` 前缀才算有群。空、`auto` 或其它值都算没有群。记下工作项 ID、项目卡名称 `name`，有群时再记下 `chat_id`。同一个 `chat_id` 只保留一次：名称合并到这一条，后面只 POST 一次。不要补建群。

按去重后的 `chat_id` 计数。恰好 1 个：直接 POST，不要再问。多于 1 个：只向产品展示项目卡名称；没有群的卡标成不可选。产品可以多选有群的卡。不选或取消：跳过发通知，基线仍有效。对每个选中且去重后的 `chat_id` 各 POST 一次，正文相同，不要把多个群放进同一次请求。可发送的群是 0 个：跳过发消息；有卡但都没有群时，结果写「项目卡还没有需求群」。

### 3. 调用需求更新通知 webhook

每个要发的 `chat_id` 单独 POST 这个地址一次，不要改地址，也不要先查环境变量：

`https://multica.yc345.tv/api/webhooks/autopilots/awt_2iYIQNOIX7Ekg5-cqvFjHoYZ7lKKsC4TJRr8owW5WmU`

`change_summary`：第一次发布写「首次发布」；之后用本行变更内容的纯文本，不带颜色标记。

```bash
curl -sS -X POST "https://multica.yc345.tv/api/webhooks/autopilots/awt_2iYIQNOIX7Ekg5-cqvFjHoYZ7lKKsC4TJRr8owW5WmU" \
  -H "Content-Type: application/json" \
  -d '{"chat_id":"<oc_...>","doc_url":"<feishu.doc_url>","change_summary":"<更新内容>","publish_version":"<发布序号>","baseline_revision_id":"<R2>"}'
```

HTTP 2xx：结果写「已提交需求更新通知，由葱明发群」。不要写成群里已经收到。非 2xx 或网络失败：发布仍成功，结果写明状态码或失败原因。不要改用本机 `im +messages-send` 重发。同一个群的重试可以再 POST 一次，幂等由葱明按 `baseline_revision_id` 和 `chat_id` 处理。不同群不算重复。

### 4. 引导提交代码

通知步骤结束后，引导产品把当前需求目录和本次基线快照提交到 specs 仓库。不代替用户执行 `git commit`，除非用户在本轮明确要求提交。用户不提交，不回滚基线。

## 约束

- 同步细则以 `prd-feishu-sync` 为准。再次发布时，只给相对上一份已发布基线新出现或改写的规则句子加红色；已经标红的历史句子和版本表旧行保持红色，不去掉。本地 `prd.md` 与快照不写颜色。
- 第一次成功发布后，再次发布不改变 `prd.status`，只替换基线指针。
- 不在本机发群。短通知只 POST「需求更新通知」webhook，由葱明发送。
- 发布结束后，当前飞书 `revision_id` 必须等于 `prd.baseline.revision_id`（`R2`）。版本表和群消息使用发布序号 `1`、`2`、`3`。`R1` 只留在 `prd.baseline.row_revision_id`。
