---
name: prd-feishu-sync
description: >-
  将工作区需求 prd.md 与飞书文档深度绑定并同步（创建、增量推送、回收对账、状态、换绑）。
  Use when: 同步 PRD 到飞书、创建飞书 PRD、推送需求文档、飞书回收、prd-feishu-sync、
  feishu sync、发布飞书文档、MODULE 行同步。不写校验结论（那是 /prd-check）。
---

# /prd-feishu-sync — PRD ↔ 飞书同步

## 定位

- **只做同步与绑定**，不做「能否开工 / 一致性通过」结论。
- 契约层准源：本地 `prd.md`；飞书为人读 / 评审面。
- **飞书文档已有内容时禁止整篇覆盖**。XML 只是内容格式，**不等于**整篇覆盖。空文档首次创建除外。
- **飞书写入默认 XML**（`--doc-format xml`）；禁止默认用 markdown 创建/整段推送（会丢 callout/色表等样式）。
- **增量失败策略 = A**：定位失败 / revision 冲突时 **STOP 询问用户**，禁止改成整篇覆盖。

## 子命令

| 命令 | 用途 |
|---|---|
| `create` | `/req-new` 后创建飞书文档并写绑定 |
| `push` | 契约层增量推送到飞书（`--stage skeleton\|v5\|v9`，可选 `--force`） |
| `pull` / `reconcile` | 飞书契约/反馈 vs 本地，确认后写 md |
| `status` | 绑定、门控、漂移摘要 |
| `rebind` | 显式更换飞书文档 |

用法：`/prd-feishu-sync push`。`--stage v5|v9` 会被忽略。

## 前置

1. 当前为 specs 仓；定位 `requirements/<目录>/`（含 `prd.md`、`metadata.yaml`）。
2. `lark-cli` 可用；优先 `--as user`。执行前：`lark-cli auth status`；缺 scope 时用 `lark-cli auth login --scope "..." --no-wait --json`，展示 `verification_url` 与二维码，等用户完成后再继续。
3. 文档操作使用当前 CLI 支持的 `docs +fetch` / `+create` / `+update` 与 drive 上传能力；正文**独立配图**可用 `+media-insert`；**MODULE「图示」列 / 表格单元格 / callout 内禁止** `media-insert`（见「图片」硬规则）。参数以本机 `lark-cli docs --help` 为准。
4. 除 `create`/`rebind` 外，必须已有 `metadata.feishu.doc_token`（可从 `feishu_doc` URL 解析后写回自愈）。

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

1. 改前：对目标范围 `docs +fetch`，需要定位时用 `--detail with-ids`；优先局部 scope。
2. 改时：仅 `str_replace` / `block_replace` / `block_insert_after` / `block_delete` /（画板）`docs +whiteboard-update`；内容用 **XML**。表格/callout 内图片**不得**用 `media-insert`（见「图片」硬规则）。
3. 结构写尽量带精确 `revision`；冲突 → **STOP**（策略 A），重新 fetch 对账后等用户决定；**禁止**改用 `latest` 盲重试，**禁止**整篇 `overwrite`。
4. 改后：再 fetch；确认目标存在、邻接未误删、表格/画板/callout 结构正常；并跑「写后自检」。
5. 输出必须列出本次实际使用的 `docs +update --command …` 清单；文档已有内容时，清单中出现 `overwrite` → **判定失败**。

## 文档分区（人读优先，禁止裸 BEGIN/END）

顶层顺序固定：**写作规范正文在前，机器区全部在文档最底部**。底部顺序：同步绑定 → 校验。变更记录只留正文里的版本表，由 `/prd-publish` 追加。不再创建「评审修改记录」。正文按写作规范组织；旧七章标题仅兼容。机器区各用一行结论加心跳码，不写「请勿手改」和操作说明。`push` 不写 ✅ / ⚠️ / ❌。

**硬禁令**：禁止在飞书正文出现裸文本  
`[PRD-SYNC:…:BEGIN]` / `[PRD-SYNC:…:END]`（严重影响可读性）。

机器定位用区标题 + 区内心跳码（行内 `<code>`，短小）：

| 区 | 人读形态 | 心跳码（区内一行即可） | 定位方式 |
|---|---|---|---|
| STATUS | 灰色 callout，标题「同步绑定」 | `prd-sync:status:v1` | callout / 心跳码 |
| PRD_BODY | **无外层包裹**；按写作规范正文 | — | chapter-map 语义标题 |
| CHECK | 蓝/绿/橙/红 callout，标题「校验」 | `prd-sync:check:v1` | callout / 心跳码 |

