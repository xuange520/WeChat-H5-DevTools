/**
 * WeChat-H5-DevTools 进程 Hook 脚本 (Frida 17+ 兼容版)
 * 功能: 拦截微信主进程及子进程 CreateProcessW，注入 WeChat 4.x / 3.x 全量调试参数
 */

var cpsPtr = null;
try {
    cpsPtr = Process.getModuleByName("kernel32.dll").findExportByName("CreateProcessW");
} catch (e) {
    cpsPtr = Module.findExportByName(null, "CreateProcessW");
}

var allocatedStrings = [];

if (cpsPtr) {
    send("[+] 核心 API CreateProcessW Hook 挂载成功: " + cpsPtr);
    Interceptor.attach(cpsPtr, {
        onEnter: function (args) {
            this.cmdlinePtr = args[1];
            if (this.cmdlinePtr) {
                var cmd = this.cmdlinePtr.readUtf16String();
                if (cmd && (cmd.indexOf("WeChatAppEx.exe") !== -1 || cmd.indexOf("WeixinExt.exe") !== -1 || cmd.indexOf("--type=renderer") !== -1)) {
                    // 过滤崩溃收集器
                    if (cmd.indexOf("crashpad") === -1) {
                        var newCmd = cmd;

                        // 1. 核心无沙箱支持（解锁外部调试与 DOM 探测）
                        if (newCmd.indexOf("--no-sandbox") === -1) {
                            newCmd += " --no-sandbox";
                        }

                        // 2. 微信 4.x flue.dll 专属原生开发者工具开关
                        if (newCmd.indexOf("--enable-chrome-inspector") === -1) {
                            newCmd += " --enable-chrome-inspector";
                        }
                        if (newCmd.indexOf("--enable-vconsole") === -1) {
                            newCmd += " --enable-vconsole";
                        }

                        // 3. 微信 3.x 兼容开关
                        if (newCmd.indexOf("--xweb-enable-inspect") === -1) {
                            newCmd += " --xweb-enable-inspect=1";
                        }

                        // 4. 自动化透明代理与证书忽略（实现微信直接打开任意公众号推文全自动挂载 vConsole，免手动拼链接）
                        if (newCmd.indexOf("--ignore-certificate-errors") === -1) {
                            newCmd += " --ignore-certificate-errors";
                        }
                        if (newCmd.indexOf("--proxy-server") === -1) {
                            newCmd += " --proxy-server=http://127.0.0.1:8899";
                        }

                        // 5. 主 Broker 进程开启远程 CDP 调试端口 (9222，避开代理 8899 端口)
                        if (cmd.indexOf("--type=") === -1 && newCmd.indexOf("--remote-debugging-port") === -1) {
                            newCmd += " --remote-debugging-port=9222";
                        }

                        this.injectedCmd = newCmd;
                        // 分配 UTF-16 内存缓冲区并存入全局数组防止 GC
                        var buf = Memory.allocUtf16String(newCmd);
                        allocatedStrings.push(buf);
                        args[1] = buf;
                        this.context.rdx = buf;
                    }
                }
            }
        },
        onLeave: function (retval) {
            if (this.injectedCmd) {
                send("[PASS] [拦截成功] 已向微信推文/H5渲染子进程注入全量调试参数: " + this.injectedCmd);
            }
        }
    });
} else {
    send("[-] 未能定位到 CreateProcessW 函数导出！");
}
