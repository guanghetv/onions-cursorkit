# Implement Plan

## 交付物 D1: repo-root 自动解析

- [ ] 1.1 `scripts/onion_state.py`：新增 `resolve_repo_root(start) -> Path`（向上找 `.trellis/`，回退 `start`）。
  - 验证：`python3 -c "from pathlib import Path; import sys; sys.path.insert(0,'plugins/onion-sdd/scripts'); from onion_state import resolve_repo_root; print(resolve_repo_root(Path('plugins/onion-sdd')))"` 在 cursorkit 内应解析到仓库根。
- [ ] 1.2 `scripts/onion_state.py`：`--repo-root` default 改 `None`；`main()` 里 `None → ONION_SDD_ROOT or resolve_repo_root(cwd)`；优先级不变。
  - 验证：`python3 plugins/onion-sdd/scripts/onion_state.py --help` 正常；`get` 在 cursorkit 根行为不变。
- [ ] 1.3 模拟 monorepo 子包场景：在 `/tmp` 造一个含 `.trellis/` 的假根 + 子包目录，从子包跑 `get`，确认 repo-root 解析到假根。
  - 验证：脚本输出读到的 current.json 路径指向假根 `.onion-sdd/`，而非子包。
- [ ] 1.4 `rules/onion-sdd.mdc`：运行态段补 repo-root 自动解析说明（1-2 句）。
  - 验证：`rg -n "repo-root|自动解析" plugins/onion-sdd/rules/onion-sdd.mdc`。

## 交付物 D2: 规范类交付物门禁

- [ ] 2.1 `skills/openspec-change/SKILL.md`：新增「规范/约定的归属」小节（tasks.md 只装产品交付物；规范属 Phase 3.3、落 `.trellis/spec/`、禁 `docs/`）。
  - 验证：`rg -n "规范|约定|\.trellis/spec|docs/" plugins/onion-sdd/skills/openspec-change/SKILL.md`。
- [ ] 2.2 `scripts/finish_check.py`：新增 `check_convention_in_docs`（扫 `docs/**` + 文件名含 convention/guideline/standard/规范/约定，输出 WARN，不改 exit code）。
  - 验证：读现有结构；造一个含 `docs/frontend-conventions.md` 的假 change，跑 `finish_check.py`，确认 WARN 出现且 exit code 不变。
- [ ] 2.3 反例验证：造一个只含 `docs/api.md`（非 convention 名）的假 change，确认无新 WARN。
  - 验证：finish_check 输出无 convention WARN。

## 发版 0.1.2

- [ ] 3.1 `CHANGELOG.md`：`[Unreleased]` 下新增 `[0.1.2] - <date>`，Added 记 D1/D2。
- [ ] 3.2 `.cursor-plugin/plugin.json`：version `0.1.1` → `0.1.2`。
  - 验证：`python3 -m json.tool plugins/onion-sdd/.cursor-plugin/plugin.json` 且 version=0.1.2；与 CHANGELOG 最新版本一致。

## 整体回归

- [ ] 4.1 `python3 plugins/onion-sdd/scripts/onion_state.py --help` 与 `finish_check.py --help` 正常。
- [ ] 4.2 `python3 -m json.tool plugins/onion-sdd/.cursor-plugin/plugin.json` 通过。
- [ ] 4.3 `rg -n "onion_state|finish_check|resolve_repo_root|convention" plugins/onion-sdd` 抽查接线。
- [ ] 4.4 ReadLints 检查改过的 .py 文件无新增 lint 错误。

## 提交规划（Phase 3.4，待实现后）

按 Conventional Commits + 简体中文拆：
- `feat(onion-sdd): onion_state.py 自动向上解析 repo-root 到 .trellis/`
- `feat(onion-sdd): 规范类交付物门禁（openspec-change 硬规则 + finish_check WARN）`
- `chore(onion-sdd): 发版 0.1.2`

## 回滚点

- D1 出问题：把 `--repo-root` default 改回 `os.environ.get("ONION_SDD_ROOT") or "."` 即恢复旧行为。
- D2 出问题：移除 `check_convention_in_docs` 调用即可恢复；openspec-change 规则为文档，回滚即删小节。
