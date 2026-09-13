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
