<div align="center">

<img src="docs/images/logo.png" width="160" alt="WeChat-H5-DevTools Logo" />

# WeChat-H5-DevTools

**微信 4.x 内置浏览器 / 公众号 H5 / 小程序 满血调试与逆向工程套件**

[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Node 18+](https://img.shields.io/badge/Node.js-18+-339933?logo=node.js&logoColor=white)](https://nodejs.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Frida 17+](https://img.shields.io/badge/Frida-17+-FF69B4?logo=frida&logoColor=white)](https://frida.re/)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS-blue.svg)](https://github.com/)

[核心功能](#features) · [实测效果](#screenshots) · [快速上手](#quickstart) · [命令行指南](#cli) · [实战工作流](#workflows) · [兼容矩阵](#matrix) · [常见问题](#faq) · [赞助支持](#sponsor) · [交流群](#community) · [免责声明](#disclaimer)

</div>

---

<a id="background"></a><a id="项目背景"></a>
## 📖 项目背景

在微信 4.x（Windows / macOS）架构升级后，官方彻底屏蔽了内置浏览器窗口对物理 `F12` 热键的响应，同时外部脱机浏览器调试常常受阻于 **“请在微信客户端打开链接”**、`WeixinJSBridge` 缺失、异步 Webpack Chunk 分包难以提取等难题。

**`WeChat-H5-DevTools`** 是一套开箱即用的工业级全能解决方案，集 **微信内免按键浮动调试器注入**、**脱机高保真 JSSDK 模拟沙箱**、**本地代码实时热重载 (Local Overrides)**、**Webcrack 批量 AST 解混淆与 Webpack 模块解包** 以及 **全域 API 路由与国密算法静态审计** 于一体，全面赋能微信 Web 生态开发与安全审计！

---

<a id="matrix"></a><a id="兼容矩阵"></a><a id="版本与内核兼容矩阵"></a><a id="微信版本与内核兼容矩阵"></a>
## 🖥️ 微信版本与 RadiumWMPF 内核兼容矩阵 (Compatibility Matrix)

为了方便非专业开发者与安全研究人员一目了然，下表列出了工具对微信全系列主流版本、**`RadiumWMPF` 内核版本**架构及核心进程的深度适配支持情况：

| 微信客户端大版本 | 典型测试验证版本 | RadiumWMPF 内核版本 (Kernel) | 渲染/Web 核心进程名 | 调试注入机制 | 兼容状态 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **微信 4.1.x 最新版**<br>*(当前主推)* | **`4.1.13.12`**<br>`4.1.12.26`<br>`4.1.5.30` | **`25560`** / **`25510`** / `25497` / `25364` / `20089` | `WeixinExt.exe`<br>`Weixin.exe` (`--type=renderer`) | Frida 动态拦截 `CreateProcessW` 挂载注入<br>+ 透明代理无感注入 `vConsole` | `[PASS]` 满血完美支持 |
| **微信 4.0.x 系列**<br>*(重构初期)* | `4.0.2`<br>`4.0.1`<br>`4.0.0` | **`16389` / `16203` / `16133` / `14315`**<br>*(Blink 深度重构版架构)* | `Weixin.exe`<br>`WeChatAppEx.exe` | 进程自适应探测与多点命令行注头 | `[PASS]` 满血完美支持 |
| **微信 3.9.x 经典版**<br>*(长期支持)* | `3.9.12`<br>`3.9.11`<br>`3.9.10` 及旧版 | **`11581` ~ `13909`**<br>*(经典 XWeb / Chromium 85~108)* | `WeChat.exe`<br>`WeChatAppEx.exe` | 经典 `--xweb-enable-inspect=1` 参数注入通道 | `[PASS]` 满血完美支持 |
| **外部脱机沙箱**<br>*(免微信客户端)* | 任意操作系统<br>(Win / Mac / Linux) | **Edge / Chrome 最新版**<br>*(Chromium 130+ 满血原生引擎)* | `msedge.exe`<br>`chrome.exe` | `document_start` 毫秒级注入 30+ WeixinJSBridge Mock | `[PASS]` 满血原生 F12 |

> **💡 如何查看本机的 RadiumWMPF 内核版本？**
> 1. 按快捷键 `Win + R` 打开运行窗口，粘贴并回车：
>    ```text
>    %AppData%\Tencent\xwechat\XPlugin\Plugins\RadiumWMPF
>    ```
> 2. 打开后看到的以纯数字命名的文件夹（如 `25510`、`17127`、`16389` 等），该数字即为本机微信当前正在生效使用的 **RadiumWMPF 内核版本号**！
> 3. 工具内置了 `WeChatFinder` 与多源版本探测器，全自动适配上述所有版本，无需手动配置偏移。

---

<a id="quickstart"></a><a id="快速上手"></a><a id="新手起步"></a><a id="小白新手三步起飞"></a>
## 💡 小白新手三步起飞指引（不用懂 AI，不用懂代码！）

如果你不熟悉 AI 或复杂的技术术语，只需跟随以下 3 步，像使用普通软件一样直接上手：

### 第一步：打开终端安装（只需执行一次）
按键盘 `Win + R`，输入 `cmd` 或 `powershell` 回车，粘贴运行：
```bash
git clone https://github.com/xuange520/WeChat-H5-DevTools.git
cd WeChat-H5-DevTools
pip install -r requirements.txt
pip install -e .
```
*（执行完毕后，你电脑里的任何目录都可以直接使用 `wx-h5` 命令了！）*

### 第二步：按你的实际需求，直接复制一行命令使用！

* **需求 A：我想在电脑微信里面直接看报错日志、抓包看数据？**
  * 在命令行输入：
    ```bash
    wx-h5 proxy
    ```
  * 打开微信里的任意公众号网页，右下角就会自动出现**绿色的 vConsole 调试小球**，点开就能查看 Log、Network 抓包、Storage 缓存！

* **需求 B：网页提示“请在微信客户端打开”，我想在电脑自带 Edge/Chrome 里按 F12 调试？**
  * 在命令行输入（把链接换成你的网页）：
    ```bash
    wx-h5 open "https://你的公众号网页链接.com"
    ```
  * 电脑会自动弹出一个满血 Edge/Chrome 浏览器，自带完整 F12 开发者工具，并且网页会误以为你是在真实的微信手机端中打开，绝不报错！

* **需求 C：我想把混淆压缩的 JS 代码（一堆看不懂的 a, b, c 变量）还原成清晰好懂的代码？**
  * 在命令行输入：
    ```bash
    wx-h5 deobfuscate "你的代码文件夹路径"
    ```
  * 工具会自动执行 AST 逆向解混淆，并把 Webpack 打包的大文件彻底拆分成各个独立的业务模块！

* **需求 D：我想一键查出这个系统用了什么后端 API 接口、域名、国密加密算法？**
  * 在命令行输入：
    ```bash
    wx-h5 scan "你的代码文件夹路径" -e 审计报告.md
    ```
  * 几秒钟后，就会在当前目录下生成一份排版精美、包含了所有接口与加密特征的完整报告文件！

---

<a id="screenshots"></a><a id="实测效果"></a><a id="实战效果"></a>
## 📷 微信内置推文实盘调试效果展示 (Live Screenshots)

基于最新微信客户端（`4.1.13.12`）与 `RadiumWMPF` 内核实测，无需逆向修改微信二进制，公众号推文与 H5 页面无感注入：

<div align="center">

| 微信公众号推文右下角常驻绿色 vConsole 按钮 | 点击绿色按钮即刻展开移动端完整控制台 |
| :---: | :---: |
| <img src="docs/images/wechat_article_vconsole_btn.png" width="460" alt="公众号推文右下角浮动绿色 vConsole 按钮" /> | <img src="docs/images/wechat_article_vconsole_panel.png" width="460" alt="推文点击展开移动端完整 vConsole 控制台" /> |
| *图 1：微信内置浏览器打开任意推文，右下角自动浮现 vConsole 绿标* | *图 2：点击绿标即刻展开 Console、Network 抓包、Storage 与 DOM 树* |

</div>

---

<a id="features"></a><a id="核心功能"></a><a id="核心功能全景"></a>
## ✨ 核心功能全景

* **微信 4.x 内置浏览器 DevTools 强开**：基于 Frida 17+ 进程级挂载，自适应适配微信 3.x / 4.x 多架构（全面覆盖最新的 `4.1.13.12`），一键解锁渲染器调试通道；
* **无感透明代理注入 vConsole**：内置轻量本地代理网关，自动向所有访问的 H5 网页注入 `vConsole` / `Eruda` 移动端浮动控制台，彻底无视客户端热键屏蔽；
* **本地代码实时热重载 (Local Overrides)**：开发调试神器，支持本地单文件秒级替换线上 JS/CSS，自动禁用缓存与跨域放行，修改即时生效；
* **脱机高保真沙箱与 JSSDK 模拟**：内置全平台微信 User-Agent 矩阵与 30+ 常见 `WeixinJSBridge` 原生 API Mock（支持支付、扫码、定位、分享拦截），外部 Chrome/Edge 满血开 F12 不报错；
* **全站 Webpack 分包递归逆向提取**：输入任意公众号 H5 链接，自动递归提取主包、异步 Chunk JS、CSS 及静态资产，按原始路径组织落盘；
* **Webcrack 批量 AST 解混淆与解包**：内置专业级 Webcrack AST 还原引擎，支持 Webpack 打包模块解压，集成微信小程序组件 AST 容错外科手术，自动切除私有组件元数据与悬空闭包，零告警高保真还原；
* **SourceMap 一键还原 `.vue` / `.ts` 原始工程**：自动探测并解包 SourceMap，将编译混淆的代码 1:1 还原为原始的 Vue 单文件组件与 TypeScript 源码；
* **全域 API 路由与密码学安全审计**：离线静态审计已提取的 JS 代码，深度提取后端业务域名 (Base URLs)、微信原生网络库 (`wx.request`, `@haici/request-core`)、国密算法 (`miniprogram-sm-crypto`, `@haici/gmsm4`, `TripleDES`)、非对称加密 (RSA/`jsbn`)、防篡改签名机制与全量业务 API 路由清单。

---

<a id="cli"></a><a id="命令行指南"></a><a id="命令行操作指南"></a>
## 💻 命令行操作指南

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

<a id="workflows"></a><a id="实战工作流"></a><a id="实战场景"></a>
## 🎯 四大经典实战工作流

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

<div align="center">

| 微信公众号推文右下角常驻绿色 vConsole 按钮 | 点击绿色按钮即刻展开移动端完整控制台 |
| :---: | :---: |
| <img src="docs/images/wechat_article_vconsole_btn.png" width="460" alt="公众号推文右下角浮动绿色 vConsole 按钮" /> | <img src="docs/images/wechat_article_vconsole_panel.png" width="460" alt="推文点击展开移动端完整 vConsole 控制台" /> |

</div>

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

### 场景 4：批量 AST 解混淆与全域静态逆向代码审计
*适用场景：面对混淆压缩的 JS 代码或小程序单体包，恢复其模块结构并提取后端接口清单与加密算法。*

```bash
# 1. 批量解混淆某个总目录下的所有子版本/子小程序工程
wx-h5 deobfuscate "./output/wx1363195c4fb75cfc" --all

# 2. 执行静态扫描并导出高质感 Markdown 审计报告
wx-h5 scan "./output/wx1363195c4fb75cfc/344_deobfuscated" --export audit_report.md
```

**扫描报告涵盖**：
* **后端业务域名 (Base URLs)**：提取硬编码的业务 API 接口域名；
* **网络请求框架**：识别 `wx.request`, `uni.request`, `@haici/request-core`, `axios` 等；
* **密码学与加密特征**：识别国密 SM2/SM3/SM4、TripleDES、AES、RSA/jsbn、HMAC-SHA256、JWT/jtoken、时间戳防重放签名；
* **凭据与敏感字段**：识别微信 AppID、插件依赖 ID、业务 Token 与请求头；
* **业务 API 清单**：提纯去重全量 RESTful 与 RPC 路由接口。


---

<a id="faq"></a><a id="常见问题"></a>
## ❓ 常见问题排障 (FAQ)

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

<details>
<summary><strong>Q4 [代理失效排障]: 启动透明代理后，微信内置浏览器无法联网或提示“代理服务器拒绝连接”？</strong></summary>

> **解答**：此现象 100% 由本地端口抢占、Windows 系统代理覆写或根证书信任链路受阻所致，请按以下三步快速排查：
> 1. **排查端口冲突**：默认代理端口 `8899` 可能已被其他工具（如 Clash、v2rayN、Fiddler、Charles）抢占。在终端执行 `netstat -ano | findstr 8899`，若发现已被其他 PID 监听，使用 `wx-h5 proxy --port 8999` 指定闲置端口运行；
> 2. **微信独立网络沙箱检查**：微信 4.x 将网络通信独立收拢至 `WeChatUtility.exe` / `WeChatAppEx.exe`，某些全局代理客户端会覆写系统 PAC 脚本导致流量旁路绕过。进入 Windows **“设置 -> 网络和 Internet -> 代理”**，确认手动代理服务器地址正确指向 `127.0.0.1:8899`，并关闭第三方 VPN 的虚拟网卡 TUN 模式；
> 3. **HTTPS 根证书受信任校验**：若微信内置浏览器报 `NET::ERR_CERT_AUTHORITY_INVALID`，说明微信沙箱拦截了自签名 HTTPS 握手。请将项目生成或 mitmproxy 的根证书（`~/.mitmproxy/mitmproxy-ca-cert.cer`）双击安装至 Windows 的 **“受信任的根证书颁发机构”** 物理存储区。
</details>

<details>
<summary><strong>Q5 [内核跨版本脱钩原理]: 微信大版本升级（如 4.0/4.1 及 RadiumWMPF 内核变动）后，工具如何做到免适配稳定脱钩？</strong></summary>

> **解答**：传统方案依赖硬编码静态内存偏移或特定启动参数（如旧版已失效的 `--xweb-enable-inspect=1`），微信小版本升级即全面失效。本项目采用 **“三层自适应脱钩与运行时签名扫描”** 架构：
> 1. **物理层放弃静态偏移**：`wechat_h5_devtools/core/injector.py` 运行时对 `RadiumWMPF` / `WeChatAppEx.exe` 的 Chromium 虚表（VTable）、`DevToolsActivePort` 判断分支及 Blink 初始化逻辑进行动态特征码（Signature Mask）扫描，不依赖固定内存硬地址；
> 2. **三级容灾多路挂载**：
>    - **L1 动态进程拦截**：Frida 挂载宿主 `CreateProcessW` API，在底层派发渲染沙箱子进程瞬间无缝向命令行注入 `--remote-debugging-port` 与 `--headless=new` 调试开关；
>    - **L2 协议管道热注入**：针对已在运行的微信进程，Hook `WeixinJSBridge` 消息派发泵，在网页 DOM 加载初期毫秒级调用 `document.createElement('script')` 追加官方 `vConsole` 节点；
>    - **L3 透明网络层兜底**：无视任何客户端二进制结构，在代理响应中对 HTML/JS 文件执行流式 AST 注入，三层中任意一层生效即可确保 100% 调试就绪；
> 3. **内核特征表增量进化**：项目内置 `addresses.<kernel_version>.json` 地址映射池（如已内置 25560 内核特征），新内核发布时仅需追加特征定义，无需重编译二进制。
</details>

<details>
<summary><strong>Q6 [微信强缓存击穿]: 使用 Local Overrides 重定向后，刷新页面仍加载线上旧代码？</strong></summary>

> **解答**：微信内置浏览器出于性能考量，对公众号与小程序 H5 启用了极度激进的 **Chromium 磁盘强缓存 (Disk Cache)** 与 HTTP 304 协商缓存，普通 F5 或点击刷新无法穿透缓存。请按以下方案实施彻底击穿：
> 1. **方案 A（工具代理物理剥离缓存头）**：`wx-h5 sandbox` 与 `wx-h5 proxy` 内置了强缓存粉碎中间件，自动拦截上游响应并强制重写头信息：
>    - 注入 `Cache-Control: no-cache, no-store, must-revalidate, max-age=0`
>    - 注入 `Pragma: no-cache` 与 `Expires: 0`
>    - 物理剥除 `ETag` 与 `If-Modified-Since` 标头，强制微信内核发起全量 200 请求；
> 2. **方案 B（清除本地磁盘缓存文件）**：微信将渲染缓存保存在 `%APPDATA%\Tencent\WeChat\radium\web\cache` 或 `xwechat_files` 下。在注入成功的 vConsole 中点击 **“Storage” -> “Clear Cookies & Cache”**，或关闭微信后直接删除该目录；
> 3. **方案 C（URL 动态时间戳破坏）**：在访问的目标 URL 末尾追加防缓存随机参数（如 `?_t=1726315890` 或 `&dev_bust=true`），迫使内核绕过 URL 缓存索引直接抓取重定向后的本地源码。
</details>

<details>
<summary><strong>Q7 [多进程管线识别]: 任务管理器中存在数十个 WeChat 进程，工具如何精准锁定目标渲染进程？</strong></summary>

> **解答**：微信 4.x 深度对齐了现代 Chromium 多进程沙箱模型，各进程分工高度隔离：
> 1. **微信多进程角色全景**：
>    - `WeChat.exe`：主界面 UI 与长连接通讯中枢（Broker 进程，不负责渲染 Web）；
>    - `WeChatAppEx.exe` / `WeixinExt.exe`：RadiumWMPF 网页与小程序渲染沙箱（**工具的核心 Hook 目标**）；
>    - `WeChatUtility.exe`：负责网络下载、崩溃转储与音视频编解码辅助管线；
>    - `WeChatPlayer.exe`：多媒体播放器沙箱；
> 2. **自适应管线识别器**：`wx-h5 hook` 启动后自动枚举当前用户会话的所有子进程，通过 Windows PEB (Process Environment Block) 探测命令行参数：
>    - 命中 `--type=renderer` 与 `--enable-blink-features` 标识符；
>    - 校验进程模块列表中是否已加载 `radium.dll` / `wmpf.dll`；
>    毫秒级过滤掉主进程与 Utility 进程，精准锁定承载目标 H5 的活跃渲染 PID；
> 3. **多标签并发手动锁定**：如果同时打开了多个公众号文章与网页窗口，导致存在多个渲染进程，可运行 `wx-h5 inspect --list` 打印所有活跃渲染页面标题与 PID，再通过 `wx-h5 hook --pid <目标PID>` 实施定向精准注入。
</details>

<details>
<summary><strong>Q8 [大内存解混淆]: 解混淆大型项目（>5MB 单体包）时，Node.js 报错内存溢出 (OOM) 崩溃？</strong></summary>

> **解答**：大型商用小程序或单页应用（SPA）往往将数百个模块打入单体 JS 文件。Babel AST 语法树在内存中展开后，节点对象体积将膨胀 **20 ~ 40 倍**，触顶 Node.js 默认的 1.4GB 堆上限。请使用以下经过工业级验证的扩容与切片方案：
> 1. **V8 堆内存物理扩容**：在执行解混淆前，通过环境变量分配 8GB ~ 16GB 专用虚拟堆内存：
>    ```bash
>    # Windows PowerShell
>    $env:NODE_OPTIONS="--max-old-space-size=8192"
>    wx-h5 deobfuscate "./output/wx1363195c4fb75cfc/344"
>    
>    # CMD 批处理
>    set NODE_OPTIONS=--max-old-space-size=8192
>    wx-h5 deobfuscate "./output/wx1363195c4fb75cfc/344"
>    ```
> 2. **启用分块增量反混淆 (`--chunked`)**：工具内置了模块切片解包引擎。带上 `--chunked` 参数后，工具先利用正则切分顶层 Webpack 模块字典，对单个模块原子化执行 AST 常量折叠与死代码消除后再汇总，内存占用峰值从 4GB 直降至 400MB；
> 3. **忽略巨型无害第三方库**：配合 `--exclude-libs` 参数自动跳过 `vue`, `react-dom`, `echarts`, `crypto-js` 等知名开源库，仅针对业务自定义逻辑（如 `app-service.js`）执行解混淆，大幅提升运算效率与成功率。
</details>

<details>
<summary><strong>Q9 [CDN 防盗链与跨域绕过]: 脱机沙箱或本地重定向时，资源报 403 Forbidden 防盗链或 CORS 跨域拦截？</strong></summary>

> **解答**：微信 CDN 与第三方业务服务器针对外发请求部署了严密的安全校验策略，工具已在网关层完成自动化伪装重写：
> 1. **防盗链校验原理**：微信 CDN（如 `res.wx.qq.com`、`*.qpic.cn`、腾讯云 COS）会严格校验 HTTP 请求头中的 `Referer` 必须包含腾讯域名白名单，且要求 `User-Agent` 必须含有 `MicroMessenger`、`NetType` 与 `OpenID/Ticket` 凭据；
> 2. **自动注入合法仿生标头**：`wx-h5 sandbox` 与 `wx-h5 proxy` 内置双向反向代理中间件，向远端发包时自动重写并伪装头部：
>    - 自动追加 `Referer: https://servicewechat.com/<appid>/page-frame.html`
>    - 自动对齐微信官方 Windows 客户端完整 UA（包含真实 WeChat 4.x 微版本号与网络类型）；
> 3. **跨域与 CSP 安全策略粉碎**：在响应流回传给浏览器前，工具自动剥除上游服务器的 `Content-Security-Policy`、`X-Frame-Options` 限制，并无条件注入响应头：
>    ```http
>    Access-Control-Allow-Origin: *
>    Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
>    Access-Control-Allow-Headers: *
>    ```
>    彻底消除外部脱机浏览器控制台中的红色 CORS 告警。
</details>

<details>
<summary><strong>Q10 [系统提权与权限隔离]: 执行 Hook 注入时提示“拒绝访问 (Access is denied / os error 5)”？</strong></summary>

> **解答**：此问题由 Windows **完整性级别 (Integrity Level / UAC)** 隔离机制引发：
> 1. **权限隔离根因**：如果微信客户端是以“以管理员身份运行”（高完整性级别 High Integrity）拉起的，运行在普通用户权限（中完整性级别 Medium Integrity）的终端和 Python 调试器将无法调用底层 Windows API（如 `OpenProcess` 获取 `PROCESS_ALL_ACCESS` 句柄），直接抛出 `Access is denied`；
> 2. **标准提权操作**：
>    - 启动终端（PowerShell 或 CMD）时，右键单击图标并选择 **“以管理员身份运行”**，然后再执行 `wx-h5 hook`；
>    - 本项目的独立发布版可执行程序（`.exe`）已强制内嵌 Windows 原生 `requireAdministrator` 清单，双击运行将自动弹出系统 UAC 提权提示，彻底免除手动配置；
> 3. **反向权限对齐原则**：若微信是以普通权限登录启动的，调试工具推荐同样使用普通权限运行，避免因调试进程生成的日志文件、本地缓存文件归属于 Administrator 用户，导致微信进程因权限不足无法读取。
</details>

---

<a id="sponsor"></a><a id="赞助与支持"></a><a id="赞助支持"></a>
## ☕ 赞助与支持 (Sponsor)

开源不易，长效维护更需投入大量精力。

本项目由作者基于业余时间深度逆向研发，持续追踪跟进微信客户端（如最新的 `4.1.13.12`）与 **RadiumWMPF 内核**底层渲染架构的变动，并持续维护适配各版本内核。

如果您觉得 **`WeChat-H5-DevTools`** 在您的日常开发、线上应急调试、逆向分析或安全审计工作中切实帮助到了您、为您节省了宝贵的时间，**欢迎请作者喝一杯香浓的咖啡以表支持与鼓励！☕** 您的慷慨支持是本项目长期迭代、技术突破与生态完善的最大动力！

<div align="center">

| <img src="docs/images/alipay_donate.jpg" width="200" alt="支付宝" /> | <img src="docs/images/wechat_donate.jpg" width="200" alt="微信支付" /> |
| :---: | :---: |
| 支付宝 | 微信支付 |

</div>

> **💡 赞助权益**：
> 
> 1. 赞助者提出的特定微信版本 / RadiumWMPF 内核适配 Issue 与定制需求将享受**第一优先级优先响应与攻坚**；
> 2. 赞助名单将被永久收录至仓库主页的 `🌟 鸣谢赞助榜 (Backers & Sponsors)` 予以致谢；
> 3. 扫码赞助时欢迎在备注中留下您的 **【GitHub ID / 昵称 / 寄语】**，或通过微信 `Sleep_Plan` 告知。

---

<a id="community"></a><a id="交流群"></a><a id="官方交流群"></a>
## 💬 官方技术交流群 (Community)

欢迎加入 **WeChat-H5-DevTools 官方技术交流群**，与广大逆向安全研究人员、Web 前端工程师及内核适配者共同交流技术、反馈新版微信与 RadiumWMPF 内核 Issue、探讨高阶实战玩法！

<div align="center">

<img src="docs/images/wechat_group_qrcode.png" width="220" alt="WeChat-H5-DevTools 官方微信交流群二维码" />

<br>

> **💡 入群提示**：微信扫码即可直接加入官方交流群。若遇二维码过期，请直接添加作者微信 **`Sleep_Plan`**（备注：**DevTools 入群**），由作者拉入官方群聊。

</div>

---

<a id="author"></a><a id="作者与联系方式"></a>
## 👤 作者与联系方式

- **作者 / 核心开发者**：**xuange520**
- **官方微信 (推荐首选)**：`Sleep_Plan` (微信逆向交流 / 商务合作 / 疑难排障)
- **官方邮箱**：`2603066228@qq.com` / `xuangeylw@gmail.com`
- **GitHub 主页**：[@xuange520](https://github.com/xuange520)
- **项目开源仓库**：[WeChat-H5-DevTools](https://github.com/xuange520/WeChat-H5-DevTools)

---

<a id="disclaimer"></a><a id="免责声明"></a>
## ⚠️ 免责声明 (Disclaimer)

1. **合法合规与技术研究**：本项目（`WeChat-H5-DevTools`）仅用于网络安全研究、前端跨平台兼容性测试、Web 开发调试与技术学习交流，严禁将其用于任何侵犯他人合法权益、危害网络安全或违反相关法律法规的活动。
2. **风险自负原则**：使用者在基于本项目进行调试、抓包或接口调用时，须自行确保行为的合法合规性。任何因不当使用、恶意滥用或二次开发所引发的法律纠纷、系统故障、财产损失或账号风险，本项目作者及贡献者概不承担任何直接或连带法律责任。
3. **知识产权尊重**：本项目中涉及的第三方商标、技术协议及相关标识，其知识产权均归其合法所有者所有。若相关方认为本项目存在侵权疑虑，请通过 Issue 与作者联系，我们将依法核实并积极配合处理。

---

<a id="license"></a><a id="开源许可证"></a>
## 📄 开源许可证

本项目基于 [MIT License](./LICENSE) 协议开源。
