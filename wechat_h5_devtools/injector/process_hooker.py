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
        import threading

        running_weixin = [p for p in psutil.process_iter(['pid', 'name']) if p.info['name'] in ['WeChat.exe', 'Weixin.exe']]

        # 模式 1：热附加模式 (微信已在运行，免重新登录/无需杀主进程)
        if running_weixin:
            log_step(f"检测到微信主程序已在运行中 (发现 {len(running_weixin)} 个微信进程)！")
            log_info("正在执行高可靠多级级联热附加 (Weixin -> WeChatAppEx Master -> Renderers)...")

            sessions = {}
            lock = threading.Lock()

            def attach_target(pid: int, name: str) -> bool:
                with lock:
                    if pid in sessions:
                        return True
                try:
                    s = frida.attach(pid)
                    sc = s.create_script(hook_code)

                    def on_message(message, data, current_pid=pid, current_name=name):
                        if message.get("type") == "send":
                            log_info(f"[{current_name}:{current_pid}] {message.get('payload', '')}")
                        elif message.get("type") == "error":
                            log_warn(f"[{current_name}:{current_pid}] Frida 告警: {message.get('description', '')}")

                    sc.on("message", on_message)
                    sc.load()
                    with lock:
                        sessions[pid] = (s, sc, name)
                    log_info(f"成功注入调试通道 -> {name} (PID: {pid})")
                    return True
                except Exception as e:
                    return False

            # 步骤 1：必须先附加到 Weixin.exe 主进程！
            log_step("[1/3] 挂载微信主进程 CreateProcessW 拦截引擎...")
            attached_weixin = 0
            for p in running_weixin:
                if attach_target(p.info['pid'], p.info['name']):
                    attached_weixin += 1

            if attached_weixin == 0:
                log_error("热附加微信主程序失败，请尝试以管理员身份运行终端！")
                return False

            # 步骤 2：优雅终止旧的 WeChatAppEx 渲染器与 Broker，促使微信以新参数全新拉起
            running_renderers = [p for p in psutil.process_iter(['pid', 'name']) if p.info['name'] in ['WeChatAppEx.exe', 'WeixinExt.exe']]
            if running_renderers:
                log_step(f"[2/3] 正在重置 {len(running_renderers)} 个旧渲染器进程以装载最新调试参数...")
                for p in running_renderers:
                    try:
                        p.kill()
                    except Exception:
                        pass
                time.sleep(1.0)

            # 步骤 3：启动后台动态巡检线程，级联捕获新拉起的 WeChatAppEx Master 与 Renderers
            log_step("[3/3] 启动多级级联守护线程，自动挂载所有新衍生进程...")
            watcher_running = True

            def watcher_loop():
                while watcher_running:
                    try:
                        for p in psutil.process_iter(['pid', 'name']):
                            if p.info['name'] in ['WeChatAppEx.exe', 'WeixinExt.exe']:
                                pid = p.info['pid']
                                with lock:
                                    if pid not in sessions:
                                        attach_target(pid, p.info['name'])
                    except Exception:
                        pass
                    time.sleep(1.0)

            watcher_th = threading.Thread(target=watcher_loop, daemon=True)
            watcher_th.start()

            # 初次扫描新生成的 WeChatAppEx
            time.sleep(1.5)

            log_step("[PASS] [微信全局推文与内置浏览器 Hook 级联挂载完毕！]")
            log_info("调试指引 (微信 4.1.x 架构规范):")
            log_info("  • 【远程 CDP 调试】在 Chrome / Edge 浏览器访问 edge://inspect 或 chrome://inspect 直连调试目标网页。")
            log_info("  • 【内置 vConsole 悬浮球】另开终端运行 wx-h5 proxy，微信访问任意 H5/推文右下角即显示绿色 vConsole 按钮。")
            log_info("  • 【独立沙箱调试】运行 wx-h5 open <网址>，在自带满血 F12 + JSSDK Mock 的桌面沙箱中秒开调试。")
            log_info("提示: 保持本终端运行即可持续生效，按 Ctrl + C 可随时卸载退出。")

            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                log_warn("已收到中断信号，正在卸载 Hook 并退出...")
                watcher_running = False
                with lock:
                    for pid, (s, sc, n) in list(sessions.items()):
                        try:
                            s.detach()
                        except Exception:
                            pass
                    sessions.clear()
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
