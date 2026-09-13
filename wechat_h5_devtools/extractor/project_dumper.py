"""
Webpack / Vue / React H5 全站前端工程深度递归抓取器 (Project Dumper)
"""

import os
import re
import urllib.request
import urllib.parse
from pathlib import Path
from typing import Set, Tuple, List

from ..utils.logger import log_info, log_warn, log_error, log_step
from ..utils.path_helper import sanitize_url_to_path
from ..sandbox.user_agents import get_wechat_ua

class ProjectDumper:
    def __init__(self, output_dir: str = "output_project", platform_ua: str = "ios"):
        self.output_dir = Path(output_dir).resolve()
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.headers = {
            "User-Agent": get_wechat_ua(platform_ua),
            "Referer": "https://mp.weixin.qq.com/",
            "Accept": "*/*"
        }
        self.downloaded: Set[str] = set()

    def _fetch_url(self, raw_u: str, base_url: str) -> str:
        if raw_u.startswith("//"):
            return "https:" + raw_u
        elif raw_u.startswith("http://") or raw_u.startswith("https://"):
            return raw_u
        return urllib.parse.urljoin(base_url, raw_u)

    def dump(self, target_url: str) -> bool:
        log_info(f"开始全站递归抓取: [bold cyan]{target_url}[/bold cyan]")
        log_step(f"本地存储根路径: {self.output_dir}")

        try:
            req = urllib.request.Request(target_url, headers=self.headers)
            with urllib.request.urlopen(req, timeout=10) as r:
                html = r.read().decode("utf-8", errors="ignore")
        except Exception as e:
            log_error(f"无法访问目标 URL: {e}")
            return False

        # 保存主 HTML
        index_file = self.output_dir / "index.html"
        with open(index_file, "w", encoding="utf-8") as f:
            f.write(html)
        log_info(f"主入口 HTML 已保存: index.html ({len(html)} 字节)")

        # 仅针对 script 和 link 标签提取真实外部引用，避免误匹配内联脚本中的字符串
        found_urls = set()
        for match in re.finditer(r'<(?:script|link)\b[^>]*?\b(?:src|href)\s*=\s*(?:["\']([^"\'>\s]+)["\']|([^"\'>\s]+))', html, re.IGNORECASE):
            u = match.group(1) or match.group(2)
            if u and not u.startswith("data:") and not u.startswith("#") and u != ".":
                found_urls.add(u)

        log_step(f"解析到 {len(found_urls)} 个初始静态资源引用，开始异步深入解包...")

        queue = list(found_urls)
        success_count = 0

        while queue:
            raw_u = queue.pop(0)
            full_u = self._fetch_url(raw_u, target_url)

            if full_u in self.downloaded:
                continue
            self.downloaded.add(full_u)

            domain, rel_path = sanitize_url_to_path(full_u)
            save_file = self.output_dir / domain / rel_path
            save_file.parent.mkdir(parents=True, exist_ok=True)

            try:
                import ssl
                ctx = ssl._create_unverified_context()
                req = urllib.request.Request(full_u, headers=self.headers)
                with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
                    data = resp.read()
                    with open(save_file, "wb") as f:
                        f.write(data)

                    log_info(f"已提取: {domain}/{rel_path} ({len(data)} 字节)")
                    success_count += 1

                    # 如果是 JS 文件，深度嗅探 Webpack 运行时动态分包与异步路由 Chunk
                    if str(rel_path).endswith(".js"):
                        try:
                            text = data.decode("utf-8", errors="ignore")
                            chunks = []
                            # 1. 常规 JS 路径
                            chunks += re.findall(r'["\'](js/[a-zA-Z0-9_\-\.]+\.js)["\']', text)
                            chunks += re.findall(r'["\'](chunk-[a-zA-Z0-9_\-\.]+\.js)["\']', text)

                            # 2. 嗅探 Webpack 动态 Chunk 加载器 (如 {"name":"name"}[e] + ".<releaseDate>.js")
                            suffix_matches = set(re.findall(r'\[e\]\|\|e\)\s*\+\s*["\']([^\'"]+\.js)["\']', text))
                            dict_matches = re.findall(r'\"([a-zA-Z0-9_\-\~]+)\"\s*:\s*\"([a-zA-Z0-9_\-\~]+)\"', text)
                            if suffix_matches and dict_matches:
                                for sfx in suffix_matches:
                                    for k, v in dict_matches:
                                        chunks.append(f"js/{v}{sfx}")

                            # 3. 嗅探 Webpack require.e("chunk-name") 动态调用链
                            e_matches = re.findall(r'\.e\((["\'])([^"\']+)\1\)', text)
                            if e_matches and suffix_matches:
                                for sfx in suffix_matches:
                                    for _, cname in e_matches:
                                        chunks.append(f"js/{cname}{sfx}")

                            # 4. 嗅探深层派生分包 chunk-xxxxxx
                            raw_chunk_ids = re.findall(r'(chunk-[a-zA-Z0-9_]+)', text)
                            if raw_chunk_ids and suffix_matches:
                                for sfx in suffix_matches:
                                    for rc in set(raw_chunk_ids):
                                        chunks.append(f"js/{rc}{sfx}")

                            for c in set(chunks):
                                target_chunk_url = self._fetch_url(c, target_url)
                                if target_chunk_url not in self.downloaded and c not in queue:
                                    queue.append(c)

                            # 探测 sourceMappingURL
                            maps = re.findall(r'sourceMappingURL=([a-zA-Z0-9_\-\.]+\.map)', text)
                            for m in set(maps):
                                if m not in queue and self._fetch_url(m, full_u) not in self.downloaded:
                                    queue.append(self._fetch_url(m, full_u))
                        except Exception:
                            pass
                    
                    # 如果是 CSS 文件，解析 url(...) 字体/图片资产
                    elif str(rel_path).endswith(".css"):
                        try:
                            css_text = data.decode("utf-8", errors="ignore")
                            css_assets = re.findall(r'url\s*\(\s*["\']?([^"\'\)\s]+)["\']?\s*\)', css_text)
                            for ca in set(css_assets):
                                if not ca.startswith("data:") and ca not in queue and self._fetch_url(ca, full_u) not in self.downloaded:
                                    queue.append(self._fetch_url(ca, full_u))
                        except Exception:
                            pass
            except Exception as e:
                log_warn(f"跳过不可达资源: {full_u} ({e})")

        log_info(f"全站前端工程抓取完成！共成功归档 [bold green]{success_count + 1}[/bold green] 个文件。")
        return True