### create 时 XML 骨架（示意）

```xml
<title>【…】PRD</title>

<h2>一、需求概述</h2>
<!-- 写作规范正文。机器区不得插在正文前面或中间。 -->

<callout emoji="🔗" background-color="light-gray" border-color="gray">
  <p><b>同步绑定</b> <code>prd-sync:status:v1</code></p>
  <p>{metadata.id} · skeleton · requirements/…/prd.md</p>
</callout>

<callout emoji="⏳" background-color="light-blue" border-color="blue">
  <p><b>校验</b> <code>prd-sync:check:v1</code></p>
  <p>未校验</p>
</callout>
```

校验结论只由 `/prd-check` 写成 ✅ / ⚠️ / ❌。可读性明细写在 `prototypes/prd-check-YYYY-MM-DD.md`，飞书只在这一行带摘要。

| 区 | create | push | reconcile 写 md | /prd-check |
|---|---|---|---|---|
| STATUS | 初始化 callout | 可更新这一行 | 否 | 否 |
| PRD_BODY | 写作规范正文骨架（XML 富样式） | 契约 unit 增量更新；背景与目标可同步 | 契约 → 本地 | 否 |
| CHECK | **必须**「未校验」 | 改了契约正文则重置为「未校验」，不写通过或失败 | 否 | **覆盖**为 ✅/⚠️/❌ |

**存量兼容**：若文档仍含旧版裸 `[PRD-SYNC:…:BEGIN/END]`，下次 `push` / `rebind` / check 写区前须迁移：删掉裸 marker。同步绑定、旧的可读性、旧的一致性若还在正文前面，用局部块移到文末。已有 `prd-sync:readability:v1` 或 `prd-sync:consistency:v1`：`push` 若重置校验，删掉这两块，改成一行「未校验」；`/prd-check` 写结论时同样删掉旧块，只留 `prd-sync:check:v1`。已有「评审修改记录」或 `prd-sync:review:v1`：表内有文字时，先把非空行摘进本次 push 结果，再删掉该区；不写入版本表。不改需求正文，禁止整篇覆盖。

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

保护白名单（普通 `push` 永不碰）：CONSISTENCY、已有 whiteboard、人工插图/评论锚点块。背景与目标仅在用户确认差异后增量更新，不得整节清空。已有「评审修改记录」按存量兼容删除，不再保护。

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
2. 存在「同步绑定」callout + `prd-sync:status:v1`；存在「校验」callout + `prd-sync:check:v1`。旧的可读性、一致性两块在本次写入后不得同时残留。
3. PRD 正文按写作规范语义结构；关键关注/回归为 **callout**（非 `> [!IMPORTANT]` 原文）。
4. `create`/`push` 使用了 **XML** 写入路径；文档已有内容时，command 清单中**不得**出现 `overwrite`。
5. 若本地/基线存在流程画板：飞书对应位置仍为 whiteboard（不得只剩文本箭头 `<pre>`）。
6. 若本次同步含 MODULE「图示」/表格配图：目标表格片段内 `<img>` 数量 = 预期；**同名图不得残留在表格外**（有则 `block_delete` 后复读）；仅表格外有图、格内无图 → **同步失败**。

**告警项（不阻断同步成功）**

- 数据表缺表头底色（对话 warning）。
- 文字墙不在 push 里下结论。完整位置和拆分建议由 `/prd-check` 写入本地报告。

## 意图路由

1. 识别子命令；未指定则根据话术推断并复述确认。
2. 执行下列对应流程。
3. 结束后可建议 `/prd-publish`（本技能不代替 `/prd-check`）。草稿 push 之后不要自动开检。

---

### create

1. 已有 `doc_token` → 停止，提示 `push` 或 `rebind`。
2. 标题用 `metadata.name`；按上文 **XML 骨架** 创建。先写写作规范正文，再在文末放同步绑定和校验「未校验」。不创建评审修改记录，也不再单独建可读性、一致性两块。
3. **`lark-cli docs +create ... --as user --doc-format xml`**（禁止默认 markdown）。
4. 写回 `metadata.feishu.*` 与 `feishu_doc`；`last_synced_stage=skeleton`；`v9_synced=false`；`consistency.status=unknown`；初始化 manifest。
5. `+fetch` 跑写后自检；确认校验行存在且无裸 BEGIN/END。

