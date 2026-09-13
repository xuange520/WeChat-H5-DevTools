"""
SourceMap 逆向解包与原始工程结构还原器 (SourceMap Rebuilder)
功能: 扫描 .map 文件或在线探测 SourceMap，将压缩混淆的 JS 1:1 还原为原始的 Vue/TS 源码。
"""

import os
import json
from pathlib import Path
from typing import Optional

from ..utils.logger import log_info, log_warn, log_error, log_step

class SourceMapRebuilder:
    def __init__(self, target_dir: str, output_src_dir: Optional[str] = None):
        self.target_dir = Path(target_dir).resolve()
        self.output_src_dir = Path(output_src_dir).resolve() if output_src_dir else (self.target_dir / "src_restored")

    def restore_from_map(self, map_file_path: Path) -> int:
        log_step(f"正在解析 SourceMap 文件: {map_file_path.name}...")
        try:
            with open(map_file_path, "r", encoding="utf-8", errors="ignore") as f:
                data = json.load(f)
        except Exception as e:
            log_error(f"读取 SourceMap 失败: {e}")
            return 0

        sources = data.get("sources", [])
        sources_content = data.get("sourcesContent", [])

        if not sources_content:
            log_warn("该 SourceMap 不包含 sourcesContent 源码正文。")
            return 0

        restored_count = 0
        for src_path, content in zip(sources, sources_content):
            if not content:
                continue

            # 清洗 webpack:// 协议前缀
            clean_path = src_path.replace("webpack:///", "").replace("webpack://", "").replace("webpack-internal:///", "")
            
            # 剥离 Vue SFC 的查询参数后缀 (例如: Home.vue?vue&type=script&lang=js -> Home.vue)
            if "?" in clean_path:
                clean_path = clean_path.split("?")[0]

            # 清洗跨目录符号与 Windows 非法字符
            clean_path = clean_path.replace("\\", "/").replace("../", "")
            safe_parts = []
            for part in clean_path.split("/"):
                part_clean = "".join(c for c in part if c not in '<>:"|?*').strip()
                if part_clean and part_clean != ".":
                    safe_parts.append(part_clean)

            if not safe_parts:
                continue

            out_file = self.output_src_dir / Path(*safe_parts)
            out_file.parent.mkdir(parents=True, exist_ok=True)

            with open(out_file, "w", encoding="utf-8", errors="ignore") as out_f:
                out_f.write(content)
            restored_count += 1

        log_info(f"成功从 {map_file_path.name} 还原 [bold green]{restored_count}[/bold green] 个原始源码文件！")
        return restored_count

    def scan_and_restore(self) -> int:
        log_info(f"扫描目录中的 SourceMap 资产: {self.target_dir}")
        map_files = list(self.target_dir.rglob("*.map"))

        if not map_files:
            log_warn("未在目录中发现 .map 映射文件（生产环境可能已剥离 SourceMap）。")
            return 0

        log_info(f"发现 {len(map_files)} 个 SourceMap 文件，开始逆向解包还原...")
        total_restored = 0
        for mf in map_files:
            total_restored += self.restore_from_map(mf)

        log_info(f"源码逆向还原完毕！原始工程保存于: [bold cyan]{self.output_src_dir}[/bold cyan]")
        return total_restored
