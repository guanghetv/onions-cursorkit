# Codex 插件格式与 CodeWiki 跨仓调研

## 结论

- Codex 官方插件格式要求 manifest 位于 `.codex-plugin/plugin.json`，技能位于 `skills/<name>/SKILL.md`。
- manifest 至少声明稳定的 `name`，本项目同时声明 `version`、`description` 和相对路径 `skills: "./skills/"`。
- Agent Skills 要求技能目录名与 `SKILL.md` frontmatter 的 `name` 一致，名称仅允许小写字母、数字和连字符。
- 当前本机没有 `codex` CLI，规划阶段只能完成静态结构、同步漂移和 ZIP 内容校验；真实安装发现验证需要在具备 Codex 的环境补跑。

## 分发边界

- Codex 包必须可独立安装，因此 ZIP 中应包含构建期复制后的完整 `skills/`、`references/` 和 `scripts/`。
- `plugins/workspace-specflow/` 继续作为业务正文唯一维护源；Codex 目录只保存 manifest、Codex 专属适配说明和同步/校验/打包脚本（脚本不进仓库根 `scripts/`）。
- 构建产物不作为第二套源码手工维护。每次打包从源目录生成，并用漂移检查保证修改源 skill 后必须重新同步。
- Codex 插件不加入 `.cursor-plugin/marketplace.json`，也不创建 `.cursor-plugin/plugin.json`，因此不会作为 Cursor 团队插件展示。

## CodeWiki 映射事实

参考 specs 仓：

- `aiclass-specs.code-workspace` 将 specs 仓和六个代码仓组成 Cursor 多根工作区。
- `scripts/workspace-repos.json` 为每个代码仓记录 `name`、本地 `path` 和 Git `remote`。
- Codex 没有依赖 Cursor 多根工作区的发现机制，应从当前 specs 仓读取该注册表。

CodeWiki/GitNexus 返回的规范仓名包含命名空间，例如：

- `teacher-desk` → `backend/teacher-desk`
- `teacher-ai-class` → `backend/teacher-ai-class`
- `teacher-school` → `teacher/backend/teacher-school`
- `onion-edu-manage` → `teacher/fe/onion-edu-manage`
- `padh5` → `teacher/fe/padh5`
- `teacher-workbench` → `teacher/fe/teacher-workbench`

因此不能把注册表 `name` 直接当作 CodeWiki `repo`。适配指令应先调用仓库清单，再以 `remote` 的 GitLab path 与规范仓名精确匹配。仅当 `remote` 缺失且仓库 basename 在清单中唯一时，才允许按 `name` 兜底；`remote` 存在但未命中时保持未匹配，不得猜测。若 CodeWiki 不可用，则按 `path` 做本地只读扫描并明确提示降级。

## 参考

- OpenAI Codex 插件打包：https://developers.openai.com/plugins/build/plugins
- Agent Skills：https://agentskills.io/specification
- specs 工作区：`/Users/lige/Onion/aiclass-specs/aiclass-specs.code-workspace`
- 仓库注册表：`/Users/lige/Onion/aiclass-specs/scripts/workspace-repos.json`
