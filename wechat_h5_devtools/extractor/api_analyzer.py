"""
前端 API 路由资产与加密签名算法静态扫描器 (API & Crypto Analyzer)
"""

import re
import os
from pathlib import Path
from typing import Dict, Set, List

from ..utils.logger import log_info, log_warn, log_step, print_table

class APIAnalyzer:
    def __init__(self, target_dir: str):
        self.target_dir = Path(target_dir).resolve()

    def analyze(self) -> Dict[str, any]:
        log_info(f"正在对工程目录进行静态逆向与代码审计: {self.target_dir}")
        js_files = list(self.target_dir.rglob("*.js"))

        if not js_files:
            log_warn("未找到可供分析的 JavaScript 文件。")
            return {}

        all_text = ""
        for jf in js_files:
            with open(jf, "r", encoding="utf-8", errors="ignore") as f:
                all_text += f.read() + "\n"

        # 1. 深度提取 API 接口 (结合业务前缀与通用 RESTful 路由)
        # 1. 深度提取 API 接口 (结合业务前缀与通用 RESTful 路由)
        STATIC_EXTENSIONS = ('.js', '.css', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.woff', '.woff2', '.ttf', '.map', '.html', '.wxss', '.wxml', '.json')
        
        # 覆盖医疗就医全业务领域前缀
        prefixes = r'api|gateway|his|patient|appointment|register|outpatient|inpatient|inspectReport|pacsReport|check|healthcard|electr|order|user|current|common|ui|support|operation|queue|service|member|pay|auth|wechat|hospital|doctor|v1|v2|v3|system|medical|card|clinic|biz|mobile|core|trade|open|cgi-bin'
        raw_apis = re.findall(
            rf'["\'`](/(?:{prefixes})/[a-zA-Z0-9_\-\/]+)["\'`]',
            all_text
        )

        # 动作动词通用接口匹配 (如: /goods/detail, /trade/create)
        verbs = r'find|get|query|list|create|save|update|delete|cancel|submit|check|info|detail|state|send|bind|verify|confirm|apply|replace|signIn|commit'
        action_apis = re.findall(
            rf'["\'`](/[a-zA-Z0-9_\-]+/[a-zA-Z0-9_\-]+/(?:{verbs})[a-zA-Z0-9_\-\/]*)["\'`]',
            all_text
        )

        all_found_apis = set(raw_apis + action_apis)
        # 严格过滤静态资产与小程序页面路径
        unique_apis = sorted([
            a.rstrip('/') for a in all_found_apis 
            if not any(a.lower().endswith(ext) for ext in STATIC_EXTENSIONS)
            and len(a.split('/')) >= 3
            and not a.startswith('//')
            and not a.startswith('/pages/')
            and not re.match(r'^/package[A-Za-z0-9_\-]+/', a)
        ])

        # 2. 提取小程序页面与分包路由 (Pages & Subpackages)
        page_routes = sorted(list(set(re.findall(
            r'["\'`](/(?:pages|package[A-Za-z0-9_\-]+)/[a-zA-Z0-9_\-\/]+)["\'`]',
            all_text
        ))))

        # 3. 提取硬编码后端域名与 Base URL
        IGNORED_DOMAINS = ('w3.org', 'schemas.microsoft.com', 'localhost', '127.0.0.1', 'github.com', 'momentjs.com')
        all_urls = set(re.findall(r'https?://[a-zA-Z0-9\.\-]+(?::\d+)?', all_text))
        base_urls = sorted([
            u for u in all_urls
            if not any(ign in u.lower() for ign in IGNORED_DOMAINS)
            and not u.endswith('.png') and not u.endswith('.jpg')
        ])

        # 4. 探测小程序与前端网络请求框架
        network_clients = []
        if re.search(r'wx\.request\b', all_text):
            network_clients.append("微信原生网络库 (wx.request)")
        if re.search(r'wx\.uploadFile\b|wx\.downloadFile\b', all_text):
            network_clients.append("微信文件传输管道 (wx.uploadFile / wx.downloadFile)")
        if re.search(r'uni\.request\b|uni\.\$u\.http\b', all_text):
            network_clients.append("UniApp 网络适配器 (uni.request / uView http)")
        if re.search(r'@haici/request-core', all_text):
            network_clients.append("海茨微服务请求核心库 (@haici/request-core)")
        if re.search(r'wepy\.request\b', all_text):
            network_clients.append("WePY 小程序框架请求层 (wepy.request)")
        if re.search(r'flyio|fly\.\b', all_text):
            network_clients.append("FlyIO 跨端请求库 (flyio)")
        if re.search(r'axios\b', all_text):
            network_clients.append("Axios HTTP 客户端 (axios)")

        # 5. 探测密码学与签名特征
        crypto_features = []
        if re.search(r'miniprogram-sm-crypto|@haici/gmsm4|sm2|sm3|sm4|SM2|SM3|SM4|sm-crypto', all_text):
            crypto_features.append("国密算法 (SM2/SM3/SM4 微信端国密套件: miniprogram-sm-crypto / gmsm4)")
        if re.search(r'tripledes|TripleDES|3DES|DES\.encrypt', all_text, re.IGNORECASE):
            crypto_features.append("DES/3DES 对称加解密 (TripleDES / DES)")
        if re.search(r'CryptoJS|AES\.encrypt|AES-CBC|AES-ECB|AES-GCM', all_text):
            crypto_features.append("高级对称加密 (CryptoJS / AES 规范)")
        if re.search(r'JSEncrypt|RSAKey|setPublicKey|jsbn', all_text):
            crypto_features.append("非对称加密与大数运算 (RSA 公钥加密 / jsbn)")
        if re.search(r'HmacSHA256|hmac|sha256|MD5|md5', all_text):
            crypto_features.append("消息摘要与数字签名 (HMAC-SHA256 / MD5 / SHA256)")
        if re.search(r'jwt|bearer|authorization|token|accessToken|jtoken', all_text, re.IGNORECASE):
            crypto_features.append("身份鉴权体系 (JWT / jtoken / Bearer Token)")
        if re.search(r'x-sign|x-signature|sign\s*=|signature\s*=|nonce|timestamp', all_text, re.IGNORECASE):
            crypto_features.append("防篡改风控签名机制 (Timestamp / Nonce / X-Sign)")

        # 6. 提取请求头与关键参数特征
        headers_found = set()
        for h in re.findall(r'["\']([xX]-[a-zA-Z0-9_\-]+|token|jtoken|openId|openid|unionId|hospitalCode|hospitalId|tenantId|signature|nonce|timestamp)["\']', all_text):
            headers_found.add(h)

        # 7. 提取敏感配置字段 (AppID, Plugin ID)
        secrets = []
        appid_matches = set(re.findall(r'["\'](wx[a-f0-9]{16})["\']', all_text))
        if appid_matches:
            secrets.append(f"微信 AppID: {', '.join(sorted(appid_matches))}")
        plugin_matches = set(re.findall(r'plugin://([a-zA-Z0-9_\-]+)', all_text))
        if plugin_matches:
            secrets.append(f"微信插件依赖 (Plugins): {', '.join(sorted(plugin_matches))}")
        if headers_found:
            secrets.append(f"关键业务请求头/参数: {', '.join(sorted(headers_found))}")

        # 8. 打印报告 (纯净文本标签，零 Emoji)
        log_step("审计扫描完成！结果如下：")

        if base_urls:
            print_table("[后端业务域名 / Base URLs]", ["序号", "域名地址"], [[str(i), u] for i, u in enumerate(base_urls, 1)])

        if network_clients:
            print_table("[网络请求框架]", ["序号", "网络客户端"], [[str(i), c] for i, c in enumerate(network_clients, 1)])

        if crypto_features:
            print_table("[前端加解密与安全特征]", ["序号", "算法/安全特性"], [[str(i), c] for i, c in enumerate(crypto_features, 1)])

        if secrets:
            print_table("[敏感配置/凭据与请求头]", ["序号", "凭据/参数信息"], [[str(i), s] for i, s in enumerate(secrets, 1)])

        if unique_apis:
            print_table(f"[后端 API 接口清单 (共 {len(unique_apis)} 个)]", ["序号", "API 路由地址"], [[str(i), a] for i, a in enumerate(unique_apis, 1)])

        result_data = {
            "base_urls": base_urls,
            "network_clients": network_clients,
            "apis": unique_apis,
            "page_routes": page_routes,
            "crypto_features": crypto_features,
            "secrets": secrets,
            "headers": sorted(headers_found)
        }

        return result_data

    def export_markdown(self, result: Dict[str, any], out_file: str):
        p = Path(out_file).resolve()
        lines = [
            "# WeChat-H5-DevTools 静态逆向与代码审计报告",
            f"\n> **审计目标目录**: `{self.target_dir}`\n",
            "## [后端业务域名 / Base URLs]\n"
        ]
        if result.get("base_urls"):
            lines.append("| 序号 | 域名地址 |")
            lines.append("| :--- | :--- |")
            for idx, u in enumerate(result["base_urls"], 1):
                lines.append(f"| {idx} | `{u}` |")
        else:
            lines.append("*未发现明文域名*\n")

        lines.append("\n## [网络请求框架]\n")
        if result.get("network_clients"):
            for idx, c in enumerate(result["network_clients"], 1):
                lines.append(f"{idx}. {c}")
        else:
            lines.append("*未发现显著网络库特征*\n")

        lines.append("\n## [前端加解密与安全特征]\n")
        if result.get("crypto_features"):
            for idx, c in enumerate(result["crypto_features"], 1):
                lines.append(f"{idx}. {c}")
        else:
            lines.append("*未发现显著加密特征*\n")

        lines.append("\n## [敏感配置/凭据与请求头]\n")
        if result.get("secrets"):
            for idx, s in enumerate(result["secrets"], 1):
                lines.append(f"{idx}. {s}")
        else:
            lines.append("*未发现明文 AppID / 密钥*\n")

        lines.append(f"\n## [后端 API 接口清单 (共 {len(result.get('apis', []))} 个)]\n")
        lines.append("| 序号 | API 路由地址 |")
        lines.append("| :--- | :--- |")
        for idx, a in enumerate(result.get("apis", []), 1):
            lines.append(f"| {idx} | `{a}` |")

        p.write_text("\n".join(lines), encoding="utf-8")
        log_info(f"审计报告已导出至: [bold cyan]{p}[/bold cyan]")
