# -*- coding: utf-8 -*-
"""
WeChat-H5-DevTools 代理服务器与 vConsole 注入逻辑
"""
from typing import Optional
from pathlib import Path
from ..injector.proxy_injector import (
    ProxyInjector,
    ProxyHTTPHandler,
    CertificateManager,
    VCONSOLE_INJECTION_SNIPPET,
)

def start_proxy_server(port: int = 8899, override_dir: Optional[str] = None):
    """启动代理服务器快捷入口"""
    proxy = ProxyInjector(port=port, override_dir=override_dir)
    proxy.start_proxy()

__all__ = [
    "ProxyInjector",
    "ProxyHTTPHandler",
    "CertificateManager",
    "VCONSOLE_INJECTION_SNIPPET",
    "start_proxy_server",
]
