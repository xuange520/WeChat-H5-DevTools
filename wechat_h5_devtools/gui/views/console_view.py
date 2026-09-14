# -*- coding: utf-8 -*-
from datetime import datetime
from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from PySide6.QtGui import QTextCursor, QColor
from qfluentwidgets import (
    TitleLabel, CaptionLabel, CardWidget, PushButton, TextEdit,
    SwitchButton, FluentIcon, InfoBar
)
from ..common.signals import bridge_signals

class ConsoleView(QWidget):
    """实时终端与调试日志流视图"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ConsoleView")
        self.init_ui()
        bridge_signals.log_emitted.connect(self.append_log)

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(36, 28, 36, 28)
        layout.setSpacing(16)

        header = QVBoxLayout()
        header.setSpacing(4)
        title = TitleLabel("实时交互控制台 (Live Console)")
        desc = CaptionLabel("底层 Frida 挂载流、透明代理请求日志、Webpack 抓取与异常告警跟踪")
        header.addWidget(title)
        header.addWidget(desc)
        layout.addLayout(header)

        # 操作工具栏
        tool_bar = QHBoxLayout()
        self.clear_btn = PushButton(FluentIcon.DELETE, "清空控制台", self)
        self.clear_btn.clicked.connect(self.clear_log)
        self.copy_btn = PushButton(FluentIcon.COPY, "复制全部日志", self)
        self.copy_btn.clicked.connect(self.copy_log)
        self.scroll_switch = SwitchButton(self)
        self.scroll_switch.setOnText("自动滚屏")
        self.scroll_switch.setOffText("固定视图")
        self.scroll_switch.setChecked(True)

        tool_bar.addWidget(self.clear_btn)
        tool_bar.addWidget(self.copy_btn)
        tool_bar.addSpacing(16)
        tool_bar.addWidget(self.scroll_switch)
        tool_bar.addStretch()
        layout.addLayout(tool_bar)

        # 终端黑色卡片
        term_card = CardWidget(self)
        t_layout = QVBoxLayout(term_card)
        t_layout.setContentsMargins(12, 12, 12, 12)

        self.log_text = TextEdit(self)
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #121314;
                color: #e0e0e0;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 13px;
                border: none;
            }
        """)
        t_layout.addWidget(self.log_text)
        layout.addWidget(term_card)

        # 初始问候语
        self.append_log("INFO", "WeChat-H5-DevTools 现代 Fluent Design 控制台已就绪")
        self.append_log("PASS", "所有核心驱动引擎已链接: Frida 17+ / Proxy 8899 / Stealth Sandbox")

    @Slot(str, str)
    def append_log(self, level: str, text: str):
        now = datetime.now().strftime("%H:%M:%S")
        color = "#e0e0e0"
        if level == "INFO":
            color = "#1890ff"
        elif level == "PASS" or level == "SUCCESS":
            color = "#52c41a"
        elif level == "WARN":
            color = "#faad14"
        elif level == "ERROR":
            color = "#ff4d4f"

        formatted = f'<span style="color: #666666;">[{now}]</span> <b style="color: {color};">[{level}]</b> <span style="color: #dddddd;">{text}</span><br>'
        self.log_text.append(formatted)

        if self.scroll_switch.isChecked():
            cursor = self.log_text.textCursor()
            cursor.movePosition(QTextCursor.End)
            self.log_text.setTextCursor(cursor)

    def clear_log(self):
        self.log_text.clear()

    def copy_log(self):
        self.log_text.selectAll()
        self.log_text.copy()
        cursor = self.log_text.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.log_text.setTextCursor(cursor)
        InfoBar.info("已复制", "终端日志已复制至剪贴板", parent=self)
