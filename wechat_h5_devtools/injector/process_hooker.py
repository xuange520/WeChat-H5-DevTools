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

        hook_js_path = Path(__file__).parent / "scripts" / "hook_inapp.js"
        with open(hook_js_path, "r", encoding="utf-8") as f:
            hook_code = f.read()

        import psutil
        running_weixin = [p for p in psutil.process_iter(['pid', 'name']) if p.info['name'] in ['WeChat.exe', 'Weixin.exe']]

        # 模式 1：热附加模式 (微信已在运行，不退出微信，不影响用户正常登录与聊天！)
        if running_weixin:
            log_step(f"检测到微信主程序已在运行中 (发现 {len(running_weixin)} 个微信进程)！")
            log_info("正在执行智能热附加 (免重新登录/无需杀主进程)...")

            # 仅清理旧的渲染子进程 WeChatAppEx，以便微信下次点击推文时以新参数拉起全新的渲染器
            running_renderers = [p for p in psutil.process_iter(['pid', 'name']) if p.info['name'] in ['WeChatAppEx.exe', 'WeixinExt.exe']]
            if running_renderers:
                log_step(f"正在重置 {len(running_renderers)} 个旧渲染子进程以激活最新调试参数...")
                for p in running_renderers:
                    try:
                        p.kill()
                    except Exception:
                        pass
                time.sleep(0.5)

            sessions = []
            for p in running_weixin:
                pid = p.info['pid']
                try:
                    session = frida.attach(pid)
                    script = session.create_script(hook_code)

                    def on_message(message, data, current_pid=pid):
                        if message.get("type") == "send":
                            log_info(f"[PID {current_pid}] {message.get('payload', '')}")
                        elif message.get("type") == "error":
                            log_warn(f"Frida 告警: {message.get('description', '')}")

                    script.on("message", on_message)
                    script.load()
                    sessions.append(session)
                except Exception:
                    pass

            if not sessions:
                log_error("热附加微信进程失败，请尝试以管理员身份运行终端！")
                return False

            log_step("[PASS] [微信全局推文与内置浏览器 Hook 挂载完毕！]")
            log_info("现在长官无需输入任何网址，只要在微信里点击任意公众号推文或网页，系统将全自动拦截并强制注入 vConsole！")
            log_info("提示: 保持本终端运行即可生效，按 Ctrl + C 可随时退出挂载。")

            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                log_warn("已收到中断信号，正在卸载 Hook 并退出...")
                for s in sessions:
                    try:
                        s.detach()
                    except Exception:
                        pass
                return True

        # 模式 2：冷启动模式 (微信未运行，自动拉起并注入)
        wechat_exe = Path(custom_wechat_path) if custom_wechat_path else self.finder.get_wechat_path()
        if not wechat_exe or not wechat_exe.exists():
            log_error("未能自动定位到微信可执行文件，请使用 --path 参数指定微信路径 (如: Weixin.exe)")
            return False

        log_info(f"匹配到微信主执行文件: {wechat_exe}")
        log_step("正在通过 Frida 调试引擎 Spawn 启动微信主进程...")

        try:
            device = frida.get_local_device()
            pid = device.spawn(str(wechat_exe))
            log_info(f"已创建微信挂起进程 PID: {pid}")

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

            log_step("[PASS] [微信全局推文与内置浏览器 Hook 挂载完毕！]")
            log_info("现在长官无需输入任何网址，只要在微信里点击任意公众号推文或网页，系统将全自动拦截并强制注入 vConsole！")
            log_info("提示: 保持本终端运行即可生效，按 Ctrl + C 可随时退出挂载。")

            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                log_warn("已收到中断信号，正在卸载 Hook 并退出...")
                session.detach()
                return True

        except Exception as e:
            log_error(f"注入过程中发生异常: {e}")
            return False
