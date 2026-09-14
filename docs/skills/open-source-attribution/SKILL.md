---
name: open-source-attribution
description: 开源项目引用溯源、诚信鸣谢与防倒卖合规审计守卫。当用户要求规范开源借用项目、补充 README 鸣谢、在 GUI 中披露第三方开源依赖或制定防倒卖免责声明时激活此技能。
---

# 开源技术诚信与鸣谢守卫技能 (Open Source Attribution & Compliance Skill)

## 01. 技能定位与触发场景
在商业软件研发与开源项目构建中，严格秉承工程诚信与学术尊重。凡直接依赖、二次封装、算法提取或设计借鉴的开源项目，均须在文档与界面中建立完备的溯源链路。

## 02. 标准执行工作流

### 第一步：全域依赖与思路审计 (Audit Phase)
1. **代码与包管理排查**：
   - 检查 equirements.txt, package.json, Cargo.toml, go.mod 中的直接依赖；
   - 检查内部脚本、逆向 Hook 脚本、反混淆解析器中引用的开源项目；
2. **算法与架构借鉴排查**：
   - 梳理逆向研究中参考的社区 PoC、特征码扫描思路与工具箱项目；
   - 提取原作者 GitHub ID 与官方仓库绝对 URL。

### 第二步：双语 README 鸣谢落盘 (Documentation Phase)
1. 在 README.md 与 README_EN.md 中开辟专门的 ## 开源引用、技术借鉴与鸣谢 (Attribution & Acknowledgements) 章节；
2. 采用 GFM 富文本表格分类呈现：
   - **核心底层依赖组件**（项目名、官方 GitHub 仓库、许可证、作用）；
   - **生态研究与架构借鉴项目**（项目名、作者/组织、官方 GitHub 仓库、借鉴价值）；
3. 确保所有 GitHub 链接均为直接可点击的绝对 URL（如 https://github.com/frida/frida）。

### 第三步：GUI 客户端界面原样同步 (In-App Presentation Phase)
1. 在软件图形界面（WebGUI 或桌面 GUI）中设立独立的“开源鸣谢”菜单或视图面板；
2. 完整展示第三方项目的仓库地址与许可证信息；
3. 为每个仓库提供可直接跳转或一键复制的交互操作。

### 第四步：防倒卖与免责声明注入 (Anti-Resale & Compliance Phase)
1. 明确声明软件仅用于合法合规的安全研究与开发测试；
2. 严正注入 **“防倒卖与非商业性声明 (Anti-Resale Ban)”**：
   - 严禁任何个人或商业机构在闲鱼、淘宝、拼多多、发卡网等二手平台打包贩卖牟利；
   - 指引受害者在平台投诉退款并保留法律追责权利。
