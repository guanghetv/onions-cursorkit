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
- **禁止默认全文 overwrite**。

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
3. 文档操作使用当前 CLI 支持的 `docs +fetch` / `+create` / `+update` / `+media-insert` 与 drive 上传能力；参数以本机 `lark-cli docs --help` 为准。
4. 除 `create`/`rebind` 外，必须已有 `metadata.feishu.doc_token`（可从 `feishu_doc` URL 解析后写回自愈）。

## 飞书排版与读写规程（本技能内建）

写入或更新飞书可读内容时，**直接按下列规则执行**（不另调外部排版命令）：

**文风**

- 用户可见正文用简体中文；专有名词/代码/路径保持英文。
- 简洁直接；重要段结论前置（callout 或短结论段）。
- 多维信息优先表格；流程/分支用 Mermaid 画板；风险与关键点用 callout。
- 禁止连续大段纯文字（契约段连续正文超过 6 行须拆成列表/表/callout）。
- 只改目标区块，保留他人未改内容。

**视觉**

- 表头可用浅色（如 light-blue）；关键/风险列可用 light-orange / light-red。
- callout 颜色语义：红=必须/阻塞；蓝=主链路；橙=待确认；绿=可选/兼容。
- 宽页表格总宽约 1170–1190；短列窄、说明列宽；三列可参考 `110 + 530 + 530`。

**读写步骤**

1. 改前：对目标范围 `docs +fetch`，需要定位时用 `--detail with-ids`；优先局部 scope，避免无关全文。
2. 改时：用 `str_replace` / `block_replace` / `block_insert_after` / `block_delete` 等局部操作；**默认禁止** `overwrite`。
3. 结构写尽量带精确 `revision`；revision 冲突则停止，重新 fetch 对账，不得改用 latest 盲重试。
4. 改后：再 fetch 目标区块，确认目标存在、邻接未误删、表格/画板/callout 结构正常。

## 文档四区布局

受管文档顶层顺序固定，marker 各出现一次、独占段落（STATUS / REVIEW / PRD_BODY / CONSISTENCY）：


```text
[PRD-SYNC:STATUS:v1:BEGIN]
... 发布状态 / 绑定 / source commit / revision ...
[PRD-SYNC:STATUS:v1:END]

[PRD-SYNC:REVIEW:v1:BEGIN]
... 评审修改记录；普通 push 不得改写 ...
[PRD-SYNC:REVIEW:v1:END]

[PRD-SYNC:PRD_BODY:v1:BEGIN]
... 七章 PRD 正文 ...
[PRD-SYNC:PRD_BODY:v1:END]

[PRD-SYNC:CONSISTENCY:v1:BEGIN]
一致性校验结果：⏳ 未校验 · —
报告：—
对应 commit：—
说明：须执行 /prd-consistency-check 或 /prd-publish 后由机器更新；请勿手改
[PRD-SYNC:CONSISTENCY:v1:END]
```

| 区 | create | push | reconcile 写 md | consistency-check |
|---|---|---|---|---|
| STATUS | 初始化 | 可更新同步机器字段 | 否 | 否 |
| REVIEW | 空壳 | **禁止** | 否 | 否 |
| PRD_BODY | 七章骨架 | 仅契约 unit；**不覆盖**已有 `narrative.*` | 契约 → 本地 | 否 |

| CONSISTENCY | **必须**写「⏳ 未校验」占位 | **禁止改写** | 否 | **覆盖**为 ✅/⚠️/❌ |

**CONSISTENCY 占位（create / rebind 后必现）**：人打开飞书即可看到尚未校验；本地 `metadata.consistency.status` 同步为 `unknown`。


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

1. 禁止默认全文 `overwrite`（或清空重建）。仅首次 `create`，或用户明确要求全文覆盖且增量定位失败并确认时，才可覆盖。
2. 禁止静默覆盖：讲解层（`narrative.*`）、REVIEW 区、远端与本地同 MODULE 均相对基线有改动时的任一侧。

3. 禁止把本地绝对路径写入飞书；禁止上传无关图片。
4. 缺 `space:folder:create` 等必要 scope 时不得静默降级到云盘根目录（除非用户明确同意并在输出标明）。
5. 未确认不得把 reconcile 结果写入 `prd.md`。
6. 本技能不得输出「一致性通过 / 可开工」。

**5/9 门控**

```text
push --stage v5:
  if feishu.v9_synced and not --force → REJECT
     （提示：/prd-feishu-sync push --stage v5 --force）
  if --force → 展示 diff → STOP 确认 → last_synced_stage=force_v5
push --stage v9 成功 → v9_synced=true, last_synced_stage=v9
```

## 增量同步策略（module-row）

