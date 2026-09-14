# WeChat-H5-DevTools 开发者贡献指南与全链路排错溯源规范 (Contributing & Troubleshooting)

感谢您关注并参与 **WeChat-H5-DevTools** 项目的开源建设！

本项目致力于构建面向微信 4.x/RadiumWMPF 新内核的工业级 Webview 调试与安全分析工具箱。为了让所有外部开发者、逆向安全研究人员与前端工程师能够**低门槛、无缝、高效地参与本项目维护与新内核适配**，特制定本规范。

---

## 目录索引

- [一、本地研发环境极速搭建](#一本地研发环境极速搭建)
- [二、系统架构全景与模块职责拓扑](#二系统架构全景与模块职责拓扑)
- [三、微信版本升级与 RadiumWMPF 内核适配 SOP (核心秘籍)](#三微信版本升级与-radiumwmpf-内核适配-sop-核心秘籍)
- [四、五大核心故障排错溯源定位诊断矩阵](#四五大核心故障排错溯源定位诊断矩阵)
- [五、代码风格、规范与 PR 提交门禁](#五代码风格规范与-pr-提交门禁)

---

## 一、本地研发环境极速搭建

### 1. 基础环境依赖基线
- **Python**：3.9+（推荐 3.10 ~ 3.12 64-bit）
- **Node.js**：18+ LTS（用于驱动 AST 语法树反混淆与 Webpack 分包还原引擎）
- **C/C++ 运行时**：Windows 10/11 需具备 Microsoft Visual C++ 2015-2022 Redistributable (x64)
- **微信客户端**：测试需在本地安装 Windows 微信 3.9.x、4.0.x 或 4.1.x（主推当前官方最新版 4.1.13.12）

### 2. 本地仓库克隆与开发依赖安装
在终端（PowerShell 或 CMD）中执行以下命令：

```bash
# 1. 克隆代码仓库
git clone https://github.com/xuange520/WeChat-H5-DevTools.git
cd WeChat-H5-DevTools

# 2. 创建并激活 Python 虚拟环境 (推荐)
python -m venv venv
# Windows PowerShell
.\venv\Scripts\Activate.ps1
# Windows CMD
.\venv\Scripts\activate.bat

# 3. 安装项目运行依赖
pip install -r requirements.txt

# 4. 以可编辑开发模式注册 CLI 入口 (重要：任何源码修改立即生效)
pip install -e .

# 5. 安装 GUI 扩展依赖 (若需调试桌面客户端)
pip install pywebview
```

### 3. 环境就绪诊断验证
安装完成后，在终端运行内置体检诊断命令：
```bash
wx-h5 doctor
```
**期望输出**：
- Python 解释器版本 [PASS]
- Frida 动态插桩库版本 [PASS]
- Node.js 运行时及全局路径 [PASS]
- 微信主程序路径与 RadiumWMPF 内核版本探测 [PASS]

---

## 二、系统架构全景与模块职责拓扑

项目源码位于 `wechat_h5_devtools/` 目录下，遵循高内聚、低耦合的模块化设计：

```text
wechat_h5_devtools/
├── cli.py                     # CLI 命令行主调度中枢 (Click 框架)
├── injector/                  # 内存注入与透明代理中枢
│   ├── process_hooker.py      # Frida 动态代码插桩与 CreateProcessW 拦截引擎
│   ├── proxy_injector.py      # 本地 HTTP/HTTPS 透明代理网关 (mitmproxy 架构)
│   ├── wechat_finder.py       # 微信多版本路径与 RadiumWMPF 内核探测器
│   ├── assets/                # 内置静态资源 (vconsole.min.js 等)
│   └── scripts/hook_inapp.js  # 运行在微信进程内部的底层 Frida JavaScript 探针
├── sandbox/                   # 外部脱机浏览器高保真沙箱
│   ├── browser_launcher.py    # Edge / Chrome 独立沙箱调起器
│   ├── user_agents.py         # 微信各平台 User-Agent 矩阵生成器
│   └── polyfills/             # document_start 毫秒级注入的 WeixinJSBridge Mock
├── extractor/                 # AST 逆向反混淆与静态代码审计引擎
│   ├── deobfuscator.py        # AST 批量解混淆调度器
│   ├── webcrack_runner.js     # Node.js 运行时执行环境
│   ├── project_dumper.py      # Webpack 异步分包递归递归提取器
│   ├── sourcemap_rebuilder.py # SourceMap 还原原始 Vue/TS 源码工程
│   └── api_analyzer.py        # 全域 API 路由、凭据与国密算法静态提取器
├── gui/                       # 桌面 GUI 交互组件 (Modern Fluent WebGUI / pywebview)
├── utils/                     # 通用工具集 (日志落盘、路径解析)
└── resources/config/          # 各代微信内核特征码与虚表地址池 (addresses.*.json)
```

---

## 三、微信版本升级与 RadiumWMPF 内核适配 SOP (核心秘籍)

当微信客户端或 **RadiumWMPF 内核**静默推送升级（例如从 25560 升级为 26000），传统硬编码方案会直接崩溃。其他开发者参与内核适配时，请严格按照以下 6 步标准 SOP 执行：

### 第一步：物理定位本机生效的内核版本
1. 按快捷键 Win + R 输入并回车：
   ```text
   %AppData%\Tencent\xwechat\XPlugin\Plugins\RadiumWMPF
   ```
2. 查看最新生成的纯数字文件夹（如 25560、26010），该数字即为当前生效的 KERNEL_VERSION；
3. 检查其内部的核心渲染动态库：
   `radium.dll` 或 `wmpf.dll`，以及主程序 `WeChatAppEx.exe`。

### 第二步：分析新内核的启动命令行特征
微信 4.x 采用多进程 Chromium 沙箱。在新版微信中打开任意公众号网页，在 PowerShell 中执行命令抓取其活跃子进程参数：
```powershell
Get-CimInstance Win32_Process -Filter "Name LIKE 'We%'" | Select-Object ProcessId, CommandLine
```
重点核对：
- 渲染子进程名是否依旧为 `WeixinExt.exe` 或 `Weixin.exe`；
- 命令行参数中是否包含 `--type=renderer` 与 `--enable-blink-features`；
- 若子进程名称发生变更，需同步更新 `wechat_h5_devtools/injector/wechat_finder.py` 与 `scripts/hook_inapp.js` 中的进程过滤正则。

### 第三步：静态/动态逆向提取 DevTools 校验分支特征
1. 将 `wmpf.dll` 或 `WeChatAppEx.exe` 载入反编译工具（IDA Pro / Ghidra）；
2. 搜索关键字符串（Strings）：
   - `--remote-debugging-port`
   - `DevToolsActivePort`
   - `--xweb-enable-inspect`
   - `--enable-media-stream`
3. 交叉引用（Xref）跳转至指令函数块，观察开启开发者工具的判定分支（通常为读取配置文件、检查特定命令行 Flag 或全局单例布尔值）。

### 第四步：提取动态特征码签名 (Signature Mask)
为了确保新版本小更新后依然免修改兼容，**严禁硬编码绝对 VA 内存地址**，必须提取机器码特征（允许使用通配符 `?`）：
```text
48 8B 05 ?? ?? ?? ?? 48 85 C0 74 ?? 48 8B 40 ?? 48 85 C0 74 ?? FF 50 ??
```

### 第五步：建立新版本特征映射池配置
在 `resources/config/` 目录下新建 `addresses.<新内核版本号>.json`（例如 `addresses.26010.json`）：
```json
{
  "kernel_version": "26010",
  "arch": "x64",
  "target_module": "radium.dll",
  "signatures": {
    "devtools_port_check": "48 8B ?? ?? ?? 85 C0 74 ?? 48 8B ?? ??",
    "vtable_cdp_dispatch": "48 8D 05 ?? ?? ?? ?? 48 89 01 48 8B 4B"
  },
  "cli_flags": [
    "--remote-debugging-port=8899",
    "--enable-blink-features=DevTools",
    "--no-sandbox"
  ]
}
```

### 第六步：执行断言验证与冒烟测试
执行注入测试命令：
```bash
wx-h5 hook
```
观察终端输出是否成功打印：`[PASS] RadiumWMPF <版本号> 特征码动态匹配成功，调试端口已接管`。

---

## 四、五大核心故障排错溯源定位诊断矩阵

| 故障场景与现象 | 根因分类 | 核心排障文件与代码位置 | 自愈排障与定位步骤 |
| :--- | :--- | :--- | :--- |
| **1. 启动报拒绝访问 (Access is denied / os error 5)** | Windows UAC 完整性级别隔离 | `wechat_h5_devtools/injector/process_hooker.py` | 微信以管理员权限启动时，普通终端无权附加 OpenProcess。<br>1. 右键终端以**“管理员身份运行”**；<br>2. 编译 EXE 时强制注入 `requireAdministrator` 清单。 |
| **2. 启动代理后微信内置网页无法联网** | 端口冲突或 HTTPS 根证书未受信 | `wechat_h5_devtools/injector/proxy_injector.py` | 1. 运行 `netstat -ano \| findstr 8899`，若冲突改用 `wx-h5 proxy --port 8999`；<br>2. 双击安装 `~/.mitmproxy/mitmproxy-ca-cert.cer` 证书至**受信任的根证书颁发机构**。 |
| **3. 微信大版本升级后 Hook 无反应** | 内核子进程名变更或虚表偏移失效 | `wechat_h5_devtools/injector/scripts/hook_inapp.js` | 运行 `wx-h5 inspect --list` 打印当前所有渲染 PID，比对 `hook_inapp.js` 中的进程监听名单；执行第三章 SOP 提取新特征码。 |
| **4. 本地替换后微信仍显示线上旧代码** | 微信 Chromium 磁盘强缓存与 304 协商 | `wechat_h5_devtools/sandbox/browser_launcher.py` | 1. 工具默认已重写响应头注入 `no-cache, no-store`；<br>2. 在 vConsole 的 Storage 面板点击 **Clear Cache**；<br>3. 在访问 URL 后添加随机参数 `?_t=时间戳` 击穿缓存。 |
| **5. AST 解混淆巨型单体包 Node 报错 OOM** | V8 堆内存默认 1.4GB 上限溢出 | `wechat_h5_devtools/extractor/deobfuscator.py` | 1. 分配 8GB 虚拟堆：`$env:NODE_OPTIONS="--max-old-space-size=8192"`；<br>2. 开启分块增量反混淆：`wx-h5 deobfuscate <dir> --chunked`。 |

---

## 五、代码风格、规范与 PR 提交门禁

为了保证代码库的工业级防腐与技术合规，所有提交至本项目的 Pull Request (PR) 必须 100% 满足以下门禁：

### 1. 语法检查与静态编译门禁
提交前必须自检所有修改过的 Python 文件，确保零语法错误：
```bash
python -m py_compile wechat_h5_devtools/**/*.py
```

### 2. 100% 纯净日志与零 Emoji 铁律
- 日志时间戳格式统一为：`[%Y-%m-%d %H:%M:%S]` 或 `[%H:%M:%S]`；
- **严禁包含任何 Emoji 与装饰符号**；统一采用纯文本规范化标签：`[INFO]`, `[SUCCESS]`, `[ERROR]`, `[WARN]`, `[PASS]`, `[HOOK]`, `[PROXY]`, `[AST]`。

### 3. 敏感数据与凭据物理隔离
- **绝对严禁提交含有任何真实用户敏感信息的数据**：包括但不限于用户 OpenID、SessionKey、Auth Token、真实商户密钥、私有抓包 HAR 文件等；
- 测试用例中的凭据必须使用标准掩码（如 `wx4b9281**********************`）。

### 4. Git Commit 信息规范 (Conventional Commits)
Commit 规范示例：
- `feat(injector): add support for RadiumWMPF kernel 26010`
- `fix(proxy): resolve port conflict auto-fallback mechanism`
- `docs(faq): add troubleshooting for SSL certificate verification`
- `perf(extractor): optimize chunked AST deobfuscation memory peak`

### 5. 开源技术诚信与非商业合规
- 凡引入第三方开源代码、逆向 PoC 或借鉴思路，必须按照项目规则在 `README.md` 与关于面板中添加完整的 GitHub 原作者仓库链接；
- 本项目基于 **CC BY-NC-SA 4.0** 协议开源，任何 PR 均默认继承该协议，严禁夹带商业专有代码或为二手倒卖留后门。
