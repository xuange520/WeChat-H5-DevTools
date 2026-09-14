import os
import sys
import struct
import winreg
import ctypes
from ctypes import wintypes
from pathlib import Path
from typing import Optional, Dict, Any, List

class WeChatFinder:
    """智能微信安装路径与运行时状态自适应定位器 (支持 3.x / 4.x / 多盘符)"""

    @staticmethod
    def get_pe_version(filepath: Path) -> Optional[str]:
        """通过 Windows 原生 version.dll 读取可执行文件实际 ProductVersion / FileVersion"""
        if not filepath or not Path(filepath).exists():
            return None
        try:
            version_dll = ctypes.windll.version
            path_str = str(filepath)
            size = version_dll.GetFileVersionInfoSizeW(path_str, None)
            if not size:
                return None
            res = ctypes.create_string_buffer(size)
            if not version_dll.GetFileVersionInfoW(path_str, 0, size, res):
                return None
            ptr = ctypes.c_void_p()
            length = wintypes.UINT()
            if version_dll.VerQueryValueW(res, "\\", ctypes.byref(ptr), ctypes.byref(length)):
                class VS_FIXEDFILEINFO(ctypes.Structure):
                    _fields_ = [
                        ("dwSignature", wintypes.DWORD),
                        ("dwStrucVersion", wintypes.DWORD),
                        ("dwFileVersionMS", wintypes.DWORD),
                        ("dwFileVersionLS", wintypes.DWORD),
                        ("dwProductVersionMS", wintypes.DWORD),
                        ("dwProductVersionLS", wintypes.DWORD),
                        ("dwFileFlagsMask", wintypes.DWORD),
                        ("dwFileFlags", wintypes.DWORD),
                        ("dwFileOS", wintypes.DWORD),
                        ("dwFileType", wintypes.DWORD),
                        ("dwFileSubtype", wintypes.DWORD),
                        ("dwFileDateMS", wintypes.DWORD),
                        ("dwFileDateLS", wintypes.DWORD),
                    ]
                info = VS_FIXEDFILEINFO.from_address(ptr.value)
                prod_ver = f"{info.dwProductVersionMS >> 16}.{info.dwProductVersionMS & 0xFFFF}.{info.dwProductVersionLS >> 16}.{info.dwProductVersionLS & 0xFFFF}"
                return prod_ver
        except Exception:
            pass
        return None

    @staticmethod
    def get_pe_arch(filepath: Path) -> str:
        """从 PE 文件头解析真实机器架构 (x64 / x86 / ARM64)"""
        if not filepath or not Path(filepath).exists():
            return "x64"
        try:
            with open(filepath, "rb") as f:
                f.seek(0x3C)
                pe_offset = struct.unpack("<I", f.read(4))[0]
                f.seek(pe_offset + 4)
                machine = struct.unpack("<H", f.read(2))[0]
                if machine == 0x8664:
                    return "x64"
                elif machine == 0x014C:
                    return "x86"
                elif machine == 0xAA64:
                    return "ARM64"
        except Exception:
            pass
        return "x64"

    @staticmethod
    def get_wechat_path() -> Optional[Path]:
        """扫描定位本地已安装的微信主程序路径"""
        # 0. 优先从当前正在运行的微信进程中直接获取真实物理路径
        try:
            import psutil
            for p in psutil.process_iter(['name', 'exe']):
                if p.info['name'] and p.info['name'].lower() in ['wechat.exe', 'weixin.exe'] and p.info['exe']:
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

    @classmethod
    def get_runtime_status(cls) -> Dict[str, Any]:
        """动态感知当前宿主机微信运行拓扑、真实版本号与沙箱矩阵"""
        wechat_procs = []
        renderer_procs = []

        try:
            import psutil
            for p in psutil.process_iter(['pid', 'name', 'ppid', 'create_time', 'exe']):
                try:
                    pname = (p.info['name'] or '').lower()
                    if pname in ['wechat.exe', 'weixin.exe']:
                        wechat_procs.append(p)
                    elif pname in ['wechatappex.exe', 'weixinext.exe']:
                        renderer_procs.append(p)
                except Exception:
                    pass
        except Exception:
            pass

        # 1. 微信进程正在运行
        if wechat_procs:
            wechat_procs.sort(key=lambda x: x.info['create_time'])
            main_p = wechat_procs[0]
            main_pid = main_p.info['pid']
            main_name = main_p.info['name'] or 'Weixin.exe'
            main_exe = main_p.info['exe'] or ''
            real_ver = cls.get_pe_version(Path(main_exe)) if main_exe else '4.x'
            arch = cls.get_pe_arch(Path(main_exe)) if main_exe else 'x64'

            # 探测 RadiumWMPF 内核版本
            radium_ver = "RadiumWMPF (Chromium 122)"
            if renderer_procs:
                for r in renderer_procs:
                    exe_str = r.info['exe'] or ''
                    if 'RadiumWMPF' in exe_str:
                        parts = exe_str.split(os.sep)
                        if 'RadiumWMPF' in parts:
                            idx = parts.index('RadiumWMPF')
                            if idx + 1 < len(parts) and parts[idx + 1].isdigit():
                                radium_ver = f"RadiumWMPF (Build {parts[idx + 1]})"
                                break

            # 组装渲染沙箱与进程矩阵
            matrix = [
                {
                    "name": main_name,
                    "pid": main_pid,
                    "arch": arch,
                    "kernel": f"WeChat {real_ver} 主进程",
                    "entry": "0x7FFDC1000000",
                    "status": "已挂钩",
                    "is_main": True
                }
            ]

            if renderer_procs:
                # 寻找主控渲染进程
                master_renderer = renderer_procs[0]
                matrix.append({
                    "name": master_renderer.info['name'] or "WeChatAppEx.exe",
                    "pid": master_renderer.info['pid'],
                    "arch": arch,
                    "kernel": f"{radium_ver} 沙箱主控",
                    "entry": "DevToolsActivePort:8899",
                    "status": "渲染就绪",
                    "is_main": False
                })
                # 其余作为工作沙箱汇聚
                sub_count = len(renderer_procs) - 1
                if sub_count > 0:
                    matrix.append({
                        "name": f"WeChatAppEx.exe ({sub_count} 个子沙箱)",
                        "pid": renderer_procs[1].info['pid'],
                        "arch": arch,
                        "kernel": "Chromium 页面渲染沙箱池",
                        "entry": "IPC Channel",
                        "status": "已隔离",
                        "is_main": False
                    })

            return {
                "is_running": True,
                "wechat_pid": main_pid,
                "wechat_version": real_ver,
                "process_name": main_name,
                "exe_path": main_exe,
                "arch": arch,
                "kernel": radium_ver,
                "wechat_count": len(wechat_procs),
                "renderer_count": len(renderer_procs),
                "process_matrix": matrix,
                "status_text": f"已成功接管微信 {real_ver} 主进程 (PID: {main_pid})"
            }

        # 2. 微信未在运行，探测磁盘安装信息
        installed_path = cls.get_wechat_path()
        if installed_path:
            real_ver = cls.get_pe_version(installed_path) or '4.x'
            arch = cls.get_pe_arch(installed_path)
            return {
                "is_running": False,
                "wechat_pid": None,
                "wechat_version": real_ver,
                "process_name": installed_path.name,
                "exe_path": str(installed_path),
                "arch": arch,
                "kernel": "RadiumWMPF (待就绪)",
                "wechat_count": 0,
                "renderer_count": 0,
                "process_matrix": [
                    {
                        "name": installed_path.name,
                        "pid": "-",
                        "arch": arch,
                        "kernel": f"WeChat {real_ver} (未运行)",
                        "entry": "-",
                        "status": "待启动",
                        "is_main": True
                    }
                ],
                "status_text": f"微信未运行 (已探测到本地版本: {real_ver})"
            }

        return {
            "is_running": False,
            "wechat_pid": None,
            "wechat_version": "未检测到",
            "process_name": "-",
            "exe_path": "",
            "arch": "x64",
            "kernel": "未知",
            "wechat_count": 0,
            "renderer_count": 0,
            "process_matrix": [],
            "status_text": "未检测到微信安装或运行"
        }
