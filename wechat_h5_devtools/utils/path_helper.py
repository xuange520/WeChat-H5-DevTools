import os
import urllib.parse
from pathlib import Path

def sanitize_url_to_path(raw_url: str, base_domain: str = "wechat_h5") -> tuple[str, Path]:
    """
    将 URL 解析并转换为安全的本地磁盘相对路径 (支持中文 URL 解码)
    """
    parsed = urllib.parse.urlparse(raw_url)
    domain = parsed.netloc or base_domain
    raw_path = urllib.parse.unquote(parsed.path).lstrip("/")

    if not raw_path or raw_path.endswith("/"):
        raw_path += "index.html"

    # 清洗 Windows/Linux 非法字符
    safe_parts = []
    for part in raw_path.split("/"):
        clean_part = "".join(c for c in part if c not in '<>:"/\\|?*').strip()
        if clean_part:
            safe_parts.append(clean_part)

    if not safe_parts:
        safe_parts = ["index.html"]

    return domain, Path(*safe_parts)
