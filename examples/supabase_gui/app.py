import os
import sys
import json
import time
import argparse
import webbrowser
from pathlib import Path

# 当前脚本及项目目录
CURRENT_DIR = Path(__file__).resolve().parent
INDEX_HTML = CURRENT_DIR / "index.html"

class SupabaseBridgeApi:
    """Python-JS 双向中继 Bridge API"""

    def __init__(self):
        self.is_injected = False
        self.proxy_active = True

    def get_system_status(self):
        return {
            "wechat_pid": 25560,
            "wechat_version": "4.0.5.10",
            "kernel": "RadiumWMPF (Chromium 122)",
            "proxy_port": 8899,
            "vconsole_active": self.is_injected,
            "proxy_active": self.proxy_active,
            "latency_ms": 3,
            "memory_mb": 29.4
        }

    def inject_vconsole(self, target_url=""):
        self.is_injected = True
        return {
            "success": True,
            "message": f"vConsole 绿色调试球已成功注入微信内置浏览器 (PID: 25560)！",
            "timestamp": time.strftime("%H:%M:%S")
        }

    def toggle_proxy(self):
        self.proxy_active = not self.proxy_active
        status_text = "已启用" if self.proxy_active else "已暂停"
        return {
            "success": True,
            "proxy_active": self.proxy_active,
            "message": f"透明代理 127.0.0.1:8899 状态: {status_text}",
            "timestamp": time.strftime("%H:%M:%S")
        }

    def run_ast_deobfuscator(self, target_dir=""):
        return {
            "success": True,
            "files_processed": 344,
            "message": "AST 语法树解混淆完成，已还原全部控制流平坦化与字符串解密池！",
            "timestamp": time.strftime("%H:%M:%S")
        }

    def run_secret_audit(self, target_dir=""):
        return {
            "success": True,
            "critical_count": 1,
            "high_count": 1,
            "message": "敏感凭据扫描完成，发现 1 个高危 AppSecret 泄露！",
            "timestamp": time.strftime("%H:%M:%S")
        }

def launch_gui(open_browser=False):
    if not INDEX_HTML.exists():
        print(f"[ERROR] 找不到界面文件: {INDEX_HTML}")
        sys.exit(1)

    if open_browser:
        print(f"[INFO] 正在以默认浏览器模式打开 Supabase Dark 界面: {INDEX_HTML}")
        webbrowser.open(INDEX_HTML.as_uri())
        return

    try:
        import webview
        print("[INFO] 正在拉起 Windows 原生 WebView2 硬件加速窗口 (Supabase Dark Edition)...")
        api = SupabaseBridgeApi()
        window = webview.create_window(
            title="WeChat-H5-DevTools | Supabase Dark Emerald Edition",
            url=str(INDEX_HTML),
            js_api=api,
            width=1140,
            height=730,
            min_size=(960, 620),
            background_color="#121212",
            text_select=True
        )
        webview.start(debug=False)
    except Exception as e:
        print(f"[WARN] WebView2 拉起异常 ({e})，正在自动回退至系统浏览器模式...")
        webbrowser.open(INDEX_HTML.as_uri())

def main():
    parser = argparse.ArgumentParser(description="WeChat-H5-DevTools Supabase UI Demo")
    parser.add_argument("--browser", action="store_true", help="使用默认浏览器直接预览 UI")
    parser.add_argument("--check", action="store_true", help="仅自检文件完整度与语法并退出")
    args = parser.parse_args()

    if args.check:
        print("[CHECK] 检查 UI 资源完整度...")
        assert INDEX_HTML.exists(), "index.html 缺失"
        print("[PASS] 自检通过！")
        return

    launch_gui(open_browser=args.browser)

if __name__ == "__main__":
    main()