### push

1. 忽略 `--stage v5|v9|auto`。稿次已取消。
2. **Read** `../../references/three-way-sync.md`。读本地 `prd.md`（及原型，用于差异提示）。按该规范展示与飞书的差异，用户确认后再写。不因仍有背景章节而 REJECT。
3. `+fetch` 飞书（with-ids）；若仍有旧裸 marker → **先迁移**再改契约（迁移也用局部替换，禁止整篇 overwrite）。
4. 按 chapter-map **语义 unit** 与 MODULE 算 diff；展示变更清单，声明不把校验行写成通过或失败 / 未变更 whiteboard；若存在评审修改记录则按存量兼容删除；背景与目标仅更新用户确认项 → **STOP 确认**。
5. 按「XML 片段 + 排版规程 + 增量策略」**局部**写入；MODULE「图示」列必须走「图片」硬规则（`block_replace` + `<img …/>`，**禁止** `media-insert`）；**不得**清空背景与目标；**不得**把校验行写成 ✅ / ⚠️ / ❌；**不得** `overwrite`。
6. 流程/Mermaid：按「画板保活」表执行；写入失败 → **STOP**（策略 A），不得文本顶替后继续。
7. 任 unit 定位失败 / revision 冲突 → **立即 STOP**，询问用户。文档已有内容时不得整篇覆盖。
8. 本次若改了契约正文：把文末校验行重置为「未校验」，`metadata.consistency.status=unknown`。旧的可读性、一致性两块一并删掉，只留 `prd-sync:check:v1`。没有校验行则插入「未校验」。机器区若仍在正文前，本步一并移到文末。不在本步扫描文字墙。
9. 回读 + 写后自检（含 command 清单，以及图示位置）；更新 `last_synced_*`、`feishu_revision`、manifest；`last_synced_stage=current`。不因本次 push 把 `v9_synced` 设为 true，也不写 `prd.baseline`。  
   不得把校验行写成已通过。

### pull / reconcile

飞书 → 本地的正路。用户只贴飞书链接、说「同步回来 / 按飞书改本地」且未点名本命令时，也按本节执行，不要整篇覆盖 `prd.md`。

1. **Read** `../../references/three-way-sync.md`，并按其中「飞书先改、贴回工作区」执行。
2. 用绑定 `doc_token` 做 `docs +fetch`（契约区与可选评论）。聊天粘贴的正文只当线索，不能代替 fetch。评审修改记录不作为契约。
3. 同时读本地 `prd.md`、原型（`prototypes/` / `assets/`，没有则记缺失），以及上次 baseline/manifest。形成决策项（`ED`/`CM`/`FB`），并写明是否还要改原型。
4. **STOP**；用户确认接受项后，只写入同意的本地契约 unit / MODULE（含背景与目标）或原型；不改契约展示序号。禁止用本地旧稿再 `push` 盖掉本次飞书手改。
5. 更新 metadata：`last_synced_*`、`feishu_revision`、`consistency.status=unknown`。若写了本地契约，把飞书文末 `prd-sync:check:v1` **重置为「未校验」**（不要写成通过）。不跑 `/prd-check`，不写基线。
6. 若用户还要求飞书镜像与本地完全一致，再单独确认后 `push`；默认到第 5 步结束。

### status

打印绑定、`v9_synced`、`last_synced_*`、只读 `consistency`、契约漂移一句话。不写远端。

### rebind

展示旧/新目标 → **STOP 确认** → 更新绑定；重置 sync 标记；将校验行重置为「未校验」（XML，`prd-sync:check:v1`）；本地 `consistency.status=unknown`；提示全量 `push` 后，发布时再跑 `/prd-check`。

## 与工作区命令协作

| 命令 | 关系 |
|---|---|
| `/req-new` | 末尾必调 `create` |
| `/pm-spec` | 默认只改本地。用户明确说同步时才 `push` |
| `/prd-check` | 内容、对齐、可读性（本技能不替代） |
| `/prd-publish` | 预检（按新鲜度）→ sync → `/prd-check` → 基线 |

## 输出

子命令、目标文档、是否真实写入、是否 XML（格式）、**实际 command 清单**、变更 unit、是否触碰画板、校验行是否仍为「未校验」、门控结果、写后自检、失败项、建议下一步。  
若因策略 A 停下：明确写出卡住的 unit、原因、请用户选「重试局部 / 指定 block」。文档已有内容时不提供整篇覆盖。
