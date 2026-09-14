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
<script src="http://127.0.0.1:8899/__vconsole__.js"></script>
<script>
    if (typeof VConsole === 'undefined') {
        var _s = document.createElement('script');
        _s.src = 'https://cdn.bootcdn.net/ajax/libs/vConsole/3.15.1/vconsole.min.js';
        document.head.appendChild(_s);
    }
    function _initVConsole() {
        if (typeof VConsole !== 'undefined') {
            if (!window.vConsole) {
                window.vConsole = new VConsole({ theme: 'dark' });
                console.log("%c[WeChat-H5-DevTools] vConsole 移动端调试器已成功激活！", "color: #07c160; font-weight: bold; font-size: 14px;");
            }
        } else {
            setTimeout(_initVConsole, 50);
        }
    }
    _initVConsole();
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
        # 1. 响应本地极速离线 vconsole.min.js (0ms 零外网依赖)
        if self.path.endswith("/__vconsole__.js") or self.path == "/__vconsole__.js":
            vconsole_path = Path(__file__).parent / "assets" / "vconsole.min.js"
            if vconsole_path.exists():
                data = vconsole_path.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "application/javascript")
                self.send_header("Content-Length", str(len(data)))
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(data)
                return

        # 2. 内置开箱即用微信 H5 调试测试靶场 (访问 http://127.0.0.1:8899/test 或 /)
        if self.path in ["/", "/test", "/demo", "/test.html"] or self.path.endswith(("/test", "/demo", "/test.html")):
            html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>WeChat-H5-DevTools 调试验证靶场</title>
    {VCONSOLE_INJECTION_SNIPPET.decode('utf-8')}
</head>
<body style="margin: 0; padding: 24px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0F172A; color: #F8FAFC;">
    <div style="max-width: 480px; margin: 20px auto; background: #1E293B; border-radius: 16px; padding: 24px; border: 1px solid #334155; box-shadow: 0 10px 25px rgba(0,0,0,0.4);">
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 16px;">
            <div style="width: 42px; height: 42px; border-radius: 10px; background: #07C160; display: flex; align-items: center; justify-content: center; font-size: 18px; font-weight: bold; color: white;">&lt;/&gt;</div>
            <div>
                <h3 style="margin: 0; font-size: 18px; color: #FFFFFF;">WeChat-H5-DevTools</h3>
                <span style="font-size: 12px; color: #07C160; font-weight: 500;">vConsole 调试器已强制注入就绪</span>
            </div>
        </div>
        <p style="font-size: 14px; line-height: 1.6; color: #94A3B8;">
            报告长官！当前内置浏览器已成功激活移动端调试套件。请看屏幕<strong>右下角</strong>，已常驻显示官方绿色 <strong>vConsole</strong> 悬浮按钮！
        </p>

        <!-- 公众号推文注入输入框 -->
        <div style="background: #0F172A; border-radius: 10px; padding: 14px; margin: 16px 0; border: 1px solid #334155;">
            <div style="font-size: 13px; color: #38BDF8; font-weight: bold; margin-bottom: 6px;">[公众号推文一键注入通道]</div>
            <p style="font-size: 12px; color: #94A3B8; margin-top: 0; margin-bottom: 8px; line-height: 1.5;">
                由于微信客户端对官方推文 (mp.weixin.qq.com) 走 HTTPS 强制直连，将推文链接粘贴在下方，即可在微信内置浏览器中以原文呈现并强制挂载绿色 vConsole！
            </p>
            <input id="articleUrl" type="text" placeholder="粘贴公众号推文链接 (如: https://mp.weixin.qq.com/s/...)" style="width: 100%; box-sizing: border-box; padding: 10px; border-radius: 8px; border: 1px solid #475569; background: #1E293B; color: #FFFFFF; font-size: 13px; margin-bottom: 8px;" />
            <button onclick="var u = document.getElementById('articleUrl').value.trim(); if(u) {{ location.href = '/read?url=' + encodeURIComponent(u); }} else {{ alert('请先粘贴公众号推文链接！'); }}" style="width: 100%; background: #2563EB; color: white; border: none; padding: 10px; border-radius: 8px; font-size: 14px; font-weight: bold; cursor: pointer;">
                一键打开推文并强制注入 vConsole
            </button>
        </div>

        <div style="background: #0F172A; border-radius: 10px; padding: 14px; margin: 16px 0; border: 1px solid #334155;">
            <div style="font-size: 13px; color: #38BDF8; font-weight: bold; margin-bottom: 6px;">[调试实测指南]</div>
            <div style="font-size: 13px; color: #CBD5E1; line-height: 1.6;">
                • 点击右下角绿色 <strong>vConsole</strong> 打开面板<br>
                • 点击下方按钮向控制台输出实时日志<br>
                • 在 Network 中查看实时网络请求瀑布流
            </div>
        </div>
        <button onclick="console.log('[DevTools 测试成功]', '时间戳: ' + new Date().toLocaleTimeString(), '当前环境: ' + navigator.userAgent); alert('测试日志已发送至 vConsole！请点击右下角绿色按钮展开查看。');" style="width: 100%; background: #07C160; color: white; border: none; padding: 12px; border-radius: 10px; font-size: 15px; font-weight: bold; cursor: pointer;">
            点击向 vConsole 发送测试日志
        </button>
    </div>
