# add-workspace-specflow-codex-plugin

## 背景

- 产品和测试人员需要在以 specs 仓为当前目录的 Codex 会话中使用 workspace-specflow。
- Cursor 依赖 `.code-workspace` 提供多根仓库上下文，Codex 不应依赖该机制，需要通过 `workspace-repos.json` 和 CodeWiki 获取跨仓代码证据。
- 需求来源为飞书工作项 `7100930454`，对应分支 `feat/138-产研SDD工作区插件支持codex-m-7100930454`。

## 目标

- 提供符合 OpenAI Codex 官方插件格式与 Agent Skills 规范、可独立安装的 workspace-specflow ZIP。
- 保持 `plugins/workspace-specflow/` 为唯一业务正文源，并自动检测同步漂移。
- 让 Codex 优先使用 CodeWiki 扫描 registry 关联仓，同时具备明确的本地降级。

## 变更

- 新增与 Cursor marketplace 隔离的 Codex 插件 manifest 和适配层。
- 在 Codex 插件目录内新增确定性同步、结构校验、漂移检查和 ZIP 打包脚本，不新增仓库根 `scripts/` 入口。
- 新增基于 Git remote 的 workspace registry → GitNexus 规范仓名映射规则。
- 新增安装、升级、卸载及降级说明。

## 影响范围

- 文件/模块: Codex 适配目录及其内部打包脚本、相关测试、workspace-specflow 说明
- 数据/API: 无业务 API；读取 `workspace-repos.json` 并调用现有 CodeWiki MCP
- 权限/安全/资金: 代码仓只读扫描；不写入凭证或 CodeWiki token
- 兼容性: 不修改 Cursor marketplace 和现有 Cursor 插件运行行为

## 不做范围

- 不修改 CodeWiki 服务端或索引实现。
- 不为其它 CursorKit 插件提供 Codex 适配。
- 不依赖 Cursor 多根工作区，不向 specs 仓写入插件正文。
- 不在本次引入 Codex 专属 UI、hooks 或业务代码写能力。
- 不把 Codex 打包脚本放到仓库根 `scripts/`，避免影响全局插件市场校验与其它插件工具。

## 验收

- ZIP 解压后包含 `.codex-plugin/plugin.json` 和 `skills/`，所有技能符合 Agent Skills 约束。
- 源 skill 变化会触发漂移检查，重新构建后产物与源一致。
- `aiclass-specs/scripts/workspace-repos.json` 六个仓库可通过 remote 映射到 GitNexus 规范仓名。
- CodeWiki 失败时转本地只读扫描；双重失败只阻断依赖代码上下文的步骤。
- `.cursor-plugin/marketplace.json` 不新增 Codex 插件，Cursor 不出现重复技能。
- 在具备 Codex CLI 的环境补跑真实安装与发现；当前环境缺少 CLI 时报告未验证，不记为通过。

## 风险与回滚

- 风险: Agent Plugins 规范或 Codex 客户端版本差异；通过 schema 校验、版本声明和外部冒烟环境补偿。
- 风险: registry 逻辑名与 GitNexus 规范仓名不一致；以 remote path 精确映射，未匹配时停止猜测。
- 回滚: 删除 Codex 旁路目录和打包入口，不影响 Cursor 插件。

## 需求调整记录

- 2026-08-28：打包、同步与校验脚本固定放在 Codex 插件目录内，不进入仓库根 `scripts/`。

## References

- 飞书工作项：https://project.feishu.cn/ruxiao/tec_prd/detail/7100930454
- OpenAI Codex 插件打包：https://developers.openai.com/plugins/build/plugins
- Agent Skills：https://agentskills.io/specification
- workspace fixture：`/Users/lige/Onion/aiclass-specs/aiclass-specs.code-workspace`
- registry fixture：`/Users/lige/Onion/aiclass-specs/scripts/workspace-repos.json`
