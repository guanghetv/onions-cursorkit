## ADDED Requirements

### Requirement: HTTP 响应状态码符合规范
HTTP 接口返回的状态码 SHALL 符合 HTTP 状态码规范，不得将所有响应统一返回 200 后在 body 中传递业务错误码替代 HTTP 语义。

#### Scenario: 错误响应返回 200
- **WHEN** 接口处理失败（如参数错误、未授权、服务内部错误）时返回 HTTP 200
- **THEN** 应提示使用对应语义的状态码（400 Bad Request / 401 Unauthorized / 500 Internal Server Error 等）

#### Scenario: 成功响应返回非 2xx
- **WHEN** 接口处理成功但返回 4xx/5xx 状态码
- **THEN** 应提示改为 2xx 系列（200 OK / 201 Created / 204 No Content 等）
