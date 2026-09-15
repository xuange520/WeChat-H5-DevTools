# -*- coding: utf-8 -*-
"""
WeChat-H5-DevTools AST 语法树解混淆与 Webpack 逆向分包引擎
"""
from typing import Optional
from ..extractor.deobfuscator import Deobfuscator

DeobfuscatorEngine = Deobfuscator

def deobfuscate_project(input_dir: str, output_dir: Optional[str] = None) -> bool:
    """快捷执行工程 AST 解混淆"""
    engine = Deobfuscator(input_dir=input_dir, output_dir=output_dir)
    return engine.deobfuscate()

__all__ = [
    "Deobfuscator",
    "DeobfuscatorEngine",
    "deobfuscate_project",
]
