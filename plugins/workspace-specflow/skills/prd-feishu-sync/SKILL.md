---
name: prd-feishu-sync
description: >-
  创建飞书需求文档、把飞书手改收回本地、查看绑定、换绑。
  只有已经处在 /prd-publish 第 4 步时，才用本技能做增量 push。
  Use when: 创建飞书 PRD、飞书回收、prd-feishu-sync create/reconcile/status/rebind、
  发布流程中的增量写入。
  用户说同步到飞书、推到飞书、发布飞书文档时，改走 /prd-publish，不要进入本技能。
---

# /prd-feishu-sync — PRD ↔ 飞书同步

## 定位

- 用户口头说把正文同步到飞书时，改走 `/prd-publish`，不要从本技能开始。`/prd-publish` 第 4 步调用本技能时，只做增量写入，不再转回发布。
- **写入步骤不做「能否开工 / 一致性通过」结论。**
- 契约层准源：本地 `prd.md`；飞书为人读 / 评审面。
- **飞书文档已有内容时禁止整篇覆盖**。XML 只是内容格式，**不等于**整篇覆盖。空文档首次创建除外。
- **飞书写入默认 XML**（`--doc-format xml`）；禁止默认用 markdown 创建/整段推送（会丢 callout/色表等样式）。
- **增量失败策略 = A**：定位失败 / revision 冲突时 **STOP 询问用户**，禁止改成整篇覆盖。

## 子命令

| 命令 | 用途 |
|---|---|
| `create` | `/req-new` 后创建飞书文档并写绑定。已有文档时不要 push，提示 `/prd-publish` 或 `rebind` |
| `push` | 只在 `/prd-publish` 第 4 步执行的增量写入。用户直接调用时改走 `/prd-publish`。`--stage` 忽略 |
| `pull` / `reconcile` | 飞书手改收回本地。这不是发布 |
| `status` | 绑定、门控、漂移摘要 |
| `rebind` | 显式更换飞书文档 |

用户侧不使用 `/prd-feishu-sync push`。`--stage v5|v9` 会被忽略。

## 前置

1. 当前为 specs 仓；定位 `requirements/<目录>/`（含 `prd.md`、`metadata.yaml`）。
2. `lark-cli` 可用；优先 `--as user`。执行前：`lark-cli auth status`；缺 scope 时用 `lark-cli auth login --scope "..." --no-wait --json`，展示 `verification_url` 与二维码，等用户完成后再继续。
3. 文档操作使用当前 CLI 支持的 `docs +fetch` / `+create` / `+update` 与 drive 上传能力；正文**独立配图**可用 `+media-insert`；**MODULE「图示」列 / 表格单元格 / callout 内禁止** `media-insert`（见「图片」硬规则）。参数以本机 `lark-cli docs --help` 为准。
4. 除 `create`/`rebind` 外，必须已有 `metadata.feishu.doc_token`。缺失时按「同一文档的 wiki 与 docx」从 `feishu_doc` / `doc_url` 解开后写回，禁止只取 URL path 最后一段当作 `doc_token`（知识库地址会解错）。`doc_token` 是正文 `obj_token`。`docs +fetch` / `+update` 只用它，不用知识库节点 token。

## 同一文档的 wiki 与 docx

知识库里打开的地址是 `/wiki/<node_token>`，正文读写地址是 `/docx/<obj_token>`。同一份文档会同时有这两个 token。项目卡「需求文档」常保存知识库地址，本地创建时先拿到 docx 地址。

绑定、换绑，以及 `/prd-publish` 找项目卡之前，对当前地址执行一次：

```bash
lark-cli wiki +node-get --node-token "<url>" --format json
```

host 先转成小写，去掉 query 和 fragment。展示地址沿用这个 host。

- 成功且有 `obj_token`：`doc_token` = `obj_token`。有 `node_token` 时 `wiki_token` = `node_token`，`doc_url` 与 `feishu_doc` 写成 `<host>/wiki/<node_token>`。没有 `node_token` 时 `wiki_token` 留空，展示地址写成 `<host>/docx/<obj_token>`。
- 命令失败，且输入路径是 `/docx/` 或 `/doc/`：文档不在知识库。`wiki_token` 留空，展示地址保持这条 docx URL，`doc_token` 取 path 最后一段。
- 命令失败，且输入路径是 `/wiki/`，或鉴权、网络失败：不要猜 token。创建和换绑停止并写明原因。发布找项目卡跳过，结果写明原因。已经在用的 `doc_token` 继续给正文读写。

