## Codex 跨仓代码上下文

<CODEX-WORKSPACE-CONTEXT>
执行本技能中任何“扫描代码仓库”步骤前，必须先加载 `workspace-code-context` skill。

- 不依赖 Cursor `.code-workspace` 或多根工作区。
- 从当前 specs 仓的 `workspace-repos.json` 或 `scripts/workspace-repos.json` 读取关联仓。
- 优先通过 CodeWiki/GitNexus 查询代码；仓库必须按 Git remote path 映射到工具返回的规范仓名，禁止直接猜测。
- CodeWiki 不可用时才按 registry 的本地 `path` 只读扫描，并明确提示降级。
- 两种方式均不可用时，只停止当前依赖代码证据的步骤，不阻断纯 PRD、同步或状态查询。
</CODEX-WORKSPACE-CONTEXT>
