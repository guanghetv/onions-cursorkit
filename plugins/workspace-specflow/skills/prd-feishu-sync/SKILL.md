---
name: prd-feishu-sync
description: >-
  将工作区需求 prd.md 与飞书文档深度绑定并同步（创建、增量推送、回收对账、状态、换绑）。
  Use when: 同步 PRD 到飞书、创建飞书 PRD、推送 5稿/9稿、飞书回收、prd-feishu-sync、
  feishu sync、发布飞书文档、MODULE 行同步。不做一致性结论（那是 prd-consistency-check）。
---

# /prd-feishu-sync — PRD ↔ 飞书同步

## 定位

- **只做同步与绑定**，不做「能否开工 / 一致性通过」结论。
- 契约层准源：本地 `prd.md`；飞书为人读 / 评审面。
- **禁止默认全文 overwrite**。XML 只是内容格式，**不等于**整篇覆盖。
- **飞书写入默认 XML**（`--doc-format xml`）；禁止默认用 markdown 创建/整段推送（会丢 callout/色表等样式）。
- **增量失败策略 = A**：定位失败 / revision 冲突时 **STOP 询问用户**，禁止静默降级为 `overwrite`。

## 子命令

| 命令 | 用途 |
|---|---|
| `create` | `/req-new` 后创建飞书文档并写绑定 |
| `push` | 契约层增量推送到飞书（`--stage skeleton\|v5\|v9`，可选 `--force`） |
| `pull` / `reconcile` | 飞书契约/反馈 vs 本地，确认后写 md |
| `status` | 绑定、门控、漂移摘要 |
| `rebind` | 显式更换飞书文档 |

用法：`/prd-feishu-sync push --stage v9`

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
5. MODULE「说明」**建议**拆成有序列表 / 分节 / 多行结构化块；验收用 checkbox 列表。出现整格纯文字墙时 **warning 告警（不阻断 push）**。
6. 复杂流程优先 `<whiteboard type="mermaid">`。**禁止**把已有画板静默降级为 `<pre>`/`<code>` 文本箭头图。

## 飞书排版与读写规程（本技能内建）

写入或更新飞书可读内容时，**直接按下列规则执行**（不另调外部 `/fs-doc` 命令名，但**排版质量须达到同等可读**）：

**文风**

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
3. 结构写尽量带精确 `revision`；冲突 → **STOP**（策略 A），重新 fetch 对账后等用户决定；**禁止**改用 `latest` 盲重试，**禁止**静默 `overwrite`。
4. 改后：再 fetch；确认目标存在、邻接未误删、表格/画板/callout 结构正常；并跑「写后自检」。
5. 输出必须列出本次实际使用的 `docs +update --command …` 清单；若含 `overwrite` 且非用户刚确认的重建模式 → **判定失败**。

## 文档分区（人读优先，禁止裸 BEGIN/END）

顶层顺序固定：**同步绑定 callout → 评审修改记录 → PRD 七章正文 → 可读性告警 callout → 一致性校验 callout**。

**硬禁令**：禁止在飞书正文出现裸文本  
`[PRD-SYNC:…:BEGIN]` / `[PRD-SYNC:…:END]`（严重影响可读性）。

机器定位用区标题 + 区内心跳码（行内 `<code>`，短小）：

| 区 | 人读形态 | 心跳码（区内一行即可） | 定位方式 |
|---|---|---|---|
| STATUS | 灰色 callout，标题「同步绑定」 | `prd-sync:status:v1` | callout / 心跳码 |
| REVIEW | `h2`「评审修改记录」+ 表 | `prd-sync:review:v1` | 标题 / 心跳码 |
| PRD_BODY | **无外层包裹**；直接七章 | — | chapter-map 语义标题 |
| READABILITY | 橙/绿 callout，标题「可读性告警」 | `prd-sync:readability:v1` | callout / 心跳码 |
| CONSISTENCY | 蓝/绿 callout，标题「一致性校验」 | `prd-sync:consistency:v1` | callout / 心跳码 |

