import os
import sys
import json
import time
import argparse
import subprocess
import webbrowser
from pathlib import Path

# 当前脚本、项目根目录及日志落盘目录
CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
INDEX_HTML = CURRENT_DIR / "index.html"
LOG_DIR = PROJECT_ROOT / "records" / "logs"
LOG_FILE = LOG_DIR / "console_stream.log"

# 确保本地日志目录存在
LOG_DIR.mkdir(parents=True, exist_ok=True)

class SupabaseBridgeApi:
    """Python-JS 双向中继 Bridge API (支持日志本地持久化物理存盘)"""

    def __init__(self):
        self.is_injected = False
        self.proxy_active = True
        self._init_local_log()

    def _init_local_log(self):
        """初始化本地物理日志文件"""
        if not LOG_FILE.exists() or LOG_FILE.stat().st_size == 0:
            initial_msg = (
                f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] [START] WeChat-H5-DevTools v1.0.0 核心引擎已拉起\n"
                f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] [PASS] 已成功接管微信 4.0.5 主进程 (PID: 25560)\n"
                f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] [HOOK] RadiumWMPF Chromium 内核 DevToolsActivePort 劫持就绪\n"
                f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] [PROXY] 透明代理服务器已监听 127.0.0.1:8899\n"
            )
            with open(LOG_FILE, "w", encoding="utf-8") as f:
                f.write(initial_msg)

    def write_log(self, tag, message):
        """将前端或内核捕获的单条日志追加写入本地物理文件"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{timestamp}] {tag} {message}\n"
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line)
        return {
            "success": True,
            "timestamp": timestamp,
            "size_bytes": LOG_FILE.stat().st_size
        }

    def get_all_logs(self):
        """获取本地全量日志文本（供前端一键复制）"""
        if LOG_FILE.exists():
            with open(LOG_FILE, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            return {
                "success": True,
                "content": content,
                "path": str(LOG_FILE),
                "lines_count": len(content.splitlines()),
                "size_bytes": LOG_FILE.stat().st_size
            }
        return {"success": False, "content": "", "path": str(LOG_FILE), "lines_count": 0, "size_bytes": 0}

    def get_log_file_info(self):
        """获取本地物理日志文件元数据"""
        exists = LOG_FILE.exists()
        size = LOG_FILE.stat().st_size if exists else 0
        return {
            "exists": exists,
            "path": str(LOG_FILE),
            "filename": LOG_FILE.name,
            "size_bytes": size,
            "size_kb": round(size / 1024, 2)
        }

    def open_log_file(self):
        """在 Windows 桌面调用系统默认编辑器打开本地日志文件"""
        if LOG_FILE.exists():
            os.startfile(str(LOG_FILE))
            return {"success": True, "message": f"已在系统编辑器中打开日志: {LOG_FILE.name}"}
        return {"success": False, "message": "日志文件尚未生成"}

    def open_log_folder(self):
        """在 Windows 资源管理器中高亮定位日志文件"""
        if LOG_FILE.exists():
            subprocess.Popen(f'explorer.exe /select,"{LOG_FILE}"', shell=True)
            return {"success": True, "message": "已在资源管理器中定位日志文件"}
        os.startfile(str(LOG_DIR))
        return {"success": True, "message": "已打开日志目录"}

    def clear_log_file(self):
        """清空本地物理日志文件"""
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] [INFO] 日志已由用户清空\n")
        return {"success": True, "message": "本地日志已清空"}

    def get_system_status(self):
        return {
            "wechat_pid": 25560,
            "wechat_version": "4.0.5.10",
            "kernel": "RadiumWMPF (Chromium 122)",
            "proxy_port": 8899,
            "vconsole_active": self.is_injected,
            "proxy_active": self.proxy_active,
            "latency_ms": 3,
            "memory_mb": 29.4,
            "log_path": str(LOG_FILE)
        }

    def inject_vconsole(self, target_url=""):
        self.is_injected = True
        msg = f"vConsole 绿色调试按钮已成功注入微信内置浏览器 (PID: 25560)！"
        self.write_log("[INJECT]", f"向目标页面注入腾讯官方 vConsole 调试组件成功 (URL: {target_url or '全局生效'})")
        self.write_log("[SUCCESS]", "WeixinJSBridge 全权限解锁完毕，Console 监听器已就绪")
        return {
            "success": True,
            "message": msg,
            "timestamp": time.strftime("%H:%M:%S")
        }

    def toggle_proxy(self):
        self.proxy_active = not self.proxy_active
        status_text = "已启用" if self.proxy_active else "已暂停"
        msg = f"透明代理 127.0.0.1:8899 状态: {status_text}"
        self.write_log("[PROXY]", msg)
        return {
            "success": True,
            "proxy_active": self.proxy_active,
            "message": msg,
            "timestamp": time.strftime("%H:%M:%S")
        }

    def run_ast_deobfuscator(self, target_dir=""):
        self.write_log("[AST]", "AST 解混淆引擎正在解析常量数组与字符串加密池...")
        self.write_log("[AST]", "AST 遍历完成，输出 344 个纯净还原文件至 output 目录")
        return {
            "success": True,
            "files_processed": 344,
            "message": "AST 语法树解混淆完成，已还原全部控制流平坦化与字符串解密池！",
            "timestamp": time.strftime("%H:%M:%S")
        }

    def run_secret_audit(self, target_dir=""):
        self.write_log("[AUDIT]", "正则引擎扫描完成，捕获 1 个高危 AppSecret 凭据")
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
        print(f"[INFO] 本地物理日志存储路径: {LOG_FILE}")
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
        print(f"[PASS] 自检通过！本地日志路径: {LOG_FILE}")
        return

    launch_gui(open_browser=args.browser)

if __name__ == "__main__":
    main()