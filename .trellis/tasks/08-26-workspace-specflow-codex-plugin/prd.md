# 封装 workspace-specflow Codex 插件

## 目标

基于现有 `plugins/workspace-specflow/` 封装可独立安装的 Codex 插件，使产品和测试人员在以 specs 仓库为主工作目录的 Codex 会话中复用现有工作区插件能力，并通过 CodeWiki 扫描 `workspace-repos.json` 关联仓库的代码上下文。

## 已确认事实

- `plugins/workspace-specflow/skills/` 是核心流程的唯一维护源，Codex 适配层不得复制并分叉业务正文。
- Codex 插件与 Cursor 插件共存于当前 `cursorkit` 仓库并纳入 Git 管理。
- 分发方式为打包 ZIP 后发送给产品或测试人员安装。
- Codex 使用场景以 specs 仓库为主工作目录。
- 现有 Cursor 插件本身不调用 CodeWiki；CodeWiki 是本次 Codex 封装新增的代码上下文获取约束。

## 需求

- 提供符合 Codex 插件规范的 manifest、技能映射和必要说明。
- 复用现有 workspace-specflow skills、references 与 scripts，不维护第二套流程正文。
- 提供可重复执行的 ZIP 打包与结构校验方式；打包脚本放在 Codex 插件目录内，不放仓库根 `scripts/`。
- Codex 插件需声明使用 CodeWiki 识别并扫描 `workspace-repos.json` 中登记的关联仓库。
- 需要代码扫描的步骤优先调用 CodeWiki；CodeWiki 不可用时尝试本地仓库扫描并明确提示当前用户。
- CodeWiki 与本地扫描均不可用时，仅阻断依赖代码上下文的当前步骤；纯 PRD、同步和状态查询能力不受影响。
- 不向 specs 仓库写入插件正文，不向 `~/.agents/skills/` 复制同名 skills，避免 Cursor 重复发现。

## 技术约束

- Codex 包采用 OpenAI 官方格式，manifest 使用 `.codex-plugin/plugin.json`，技能遵循 Agent Skills 规范。
- Codex 包通过构建期复制生成完整 ZIP；ZIP 自包含 skills、references 与 scripts，不要求用户访问 cursorkit。
- `plugins/workspace-specflow/` 是业务正文唯一维护源，生成内容禁止手工修改，并提供漂移检测。
- Codex 包不注册 `.cursor-plugin/marketplace.json`，不创建 `.cursor-plugin/plugin.json`，不在 Cursor 中展示。
- CodeWiki 仓库定位以 `workspace-repos.json` 的 `remote` 与 GitNexus 规范仓名匹配为主，禁止直接假设逻辑名等于规范仓名。

## 验收标准

- [ ] ZIP 解压安装后，Codex 能发现并调用 workspace-specflow 的核心技能。
- [ ] Cursor 团队插件不因 Codex 插件安装而出现同名技能重复。
- [ ] 修改源 skill 后，Codex 打包产物可自动同步且能检测漂移。
- [ ] 在 specs 仓库中，Codex 能读取 `workspace-repos.json` 并通过 CodeWiki 获取关联仓代码上下文。
- [ ] CodeWiki 失败时先尝试本地扫描并提示用户；双重失败只阻断依赖代码上下文的步骤。
- [ ] 产品和测试用户可依据简短安装说明完成安装、升级和卸载。
- [ ] Codex 插件目录未进入 Cursor marketplace，Cursor 插件列表不新增重复的 workspace-specflow。
- [ ] 静态校验覆盖 Agent Plugins manifest、Agent Skills frontmatter、相对引用、ZIP 根目录和生成漂移。
- [ ] 在具备 Codex CLI 的环境完成一次安装、技能发现与 CodeWiki 查询冒烟验证；本机无 Codex 时明确记录为待补验证。

## 不做范围

- 不修改 CodeWiki 服务端或索引实现。
- 不为全部 CursorKit 插件提供 Codex 适配。
- 不把 Codex 适配产物提交到业务 specs 仓库。
- 不把 Codex 打包脚本放到仓库根 `scripts/`。
