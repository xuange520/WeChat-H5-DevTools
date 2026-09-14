# -*- coding: utf-8 -*-
from pathlib import Path
import threading
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QFileDialog
from qfluentwidgets import (
    TitleLabel, SubtitleLabel, CaptionLabel, BodyLabel, StrongBodyLabel,
    CardWidget, PrimaryPushButton, PushButton, LineEdit, TextEdit,
    InfoBar, InfoBarPosition, FluentIcon, ScrollArea
)
from ..common.signals import bridge_signals
from ...extractor.api_analyzer import APIAnalyzer

class ScannerView(ScrollArea):
    """接口路由清单与国密算法静态安全审计视图"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.view = QWidget(self)
        self.setWidget(self.view)
        self.setWidgetResizable(True)
        self.setObjectName("ScannerView")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self.view)
        layout.setContentsMargins(36, 28, 36, 28)
        layout.setSpacing(20)

        header = QVBoxLayout()
        header.setSpacing(4)
        title = TitleLabel("全域 API 路由与国密算法安全审计 (Security Scanner)")
        desc = CaptionLabel("深度静态扫描解混淆后的 JS 代码，识别后端 Base URLs、国密 SM2/3/4、RSA 算法与 RESTful 接口清单")
        header.addWidget(title)
        header.addWidget(desc)
        layout.addLayout(header)

        # 扫描配置卡片
        ctrl_card = CardWidget(self)
        c_layout = QVBoxLayout(ctrl_card)
        c_layout.setContentsMargins(24, 20, 24, 20)
        c_layout.setSpacing(16)

        c_title = StrongBodyLabel("审计目标工程选择")
        c_layout.addWidget(c_title)

        dir_box = QHBoxLayout()
        self.scan_dir_edit = LineEdit(self)
        self.scan_dir_edit.setText(str(Path.cwd() / "output_h5_resources"))
        browse_btn = PushButton(FluentIcon.FOLDER, "浏览目录...", self)
        browse_btn.clicked.connect(self.choose_scan_dir)
        dir_box.addWidget(self.scan_dir_edit)
        dir_box.addWidget(browse_btn)
        c_layout.addLayout(dir_box)

        btn_box = QHBoxLayout()
        self.start_scan_btn = PrimaryPushButton(FluentIcon.SEARCH, "一键执行静态深度代码审计", self)
        self.start_scan_btn.clicked.connect(self.start_scan)
        self.export_report_btn = PushButton(FluentIcon.DOCUMENT, "导出精美 Markdown 审计报告", self)
        self.export_report_btn.clicked.connect(self.export_report)
        btn_box.addWidget(self.start_scan_btn)
        btn_box.addWidget(self.export_report_btn)
        c_layout.addLayout(btn_box)

        layout.addWidget(ctrl_card)

        # 扫描结果展示卡片
        result_card = CardWidget(self)
        r_layout = QVBoxLayout(result_card)
        r_layout.setContentsMargins(24, 20, 24, 20)
        r_layout.setSpacing(12)

        r_title = StrongBodyLabel("静态审计大盘与高信噪比接口提纯")
        r_layout.addWidget(r_title)

        self.result_display = TextEdit(self)
        self.result_display.setReadOnly(True)
        self.result_display.setPlaceholderText("点击“一键执行静态深度代码审计”后，此处将呈现提取出的 Base URLs、国密特征与 API 路由清单...")
        self.result_display.setMinimumHeight(350)
        r_layout.addWidget(self.result_display)

        layout.addWidget(result_card)
        layout.addStretch()

    def choose_scan_dir(self):
        d = QFileDialog.getExistingDirectory(self, "选择待审计的 JS/源码目录")
        if d:
            self.scan_dir_edit.setText(d)

    def start_scan(self):
        target = self.scan_dir_edit.text().strip()
        if not target or not Path(target).exists():
            InfoBar.warning("目录不存在", "请指定有效的前端源码或解混淆目录", parent=self)
            return

        self.start_scan_btn.setEnabled(False)
        self.result_display.setPlainText("正在进行 AST 静态特征扫描与接口提取，请稍候...")
        bridge_signals.log_emitted.emit("INFO", f"启动静态安全审计: {target}")

        def worker():
            try:
                analyzer = APIAnalyzer(target_path=target)
                report_text = analyzer.generate_report()
                self.result_display.setPlainText(report_text)
                bridge_signals.log_emitted.emit("PASS", f"静态审计完成，已提纯全部 API 路由与密码学特征")
            except Exception as e:
                self.result_display.setPlainText(f"扫描异常: {e}")
                bridge_signals.log_emitted.emit("ERROR", f"审计失败: {e}")
            finally:
                self.start_scan_btn.setEnabled(True)

        threading.Thread(target=worker, daemon=True).start()

    def export_report(self):
        content = self.result_display.toPlainText()
        if not content:
            InfoBar.warning("暂无内容", "请先执行扫描后再导出报告", parent=self)
            return
        save_path, _ = QFileDialog.getSaveFileName(self, "保存审计报告", "audit_report.md", "Markdown (*.md)")
        if save_path:
            Path(save_path).write_text(content, encoding="utf-8")
            InfoBar.success("导出成功", f"审计报告已保存至: {save_path}", parent=self)
