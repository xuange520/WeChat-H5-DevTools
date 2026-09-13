# WeChat-H5-DevTools v1.0.0 版本独立溯源与排错归档档案

---

## 📌 版本基础元数据 (Metadata)

| 属性字段 | 详细记录值 | 备注说明 |
| :--- | :--- | :--- |
| **版本号** | **`v1.0.0`** | 首次官方生产级发布版 |
| **归档日期** | `2026-09-14` | 发布与封版日期 |
| **Git 标签** | `v1.0.0` | 远端唯一对齐 Tag |
| **Git Commit** | `24072ebf09a828fb66fc3b314461f71fa7d3f003` | 封版物理提交 SHA |
| **发布分支** | `main` | 默认主分支 |
| **核心维护者** | **xuange520** (Jay) | GitHub: [@xuange520](https://github.com/xuange520) |
| **排障微信通道** | `JAY_Secretsignal` | 疑难排障与适配第一优先级通道 |
| **官方邮箱** | `2603066228@qq.com` / `xuangeylw@gmail.com` | 备用沟通通道 |

---

## 🖥️ 微信版本与 RadiumWMPF 内核兼容基准

本版本经过真实环境端到端验证，兼容以下微信客户端版本与内嵌 RadiumWMPF 内核：

| 微信客户端版本 | 内嵌 RadiumWMPF 内核版本 | 关键渲染子进程 | 注入与挂载通道 |
| :--- | :--- | :--- | :--- |
| **微信 4.1.13.12 (最新)**<br>微信 4.1.12.26<br>微信 4.1.5.30 | **`25510`**<br>`25497`<br>`25364`<br>`20089` | `WeixinExt.exe`<br>`Weixin.exe` (`--type=renderer`) | Frida 拦截 `CreateProcessW` 挂载<br>+ 透明代理无感注入 `vConsole` |
| **微信 4.0.2**<br>微信 4.0.1<br>微信 4.0.0 | **`16389`**<br>`16203`<br>`16133`<br>`14315` | `Weixin.exe`<br>`WeChatAppEx.exe` | 进程特征自适应探测与命令行注头 |
| **微信 3.9.12 经典版**<br>微信 3.9.11<br>微信 3.9.10 | **`11581` ~ `13909`**<br>*(经典 XWeb 内核)* | `WeChat.exe`<br>`WeChatAppEx.exe` | 经典 `--xweb-enable-inspect=1` 通道 |
| **外部脱机高保真沙箱** | Chromium 130+ (Edge/Chrome) | `msedge.exe` / `chrome.exe` | 毫秒级 30+ `WeixinJSBridge` 原生 Mock |

> **物理路径存证**：`%AppData%\Tencent\xwechat\XPlugin\Plugins\RadiumWMPF`

---

## 📦 本地发布产物与 SHA-256 指纹存证

所有 v1.0.0 版本的正式打包分发物已于本地物理落盘，任何外部汇报异常均需先核验 SHA-256 是否被篡改或损坏：

| 产物文件名 | 文件大小 | SHA-256 哈希值 |
| :--- | :--- | :--- |
| `WeChat-H5-DevTools-v1.0.0-standalone.zip` | 8,331,112 字节 | `2b14a4698a91f01566c9c296a15605c2c6e81a5fcbe7700ea0c235085ab80b7f` |
| `wechat_h5_devtools-1.0.0-py3-none-any.whl` | 45,940 字节 | `e839be21b65e3e6cd949810b394fb07b4303c3ddc0e0c01a9988d11e8743f3c1` |
| `wechat_h5_devtools-1.0.0.tar.gz` | 44,290 字节 | `8613b8d413e4fa51b8ad5c39313e126c0945e75a98e079eb2a0e438c9d36619a` |

---

## 🛠️ 后续排错、溯源与报错定位 SOP (Troubleshooting Protocol)

当后续用户或买家运行此版本出现报错时，请按以下 4 级 SOP 逐级排错定位：

### 阶段一：指纹与版本一致性校验 (Fingerprint Audit)
1. **核对哈希**：运行 PowerShell 校验用户本地文件哈希：
   ```powershell
   Get-FileHash -Algorithm SHA256 <用户的文件路径>
   ```
   对比是否与上方存证的 SHA-256 完全匹配。若不一致，判定为文件下载不完整或被第三方改动。
2. **核对 Git Commit**：运行 `git rev-parse HEAD` 确认源码是否处于 `24072eb`。

### 阶段二：微信与 RadiumWMPF 内核版本偏移排查 (Kernel Drift Detection)
1. 引导用户打开运行窗口（`Win + R`），输入：
   ```text
   %AppData%\Tencent\xwechat\XPlugin\Plugins\RadiumWMPF
   ```
2. **定位目录下的纯数字**：
   - 若数字落在 `25510`、`25497`、`25364`、`20089`、`16389`、`11581` 范围内：内核完全匹配，故障通常由权限、网络代理或防火墙引起；
   - 若数字为**全新未收录版本**（如 `26xxx` 或 `27xxx`）：说明微信静默推送了新内核，需抓取子进程启动参数比对 CEF 命令行开关是否变更。

### 阶段三：子系统定位与 Trace 日志提取 (Trace Log Extraction)
| 异常报错现象 | 对应底层模块 | 核心排障文件与代码位置 | 自愈排障步骤 |
| :--- | :--- | :--- | :--- |
| **`wx-h5 doctor` 报 Frida 或环境缺失** | 环境探测器 | `wechat_h5_devtools/cli.py:doctor()` | 运行 `pip install frida>=16.0.0`，检查系统 PATH 中是否安装了 Node.js。 |
| **`wx-h5 proxy` 启动后无小球** | 透明代理与注头网关 | `wechat_h5_devtools/injector/proxy_injector.py` | 1. 检查 `8899` 端口是否被占用；<br>2. 检查微信代理是否正确指向 `127.0.0.1:8899`；<br>3. 检查是否开启了全局 VPN/科学上网软件导致回路截断。 |
| **`wx-h5 open` 提示页面环境异常** | 独立沙箱 Polyfill | `wechat_h5_devtools/sandbox/polyfills/weixin_bridge.js` | 目标 H5 调用了冷门微信专属 API，在 `weixin_bridge.js` 中补全该 API 的 mock 返回。 |
| **`wx-h5 deobfuscate` 报错** | Webcrack 逆向引擎 | `wechat_h5_devtools/extractor/webcrack_runner.js` | 运行 `node wechat_h5_devtools/extractor/webcrack_runner.js --help` 验证 Node 环境。 |
| **微信 4.1.x 下子进程未被挂载** | Frida Hook 引擎 | `wechat_h5_devtools/injector/scripts/hook_inapp.js` | 确认任务管理器中是否存在 `WeixinExt.exe` 或 `Weixin.exe`，检查是否有第三方杀软拦截进程创建。 |

### 阶段四：不可抗力与长官直接介入通道 (Escalation)
若上述 3 级排错均无法解决：
1. 请用户执行 `wx-h5 doctor > diag.txt 2>&1` 导出脱敏诊断文件；
2. 直接通过微信联系核心开发者 `JAY_Secretsignal`，并附上本档案编号 `v1.0.0-24072eb` 启动 1 对 1 定向修复。
