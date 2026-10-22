# workspace-specflow Codex 插件设计

## 架构

采用“单一源目录 + 可重复构建包”：

```text
plugins/workspace-specflow/                 # 业务正文唯一源
codex-plugins/workspace-specflow/           # Codex 插件源：manifest、适配说明、打包脚本
  .codex-plugin/plugin.json
  README.md
  scripts/pack.py                           # 同步、校验、ZIP 入口（仅本插件，不进仓库根 scripts/）
  dist/                                     # 本地生成 ZIP，不作为业务正文源
```

Codex 插件不放入 `plugins/` 的 Cursor marketplace 发现链路。打包脚本只放在该 Codex 插件目录内，不新增仓库根 `scripts/` 入口，也不改现有 `scripts/validate-template.mjs` 等全局工具。构建时从 `plugins/workspace-specflow/skills/` 复制完整技能树到临时包根，叠加 Codex 专属说明后生成 ZIP；维护用打包脚本默认不打进给用户的 ZIP。

## 包结构

```text
workspace-specflow/
├── .codex-plugin/
│   └── plugin.json
├── README.md
└── skills/
    ├── req-new/
    │   └── SKILL.md
    └── ...
```

`.codex-plugin/plugin.json` 按 OpenAI Codex 官方格式声明 `skills: "./skills/"`。Cursor 的 `commands/` 与 `.mdc` rules 不直接进入标准包；需要保留的触发语义应由技能 description 或 Codex 专属入口 skill 表达。

## 同步策略

- 构建期复制源 skills，保留每个技能下的 `references/`、`scripts/` 和 assets。
- 复制后执行可移植性检查：禁止引用 Cursor 独有命令路径、绝对的 cursorkit 路径或包外文件。
- `--check` 模式在临时目录生成并与预期清单/摘要对比，用于发现源技能变化导致的漂移。
- ZIP 每次从干净临时目录生成，避免把缓存、系统文件或旧产物带入。

## CodeWiki 跨仓流程

1. 从当前 specs 仓定位根目录或 `scripts/workspace-repos.json`。
2. 解析 `name`、`path`、`remote`，不得依赖 `.code-workspace` 的多根运行时。
3. 调用 CodeWiki/GitNexus 仓库清单。
4. 将 `remote` 归一化为 GitLab path，与清单规范仓名精确匹配；仅当 `remote` 缺失且 basename 唯一时允许名称兜底。
5. 对匹配仓使用 CodeWiki 代码搜索；未匹配项给出证据缺口，不猜测。
6. CodeWiki 不可用时，检查 `path` 是否可访问并执行本地只读扫描，同时提示降级。
7. 两种方式均不可用时，只停止当前依赖代码证据的步骤。

## 兼容与回滚

- 原 Cursor 插件目录和 marketplace 条目不修改，现有用户行为保持不变。
- Codex 包删除或停止分发即可回滚，不影响 Cursor 插件。
- 源技能不为 Codex 分叉；适配差异集中在构建配置和 Codex 专属入口说明。

## 验证

- JSON schema/语法、Skill frontmatter 和目录名校验。
- 两次构建产物清单与摘要一致。
- 修改一个源 skill 后 `--check` 失败，重新同步后通过。
- ZIP 解压后根目录、相对引用和必要脚本完整。
- 用 `aiclass-specs` fixture 验证六个 registry 项能映射到 GitNexus 规范仓名。
- 有 Codex CLI 的环境补跑安装、发现和一次 CodeWiki 查询冒烟测试。
