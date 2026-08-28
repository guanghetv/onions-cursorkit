# Tasks: add-workspace-specflow-codex-plugin

> 执行约束
> - 每个任务必须有验证点，能自动化时先写失败用例再做最小实现。
> - 不修改 Cursor marketplace，不手工维护第二份 workspace-specflow 业务正文。
> - CodeWiki 与代码仓均为只读；未匹配仓库时禁止猜测。
> - Tier 2 需要等价验收报告；缺少 Codex CLI 的真实安装验证必须显式留待外部环境补跑。

## 1. Codex 插件契约

- [x] 1.1 新增官方 `.codex-plugin/plugin.json` 与 Codex 适配入口，保持 Cursor 发现隔离
      验证点: JSON/schema 校验通过；marketplace diff 无 Codex 条目；Skill frontmatter 合规

## 2. 同步与打包

- [x] 2.1 在 Codex 插件目录内实现从 workspace-specflow 唯一源生成自包含技能树的确定性同步
      验证点: 脚本位于该插件目录；仓库根 `scripts/` 无新增入口；连续两次生成的文件清单和摘要一致；源变化时 check 模式失败
- [x] 2.2 用同一插件目录内的脚本实现 ZIP 打包与包内引用完整性校验
      验证点: 解压后根结构、所有相对引用和辅助文件存在；无缓存或旧产物；维护用打包脚本默认不打进用户 ZIP

## 3. CodeWiki 跨仓适配

- [x] 3.1 实现 registry 解析与 remote → GitNexus 规范仓名映射规则
      验证点: `aiclass-specs` 六个 fixture 项映射正确，歧义和缺失项不误匹配
- [x] 3.2 固化 CodeWiki 优先、本地只读降级和步骤级阻断行为
      验证点: 覆盖 CodeWiki 成功、CodeWiki 失败但本地可用、双重失败三类 Scenario

## 4. 文档与验收

- [x] 4.1 编写安装、升级、卸载、同步和故障排查说明
      验证点: 新用户可按文档完成 ZIP 操作，且明确 CodeWiki 权限和本地降级边界
- [x] 4.2 执行全量静态校验并生成等价验收报告
      验证点: 仓库检查、manifest/skill/ZIP/漂移/映射测试通过；真实 Codex 冒烟状态如实记录
