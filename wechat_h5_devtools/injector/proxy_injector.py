"""
本地轻量透明代理注入网关 (Proxy Injector)
功能: 在微信或浏览器通过该代理访问网页时，自动在 HTML <head> 首行注入 vConsole / Eruda 调试器。
"""

import http.server
import socketserver
import urllib.request
from typing import Optional
from ..utils.logger import log_info, log_warn, log_step

import mimetypes
import urllib.parse
from pathlib import Path

VCONSOLE_INJECTION_SNIPPET = """
<!-- WeChat-H5-DevTools Injected vConsole -->
<script src="https://unpkg.com/vconsole/dist/vconsole.min.js"></script>
<script>
    try {
        window.vConsole = new VConsole({ theme: 'dark' });
        console.log("%c[WeChat-H5-DevTools] vConsole 移动端调试器已成功激活！", "color: #07c160; font-weight: bold; font-size: 14px;");
    } catch(e) {}
</script>
""".encode("utf-8")

class ProxyHTTPHandler(http.server.BaseHTTPRequestHandler):
    override_dir: Optional[Path] = None

    def _find_local_override_file(self, url: str) -> Optional[Path]:
        if not self.override_dir or not self.override_dir.exists():
            return None

        parsed = urllib.parse.urlparse(url)
        clean_path = urllib.parse.unquote(parsed.path).lstrip("/")
        if not clean_path:
            return None

        # 1. 尝试完整相对路径匹配 (例如 override_dir/js/chunk.js)
        cand1 = self.override_dir / clean_path
        if cand1.is_file():
            return cand1

        # 2. 尝试纯文件名匹配 (例如 override_dir/chunk.js)
        cand2 = self.override_dir / Path(clean_path).name
        if cand2.is_file():
            return cand2

        # 3. 尝试模糊去除 hash 后的文件名 (例如 chunk-common.12345.js -> chunk-common.js)
        raw_name = Path(clean_path).name
        for local_f in self.override_dir.rglob("*"):
            if local_f.is_file() and (local_f.name == raw_name or local_f.stem in raw_name):
                return local_f

        return None

    def do_GET(self):
        url = self.path
        if not url.startswith("http://") and not url.startswith("https://"):
            self.send_error(400, "Bad URL")
            return

        # 检查是否命中 Local Overrides 本地文件替换
        local_override = self._find_local_override_file(url)
        if local_override:
            try:
                data = local_override.read_bytes()
                mime_type, _ = mimetypes.guess_type(str(local_override))
                mime_type = mime_type or "application/octet-stream"

                log_info(f"[bold green]⚡ [Local Overrides 实时替换][/bold green] {url} -> [cyan]{local_override}[/cyan]")
                self.send_response(200)
                self.send_header("Content-Type", mime_type)
                self.send_header("Content-Length", str(len(data)))
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
                self.send_header("Pragma", "no-cache")
                self.send_header("Expires", "0")
                self.end_headers()
                self.wfile.write(data)
                return
            except Exception as e:
                log_warn(f"本地替换文件读取失败: {e}")

        headers = {k: v for k, v in self.headers.items() if k.lower() not in ["host", "accept-encoding"]}
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as resp:
                content_type = resp.headers.get("Content-Type", "")
                data = resp.read()

                # 如果是 HTML 页面，自动注入 vConsole
                if "text/html" in content_type:
                    if b"<head>" in data:
                        data = data.replace(b"<head>", b"<head>" + VCONSOLE_INJECTION_SNIPPET, 1)
                    elif b"<body>" in data:
                        data = data.replace(b"<body>", b"<body>" + VCONSOLE_INJECTION_SNIPPET, 1)

                self.send_response(resp.status)
                for k, v in resp.headers.items():
                    if k.lower() not in ["content-length", "content-encoding", "transfer-encoding"]:
                        self.send_header(k, v)
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
        except Exception as e:
            self.send_error(502, f"Proxy Error: {e}")

    def do_CONNECT(self):
        """处理 HTTPS CONNECT 隧道请求"""
        import socket
        import select

        host, port = self.path.split(":")
        port = int(port)

        try:
            target_sock = socket.create_connection((host, port), timeout=10)
            self.send_response(200, "Connection Established")
            self.end_headers()

            conns = [self.connection, target_sock]
            while True:
                r, w, x = select.select(conns, [], conns, 10)
                if x:
                    break
                if not r:
                    break
                for s in r:
                    other = target_sock if s is self.connection else self.connection
                    data = s.recv(8192)
                    if not data:
                        return
                    other.sendall(data)
        except Exception:
            self.send_error(502, "Bad Gateway")
        finally:
            try:
                target_sock.close()
            except Exception:
                pass

    def do_POST(self):
        """处理 POST 请求转发"""
        url = self.path
        content_len = int(self.headers.get("Content-Length", 0))
        post_body = self.rfile.read(content_len) if content_len > 0 else None

        headers = {k: v for k, v in self.headers.items() if k.lower() not in ["host", "accept-encoding"]}
        try:
            req = urllib.request.Request(url, data=post_body, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = resp.read()
                self.send_response(resp.status)
                for k, v in resp.headers.items():
                    if k.lower() not in ["content-length", "content-encoding", "transfer-encoding"]:
                        self.send_header(k, v)
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
        except Exception as e:
            self.send_error(502, f"Proxy POST Error: {e}")

class ProxyInjector:
    def __init__(self, port: int = 8899, override_dir: Optional[str] = None):
        self.port = port
        self.override_dir = Path(override_dir).resolve() if override_dir else None

    def start_proxy(self):
        ProxyHTTPHandler.override_dir = self.override_dir

        if self.override_dir:
            log_step(f"⚡ [Local Overrides 模式已激活] 正在监听并映射本地目录: [bold cyan]{self.override_dir}[/bold cyan]")
            log_info("当线上 H5 网页请求 JS/CSS/HTML 时，同名文件将直接被本地文件无感替换！")
        
        log_step(f"正在启动代理网关服务: 127.0.0.1:{self.port}...")
        with socketserver.ThreadingTCPServer(("127.0.0.1", self.port), ProxyHTTPHandler) as httpd:
            log_info(f"代理网关已就绪！监听地址: http://127.0.0.1:{self.port}")
            log_info("提示: 将浏览器或微信代理设置为该端口，打开任意 H5 页面都会自动注入调试器与本地替换！")
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                log_warn("代理服务已停止。")