`doc_url`、`feishu_doc` 和本地 `prd.md` 末尾「飞书文档」写展示地址。这一节不上传。历史目录不批量改，下次创建、换绑或发布时补齐。

## 写入格式硬规则（XML）

1. **`create` / `push` / 补插机器区：一律 `--doc-format xml`**（CLI 默认即 xml 时也须显式按 XML 组织内容）。
2. **禁止**用 markdown 作为默认创建/推送格式；仅当用户明确要求「导入 Markdown」且接受样式降级时，才可例外，并在输出中标明。
3. 本地 md 的 `> [!IMPORTANT]` / `> [!NOTE]` / `> [!WARNING]` **必须**转为飞书 `<callout>`（勿原样贴成引用段）。
4. 表头加 `background-color="light-blue"`；关键关注用红/橙 callout；回归用蓝/灰 callout。
5. MODULE「详细说明」**建议**拆成有序列表 / 分节 / 多行结构化块，按规则、状态、异常组织。**禁止**为凑格式再写一遍验收 checkbox。出现整格纯文字墙时 **warning 告警（不阻断 push）**。
6. 复杂流程优先 `<whiteboard type="mermaid">`。**禁止**把已有画板静默降级为 `<pre>`/`<code>` 文本箭头图。

## 飞书排版与读写规程（本技能内建）

写入或更新飞书可读内容时，**直接按下列规则执行**（不另调外部 `/fs-doc` 命令名，但**排版质量须达到同等可读**）：

**文风**

