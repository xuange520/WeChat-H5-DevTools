/**
 * WeChat-H5-DevTools 进程 Hook 脚本 (Frida 17+ 兼容版)
 * 功能: 拦截微信主进程 CreateProcessW，向渲染器及内嵌浏览器注入调试参数
 */

var cpsPtr = null;
try {
    cpsPtr = Module.getExportByName("kernel32.dll", "CreateProcessW");
} catch (e) {
    try {
        cpsPtr = Module.findExportByName("kernel32.dll", "CreateProcessW");
    } catch (e2) {
        cpsPtr = Process.getModuleByName("kernel32.dll").getExportByName("CreateProcessW");
    }
}

if (!cpsPtr) {
    cpsPtr = Module.findExportByName(null, "CreateProcessW");
}

if (cpsPtr) {
    Interceptor.attach(cpsPtr, {
        onEnter: function (args) {
            this.cmdlinePtr = args[1];
            if (this.cmdlinePtr) {
                var cmd = this.cmdlinePtr.readUtf16String();
                if (cmd && cmd.indexOf("WeChatAppEx.exe") !== -1) {
                    // 仅针对非崩溃收集器的 WeChatAppEx 渲染与 Web 进程注入
                    if (cmd.indexOf("crashpad") === -1 && cmd.indexOf("--xweb-enable-inspect") === -1) {
                        var newCmd = cmd;
                        if (newCmd.indexOf("--log-level=2") !== -1) {
                            newCmd = newCmd.replaceAll("--log-level=2", "--log-level=0 --xweb-enable-inspect=1");
                        } else {
                            newCmd = newCmd + " --xweb-enable-inspect=1";
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
                send("[+] 子进程已安全注入内置浏览器调试参数: " + this.injectedCmd);
            }
        }
    });
}
