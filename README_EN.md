<div align="center">

# 🚀 WeChat-H5-DevTools

**The Ultimate Debugging & Reverse-Engineering Toolkit for WeChat 4.x In-App Browser & Official Account H5 Webpages**

[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Frida 17+](https://img.shields.io/badge/Frida-17+-FF69B4?logo=frida&logoColor=white)](https://frida.re/)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS-blue.svg)](https://github.com/)

[中文文档](./README.md) · [Features](#-key-features) · [Quickstart](#-quickstart) · [CLI Usage](#-cli-usage-guide) · [Architecture](#-architecture)

</div>

---

## 📖 Overview

Following the WeChat 4.x desktop architecture updates, the native `F12` hotkey on the embedded browser window was completely removed. Additionally, testing WeChat H5 pages in standard external desktop browsers typically suffers from `"Please open this link in WeChat"`, missing `WeixinJSBridge` runtimes, and complex asynchronous Webpack chunk extraction.

**`WeChat-H5-DevTools`** delivers an all-in-one, production-grade toolkit combining **In-App vConsole Injection**, **Stealth WeChat Sandbox & JSSDK Polyfill**, and **Deep Webpack SPA Reverse Engineering**.

---

## ✨ Key Features

* 🎛️ **WeChat 4.x In-App DevTools Unlocker**: Powered by Frida 17+ hooks with multi-version auto-detection;
* 🟢 **Zero-Hotkey Transparent vConsole Proxy**: Built-in HTTP proxy gateway that injects `vConsole` / `Eruda` into all visited H5 web pages automatically;
* 🛡️ **Stealth Browser Sandbox & JSSDK Mock**: Multi-platform WeChat UA presets paired with 30+ `WeixinJSBridge` native mocks (Payment, Scan, Location, Menu events) with native Chrome/Edge DevTools;
* 📦 **Full-Site Webpack Chunk Dumper**: Recursively unpacks all HTML, Webpack async JS bundles, CSS, and static assets preserving original path structures;
* 🧩 **SourceMap Rebuilder**: Unpacks `.map` files into original human-readable `.vue` SFCs, TypeScript, and SCSS/Less code;
* 🔍 **API Endpoint & Crypto Analyzer**: Scans dumped JS for RESTful API routes, hardcoded AppIDs, and cryptographic algorithms (SM2/SM3/SM4, AES, RSA, HMAC).

---

## 🚀 Quickstart

```bash
# Clone the repository
git clone https://github.com/your-username/WeChat-H5-DevTools.git
cd WeChat-H5-DevTools

# Install requirements
pip install -r requirements.txt

# (Optional) Install as a global CLI command
pip install -e .
```

### Environment Check

```bash
python main.py doctor
```

---

## 💻 CLI Usage Guide & Workflows

You can invoke commands using `python main.py <command>` or the global alias `wx-h5 <command>`.

### 📋 Command & Options Cheat Sheet

| Command | Purpose | Key Arguments & Flags | Example |
| :--- | :--- | :--- | :--- |
| `doctor` | Diagnose local WeChat, browser & Frida environment | None | `wx-h5 doctor` |
| `hook` | Inject DevTools parameters into running WeChat | `--path` (optional custom Weixin.exe path) | `wx-h5 hook` |
| `proxy` | Start local vConsole HTTP transparent proxy | `--port, -p` (default: `8899`) | `wx-h5 proxy --port 8899` |
| `open` | Launch external Chrome/Edge with full F12 & Mock | `<url>`, `--browser`, `--ua`, `--no-devtools` | `wx-h5 open "https://..." --ua ios` |
| `dump` | Recursively dump full Webpack SPA assets | `<url>`, `--output, -o` (output directory) | `wx-h5 dump "https://..." -o ./site` |
| `restore` | Reconstruct original Vue/TS source from maps | `<target_dir>` | `wx-h5 restore ./site` |
| `scan` | Scan JS for REST APIs and Crypto signatures | `<target_dir>`, `--export, -e` (export MD) | `wx-h5 scan ./site -e report.md` |

---

### 🎯 Typical Scenarios

#### Scenario 1: Debugging Directly Inside WeChat Desktop (Floating vConsole)
1. Start the proxy: `wx-h5 proxy --port 8899`
2. Set your system or WeChat upstream proxy to `127.0.0.1:8899`
3. Open any Official Account H5 in WeChat; a green `vConsole` panel will automatically appear at the bottom right.

#### Scenario 2: Debugging WeChat H5 in Chrome/Edge with Native DevTools
1. Run: `wx-h5 open "https://mp.weixin.qq.com/s/..." --browser edge --ua ios`
2. The browser launches with full Chrome DevTools, preloaded with `WeixinJSBridge` mock at `document_start`.

#### Scenario 3: Reverse Engineering Webpack SPA Source Code
1. **Dump assets**: `wx-h5 dump "https://target-h5.com/..." -o ./my_project`
2. **Rebuild source**: `wx-h5 restore ./my_project`
3. **Audit APIs**: `wx-h5 scan ./my_project --export api_report.md`

---

## 💬 Community & Discussion

Join the **WeChat-H5-DevTools Community** for the latest JSSDK reverse-engineering tips, automation strategies, and updates:

<div align="center">
  <img src="./assets/community_group.png" width="280" alt="WeChat Community Group QR Code" />
  <p><strong>💡 Note</strong>: If the QR code has expired or cannot be joined directly, <strong>please add the author's WeChat (Remark: H5 DevTools)</strong> to be manually invited to the core group.</p>
</div>

---

## ⚠️ Disclaimer

1. **For Research & Development Only**: This project (`WeChat-H5-DevTools`) is intended solely for educational, security research, cross-platform compatibility testing, and Web debugging purposes. Any unauthorized or malicious use is strictly prohibited.
2. **Assumption of Risk**: Users are solely responsible for compliance with relevant local laws, platform terms of service, and policies. The authors and contributors shall not be held liable for any direct or indirect consequences, account restrictions, or legal liabilities arising from the use of this tool.
3. **Intellectual Property**: All third-party trademarks, brand names, and protocol logos referenced belong to their respective copyright holders.

---

## 📄 License

Distributed under the [MIT License](./LICENSE).
