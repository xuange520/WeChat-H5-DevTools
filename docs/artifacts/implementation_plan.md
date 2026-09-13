# WeChat-H5-DevTools 全栈架构设计与实施计划

`WeChat-H5-DevTools` 是一套专为 **微信 4.x 内置浏览器、公众号 H5 页面及企微 Webview** 打造的现代化开发调试、环境模拟与全站源码逆向提取开源套件。

---

## 🎯 痛点与战术定位

| 传统痛点 | `WeChat-H5-DevTools` 解决范式 |
| :--- | :--- |
| **微信 4.x 屏蔽 F12 热键** | **免按键浮动控制台**：通过 Frida/内存注入，打开任意网页自动悬浮 `vConsole` / `Eruda` 移动端 DevTools |
| **外部浏览器调试提示“请在微信中打开”** | **高保真微信沙箱**：自动伪装全平台 WeChat UA + 深度 Mock `WeixinJSBridge` 与 JSSDK，原生弹出 Chrome F12 |
| **微信 OAuth2 授权无法在外部本地调试** | **本地 Mock 拦截网关**：自动拦截 `open.weixin.qq.com/oauth2` 并注入 Mock Code 与 OpenID |
| **Webpack 异步分包 JS 难以批量抓取** | **全站 AST 逆向提取器**：递归提取所有动态 Chunk JS/CSS + 自动恢复 SourceMap 原始源码目录 |
| **前端接口与敏感参数人工排查费时** | **API 资产与敏感字段探测器**：自动分析 JS 代码，一键导出全部后端 API 路由、加签逻辑与硬编码凭据 |

---

## 🏗️ 系统分层架构设计 (Architecture Blueprint)

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                   WeChat-H5-DevTools CLI / API (统一调度中枢)                          │
├────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                        │
│  ┌───────────────────────┐  ┌────────────────────────┐  ┌───────────────────────────┐  │
│  │   1. inapp_injector   │  │   2. stealth_sandbox   │  │    3. asset_extractor     │  │
│  │  (微信内置注入引擎)    │  │  (外部高保真沙箱引擎)  │  │   (全站源码逆向提取引擎)   │  │
│  ├───────────────────────┤  ├────────────────────────┤  ├───────────────────────────┤  │
│  │ • 进程自适应探测      │  │ • 全平台微信 UA 矩阵   │  │ • HTML / DOM 深度解析器   │  │
│  │ • Frida 17+ 兼容挂载  │  │ • WeixinJSBridge 完整  │  │ • Webpack 异步分包递归器   │  │
│  │ • 透明代理 vConsole   │  │   生命周期与事件 Mock  │  │ • SourceMap 源码目录还原  │  │
│  │   自动无感注头        │  │ • JSSDK 1.6.0 挡板系统 │  │   (一键还原 .vue/.ts 源码)│  │
│  │ • XWeb inspect 参数补全│ │ • Chrome/Edge 满血启动 │  │ • API 路由与密码学特征扫描│  │
│  └───────────────────────┘  └────────────────────────┘  └───────────────────────────┘  │
│                                                                                        │
│  ┌──────────────────────────────────────────────────────────────────────────────────┐  │
│  │                           4. common_core (核心通用层)                            │  │
│  │  • 终端彩色 Banner 与 Logger • 网络请求与代理会话 • 路径安全与编码保障 (Strict UTF-8)│  │
│  └──────────────────────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔬 深度技术实现细节与边界攻防

### 1. 内置注入引擎 (`inapp_injector`)
* **双重注入机制**：
  - **路径 A（进程参数级）**：Hook `CreateProcessW`，为 `WeChatAppEx.exe` 注入 `--xweb-enable-inspect=1` 与 `--remote-debugging-port`；
  - **路径 B（透明代理注头级，无敌兼容）**：内置轻量级本地代理转发网关，在微信加载任意 HTML 时，自动在 `<head>` 首行注入 `vConsole` / `Eruda` 脚本。即使微信未来版本彻底封杀任何参数，微信内置浏览器依然能 100% 弹出绿色浮动 DevTools！

### 2. 高保真沙箱与 JSSDK Mock (`stealth_sandbox`)
* **`WeixinJSBridge` 完整模拟**：
  - 模拟 `WeixinJSBridge.invoke`（支持 `getBrandWCPayRequest`、`openLocation`、`scanQRCode`、`chooseImage` 等 30+ 常见微信原生能力模拟响应）；
  - 模拟 `WeixinJSBridge.on` / `emit`（支持微信菜单点击、分享回调、右上角关闭拦截）；
* **JSSDK 1.6.0 穿透**：
  - 自动劫持 `wx.config`：无视后端签名算法与 AppID 校验，直接分发 `wx.ready()` 成功事件，彻底阻断 `wx.error` 拦截。

### 3. 全站源码逆向与资产还原引擎 (`asset_extractor`)
* **Webpack Chunk 深度递归**：
  - 不仅匹配静态 `<script>` 标签，还通过 AST/正则深度分析 `manifest.js` 和 `chunk-vendors.js` 中的 Chunk ID 映射表，并发递归拉取所有异步分包；
