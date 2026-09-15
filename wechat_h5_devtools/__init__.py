import os
import sys
from pathlib import Path

__version__ = "1.1.0"
__author__ = "Antigravity Team"
__description__ = "WeChat-H5-DevTools: 微信公众号与内嵌 H5 满血调试与逆向工程套件"

# 确保 UTF-8 输出
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")
