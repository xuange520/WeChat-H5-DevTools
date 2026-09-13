"""
全平台微信客户端高保真 User-Agent 字典库
"""

WECHAT_USER_AGENTS = {
    "ios": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.48(0x18003029) NetType/WIFI Language/zh_CN",
    "android": "Mozilla/5.0 (Linux; Android 14; 23116PN5BC Build/UKQ1.230804.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/122.0.6261.119 Mobile Safari/537.36 XWEB/1220037 MMWEBSDK/20240401 MMWEBID/1234 MicroMessenger/8.0.48.2580(0x28003036) WeChat/arm64 Weixin NetType/WIFI Language/zh_CN ABI/arm64",
    "windows": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.95 Safari/537.36 NetType/WIFI MicroMessenger/7.0.20.1781(0x6700143B) WindowsWechat(0x63090a13) UnifiedPCWindowsWechat(0xf254101e) XWEB/11275",
    "mac": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) MicroMessenger/3.8.8(0x13080812) MacWechat/3.8.8(0x13080812) NetType/WIFI Language/zh_CN",
}

def get_wechat_ua(platform: str = "ios") -> str:
    return WECHAT_USER_AGENTS.get(platform.lower(), WECHAT_USER_AGENTS["ios"])