- 飞书需求文档正文写法以 `../../references/产品组PRD写作规范.md` 为准（来源 [产品组 PRD 写作规范 V1.0](https://guanghe.feishu.cn/docx/Cqtqd9BxJoUYAFxbXFocp2qYnWd)）。
- Agent 禁令以 `../../rules/agent-hard-rules.mdc` 为准。更新飞书文档时禁止删除已有评论；查询现有实现时必须先调用 `user-codewiki-mcp` 的 `search_wiki`。
- 用户可见正文用简体中文；专有名词/代码/路径保持英文。
- 简洁直接；重要段结论前置（callout 或短结论段）。
- 多维信息优先表格；流程/分支用 Mermaid 画板；风险与关键点用 callout。
- 契约段连续正文超过 6 行（裸段落）或 MODULE 说明整格文字墙：**warning 告警并建议拆成列表/表/callout，不阻断本次 push**。
- 只改目标区块，保留他人未改内容。

**视觉**

- 表头 `light-blue`；关键/风险列可用 light-orange / light-red。
- callout：红=必须/阻塞；蓝=主链路/信息；橙=待确认；绿=可选；灰=机器维护区。
- 宽页表格总宽约 1170–1190；短列窄、说明列宽；三列可参考 `110 + 530 + 530`。

**读写步骤**

1. 改前：对目标范围 `docs +fetch`，需要定位时用 `--detail with-ids`。定位可以先看局部，比对和写入前必须拿到每个契约 unit 的全文，尤其每个 MODULE 详细说明整格。截断或只剩开头和结尾，视为没读完，停止，不得当成没有差异。`revision_id` 跳号不是插入图片。
2. 改时：仅 `str_replace` / `block_replace` / `block_insert_after` / `block_delete` /（画板）`docs +whiteboard-update`；内容用 **XML**。表格/callout 内图片**不得**用 `media-insert`（见「图片」硬规则）。
3. 结构写尽量带精确 `revision`；冲突 → **STOP**（策略 A），重新 fetch 对账后等用户决定；**禁止**改用 `latest` 盲重试，**禁止**整篇 `overwrite`。
4. 改后：再 fetch；确认目标存在、邻接未误删、表格/画板/callout 结构正常；并跑「写后自检」。
5. 输出必须列出本次实际使用的 `docs +update --command …` 清单；文档已有内容时，清单中出现 `overwrite` → **判定失败**。

## 文档分区（人读优先，禁止裸 BEGIN/END）

顶层顺序固定：**写作规范正文在前，文末只有一块机器区**。变更记录只留正文里的版本表，由 `/prd-publish` 追加。不再创建「评审修改记录」。正文按写作规范组织；旧七章标题仅兼容。机器区不写「请勿手改」和操作说明。`push` 不写 ✅ / ⚠️ / ❌，也不把这块的 emoji 留成这三枚。

**硬禁令**：禁止在飞书正文出现裸文本  
`[PRD-SYNC:…:BEGIN]` / `[PRD-SYNC:…:END]`（严重影响可读性）。

机器定位用区标题 + 区内心跳码（行内 `<code>`，短小）：

| 区 | 人读形态 | 心跳码（区内一行即可） | 定位方式 |
|---|---|---|---|
| PRD_BODY | **无外层包裹**；按写作规范正文 | — | chapter-map 语义标题 |
| DOC_STATUS | 文末一块 callout，标题「文档状态」。emoji、底色、边框一起跟着下表变 | 块内同时有 `prd-sync:status:v1` 与 `prd-sync:check:v1` | 这一块 callout / 两个心跳码 |

改这一块时，emoji、`background-color`、`border-color` 和校验行一起换。不要只改底色，也不要只改校验行文字。

| 态 | emoji | background-color | border-color | 校验行 |
|---|---|---|---|---|
| 未校验 | 📎 | light-blue | blue | 未校验 |
| 通过 | ✅ | light-green | green | ✅ · 日期 · 报告路径 |
| 告警 | ⚠️ | light-orange | orange | ⚠️ · 日期 · 可读性约 N 处 · 报告路径 |
| 失败 | ❌ | light-red | red | ❌ · 日期 · 报告路径 |

通过、告警、失败只由 `/prd-check` 写入。`push`、reconcile、rebind 只能写回未校验态。

### create 时 XML 骨架（示意）

标题等于 `metadata.name`。正文与 `req-new/references/templates.md` 的空骨架一致：需求概述、版本表、背景与目标、需求详情。背景、目标、本次范围只留标题。飞书版本表只有日期、版本号、PM、变更内容，不建「对应 spec / demo」。不写空的关键关注、回归范围、Feature List、关联材料、数据观察，不预置 `MODULE-N`，不写 `-` 占位，不把技能说明写进正文。

```xml
<title>需求名称</title>

<h2>需求概述</h2>
<!-- 概述一段 + 需求类型/影响范围表 + 版本表 + 背景与目标（三节只留标题）+ 空的需求详情表。不写 MODULE-N，不写 -。 -->

<callout emoji="📎" background-color="light-blue" border-color="blue">
  <p><b>文档状态</b></p>
  <p><b>同步绑定</b> <code>prd-sync:status:v1</code></p>
  <p>{metadata.id} · skeleton · requirements/…/prd.md</p>
  <p><b>校验</b> <code>prd-sync:check:v1</code></p>
  <p>未校验</p>
</callout>
```

校验结论只由 `/prd-check` 按四态表改 emoji、底色、边框和校验行。可读性明细写在 `prototypes/prd-check-YYYY-MM-DD.md`，飞书只在校验行带摘要。更新时保留同步绑定行。

| 行 | create | push | reconcile 写 md | /prd-check |
|---|---|---|---|---|
| 同步绑定 | 写入 id、阶段、路径 | 可更新这一行 | 否 | 保留，不改结论 |
| 正文 | 空骨架 | 契约 unit 增量更新 | 契约 → 本地 | 否 |
| 校验 | **必须**未校验态 | 改了契约正文则重置为未校验态，不写通过或失败 | 写了本地契约则同样重置为未校验态 | **覆盖**为通过、告警或失败态 |

**存量兼容**：若文档仍含旧版裸 `[PRD-SYNC:…:BEGIN/END]`，下次 `push` / `rebind` / check 写区前须迁移：删掉裸 marker。分开的「同步绑定」和「校验」，以及旧的可读性、一致性，下次写入时合并成文末一块「文档状态」，两行心跳码都留下，删掉多余块。已有「评审修改记录」或 `prd-sync:review:v1`：表内有文字时，先把非空行摘进本次 push 结果，再删掉该区；不写入版本表。不改需求正文，禁止整篇覆盖。

## 章节与同步单元（语义优先）

权威匹配表见 [`references/chapter-map.md`](references/chapter-map.md)。

完整表见 `references/chapter-map.md`。常用 unit：`contract.overview` / `versions` / `background` / `goal` / `scope` / `critical` / `regression` / `features` / `MODULE-N` / `details` / `materials` / `observability`。旧 `narrative.background` / `narrative.value` 映射为 `contract.background` / `contract.goal`，**不再删除**。

**定位顺序**：unit key → 标题关键词 → 序号兼容。禁止只靠「3.1/3.2」判断。  
背景与目标是契约正文的一部分，可按用户确认后的差异增量同步。不得为补洞而改写契约小节的展示序号或前移后续章节。

## 安全硬约束

违反任一条 → **停止写飞书**。

1. **文档已有内容时禁止整篇覆盖**，包括 `overwrite`、清空重写、用新正文替换整篇。即使用户要求「整篇重建 / 全文覆盖」也不执行，改为局部更新。空文档首次 `create` 不受此限。已有飞书评论仍禁止删除；评论或被评论的正文确实要删时，须单独说明并得到用户第二次明确确认。  
   **增量失败不得降级为 overwrite**（策略 A：STOP 询问）。
2. 禁止静默覆盖：用户未确认的背景/目标改动、已有 whiteboard、远端与本地同 MODULE 均相对基线有改动时的任一侧。
3. 禁止把本地绝对路径写入飞书；禁止上传无关图片。
4. 缺 `space:folder:create` 等必要 scope 时不得静默降级到云盘根目录（除非用户明确同意并在输出标明）。
5. 未确认不得把 reconcile 结果写入 `prd.md`。
6. 本技能不得输出「一致性通过 / 可开工」。
7. **禁止**写入裸 `[PRD-SYNC:…:BEGIN/END]`；**禁止**默认 markdown 写飞书。
8. **禁止**用 `<pre>`/`代码块箭头图` 顶替或删除已有流程图画板后宣称同步成功。
9. **禁止**删除已有飞书评论、回复、reaction 和评论锚点。评论内容或被评论正文确实要删除时，须得到用户第二次明确确认；只同意更新或重建不够。

**稿次**

5 稿 / 9 稿已取消。`push` 不区分 `--stage v5|v9`。传入这些参数时忽略，并在结果里说明。

不因为正文仍有「背景」「价值」而拒绝推送。`feishu.v9_synced=true` 只表示旧数据曾经按 9 稿同步过，不阻止本次 push。

push 成功后写 `last_synced_stage=current`，并记录读到的 `feishu_revision`。这不是基线。基线只由 `/prd-publish` 写入 `prd.baseline`。

## 增量同步策略（module-row）

- 首次 `create`：允许整篇创建骨架（**XML**）并生成 manifest（此为新建，不是对已有文档的 overwrite）。
- 已有文档：比较「当前飞书」与「本地最新 prd」，manifest 只作 block/图片/画板缓存，不作唯一真相。
- 普通契约章节：优先最小段落 `block_replace` / `str_replace`，写入内容为 **XML 片段**（局部内容仍用 xml，不是整篇覆盖）。
- MODULE：说明拆成列表/分节；表格行级增删改；图示列走下方「图片」硬规则（**禁止**用 `media-insert` 填单元格）。
- 单元 hash 须含图片文件 sha256，不只比路径。
- 远端手工改动与本地同 unit 均变 → 报告冲突，不静默覆盖。
- **定位不到目标 block / revision 冲突 / 局部写入失败** → **STOP**，展示失败 unit 与可选方案（重试 fetch / 用户手工指定 block）。文档已有内容时**禁止**整篇重建或 `overwrite`。

## 流程图 / 画板保活

| 场景 | 必须做法 |
|---|---|
| 本地有 Mermaid / 主流程源，飞书尚无画板 | 插入 `<whiteboard type="mermaid">…</whiteboard>` |
| 飞书已有 whiteboard | **不得删块用文本顶替**；用 `docs +whiteboard-update` 或仅 `block_replace` 该画板块 |
| Mermaid 写入/渲染失败 | **保留旧画板**（若有）+ warning；**禁止**降级为 `<pre>` 后标成功 |
| Manifest | 记录 `unit → board_token / block_id / mermaid_hash`；hash 不变则跳过 |

保护白名单（普通 `push` 永不碰）：已有 whiteboard、人工插图/评论锚点块。本地 `prd.md` 末尾「飞书文档」不上传，也不参与契约 diff。背景与目标按 `/prd-publish` 第 2 步已经做出的决定增量更新，不得整节清空，也不要在发布里再追问一次。已有「评审修改记录」按存量兼容删除，不再保护。「文档状态」不在白名单：契约正文有变更时必须重置为未校验态。例外只有 `/prd-publish` 追加的版本表基线行：这一行不重置，emoji、底色、边框和校验结论保持 `/prd-check` 刚写上的那一态。旧的一致性、可读性块合并进这一块后删除，不再保护。

## 图片（硬规则）

> 事故根因备忘：`docs +media-insert --selection-with-ellipsis` 命中表格/callout 内文本时，图片会落到**顶层祖先块外**；上传成功 ≠ 位置正确。MODULE「图示」列不得用该命令「凑合插入」。

### 决策树

| 目标位置 | 唯一首选 | 禁止 |
|---|---|---|
| MODULE「图示」列 / 任意表格单元格 / callout 内 | `docs +update --command block_replace`（或单元格内可接受的 `block_insert_after`）写入 `<img …/>` | `docs +media-insert`（含 `--selection-with-ellipsis` / `--before`） |
| 正文独立配图（非表格、非 callout） | `docs +media-insert --file`（默认可追加末尾） | 用独立块冒充「已进入图示列」 |

### 表格「图示」列写法

1. 在需求目录为 cwd，用相对路径（**推荐** `path="@./…"`；勿写本机绝对路径）：

   ```bash
   # cwd = requirements/<需求目录>/
   lark-cli docs +update --doc <doc_token> --as user --doc-format xml \
     --command block_replace --block-id <图示单元格内段落/块 id> \
     --content '<img path="@./images/xxx.png" width="320" caption="说明"/>'
   ```

2. 多图可同一单元格连续多个 `<img …/>`。
3. `path` 报 `2127` / Invalid local resource path 时的 fallback（按序，**不得跳到表格外**）：
   1. 确认 cwd 正确，改用 `@./相对路径`
   2. 若已有上传 token：`<img src="<file_token>" …/>` 回填**同一单元格**
   3. 仍失败 → **STOP**，报告失败 unit；**禁止**降级为「先 `media-insert` 到表格外再口头说明」
4. 可选：先 `drive +upload` 到需求同名文件夹拿 `file_token`，再以 `src` 写入单元格（与上式等价，仍须落在格内）。
5. 需要转换引用时用临时同步稿，**默认不把**飞书 token 写回正式 `prd.md`。
6. manifest 记录 folderToken 与图片 sha256→fileToken / block_id 映射；未变化则复用。
7. 飞书不能把 Drive `/file/` 页 URL、需 SSO 的 pages 链接当图片直链 `href`（易 302/鉴权失败）。

## Manifest

路径建议：`requirements/<目录>/prd-feishu-sync-manifest.json`

```json
{
  "schema_version": 1,
  "docUrl": "",
  "docToken": "",
  "strategy": "module-row",
  "assetFolder": { "name": "", "folderToken": null },
  "baseline": {
    "sourceCommit": null,
    "feishuRevision": null,
    "syncedAt": null,
    "stage": null
  },
  "units": {}
}
```

## 写后自检

**硬项（不通过则不得宣称同步成功）**

1. 全文**无**裸 `[PRD-SYNC:` 字符串。
2. 文末只有一块「文档状态」callout，同时含 `prd-sync:status:v1` 与 `prd-sync:check:v1`。仍是两块时，本次写入须合并后再结束。旧的可读性、一致性不得残留。
3. PRD 正文按写作规范语义结构。关键关注、回归只在有内容时出现；出现时必须是 callout，不能留下 `> [!IMPORTANT]` 原文。没有这两节不算失败，不要为了通过检查补空 callout。空骨架没有 `MODULE-N` 不算失败；正文已经写了规则、状态或异常时，缺少 `MODULE-N` 才失败。
4. `create`/`push` 使用了 **XML** 写入路径；文档已有内容时，command 清单中**不得**出现 `overwrite`。
5. 若本地/基线存在流程画板：飞书对应位置仍为 whiteboard（不得只剩文本箭头 `<pre>`）。
6. 若本次同步含 MODULE「图示」/表格配图：目标表格片段内 `<img>` 数量 = 预期；**同名图不得残留在表格外**（有则 `block_delete` 后复读）；仅表格外有图、格内无图 → **同步失败**。

**告警项（不阻断同步成功）**

- 数据表缺表头底色（对话 warning）。
- 文字墙不在 push 里下结论。完整位置和拆分建议由 `/prd-check` 写入本地报告。

## 意图路由

1. 用户要把当前正文同步到飞书、推到飞书，或直接说 `/prd-feishu-sync push`，且当前不是 `/prd-publish` 第 4 步：不要进入 push。改走 `/prd-publish`。
2. 「同步回来 / 按飞书改本地 / 飞书里我已经改过了」走 reconcile。贴了绑定文档并说更新需求、改范围或这条先不做了，先写入本地 `prd.md`。两条都在写完后按 `three-way-sync.md` 的「文档更新后的二次确认」引导 `/prd-publish`，不在本技能里直接发布。不要先改飞书再拉回。
3. create、status、rebind 仍在本技能。create 结束后建议 `/pm-spec`，不要问是否发布空骨架。
4. 已经在 `/prd-publish` 第 4 步：只执行下面的 push 写入。禁止再调用 `/prd-publish`，禁止在本步跑 `/prd-check`。

---

### create

1. 已有 `doc_token` → 停止，提示继续 `/pm-spec`，或二次确认后 `/prd-publish`，或 `rebind`。不要在这里 push，也不要直接进入发布。
2. 标题用 `metadata.name`。name 里如果还套着 `【】` 或末尾 `PRD` / `prd`，先按 `req-new` Step 2 清洗并写回 `metadata.name`，不改已经建好的目录名。按上文 **XML 骨架** 创建空骨架，文末只放一块未校验态「文档状态」。不创建评审修改记录，也不再单独建同步绑定、校验、可读性、一致性多块。
3. **`lark-cli docs +create ... --as user --doc-format xml`**（禁止默认 markdown）。
4. 按「同一文档的 wiki 与 docx」解析刚创建的地址，再写回 `metadata.feishu.*`（含 `wiki_token`）与 `feishu_doc`。`last_synced_stage=skeleton`；`v9_synced=false`；`consistency.status=unknown`；初始化 manifest。把展示地址写到本地 `prd.md` 末尾的「飞书文档」。已有这一节就替换地址，没有就追加。不要把这一节写入飞书。
5. `+fetch` 跑写后自检；确认校验行存在且无裸 BEGIN/END。

### push

0. 当前不是 `/prd-publish` 第 4 步：停止，不写入。改走 `/prd-publish`。
1. 已经在 `/prd-publish` 第 4 步。忽略 `--stage v5|v9|auto`。发布第 2 步已经决定写入，本步不再追问，禁止再调用 `/prd-publish`，禁止跑 `/prd-check`。不因仍有背景章节而 REJECT。
2. `+fetch` 飞书（with-ids）；若仍有旧裸 marker → **先迁移**再改契约（迁移也用局部替换，禁止整篇 overwrite）。
3. 按 chapter-map **语义 unit** 与 MODULE 算 diff。声明不把校验行写成通过或失败，不改未变更的 whiteboard。若存在评审修改记录则按存量兼容删除。背景与目标按发布第 2 步已经确认的范围增量更新。
4. 按「XML 片段 + 排版规程 + 增量策略」**局部**写入；MODULE「图示」列必须走「图片」硬规则（`block_replace` + `<img …/>`，**禁止** `media-insert`）；**不得**清空背景与目标；**不得**把校验行写成 ✅ / ⚠️ / ❌，也不得把 emoji 留成这三枚；**不得** `overwrite`。本次 push 不上传「对应 spec / demo」，也不写快照路径。飞书版本表还有这一列时，不论其他格子有没有变化，都删掉表头和格子。本地 `prd.md` 保留该列。契约正文按去掉 `<span text-color="red">` 后的纯文本比较。文字没变的块不要改，已有红色留在原处。改写带红色的片段之前先记下已经标红的句子；替换时没改的红句必须把 span 写回去，禁止用纯文本把旧红色洗掉。这次新改的句子先写纯文本，由 `/prd-publish` 在校验通过后只给相对上一份基线的新句子加红色，并补回被洗掉的历史红句。正文哈希按去掉这种 span 后的纯文本计算。
5. 流程/Mermaid：按「画板保活」表执行；写入失败 → **STOP**（策略 A），不得文本顶替后继续。
6. 任 unit 定位失败 / revision 冲突 → **立即 STOP**，询问用户。文档已有内容时不得整篇覆盖。
7. 本次若改了契约正文：在同一块「文档状态」里重置为未校验态（emoji、底色、边框、校验行一起改），`metadata.consistency.status=unknown`。同步绑定行保留。若仍是分开的两块，或还有旧的可读性、一致性，先合并成这一块再重置。没有这块则在文末插入。机器区若仍在正文前，本步一并移到文末。不在本步扫描文字墙。
8. 回读 + 写后自检（含 command 清单，以及图示位置）；更新 `last_synced_*`、`feishu_revision`、manifest；`last_synced_stage=current`。不因本次 push 把 `v9_synced` 设为 true，也不写 `prd.baseline`。  
   不得把校验行写成已通过。

### pull / reconcile

飞书 → 本地的正路，只用于拉回。用户只贴飞书链接、说「同步回来 / 按飞书改本地」且未点名本命令时，也按本节执行，不要整篇覆盖 `prd.md`。绑定文档上的新决定不走本节。

1. **Read** `../../references/three-way-sync.md`，并按其中「飞书先改、贴回工作区」执行。
2. 用绑定 `doc_token` 做 `docs +fetch`（契约区与可选评论）。聊天粘贴的正文只当线索，不能代替 fetch。评审修改记录不作为契约。
3. 同时读本地 `prd.md`、原型（`prototypes/` / `assets/`，没有则记缺失），以及上次 baseline/manifest。形成决策项（`ED`/`CM`/`FB`），并写明是否还要改原型。
4. **STOP**；用户确认接受项后，只写入同意的本地契约 unit / MODULE（含背景与目标）或原型；不改契约展示序号。禁止用本地旧稿再 `push` 盖掉本次飞书手改。写回版本表时不追加版本行，并保留本地「对应 spec / demo」：按版本号对上已有行的快照路径。禁止因为飞书没有这一列就删掉本地表头或已有路径。写回 `prd.md` 时去掉 `<span text-color="red">` 和对应 `</span>`，不把颜色留在本地。
5. 更新 metadata：`last_synced_*`、`feishu_revision`、`consistency.status=unknown`。若写了本地契约，把同一块「文档状态」**重置为未校验态**（emoji、底色、边框、校验行一起改，不要写成通过）。不跑 `/prd-check`，不写基线。
6. 写完停住。按 `three-way-sync.md` 的「文档更新后的二次确认」再问是否发布，并说明下一步是 `/prd-publish`。第二次明确同意之前不进入发布。不要在 reconcile 里直接 push。

### status

打印绑定、`v9_synced`、`last_synced_*`、只读 `consistency`、契约漂移一句话。不写远端。

### rebind

展示旧/新目标 → **STOP 确认** → 按「同一文档的 wiki 与 docx」解析新地址并更新绑定（`doc_token`、`wiki_token`、展示用 `doc_url` / `feishu_doc`）；重置 sync 标记；在同一块「文档状态」里重置为未校验态（emoji、底色、边框、校验行一起改；XML，`prd-sync:check:v1`）。仍是分开的两块时先合并。本地 `consistency.status=unknown`。本地 `prd.md` 末尾「飞书文档」改成新的展示地址。换绑后停住，按 `three-way-sync.md` 二次确认并引导 `/prd-publish`。不要单独 push，也不要把校验留到下一次。

## 与工作区命令协作

| 命令 | 关系 |
|---|---|
| `/req-new` | 末尾必调 `create` |
| `/pm-spec` | 默认只改本地。写完后二次确认，再引导 `/prd-publish`。不在这里 push |
| `/prd-check` | 内容、对齐、可读性（本技能不替代） |
| `/prd-publish` | 第 4 步才调用本技能的 push。本技能不得再转回发布 |

## 输出

子命令、目标文档、是否真实写入、是否 XML（格式）、**实际 command 清单**、变更 unit、是否触碰画板、校验行是否仍为「未校验」、门控结果、写后自检、失败项。处在 `/prd-publish` 第 4 步时，把结果交回发布流程，不要再建议发布。  
若因策略 A 停下：明确写出卡住的 unit、原因、请用户选「重试局部 / 指定 block」。文档已有内容时不提供整篇覆盖。
