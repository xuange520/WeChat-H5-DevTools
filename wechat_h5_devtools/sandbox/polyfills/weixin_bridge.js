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
