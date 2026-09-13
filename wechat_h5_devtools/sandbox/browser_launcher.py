import os
import sys
import subprocess
import shutil
from pathlib import Path
from typing import Optional

from ..utils.logger import log_info, log_warn, log_error, log_step
from .user_agents import get_wechat_ua

class BrowserLauncher:
    """脱机高保真微信沙箱浏览器拉起引擎"""

    def __init__(self, browser_type: str = "edge"):
        self.browser_type = browser_type.lower()

    def find_browser_exe(self) -> Optional[str]:
        if self.browser_type == "chrome":
            candidates = [
                shutil.which("chrome"),
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
                r"D:\Software\Chrome\chrome.exe"
            ]
        else:
            candidates = [
                shutil.which("msedge"),
                r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
                os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Edge\Application\msedge.exe")
            ]

        for cand in candidates:
            if cand and Path(cand).exists():
                return str(cand)
        return None

    def _build_mock_extension(self) -> Path:
        """生成自动注入 WeixinJSBridge & JSSDK 的轻量临时扩展"""
        ext_dir = Path(__file__).parent / "_runtime_extension"
        ext_dir.mkdir(parents=True, exist_ok=True)

        bridge_js = (Path(__file__).parent / "polyfills" / "weixin_bridge.js").read_text(encoding="utf-8")
        jssdk_js = (Path(__file__).parent / "polyfills" / "jssdk_mock.js").read_text(encoding="utf-8")
        
        injected_content = bridge_js + "\n\n" + jssdk_js
        (ext_dir / "inject.js").write_text(injected_content, encoding="utf-8")

        manifest = {
            "manifest_version": 3,
            "name": "WeChat-H5-DevTools Mock Extension",
            "version": "1.0.0",
            "content_scripts": [
                {
                    "matches": ["<all_urls>"],
                    "js": ["inject.js"],
                    "run_at": "document_start",
                    "world": "MAIN"
                }
            ]
        }
        import json
        (ext_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        return ext_dir

    def launch(self, target_url: str, platform_ua: str = "ios", open_devtools: bool = True) -> bool:
        browser_exe = self.find_browser_exe()
        if not browser_exe:
            log_error(f"未在系统中找到 {self.browser_type} 浏览器可执行文件！")
            return False

        ua = get_wechat_ua(platform_ua)
        log_info(f"正在拉起高保真微信沙箱 [{self.browser_type.upper()}]...")
        log_info(f"模拟终端平台: [bold cyan]{platform_ua.upper()} WeChat[/bold cyan]")
        log_info(f"目标访问 URL: {target_url}")

        # 自动生成 WeixinJSBridge & JSSDK 毫秒级自注入扩展
        ext_path = self._build_mock_extension()
        log_step(f"已动态挂载 JSSDK / WeixinJSBridge 自动注入扩展: {ext_path.name}")

        args = [
            browser_exe,
            f"--user-agent={ua}",
            f"--load-extension={ext_path}",
            "--disable-blink-features=AutomationControlled",
        ]

        if open_devtools:
            args.append("--auto-open-devtools-for-tabs")

        args.append(target_url)

        try:
            log_step("拉起独立浏览器进程并自动挂载满血 F12 控制台...")
            subprocess.Popen(args)
            log_info("浏览器已启动！页面已内置 WeixinJSBridge 挡板，您可以在 DevTools 中尽情调试。")
            return True
        except Exception as e:
            log_error(f"启动浏览器失败: {e}")
            return False
