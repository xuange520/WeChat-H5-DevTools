# -*- coding: utf-8 -*-
from pathlib import Path
import threading
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QFileDialog
from qfluentwidgets import (
    TitleLabel, SubtitleLabel, CaptionLabel, BodyLabel, StrongBodyLabel,
    CardWidget, PrimaryPushButton, PushButton, LineEdit, CheckBox,
    ProgressBar, InfoBar, InfoBarPosition, FluentIcon, ScrollArea
)
from ..common.signals import bridge_signals
from ...extractor.project_dumper import ProjectDumper

class ExtractorView(ScrollArea):
    """资产提取与全站分包递归抓取视图"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.view = QWidget(self)
        self.setWidget(self.view)
        self.setWidgetResizable(True)
        self.setObjectName("ExtractorView")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self.view)
        layout.setContentsMargins(36, 28, 36, 28)
        layout.setSpacing(20)

        header = QVBoxLayout()
        header.setSpacing(4)
        title = TitleLabel("全站源码逆向提取与分包抓取 (Asset Extractor)")
        desc = CaptionLabel("输入任意公众号 H5 链接，自动递归提取主包、所有异步 Webpack Chunk、CSS 及静态资产")
        header.addWidget(title)
        header.addWidget(desc)
        layout.addLayout(header)

        # 控制卡片
        main_card = CardWidget(self)
        m_layout = QVBoxLayout(main_card)
        m_layout.setContentsMargins(24, 20, 24, 20)
        m_layout.setSpacing(16)

        m_title = StrongBodyLabel("提取任务配置")
        m_layout.addWidget(m_title)

        url_box = QVBoxLayout()
        url_box.setSpacing(6)
        url_box.addWidget(BodyLabel("目标公众号网页 URL:"))
        self.target_url_edit = LineEdit(self)
        self.target_url_edit.setPlaceholderText("https://example.com/h5/index.html")
        self.target_url_edit.setClearButtonEnabled(True)
        url_box.addWidget(self.target_url_edit)
        m_layout.addLayout(url_box)

        path_box = QVBoxLayout()
        path_box.setSpacing(6)
        path_box.addWidget(BodyLabel("工程落盘保存目录:"))
        dir_sub = QHBoxLayout()
        self.output_path_edit = LineEdit(self)
        self.output_path_edit.setText(str(Path.cwd() / "output_h5_resources"))
        browse_btn = PushButton(FluentIcon.FOLDER, "选择输出目录...", self)
        browse_btn.clicked.connect(self.choose_output_dir)
        dir_sub.addWidget(self.output_path_edit)
        dir_sub.addWidget(browse_btn)
        path_box.addLayout(dir_sub)
        m_layout.addLayout(path_box)

        # 选项
        opt_box = QHBoxLayout()
        self.chk_deobfuscate = CheckBox("提取后自动进行 AST 语法树反混淆与模块解包", self)
        self.chk_deobfuscate.setChecked(True)
        self.chk_sourcemap = CheckBox("自动探测并还原 SourceMap (.vue / .ts)", self)
        self.chk_sourcemap.setChecked(True)
        opt_box.addWidget(self.chk_deobfuscate)
        opt_box.addWidget(self.chk_sourcemap)
        opt_box.addStretch()
        m_layout.addLayout(opt_box)

        # 进度条
        self.progress_bar = ProgressBar(self)
        self.progress_bar.setValue(0)
        m_layout.addWidget(self.progress_bar)

        # 按钮
        self.extract_btn = PrimaryPushButton(FluentIcon.DOWNLOAD, "开始全站分包递归提取与源码恢复", self)
        self.extract_btn.clicked.connect(self.start_extract)
        m_layout.addWidget(self.extract_btn)

        layout.addWidget(main_card)
        layout.addStretch()

    def choose_output_dir(self):
        d = QFileDialog.getExistingDirectory(self, "选择资源输出保存目录")
        if d:
            self.output_path_edit.setText(d)

    def start_extract(self):
        url = self.target_url_edit.text().strip()
        if not url:
            InfoBar.warning("请输入链接", "目标公众号 H5 链接不能为空", parent=self)
            return

        out_dir = self.output_path_edit.text().strip()
        do_deobf = self.chk_deobfuscate.isChecked()

        self.extract_btn.setEnabled(False)
        self.progress_bar.setValue(20)
        bridge_signals.log_emitted.emit("INFO", f"开始递归提取全站资源: {url} -> {out_dir}")

        def worker():
            try:
                dumper = ProjectDumper(output_dir=out_dir)
                dumper.dump_site(url=url, auto_deobfuscate=do_deobf)
                self.progress_bar.setValue(100)
                bridge_signals.log_emitted.emit("PASS", f"全站资源递归提取完毕，已保存在: {out_dir}")
            except Exception as e:
                bridge_signals.log_emitted.emit("ERROR", f"提取失败: {e}")
            finally:
                self.extract_btn.setEnabled(True)

        threading.Thread(target=worker, daemon=True).start()
        InfoBar.info("提取任务已启动", "正在递归探测 HTML 与异步 Webpack 分包，请关注控制台日志", parent=self)
