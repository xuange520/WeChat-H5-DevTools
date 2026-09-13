"""
Webcrack AST 批量解混淆与 Webpack 分包逆向管理器 (Deobfuscator)
"""

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional, List

from ..utils.logger import log_info, log_warn, log_error, log_step

class Deobfuscator:
    def __init__(self, input_dir: str, output_dir: Optional[str] = None):
        self.input_dir = Path(input_dir).resolve()
        if output_dir:
            self.output_dir = Path(output_dir).resolve()
        else:
            self.output_dir = self.input_dir.parent / f"{self.input_dir.name}_deobfuscated"

        self.runner_script = Path(__file__).parent / "webcrack_runner.js"
        self._define_regex = re.compile(r'define\(["\']([^"\']+)["\'],\s*function\([^)]*\)\s*\{')

    def _auto_unpack_miniprogram_defines(self) -> int:
        """自动检测并拆解微信小程序 app-service.js 或单体包中的全部 define 模块"""
        total_unpacked = 0
        if not self.input_dir.exists():
            return 0

        # 扫描可能包含大量 define 模块的单体文件
        candidate_files = []
        for js_f in list(self.input_dir.rglob("*.js")):
            if "_unpacked" in str(js_f) or "_deobfuscated" in str(js_f):
                continue
            try:
                # 仅探测大小超过 50KB 且包含 define( 的文件
                if js_f.stat().st_size > 50 * 1024:
                    sample = js_f.read_text(encoding="utf-8", errors="ignore")[:4096]
                    if "define(" in sample:
                        candidate_files.append(js_f)
            except Exception:
                continue

        for bundle_f in candidate_files:
            try:
                txt = bundle_f.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue

            matches = list(self._define_regex.finditer(txt))
            if len(matches) > 1:
                log_step(f"自动侦测到微信小程序单体打包: [cyan]{bundle_f.relative_to(self.input_dir)}[/cyan] (包含 {len(matches)} 个模块)，正在执行结构化拆解...")
                for i, m in enumerate(matches):
                    rel_path = m.group(1)
                    start_pos = m.end()
                    if i + 1 < len(matches):
                        next_pos = matches[i + 1].start()
                        chunk = txt[start_pos:next_pos]
                    else:
                        chunk = txt[start_pos:]

                    # 清洗微信私有插件声明残余 (如 global.publishDomainComponents)
                    if "global.publishDomainComponents" in chunk:
                        g_idx = chunk.find("global.publishDomainComponents")
                        # 往前找闭合的 });
                        pre_sub = chunk[:g_idx]
                        last_c = pre_sub.rfind("});")
                        if last_c != -1:
                            chunk = pre_sub[:last_c].strip()

                    # 清洗微信运行时末尾元数据: }, { isPage: false ...
                    clean_idx = chunk.rfind("\n}, {")
                    if clean_idx != -1:
                        code = chunk[:clean_idx].strip()
                    else:
                        clean_idx = chunk.rfind("\n});")
                        if clean_idx != -1:
                            code = chunk[:clean_idx].strip()
                        else:
                            clean_idx = chunk.rfind("});")
                            if clean_idx != -1:
                                code = chunk[:clean_idx].strip()
                            else:
                                code = chunk.strip()

                    target_f = self.input_dir / rel_path
                    target_f.parent.mkdir(parents=True, exist_ok=True)
                    target_f.write_text(code, encoding="utf-8")
                    total_unpacked += 1

        if total_unpacked > 0:
            log_info(f"已完成微信小程序单体解包，共成功析出 [bold green]{total_unpacked}[/bold green] 个独立业务源码文件！")
        return total_unpacked

    def deobfuscate(self) -> bool:
        if not self.input_dir.exists():
            log_error(f"输入目录不存在: {self.input_dir}")
            return False

        log_step(f"准备对工程实施 AST 语法解混淆与 Webpack 模块解包")
        log_info(f"输入源工程: [cyan]{self.input_dir}[/cyan]")
        log_info(f"解混淆产物输出目录: [green]{self.output_dir}[/green]")

        # 1. 自动侦测并拆解小程序 define 模块
        self._auto_unpack_miniprogram_defines()

        # 2. 调度 Node.js 运行时执行 Webcrack
        node_exe = shutil.which("node")
        if not node_exe:
            log_error("未检测到 Node.js 运行时，请确保已安装 Node.js v18+")
            return False

        cmd = [node_exe, str(self.runner_script), str(self.input_dir), str(self.output_dir)]

        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace"
            )

            for line in iter(process.stdout.readline, ""):
                line_str = line.strip()
                if not line_str:
                    continue
                if "[SUCCESS]" in line_str:
                    log_info(line_str)
                elif "[INFO]" in line_str:
                    log_step(line_str)
                elif "[WARN]" in line_str:
                    log_warn(line_str)
                elif "[ERROR]" in line_str:
                    log_error(line_str)
                else:
                    log_info(line_str)

            process.wait()
            if process.returncode == 0:
                log_info(f"[bold green]全量 AST 解混淆完成！全部源码与模块已导出至: {self.output_dir}[/bold green]")
                return True
            else:
                log_error(f"Webcrack 执行异常，退出码: {process.returncode}")
                return False
        except Exception as e:
            log_error(f"解混淆子进程启动失败: {e}")
            return False