### create 时 XML 骨架（示意）

```xml
<title>【…】PRD</title>

<callout emoji="🔗" background-color="light-gray" border-color="gray">
  <p><b>同步绑定</b>（机器维护，请勿手改）</p>
  <p><code>prd-sync:status:v1</code></p>
  <table>
    <colgroup><col width="280"/><col width="900"/></colgroup>
    <thead><tr>
      <th background-color="light-blue">字段</th>
      <th background-color="light-blue">值</th>
    </tr></thead>
    <tbody>
      <tr><td>绑定需求</td><td>{metadata.id}</td></tr>
      <tr><td>本地准源</td><td>requirements/…/prd.md</td></tr>
      <tr><td>同步阶段</td><td>skeleton</td></tr>
      <tr><td>说明</td><td>契约准源为本地 prd.md；本区请勿手改</td></tr>
    </tbody>
  </table>
</callout>

<h2>评审修改记录</h2>
<p>人工填写；普通 push 不改写本区。<code>prd-sync:review:v1</code></p>
<table>
  <colgroup><col width="200"/><col width="200"/><col width="780"/></colgroup>
  <thead><tr>
    <th background-color="light-blue">日期</th>
    <th background-color="light-blue">评审人</th>
    <th background-color="light-blue">修改说明</th>
  </tr></thead>
  <tbody><tr><td></td><td></td><td></td></tr></tbody>
</table>

<h2>一、需求概述</h2>
<!-- …七章骨架；关键关注/回归用 callout；表头着色… -->

<callout emoji="✨" background-color="light-green" border-color="green">
  <p><b>可读性告警</b>（机器维护，不阻断；请勿手改）</p>
  <p><code>prd-sync:readability:v1</code></p>
  <p>状态：✅ 暂无文字墙告警 · —</p>
  <p>说明：有告警时本区变橙并指向本地报告；细节不写在飞书</p>
</callout>

<callout emoji="⏳" background-color="light-blue" border-color="blue">
  <p><b>一致性校验</b>（机器维护，请勿手改）</p>
  <p><code>prd-sync:consistency:v1</code></p>
  <p>一致性校验结果：⏳ 未校验 · —</p>
  <p>报告：—</p>
  <p>对应 commit：—</p>
  <p>说明：须执行 /prd-consistency-check 或 /prd-publish 后由机器更新</p>
</callout>
```

### 可读性告警区（飞书只摘要，细节进本地报告）

`push` / `prd-consistency-check` / AI Review（已绑定飞书时）发现文字墙时，**必须**用 XML 局部更新本区：

- **飞书**：只写状态摘要（有/无、条数、日期）+ **详情报告路径**；**禁止**在飞书罗列全部位置/改写建议。
- **本地报告**：完整位置清单与建议写入 `prototypes/ai-review-v5.md` / `ai-review.md` / `prd-consistency-check-YYYY-MM-DD.md`（谁扫描谁写）。

有告警示例：

```xml
<callout emoji="⚠️" background-color="light-orange" border-color="orange">
  <p><b>可读性告警</b>（机器维护，不阻断；请勿手改）</p>
  <p><code>prd-sync:readability:v1</code></p>
  <p>状态：⚠️ 发现可读性问题（约 N 处）· YYYY-MM-DD</p>
  <p>详情报告：prototypes/ai-review.md（或 ai-review-v5.md / prd-consistency-check-日期.md）</p>
  <p>说明：不阻断 push / confirmed；请在本地报告中查看位置与拆分建议</p>
</callout>
```

