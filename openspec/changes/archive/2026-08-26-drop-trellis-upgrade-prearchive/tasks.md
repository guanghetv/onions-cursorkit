# Tasks: drop-trellis-upgrade-prearchive

> 执行约束
> - 工程执行顺序与回滚点见 `.trellis/tasks/08-26-onion-sdd-drop-upgrade-pre-archive/implement.md`。
> - 每项完成后记录可复现验证证据。
> - 本次为 Tier 2 流程能力变更，以定向自动化测试、文档契约检查和插件模板校验作为等价验收证据。

## 1. 手动完整流程

- [x] 1.1 移除 Trellis 更新检查，并加入遗留 task 扫描、排除、确认归档与失败降级规则。
      验证证据: `rg -n "trellis upgrade|trellis update|Trellis update available|更新检查" plugins/onion-sdd` 仅命中 `[0.0.4]` 历史 CHANGELOG；流程逐条覆盖候选、排除、确认与失败继续规则。

## 2. 用户文档与自动化边界

- [x] 2.1 对齐 README、USAGE、飞书 wiki、设计补充、CHANGELOG 与 `/onsf-auto` 的行为说明。
      验证证据: 当前流程文档已移除版本维护建议；`onsf-auto.md` 明确遗留扫描仅限手动入口。

## 3. 本地运行态治理

- [x] 3.1 扩展 `onion_state.py`，幂等忽略 `.onion-sdd/`，只清 Git index 并保留本地文件，失败时警告且继续写入。
      验证证据: `python3 -m unittest discover -s plugins/onion-sdd/scripts -p "test_*.py" -v`，6 项测试全部通过。

## 4. 收口验证

- [x] 4.1 运行插件模板校验、OpenSpec 校验或等价静态检查，并确认 `.trellis/scripts/**` 无 diff。
      验证证据: `openspec validate drop-trellis-upgrade-prearchive` 通过；`python3 -m py_compile ...` 通过；`git diff -- .trellis/scripts` 为空。`node scripts/validate-template.mjs` 被既有 `plugins/fe-specflow/skills/design-to-opsx/SKILL.md` 缺少 frontmatter `description` 阻断，与本次改动无关。
