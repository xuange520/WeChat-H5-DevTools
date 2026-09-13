import os
import sys
import time
from pathlib import Path
from typing import Optional

try:
    import frida
except ImportError:
    frida = None

from ..utils.logger import log_info, log_warn, log_error, log_step
from .wechat_finder import WeChatFinder

class ProcessHooker:
    """微信进程注入管理器"""

    def __init__(self):
        self.finder = WeChatFinder()

    def launch_and_hook(self, custom_wechat_path: Optional[str] = None) -> bool:
        if not frida:
            log_error("未检测到 frida 依赖，请先执行: pip install frida")
            return False

        wechat_exe = Path(custom_wechat_path) if custom_wechat_path else self.finder.get_wechat_path()
        if not wechat_exe or not wechat_exe.exists():
            log_error("未能自动定位到微信可执行文件，请使用 --path 参数指定微信路径 (如: Weixin.exe)")
            return False

        # 检查是否已有微信进程在运行
        import psutil
        running_wechat = [p for p in psutil.process_iter(['pid', 'name']) if p.info['name'] in ['WeChat.exe', 'Weixin.exe', 'WeChatAppEx.exe']]
        if running_wechat:
            log_warn(f"检测到当前已有 {len(running_wechat)} 个微信相关进程正在运行。")
            log_step("正在自动终止旧微信进程以确保 Hook 探针能够冷启动挂载...")
            for p in running_wechat:
                try:
                    p.kill()
                except Exception:
                    pass
            time.sleep(1)

        log_info(f"匹配到微信主执行文件: {wechat_exe}")
        log_step("正在通过 Frida 调试引擎 Spawn 启动微信主进程...")

        try:
            device = frida.get_local_device()
            pid = device.spawn(str(wechat_exe))
            log_info(f"已创建微信挂起进程 PID: {pid}")

            # 加载 hook 脚本
            hook_js_path = Path(__file__).parent / "scripts" / "hook_inapp.js"
            with open(hook_js_path, "r", encoding="utf-8") as f:
                hook_code = f.read()

            session = device.attach(pid)
            script = session.create_script(hook_code)

            def on_message(message, data):
                if message.get("type") == "send":
                    log_info(message.get("payload", ""))
                elif message.get("type") == "error":
                    log_warn(f"Frida 告警: {message.get('description', '')}")

            script.on("message", on_message)
            script.load()

            log_step("恢复微信进程执行...")
            device.resume(pid)

            log_step("正在等待微信子进程完成初始化与参数挂载 (等待 6 秒)...")
            time.sleep(6)

            session.detach()
            log_info("注入完成！微信内置浏览器已处于开发者调试就绪状态。")
            return True

        except Exception as e:
            log_error(f"注入过程中发生异常: {e}")
            return False
