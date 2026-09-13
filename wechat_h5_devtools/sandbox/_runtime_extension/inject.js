/**
 * WeixinJSBridge 高保真模拟挡板 (WeChat-H5-DevTools Polyfill)
 * 支持 30+ 常见微信底层 API 模拟调用与事件监听分发
 */

(function initWeixinJSBridge() {
    if (window.WeixinJSBridge) return;

    var _eventHandlers = {};

    var BridgeMock = {
        invoke: function (api, params, callback) {
            console.log("%c[WeixinJSBridge.invoke] 调用 API: " + api, "color: #10aeff; font-weight: bold;", params);
            
            var res = { err_msg: api + ":ok" };

            // 常见原生 API 智能响应 Mock
            switch (api) {
                case "getBrandWCPayRequest":
                    res.err_msg = "get_brand_wcpay_request:ok";
                    break;
                case "getNetworkType":
                    res.network_type = "wifi";
                    break;
                case "openLocation":
                case "getLocation":
                    res.latitude = 39.9087;
                    res.longitude = 116.3975;
                    res.speed = 0;
                    res.accuracy = 65;
                    break;
                case "scanQRCode":
                    res.resultStr = "https://wechat-h5-devtools.mock/qrcode_sample";
                    break;
                case "chooseImage":
                    res.localIds = ["weixin://resourceid/mock_image_123456"];
                    break;
                case "closeWindow":
                    console.log("%c[WeixinJSBridge] closeWindow 触发", "color: #fa5151; font-weight: bold;");
                    break;
                default:
                    res.err_msg = api + ":ok";
            }

            if (typeof callback === "function") {
                setTimeout(function () {
                    callback(res);
                }, 50);
            }
        },

        call: function (api, params) {
            console.log("%c[WeixinJSBridge.call] " + api, "color: #10aeff;", params);
        },

        on: function (eventName, handler) {
            console.log("%c[WeixinJSBridge.on] 监听事件: " + eventName, "color: #07c160;");
            _eventHandlers[eventName] = handler;
        },

        emit: function (eventName, data) {
            if (_eventHandlers[eventName]) {
                _eventHandlers[eventName](data || {});
            }
        },

        log: function (msg) {
            console.log("[WeixinJSBridge.log]", msg);
        }
    };

    try {
        var currentBridge = BridgeMock;
        Object.defineProperty(window, "WeixinJSBridge", {
            get: function () {
                return currentBridge;
            },
            set: function (newVal) {
                if (newVal && newVal !== currentBridge) {
                    currentBridge = Object.assign(newVal, BridgeMock);
                }
            },
            configurable: true,
            enumerable: true
        });
    } catch (e) {
        window.WeixinJSBridge = BridgeMock;
    }

    window.__wxjs_is_wkwebview = true;
    window.__wxjs_environment = window.__wxjs_environment || "miniprogram";

    // 触发 WeixinJSBridgeReady 原生就绪事件
    var readyEvent = document.createEvent("HTMLEvents");
    readyEvent.initEvent("WeixinJSBridgeReady", false, false);
    document.dispatchEvent(readyEvent);

    console.log("%c[WeChat-H5-DevTools] WeixinJSBridge 原生环境挡板已装载完毕！", "color: #07c160; font-weight: bold;");
})();


/**
 * 微信 JSSDK (jweixin) 自动穿透挡板
 * 拦截 wx.config / wx.ready / wx.error 签名校验，实现免授权无感运行
 */

(function initJSSDKMock() {
    var originalWx = window.wx || {};

    var WxMock = {
        config: function (cfg) {
            console.log("%c[wx.config] 收到 JSSDK 鉴权配置:", "color: #07c160; font-weight: bold;", cfg);
            // 自动模拟签名通过，异步分发 ready 回调
            setTimeout(function () {
                if (typeof WxMock._readyCb === "function") {
                    WxMock._readyCb();
                }
            }, 100);
        },

        ready: function (cb) {
            console.log("%c[wx.ready] 注册 JSSDK 成功回调", "color: #07c160;");
            WxMock._readyCb = cb;
            setTimeout(cb, 100);
        },

        error: function (errCb) {
            // 拦截并压制错误回调
            console.log("%c[wx.error] 已由 WeChat-H5-DevTools 自动旁路签名错误", "color: #999;");
        },

        checkJsApi: function (options) {
            if (options && typeof options.success === "function") {
                var checkResult = {};
                (options.jsApiList || []).forEach(function (api) {
                    checkResult[api] = true;
                });
                options.success({ checkResult: checkResult, errMsg: "checkJsApi:ok" });
            }
        }
    };

    // 继承所有原生微信 Bridge 接口
    var apis = [
        "updateAppMessageShareData", "updateTimelineShareData", "onMenuShareTimeline",
        "onMenuShareAppMessage", "onMenuShareQQ", "onMenuShareWeibo", "onMenuShareQZone",
        "startRecord", "stopRecord", "onVoiceRecordEnd", "playVoice", "pauseVoice",
        "stopVoice", "onVoicePlayEnd", "uploadVoice", "downloadVoice", "chooseImage",
        "previewImage", "uploadImage", "downloadImage", "translateVoice", "getNetworkType",
        "openLocation", "getLocation", "hideOptionMenu", "showOptionMenu", "hideMenuItems",
        "showMenuItems", "hideAllNonBaseMenuItem", "showAllNonBaseMenuItem", "closeWindow",
        "scanQRCode", "chooseWXPay", "openProductSpecificView", "addCard", "chooseCard", "openCard"
    ];

    apis.forEach(function (api) {
        WxMock[api] = function (opt) {
            opt = opt || {};
            console.log("%c[wx." + api + "] 调用", "color: #10aeff;", opt);
            if (typeof opt.success === "function") {
                setTimeout(function () {
                    opt.success({ errMsg: api + ":ok" });
                }, 50);
            }
            if (typeof opt.complete === "function") {
                setTimeout(function () {
                    opt.complete({ errMsg: api + ":ok" });
                }, 50);
            }
        };
    });

    // 保护 wx 对象，防止页面后续通过 <script> 动态加载官方 jweixin.js 时覆盖掉穿透挡板
    try {
        var currentWx = WxMock;
        Object.defineProperty(window, "wx", {
            get: function () {
                return currentWx;
            },
            set: function (newVal) {
                if (newVal && newVal !== currentWx) {
                    currentWx = Object.assign(newVal, WxMock);
                }
            },
            configurable: true,
            enumerable: true
        });
        window.jWeixin = window.wx;
    } catch (e) {
        window.wx = Object.assign(originalWx, WxMock);
        window.jWeixin = window.wx;
    }

    console.log("%c[WeChat-H5-DevTools] 微信 JSSDK 1.6.0 全功能穿透挡板加载完毕！", "color: #07c160; font-weight: bold;");
})();
