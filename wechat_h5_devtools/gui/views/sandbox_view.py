# -*- coding: utf-8 -*-
import threading
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel
from qfluentwidgets import (
    TitleLabel, SubtitleLabel, CaptionLabel, BodyLabel, StrongBodyLabel,
    CardWidget, PrimaryPushButton, PushButton, LineEdit, ComboBox,
    InfoBar, InfoBarPosition, FluentIcon, ScrollArea
)
from ..common.signals import bridge_signals
from ...sandbox.browser_launcher import BrowserLauncher

class SandboxView(ScrollArea):
    """脱机高保真沙箱调试视图"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.view = QWidget(self)
        self.setWidget(self.view)
        self.setWidgetResizable(True)
        self.setObjectName("SandboxView")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self.view)
        layout.setContentsMargins(36, 28, 36, 28)
        layout.setSpacing(20)

        header = QVBoxLayout()
        header.setSpacing(4)
        title = TitleLabel("脱机高保真沙箱调试器 (Stealth Sandbox)")
        desc = CaptionLabel("脱离微信客户端限制，在电脑原生 Edge / Chrome 中以真实微信身份拉起网页，自动展开满血 F12 开发者工具")
        header.addWidget(title)
        header.addWidget(desc)
        layout.addLayout(header)

        # 启动卡片
        main_card = CardWidget(self)
        m_layout = QVBoxLayout(main_card)
        m_layout.setContentsMargins(24, 20, 24, 20)
        m_layout.setSpacing(16)

        m_title = StrongBodyLabel("高保真沙箱拉起设置")
        m_layout.addWidget(m_title)

        # URL 输入框
        url_box = QVBoxLayout()
        url_box.setSpacing(6)
        url_box.addWidget(BodyLabel("目标公众号或 H5 网页 URL:"))
        self.url_edit = LineEdit(self)
        self.url_edit.setPlaceholderText("https://mp.weixin.qq.com/s/... 或任何提示“请在微信客户端打开”的网页")
        self.url_edit.setText("https://mp.weixin.qq.com")
        self.url_edit.setClearButtonEnabled(True)
        url_box.addWidget(self.url_edit)
        m_layout.addLayout(url_box)

        # 快捷填入预设
        preset_box = QHBoxLayout()
        preset_box.addWidget(CaptionLabel("常用快捷预设:"))
        preset_mp = PushButton("微信官方推文样例", self)
        preset_mp.clicked.connect(lambda: self.url_edit.setText("https://mp.weixin.qq.com/s?__biz=MjM5NDAwNDI1MQ==&mid=2651872124&idx=1&sn=6185bbdffcc05beecdf3f590ffc13f64"))
        preset_pay = PushButton("微信 JS-SDK 规范样例", self)
        preset_pay.clicked.connect(lambda: self.url_edit.setText("https://open.weixin.qq.com/connect/oauth2/authorize"))
        preset_local = PushButton("本地代理测试页", self)
        preset_local.clicked.connect(lambda: self.url_edit.setText("http://127.0.0.1:8899/test"))
        preset_box.addWidget(preset_mp)
        preset_box.addWidget(preset_pay)
        preset_box.addWidget(preset_local)
        preset_box.addStretch()
        m_layout.addLayout(preset_box)

        # 浏览器与 UA 配置
        opt_grid = QGridLayout()
        opt_grid.setSpacing(12)

        opt_grid.addWidget(BodyLabel("目标浏览器引擎:"), 0, 0)
        self.browser_combo = ComboBox(self)
        self.browser_combo.addItems(["Microsoft Edge (系统原生内置 Chromium)", "Google Chrome"])
        opt_grid.addWidget(self.browser_combo, 0, 1)

        opt_grid.addWidget(BodyLabel("微信 User-Agent 伪装矩阵:"), 0, 2)
        self.ua_combo = ComboBox(self)
        self.ua_combo.addItems([
            "iOS 微信 (iPhone 15 Pro / WeChat 8.0.49)",
            "Android 微信 (Galaxy / WeChat 8.0.48 / XWEB 25560)",
            "Windows 微信桌面端 (WeChat 4.1.13 / XWEB 25560)",
            "macOS 微信桌面端 (Mac WeChat 4.0)"
        ])
        opt_grid.addWidget(self.ua_combo, 0, 3)

        m_layout.addLayout(opt_grid)

        # 启动按钮
        self.launch_btn = PrimaryPushButton(FluentIcon.PLAY, "拉起原生沙箱并在右侧展开 F12 调试器", self)
        self.launch_btn.clicked.connect(self.launch_sandbox)
        m_layout.addWidget(self.launch_btn)

        layout.addWidget(main_card)

        # Mock 原生接口矩阵展示卡片
        mock_card = CardWidget(self)
        mock_layout = QVBoxLayout(mock_card)
        mock_layout.setContentsMargins(24, 20, 24, 20)
        mock_layout.setSpacing(12)

        mock_title = StrongBodyLabel("沙箱高保真 WeixinJSBridge & JSSDK 挡板系统 (30+ 原生 API)")
        mock_layout.addWidget(mock_title)

        mock_desc = CaptionLabel(
            "沙箱将在页面启动的第 0 毫秒（document_start）注入原生 WeixinJSBridge 运行时与 JSSDK 1.6.0 挡板，\n"
            "已内置支持：微信支付请求（getBrandWCPayRequest）、实时精确定位（getLocation）、摄像头扫一扫（scanQRCode）、\n"
            "页面转发分享（sendAppMessage）、右上角菜单隐藏与标题设定等。页面判定为纯正微信环境，绝不报错弹窗拦截。"
        )
        mock_layout.addWidget(mock_desc)

        layout.addWidget(mock_card)
        layout.addStretch()

    def launch_sandbox(self):
        url = self.url_edit.text().strip()
        if not url:
            InfoBar.warning("输入有误", "请输入待调试的目标网页链接", parent=self)
            return

        browser_type = "edge" if "Edge" in self.browser_combo.currentText() else "chrome"
        ua_choice = self.ua_combo.currentText()
        ua_type = "ios"
        if "Android" in ua_choice:
            ua_type = "android"
        elif "Windows" in ua_choice:
            ua_type = "windows"
        elif "macOS" in ua_choice:
            ua_type = "mac"

        bridge_signals.log_emitted.emit("INFO", f"正在拉起沙箱: 浏览器={browser_type}, UA={ua_type}, 目标={url}")
        
        def run():
            try:
                launcher = BrowserLauncher(browser_type=browser_type)
                launcher.launch_url(url=url, ua_type=ua_type, open_devtools=True)
            except Exception as e:
                bridge_signals.log_emitted.emit("ERROR", f"沙箱拉起异常: {e}")

        threading.Thread(target=run, daemon=True).start()
        InfoBar.success("沙箱已拉起", f"已在独立 {browser_type.title()} 窗口中打开，F12 开发者工具已就绪！", parent=self)