- 首次 `create`：允许整篇创建骨架并生成 manifest。
- 已有文档：比较「当前飞书」与「本地最新 prd」，manifest 只作 block/图片缓存，不作唯一真相。
- 普通契约章节：优先 `str_replace` 或最小段落 `block_replace`，不整章替换。
- MODULE 表：以行为单位（模块/页面 | 图示 | 说明）；任列变化则整行 `block_replace`；增行 `block_insert_after`；删行 `block_delete`。
- 单元 hash 须含图片文件 sha256，不只比路径。
- 远端手工改动与本地同 unit 均变 → 报告冲突，不静默覆盖。

## 图片

1. 飞书不能使用本地路径或 Drive `/file/` 页 URL 当图片直链。
2. 表格「图示」列：优先 `drive +upload` 到需求同名文件夹，得 `file_token`，在同步片段中写 `<img src="file_token" caption="..."/>`。
3. 独立图片块：可用 `docs +media-insert --file`；默认追加末尾，不能冒充表格内图片除非已验证 cell 定位。
4. 需要转换引用时用临时同步稿（如 `prd.feishu-sync.md`），**默认不把**飞书 token 写回正式 `prd.md`。
5. manifest 记录 folderToken 与图片 sha256→fileToken 映射，未变化则复用。

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

## 意图路由

1. 识别子命令；未指定则根据话术推断并复述确认。
2. 执行下列对应流程。
3. 结束后可建议跑 `/prd-consistency-check` 或 `/prd-publish`（本技能不代替校验）。

---

### create

1. 已有 `doc_token` → 停止，提示 `push` 或 `rebind`。
2. 标题用 `metadata.name`；正文为七章骨架（含讲解层「背景/价值」占位，对齐飞书产品模板）+ 四区 marker（STATUS / REVIEW / PRD_BODY / **CONSISTENCY**）。
3. STATUS 写明 Git 契约准源与勿手改机器字段；**CONSISTENCY 必须含「⏳ 未校验」占位**（见上文模板），禁止省略。
4. `lark-cli docs +create ... --as user --doc-format markdown`；记录 url/token。
5. 写回 `metadata.feishu.*` 与 `feishu_doc`；`last_synced_stage=skeleton`；`v9_synced=false`；`consistency.status=unknown`（若字段缺失则补上）；初始化 manifest。
6. `+fetch` 确认 CONSISTENCY 区存在且为未校验文案。

### push

1. 解析 stage：显式参数优先；否则若 `v9_synced` 或 `prd.stage` ∈ {`v9_pending`, `confirmed`} → `v9`，否则 `v5`。
2. 执行 5/9 门控。
3. 读本地 prd；`+fetch` 飞书（with-ids，优先 PRD_BODY）；按 **chapter-map 语义 unit** 与 MODULE 行算 hash/diff（关键词优先，序号仅兼容）。
4. 展示将变更的 unit 清单，声明不改 `narrative.*` / REVIEW / **CONSISTENCY** → **STOP 确认**。
5. 按「飞书排版与读写规程」+「增量同步策略」局部写入；本地无讲解层时**不得**清空飞书 `narrative.*`；**不得**改写或删除 CONSISTENCY 区。
6. 复杂流程 Mermaid 尽力转画板；失败则保留代码块并 warning。
7. 回读校验；更新 `last_synced_*`、`feishu_revision`、manifest；v9 成功则 `v9_synced=true`。  
   若飞书缺少 CONSISTENCY 区（存量文档）：**仅插入**「⏳ 未校验」占位，不假装已通过。

### pull / reconcile

1. fetch 飞书契约区与可选评论/REVIEW。
2. 三方：当前 Git prd、上次 baseline/manifest、当前飞书契约 → 决策项（`ED`/`CM`/`FB`）。
3. **STOP**；用户确认接受项后，仅写入本地**契约** unit / MODULE；**不写** `narrative.*` 进 md；不改契约展示序号。
4. 更新 metadata；建议再 `push` 对齐镜像。

### status

打印绑定、`v9_synced`、`last_synced_*`、只读 `consistency`、契约漂移一句话。不写远端。

### rebind

展示旧/新目标 → **STOP 确认** → 更新绑定；重置 sync 标记；将飞书 CONSISTENCY（或新建）重置为「⏳ 未校验」；本地 `consistency.status=unknown`；提示全量 `push` 后再 `/prd-consistency-check`。


## 与工作区命令协作

| 命令 | 关系 |
|---|---|
| `/req-new` | 末尾必调 `create` |
| `/pm-spec-5` / `/pm-spec` | 确认后按门控 `push` |
| `/prd-consistency-check` | 一致性校验（本技能不替代） |
| `/prd-publish` | 编排 sync → check |

## 输出

子命令、目标文档、是否真实写入、变更 unit、门控结果、失败项、建议下一步。
