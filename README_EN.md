<div align="center">

<img src="docs/images/logo.png" width="160" alt="WeChat-H5-DevTools Logo" />

# WeChat-H5-DevTools

**The Ultimate Debugging & Reverse-Engineering Toolkit for WeChat 4.x In-App Browser & Official Account H5 Webpages**

[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Frida 17+](https://img.shields.io/badge/Frida-17+-FF69B4?logo=frida&logoColor=white)](https://frida.re/)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS-blue.svg)](https://github.com/)

[中文文档](./README.md) · [Matrix](#matrix) · [Screenshots](#screenshots) · [Features](#features) · [Quickstart](#quickstart) · [FAQ](#faq) · [Sponsor](#sponsor) · [Community](#community) · [License](#license)

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


<a id="faq"></a>
## ❓ Troubleshooting & FAQ

<details>
<summary><strong>Q1 [Proxy Troubleshooting]: Why does the WeChat in-app browser fail to connect or display "Proxy Server Refused Connection"?</strong></summary>

> **Solution**: This is typically caused by local port occupation, system proxy overwrite, or unverified root certificates:
> 1. **Port Conflicts**: Default proxy port `8899` might be occupied by other proxies/tools (Clash, v2rayN, Fiddler, Charles). Run `netstat -ano | findstr 8899` and specify an idle port using `wx-h5 proxy --port 8999`;
> 2. **Network Sandbox**: WeChat 4.x isolates networking into `WeChatUtility.exe` / `WeChatAppEx.exe`. Ensure Windows Proxy Settings point to `127.0.0.1:8899` and disable conflicting TUN mode VPNs;
> 3. **HTTPS Certificate**: If `NET::ERR_CERT_AUTHORITY_INVALID` is encountered, install the generated mitmproxy root certificate (`~/.mitmproxy/mitmproxy-ca-cert.cer`) into the Windows **Trusted Root Certification Authorities** store.
</details>

<details>
<summary><strong>Q2 [Cross-Version Kernel Decoupling]: How does the tool maintain compatibility across WeChat 3.9/4.0/4.1 and RadiumWMPF upgrades without manual offsets?</strong></summary>

> **Solution**: Rather than hardcoded static memory offsets or legacy CLI switches (`--xweb-enable-inspect=1`), the suite uses a **Three-Tier Adaptive Decoupling & Signature Scanning** architecture:
> 1. **Runtime Signature Scanning**: Dynamically scans Chromium VTable pointers, `DevToolsActivePort` branches, and Blink initialization routines;
> 2. **Three-Tier Fallback**:
>    - **L1 Process Interception**: Frida hooks host `CreateProcessW` to inject `--remote-debugging-port` at process birth;
>    - **L2 Protocol Injection**: Hooks runtime `WeixinJSBridge` message dispatch to append `vConsole`;
>    - **L3 Transparent Proxy**: Streaming AST injection at the network transport layer;
> 3. **Address Pools**: Built-in `addresses.<kernel_version>.json` configuration pool (e.g. Radium 25560) enables zero-recompile hot updates.
</details>

<details>
<summary><strong>Q3 [Strong Cache Busting]: Why do modified local scripts in Local Overrides fail to reflect upon refreshing?</strong></summary>

> **Solution**: WeChat enables aggressive **Chromium Disk Cache** and HTTP 304 revalidation for web resources:
> 1. **Automatic Header Stripping**: `wx-h5 sandbox` and `wx-h5 proxy` strip `ETag` / `If-Modified-Since` and inject `Cache-Control: no-cache, no-store, must-revalidate` and `Pragma: no-cache`;
> 2. **Disk Cache Purge**: Clear via vConsole **Storage -> Clear Cookies & Cache** or clear `%APPDATA%\Tencent\WeChat\radium\web\cache`;
> 3. **URL Timestamping**: Append query parameter `?_t=<timestamp>` to bypass URL index caching.
</details>

<details>
<summary><strong>Q4 [Multi-Process Pipeline Identification]: How does the tool isolate the target renderer among dozens of WeChat processes?</strong></summary>

> **Solution**: WeChat 4.x adopts the Chromium multi-process sandbox architecture:
> 1. **Process Topology**:
>    - `WeChat.exe`: Main UI & messaging broker;
>    - `WeChatAppEx.exe` / `WeixinExt.exe`: RadiumWMPF Chromium rendering sandbox (Hook target);
>    - `WeChatUtility.exe`: Background network & media codecs;
> 2. **Pipeline Detector**: `wx-h5 hook` scans process command line arguments for `--type=renderer` and verifies loaded `radium.dll` modules to lock the exact PID;
> 3. **Manual PID Binding**: Run `wx-h5 inspect --list` and bind with `wx-h5 hook --pid <PID>`.
</details>

<details>
<summary><strong>Q5 [Large-Memory AST Deobfuscation]: Why does Node.js crash with "JavaScript heap out of memory" on large bundles (>5MB)?</strong></summary>

> **Solution**: Large SPAs expand 20-40x in AST memory during node traversal:
> 1. **V8 Heap Expansion**: Allocate 8GB+ memory before running:
>    `$env:NODE_OPTIONS="--max-old-space-size=8192"` (PowerShell) or `set NODE_OPTIONS=--max-old-space-size=8192` (CMD);
> 2. **Chunked Deobfuscation (`--chunked`)**: Splits top-level Webpack module dictionaries and deobfuscates modules individually, reducing peak memory from 4GB to ~400MB;
> 3. **Library Exclusion**: Pass `--exclude-libs` to skip known OSS libraries (`vue`, `react`, `echarts`).
</details>

<details>
<summary><strong>Q6 [CDN Anti-Hotlinking & CORS Bypass]: How to resolve 403 Forbidden or CORS errors when loading remote assets?</strong></summary>

> **Solution**:
> 1. **Anti-Hotlinking Header Spoofing**: Automatically injects valid WeChat headers:
>    `Referer: https://servicewechat.com/` and genuine `MicroMessenger` User-Agent strings;
> 2. **CORS & CSP Stripping**: Automatically strips upstream `Content-Security-Policy` and injects `Access-Control-Allow-Origin: *`.
</details>

<details>
<summary><strong>Q7 [Privilege Elevation & UAC Isolation]: Why does Hook injection fail with "Access is denied (os error 5)"?</strong></summary>

> **Solution**:
> 1. **Integrity Level**: If WeChat is launched as Administrator (High Integrity), medium-integrity terminal processes cannot obtain `PROCESS_ALL_ACCESS` handles;
> 2. **Elevation**: Right click PowerShell/CMD and select **Run as administrator**;
> 3. **Native UAC**: Standalone executables are embedded with `requireAdministrator` manifests to auto-prompt for UAC elevation upon double-click.
</details>

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

<a id="license"></a>
## 📄 License

This project is open-source under the [MIT License](./LICENSE).
