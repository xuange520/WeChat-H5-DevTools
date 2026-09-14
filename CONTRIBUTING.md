# 贡献指南与排错溯源定位规范 (Contributing & Troubleshooting)

感谢您对 **WeChat-H5-DevTools** 项目的关注！为了让开发者与用户在遇到微信版本更新、内核渲染异常或接口逆向故障时能够高效溯源、精准定位并快速修复，请遵循本规约。

---

## 🔍 故障排查与定位四步法 (Troubleshooting Protocol)

遇到任何执行异常或调试器未按预期唤出时，请按以下 4 步执行全链路溯源：

### 第一步：环境自我诊断
运行内置健康体检命令：
```bash
wx-h5 doctor
```
- 检查项包括：微信主程序是否存在、Chrome/Edge 安装路径、Frida 动态 Hook 运行库版本、Node.js 运行时及 AST 反混淆组件依赖。

### 第二步：核验 RadiumWMPF 内核版本
1. 按 `Win + R` 输入：
   ```text
   %AppData%\Tencent\xwechat\XPlugin\Plugins\RadiumWMPF
   ```
2. 查看当前生效的纯数字文件夹（如 `25510`、`16389`、`17127`）。
3. 检查该版本号是否在 [README 兼容矩阵](README.md#matrix) 中。若遇全新版本，微信可能升级了子进程名或注头偏移。

### 第三步：开启详细调试日志 (Debug Trace)
在命令后添加环境变量或捕获终端完整 Traceback：
```bash
python main.py doctor
wx-h5 proxy --port 8899
```
重点观察：
- 进程匹配是否命中 `WeixinExt.exe` 或 `Weixin.exe (--type=renderer)`；
- 端口 `8899` 是否被其他软件占用；
- 本地防火墙是否拦截了本地透明代理。

### 第四步：提交规范化 Bug 报告
如果确认属于内核不兼容或功能缺陷，请前往 [GitHub Issues](https://github.com/xuange520/WeChat-H5-DevTools/issues) 提交工单，或添加作者微信 `Sleep_Plan` 提交脱敏日志。

---

## 🛠️ 代码提交与 PR 规约

1. **分支策略**：所有开发基于 `main` 分支派生，PR 需包含清晰的 commit 信息（遵循 Conventional Commits 格式，如 `feat:`, `fix:`, `docs:`）。
2. **零凭据与噪音隔离**：严禁提交包含个人微信聊天数据、Cookies、临时抓包文件（`.har`）、测试报告等敏感资产。
3. **兼容性守则**：修改 `process_hooker.py` 或 `hook_inapp.js` 时，必须确保向后兼容微信 3.9.x、4.0.x 以及最新版 4.1.x。
