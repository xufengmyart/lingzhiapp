#!/usr/bin/env node

/**
 * 自动化版本生成器
 *
 * 功能：
 * 1. 自动生成版本号（基于时间戳）
 * 2. 生成版本信息 JSON
 * 3. 注入到 Service Worker 文件
 * 4. 注入到版本信息文件
 * 5. 生成 Git 提交信息
 *
 * 使用方法：
 *   node scripts/generate-version.js
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// 配置
const PROJECT_ROOT = path.resolve(__dirname, '..');
const VERSION_FILE = path.join(PROJECT_ROOT, 'public', 'version.json');
const SW_FILE = path.join(PROJECT_ROOT, 'public', 'sw.js');
const SW_TEMPLATE = path.join(PROJECT_ROOT, 'public', 'sw.template.js');
const INDEX_HTML_FILE = path.join(PROJECT_ROOT, 'index.html');

/**
 * 生成版本号
 * 格式：YYYYMMDD-HHMM
 */
function generateVersion() {
  const now = new Date();
  const date = now.toISOString().slice(0, 10).replace(/-/g, ''); // YYYYMMDD
  const time = now.toTimeString().slice(0, 5).replace(/:/g, '');   // HHMM
  return `${date}-${time}`;
}

/**
 * 获取 Git 信息
 */
function getGitInfo() {
  try {
    const commit = execSync('git rev-parse --short HEAD', { encoding: 'utf-8' }).trim();
    const branch = execSync('git rev-parse --abbrev-ref HEAD', { encoding: 'utf-8' }).trim();
    const tag = execSync('git describe --tags --abbrev=0 2>/dev/null || echo ""', { 
      encoding: 'utf-8',
      shell: '/bin/bash' 
    }).trim();
    const message = execSync('git log -1 --pretty=%B', { encoding: 'utf-8' }).trim();
    
    return {
      commit,
      branch,
      tag,
      message
    };
  } catch (error) {
    console.warn('无法获取 Git 信息:', error.message);
    return {
      commit: 'unknown',
      branch: 'unknown',
      tag: '',
      message: ''
    };
  }
}

/**
 * 生成版本信息
 */
function generateVersionInfo() {
  const now = new Date();
  const version = generateVersion();
  const gitInfo = getGitInfo();
  const builder = process.env.USER || process.env.USERNAME || 'system';
  
  return {
    version,
    buildTime: now.toISOString(),
    gitCommit: gitInfo.commit,
    gitBranch: gitInfo.branch,
    gitTag: gitInfo.tag,
    gitMessage: gitInfo.message,
    builder,
    environment: process.env.NODE_ENV || 'production'
  };
}

/**
 * 写入版本信息文件
 */
function writeVersionFile(versionInfo) {
  const content = JSON.stringify(versionInfo, null, 2);
  fs.writeFileSync(VERSION_FILE, content, 'utf-8');
  console.log('✓ 版本信息已写入:', VERSION_FILE);
}

/**
 * 生成 Service Worker 文件
 */
function generateServiceWorker(versionInfo) {
  const cleanup_sw_path = path.join(PROJECT_ROOT, 'public', 'sw-cleanup.js');

  // 使用清理用的 Service Worker
  if (fs.existsSync(cleanup_sw_path)) {
    const swContent = fs.readFileSync(cleanup_sw_path, 'utf-8');
    fs.writeFileSync(SW_FILE, swContent, 'utf-8');
    console.log('✓ Service Worker 已更新 (清理版本):', SW_FILE);
  } else {
    // 检查是否存在模板文件
    if (fs.existsSync(SW_TEMPLATE)) {
      // 从模板生成
      let swContent = fs.readFileSync(SW_TEMPLATE, 'utf-8');
      // 替换版本号
      swContent = swContent.replace(/{{VERSION}}/g, versionInfo.version);
      fs.writeFileSync(SW_FILE, swContent, 'utf-8');
      console.log('✓ Service Worker 已更新:', SW_FILE);
    } else {
      // 检查是否已存在 sw.js
      if (fs.existsSync(SW_FILE)) {
        // 更新现有文件
        let swContent = fs.readFileSync(SW_FILE, 'utf-8');
        swContent = swContent.replace(/const CURRENT_VERSION = '.*?'/, `const CURRENT_VERSION = '${versionInfo.version}'`);
        fs.writeFileSync(SW_FILE, swContent, 'utf-8');
        console.log('✓ Service Worker 已更新:', SW_FILE);
      } else {
        // 创建新的 Service Worker
        const swContent = generateDefaultServiceWorker(versionInfo.version);
        fs.writeFileSync(SW_FILE, swContent, 'utf-8');
        console.log('✓ Service Worker 已创建:', SW_FILE);
      }
    }
  }
}

/**
 * 更新 index.html 文件，注入版本号
 */