* **SourceMap 还原还原器 (`sourcemap_rebuilder`)**：
  - 自动探测是否存在 `[name].js.map`。若存在，直接解析 SourceMap JSON，**将编译混淆的代码 1:1 还原为原始的 Vue SFC 组件（`.vue`）、TypeScript（`.ts`）和 Less/SCSS 样式源文件**！
* **API 路由与密码学算法字典探测 (`api_analyzer`)**：
  - 自动抽取 Axios / Fetch 接口 URL 列表；
  - 自动识别前端加密特征（国密 SM2/SM3/SM4、AES、RSA、DES、MD5、HMAC-SHA256、Base64 等加签逻辑）。

---

## 📂 项目工程目录规划

落地物理根路径：`D:\源码\自写工具\WeChat-H5-DevTools\`

```text
D:\源码\自写工具\WeChat-H5-DevTools\
├── README.md                      <-- 顶级开源项目文档 (精美中英文徽章、动图演示、架构说明)
├── README_EN.md                   <-- 英文版本文档
├── LICENSE                        <-- MIT 开源协议
├── pyproject.toml                 <-- 现代化 Python 打包配置 (支持 uv / pip 一键安装)
├── requirements.txt               <-- 依赖清单 (frida, websockets, click, rich, httpx 等)
├── main.py                        <-- CLI 主入口快捷方式
└── wechat_h5_devtools/           <-- 核心源码包
    ├── __init__.py                <-- 版本信息与统一导出
    ├── cli.py                     <-- 基于 Click / Rich 的交互式命令行
    │
    ├── injector/                  <-- 模块 1: 微信客户端内置注入器
    │   ├── __init__.py
    │   ├── wechat_finder.py       <-- 智能自适应定位微信 3.x / 4.x 安装目录
    │   ├── process_hooker.py      <-- 基于 Frida 的进程生命周期管理与 Hook 引擎
    │   ├── proxy_injector.py      <-- 本地透明代理自动注入 vConsole 引擎
    │   └── scripts/               <-- 注入 JS 脚本库
    │       ├── hook_inapp.js      <-- 拦截 CreateProcessW / XWeb 参数注入
    │       └── vconsole_loader.js <-- 网页自动注入 vConsole 脚本
    │
    ├── sandbox/                   <-- 模块 2: 独立微信伪装与 JSSDK 沙箱
    │   ├── __init__.py
    │   ├── browser_launcher.py    <-- Chrome / Edge 自动化拉起与 DevTools 挂载
    │   ├── user_agents.py         <-- iOS / Android / Windows / Mac 微信 UA 矩阵
    │   └── polyfills/             <-- JSSDK 与 WeixinJSBridge 挡板脚本
    │       ├── weixin_bridge.js   <-- WeixinJSBridge API 完整 Mock
    │       └── jssdk_mock.js      <-- wx.config / wx.ready / 扫码 / 支付 Mock
    │
    ├── extractor/                 <-- 模块 3: 全站前端源码逆向提取与审计引擎
    │   ├── __init__.py
    │   ├── project_dumper.py      <-- 递归全站 Webpack 分包与静态资产下载器
    │   ├── sourcemap_rebuilder.py <-- SourceMap 逆向还原原始 src/ 目录
    │   └── api_analyzer.py        <-- 离线 JS 代码静态分析与 API/加密算法探测
    │
    └── utils/                     <-- 通用工具库
        ├── __init__.py
        ├── logger.py              <-- Rich 炫彩日志终端输出
        └── path_helper.py         <-- 防乱码路径与跨平台路径清洗
```

---

## 💻 CLI 命令行调用设计 (User Interface Experience)

```bash
# 1. 启动微信并自动注入内置 vConsole / DevTools 浮动面板
wx-h5 hook

# 2. 在独立 Chrome/Edge 中打开目标公众号链接（带满血 F12 + JSSDK 模拟）
wx-h5 open "https://mp.weixin.qq.com/s/..."

# 3. 递归反编译提取目标公众号 H5 的全站源码与 Webpack 分包
wx-h5 dump "https://mp.mhealth100.com/patient/..." -o ./my_project

# 4. 尝试探测并一键从 SourceMap 还原原始 Vue/TS 源码工程
wx-h5 restore ./my_project

# 5. 离线扫描已导出的项目代码，提取 API 路由与密码学加密特征
wx-h5 scan ./my_project
```

---

## 🔒 需您审查的安全点

> [!IMPORTANT]
> - 本工具定位为 **前端开发调试辅助工具、跨平台 Web 沙箱模拟器及离线代码质量审计工具**，代码与设计严格遵守防御性架构标准。
> - 所有生成的源码资产均保存于本地独立输出目录，不向任何第三方上报遥测数据。

---

## 🏁 验证与测试计划

1. **模块 1 验证**：在本地微信 4.1.0.30 运行 `wx-h5 hook`，验证进程拉起与参数注入；
2. **模块 2 验证**：执行 `wx-h5 open <url>`，验证 Edge / Chrome 自动弹起 F12 且无 `WeixinJSBridge` 报错；
3. **模块 3 验证**：执行 `wx-h5 dump <url>`，验证全站 HTML、Webpack Chunks 和 CSS 自动还原落盘；
4. **包管理验证**：测试 `pip install -e .` 或 `uv sync` 构建体验，确保开箱即用。
