# WeChat-H5-DevTools v1.0.0 发布说明 (Release Notes)

- **版本号**：`v1.0.0`
- **发布日期**：`2026-09-14`
- **适用平台**：Windows 10 / Windows 11 (x64)
- **微信内核支持**：微信 4.1.x (`4.1.13.12`) 及 4.0.x，RadiumWMPF (`25510` 及历史版本)

---

## 核心更新概括

1. **微信版本与内核动态感知**：
   - 动态识别并捕获当前运行中的微信主程序 (`Weixin.exe` / `WeChat.exe`)；
   - 原生提取宿主机微信真实 PE 版本号 (`4.1.13.12`) 与机器架构 (`x64`)；
   - 实时识别 RadiumWMPF 沙箱主控与渲染沙箱进程拓扑。

2. **现代 Fluent WebGUI 桌面工作台**：
   - 基于原生 WebView2 硬件加速打造，全面融入 Supabase 深色美学与主题规范；
   - 原生多尺寸应用图标装配与标题栏适配；
   - 本地物理日志实时存盘 (`records/logs/console_stream.log`)，支持一键复制与目录定位。

3. **公众号 / 小程序 H5 调试按钮注入**：
   - 绕过 RadiumWMPF 安全沙箱限制，在任意公众号文章或网页中注入绿色 vConsole 调试按钮；
   - 全权限解锁 `WeixinJSBridge`、控制台日志、网络抓包与 Storage 审查。

4. **脱机高保真沙箱与透明代理**：
   - 本地 HTTP/HTTPS 透明代理监听 (`127.0.0.1:8899`)；
   - 外部脱机浏览器 (Edge / Chrome) 模拟真实微信环境，注入 JSSDK Polyfill 与 UA 矩阵。

5. **AST 语法树解混淆与安全审计**：
   - 自动化批量深度解混淆，还原控制流平坦化与字符串解密池；
   - 递归提取 Webpack 异步分包与 SourceMap 还原；
   - 全域 API 路由、敏感凭据与国密算法静态安全审计。

---

## 快速启动

```bash
# 启动桌面控制台
wx-h5 gui

# 或直接运行
python examples/supabase_gui/app.py
```
