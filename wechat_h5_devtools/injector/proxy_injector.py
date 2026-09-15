"""
本地轻量透明代理注入网关 (Proxy Injector)
功能: 在微信或浏览器通过该代理访问网页时，自动在 HTML <head> 首行注入 vConsole / Eruda 调试器。
"""

import ssl
import gzip
import datetime
import http.server
import socketserver
import urllib.request
from typing import Optional, Tuple, Dict
from ..utils.logger import log_info, log_warn, log_step

import mimetypes
import urllib.parse
from pathlib import Path

try:
    from cryptography import x509
    from cryptography.x509.oid import NameOID
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.primitives import serialization
    HAS_CRYPTO = True
except ImportError:
    HAS_CRYPTO = False

class CertificateManager:
    """自动化动态证书生成与管理引擎 (支持 HTTPS 微信推文与 H5 无感解密与脚本注入)"""
    _instance: Optional["CertificateManager"] = None

    def __init__(self, ca_dir: Optional[Path] = None):
        if not ca_dir:
            ca_dir = Path(__file__).resolve().parent.parent.parent / "resources" / "ca"
        self.ca_dir = ca_dir
        self.ca_dir.mkdir(parents=True, exist_ok=True)
        self.ca_cert_path = self.ca_dir / "ca.crt"
        self.ca_key_path = self.ca_dir / "ca.key"
        self._cert_cache: Dict[str, Tuple[str, str]] = {}
        self._init_ca()

    @classmethod
    def get_instance(cls) -> "CertificateManager":
        if cls._instance is None:
            cls._instance = CertificateManager()
        return cls._instance

    def _init_ca(self):
        if not HAS_CRYPTO:
            return
        if not self.ca_cert_path.exists() or not self.ca_key_path.exists():
            root_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
            subject = issuer = x509.Name([
                x509.NameAttribute(NameOID.COUNTRY_NAME, "CN"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "WeChat-H5-DevTools"),
                x509.NameAttribute(NameOID.COMMON_NAME, "WeChat H5 DevTools Root CA"),
            ])
            root_cert = (
                x509.CertificateBuilder()
                .subject_name(subject)
                .issuer_name(issuer)
                .public_key(root_key.public_key())
                .serial_number(x509.random_serial_number())
                .not_valid_before(datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1))
                .not_valid_after(datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=3650))
                .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
                .sign(root_key, hashes.SHA256())
            )
            self.ca_cert_path.write_bytes(root_cert.public_bytes(serialization.Encoding.PEM))
            self.ca_key_path.write_bytes(root_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            ))

        self.root_cert = x509.load_pem_x509_certificate(self.ca_cert_path.read_bytes())
        self.root_key = serialization.load_pem_private_key(self.ca_key_path.read_bytes(), password=None)

    def get_cert_for_host(self, hostname: str) -> Optional[Tuple[str, str]]:
        if not HAS_CRYPTO:
            return None
        if hostname in self._cert_cache:
            return self._cert_cache[hostname]

        cert_file = self.ca_dir / f"{hostname}.crt"
        key_file = self.ca_dir / f"{hostname}.key"
        if cert_file.exists() and key_file.exists():
            res = (str(cert_file), str(key_file))
            self._cert_cache[hostname] = res
            return res

        host_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        host_subject = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "CN"),
            x509.NameAttribute(NameOID.COMMON_NAME, hostname),
        ])
        host_cert = (
            x509.CertificateBuilder()
            .subject_name(host_subject)
            .issuer_name(self.root_cert.subject)
            .public_key(host_key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1))
            .not_valid_after(datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=365))
            .add_extension(x509.SubjectAlternativeName([x509.DNSName(hostname)]), critical=False)
            .sign(self.root_key, hashes.SHA256())
        )
        cert_file.write_bytes(host_cert.public_bytes(serialization.Encoding.PEM))
        key_file.write_bytes(host_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))
        res = (str(cert_file), str(key_file))
        self._cert_cache[hostname] = res
        return res

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

    def _is_mitm_target(self, host: str) -> bool:
        """判断是否为需要自动注入 vConsole 的微信或公众号网页目标"""
        h = host.lower()
        return (
            h == "mp.weixin.qq.com" or
            h.endswith(".weixin.qq.com") or
            h.endswith(".wechat.com") or
            h.endswith(".tenpay.com") or
            h == "res.wx.qq.com"
        )

    def do_CONNECT(self):
        """处理 HTTPS CONNECT 隧道请求 (支持微信公众号推文 TLS MITM 透明解密与全自动 vConsole 挂载)"""
        import socket
        import select

        host, port_str = self.path.split(":")
        port = int(port_str)

        if HAS_CRYPTO and self._is_mitm_target(host):
            self._handle_mitm(host, port)
            return

        # 回退至原生 TCP 盲转发隧道
        self._handle_passthrough(host, port)

    def _handle_passthrough(self, host: str, port: int):
        import socket
        import select

        try:
            target_sock = socket.create_connection((host, port), timeout=10)
            self.send_response(200, "Connection Established")
            self.end_headers()

            conns = [self.connection, target_sock]
            while True:
                r, w, x = select.select(conns, [], conns, 10)
                if x or not r:
                    break
                for s in r:
                    other = target_sock if s is self.connection else self.connection
                    data = s.recv(8192)
                    if not data:
                        return
                    other.sendall(data)
        except Exception:
            pass
        finally:
            try:
                target_sock.close()
            except Exception:
                pass

    def _handle_mitm(self, host: str, port: int):
        """TLS 中间人解密，自动向公众号文章与微信 H5 HTML 注入 vConsole"""
        cert_mgr = CertificateManager.get_instance()
        cert_pair = cert_mgr.get_cert_for_host(host)
        if not cert_pair:
            self._handle_passthrough(host, port)
            return

        cert_file, key_file = cert_pair
        try:
            self.send_response(200, "Connection Established")
            self.end_headers()
        except Exception:
            return

        try:
            ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            ctx.load_cert_chain(certfile=cert_file, keyfile=key_file)
            tls_sock = ctx.wrap_socket(self.connection, server_side=True)
        except Exception:
            return

        try:
            rfile = tls_sock.makefile("rb")
            wfile = tls_sock.makefile("wb")

            req_line = rfile.readline().decode("iso-8859-1")
            if not req_line:
                return
            parts = req_line.strip().split()
            if len(parts) < 2:
                return
            method, path = parts[0], parts[1]

            headers = {}
            while True:
                line = rfile.readline().decode("iso-8859-1")
                if line in ("\r\n", "\n", ""):
                    break
                if ":" in line:
                    k, v = line.split(":", 1)
                    headers[k.strip()] = v.strip()

            content_len = int(headers.get("Content-Length", 0))
            post_body = rfile.read(content_len) if content_len > 0 else None

            # 构造真实向上游请求
            upstream_url = f"https://{host}:{port}{path}"
            req_headers = {k: v for k, v in headers.items() if k.lower() not in ["host", "accept-encoding", "content-length"]}
            if "User-Agent" not in req_headers:
                req_headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI WindowsWechat(0x63090a13) XWEB/25510"

            req = urllib.request.Request(upstream_url, data=post_body, headers=req_headers, method=method)
            with urllib.request.urlopen(req, timeout=15) as resp:
                resp_body = resp.read()
                content_type = resp.headers.get("Content-Type", "")
                content_encoding = resp.headers.get("Content-Encoding", "").lower()

                # 如果有 gzip，先解压
                if "gzip" in content_encoding:
                    try:
                        resp_body = gzip.decompress(resp_body)
                    except Exception:
                        pass

                # 自动无感注入 vConsole
                if "text/html" in content_type:
                    if b"<head>" in resp_body:
                        resp_body = resp_body.replace(b"<head>", b"<head>" + VCONSOLE_INJECTION_SNIPPET, 1)
                    elif b"<body>" in resp_body:
                        resp_body = resp_body.replace(b"<body>", b"<body>" + VCONSOLE_INJECTION_SNIPPET, 1)
                    else:
                        resp_body = VCONSOLE_INJECTION_SNIPPET + resp_body
                    log_info(f"[PASS] [微信公众号推文自动注入成功] {upstream_url} (已自动挂载 vConsole)")

                wfile.write(f"HTTP/1.1 {resp.status} OK\r\n".encode("ascii"))
                for k, v in resp.headers.items():
                    if k.lower() not in ["content-length", "content-encoding", "transfer-encoding"]:
                        wfile.write(f"{k}: {v}\r\n".encode("iso-8859-1"))
                wfile.write(f"Content-Length: {len(resp_body)}\r\n\r\n".encode("ascii"))
                wfile.write(resp_body)
                wfile.flush()
        except Exception:
            pass
        finally:
            try:
                tls_sock.close()
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
