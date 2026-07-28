# 章节定位表（语义优先）

定位章节时 **禁止只靠序号**。顺序：

1. **sync unit key**（稳定身份）  
2. **标题关键词**（主匹配）  
3. **常见序号**（仅兼容旧稿 / 飞书默认模板展示，可缺省）

父章「背景和价值」用关键词：标题含「背景和价值」或「背景与价值」。

| sync unit key | 层 | 标题关键词（主匹配） | 常见序号（兼容） | 9 稿本地 |
|---|---|---|---|---|
| `contract.overview` | 契约 | `需求概述` | `一、` | 必留 |
| `contract.versions` | 契约 | `版本` +（`进度` 或 `跟踪`） | `二、` | 必留 |
| `narrative.background` | 讲解 | 在「背景和价值」下，标题含 **`背景`**，且 **不含**「关键关注」「回归」 | 常为 `3.1` | **整节删除** |
| `narrative.value` | 讲解 | 在「背景和价值」下，标题含 **`价值`** | 常为 `3.2` | **整节删除** |
| `contract.critical` | 契约 | **`关键关注`** | 常为 `3.3` | 必留（**不改号**） |
| `contract.regression` | 契约 | **`回归`** | 常为 `3.4` | 必留（**不改号**） |
| `contract.features` | 契约 | `Feature` 或 `功能清单` | `四、` | 必留 |
| `MODULE-N` | 契约 | `MODULE-` + 数字 | — | 必留 |
| `contract.details` | 契约 | `需求详情` | `五、` | 必留（含 MODULE） |
| `contract.design` | 契约 | `设计图` | `六、` | 按需 |
| `contract.tracking` | 契约 | `埋点` | `七、` | 按需 |

## 匹配伪代码

```text
locate(unit):
  candidates = headings matching title_keywords(unit)
  if len(candidates) == 1: return that
  if len(candidates) > 1: prefer under expected parent; else STOP 人工确认
  if len(candidates) == 0:
    try optional number pattern (compat)
    if still none: report missing (契约层 → fail / 讲解层按规则忽略或删)
```

## 硬规则

- push / check / 瘦身：**按 unit key + 关键词**识别；不得写死「凡是 3.1 就删/就不同步」。  
- 讲解层（`narrative.*`）：push **不覆盖**飞书已有正文；9 稿本地须删光（禁止指针）。  
- 契约层：权威对齐对象；不得为「好看」把 `contract.critical` 改写成更小的序号或前移四～七。  
- MODULE：仅认 `MODULE-\d+`，与章节序号无关。
