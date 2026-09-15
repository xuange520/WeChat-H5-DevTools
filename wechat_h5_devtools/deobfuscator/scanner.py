# -*- coding: utf-8 -*-
"""
WeChat-H5-DevTools 前端资产与加密特征静态审计扫描器
"""
from typing import Dict, Any
from ..extractor.api_analyzer import APIAnalyzer

Scanner = APIAnalyzer

def scan_project(target_dir: str) -> Dict[str, Any]:
    """快捷执行前端工程静态代码审计"""
    scanner = APIAnalyzer(target_dir=target_dir)
    return scanner.analyze()

__all__ = [
    "APIAnalyzer",
    "Scanner",
    "scan_project",
]
