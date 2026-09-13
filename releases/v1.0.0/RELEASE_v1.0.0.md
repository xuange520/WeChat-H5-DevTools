# WeChat-H5-DevTools v1.0.0 发布归档与溯源存证 (Release & Traceability Archive)

- **发布版本**：`v1.0.0`
- **归档日期**：`2026-09-14`
- **核心内核支持**：微信 4.1.x (`4.1.13.12`), RadiumWMPF (`25510`, `25497`, `25364`, `20089`, `16389`, `11581`)
- **发布产物清单与 SHA-256 校验哈希**：
```text
2b14a4698a91f01566c9c296a15605c2c6e81a5fcbe7700ea0c235085ab80b7f  WeChat-H5-DevTools-v1.0.0-standalone.zip
e839be21b65e3e6cd949810b394fb07b4303c3ddc0e0c01a9988d11e8743f3c1  wechat_h5_devtools-1.0.0-py3-none-any.whl
8613b8d413e4fa51b8ad5c39313e126c0945e75a98e079eb2a0e438c9d36619a  wechat_h5_devtools-1.0.0.tar.gz
```

---

## 🔍 后续排错与溯源定位指南 (Troubleshooting & Traceability Guide)

当用户或买家在后续使用中报告报错时，请按以下指引进行快速排障与版本锁定：

1. **版本锁定与哈希对比**：
   - 核对用户所用文件的 SHA-256 是否与上述发布基准一致，排查是否因本地修改或下载损坏导致；
2. **RadiumWMPF 路径与内核匹配**：
   - 用户微信内嵌环境路径：`%AppData%\Tencent\xwechat\XPlugin\Plugins\RadiumWMPF`
   - 检查该路径下的文件夹数字（如是否超过 25510），若为更高版本需排查注头偏移；
3. **关键进程拦截点检查**：
   - 微信 4.1.x 架构下必须捕获 `WeixinExt.exe` 与 `Weixin.exe (--type=renderer)`；
   - 若 Frida 挂载超时，使用 `wx-h5 doctor` 排查 Frida 与 Node 依赖环境；
4. **透明代理端口冲突排查**：
   - 默认端口 `8899`，若遇端口占用，引导用户切换：`wx-h5 proxy --port 9090`。