| 区 | create | push | reconcile 写 md | consistency-check |
|---|---|---|---|---|
| STATUS | 初始化 callout | 可更新表内同步字段 | 否 | 否 |
| REVIEW | 空表 | **禁止** | 否 | 否 |
| PRD_BODY | 七章骨架（XML 富样式） | 仅契约 unit；**不覆盖**已有 `narrative.*` | 契约 → 本地 | 否 |
| READABILITY | **必须**占位（暂无告警） | **覆盖**扫描结果（有/无告警） | 否 | 若命中 W2 **覆盖**；无 W2 可保持或标暂无 |
| CONSISTENCY | **必须**「⏳ 未校验」callout | **禁止改写** | 否 | **覆盖**为 ✅/⚠️/❌ |

**存量兼容**：若文档仍含旧版裸 `[PRD-SYNC:…:BEGIN/END]`，下次 `push` / `rebind` / check 写区前须 **迁移**：删掉裸 marker，改为上表 callout/标题形态，保留区内业务内容。

## 章节与同步单元（语义优先）

权威匹配表见 [`references/chapter-map.md`](references/chapter-map.md)。

| sync unit key | 层 | 标题关键词（主匹配） | 常见序号（仅兼容） |
|---|---|---|---|
| `contract.overview` | 契约 | 需求概述 | 一、 |
| `contract.versions` | 契约 | 版本 + 进度/跟踪 | 二、 |
| `narrative.background` | 讲解 | 背景（非关键关注/回归） | 常 3.1 |
| `narrative.value` | 讲解 | 价值 | 常 3.2 |
| `contract.critical` | 契约 | 关键关注 | 常 3.3 |
| `contract.regression` | 契约 | 回归 | 常 3.4 |
| `contract.features` | 契约 | Feature / 功能清单 | 四、 |
| `MODULE-N` | 契约 | `MODULE-\d+` | — |
| `contract.details` | 契约 | 需求详情 | 五、 |
| `contract.design` | 契约 | 设计图 | 六、 |
| `contract.tracking` | 契约 | 埋点 | 七、 |

**定位顺序**：unit key → 标题关键词 → 序号兼容。禁止只靠「3.1/3.2」判断。  
讲解层（`narrative.*`）差异不参与字面对齐；push 不覆盖飞书已有讲解。契约层为权威对齐对象；不得为补洞而改写契约小节的展示序号或前移四～七。

## 安全硬约束

违反任一条 → **停止写飞书**。

1. **`push` 禁止 `overwrite`**（清空重建）。唯一例外：用户在本轮对话**明确**要求「整篇重建 / 全文覆盖」并确认风险后；此时须先说明会丢画板/评论/人工段落，再执行。  
   **增量失败不得自动降级为 overwrite**（策略 A：STOP 询问）。
2. 禁止静默覆盖：讲解层（`narrative.*`）、REVIEW 区、已有 whiteboard、远端与本地同 MODULE 均相对基线有改动时的任一侧。
3. 禁止把本地绝对路径写入飞书；禁止上传无关图片。
4. 缺 `space:folder:create` 等必要 scope 时不得静默降级到云盘根目录（除非用户明确同意并在输出标明）。
5. 未确认不得把 reconcile 结果写入 `prd.md`。
6. 本技能不得输出「一致性通过 / 可开工」。
7. **禁止**写入裸 `[PRD-SYNC:…:BEGIN/END]`；**禁止**默认 markdown 写飞书。
8. **禁止**用 `<pre>`/`代码块箭头图` 顶替或删除已有流程图画板后宣称同步成功。

**5/9 门控**

```text
push --stage v5:
  if feishu.v9_synced and not --force → REJECT
     （提示：/prd-feishu-sync push --stage v5 --force）
  if --force → 展示 diff → STOP 确认 → last_synced_stage=force_v5

push --stage v9（含 auto 解析为 v9）:
  if 本地仍存在 narrative.*（标题含「背景」「价值」的讲解小节，含空壳/指针）
     → REJECT（不得写入飞书、不得标 v9_synced）
     提示：先完成 /pm-spec Step 4 瘦身（删讲解层）后再 push v9；
           草稿期请用 --stage v5 或等瘦身完成
  else → 允许继续增量 push
push --stage v9 成功 → v9_synced=true, last_synced_stage=v9
```

