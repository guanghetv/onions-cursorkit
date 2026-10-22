# 章节定位表（语义优先）

定位章节时 **禁止只靠序号**。顺序：

1. **sync unit key**（稳定身份）  
2. **标题关键词**（主匹配）  
3. **常见序号**（仅兼容旧稿 / 飞书默认模板展示，可缺省）

父章「背景和价值」「背景与目标」都用关键词：标题含「背景和价值」或「背景与目标」。

| sync unit key | 层 | 标题关键词（主匹配） | 常见序号（兼容） | 现行处理 |
|---|---|---|---|---|
| `contract.overview` | 契约 | `需求概述` | `一、` | 必留 |
| `contract.versions` | 契约 | `版本` +（`进度` 或 `跟踪`） | `二、` | 必留；基线行只由 `/prd-publish` 追加。飞书没有「对应 spec / demo」；该列只在本地 `prd.md` |
| `contract.background` | 契约 | 在背景父章下，标题含 **`背景`**，且 **不含**「关键关注」「回归」「目标」「范围」 | 常为 `3.1` | **保留**；可与飞书对齐 |
| `contract.goal` | 契约 | 标题含 **`目标`**，或旧稿「价值」 | 常为 `3.2` | **保留**；旧「价值」按目标语义读写 |
| `contract.scope` | 契约 | `本次范围` 或 `范围` | — | 有则同步；小需求可缺 |
| `contract.critical` | 契约 | **`关键关注`** | 常为 `3.3` | 有内容则保留（**不改号**） |
| `contract.regression` | 契约 | **`回归`** | 常为 `3.4` | 有内容则保留（**不改号**） |
| `contract.features` | 契约 | `Feature` 或 `功能清单` | `四、` | 多模块时保留；小需求可缺 |
| `MODULE-N` | 契约 | `MODULE-` + 数字 | — | 写下规则、状态或异常后必留。空骨架可以没有，不要补空的 `MODULE-1` |
| `contract.details` | 契约 | `需求详情` | `五、` | 必留。空骨架只有空表；写下规则后必须含 `MODULE-N` |
| `contract.materials` | 契约 | `关联材料` 或 `待确认` | 常为 `六、` | 有则同步；旧「设计图」归入此类 |
| `contract.design` | 契约 | `设计图` | 旧 `六、` | 兼容旧标题；新稿优先 `contract.materials` |
| `contract.observability` | 契约 | `数据观察` 或 `发布约束` | 常为 `七、` | 按需 |
| `contract.tracking` | 契约 | `埋点` | 旧 `七、` | 兼容旧标题；新稿优先 `contract.observability` |
| `local.feishu_link` | 本地 | `飞书文档` | — | 只在 `prd.md` 末尾，由 create、rebind 或发布补上展示地址。在知识库时写 `/wiki/<node_token>`。不上传，不参与契约 diff，reconcile 不删这一节 |

## 兼容别名

- 旧 unit `narrative.background` / `narrative.value`：读写时分别映射到 `contract.background` / `contract.goal`。**不再删除**。
- 旧「背景和价值」父标题：视为「背景与目标」。
- 旧「需求详情说明」：视为「需求详情」。

## 匹配伪代码

```text
locate(unit):
  candidates = headings matching title_keywords(unit)
  if len(candidates) == 1: return that
  if len(candidates) > 1: prefer under expected parent; else STOP 人工确认
  if len(candidates) == 0:
    try optional number pattern (compat)
    if still none: report missing（必留 unit → fail；按需 unit 可缺）
```

## 硬规则

- push / check：**按 unit key + 关键词**识别；不得写死「凡是 3.1 就删」。
- 背景与目标是正文的一部分；push 可增量更新本地已确认内容，不得为了「旧 9 稿瘦身」清空飞书或本地背景。
- 不得为「好看」把已有的 `contract.critical` / `regression` 改写成更小序号，也不得把它们后面的章节整段前移。新文档不写「一、」到「七、」，按标题关键词定位，不要补序号。
- MODULE：仅认 `MODULE-\d+`，与章节序号无关。空骨架（需求详情尚无规则、状态或异常）缺少 `MODULE-N` 不算失败。已经写下这些内容时，缺少 `MODULE-N` 才 fail。
- 详细说明写规则、状态、异常；不要求验收 checkbox 列表。
