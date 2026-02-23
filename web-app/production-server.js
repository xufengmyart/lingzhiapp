#!/usr/bin/env node

import http from 'http';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { parse as parseUrl } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const PORT = process.env.PORT || 3000;
const DIST_DIR = path.join(__dirname, 'dist');

// MIME类型映射
const MIME_TYPES = {
  '.html': 'text/html',
  '.css': 'text/css',
  '.js': 'application/javascript',
  '.json': 'application/json',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.gif': 'image/gif',
  '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon',
  '.woff': 'font/woff',
  '.woff2': 'font/woff2',
  '.ttf': 'font/ttf',
  '.eot': 'application/vnd.ms-fontobject',
};

const server = http.createServer((req, res) => {
  const parsedUrl = parseUrl(req.url);
  let pathname = parsedUrl.pathname;

  // 处理SPA路由 - 所有路由都返回index.html
  if (pathname !== '/' && !path.extname(pathname)) {
    pathname = '/';
  }

  // 解析文件路径
  let filePath = path.join(DIST_DIR, pathname === '/' ? 'index.html' : pathname);

  // 安全检查：确保路径在dist目录内
  const resolvedPath = path.resolve(filePath);
  if (!resolvedPath.startsWith(path.resolve(DIST_DIR))) {
    res.writeHead(403);
    res.end('Forbidden');
    return;
  }

  // 读取文件
  fs.readFile(filePath, (err, data) => {
    if (err) {
      if (err.code === 'ENOENT') {
        // 文件不存在，返回index.html（SPA路由支持）
        const indexPath = path.join(DIST_DIR, 'index.html');
        fs.readFile(indexPath, (err, indexData) => {
          if (err) {
            res.writeHead(404);
            res.end('Not Found');
          } else {
            res.writeHead(200, { 
              'Content-Type': 'text/html',
              'Cache-Control': 'no-cache'
            });
            res.end(indexData);
          }
        });
      } else {
        res.writeHead(500);
        res.end('Server Error');
      }
      return;
    }

    const ext = path.extname(filePath);
    const contentType = MIME_TYPES[ext] || 'application/octet-stream';

    // 设置缓存头
    const cacheControl = ext === '.html' 
      ? 'no-cache' 
      : 'public, max-age=31536000, immutable';

    res.writeHead(200, { 
      'Content-Type': contentType,
      'Cache-Control': cacheControl
    });
    res.end(data);
  });
});

server.listen(PORT, '0.0.0.0', () => {
  console.log(`\n🚀 灵值生态智能体 Web APP 生产服务器已启动！`);
  console.log(`📦 服务地址: http://0.0.0.0:${PORT}`);
  console.log(`📁 构建目录: ${DIST_DIR}`);
  console.log(`\n按 Ctrl+C 停止服务器\n`);
});

// 优雅关闭
process.on('SIGTERM', () => {
  console.log('\n收到SIGTERM信号，正在关闭服务器...');
  server.close(() => {
    console.log('服务器已关闭');
    process.exit(0);
  });
});

process.on('SIGINT', () => {
  console.log('\n收到SIGINT信号，正在关闭服务器...');
  server.close(() => {
    console.log('服务器已关闭');
    process.exit(0);
  });
});
