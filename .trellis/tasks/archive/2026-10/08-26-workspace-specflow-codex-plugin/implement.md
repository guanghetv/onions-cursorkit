# workspace-specflow Codex 插件实施计划

## 1. 固化 Codex 包契约

- 新建隔离的 Codex 插件源目录与官方 `.codex-plugin/plugin.json`。
- 增加 Codex 专属入口说明，明确 specs 根定位、CodeWiki 优先和本地降级规则。
- 验证：`.codex-plugin/plugin.json` 可解析、组件路径为 `./skills/`；目录不在 `.cursor-plugin/marketplace.json`。

## 2. 实现确定性同步与打包

- 在 Codex 插件目录内新增打包脚本（如 `codex-plugins/workspace-specflow/scripts/pack.py`），从 `plugins/workspace-specflow/skills/` 复制完整技能资源；不新增仓库根 `scripts/` 入口。
- 生成文件清单/摘要并提供 check 模式，禁止手工维护第二份技能正文。
- 生成自包含 ZIP，固定包内根目录并排除缓存、隐藏临时文件和历史产物。
- 验证：连续两次构建摘要一致；源文件变化能触发漂移失败；ZIP 解压结构符合契约。

## 3. 实现 CodeWiki 仓库映射

- 解析根目录或 `scripts/workspace-repos.json`。
- 依据 `remote` GitLab path 与 GitNexus 规范仓名匹配，名称只作唯一兜底。
- 实现 CodeWiki → 本地只读扫描 → 当前步骤阻断的分级降级提示。
- 验证：以 `aiclass-specs/scripts/workspace-repos.json` 为 fixture，覆盖六个仓库映射及未匹配场景。

## 4. 校验现有技能的 Codex 可移植性

- 检查所有 `SKILL.md` frontmatter、目录名、相对引用和辅助脚本。
- 对 Cursor 独有 command/rule 依赖增加 Codex 适配或在构建时给出明确错误。
- 验证：所有打包技能通过 Agent Skills 静态校验，引用文件均存在于 ZIP。

## 5. 文档与验收

- 编写安装、升级、卸载、同步和故障降级说明。
- 运行仓库既有模板校验，确认 Cursor marketplace 无新增 Codex 插件条目。
- 生成等价验收报告；当前机器没有 `codex` CLI，真实安装冒烟测试标记为外部环境待补，不虚构通过。

## Review gates

- 修改范围限于 Codex 适配目录及其内部打包/校验脚本、测试、workspace-specflow 必要说明及本次规划产物；不改仓库根 `scripts/`。
- 不修改 `.trellis/scripts/**`、`.trellis/.runtime/**`、CodeWiki 服务端或 specs 业务仓。
- 实现完成后依次执行项目检查、暂存本 change 文件、完整 `/cr` 和 OpenSpec 验证。

## 回滚点

- 新增目录和脚本均为旁路能力；删除 Codex 适配目录与打包入口即可恢复。
- 不改 Cursor marketplace 与 workspace-specflow 源技能行为，避免回滚牵连现有 Cursor 用户。
