/**
 * WeChat-H5-DevTools 进程 Hook 脚本 (Frida 17+ 兼容版)
 * 功能: 拦截微信主进程 CreateProcessW，向渲染器及内嵌浏览器注入调试与 vConsole 参数
 */

var cpsPtr = null;
try {
    cpsPtr = Process.getModuleByName("kernel32.dll").getExportByName("CreateProcessW");
} catch (e) {
    try {
        cpsPtr = Module.findExportByName("kernel32.dll", "CreateProcessW");
    } catch (e2) {
        cpsPtr = Module.findExportByName(null, "CreateProcessW");
    }
}

if (cpsPtr) {
    send("[+] 核心 API CreateProcessW Hook 挂载成功: " + cpsPtr);
    Interceptor.attach(cpsPtr, {
        onEnter: function (args) {
            this.cmdlinePtr = args[1];
            if (this.cmdlinePtr) {
                var cmd = this.cmdlinePtr.readUtf16String();
                if (cmd && (cmd.indexOf("WeChatAppEx.exe") !== -1 || cmd.indexOf("WeixinExt.exe") !== -1 || cmd.indexOf("--type=renderer") !== -1)) {
                    // 仅针对非崩溃收集器的渲染与 Web 进程注入
                    if (cmd.indexOf("crashpad") === -1 && cmd.indexOf("--enable-vconsole") === -1) {
                        var newCmd = cmd;
                        if (newCmd.indexOf("--log-level=2") !== -1) {
                            newCmd = newCmd.replaceAll("--log-level=2", "--log-level=0 --enable-vconsole --xweb-enable-inspect=1 --chrome-inspector");
                        } else {
                            newCmd = newCmd + " --enable-vconsole --xweb-enable-inspect=1 --chrome-inspector";
                        }

                        this.injectedCmd = newCmd;
                        // 动态分配全新的 UTF-16 内存缓冲区，防止原地覆写越界
                        args[1] = Memory.allocUtf16String(newCmd);
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
