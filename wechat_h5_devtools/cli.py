import os
import sys
import click
from pathlib import Path
from typing import Optional

from .utils.logger import print_banner, log_info, log_warn, log_error, log_step, print_table
from .injector.process_hooker import ProcessHooker
from .injector.proxy_injector import ProxyInjector
from .injector.wechat_finder import WeChatFinder
from .sandbox.browser_launcher import BrowserLauncher
from .extractor.project_dumper import ProjectDumper
from .extractor.sourcemap_rebuilder import SourceMapRebuilder
from .extractor.api_analyzer import APIAnalyzer
from .injector.kernel_cdp import run_cdp_engine, DEFAULT_DEBUG_PORT, DEFAULT_CDP_PORT

@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """WeChat-H5-DevTools: 微信公众号与内置 H5 满血调试与逆向工程套件"""
    if ctx.invoked_subcommand is None:
        print_banner()
        click.echo(ctx.get_help())

@cli.command(name="doctor", help="诊断本地微信、浏览器与调试依赖环境")
def doctor_cmd():
    print_banner()
    log_step("正在诊断本地开发与调试环境...")

    wechat_path = WeChatFinder.get_wechat_path()
    wechat_status = f"[green]已找到: {wechat_path}[/green]" if wechat_path else "[red]未检测到微信主程序[/red]"

    edge_launcher = BrowserLauncher("edge")
    edge_path = edge_launcher.find_browser_exe()
    edge_status = f"[green]可用: {edge_path}[/green]" if edge_path else "[yellow]未找到[/yellow]"

    chrome_launcher = BrowserLauncher("chrome")
    chrome_path = chrome_launcher.find_browser_exe()
    chrome_status = f"[green]可用: {chrome_path}[/green]" if chrome_path else "[yellow]未找到[/yellow]"

    try:
        import frida
        frida_status = f"[green]已安装 (v{frida.__version__})[/green]"
    except Exception:
        frida_status = "[red]未安装 (pip install frida)[/red]"

    rows = [
        ["微信客户端 (WeChat/Weixin)", wechat_status],
        ["Frida 动态注入引擎", frida_status],
        ["Microsoft Edge 浏览器", edge_status],
        ["Google Chrome 浏览器", chrome_status],
        ["Python 运行时", f"[green]{sys.version.split()[0]} ({sys.executable})[/green]"]
    ]

    print_table("[本地运行环境诊断矩阵]", ["组件名称", "探测状态"], rows)

@cli.command(name="hook", help="启动微信并自动注入内置浏览器 DevTools 调试通道")
@click.option("--path", "-p", default=None, help="自定义指定微信主程序路径 (如: Weixin.exe)")
def hook_cmd(path):
    print_banner()
    hooker = ProcessHooker()
    hooker.launch_and_hook(path)

@cli.command(name="cdp", help="启动原生双通道微信内核 CDP 调试引擎 (9421 & 62000)")
@click.option("--debug-port", "-d", default=DEFAULT_DEBUG_PORT, help="flue.dll 内部调试端口 (默认: 9421)")
@click.option("--cdp-port", "-c", default=DEFAULT_CDP_PORT, help="标准 CDP 兼容端口 (默认: 62000)")
@click.option("--version", "-v", default=None, type=int, help="手动指定 WMPF 内核版本号 (如: 25510)")
@click.option("--no-hook", is_flag=True, default=False, help="仅启动网关服务，不执行 Frida 注入")
def cdp_cmd(debug_port, cdp_port, version, no_hook):
    print_banner()
    run_cdp_engine(
        debug_port=debug_port,
        cdp_port=cdp_port,
        no_hook=no_hook,
        version=version
    )

@cli.command(name="proxy", help="启动 vConsole 透明代理注入网关 (支持微信免 F12 浮动控制台与本地文件替换)")
@click.option("--port", "-p", default=8899, help="代理监听端口 (默认: 8899)")
@click.option("--override-dir", "-d", default=None, help="本地代码目录 (启用 Local Overrides 实时替换线上 JS/CSS)")
def proxy_cmd(port, override_dir):
    print_banner()
    proxy = ProxyInjector(port=port, override_dir=override_dir)
    proxy.start_proxy()

