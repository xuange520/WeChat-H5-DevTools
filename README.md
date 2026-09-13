<div align="center">

# WeChat-H5-DevTools

**微信 4.x 内置浏览器 / 公众号 H5 / 小程序 满血调试与逆向工程套件**

[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Node 18+](https://img.shields.io/badge/Node.js-18+-339933?logo=node.js&logoColor=white)](https://nodejs.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Frida 17+](https://img.shields.io/badge/Frida-17+-FF69B4?logo=frida&logoColor=white)](https://frida.re/)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS-blue.svg)](https://github.com/)

[核心功能](#-核心功能) · [快速上手](#-快速上手) · [命令行指南](#-命令行操作指南) · [实战工作流](#-实战工作流) · [系统架构](#-系统架构) · [免责声明](#-免责声明-disclaimer)

</div>

---

## 项目背景

在微信 4.x（Windows / macOS）架构升级后，官方屏蔽了内置浏览器窗口对物理 `F12` 热键的响应，同时外部脱机浏览器调试常常受阻于 **“请在微信客户端打开链接”**、`WeixinJSBridge` 缺失、异步 Webpack Chunk 分包难以提取等难题。

**`WeChat-H5-DevTools`** 是一套开箱即用的全能解决方案，集 **微信内免按键浮动调试器注入**、**脱机高保真 JSSDK 模拟沙箱**、**本地代码实时热重载 (Local Overrides)**、**Webcrack 批量 AST 解混淆与 Webpack 模块解包** 以及 **全域 API 路由与国密算法静态审计** 于一体，全面覆盖公众号 H5 与微信小程序前端工程！

---

## 核心功能

* **微信 4.x 内置浏览器 DevTools 强开**：基于 Frida 17+ 进程级挂载，自适应适配微信 3.x / 4.x 多架构，一键解锁渲染器调试通道；
* **无感透明代理注入 vConsole**：内置轻量本地代理网关，自动向所有访问的 H5 网页注入 `vConsole` / `Eruda` 移动端浮动控制台，彻底无视客户端热键屏蔽；
* **本地代码实时热重载 (Local Overrides)**：开发调试神器，支持本地单文件秒级替换线上 JS/CSS，自动禁用缓存与跨域放行，修改即时生效；
* **脱机高保真沙箱与 JSSDK 模拟**：内置全平台微信 User-Agent 矩阵与 30+ 常见 `WeixinJSBridge` 原生 API Mock（支持支付、扫码、定位、分享拦截），外部 Chrome/Edge 满血开 F12 不报错；
* **全站 Webpack 分包递归逆向提取**：输入任意公众号 H5 链接，自动递归提取主包、异步 Chunk JS、CSS 及静态资产，按原始路径组织落盘；
* **Webcrack 批量 AST 解混淆与解包**：内置专业级 Webcrack AST 还原引擎，支持 Webpack 打包模块解压，集成微信小程序组件 AST 容错外科手术，自动切除私有组件元数据与悬空闭包，零告警高保真还原；
* **SourceMap 一键还原 `.vue` / `.ts` 原始工程**：自动探测并解包 SourceMap，将编译混淆的代码 1:1 还原为原始的 Vue 单文件组件与 TypeScript 源码；
* **全域 API 路由与密码学安全审计**：离线静态审计已提取的 JS 代码，深度提取后端业务域名 (Base URLs)、微信原生网络库 (`wx.request`, `@haici/request-core`)、国密算法 (`miniprogram-sm-crypto`, `@haici/gmsm4`, `TripleDES`)、非对称加密 (RSA/`jsbn`)、防篡改签名机制与全量业务 API 路由清单。

---

## 快速上手

### 1. 运行环境准备

* **Python 3.9+**
* **Node.js 18+**（用于 Webcrack AST 解混淆引擎）
* **微信客户端**（Windows / macOS）

### 2. 安装项目依赖

```bash
# 克隆仓库
git clone https://github.com/xuange925/wx-h5.git
cd wx-h5

# 安装 Python 依赖
pip install -r requirements.txt

# 安装为全局 CLI 工具 (推荐)
pip install -e .
```

### 3. 一键环境诊断

```bash
wx-h5 doctor
```

---

## 命令行操作指南

你可以通过全局别名 `wx-h5 <命令>` 或 `python main.py <命令>` 进行调用。

### 核心命令与参数索引表

| 命令 | 核心功能 | 核心参数与选项 | 典型调用范例 |
| :--- | :--- | :--- | :--- |
| `doctor` | 本地微信、浏览器与 Frida 环境诊断 | 无 | `wx-h5 doctor` |
| `hook` | 微信客户端进程级 DevTools 参数注入 | `--path, -p` (指定微信主程序路径) | `wx-h5 hook` |
| `proxy` | 启动 vConsole 移动端透明代理网关 | `--port, -p` (默认 8899), `--override-dir, -d` | `wx-h5 proxy --port 8899 -d ./local_js` |
| `override` | 【开发神器】本地代码实时替换与热重载 | `<override_dir>`, `--port, -p` | `wx-h5 override ./local_js --port 8899` |
| `open` | 外部独立沙箱拉起满血 F12 (免微信) | `<url>`, `--browser, -b`, `--ua, -u` | `wx-h5 open "https://..." --ua ios` |
| `dump` | 全站 Webpack 异步分包递归抓取 | `<url>`, `-o` (输出目录), `-d` (抓取后自动解混淆) | `wx-h5 dump "https://..." -o ./site -d` |
| `deobfuscate` | 【Webcrack】批量 AST 解混淆与模块解包 | `<target_dir>`, `-o` (输出目录), `-a / --all` (批量子工程) | `wx-h5 deobfuscate ./site -a` |
| `restore` | 从 SourceMap 逆向还原 Vue/TS 源码 | `<target_dir>`, `-o` (输出目录) | `wx-h5 restore ./site` |
| `scan` | 静态审计提取域名、API、国密与凭据 | `<target_dir>`, `-e` (导出MD报告), `-a / --all` | `wx-h5 scan ./site -e report.md` |

---

## 实战工作流

### 场景 1：在微信客户端内部直接唤出调试器 (vConsole 浮动绿标)
*适用场景：需要在真实微信登录态、支付环境或企业微信内部调试页面。*

1. **启动透明代理网关**：
   ```bash
   wx-h5 proxy --port 8899
   ```
2. **配置微信或系统代理**：
   将系统代理或网络抓包工具的上游代理设置为 `127.0.0.1:8899`。
3. **打开任意公众号网页**：
   页面右下角将自动浮现绿色 `vConsole` 按钮，点击即可实时查看 Console 日志、Network 抓包、Storage 缓存与 Elements DOM 树！

---

### 场景 2：【开发神器】本地代码实时映射替换与热重载 (Local Overrides)
*适用场景：线上 H5 出了 Bug，想在本地修改某个 JS/CSS 文件并立即在微信或浏览器中查看实际效果，无需繁琐重新打包上线。*

1. **准备本地修改后的 JS 文件**（例如 `D:/debug_js/chunk-common.js`）；
2. **启动 Local Overrides 拦截服务**：
   ```bash
   wx-h5 override D:/debug_js --port 8899
   ```
3. **刷新网页**：
   当网页请求该脚本时，代理网关将自动命中并**以本地文件秒级替换返回**（自动禁用缓存并放行跨域），修改本地代码立即生效！

---

### 场景 3：脱离微信，在 Chrome / Edge 原生 F12 中畅快调试
*适用场景：微信内无法按 F12，想在电脑原生浏览器中打断点、抓包、修改 CSS，且不被“请在微信客户端打开”拦截。*

```bash
# 模拟 iPhone 微信环境并在 Edge 中打开
wx-h5 open "https://mp.weixin.qq.com/s/xxxx" --browser edge --ua ios

# 模拟 Android 微信环境并在 Chrome 中打开
wx-h5 open "https://mp.weixin.qq.com/s/xxxx" --browser chrome --ua android
```
工具会在浏览器启动瞬间（`document_start` 第 0 毫秒）自动注入包含 30+ 原生 API 的 `WeixinJSBridge` 与 `JSSDK` 挡板，目标页面直接判定为纯正微信环境，右侧自动展开满血 DevTools 开发者工具！

---

### 场景 4：批量 AST 解混淆与 Webpack 模块解包 (Webcrack 引擎)
*适用场景：面对混淆压缩的 JS 代码或小程序单体包，将其恢复为清晰可读的原始模块结构。*

```bash
# 单工程解混淆
wx-h5 deobfuscate "./output/wx1363195c4fb75cfc/344"

# 批量解混淆某个总目录下的所有子版本/子小程序工程
wx-h5 deobfuscate "./output/wx1363195c4fb75cfc" --all
```
*内置 AST 容错清洗算法，自动清除微信私有组件元数据与孤立闭包，告警 100% 清零。*

---

### 场景 5：全域静态逆向代码审计与资产报告导出
*适用场景：梳理目标系统的后端 API 接口清单、硬编码域名、密码学算法与鉴权安全机制。*

```bash
# 执行静态扫描并导出高质感 Markdown 审计报告
wx-h5 scan "./output/site_deobfuscated" --export audit_report.md
```

**扫描维度涵盖**：
* **后端业务域名 (Base URLs)**：提取硬编码的业务 API 接口域名；
* **网络请求框架**：识别 `wx.request`, `uni.request`, `@haici/request-core`, `axios` 等；
* **密码学与加密特征**：识别国密 SM2/SM3/SM4、TripleDES、AES、RSA/jsbn、HMAC-SHA256、JWT/jtoken、时间戳防重放签名；
* **凭据与敏感字段**：识别微信 AppID、插件依赖 ID、业务 Token 与请求头；
* **业务 API 清单**：提纯去重全量 RESTful 与 RPC 路由接口。

---

## 常见问题排障 (FAQ)

<details>
<summary><strong>Q1: 运行 <code>wx-h5</code> 提示“无法识别为 cmdlet 或命令”？</strong></summary>

> **解答**：请在项目根目录运行 `pip install -e .`，或者直接使用 `python main.py <命令>` 进行调用。
</details>

<details>
<summary><strong>Q2: 执行 <code>wx-h5 hook</code> 提示“已有微信进程在运行”？</strong></summary>

> **解答**：微信在开启状态下无法由调试器冷启动。工具内置了自愈清理逻辑，会自动提示并终止旧进程重新拉起；你也可以手动完全退出微信托盘图标后再执行此命令。
</details>

<details>
<summary><strong>Q3: 外部浏览器打开页面仍提示“环境异常”或特定 JSSDK 接口未响应？</strong></summary>

> **解答**：工具沙箱已内置 `getBrandWCPayRequest`（微信支付）、`getLocation`（定位）、`scanQRCode`（扫码）等 30+ 常见接口。若遇到极其私有的微信定制 API，可直接在 `wechat_h5_devtools/sandbox/polyfills/weixin_bridge.js` 中按需扩展对应 Mock 响应。
</details>

---

## 系统架构

```
+------------------------------------------------------------------------+
|                   WeChat-H5-DevTools (统一调度中枢)                    |
+------------------+----------------------+------------------------------+
| 1. inapp_injector| 2. stealth_sandbox   | 3. asset_extractor           |
| (微信内置注入引擎) | (外部高保真沙箱引擎) | (全站源码逆向提取引擎)       |
+------------------+----------------------+------------------------------+
| * 进程自适应探测 | * 全平台微信 UA 矩阵 | * HTML/DOM 深度解析器        |
| * Frida 17+ 挂载 | * WeixinJSBridge Mock| * Webpack 异步分包递归器     |
| * 透明代理注头   | * JSSDK 1.6.0 挡板系统| * SourceMap 源码目录还原     |
| * vConsole 浮动窗| * 原生 Chrome 满血拉起| * Webcrack AST 解混淆与解包  |
| * Local Overrides|                      | * 全域 API 与国密特征静态审计|
+------------------+----------------------+------------------------------+
```

---

## 免责声明 (Disclaimer)

1. **合法合规与技术研究**：本项目（`WeChat-H5-DevTools`）仅用于网络安全研究、前端跨平台兼容性测试、Web 开发调试与技术学习交流，严禁将其用于任何侵犯他人合法权益、危害网络安全或违反相关法律法规的活动。
2. **风险自负原则**：使用者在基于本项目进行调试、抓包或接口调用时，须自行确保行为的合法合规性。任何因不当使用、恶意滥用或二次开发所引发的法律纠纷、系统故障、财产损失或账号风险，本项目作者及贡献者概不承担任何直接或连带法律责任。
3. **知识产权尊重**：本项目中涉及的第三方商标、技术协议及相关标识，其知识产权均归其合法所有者所有。若相关方认为本项目存在侵权疑虑，请通过 Issue 与作者联系，我们将依法核实并积极配合处理。

---

## 开源许可证

本项目基于 [MIT License](./LICENSE) 协议开源。
