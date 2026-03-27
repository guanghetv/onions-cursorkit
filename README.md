# CursorKit

此项目用于维护洋葱内部自建或从第三方收集的`cursor command` `cursor rules` `agent skills`

- [cursor command](.cursor/commands/README.md)
- [cursor rules](.cursor/rules/README.md)
- [agent skills](.cursor/skills/README.md)

## 技能同步

CursorKit 集成了来自 Anthropic 官方的高质量 agent skills。使用以下命令从 [Anthropic skills 仓库](https://github.com/anthropics/skills) 同步官方技能到本地：

```bash
./install/sync-skills
```

### 功能说明

- **职责范围**：此脚本仅负责将 Anthropic 官方技能同步到 CursorKit 本地仓库的 `.cursor/skills/` 目录
- **自定义技能保护**：项目中的自定义技能（`openspec-*` 系列和 `create-feature-branch`）不会被覆盖
- **排除策略**：自动跳过 source-available 许可证的技能（docx、pdf、pptx、xlsx）

### 使用示例

```bash
# 预览同步操作（不实际修改文件）
./install/sync-skills --dry-run

# 执行同步
./install/sync-skills

# 同步前备份现有文件
./install/sync-skills --backup

# 强制覆盖已存在的文件
./install/sync-skills --force
```

### 同步流程

1. 克隆 Anthropic skills 仓库到临时目录
2. 识别和过滤技能（跳过自定义技能和排除列表中的技能）
3. 复制技能目录到 `.cursor/skills/`
4. 更新 `.cursor/skills/README.md`，记录同步时间和源仓库版本
5. 清理临时目录

## 单项同步

在 cursorkit 仓库目录下，使用 `install/cursor` + `--only` + `--name` 同步单个 skill、command 或 rule，默认写入用户 `~/.cursor`（全局生效），无需网络访问：

```bash
# 列出可用条目
bash install/cursor --only skills --list
bash install/cursor --only commands --list
bash install/cursor --only rules --list

# 同步单个 skill 到用户 ~/.cursor（默认，全局生效）
bash install/cursor --only skills --name frontend-design

# 同步单个 command 到用户 ~/.cursor
bash install/cursor --only commands --name cr

# 同步单个 rule（自动识别 .mdc 文件或目录）
bash install/cursor --only rules --name doc-writing-zh

# 同步到指定项目的 .cursor/（而非用户目录）
bash install/cursor --only skills --name frontend-design --target /path/to/project

# 强制覆盖已有文件（跳过冲突检测，直接更新）
bash install/cursor --only skills --name frontend-design --force

# 预览操作（不写入文件）
bash install/cursor --only skills --name frontend-design --dry-run
```

- **默认目标**：单项同步不指定 `--target` 时写入 `~/.cursor`，对所有项目全局生效。
- **指定项目**：使用 `--target <path>` 将条目写入该项目的 `.cursor/` 子目录。

## 项目中快速集成（全量同步）

全量同步会将 commands、rules、skills 三个范围全部写入目标项目的 `.cursor/` 目录，默认目标为**当前目录**。

### SSH 一键安装（推荐）

```bash
# 同步到当前目录（默认）
bash -c 'tmp="$(mktemp -d)" && git clone --depth 1 git@gitlab.yc345.tv:backend/cursorkit.git "$tmp/cursorkit" && bash "$tmp/cursorkit/install/cursor"'

# 同步到指定目录
bash -c 'tmp="$(mktemp -d)" && git clone --depth 1 git@gitlab.yc345.tv:backend/cursorkit.git "$tmp/cursorkit" && bash "$tmp/cursorkit/install/cursor" --target /path/to/project'
```

可选参数示例：

```bash
# 仅同步规则
bash install/cursor --target /path/to/project --only rules

# 预览操作
bash install/cursor --target /path/to/project --dry-run
```

注意：
- 全量同步需要指定 `--repo`（一键安装命令已包含），或设置环境变量 `CURSORKIT_REPO_URL`。
- 仅支持 SSH 仓库地址（`git@host:org/repo.git` 或 `ssh://git@host/org/repo.git`），HTTPS 等方式不受支持。
- 若目标已有 `.cursor` 文件冲突，可使用 `--backup` 或 `--force`。

### git remote 方式（备选）

适合无法直接使用一键安装、但可以访问 SSH 的场景。

1. 在目标项目添加远程：
   - `git remote add cursorkit git@gitlab.yc345.tv:backend/cursorkit.git`
2. 拉取远程内容：
   - `git fetch cursorkit master`
3. 运行安装脚本（在目标项目内执行）：
   - `bash install/cursor --target .`

注意事项：
- 若仓库无共同历史，`git pull` 需要 `--allow-unrelated-histories`，且可能产生合并冲突。
- 如不希望合并历史，可只拉取 `install/cursor` 并执行，不必合并分支。


# 洋葱cursor插件市场

An example Team Marketplace that includes a set of starter plugins for Cursor.

## Included plugins

This repo currently ships five grouped plugins:

- **git-workflows**: commit, PR, CI, merge conflict, and branch validation workflows
- **documentation**: README updates, weekly review summaries, markdown naming, and docs writing
- **pm**: Ticket-oriented PM workflows with MCP config, ticket writing, and board summarization
- **design**: wireframes, component design support, and mockup workflow
- **testing-reliability**: Datadog dashboards, performance optimization, and testing agents

## Repository structure

- `.cursor-plugin/marketplace.json`: marketplace manifest and plugin registry
- `plugins/<plugin-name>/.cursor-plugin/plugin.json`: per-plugin metadata
- `plugins/<plugin-name>/rules`: rule files (`.mdc`)
- `plugins/<plugin-name>/skills`: skill folders with `SKILL.md`
- `plugins/<plugin-name>/agents`: subagent definitions
- `plugins/<plugin-name>/mcp.json`: MCP server configuration for each plugin

## Validate changes

Run:

```bash
node scripts/validate-template.mjs
```

This checks marketplace paths, plugin manifests, and required frontmatter in rule/skill/agent/command files.

## Submission checklist

- Each plugin has a valid `.cursor-plugin/plugin.json`
- Plugin names are unique, lowercase, and kebab-case
- `.cursor-plugin/marketplace.json` entries map to real plugin folders
- Required frontmatter metadata exists in plugin content files
- Logo paths resolve correctly from each plugin manifest
- `node scripts/validate-template.mjs` passes
