# 实施计划

## 清单

- [x] 新增 `plugins/onion-sdd/skills/trellis-adapter/SKILL.md`。
- [x] 更新 `plugins/onion-sdd/commands/onion-continue.md`，加入 Trellis-aware 恢复优先级。
- [x] 更新 `plugins/onion-sdd/rules/onion-sdd.mdc`，明确 OpenSpec / current / Trellis metadata 边界。
- [x] 更新 `plugins/onion-sdd/templates/current.example.json`，增加 `trellis_task` 示例。
- [x] 更新 `plugins/onion-sdd/README.md`，说明 adapter 使用方式和不做范围。
- [x] 更新 `plugins/onion-sdd/DESIGN-SUPPLEMENT.md`，补充字段映射、同步时机和 Tier 3 映射。
- [x] 运行验证命令并记录结果。

## 文件责任

| 文件 | 责任 |
| --- | --- |
| `skills/trellis-adapter/SKILL.md` | Adapter 协议、字段映射、同步/恢复/冲突处理 |
| `commands/onion-continue.md` | 用户可见的恢复顺序 |
| `rules/onion-sdd.mdc` | 边界和门禁 |
| `templates/current.example.json` | 轻量状态兼容模板 |
| `README.md` | 使用方式 |
| `DESIGN-SUPPLEMENT.md` | 技术细节 |

## 验证命令

```bash
find plugins/onion-sdd -type f | sort
python3 -m json.tool plugins/onion-sdd/.cursor-plugin/plugin.json
python3 -m json.tool plugins/onion-sdd/templates/current.example.json
rg -n "trellis-adapter|meta.onion|trellis_task|source_hashes" plugins/onion-sdd
rg -n "OpenSpec 是变更正文唯一真相源|不复制 OpenSpec 正文" plugins/onion-sdd
rg -n "必须全量扫描|全量扫描项目|扫描当前仓库" plugins/onion-sdd
python3 ./.trellis/scripts/task.py list
python3 ./.trellis/scripts/get_context.py
node scripts/validate-template.mjs
```

## Review Gate

开始实现前，需要用户确认：

- 第一版 adapter 不修改 `.trellis/scripts/**`。
- Adapter 通过 `trellis-adapter` skill 和文档协议落地。
- `task.json.meta.onion` 作为 Trellis metadata 扩展位置，OpenSpec 正文不复制到 Trellis。

用户已补充确认：整个方案都不改造 Trellis 源码；任何涉及 Trellis 改造的事项必须另行确认。

## 验证结果

- `find plugins/onion-sdd -type f | sort`：通过，已包含 `skills/trellis-adapter/SKILL.md`。
- `python3 -m json.tool plugins/onion-sdd/.cursor-plugin/plugin.json`：通过。
- `python3 -m json.tool plugins/onion-sdd/templates/current.example.json`：通过。
- `rg -n "trellis-adapter|meta.onion|trellis_task|source_hashes" plugins/onion-sdd`：通过，README、command、rule、skill、design 和模板均有覆盖。
- `rg -n "OpenSpec 是变更正文唯一真相源|不复制 OpenSpec 正文" plugins/onion-sdd`：通过。
- `rg -n "必须全量扫描|全量扫描项目|扫描当前仓库" plugins/onion-sdd`：无命中。
- `rg -n "fe-sdd|fe-specflow|调用 fe-specflow|依赖 fe-specflow" plugins/onion-sdd`：无命中。
- `rg -n "不做 Trellis adapter|Trellis adapter 接入后|后续接入 Trellis|后续 Trellis adapter|不读写 Trellis workflow-state|Phase 1 接入 Trellis 后" plugins/onion-sdd`：无命中。
- `python3 ./.trellis/scripts/task.py list`：通过，adapter 子任务为 current。
- `python3 ./.trellis/scripts/get_context.py`：通过。
- `node scripts/validate-template.mjs`：通过，仅保留仓库既有 hooks/mcp 缺失 warning。
