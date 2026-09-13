<div align="center">

# WeChat-H5-DevTools

**The Ultimate Debugging & Reverse-Engineering Toolkit for WeChat 4.x In-App Browser & Official Account H5 Webpages**

[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Frida 17+](https://img.shields.io/badge/Frida-17+-FF69B4?logo=frida&logoColor=white)](https://frida.re/)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS-blue.svg)](https://github.com/)

[中文文档](./README.md) · [Matrix](#matrix) · [Features](#features) · [Quickstart](#quickstart) · [Architecture](#architecture) · [Sponsor](#sponsor) · [License](#license)

</div>

---

<a id="overview"></a>
## 📖 Overview

Following the WeChat 4.x desktop architecture updates, the native `F12` hotkey on the embedded browser window was completely removed. Additionally, testing WeChat H5 pages in standard external desktop browsers typically suffers from `"Please open this link in WeChat"`, missing `WeixinJSBridge` runtimes, and complex asynchronous Webpack chunk extraction.

**`WeChat-H5-DevTools`** delivers an all-in-one, production-grade toolkit combining **In-App vConsole Injection**, **Stealth WeChat Sandbox & JSSDK Polyfill**, **Local Overrides Hot-Reloading**, **Webcrack AST Deobfuscation & Webpack Extraction**, and **Deep Static Code & Cryptography Auditing**.

---

<a id="matrix"></a>
## 🖥️ WeChat & RadiumWMPF Kernel Compatibility Matrix

| WeChat Major Version | Tested Versions | RadiumWMPF Kernel Version | Core Render Process | Injection & Debug Mechanism | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **WeChat 4.1.x (Latest)**<br>*(Primary)* | **`4.1.13.12`**<br>`4.1.12.26`<br>`4.1.5.30` | **`25510` / `25497` / `25364` / `20089`**<br>*(Chromium 126+ CEF Pipeline)* | `WeixinExt.exe`<br>`Weixin.exe` (`--type=renderer`) | Frida dynamic hook on `CreateProcessW`<br>+ Transparent proxy auto-injects `vConsole` | `[PASS]` Full Support |
| **WeChat 4.0.x Series** | `4.0.2`<br>`4.0.1`<br>`4.0.0` | **`16389` / `16203` / `16133` / `14315`**<br>*(Blink Architecture)* | `Weixin.exe`<br>`WeChatAppEx.exe` | Adaptive process detection & multi-point CLI argument injection | `[PASS]` Full Support |
| **WeChat 3.9.x Classic** | `3.9.12`<br>`3.9.11`<br>`3.9.10` & older | **`11581` ~ `13909`**<br>*(Classic XWeb / Chromium 85~108)* | `WeChat.exe`<br>`WeChatAppEx.exe` | Native `--xweb-enable-inspect=1` channel | `[PASS]` Full Support |
| **Stealth Sandbox**<br>*(Standalone)* | Any OS<br>(Win / Mac / Linux) | **Latest Edge / Chrome**<br>*(Full Chromium 130+ V8 Engine)* | `msedge.exe`<br>`chrome.exe` | Sub-millisecond `document_start` injection with 30+ WeixinJSBridge mocks | `[PASS]` Native F12 |

> **💡 How to check your local RadiumWMPF kernel version?**
> Press `Win + R` and navigate to:
> `%AppData%\Tencent\xwechat\XPlugin\Plugins\RadiumWMPF`
> The numeric subfolder names (e.g. `25510`, `16389`) represent your active **RadiumWMPF kernel version**.

---

<a id="features"></a>
## ✨ Key Features

* **WeChat 4.x In-App DevTools Unlocker**: Powered by Frida 17+ hooks with multi-version auto-detection (fully verified on `4.1.13.12`);
* **Zero-Hotkey Transparent vConsole Proxy**: Built-in HTTP proxy gateway that injects `vConsole` / `Eruda` into all visited H5 web pages automatically;
* **Local Overrides Hot-Reloading**: Instantly replace remote online JS/CSS scripts with local files in real time without rebuilding or redeploying;
* **Stealth Browser Sandbox & JSSDK Mock**: Multi-platform WeChat UA presets paired with 30+ `WeixinJSBridge` native mocks (Payment, Scan, Location, Menu events) with native Chrome/Edge DevTools;
* **Full-Site Webpack Chunk Dumper**: Recursively unpacks all HTML, Webpack async JS bundles, CSS, and static assets preserving original path structures;
* **Webcrack AST Deobfuscator**: Integrated AST sanitization engine that repairs dangling closures and WeChat plugin wrappers, unpacking single-bundle files without warnings;
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

---

<a id="architecture"></a>
## 🏗️ Architecture

```
+------------------------------------------------------------------------+
|                   WeChat-H5-DevTools (Unified Engine)                  |
+------------------+----------------------+------------------------------+
| 1. inapp_injector| 2. stealth_sandbox   | 3. asset_extractor           |
| (WeChat Hook)    | (Stealth F12 Sandbox)| (Full-Site Source Reversing) |
+------------------+----------------------+------------------------------+
| * Process Detect | * Multi-OS WeChat UA | * HTML/DOM Deep Parser       |
| * Frida 17+ Hook | * WeixinJSBridge Mock| * Async Webpack Chunk Dumper |
| * Proxy Injector | * JSSDK 1.6.0 Mock   | * SourceMap Reconstruction   |
| * vConsole Ball  | * Chrome DevTools F12| * Webcrack AST Deobfuscator  |
| * Local Overrides|                      | * Full-Scale API & SM2/3/4   |
+------------------+----------------------+------------------------------+
```

---

<a id="sponsor"></a>
## ☕ Sponsor & Support

This project is actively maintained in the author's spare time, tracking the latest internal architecture updates of WeChat desktop clients (such as `4.1.13.12`) and **RadiumWMPF kernels**.

If **WeChat-H5-DevTools** helped your development, debugging, or security analysis workflow, feel free to sponsor a cup of coffee to support continued maintenance!

<div align="center">

| Alipay (Recommended) | WeChat Pay |
| :---: | :---: |
| <img src="docs/images/alipay_donate.jpg" width="220" alt="Alipay QR Code" /> | <img src="docs/images/wechat_donate.jpg" width="220" alt="WeChat Pay QR Code" /> |
| **Alipay: 苏辰的店铺 (**勇)** | **WeChat Pay: Y(**勇)** |

</div>

---

<a id="author"></a>
## 👤 Author & Contact

- **Author / Core Maintainer**: **xuange520**
- **WeChat (Recommended)**: `JAY_Secretsignal`
- **Email**: `2603066228@qq.com` / `xuangeylw@gmail.com`
- **GitHub Profile**: [@xuange520](https://github.com/xuange520)

---

<a id="license"></a>
## 📄 License

This project is open-source under the [MIT License](./LICENSE).
