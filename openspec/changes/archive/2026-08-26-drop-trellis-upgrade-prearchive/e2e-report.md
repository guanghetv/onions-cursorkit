# 验收报告：drop-trellis-upgrade-prearchive

## 验收范围

- 手动 Tier 2+/3 入口的遗留变更扫描：Trellis 与 OpenSpec 成对；无 Trellis 时只归档上一轮 OpenSpec。
- `/onsf-auto`、mini、light 的排除边界。
- `.onion-sdd/` 忽略、Git index 清理、本地文件保留与失败降级。
- 当前用户文档与 OpenSpec 产物一致性。

## 验证记录

- `python3 -m unittest discover -s plugins/onion-sdd/scripts -p "test_*.py" -v`：通过，6 项测试覆盖忽略幂等、等价规则、已跟踪文件清理、本地文件保留、非 Git/失败降级，以及 nested `--repo-root` 不误清父仓库 index。
- `python3 -m py_compile plugins/onion-sdd/scripts/onion_state.py plugins/onion-sdd/scripts/test_onion_state.py`：通过。
- `openspec validate drop-trellis-upgrade-prearchive`：通过。
- `python3 plugins/onion-sdd/scripts/finish_check.py --repo-root . --change-id drop-trellis-upgrade-prearchive --tier 2`：通过，无 hard failure，OpenSpec soft check 通过。
- `rg -n "trellis upgrade|trellis update|Trellis update available|更新检查" plugins/onion-sdd`：仅命中 `[0.0.4]` 历史 CHANGELOG。
- `git diff -- .trellis/scripts`：无输出，未修改 Trellis scripts。
- `node scripts/validate-template.mjs`：未通过；唯一 hard failure 为既有 `plugins/fe-specflow/skills/design-to-opsx/SKILL.md` 缺少 frontmatter `description`，不在本次改动范围。

## 验收结论

通过。当前变更的定向自动化测试、OpenSpec 校验和静态契约检查均通过；全仓模板校验仅剩与本次无关的既有阻断，不影响 Onion SDD 本次能力验收。

## 剩余风险

- 遗留扫描由 Agent 按 skill 协议执行。成对归档时 OpenSpec 预检失败则整项跳过，避免 Trellis 与 spec 分裂。无 Trellis 时依赖 `current.json` 或未归档 OpenSpec 目录列表。
- `git rm --cached` 遇到复杂 staged 状态可能失败；helper 会保留本地文件、警告并继续状态写入，由用户后续处理 index。
- `--repo-root` 若不是 Git 仓库根，helper 会跳过 index 清理以免误改父仓库；业务仓应按仓库根调用。