@cli.command(name="override", help="【开发神器】启动 Local Overrides 实时代码替换与热重载服务")
@click.argument("override_dir")
@click.option("--port", "-p", default=8899, help="代理监听端口 (默认: 8899)")
def override_cmd(override_dir, port):
    print_banner()
    proxy = ProxyInjector(port=port, override_dir=override_dir)
    proxy.start_proxy()

@cli.command(name="open", help="【默认】启动微信公众号/内置内核浏览器 CDP 调试通道 (直连微信原生内核，免弹外部浏览器)")
@click.argument("url", required=False, default=None)
@click.option("--port", "-p", default=62000, type=int, help="CDP 远程调试服务端口 (默认: 62000)")
@click.option("--no-kill", is_flag=True, default=False, help="启动时不主动重置旧渲染器进程")
@click.option("--sandbox", is_flag=True, default=False, help="回退使用独立外部浏览器沙箱模式 (Edge/Chrome)")
@click.option("--browser", "-b", default="edge", type=click.Choice(["edge", "chrome"]), help="[沙箱模式] 使用的浏览器内核")
@click.option("--ua", "-u", default="ios", type=click.Choice(["ios", "android", "windows", "mac"]), help="[沙箱模式] 模拟终端平台")
def open_cmd(url, port, no_kill, sandbox, browser, ua):
    print_banner()
    if sandbox:
        if not url:
            log_error("沙箱模式必须指定目标公众号链接 URL！(例如: wx-h5 open https://mp.weixin.qq.com/s/xxx --sandbox)")
            return
        log_step("已指定 --sandbox 选项，切换为独立外部浏览器沙箱兼容模式...")
        launcher = BrowserLauncher(browser)
        launcher.launch(target_url=url, platform_ua=ua, open_devtools=True)
        return

    # 默认流程：调用 wechat_h5_devtools.injector.kernel_cdp 启动微信内核 CDP 服务
    log_step(f"正在启动微信原生内核 CDP 远程调试通道 (端口: {port})...")
    if url:
        log_info(f"目标推文链接: [cyan underline]{url}[/cyan underline]")
        log_info("已就绪！请直接在电脑微信内点击或阅读该文章，CDP 服务将自动捕获其上下文与页面 DOM/JS。")
    else:
        log_info("已就绪！请直接在电脑微信内点击任意公众号推文或打开内置 H5，CDP 服务将自动侦听并捕获活动目标。")

    try:
        run_cdp_engine(cdp_port=port)
    except Exception as e:
        log_error(f"微信内核 CDP 调试服务异常退出: {e}")

PROJECT_ROOT = Path(__file__).resolve().parent.parent

def _resolve_path(path_str: Optional[str], default_name: str = "") -> Path:
    """智能路径解析器：相对路径一律归拢至本项目 output 目录下，严禁污染 C 盘或用户主目录"""
    if not path_str:
        p = PROJECT_ROOT / "output" / default_name
    else:
        p = Path(path_str)
        if not p.is_absolute():
            # 如果当前执行目录下不存在该文件，则优先指向项目 output 目录
            p = PROJECT_ROOT / "output" / p
    p.parent.mkdir(parents=True, exist_ok=True)
    return p

from .extractor.project_dumper import ProjectDumper
from .extractor.sourcemap_rebuilder import SourceMapRebuilder
from .extractor.api_analyzer import APIAnalyzer
from .extractor.deobfuscator import Deobfuscator

@cli.command(name="dump", help="递归反编译提取目标公众号 H5 的全站源码工程与 Webpack 分包")
@click.argument("url")
@click.option("--output", "-o", default="output_project", help="本地源码保存目录 (相对路径自动存入本项目 output/ 目录)")
@click.option("--ua", "-u", default="ios", help="请求 User-Agent 平台")
@click.option("--deobfuscate", "-d", is_flag=True, default=False, help="抓取完成后自动执行全量 AST 语法树解混淆与解包")
def dump_cmd(url, output, ua, deobfuscate):
    print_banner()
    final_output = _resolve_path(output, "output_project")
    dumper = ProjectDumper(output_dir=str(final_output), platform_ua=ua)
    success = dumper.dump(url)
    if success and deobfuscate:
        deobf = Deobfuscator(input_dir=str(final_output))
        deobf.deobfuscate()

