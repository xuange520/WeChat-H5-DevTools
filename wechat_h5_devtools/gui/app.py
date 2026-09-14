# -*- coding: utf-8 -*-
import sys
import os
from pathlib import Path
from PySide6.QtCore import Qt, QSize, QTimer
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication
from qfluentwidgets import (
    MSFluentWindow, NavigationItemPosition, FluentIcon,
    setTheme, Theme, InfoBar, InfoBarPosition
)

from .views.dashboard_view import DashboardView
from .views.injector_view import InjectorView
from .views.sandbox_view import SandboxView
from .views.extractor_view import ExtractorView
from .views.scanner_view import ScannerView
from .views.console_view import ConsoleView
from .common.signals import bridge_signals

class MainWindow(MSFluentWindow):
    """WeChat-H5-DevTools 现代 Fluent Design 主工作台"""
    def __init__(self):
        self._resize_timer = None
        super().__init__()
        self.setWindowTitle("WeChat-H5-DevTools v1.0.0 - 微信内置浏览器 / 公众号 H5 调试工程套件")
        
        # 默认暗黑极客主题
        setTheme(Theme.DARK)

        # 统一暗黑背景与透明滚动条
        self.setStyleSheet("""
            MSFluentWindow, MainWindow {
                background-color: #202020;
            }
            ScrollArea, QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollArea > QWidget > QWidget {
                background-color: transparent;
            }
        """)

        # 80ms 窗口缩放防抖节流 (Rule 28 性能规范)
        self._resize_timer = QTimer(self)
        self._resize_timer.setSingleShot(True)
        self._resize_timer.setInterval(80)

        self.init_views()
        self.init_navigation()
        self.init_window()

    def init_views(self):
        """初始化各功能子视窗"""
        self.dashboard_view = DashboardView(self)
        self.injector_view = InjectorView(self)
        self.sandbox_view = SandboxView(self)
        self.extractor_view = ExtractorView(self)
        self.scanner_view = ScannerView(self)
        self.console_view = ConsoleView(self)

    def init_navigation(self):
        """初始化 Fluent 侧边栏导航"""
        self.addSubInterface(self.dashboard_view, FluentIcon.SPEED_HIGH, "状态大盘")
        self.addSubInterface(self.injector_view, FluentIcon.GLOBE, "客户端注入")
        self.addSubInterface(self.sandbox_view, FluentIcon.CHEVRON_RIGHT_MED, "脱机沙箱")
        self.addSubInterface(self.extractor_view, FluentIcon.DOWNLOAD, "资产提取")
        self.addSubInterface(self.scanner_view, FluentIcon.SEARCH, "代码审计")
        self.addSubInterface(self.console_view, FluentIcon.COMMAND_PROMPT, "实时终端")

        # 底部导航项
        self.navigationInterface.addItem(
            routeKey="github",
            icon=FluentIcon.GITHUB,
            text="GitHub 仓库",
            onClick=self.open_github,
            selectable=False,
            position=NavigationItemPosition.BOTTOM
        )
        self.navigationInterface.addItem(
            routeKey="sponsor",
            icon=FluentIcon.HEART,
            text="赞助支持",
            onClick=self.show_sponsor,
            selectable=False,
            position=NavigationItemPosition.BOTTOM
        )

    def init_window(self):
        """初始化窗口属性"""
        self.resize(1180, 780)
        self.setMinimumSize(960, 640)
        
        # 居中屏幕
        screen = QApplication.primaryScreen().geometry()
        self.move(
            (screen.width() - self.width()) // 2,
            (screen.height() - self.height()) // 2
        )

    def open_github(self):
        import webbrowser
        webbrowser.open("https://github.com/xuange520/WeChat-H5-DevTools")

    def show_sponsor(self):
        InfoBar.info(
            title="感谢支持开源",
            content="欢迎在 GitHub 关注本项目并 Star！商务交流或疑难排障请联系微信: Sleep_Plan",
            parent=self,
            position=InfoBarPosition.BOTTOM_RIGHT,
            duration=4000
        )

    def resizeEvent(self, event):
        """防抖处理 (Rule 28)"""
        super().resizeEvent(event)
        if hasattr(self, '_resize_timer') and self._resize_timer is not None:
            self._resize_timer.start()

def launch_gui():
    """GUI 启动主函数"""
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    launch_gui()
