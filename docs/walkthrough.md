# WeChat-H5-DevTools 仓库构建与 GitHub 私有部署完工总结

## 任务目标

将 `WeChat-H5-DevTools` 项目精简、完成代码审查、配置包含“微信全版本/内核兼容矩阵”、“新手傻瓜式三步起飞”与“赞助渠道”的大厂级 README，并在 GitHub 上以**私有仓库 (Private)** 形式完成初始化与推送，自动注入所选方案 3 Description 与 11 个核心 Topics 标签。

---

## 核心完成工作

### 1. 微信全版本与内核架构兼容矩阵 (Compatibility Matrix)
在 [README.md](file:///D:/源码/自写工具/WeChat-H5-DevTools/README.md) 与 [README_EN.md](file:///D:/源码/自写工具/WeChat-H5-DevTools/README_EN.md) 中完整梳理出微信全系列版本兼容矩阵：
- **微信 4.1.x 最新版**（如 `4.1.13.12`、`4.1.12.26`、`4.1.5.30`）：基于 Chromium 126+ (CEF 最新双进程渲染管线)，子进程标识为 `WeixinExt.exe` 与 `Weixin.exe (--type=renderer)`，支持 Frida 动态拦截 `CreateProcessW` 挂载注入 + 透明代理无感注入 `vConsole`。
- **微信 4.0.x 系列**（如 `4.0.0 ~ 4.0.2`）：基于 Chromium 116 ~ 122 (Blink 深度重构版)，子进程标识为 `Weixin.exe` / `WeChatAppEx.exe`。
- **微信 3.9.x 经典版**（如 `3.9.10 ~ 3.9.12` 及旧版）：基于 Chromium 85 ~ 108 (经典 XWeb 内核)，子进程标识为 `WeChatAppEx.exe`。
- **外部脱机沙箱**（全系统 Chrome / Edge 满血 F12）：基于独立浏览器引擎，毫秒级注入 30+ `WeixinJSBridge` 原生 Mock。

### 2. 小白新手三步起飞指引（零 AI 门槛、零编程基础）
针对不熟悉 AI 与命令行的非专业开发者，拆解并提炼出保姆级常用场景：
- **需求 A**：在电脑微信里看控制台与抓包 -> `wx-h5 proxy`，微信网页右下角直接浮动绿色 vConsole 按钮。
- **需求 B**：绕过微信客户端限制在电脑浏览器按 F12 调试 -> `wx-h5 open "链接"`，直接拉起原生 F12 沙箱。
- **需求 C**：混淆代码还原与模块拆包 -> `wx-h5 deobfuscate "目录"`，一键全量 AST 解混淆与 Webpack 解包。
- **需求 D**：一键排查后端 API、域名与国密加密 -> `wx-h5 scan "目录" -e 审计报告.md`，自动导出排版精美报告。

### 3. 开源赞助与支持板块 (Sponsor)
- 新增 `☕ 赞助与支持 (Sponsor)` 章节。
- 阐明业余深度逆向研发、持续追踪跟进微信客户端（如最新的 `4.1.13.12`）底层渲染架构不易。
- 设立微信赞助与支付宝赞助双通道，并提供赞助者专属权益（优先响应特定版本适配需求、永久收录赞助榜）。

### 4. 纯净代码审查与噪音阻断
- 全项目严格限定为 **30 个核心纯净源码文件**，杜绝任何历史抓包、中间临时脚本与缓存外流。
- 逆向输出 `output/`、临时探针 `scratch/`、测试报告 `audit_report.md` 及构建缓存 `__pycache__` 已 100% 由 `.gitignore` 阻断。

### 5. GitHub 远端私有部署与元数据全自动绑定
- **仓库地址**：`https://github.com/xuange520/WeChat-H5-DevTools`
- **可见性**：**Private (私有)**，严格满足长官安全确认要求。
- **Description 方案 3 自动注入**：
  > 微信内置浏览器与公众号 H5 满血调试与逆向工具箱 / The ultimate debugging & reverse-engineering toolkit for WeChat In-App Browser & H5 Webpages with Frida hook, vConsole proxy, Webcrack and API analyzer.
- **Topics 标签全自动注入 (11项)**：
  `wechat` · `wechat-devtools` · `h5-debugging` · `frida` · `vconsole` · `local-overrides` · `webpack-reverse` · `webcrack` · `reverse-engineering` · `miniprogram` · `sourcemap`
- **远程分支提交树**：
  - `bad9a25` feat: initial commit for WeChat-H5-DevTools (wx-h5)
  - `093d0a7` fix(hook): add WeixinExt.exe and --type=renderer support for WeChat 4.1.x
  - `e315f5c` docs: add WeChat version compatibility matrix, beginner guide, and sponsor section
  - `6dea3d9` fix(docs): fix anchor navigation links and restore system architecture section
  - `24072eb` feat(release): v1.0.0 release archive, RadiumWMPF matrix, QR sponsor codes, and contributor workflows

---

### 6. README 顶部导航锚点 100% 物理对齐与系统架构恢复
- **失效根因排查**：
  1. GFM (GitHub Flavored Markdown) 解析中文与 Emoji 标题时会自动剥离 Emoji，且不会在标题前生成 `-`（如 `## ✨ 核心功能全景` 对应 slug 为 `#核心功能全景`，而旧导航链接使用了 `[核心功能](#-核心功能)`，产生双重不匹配）；
  2. 旧版 `README.md` 中缺少 `## 🏗️ 系统架构` 章节，导致点击该锚点无法命中目标；
  3. 各浏览器对多语言中文字符 URL Hash 编码存在差异，纯依靠自动生成 slug 容易出现兼容性漂移。
- **物理修复方案**：
  1. 为 `README.md` 与 `README_EN.md` 全量章节注入显式 HTML 锚点标签（如 `<a id="features"></a><a id="核心功能"></a>`、`<a id="quickstart"></a><a id="快速上手"></a>` 等），兼容英文简写与原生中文；
  2. 恢复原汁原味的 `## 🏗️ 系统架构` ASCII 架构全景图解；
  3. 顶部导航栏全面升级为纯净锚点路由：
     `[核心功能](#features) · [快速上手](#quickstart) · [命令行指南](#cli) · [实战工作流](#workflows) · [系统架构](#architecture) · [兼容矩阵](#matrix) · [常见问题](#faq) · [赞助支持](#sponsor) · [免责声明](#disclaimer)`；
  4. 提交并无缝推送至 GitHub 远端 `main` 分支。

---

### 7. Releases / Packages / Contributors 三大中枢与本地归档存证建立

#### A. Releases 首次官方发布与本地完整归档
- **GitHub 远端 Release**：已正式发布 [v1.0.0 Release](https://github.com/xuange520/WeChat-H5-DevTools/releases/tag/v1.0.0)，附带全套资产；
- **本地归档存证目录**：`releases/v1.0.0/`
  - `WeChat-H5-DevTools-v1.0.0-standalone.zip`（绿色免安装独立分发包，8.33MB）
  - `wechat_h5_devtools-1.0.0-py3-none-any.whl`（Python 纯净二进制包，45.9KB）
  - `wechat_h5_devtools-1.0.0.tar.gz`（源码包，44.2KB）
  - `SHA256SUMS.txt`（物理完整性校验清单）
  - `RELEASE_v1.0.0.md`（版本锁定、发布元数据与排错溯源指南）

#### B. Packages 规范化构建与分发
- **打包配置强化**：在 `pyproject.toml` 中配置 `package-data`，全量打包 `injector/scripts/*.js`、`sandbox/_runtime_extension/*`、`sandbox/polyfills/*.js` 与 `extractor/*.js`，彻底杜绝 pip 安装后非 Python 静态文件缺失问题；
- **本地包仓库**：产物同步收拢于 `dist/` 与 `releases/v1.0.0/packages/`，支持离线环境一键 `pip install`。

#### C. Contributors 贡献者关联与排错溯源支撑体系
- **GitHub 贡献者图谱打通**：通过将 Commit 提交作者与 GitHub 账号 `xuange520 <xuangeylw@gmail.com>` 完美对齐，GitHub 仓库侧边栏 `Contributors` 计数实时激活为 `1`；
- **排错溯源定位制度化**：
  - [CONTRIBUTORS.md](file:///D:/源码/自写工具/WeChat-H5-DevTools/CONTRIBUTORS.md)：收录核心维护者与官方微信联系渠道 `JAY_Secretsignal`；
  - [CONTRIBUTING.md](file:///D:/源码/自写工具/WeChat-H5-DevTools/CONTRIBUTING.md)：建立“故障排查与定位四步法”（环境自我诊断 -> RadiumWMPF 内核核验 -> Debug Trace 捕获 -> 标准化工单提交）；
  - `.github/ISSUE_TEMPLATE/`：内置包含微信版本号、RadiumWMPF 内核版本、OS 版本与完整 Traceback 的 `bug_report.yml`、`feature_request.yml` 与紧急排障链接 `config.yml`。

---

### 8. RadiumWMPF 内核版本深度梳理与真实收款码同步
1. **RadiumWMPF 内核版本矩阵写入**：
   - 微信 4.1.x 最新版：RadiumWMPF **`25510` / `25497` / `25364` / `20089`**（基于 Chromium 126+ CEF 最新渲染管线）
   - 微信 4.0.x 系列：RadiumWMPF **`16389` / `16203` / `16133` / `14315`**
   - 微信 3.9.x 经典版：RadiumWMPF **`11581` ~ `13909`**
   - 附带本路径查看指引：`%AppData%\Tencent\xwechat\XPlugin\Plugins\RadiumWMPF`
2. **赞助二维码从 Antigravity-Nexus 无损迁移**：
   - 从 `xuange520/Antigravity-Nexus` 镜像拉取 `alipay_donate.jpg` 与 `wechat_donate.jpg` 至 `docs/images/`；
   - 在中英双语 README 赞助栏以居中富文本表格渲染真实收款码，并补充作者官方微信 `JAY_Secretsignal` 商务与技术交流通道。

---

### 9. 一版本一目录独立版本存证架构落地 (`records/`)
为严格落实长官关于**“每个版本记录单独一个文件存放，不要所有版本记录混在同一个文件夹内”**的指令，在项目内设立全新原子化存证体系：
- **存证根目录**：[records/README.md](file:///D:/源码/自写工具/WeChat-H5-DevTools/records/README.md)（明确多版本隔离规约与索引）；
- **v1.0.0 专属目录**：[records/v1.0.0/](file:///D:/源码/自写工具/WeChat-H5-DevTools/records/v1.0.0)
  - [version_record.md](file:///D:/源码/自写工具/WeChat-H5-DevTools/records/v1.0.0/version_record.md)：人类可读排错溯源档案（元数据、RadiumWMPF 兼容基准、发布物指纹、4 级排错 SOP、常见异常与自愈速查表）；
  - [version_record.json](file:///D:/源码/自写工具/WeChat-H5-DevTools/records/v1.0.0/version_record.json)：机器可读结构化元数据（便于自动化运维工具校验）；
  - [checksums.sha256](file:///D:/源码/自写工具/WeChat-H5-DevTools/records/v1.0.0/checksums.sha256)：唯一物理哈希防篡改指纹；
- **后续版本演进标准**：当发布 `v1.0.1`、`v1.1.0` 时，强制新建独立同级目录 `records/v1.0.1/`，各版本生命周期与故障溯源 100% 物理隔离。

---

### 10. 全局准则 Rule 35 写入与专属技能固化

#### A. 全局核心准则第 35 条写入 (`AGENTS.md`)
- **文件路径**：[C:/Users/26030/.gemini/config/AGENTS.md](file:///C:/Users/26030/.gemini/config/AGENTS.md)
- **准则条目**：`35. GitHub 项目 Releases、Packages 与 Contributors 三位一体中枢铁律 (GitHub Lifecycle Protocol)`
- **核心约束**：
  1. 凡 GitHub 项目交付、开源或公开发布（如有必要），必须 100% 规范建立 **Releases**（Tag/Changelog/独立包/SHA-256）、**Packages**（静态资源完整打包入库/双向分发）与 **Contributors**（Git 作者强绑定 GitHub 账号激活图谱/贡献与排错指南）；
  2. 本地版本记录强制在 `records/vX.Y.Z/` 独立目录中单文件存放，严禁多版本混存同一文件或目录。

#### B. 专属工程技能落盘 (`github-release-packages-hub`)
- **技能路径**：[C:/Users/26030/.gemini/config/skills/github-release-packages-hub/SKILL.md](file:///C:/Users/26030/.gemini/config/skills/github-release-packages-hub/SKILL.md)
- **涵盖内容**：
  - 交付标准与三位一体架构定义；
  - Releases 自动化 API 发布流水线与 Assets 挂载 SOP；
  - Packages 标准打包与静态资源 `package-data` 防漏校验门禁；
  - Contributors 账号绑定与工单模版套件设计；
  - `records/` 原子化版本存证 SOP；
  - 避坑指南（包括 PAT Token 缺少 `workflow` 权限时自愈方案、Contributors 未激活排查等）。

---

### 11. 收款二维码纯码微创裁剪与实名脱敏

为 100% 落实长官关于**“去掉实名后面名字、只截取二维码、底下只标注支付宝或微信”**的指令：
1. **OpenCV 精准特征点定位与裁剪**：
   - 调用 `cv2.QRCodeDetector` 定位两张收款码的四个物理角点；
   - 支付宝码裁剪至 `(450, 449)` 纯黑白矩阵，微信码裁剪至 `(342, 342)` 纯黑白矩阵，外留 18px 纯白安全边距；
   - 彻底剥离顶部店铺名、底部括号后缀及任何真实姓名文字；
2. **README 双语文档标注纯净化**：
   - 替换所有原“苏辰的店铺”、“勇”字样；
   - 中文 README 对应标注统一改为：`| 支付宝 | 微信支付 |`；
   - 英文 README 对应标注统一改为：`| Alipay | WeChat Pay |`；
3. **全项目二次实据核验**：
   - 经全局敏感词检索，全项目代码与文档已实现 0 字符实名残留；
   - 提交 `ef49c92` 并实时推送至 GitHub 远端 `main` 分支。
