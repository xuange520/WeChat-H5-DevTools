# -*- coding: utf-8 -*-
"""
WeChat-H5-DevTools 脱机高保真模拟沙箱启动器模块
"""
from typing import Optional
from .browser_launcher import BrowserLauncher
from .user_agents import get_wechat_ua

def launch_sandbox(target_url: str, browser: str = "edge", ua: str = "ios", open_devtools: bool = True) -> bool:
    """快捷启动高保真微信模拟沙箱"""
    launcher = BrowserLauncher(browser_type=browser)
    return launcher.launch(target_url=target_url, platform_ua=ua, open_devtools=open_devtools)

__all__ = [
    "BrowserLauncher",
    "get_wechat_ua",
    "launch_sandbox",
]