## 增量同步策略（module-row）

- 首次 `create`：允许整篇创建骨架（**XML**）并生成 manifest（此为新建，不是对已有文档的 overwrite）。
- 已有文档：比较「当前飞书」与「本地最新 prd」，manifest 只作 block/图片/画板缓存，不作唯一真相。
- 普通契约章节：优先最小段落 `block_replace` / `str_replace`，写入内容为 **XML 片段**（局部内容仍用 xml，不是整篇覆盖）。
- MODULE：说明拆成列表/分节；表格行级增删改；图示列走下方「图片」硬规则（**禁止**用 `media-insert` 填单元格）。
- 单元 hash 须含图片文件 sha256，不只比路径。
- 远端手工改动与本地同 unit 均变 → 报告冲突，不静默覆盖。
- **定位不到目标 block / revision 冲突 / 局部写入失败** → **STOP**，展示失败 unit 与可选方案（重试 fetch / 用户手工指定 block / 用户确认整篇重建）；**默认不 overwrite**。

## 流程图 / 画板保活

| 场景 | 必须做法 |
|---|---|
| 本地有 Mermaid / 主流程源，飞书尚无画板 | 插入 `<whiteboard type="mermaid">…</whiteboard>` |
| 飞书已有 whiteboard | **不得删块用文本顶替**；用 `docs +whiteboard-update` 或仅 `block_replace` 该画板块 |
| Mermaid 写入/渲染失败 | **保留旧画板**（若有）+ warning；**禁止**降级为 `<pre>` 后标成功 |
| Manifest | 记录 `unit → board_token / block_id / mermaid_hash`；hash 不变则跳过 |

保护白名单（普通 `push` 永不碰）：讲解层、REVIEW、CONSISTENCY、已有 whiteboard、人工插图/评论锚点块。

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
2. 存在「同步绑定」callout + `prd-sync:status:v1`；存在「可读性告警」callout + `prd-sync:readability:v1`；存在「一致性校验」callout + `prd-sync:consistency:v1`。
3. PRD 正文为七章语义结构；关键关注/回归为 **callout**（非 `> [!IMPORTANT]` 原文）。
4. `create`/`push` 使用了 **XML** 写入路径；且本次 command 清单中**无未授权** `overwrite`。
5. 若本地/基线存在流程画板：飞书对应位置仍为 whiteboard（不得只剩文本箭头 `<pre>`）。
6. 本次若扫描到文字墙：飞书 READABILITY 区已更新为**橙色摘要**（含条数 + 报告路径，无明细列表）；若无文字墙：绿色「暂无」。**区缺失或未回写 → 同步失败**（告警本身仍不阻断业务 confirmed）。明细须落在本地报告。
7. 若本次同步含 MODULE「图示」/表格配图：目标表格片段内 `<img>` 数量 = 预期；**同名图不得残留在表格外**（有则 `block_delete` 后复读）；仅表格外有图、格内无图 → **同步失败**。

**告警项（不阻断同步成功）**

- 数据表缺表头底色（对话 warning；可不进 READABILITY 区）。
- 文字墙：对话可点名；飞书只写摘要+报告路径；**完整位置/建议必须写入本地报告**。

## 意图路由

1. 识别子命令；未指定则根据话术推断并复述确认。
2. 执行下列对应流程。
3. 结束后可建议跑 `/prd-consistency-check` 或 `/prd-publish`（本技能不代替校验）。

---

### create

