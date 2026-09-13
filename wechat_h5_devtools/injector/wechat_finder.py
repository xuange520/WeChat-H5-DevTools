import os
import sys
import winreg
from pathlib import Path
from typing import Optional

class WeChatFinder:
    """智能微信安装路径自适应定位器 (支持 3.x / 4.x / 多盘符)"""

    @staticmethod
    def get_wechat_path() -> Optional[Path]:
        # 0. 优先从当前正在运行的微信进程中直接获取真实物理路径
        try:
            import psutil
            for p in psutil.process_iter(['name', 'exe']):
                if p.info['name'] in ['WeChat.exe', 'Weixin.exe'] and p.info['exe']:
                    cand = Path(p.info['exe'])
                    if cand.exists() and cand.is_file():
                        return cand
        except Exception:
            pass

        # 1. 扫描已知常见安装路径
        known_paths = [
            Path(r"D:\Software\WeChat\Weixin\Weixin.exe"),
            Path(r"D:\Software\WeChat\WeChat.exe"),
            Path(r"C:\Program Files\Tencent\Weixin\Weixin.exe"),
            Path(r"C:\Program Files (x86)\Tencent\WeChat\WeChat.exe"),
            Path(r"C:\Program Files\Tencent\WeChat\WeChat.exe"),
            Path(os.path.expandvars(r"%LOCALAPPDATA%\Programs\Tencent\Weixin\Weixin.exe")),
            Path(os.path.expandvars(r"%APPDATA%\Tencent\WeChat\WeChat.exe")),
        ]

        for p in known_paths:
            if p.exists() and p.is_file():
                return p

        # 2. 尝试从 Windows 注册表读取
        if sys.platform == "win32":
            registry_keys = [
                (winreg.HKEY_CURRENT_USER, r"Software\Tencent\Weixin", "InstallPath"),
                (winreg.HKEY_CURRENT_USER, r"Software\Tencent\WeChat", "InstallPath"),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Tencent\WeChat", "InstallPath"),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Tencent\WeChat", "InstallPath"),
            ]

            for hkey, subkey, val_name in registry_keys:
                try:
                    with winreg.OpenKey(hkey, subkey) as key:
                        install_dir, _ = winreg.QueryValueEx(key, val_name)
                        if install_dir:
                            base = Path(install_dir)
                            for exe_name in ["Weixin.exe", "WeChat.exe"]:
                                cand = base / exe_name
                                if cand.exists():
                                    return cand
                                # 兼容嵌套子目录 Weixin/Weixin.exe
                                cand_sub = base / "Weixin" / exe_name
                                if cand_sub.exists():
                                    return cand_sub
                except Exception:
                    pass

        return None