@cli.command(name="deobfuscate", help="对已下载的前端工程执行批量 AST 语法树解混淆与 Webpack 模块解包")
@click.argument("target_dir")
@click.option("--output", "-o", default=None, help="解混淆源码输出目录 (默认: <target_dir>_deobfuscated)")
@click.option("--all", "-a", "all_dirs", is_flag=True, default=False, help="批量解混淆该总目录下的所有子工程/子版本目录")
def deobfuscate_cmd(target_dir, output, all_dirs):
    print_banner()
    final_target = Path(target_dir) if Path(target_dir).exists() else _resolve_path(target_dir)
    if not final_target.exists():
        log_error(f"目标目录不存在: {final_target}")
        return

    if all_dirs:
        subdirs = [p for p in final_target.iterdir() if p.is_dir() and not p.name.endswith("_deobfuscated")]
        if not subdirs:
            log_warn(f"在 {final_target} 下未找到任何子工程目录。")
            return
        log_step(f"已启用批量处理模式，共发现 {len(subdirs)} 个工程目录待解混淆...")
        success_count = 0
        for sub in subdirs:
            log_step(f"正在批量处理子工程: [cyan]{sub.name}[/cyan]")
            sub_out = str(sub.parent / f"{sub.name}_deobfuscated")
            deobf = Deobfuscator(input_dir=str(sub), output_dir=sub_out)
            if deobf.deobfuscate():
                success_count += 1
        log_info(f"批量解混淆全部完成！成功: {success_count}/{len(subdirs)}")
    else:
        final_output = str(_resolve_path(output)) if output else None
        deobf = Deobfuscator(input_dir=str(final_target), output_dir=final_output)
        deobf.deobfuscate()

@cli.command(name="restore", help="从 SourceMap 逆向还原原始 Vue / TypeScript 工程目录")
@click.argument("target_dir")
@click.option("--output", "-o", default=None, help="还原源码保存目录 (默认: <target_dir>/src_restored)")
def restore_cmd(target_dir, output):
    print_banner()
    final_target = Path(target_dir) if Path(target_dir).exists() else _resolve_path(target_dir)
    final_output = str(_resolve_path(output)) if output else None
    rebuilder = SourceMapRebuilder(target_dir=str(final_target), output_src_dir=final_output)
    rebuilder.scan_and_restore()

@cli.command(name="scan", help="静态审计已导出的前端项目，提取全量 API 路由与密码学加密特征")
@click.argument("target_dir")
@click.option("--export", "-e", default=None, help="导出 Markdown 格式审计报告至指定文件 (如: report.md)")
@click.option("--all", "-a", "all_dirs", is_flag=True, default=False, help="批量静态审计该总目录下的所有子工程/子版本目录")
def scan_cmd(target_dir, export, all_dirs):
    print_banner()
    final_target = Path(target_dir) if Path(target_dir).exists() else _resolve_path(target_dir)
    if not final_target.exists():
        log_error(f"目标目录不存在: {final_target}")
        return

    if all_dirs:
        subdirs = [p for p in final_target.iterdir() if p.is_dir()]
        for sub in subdirs:
            log_step(f"正在静态审计子工程: [cyan]{sub.name}[/cyan]")
            analyzer = APIAnalyzer(target_dir=str(sub))
            res = analyzer.analyze()
            if export:
                out_name = f"{sub.name}_report.md" if export == "report.md" else f"{sub.name}_{export}"
                final_export = _resolve_path(out_name)
                analyzer.export_markdown(res, str(final_export))
    else:
        analyzer = APIAnalyzer(target_dir=str(final_target))
        res = analyzer.analyze()
        if export:
            final_export = _resolve_path(export, "report.md")
            analyzer.export_markdown(res, str(final_export))


@cli.command(name="gui", help="启动现代化 Fluent Design 桌面图形控制台")
def gui_cmd():
    print_banner()
    log_info("正在拉起 WeChat-H5-DevTools 现代 Fluent 桌面工作台...")
    import subprocess
    import sys
    from pathlib import Path
    app_script = Path(__file__).resolve().parent.parent / "examples" / "supabase_gui" / "app.py"
    if app_script.exists():
        subprocess.run([sys.executable, str(app_script)])
    else:
        log_error(f"未找到图形界面入口脚本: {app_script}")

def main():
    cli()

if __name__ == "__main__":
    main()
