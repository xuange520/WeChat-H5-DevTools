# Changelog

All notable changes to the WeChat-H5-DevTools project will be documented in this file.
The format is based on Keep a Changelog, and this project adheres to Semantic Versioning.

---

## [1.1.0] - 2026-09-15

### [ADDED]
- **微信公众号内核浏览器 CDP 调试引擎 (Kernel CDP Gateway)**:
  - 9421 内部调试端口与 62000 标准 CDP 端口双通道复合网关，兼容 Chrome DevTools Protocol 1.3 规范。
  - 标准 HTTP 端点支持：`/json`, `/json/version`, `/json/list`, `/json/protocol`, `/json/new`。
  - 动态 Protobuf 二进制与标准 CDP JSON 报文双向透明桥接，自动化提取页面 Title、URL 与运行上下文。
  - 针对外部 DevTools 地址栏触发的 `Page.navigate` 进行即刻响应与全生命周期事件流合成（`Page.frameStartedLoading`、`Page.frameNavigated`、`Page.domContentEventFired`、`Page.loadEventFired`、`Page.frameStoppedLoading`）。
- **Google Chrome / Microsoft Edge 设备挂载完整链路**:
  - 权威支持 `chrome://inspect` 与 `edge://inspect` 发现并挂载微信原生内置窗口。
  - 支持 `devtools://devtools/bundled/inspector.html?ws=127.0.0.1:62000` 秒级直连进入独立 F12 控制台。
- **GUI 桌面客户端全功能穿透与日志管理**:
  - 11 项核心 Bridge API 接口全覆盖（系统感知、热注入、代理控制、AST 反混淆、安全审计、全量日志读取与清空）。
  - 物理日志自动同步存盘至本地 `records/logs/console_stream.log`，前端新增日志清空与元数据动态刷新。
- **SOP 规范与操作指引**:
  - 系统化梳理微信公众号推文 / H5 页面 4 大最快调试操作顺序（vConsole 绿标注入、原生右键检查、DevTools 地址栏直达、脱机沙箱双开 F12）。
  - 微信小程序 4 步标准调试 SOP。
  - 聚焦实战：微信推文直奔 4 大实测最快调试路径（微信内绿标/原生右键/地址栏秒达/沙箱双开）。

### [CHANGED]
- `wx-h5 open` 默认行为全面升级为启动微信内核 CDP 调试服务，直连微信内置原生窗口（免弹外部浏览器）；增加 `--sandbox` 参数作为旧版脱机模拟沙箱回退开关。
- 将 `check_port` 预检绑定地址从 `127.0.0.1` 优化为 `0.0.0.0`，杜绝 Windows Winsock 下因地址重叠导致的 WinError 10048 误报。

### [FIXED]
- 修复外部开发者工具连接初始白板目标时因离线探测导致挂死的问题，增加基础 CDP 探测指令合成响应机制。
- 修复 32 位旧版微信与 64 位注入框架架构不匹配的阻断提示，明确官方 64 位无缝升级指引。

---

## [1.0.0] - 2026-09-14

### [ADDED]
- 首次官方生产级发布。
- 基于 Frida 17+ 的微信 4.x 内置浏览器进程级 Hook 与参数注入。
- 本地透明代理网关自动注入 vConsole / Eruda 移动端控制台。
- 本地代码实时热重载 (Local Overrides) 拦截服务。
- 脱机高保真沙箱与 30+ 常见 `WeixinJSBridge` 原生 API Mock。
- 全站 Webpack 分包递归抓取与 AST 深度解混淆还原。
- 现代 Fluent / Supabase 暗黑极简桌面工作台。
