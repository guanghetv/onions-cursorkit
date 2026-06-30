# 类型与结构安全

## JSON manifest

插件 manifest 和 marketplace 必须是合法 JSON：

```bash
python3 -m json.tool .cursor-plugin/marketplace.json
python3 -m json.tool plugins/<plugin>/.cursor-plugin/plugin.json
```

正式插件需要通过 `scripts/validate-template.mjs`，它会检查：

- plugin name 是否符合模式。
- marketplace entry 和 plugin.json 的 name 是否一致。
- `rules`、`skills`、`commands` 等引用路径是否存在且安全。
- frontmatter 是否包含必需字段。

## Frontmatter

rule、command、skill、agent 的 YAML frontmatter 是本仓库最重要的“类型契约”之一。

必需字段：

- rule：`description`
- command：`name`、`description`
- skill：`name`、`description`
- agent：`name`、`description`

frontmatter 必须从文件第一行开始：

```markdown
---
name: onion-plan
description: 对变更做 Onion SDD Tier 分级。
---
```

不要在 frontmatter 前留空行；`scripts/validate-template.mjs` 会按文件开头解析。

## Markdown 模板字段

命令和技能中的模板字段应使用稳定名称。例如 onion-sdd 中：

- `## 背景`
- `## 变更`
- `## 影响范围`
- `## 验证`
- `## 带债项`

后续自动化会依赖这些标题恢复状态；不要随意重命名。

## Python 类型习惯

Trellis Python 脚本已经使用类型标注和 `Path`：

- 新函数补充参数和返回类型。
- 文件路径使用 `pathlib.Path`，不要混用大量裸字符串。
- JSON 读取/写入优先复用 `.trellis/scripts/common/io.py`。

参考：`.trellis/scripts/common/task_store.py`。

## 常见错误

- 在 JSON 示例里写注释。
- command 文件缺 `name`，导致校验失败。
- rule 文件只有 `globs` 没有 `description`。
- 用绝对路径写 manifest 引用，破坏跨机器安装。
