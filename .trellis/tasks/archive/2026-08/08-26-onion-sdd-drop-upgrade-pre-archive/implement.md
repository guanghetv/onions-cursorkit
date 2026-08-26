# Implement: onion-sdd 去掉升级推荐 + 开任务前确认归档

> 每个步骤先能验证，再改最小集合。不修改 `.trellis/scripts/**`。

## 1. 改 `full-change` 流程正文

- [x] 1.1 删除「更新检查」整节；第 1 步「存在 → 可用」改为：跳过安装后先做「遗留 task 扫描」，再「task 绑定询问」。
      验证点: `rg -n "trellis upgrade|更新检查|Trellis update available" plugins/onion-sdd/skills/full-change/SKILL.md` 无命中。
- [x] 1.2 新增「遗留变更扫描」：Trellis 与 OpenSpec 成对；无 Trellis 仍扫上一轮 OpenSpec；失败不阻塞；mini/light/`/onsf-auto` 不执行。
      验证点: 与 `prd.md` Decision 1–3 逐条对照。
- [x] 1.3 保留「Trellis 使用检查」安装/init 与「gitignore 追加」；文案不提 upgrade。

## 2. 对齐命令与文档

- [x] 2.1 `commands/onsf-auto.md` Trellis 边界：安装询问仍仅手动入口；明确不扫描、不归档遗留 task；删任何 upgrade 暗示。
- [x] 2.2 `USAGE.md`、`README.md`、`docs/feishu-wiki-onion-sdd-usage.md`：未安装路径保留；删除「已安装但有更新」；补一句开任务前确认归档遗留 Trellis task。
- [x] 2.3 `DESIGN-SUPPLEMENT.md` 同步时机表：可用且未绑定不再经过 upgrade；增加遗留扫描行。
- [x] 2.4 `CHANGELOG.md` 的 `[Unreleased]` 写 Removed（升级询问）与 Added（开任务前确认归档）。

## 3. OpenSpec 落盘（本仓 onion-sdd 变更）

- [x] 3.1 按 `openspec-change` 写入 `openspec/changes/<change-id>/`：`proposal.md`、`specs/**/spec.md`、`tasks.md`（可验证交付物，引用本 implement 而不复制全文）。
- [x] 3.2 `onion_state.py set --change-id ... --phase openspec`（已绑定则主写 meta）。

## 4. `.onion-sdd/` 本地状态治理

- [x] 4.1 扩展 `onion_state.py`：确保 `.onion-sdd/` 被忽略后，检测并清除该目录下已跟踪文件的 Git index 记录；保留本地文件；Git 失败只警告。
- [x] 4.2 添加临时 Git 仓库测试：首次追加、重复调用不重复、已跟踪 `current.json` 被 untrack 且文件仍存在、非 Git/失败路径不阻断。
      验证点: 运行 onion-sdd 相关 Python 测试；`git ls-files .onion-sdd` 为空且文件存在。
- [x] 4.3 文档说明 `.onion-sdd/` 是 per-user 本地状态，不应提交；已有跟踪会自动清除。

## 5. 收口检查

- [x] 5.1 `rg -n "trellis upgrade|trellis update|Trellis update available" plugins/onion-sdd` 仅允许 CHANGELOG 历史版本小节（如 0.1.x）保留过去记录；Unreleased/当前 skill/USAGE/README/wiki/auto 不得再推荐执行。
- [x] 5.2 不出现对 `.trellis/scripts/**` 的 diff。
- [x] 5.3 文档正文中文、命令与路径保留英文。

## 验证结果

- `python3 -m unittest discover -s plugins/onion-sdd/scripts -p "test_*.py" -v`：6 项通过。
- `python3 -m py_compile plugins/onion-sdd/scripts/onion_state.py plugins/onion-sdd/scripts/test_onion_state.py`：通过。
- `openspec validate drop-trellis-upgrade-prearchive`：通过。
- `python3 plugins/onion-sdd/scripts/finish_check.py --repo-root . --change-id drop-trellis-upgrade-prearchive --tier 2`：通过，无 hard failure。
- `rg -n "trellis upgrade|trellis update|Trellis update available|更新检查" plugins/onion-sdd`：仅命中 `[0.0.4]` 历史 CHANGELOG。
- `git diff -- .trellis/scripts`：无输出。
- `node scripts/validate-template.mjs`：被既有 `plugins/fe-specflow/skills/design-to-opsx/SKILL.md` 缺少 frontmatter `description` 阻断；与本次改动无关。

## Rollback

`git checkout --` 上述 onion-sdd 与 openspec 路径。无运行时数据格式变更。