</body>
</html>""".encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(html)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(html)
            return

        # 3. 微信公众号推文一键中继与 vConsole 注入器 (/read?url=...)
        if self.path.startswith("/read?url=") or "/read?url=" in self.path:
            import urllib.parse
            query = urllib.parse.urlsplit(self.path).query
            params = urllib.parse.parse_qs(query)
            target_url = params.get("url", [""])[0]
            if target_url:
                try:
                    headers = {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI WindowsWechat(0x63090a13) XWEB/25510",
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                        "Accept-Language": "zh-CN,zh;q=0.9",
                    }
                    req = urllib.request.Request(target_url, headers=headers)
                    with urllib.request.urlopen(req, timeout=10) as resp:
                        content_type = resp.headers.get("Content-Type", "text/html; charset=utf-8")
                        data = resp.read()

                        # 自动注入 vConsole
                        if b"<head>" in data:
                            data = data.replace(b"<head>", b"<head>" + VCONSOLE_INJECTION_SNIPPET, 1)
                        elif b"<body>" in data:
                            data = data.replace(b"<body>", b"<body>" + VCONSOLE_INJECTION_SNIPPET, 1)
                        else:
                            data = VCONSOLE_INJECTION_SNIPPET + data

                        self.send_response(200)
                        self.send_header("Content-Type", content_type)
                        self.send_header("Content-Length", str(len(data)))
                        self.send_header("Access-Control-Allow-Origin", "*")
                        self.end_headers()
                        self.wfile.write(data)
                        return
                except Exception as e:
                    self.send_error(500, f"Proxy Article Error: {e}")
                    return

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

                log_info(f"[bold green][PASS] [Local Overrides 实时替换][/bold green] {url} -> [cyan]{local_override}[/cyan]")
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
            log_step(f"[PASS] [Local Overrides 模式已激活] 正在监听并映射本地目录: [bold cyan]{self.override_dir}[/bold cyan]")
            log_info("当线上 H5 网页请求 JS/CSS/HTML 时，同名文件将直接被本地文件无感替换！")
        
        log_step(f"正在启动代理网关服务: 127.0.0.1:{self.port}...")
        with socketserver.ThreadingTCPServer(("127.0.0.1", self.port), ProxyHTTPHandler) as httpd:
            log_info(f"代理网关已就绪！监听地址: http://127.0.0.1:{self.port}")
            log_info("提示: 将浏览器或微信代理设置为该端口，打开任意 H5 页面都会自动注入调试器与本地替换！")
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                log_warn("代理服务已停止。")