1. 已有 `doc_token` → 停止，提示 `push` 或 `rebind`。
2. 标题用 `metadata.name`；按上文 **XML 骨架** 创建（同步绑定 + 评审区 + 七章 + **可读性告警占位** + 一致性「⏳ 未校验」）。
3. **`lark-cli docs +create ... --as user --doc-format xml`**（禁止默认 markdown）。
4. 写回 `metadata.feishu.*` 与 `feishu_doc`；`last_synced_stage=skeleton`；`v9_synced=false`；`consistency.status=unknown`；初始化 manifest。
5. `+fetch` 跑写后自检；确认可读性区与一致性区存在且无裸 BEGIN/END。

### push

1. 解析 stage：显式参数优先；否则若 `v9_synced` 或 `prd.stage` ∈ {`v9_pending`, `confirmed`} → `v9`，否则 `v5`。
2. 读本地 `prd.md`，执行 5/9 门控（含 **v9 + 仍有 narrative → REJECT**）。
3. `+fetch` 飞书（with-ids）；若仍有旧裸 marker → **先迁移**再改契约（迁移也用局部替换，禁止整篇 overwrite）。
4. 按 chapter-map **语义 unit** 与 MODULE 算 diff；顺带扫描文字墙位置清单；展示变更清单，声明不改 `narrative.*` / REVIEW / **CONSISTENCY** / 未变更 whiteboard → **STOP 确认**。
5. 按「XML 片段 + 排版规程 + 增量策略」**局部**写入；MODULE「图示」列必须走「图片」硬规则（`block_replace` + `<img …/>`，**禁止** `media-insert`）；本地无讲解层时**不得**清空飞书 `narrative.*`；**不得**改写 CONSISTENCY；**不得** `overwrite`。
6. 流程/Mermaid：按「画板保活」表执行；写入失败 → **STOP**（策略 A），不得文本顶替后继续。
7. 任 unit 定位失败 / revision 冲突 → **立即 STOP**，询问用户；未获「整篇重建」确认前不得覆盖。
8. **更新 READABILITY callout**（有告警 → 橙**摘要**：约 N 处 + 本地报告路径，禁止飞书罗列明细；无 → 绿「暂无」）；区缺失则在一致性 callout **之前** XML 插入。此步失败 → 同步失败（但告警内容本身从不构成业务硬拦）。
9. 回读 + 写后自检（含 command 清单、飞书可读性区、以及图示位置第 7 条）；更新 `last_synced_*`、`feishu_revision`、manifest；v9 成功则 `v9_synced=true`。  
   若缺少一致性 callout：用 XML **插入**「⏳ 未校验」占位，不假装已通过。

### pull / reconcile

1. fetch 飞书契约区与可选评论/REVIEW。
2. 三方：当前 Git prd、上次 baseline/manifest、当前飞书契约 → 决策项（`ED`/`CM`/`FB`）。
3. **STOP**；用户确认接受项后，仅写入本地**契约** unit / MODULE；**不写** `narrative.*` 进 md；不改契约展示序号。
4. 更新 metadata；建议再 `push` 对齐镜像（XML 富样式）。

### status

打印绑定、`v9_synced`、`last_synced_*`、只读 `consistency`、契约漂移一句话。不写远端。

### rebind

展示旧/新目标 → **STOP 确认** → 更新绑定；重置 sync 标记；将一致性区重置为「⏳ 未校验」callout（XML）；本地 `consistency.status=unknown`；提示全量 `push` 后再 `/prd-consistency-check`。

## 与工作区命令协作

| 命令 | 关系 |
|---|---|
| `/req-new` | 末尾必调 `create` |
| `/pm-spec-5` / `/pm-spec` | 确认后按门控 `push` |
| `/prd-consistency-check` | 一致性校验（本技能不替代） |
| `/prd-publish` | 编排 sync → check |

## 输出

子命令、目标文档、是否真实写入、是否 XML（格式）、**实际 command 清单**、变更 unit、是否触碰画板、**可读性告警（飞书已写/条数）**、门控结果、写后自检、失败项、建议下一步。  
若因策略 A 停下：明确写出卡住的 unit、原因、请用户选「重试局部 / 指定 block / 确认整篇重建」。
