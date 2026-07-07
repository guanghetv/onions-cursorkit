## ADDED Requirements

### Requirement: 用户设备参数脱敏表示
用户设备相关参数 SHALL 使用无语义化、脱敏的字段表示，不得使用可读字段；如 `deviceid` SHALL 用 `omvd` 表示。

#### Scenario: 使用明文 deviceid 字段
- **WHEN** 接口或数据库中出现 `device_id`、`deviceId` 等可读设备标识字段
- **THEN** 应提示改为脱敏字段（如 `omvd`），并参考设备 ID 相关规范

---

### Requirement: 个人敏感信息加密存储
个人敏感信息（如手机号）SHALL 加密存储，不得在数据库中明文保存；已注销用户信息 SHALL 进行脱敏（编码或加密）。

#### Scenario: 手机号明文存储
- **WHEN** 数据库字段直接存储明文手机号
- **THEN** 应提示使用加密方案（参考 `gitlab.yc345.tv/backend/utils/-/tree/feature/crypt/crypt`）加密后存储

#### Scenario: 已注销用户数据未脱敏
- **WHEN** 注销用户流程中未对业务库中的敏感字段做脱敏处理
- **THEN** 应提示对姓名、手机号等字段进行编码或加密

---

### Requirement: 视频播放符合加密规范
视频播放业务 SHALL 符合洋葱视频加密规范，不得使用未加密的视频直链。

#### Scenario: 视频使用未加密直链
- **WHEN** 接口返回未经加密处理的视频播放地址
- **THEN** 应提示参考《洋葱视频加密规范》实现加密播放

---

### Requirement: 接口安全推荐开启网关加密
对外接口 SHALL 推荐在网关层开启接口加密（签名验证），防止接口被未授权调用。

#### Scenario: 新接口未评估网关加密
- **WHEN** 新增对外接口未在 API 设计中说明是否需要网关签名
- **THEN** 应提示评估并参考《各端签名逻辑整理》决定是否开启接口加密
