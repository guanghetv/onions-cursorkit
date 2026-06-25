# QA Smoke Spec

## 来源

本文件是 smoke-test QA spec 样例，用于验证 `verify-change` 在存在 QA spec 时以 QA spec 为最高优先级。

## 验收场景

| 场景 | 预期 |
|------|------|
| Trellis metadata 指向现有 change | `/onion-continue` 优先恢复该 change |
| `e2e-report.md` 结论通过且无阻塞 | `/onion-finish` 建议可归档 |
| 需要修改 Trellis 源码 | 流程停止并要求用户确认 |
| 用户要求 `/onion-auto` | 标记为后续迭代，不在本轮执行 |

