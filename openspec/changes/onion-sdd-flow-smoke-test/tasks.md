# Tasks: onion-sdd-flow-smoke-test

> 执行约束
> - 每个任务先明确验证点，再做最小实现或文档演练。
> - 本 smoke test 不修改业务代码。
> - 不实现 `/onion-auto`。
> - 不修改 Trellis 源码、`.trellis/scripts/**` 或 `.trellis/.runtime/**`。

## 1. Static contract validation

- [x] 1.1 验证 `plugins/onion-sdd` 文件结构完整。
      验证点: `find plugins/onion-sdd -type f | sort`
- [x] 1.2 验证 plugin manifest 和 current template 是合法 JSON。
      验证点: `python3 -m json.tool ...`
- [x] 1.3 验证 marketplace 注册后模板校验通过。
      验证点: `node scripts/validate-template.mjs`

## 2. Flow routing validation

- [x] 2.1 验证 `/onion-plan` 能路由到 Tier 2+ 完整 skills。
      验证点: 搜索 `full-change|openspec-change|external-spec|verify-change`
- [x] 2.2 验证 `/onion-continue` 能描述 Trellis-aware 恢复和 OpenSpec fallback。
      验证点: 搜索 `trellis-adapter|meta.onion|trellis_task|source_hashes`
- [x] 2.3 验证 `/onion-finish` 能以 `e2e-report.md` 判断归档。
      验证点: 本 change 的 `e2e-report.md`

## 3. Boundary validation

- [x] 3.1 验证没有硬性全仓扫描要求。
      验证点: `rg -n "必须全量扫描|全量扫描项目|扫描当前仓库" plugins/onion-sdd`
- [x] 3.2 验证没有旧插件运行时依赖。
      验证点: `rg -n "/fe-sdd|调用 fe-specflow|依赖 fe-specflow" plugins/onion-sdd`
- [x] 3.3 验证 `/onion-auto` 仍为不做范围。
      验证点: README、rule、command、skill 中的边界说明

