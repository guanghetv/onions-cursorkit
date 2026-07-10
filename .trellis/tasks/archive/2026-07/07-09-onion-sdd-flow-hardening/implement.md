# Implement: onion-sdd flow hardening

## Order

1. **脚本骨架** → verify: `python3 plugins/onion-sdd/scripts/onion_state.py --help` 与 `finish_check.py --help` 可运行
2. **实现 `onion_state.py`**（get/set/bind-trellis/mark-tier0pp/clear-tier0pp-pending；写：有 task 主写 meta+镜像 current，无 task 只写 current；读：meta→current）→ verify: fixture 覆盖「仅 current」「meta+镜像」「meta 失败降级 current」；`--idle` 清空 active
3. **实现 `finish_check.py`**（hard: tasks / Tier2 e2e 结论 / 0++ 逾期+无带债项；soft: openspec validate）→ verify: 构造最小 change fixture，pass/fail 各至少 1 例
4. **扩展 `templates/current.example.json` + `trellis-adapter` 字段表** → verify: 文档字段与脚本读写键名一致
5. **接线 commands/skills/rules**（finish 预检前置；阶段切换必须调 state helper；0++ 逾期硬提示；删除「不保证写入」）→ verify: `rg` 确认关键文件已引用脚本路径与纪律
6. **文档收敛**（README 脚本入口；USAGE 主路径仅 `/onsf-*`；DESIGN 已实现/未做；feishu wiki 关键点）→ verify: 无「current.json 无自动写入」与新纪律矛盾的表述；无 Multica 新增交付
7. **自检** → verify: 预检脚本对 cursorkit 自身若无活跃 openspec change 时行为安全（明确报错/跳过，不误删）

## Validation commands

```bash
python3 plugins/onion-sdd/scripts/onion_state.py --help
python3 plugins/onion-sdd/scripts/finish_check.py --help
# fixture 级：在临时目录设置 ONION_SDD_ROOT 或 --repo-root（实现时二选一，design 已要求可测）
rg -n "onion_state|finish_check|tier0pp_|不保证写入" plugins/onion-sdd
python3 -m json.tool plugins/onion-sdd/templates/current.example.json
```

## Review gates

- [ ] 未修改 `.trellis/scripts/**` / Trellis 源码
- [ ] 无 Multica 相关文件改动
- [ ] `/onsf-finish` 在预检失败路径明确禁止 archive
- [ ] 0++ 转 follow-up 必须 `## 带债项` 落盘
- [ ] USAGE 不把 `/trellis:*` 当用户主路径

## Rollback points

- 步骤 1–3 可单独回退（删 scripts）
- 步骤 5–6 文档/纪律回退不影响已产生的 OpenSpec 正文

## Notes for implementer

- 优先 stdlib；保持脚本可在业务仓根通过 `--repo-root .` 调用。
- 状态写路径必须落实选项 A：Trellis `meta.onion` 主写 + `current.json` 镜像/兜底；文档勿再写成「主写 current、可选 sync-meta」。
- `auto-flow` 保留与手动路径的既有差异，只加状态写入与逾期扫描，不「对齐」交互策略。
