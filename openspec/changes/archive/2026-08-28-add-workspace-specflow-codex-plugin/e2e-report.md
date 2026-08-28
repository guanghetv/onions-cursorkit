# E2E 验收报告：workspace-specflow Codex 插件

## 结论

静态结构、源漂移、确定性 ZIP、CodeWiki 仓库映射和 Cursor 隔离验证通过。当前机器没有 `codex` CLI，真实安装与技能发现冒烟测试未执行，需在具备 Codex 的环境补跑。

## 验证环境

- 日期：2026-08-28
- Python：本机 Python 3
- Codex CLI：不可用（`command not found: codex`）
- 测试 fixture：`/Users/lige/Onion/aiclass-specs/scripts/workspace-repos.json`

## 自动化结果

- `python3 -m unittest discover -s codex-plugins/workspace-specflow/tests -v`
  - 结果：14 tests passed
  - 覆盖：Git remote 归一化、精确映射、remote 未命中不猜、`unique-name` 仅 remote 缺失、歧义拒绝、六仓 fixture、完整 skill 打包、CodeWiki appendix、qa-execute metadata + hard gate、目录内/目录级 symlink 拒绝、manifest 拒绝 `hooks` 与不完整 interface、确定性 ZIP、源锁一致性
- `python3 -m py_compile codex-plugins/workspace-specflow/scripts/pack.py codex-plugins/workspace-specflow/tests/test_pack.py`
  - 结果：通过
- `python3 codex-plugins/workspace-specflow/scripts/pack.py check`
  - 结果：通过
- `python3 codex-plugins/workspace-specflow/scripts/pack.py pack`
  - 结果：通过
  - 产物：`codex-plugins/workspace-specflow/dist/workspace-specflow.zip`（由局部 `.gitignore` 排除）
  - ZIP 结构：唯一顶层目录 `workspace-specflow/`，manifest 位于 `.codex-plugin/plugin.json`
  - SHA-256：`59aa058e2aab33a6d6a0f9b6a823f28a1640666d43c4fecd4a7bf2cfec7be4de`
- `uvx --from skills-ref agentskills validate <skill>`
  - 结果：包内 12 个 skills 全部通过 Agent Skills 官方参考校验器
  - 兼容处理：构建时从 `qa-execute` 生成副本去掉非法顶层字段 `disable-model-invocation`，写入 `metadata.disable-model-invocation` 与正文 `<HARD-GATE>`，不修改 Cursor 源 skill
- Codex 官方 `validate_plugin.py`（本机 `~/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py`）
  - 结果：解压后的 `workspace-specflow` 插件根通过
- `openspec validate add-workspace-specflow-codex-plugin`
  - 结果：通过

## workspace registry 实测

实际读取 `aiclass-specs/scripts/workspace-repos.json`，六个 registry 项均按 remote path 精确映射：

- `teacher-desk` → `backend/teacher-desk`
- `teacher-ai-class` → `backend/teacher-ai-class`
- `teacher-school` → `teacher/backend/teacher-school`
- `onion-edu-manage` → `teacher/fe/onion-edu-manage`
- `padh5` → `teacher/fe/padh5`
- `teacher-workbench` → `teacher/fe/teacher-workbench`

## Cursor 隔离

- `.cursor-plugin/marketplace.json` 无改动。
- `plugins/workspace-specflow/` 无改动。
- 仓库根 `scripts/` 无改动。
- 打包、同步和校验入口仅位于 `codex-plugins/workspace-specflow/scripts/pack.py`。
- ZIP 不包含维护用 `pack.py`、测试、源锁或构建缓存。

## 已知外部阻塞

仓库级 `node scripts/validate-template.mjs` 仍因既有文件 `plugins/fe-specflow/skills/design-to-opsx/SKILL.md` 缺少 `description` 而失败。本次没有修改该插件，该失败不属于本 change。

## 待补真实冒烟

在安装 Codex CLI 且配置 CodeWiki MCP 的环境：

1. 安装生成的 ZIP。
2. 确认能发现 workspace-specflow 原有 skills 与 `workspace-code-context`。
3. 在 aiclass-specs 根目录触发 `qa-spec` 或 `pm-proto` 的代码扫描步骤。
4. 确认先加载 `workspace-code-context`，并使用 GitNexus 规范仓名查询。
5. 模拟 CodeWiki 不可用，确认降级为 registry 本地路径只读扫描。
