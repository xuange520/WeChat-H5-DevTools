#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WeChat-H5-DevTools 主启动入口
"""

import sys
from pathlib import Path

# 将当前根目录追加到 sys.path
root_dir = Path(__file__).parent.resolve()
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from wechat_h5_devtools.cli import main

if __name__ == "__main__":
    main()
