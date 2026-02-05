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

## 项目中快速集成

### SSH 一键安装（推荐）

- 默认当前目录：
```bash
bash -c 'tmp="$(mktemp -d)" && git clone --depth 1 git@gitlab.yc345.tv:backend/cursorkit.git "$tmp/cursorkit" && bash "$tmp/cursorkit/install/cursor"'
```
- 指定目标目录：
```bash
bash -c 'tmp="$(mktemp -d)" && git clone --depth 1 git@gitlab.yc345.tv:backend/cursorkit.git "$tmp/cursorkit" && bash "$tmp/cursorkit/install/cursor" --target /path/to/project'
```

可选参数示例：
- 仅同步规则：
```bash
bash install/cursor --target /path/to/project --only rules
```
- 预览操作：
```bash
bash install/cursor --target /path/to/project --dry-run
```

注意：
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