function updateIndexHtml(versionInfo) {
  const INDEX_TEMPLATE_FILE = path.join(PROJECT_ROOT, 'index.template.html');

  if (!fs.existsSync(INDEX_HTML_FILE)) {
    console.log('✗ index.template.html 文件不存在，跳过更新');
    return;
  }

  // 使用模板生成 index.html
  let htmlContent = fs.readFileSync(INDEX_TEMPLATE_FILE, 'utf-8');

  // 替换版本号
  htmlContent = htmlContent.replace(/{{VERSION}}/g, versionInfo.version);
  htmlContent = htmlContent.replace(/{{BUILD_TIME}}/g, versionInfo.buildTime);

  // 写入 index.html
  fs.writeFileSync(INDEX_HTML_FILE, htmlContent, 'utf-8');
  console.log('✓ index.html 已更新:', INDEX_HTML_FILE);
}

/**
 * 生成默认 Service Worker
 */
function generateDefaultServiceWorker(version) {
  return `/**
 * 自动生成的 Service Worker
 * 版本: ${version}
 * 生成时间: ${new Date().toISOString()}
 */

const CACHE_NAME_PREFIX = 'lingzhi-ecosystem-';
const VERSION = '${version}';

// 缓存策略配置
const CACHE_STRATEGIES = {
  // HTML 文件：不缓存，总是从网络获取
  html: {
    match: /\/?$/,
    strategy: 'network-only'
  },
  
  // API 请求：不缓存
  api: {
    match: /^\\/api\\//,
    strategy: 'network-only'
  },
  
  // JS/CSS 文件：基于文件名哈希（如果文件名包含哈希）
  // 否则缓存 30 天
  assets: {
    match: /\\.(js|css)$/,
    strategy: 'cache-first',
    maxAge: 30 * 24 * 60 * 60 * 1000
  },
  
  // 图片：缓存优先
  images: {
    match: /\\.(png|jpg|jpeg|gif|svg|ico|webp)$/,
    strategy: 'cache-first',
    maxAge: 7 * 24 * 60 * 60 * 1000
  }
};

const CURRENT_CACHE = \`\${CACHE_NAME_PREFIX}\${VERSION}\`;

/**
 * 安装 Service Worker
 */
self.addEventListener('install', (event) => {
  console.log('[SW] 安装中...', VERSION);
  self.skipWaiting();
});

/**
 * 激活 Service Worker
 */
self.addEventListener('activate', (event) => {
  console.log('[SW] 激活中...', VERSION);
  
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter(cacheName => 
            cacheName.startsWith(CACHE_NAME_PREFIX) && 
            cacheName !== CURRENT_CACHE
          )
          .map(cacheName => {
            console.log('[SW] 删除旧缓存:', cacheName);
            return caches.delete(cacheName);
          })
      );
    }).then(() => {
      return self.clients.claim();
    })
  );
});

/**
 * 处理请求
 */
self.addEventListener('fetch', (event) => {
  const request = event.request;
  const url = new URL(request.url);
  
  // 只处理同源请求
  if (url.origin !== location.origin) {
    return;
  }
  
  // 确定缓存策略
  let strategy = 'network-first';
  for (const [name, config] of Object.entries(CACHE_STRATEGIES)) {
    if (config.match.test(url.pathname)) {
      strategy = config.strategy;
      break;
    }
  }
  
  // 根据策略处理请求
  switch (strategy) {
    case 'network-only':
      event.respondWith(fetch(request));
      break;
      
    case 'cache-first':
      event.respondWith(
        caches.open(CURRENT_CACHE).then((cache) => {
          return cache.match(request).then((cachedResponse) => {
            if (cachedResponse) {
              return cachedResponse;
            }
            return fetch(request).then((networkResponse) => {
              cache.put(request, networkResponse.clone());
              return networkResponse;
            });
          });
        })
      );
      break;
      
    case 'network-first':
    default:
      event.respondWith(
        fetch(request).then((networkResponse) => {
          // 缓存成功的响应
          if (networkResponse.ok) {
            const clone = networkResponse.clone();
            caches.open(CURRENT_CACHE).then((cache) => {
              cache.put(request, clone);
            });
          }
          return networkResponse;
        }).catch(() => {
          // 网络失败时尝试缓存
          return caches.open(CURRENT_CACHE).then((cache) => {
            return cache.match(request);
          });
        })
      );
      break;
  }
});

/**
 * 处理消息
 */
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
  
  if (event.data && event.data.type === 'GET_VERSION') {
    event.ports[0].postMessage({ version: VERSION });
  }
});
`;
}

/**
 * 主函数
 */
function main() {
  console.log('========================================');
  console.log('自动化版本生成器');
  console.log('========================================\n');
  
  // 生成版本信息
  const versionInfo = generateVersionInfo();
  console.log('版本信息:');
  console.log(`  版本号: ${versionInfo.version}`);
  console.log(`  构建时间: ${versionInfo.buildTime}`);
  console.log(`  Git 提交: ${versionInfo.gitCommit}`);
  console.log(`  Git 分支: ${versionInfo.gitBranch}`);
  console.log('');
  
  // 写入文件
  writeVersionFile(versionInfo);
  generateServiceWorker(versionInfo);
  updateIndexHtml(versionInfo);
  
  console.log('\n========================================');
  console.log('✓ 版本生成完成');
  console.log('========================================');
}

// 执行主函数
main();
