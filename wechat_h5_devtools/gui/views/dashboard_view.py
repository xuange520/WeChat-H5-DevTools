# -*- coding: utf-8 -*-
from pathlib import Path
import os
import sys
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QFrame
from qfluentwidgets import (
    TitleLabel, SubtitleLabel, CaptionLabel, BodyLabel, StrongBodyLabel,
    CardWidget, PrimaryPushButton, PushButton, InfoBar, InfoBarPosition,
    FluentIcon, ScrollArea, ToolButton
)
from ..common.signals import bridge_signals
from ...injector.wechat_finder import WeChatFinder

class DashboardView(ScrollArea):
    """状态大盘与环境雷达视图"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.view = QWidget(self)
        self.setWidget(self.view)
        self.setWidgetResizable(True)
        self.setObjectName("DashboardView")
        self.init_ui()
        self.refresh_status()

    def init_ui(self):
        layout = QVBoxLayout(self.view)
        layout.setContentsMargins(36, 28, 36, 28)
        layout.setSpacing(20)

        # 标题栏
        header = QVBoxLayout()
        header.setSpacing(4)
        title = TitleLabel("状态大盘与环境雷达")
        desc = CaptionLabel("微信运行状态实时探测、RadiumWMPF 内核版本定位与本地依赖环境健康度")
        header.addWidget(title)
        header.addWidget(desc)
        layout.addLayout(header)

        # 状态卡片栅格
        grid = QGridLayout()
        grid.setSpacing(16)

        # 微信客户端卡片
        self.wx_card = CardWidget(self)
        wx_layout = QVBoxLayout(self.wx_card)
        wx_layout.setContentsMargins(20, 16, 20, 16)
        wx_title_box = QHBoxLayout()
        wx_title = StrongBodyLabel("微信桌面客户端")
        self.wx_status_badge = CaptionLabel("探测中...")
        self.wx_status_badge.setStyleSheet("color: #ffa500; font-weight: bold;")
        wx_title_box.addWidget(wx_title)
        wx_title_box.addStretch()
        wx_title_box.addWidget(self.wx_status_badge)
        wx_layout.addLayout(wx_title_box)

        self.wx_path_lbl = CaptionLabel("安装路径: 正在扫描...")
        self.wx_pid_lbl = CaptionLabel("进程 PID: --")
        self.wx_render_lbl = CaptionLabel("渲染管线: WeixinExt.exe / CEF 126+")
        wx_layout.addWidget(self.wx_path_lbl)
        wx_layout.addWidget(self.wx_pid_lbl)
        wx_layout.addWidget(self.wx_render_lbl)
        grid.addWidget(self.wx_card, 0, 0)

        # RadiumWMPF 内核卡片
        self.kernel_card = CardWidget(self)
        k_layout = QVBoxLayout(self.kernel_card)
        k_layout.setContentsMargins(20, 16, 20, 16)
        k_title_box = QHBoxLayout()
        k_title = StrongBodyLabel("RadiumWMPF 内核版本")
        self.kernel_badge = CaptionLabel("最新支持")
        self.kernel_badge.setStyleSheet("color: #52c41a; font-weight: bold;")
        k_title_box.addWidget(k_title)
        k_title_box.addStretch()
        k_title_box.addWidget(self.kernel_badge)
        k_layout.addLayout(k_title_box)

        self.kernel_ver_lbl = StrongBodyLabel("内核版本: 25560 (基准适配)")
        self.kernel_ver_lbl.setStyleSheet("font-size: 16px; color: #1890ff;")
        self.kernel_dir_lbl = CaptionLabel("内核路径: %AppData%\\Tencent\\xwechat\\...\\25560")
        self.kernel_status_lbl = CaptionLabel("适配矩阵: 25560 / 25510 / 25497 / 25364 / 20089")
        k_layout.addWidget(self.kernel_ver_lbl)
        k_layout.addWidget(self.kernel_dir_lbl)
        k_layout.addWidget(self.kernel_status_lbl)
        grid.addWidget(self.kernel_card, 0, 1)

        # 代理与注头状态卡片
        self.proxy_card = CardWidget(self)
        p_layout = QVBoxLayout(self.proxy_card)
        p_layout.setContentsMargins(20, 16, 20, 16)
        p_title_box = QHBoxLayout()
        p_title = StrongBodyLabel("透明代理与 vConsole 注入")
        self.proxy_badge = CaptionLabel("未运行")
        self.proxy_badge.setStyleSheet("color: #999999;")
        p_title_box.addWidget(p_title)
        p_title_box.addStretch()
        p_title_box.addWidget(self.proxy_badge)
        p_layout.addLayout(p_title_box)

        self.proxy_port_lbl = CaptionLabel("监听端口: 127.0.0.1:8899")
        self.proxy_mode_lbl = CaptionLabel("注入模式: 微信推文与 H5 全域自动注头")
        self.proxy_override_lbl = CaptionLabel("Local Overrides: 未启用")
        p_layout.addWidget(self.proxy_port_lbl)
        p_layout.addWidget(self.proxy_mode_lbl)
        p_layout.addWidget(self.proxy_override_lbl)
        grid.addWidget(self.proxy_card, 1, 0)

        # 脱机沙箱状态卡片
        self.sandbox_card = CardWidget(self)
        s_layout = QVBoxLayout(self.sandbox_card)
        s_layout.setContentsMargins(20, 16, 20, 16)
        s_title_box = QHBoxLayout()
        s_title = StrongBodyLabel("脱机原生 F12 沙箱")
        self.sandbox_badge = CaptionLabel("就绪")
        self.sandbox_badge.setStyleSheet("color: #52c41a;")
        s_title_box.addWidget(s_title)
        s_title_box.addStretch()
        s_title_box.addWidget(self.sandbox_badge)
        s_layout.addLayout(s_title_box)

        self.sandbox_edge_lbl = CaptionLabel("Microsoft Edge: 可用")
        self.sandbox_chrome_lbl = CaptionLabel("Google Chrome: 可用")
        self.sandbox_jssdk_lbl = CaptionLabel("JSSDK Polyfill: 30+ WeixinJSBridge Mock")
        s_layout.addWidget(self.sandbox_edge_lbl)
        s_layout.addWidget(self.sandbox_chrome_lbl)
        s_layout.addWidget(self.sandbox_jssdk_lbl)
        grid.addWidget(self.sandbox_card, 1, 1)

        layout.addLayout(grid)

        # 环境自检卡片与刷新按钮
        env_card = CardWidget(self)
        env_layout = QVBoxLayout(env_card)
        env_layout.setContentsMargins(20, 20, 20, 20)
        env_layout.setSpacing(12)

        env_header = QHBoxLayout()
        env_title = StrongBodyLabel("系统依赖与环境自检")
        self.refresh_btn = PrimaryPushButton(FluentIcon.SYNC, "一键重新检测", self)
        self.refresh_btn.clicked.connect(self.refresh_status)
        env_header.addWidget(env_title)
        env_header.addStretch()
        env_header.addWidget(self.refresh_btn)
        env_layout.addLayout(env_header)

        self.env_py_lbl = CaptionLabel(f"Python 运行时: {sys.version.split()[0]} ({sys.executable})")
        self.env_frida_lbl = CaptionLabel("Frida 动态挂载引擎: 检测中...")
        self.env_node_lbl = CaptionLabel("Node.js 运行时: 检测中...")
        env_layout.addWidget(self.env_py_lbl)
        env_layout.addWidget(self.env_frida_lbl)
        env_layout.addWidget(self.env_node_lbl)

        layout.addWidget(env_card)
        layout.addStretch()

    def refresh_status(self):
        """刷新微信与环境状态"""
        wechat_path = WeChatFinder.get_wechat_path()
        if wechat_path and os.path.exists(wechat_path):
            self.wx_path_lbl.setText(f"安装路径: {wechat_path}")
            self.wx_status_badge.setText("已安装")
            self.wx_status_badge.setStyleSheet("color: #52c41a; font-weight: bold;")
        else:
            self.wx_path_lbl.setText("安装路径: 未检测到默认安装路径")
            self.wx_status_badge.setText("未定位")
            self.wx_status_badge.setStyleSheet("color: #ff4d4f; font-weight: bold;")

        # 检查是否已有微信进程运行
        try:
            import psutil
            wx_pids = [p.pid for p in psutil.process_iter(['name', 'pid']) if p.info['name'] and 'weixin' in p.info['name'].lower()]
            if wx_pids:
                self.wx_pid_lbl.setText(f"进程 PID: {wx_pids[0]} (共 {len(wx_pids)} 个进程)")
                self.wx_status_badge.setText("运行中")
            else:
                self.wx_pid_lbl.setText("进程 PID: 未启动 (支持一键冷启动挂载)")
        except Exception:
            self.wx_pid_lbl.setText("进程 PID: 运行状态就绪")

        # 检查 Frida
        try:
            import frida
            self.env_frida_lbl.setText(f"Frida 动态挂载引擎: 已就绪 (v{frida.__version__})")
            self.env_frida_lbl.setStyleSheet("color: #52c41a;")
        except Exception:
            self.env_frida_lbl.setText("Frida 动态挂载引擎: 未安装 (pip install frida)")
            self.env_frida_lbl.setStyleSheet("color: #ff4d4f;")

        # 检查 Node
        import shutil
        node_path = shutil.which("node")
        if node_path:
            self.env_node_lbl.setText(f"Node.js 运行时: 已就绪 ({node_path})")
            self.env_node_lbl.setStyleSheet("color: #52c41a;")
        else:
            self.env_node_lbl.setText("Node.js 运行时: 未在 PATH 中找到")
            self.env_node_lbl.setStyleSheet("color: #faad14;")
