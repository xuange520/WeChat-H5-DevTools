# -*- coding: utf-8 -*-
from pathlib import Path
import threading
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QFileDialog, QMessageBox
)
from qfluentwidgets import (
    TitleLabel, SubtitleLabel, CaptionLabel, BodyLabel, StrongBodyLabel,
    CardWidget, PrimaryPushButton, PushButton, SwitchButton, LineEdit,
    SpinBox, ComboBox, InfoBar, InfoBarPosition, FluentIcon, ScrollArea
)
from ..common.signals import bridge_signals
from ...injector.proxy_injector import ProxyInjector
from ...injector.process_hooker import ProcessHooker

class InjectorView(ScrollArea):
    """客户端内置注入与代理视图"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.view = QWidget(self)
        self.setWidget(self.view)
        self.setWidgetResizable(True)
        self.setObjectName("InjectorView")
        self.proxy_thread = None
        self.proxy_running = False
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self.view)
        layout.setContentsMargins(36, 28, 36, 28)
        layout.setSpacing(20)

        # 标题
        header = QVBoxLayout()
        header.setSpacing(4)
        title = TitleLabel("微信内置注入与透明代理网关")
        desc = CaptionLabel("向微信 4.x 内置浏览器与公众号推文自动注入 vConsole 浮动绿标，支持本地代码实时映射 (Local Overrides)")
        header.addWidget(title)
        header.addWidget(desc)
        layout.addLayout(header)

        # 卡片 1: 透明代理服务控制
        proxy_card = CardWidget(self)
        p_layout = QVBoxLayout(proxy_card)
        p_layout.setContentsMargins(24, 20, 24, 20)
        p_layout.setSpacing(16)

        p_title_box = QHBoxLayout()
        p_title = StrongBodyLabel("透明代理注头服务")
        self.status_tag = CaptionLabel("未启动")
        self.status_tag.setStyleSheet("color: #999999; font-weight: bold;")
        p_title_box.addWidget(p_title)
        p_title_box.addStretch()
        p_title_box.addWidget(self.status_tag)
        p_layout.addLayout(p_title_box)

        # 端口与控制台选项
        settings_grid = QGridLayout()
        settings_grid.setSpacing(12)

        settings_grid.addWidget(BodyLabel("监听端口:"), 0, 0)
        self.port_spin = SpinBox(self)
        self.port_spin.setRange(1024, 65535)
        self.port_spin.setValue(8899)
        settings_grid.addWidget(self.port_spin, 0, 1)

        settings_grid.addWidget(BodyLabel("移动端控制台:"), 0, 2)
        self.console_combo = ComboBox(self)
        self.console_combo.addItems(["vConsole 3.15.1 (官方推荐绿球)", "Eruda 3.0 (全功能移动调试板)"])
        settings_grid.addWidget(self.console_combo, 0, 3)

        p_layout.addLayout(settings_grid)

        # 操作按钮
        btn_box = QHBoxLayout()
        self.start_proxy_btn = PrimaryPushButton(FluentIcon.PLAY, "启动代理网关并在推文中注入 vConsole", self)
        self.start_proxy_btn.clicked.connect(self.toggle_proxy)
        btn_box.addWidget(self.start_proxy_btn)
        p_layout.addLayout(btn_box)

        p_hint = CaptionLabel("说明：启动代理后，微信打开任意公众号推文或 H5，右下角将自动浮现 vConsole 绿球，点击展开完整控制台。")
        p_hint.setStyleSheet("color: #888888;")
        p_layout.addWidget(p_hint)

        layout.addWidget(proxy_card)

        # 卡片 2: Local Overrides 本地代码实时热重载
        override_card = CardWidget(self)
        o_layout = QVBoxLayout(override_card)
        o_layout.setContentsMargins(24, 20, 24, 20)
        o_layout.setSpacing(16)

        o_title_box = QHBoxLayout()
        o_title = StrongBodyLabel("【开发神器】Local Overrides 本地代码实时替换与热重载")
        self.override_switch = SwitchButton(self)
        self.override_switch.setOnText("已激活")
        self.override_switch.setOffText("未启用")
        o_title_box.addWidget(o_title)
        o_title_box.addStretch()
        o_title_box.addWidget(self.override_switch)
        o_layout.addLayout(o_title_box)

        o_desc = CaptionLabel("选择包含修改后 JS/CSS 脚本的本地文件夹。当微信访问线上同名资源时，代理网关将自动以本地文件秒级替换返回！")
        o_layout.addWidget(o_desc)

        path_box = QHBoxLayout()
        self.override_path_edit = LineEdit(self)
        self.override_path_edit.setPlaceholderText("请选择或输入本地待映射的脚本目录 (例如: D:/my_debug_js)")
        browse_btn = PushButton(FluentIcon.FOLDER, "浏览目录...", self)
        browse_btn.clicked.connect(self.choose_override_dir)
        path_box.addWidget(self.override_path_edit)
        path_box.addWidget(browse_btn)
        o_layout.addLayout(path_box)

        layout.addWidget(override_card)

        # 卡片 3: 微信客户端调试通道注入
        hook_card = CardWidget(self)
        h_layout = QVBoxLayout(hook_card)
        h_layout.setContentsMargins(24, 20, 24, 20)
        h_layout.setSpacing(16)

        h_title = StrongBodyLabel("微信主程序 DevTools 调试通道挂载")
        h_desc = CaptionLabel("通过 Frida 17+ 拦截 CreateProcessW，自动向微信渲染进程（WeixinExt.exe）注入 --enable-vconsole 等底层参数")
        h_layout.addWidget(h_title)
        h_layout.addWidget(h_desc)

        h_btn_box = QHBoxLayout()
        self.hook_cold_btn = PushButton(FluentIcon.POWER_BUTTON, "冷启动微信并注入调试通道", self)
        self.hook_cold_btn.clicked.connect(self.run_hook_cold)
        self.hook_attach_btn = PushButton(FluentIcon.LINK, "热挂载当前已运行的微信进程", self)
        self.hook_attach_btn.clicked.connect(self.run_hook_attach)
        h_btn_box.addWidget(self.hook_cold_btn)
        h_btn_box.addWidget(self.hook_attach_btn)
        h_layout.addLayout(h_btn_box)

        layout.addWidget(hook_card)
        layout.addStretch()

    def choose_override_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, "选择本地代码替换目录")
        if dir_path:
            self.override_path_edit.setText(dir_path)
            self.override_switch.setChecked(True)

    def toggle_proxy(self):
        if not self.proxy_running:
            port = self.port_spin.value()
            override_dir = self.override_path_edit.text() if self.override_switch.isChecked() else None
            
            # 后台线程启动代理
            def run_proxy():
                try:
                    injector = ProxyInjector(port=port, override_dir=override_dir)
                    injector.start()
                except Exception as e:
                    bridge_signals.log_emitted.emit("ERROR", f"代理启动异常: {e}")

            self.proxy_thread = threading.Thread(target=run_proxy, daemon=True)
            self.proxy_thread.start()
            self.proxy_running = True
            self.status_tag.setText("运行中 (127.0.0.1:8899)")
            self.status_tag.setStyleSheet("color: #52c41a; font-weight: bold;")
            self.start_proxy_btn.setText("停止透明代理服务")
            self.start_proxy_btn.setIcon(FluentIcon.PAUSE)
            bridge_signals.log_emitted.emit("INFO", f"透明代理已在 127.0.0.1:{port} 启动")
            InfoBar.success(
                title="代理服务已启动",
                content=f"微信推文与 H5 已全面激活 vConsole 自动注头！监听端口: {port}",
                parent=self,
                position=InfoBarPosition.TOP_RIGHT,
                duration=3000
            )
        else:
            self.proxy_running = False
            self.status_tag.setText("已停止")
            self.status_tag.setStyleSheet("color: #999999; font-weight: bold;")
            self.start_proxy_btn.setText("启动代理网关并在推文中注入 vConsole")
            self.start_proxy_btn.setIcon(FluentIcon.PLAY)
            bridge_signals.log_emitted.emit("INFO", "代理服务已停止")

    def run_hook_cold(self):
        bridge_signals.log_emitted.emit("INFO", "正在尝试冷启动微信并注入调试通道...")
        threading.Thread(target=lambda: ProcessHooker().launch_and_hook(), daemon=True).start()
        InfoBar.info("指令已下发", "正在拉起微信主程序并挂载 Frida 调试通道", parent=self)

    def run_hook_attach(self):
        bridge_signals.log_emitted.emit("INFO", "正在扫描已有微信主进程并热挂载...")
        threading.Thread(target=lambda: ProcessHooker().attach_running_wechat(), daemon=True).start()
        InfoBar.info("指令已下发", "正在热挂载正在运行的微信主进程与渲染管线", parent=self)
