<div align="center">

<img src="docs/images/logo.png" width="160" alt="WeChat-H5-DevTools Logo" />

# WeChat-H5-DevTools

**The ultimate debugging & reverse-engineering toolkit for WMPFDebugger In-App Browser & H5 Webpages with Frida hook, vConsole proxy, and API analyzer.**

[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License: CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC_BY--NC--SA_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc-sa/4.0/)
[![Frida 17+](https://img.shields.io/badge/Frida-17+-FF69B4?logo=frida&logoColor=white)](https://frida.re/)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS-blue.svg)](https://github.com/)

[中文文档](./README.md) · [Matrix](#matrix) · [Screenshots](#screenshots) · [Features](#features) · [Quickstart](#quickstart) · [GUI](#gui) · [FAQ](#faq) · [Attribution](#attribution) · [Sponsor](#sponsor) · [Community](#community) · [License](#license)

</div>

---

<a id="overview"></a>
## 📖 Overview

Following the WeChat 4.x desktop architecture updates, the native `F12` hotkey on the embedded browser window was completely removed. Additionally, testing WeChat H5 pages in standard external desktop browsers typically suffers from `"Please open this link in WeChat"`, missing `WeixinJSBridge` runtimes, and complex asynchronous Webpack chunk extraction.

**`WeChat-H5-DevTools`** delivers an all-in-one, production-grade toolkit combining **In-App vConsole Injection**, **Stealth WeChat Sandbox & JSSDK Polyfill**, **Local Overrides Hot-Reloading**, **Automated AST Deobfuscation & Webpack Extraction**, and **Deep Static Code & Cryptography Auditing**.

---

<a id="matrix"></a>
## 🖥️ WeChat & RadiumWMPF Kernel Compatibility Matrix

| WeChat Major Version | Tested Versions | RadiumWMPF Kernel Version | Core Render Process | Injection & Debug Mechanism | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **WeChat 4.1.x (Latest)**<br>*(Primary)* | **`4.1.13.12`**<br>`4.1.12.26`<br>`4.1.5.30` | **`25560`** / **`25510`** / `25497` / `25364` / `20089` | `WeixinExt.exe`<br>`Weixin.exe` (`--type=renderer`) | Frida dynamic hook on `CreateProcessW`<br>+ Transparent proxy auto-injects `vConsole` | `[PASS]` Full Support |
| **WeChat 4.0.x Series** | `4.0.2`<br>`4.0.1`<br>`4.0.0` | **`16389` / `16203` / `16133` / `14315`**<br>*(Blink Architecture)* | `Weixin.exe`<br>`WeChatAppEx.exe` | Adaptive process detection & multi-point CLI argument injection | `[PASS]` Full Support |
| **WeChat 3.9.x Classic** | `3.9.12`<br>`3.9.11`<br>`3.9.10` & older | **`11581` ~ `13909`**<br>*(Classic XWeb / Chromium 85~108)* | `WeChat.exe`<br>`WeChatAppEx.exe` | Native `--xweb-enable-inspect=1` channel | `[PASS]` Full Support |
| **Stealth Sandbox**<br>*(Standalone)* | Any OS<br>(Win / Mac / Linux) | **Latest Edge / Chrome**<br>*(Full Chromium 130+ V8 Engine)* | `msedge.exe`<br>`chrome.exe` | Sub-millisecond `document_start` injection with 30+ WeixinJSBridge mocks | `[PASS]` Native F12 |

> **💡 How to check your local RadiumWMPF kernel version?**
> Press `Win + R` and navigate to:
> `%AppData%\Tencent\xwechat\XPlugin\Plugins\RadiumWMPF`
> The numeric subfolder names (e.g. `25510`, `16389`) represent your active **RadiumWMPF kernel version**.

---

<a id="screenshots"></a>
## 📷 Live In-App WeChat Article Debugging Screenshots

Tested and verified on the latest WeChat desktop client (`4.1.13.12`) with `RadiumWMPF` kernel. No binary patching required — transparent floating vConsole injection across all official account articles and H5 pages:

<div align="center">

| WeChat Official Account Article with Floating vConsole | Expanding Mobile DevTools Panel on Live Article |
| :---: | :---: |
| <img src="docs/images/wechat_article_vconsole_btn.png" width="460" alt="WeChat Article with Floating vConsole" /> | <img src="docs/images/wechat_article_vconsole_panel.png" width="460" alt="vConsole Panel Expanded on WeChat Article" /> |
| *Figure 1: Visiting any article in WeChat automatically displays the floating vConsole button* | *Figure 2: Clicking the button unfolds the full Console, Network, Storage, and Elements tree* |

</div>

---

<a id="features"></a>
## ✨ Key Features

* **WeChat 4.x In-App DevTools Unlocker**: Powered by Frida 17+ hooks with multi-version auto-detection (fully verified on `4.1.13.12`);
* **Zero-Hotkey Transparent vConsole Proxy**: Built-in HTTP proxy gateway that injects `vConsole` / `Eruda` into all visited H5 web pages automatically;
* **Local Overrides Hot-Reloading**: Instantly replace remote online JS/CSS scripts with local files in real time without rebuilding or redeploying;
* **Stealth Browser Sandbox & JSSDK Mock**: Multi-platform WeChat UA presets paired with 30+ `WeixinJSBridge` native mocks (Payment, Scan, Location, Menu events) with native Chrome/Edge DevTools;
* **Full-Site Webpack Chunk Dumper**: Recursively unpacks all HTML, Webpack async JS bundles, CSS, and static assets preserving original path structures;
* **Automated AST Deobfuscator & Unpacker**: Integrated AST sanitization engine that repairs dangling closures and WeChat plugin wrappers, unpacking single-bundle files without warnings;
* **SourceMap Rebuilder**: Unpacks `.map` files into original human-readable `.vue` SFCs, TypeScript, and SCSS/Less code;
* **API Endpoint & Crypto Analyzer**: Scans dumped JS for RESTful API routes, hardcoded Base URLs, AppIDs, and cryptographic algorithms (SM2/SM3/SM4, AES, RSA, HMAC).

---

<a id="quickstart"></a>
## 🚀 Quickstart

```bash
# Clone the repository
git clone https://github.com/xuange520/WeChat-H5-DevTools.git
cd WeChat-H5-DevTools

# Install requirements
pip install -r requirements.txt

# Install as global CLI tool
pip install -e .
```

### 1-Minute Beginner Guide

* **Inspect live WeChat pages with floating console**:
  ```bash
  wx-h5 proxy
  ```
  Open any official account page in WeChat, and a green `vConsole` button will appear on the bottom-right corner!

* **Debug WeChat H5 inside desktop Chrome/Edge with native F12**:
  ```bash
  wx-h5 open "https://your-wechat-h5-link.com"
  ```

* **Deobfuscate packed JS modules**:
  ```bash
  wx-h5 deobfuscate "./output/site" --all
  ```

* **Audit API routes and cryptography**:
  ```bash
  wx-h5 scan "./output/site_deobfuscated" -e report.md
  ```


* **Prefer a graphical desktop client rather than CLI?**:
  ```bash
  python examples/supabase_gui/app.py
  ```
  Launches the modern Fluent desktop interface with real-time log streaming, disk persistence, one-click copy, and visual proxy/AST deobfuscation!

---

<a id="gui"></a>
## 🖥️ Graphical User Interface (GUI) Guide

In addition to the powerful command-line interface (CLI), this project offers two desktop graphical user interfaces to fit various workflows:

### 1. Modern Fluent WebGUI (Recommended / Hardware-Accelerated via WebView2)
Adheres to Microsoft Fluent Design and Supabase dark-mode interface standards:
- **Physical Disk Log Persistence**: Automatically writes streaming console logs to `records/logs/console_stream.log`;
- **Interactive Operations**: Built-in physical buttons for **`[Copy All Logs]`**, **`[Open Local Log]`**, and **`[Locate Log Directory]`**;
- **Visual Reverse & Debugging**: One-click actions for transparent proxy injection, AST deobfuscation, and Webpack chunk extraction;
- **Integrated Attribution & Disclaimers**: In-app views displaying complete open-source GitHub repositories and anti-resale clauses.

**Launch command**:
```bash
python examples/supabase_gui/app.py
```
> *System requirements: Windows 10/11 (Windows 11 includes WebView2 Runtime natively; Windows 10 requires Microsoft Edge WebView2 Evergreen Runtime).*

### 2. PyQt6 Fluent Desktop Edition
Traditional native Qt6 desktop client with automatic dark/light theme switching.

**Launch command**:
```bash
# Method A: Via CLI subcommand
wx-h5 gui

# Method B: Direct Python module execution
python -m wechat_h5_devtools.gui.main_window
```
> *Dependency installation: Run `pip install PyQt6 PyQt-Fluent-Widgets pywebview` first.*

---

<a id="faq"></a>
## ❓ Frequently Asked Questions (FAQ)

To maintain a clean and concise main overview, all 11 detailed troubleshooting procedures (including proxy port conflict resolution, kernel decoupling, aggressive disk cache busting, multi-process PID filtering, Node 8GB heap expansion, and UAC elevation) are compiled into the dedicated guide:

👉 **[Read the Complete Troubleshooting Guide: FAQ_EN.md](./docs/FAQ_EN.md)**

### Top 3 Quick Answers:

<details>
<summary><strong>Q1: 'wx-h5' is not recognized as a command?</strong></summary>

> **Solution**: Run `pip install -r requirements.txt` and `pip install -e .` in the project root, or execute via `python main.py <command>`. See [FAQ_EN.md: Q1](./docs/FAQ_EN.md#q1-wx-h5-is-not-recognized-as-an-internal-or-external-command).
</details>

<details>
<summary><strong>Q2: 'wx-h5 hook' reports existing WeChat process already running?</strong></summary>

> **Solution**: WeChat cannot be attached with remote debugging switches while running. Completely exit WeChat from the tray or run `taskkill /F /IM WeChat.exe /IM Weixin.exe /IM WeChatAppEx.exe /T` and retry. See [FAQ_EN.md: Q2](./docs/FAQ_EN.md#q2-wx-h5-hook-reports-existing-wechat-process-already-running).
</details>

<details>
<summary><strong>Q3: Offline browser displays 'Please open this link in WeChat'?</strong></summary>

> **Solution**: Launch via `wx-h5 open "<URL>" --browser edge --ua ios`. At `document_start` (0ms), mock implementations for 30+ WeixinJSBridge APIs are injected before page execution. See [FAQ_EN.md: Q3](./docs/FAQ_EN.md#q3-offline-browser-shows-please-open-in-wechat-or-custom-jssdk-apis-fail).
</details>

> 📘 **For comprehensive solutions (proxy conflicts, 8GB OOM, 403 Forbidden CORS, UAC elevation, GUI errors)**, refer to [docs/FAQ_EN.md](./docs/FAQ_EN.md).

---

<a id="sponsor"></a>
## ☕ Sponsor & Support

This project is actively maintained in the author's spare time, tracking the latest internal architecture updates of WeChat desktop clients (such as `4.1.13.12`) and **RadiumWMPF kernels**.

If **WeChat-H5-DevTools** helped your development, debugging, or security analysis workflow, feel free to sponsor a cup of coffee to support continued maintenance!

<div align="center">

| <img src="docs/images/alipay_donate.jpg" width="200" alt="Alipay" /> | <img src="docs/images/wechat_donate.jpg" width="200" alt="WeChat Pay" /> |
| :---: | :---: |
| Alipay | WeChat Pay |

</div>

---

<a id="community"></a>
## 💬 Community & Discussion

Join the **WeChat-H5-DevTools Community** to exchange reverse-engineering insights, web debugging techniques, and report new WeChat & RadiumWMPF kernel updates!

<div align="center">

<img src="docs/images/wechat_group_qrcode.png" width="220" alt="WeChat-H5-DevTools Community QR Code" />

<br>

> **💡 Note**: Scan via WeChat to join. If the QR code is expired, add WeChat ID **`Sleep_Plan`** with the note *"DevTools"* to be invited.

</div>

---

<a id="author"></a>
## 👤 Author & Contact

- **Author / Core Maintainer**: **xuange520**
- **WeChat (Recommended)**: `Sleep_Plan`
- **Email**: `2603066228@qq.com` / `xuangeylw@gmail.com`
- **GitHub Profile**: [@xuange520](https://github.com/xuange520)

---

<a id="attribution"></a>
## 🙏 Attribution & Acknowledgements

This project adheres strictly to academic and technical integrity in the open-source community. During development and security research, we have built upon, referenced, and drawn inspiration from the following open-source projects:

### 1. Core Runtime Dependencies & Frameworks

| Project | Repository (GitHub) | License | Role in WeChat-H5-DevTools |
| :--- | :--- | :--- | :--- |
| **Frida** | [frida/frida](https://github.com/frida/frida) | wxWindows | Dynamic code instrumentation toolkit for Windows WeChat `CreateProcessW` hooking and Chromium sandbox attachment |
| **vConsole** | [Tencent/vConsole](https://github.com/Tencent/vConsole) | MIT | Tencent official mobile web developer panel for floating debug console injection without hotkeys |
| **Eruda** | [liriliri/eruda](https://github.com/liriliri/eruda) | MIT | In-browser devtools for mobile browsers providing Elements DOM tree inspection, Network sniffing, and Storage editing |
| **AST Deobfuscator Engine** | [j4k0xb/webcrack](https://github.com/j4k0xb/webcrack) | MIT | Deobfuscate, unminify, and unpack bundled JavaScript AST trees and Webpack chunks |
| **Mitmproxy** | [mitmproxy/mitmproxy](https://github.com/mitmproxy/mitmproxy) | MIT | Interactive TLS-capable intercepting proxy for live header and body streaming rewrites |
| **Babel** | [babel/babel](https://github.com/babel/babel) | MIT | Foundational compiler and AST parsing/traversal engine for JavaScript syntax reconstruction |
| **PyWebView** | [r0x0r/pywebview](https://github.com/r0x0r/pywebview) | BSD-3-Clause | Lightweight cross-platform desktop GUI container leveraging native Windows 10/11 WebView2 hardware acceleration |
| **Click** | [pallets/click](https://github.com/pallets/click) | BSD-3-Clause | Python composable command-line interface toolkit |
| **Rich** | [Textualize/rich](https://github.com/Textualize/rich) | MIT | Terminal formatting, syntax highlighting, and progress tables |
| **PyQt-Fluent-Widgets** | [zhiyiYo/PyQt-Fluent-Widgets](https://github.com/zhiyiYo/PyQt-Fluent-Widgets) | GPLv3 | Fluent Design styling inspiration for modern desktop interfaces |

### 2. WeChat Research & Reference Ecosystem

| Reference Project | Author / Org | Repository (GitHub) | Research Insights & Inspiration |
| :--- | :--- | :--- | :--- |
| **WeChatOpenDevTools-Python** | JaveleyQAQ | [JaveleyQAQ/WeChatOpenDevTools-Python](https://github.com/JaveleyQAQ/WeChatOpenDevTools-Python) | Pioneering memory offset scanning and DevTools unlocking mechanisms in WeChat |
| **First** | notstarr | [notstarr/First](https://github.com/notstarr/First) | Comprehensive WeChat miniapp debugging framework combining Frida + CDP protocol architecture |
| **e0e1-wx** | eeeeeeeeee-code | [eeeeeeeeee-code/e0e1-wx](https://github.com/eeeeeeeeee-code/e0e1-wx) | WeChat unpacking workflows, asset recovery, and automated analysis pipelines |
| **WeChat-Hook** | aixed | [aixed/WeChat-Hook](https://github.com/aixed/WeChat-Hook) | Windows WeChat low-level hook techniques and internal protocol analysis |
| **wechat-windows-versions** | tom-snow | [tom-snow/wechat-windows-versions](https://github.com/tom-snow/wechat-windows-versions) | Archival tracking of WeChat desktop client versions and RadiumWMPF kernel evolution |

---

<a id="disclaimer"></a>
## ⚠️ Disclaimer

1. **Research and Compliance Only**: This project is provided exclusively for legitimate cybersecurity research, educational learning, frontend interoperability testing, and developer debugging. Any malicious use or illegal activities are strictly forbidden.
2. **User Responsibility**: Users assume full responsibility for their actions. The authors and contributors bear no liability for any direct or consequential damages, account restrictions, or legal disputes resulting from misuse.
3. **Intellectual Property**: All third-party trademarks, company names, and logos belong to their respective owners.
4. **Anti-Resale & Non-Commercial Notice**: This software and source code are **100% free and open-source**. **Reselling, repacking, or monetizing this tool on platforms such as Xianyu, Taobao, Pinduoduo, or automated card vending shops is strictly prohibited.** If you paid for this tool, please demand a full refund immediately.

---

<a id="license"></a>
## 📄 License

This project is licensed under the [CC BY-NC-SA 4.0 License](./LICENSE) (Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International), strictly prohibiting any commercial exploitation and unauthorized resale.
