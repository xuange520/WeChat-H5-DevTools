/**
 * WeChat-H5-DevTools 专用 Webcrack 批量 AST 解混淆与解包引擎
 */
const fs = require('fs');
const path = require('path');

// 智能加载 webcrack 依赖
let webcrack = null;
const possiblePaths = [
    'D:/Tools/开发工具/Packer-InfoFinder(1.6)/node_modules',
    path.resolve(__dirname, '../../node_modules'),
    path.resolve(process.cwd(), 'node_modules'),
];

for (const p of possiblePaths) {
    if (fs.existsSync(p)) {
        process.env.NODE_PATH = (process.env.NODE_PATH ? process.env.NODE_PATH + path.delimiter : '') + p;
    }
}
require('module').Module._initPaths();

try {
    webcrack = require('webcrack').webcrack;
} catch (e) {
    try {
        const reqPath = 'D:/Tools/开发工具/Packer-InfoFinder(1.6)/node_modules/webcrack';
        webcrack = require(reqPath).webcrack;
    } catch (e2) {
        console.error('[ERROR] 无法加载 webcrack 模块，请确保依赖已安装:', e2.message);
        process.exit(1);
    }
}

const inDir = process.argv[2] ? path.resolve(process.argv[2]) : path.resolve('output/hospital_h5');
const outDir = process.argv[3] ? path.resolve(process.argv[3]) : path.resolve('output/hospital_h5_deobfuscated');

function sanitizeWeChatCode(rawCode) {
    let sanitized = rawCode;
    const gIdx = sanitized.indexOf('global.publishDomainComponents');
    if (gIdx !== -1) {
        const pre = sanitized.slice(0, gIdx);
        const m = pre.match(/([\s\S]*\}\);)\s*\}\);\s*(?:require\(["'][^"']+["']\);\s*)?$/);
        if (m) {
            sanitized = m[1].trim();
        } else {
            const last = pre.lastIndexOf('});');
            if (last !== -1) {
                const secondLast = pre.lastIndexOf('});', last - 1);
                if (secondLast !== -1 && pre.slice(secondLast + 3, last).trim() === '') {
                    sanitized = pre.slice(0, secondLast + 3).trim();
                } else {
                    sanitized = pre.slice(0, last + 3).trim();
                }
            }
        }
    }
    return sanitized;
}

async function processFile(filePath) {
    const relPath = path.relative(inDir, filePath);
    const outPath = path.join(outDir, relPath);
    const outDirPath = path.dirname(outPath);
    fs.mkdirSync(outDirPath, { recursive: true });

    if (filePath.endsWith('.js')) {
        let code = '';
        try {
            code = fs.readFileSync(filePath, 'utf8').trim();
            
            // 1. 如果是伪装成 JS 的 HTML/XML，原样保留
            if (code.startsWith('<')) {
                fs.copyFileSync(filePath, outPath);
                return;
            }

            // 2. 如果是 JSON，格式化美化
            if ((code.startsWith('{') && code.endsWith('}')) || (code.startsWith('[') && code.endsWith(']'))) {
                try {
                    const parsed = JSON.parse(code);
                    fs.writeFileSync(outPath, JSON.stringify(parsed, null, 2), 'utf8');
                    console.log(`[PASS] JSON 格式化已保存: ${relPath}`);
                    return;
                } catch (_) {}
            }

            // 3. 针对微信小程序私有语法做前置容错清洗
            const sanitizedCode = sanitizeWeChatCode(code);

            console.log(`[INFO] 正在 AST 解混淆: ${relPath} (${sanitizedCode.length} 字节)...`);
            const result = await webcrack(sanitizedCode, {
                unpack: true,
                deobfuscate: true,
                jsx: false
            });

            // 写入解混淆后的单文件代码
            fs.writeFileSync(outPath, result.code, 'utf8');

            // 如果该文件包含 Webpack bundle，独立解包成模块子目录
            if (result.bundle) {
                const baseName = path.basename(filePath, '.js');
                const bundleDir = path.join(outDirPath, `${baseName}_unpacked`);
                fs.mkdirSync(bundleDir, { recursive: true });
                await result.save(bundleDir);
                console.log(`[SUCCESS] Webpack 分包已彻底解压至: ${path.relative(outDir, bundleDir)}`);
            } else {
                console.log(`[SUCCESS] 解混淆完成: ${relPath}`);
            }

        } catch (e) {
            // 二次降级兜底：尝试深度移除所有悬空结尾闭包
            let repaired = false;
            try {
                const fallbackCode = code.replace(/\n\s*\}\);\s*[\s\S]*$/, '\n});');
                const retryResult = await webcrack(fallbackCode, {
                    unpack: true,
                    deobfuscate: true,
                    jsx: false
                });
                fs.writeFileSync(outPath, retryResult.code, 'utf8');
                console.log(`[SUCCESS] 自动二次容错修复并解混淆完成: ${relPath}`);
                repaired = true;
            } catch (retryErr) {
                // 容错修复若仍失败则走安全降级
            }

            if (!repaired) {
                console.log(`[WARN] 非标准语法降级保留: ${relPath} (${e.message})`);
                fs.copyFileSync(filePath, outPath);
            }
        }
    } else {
        // 非 JS 文件（HTML, CSS, 图标等）直接复制
        fs.copyFileSync(filePath, outPath);
    }
}

async function walk(dir) {
    const entries = fs.readdirSync(dir, { withFileTypes: true });
    for (const ent of entries) {
        const full = path.join(dir, ent.name);
        if (ent.isDirectory()) {
            await walk(full);
        } else {
            await processFile(full);
        }
    }
}

async function main() {
    console.log(`[START] 输入工程路径: ${inDir}`);
    console.log(`[START] 输出解混淆路径: ${outDir}`);
    fs.mkdirSync(outDir, { recursive: true });
    await walk(inDir);
    console.log('[FINISH] 全量批量 AST 解混淆与 Webpack 解包彻底完成！');
}

main().catch(err => {
    console.error('[ERROR] 批量处理异常:', err);
    process.exit(1);
});
