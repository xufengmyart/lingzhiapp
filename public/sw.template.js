/**
 * 灵值生态园 - Service Worker
 * 版本: {{VERSION}}
 * 功能: 自动更新、缓存管理
 */

const CACHE_PREFIX = 'lingzhi-ecosystem';
const CURRENT_VERSION = '{{VERSION}}';
const CACHE_NAME = `${CACHE_PREFIX}-${CURRENT_VERSION}`;

// 需要缓存的资源（可选，目前禁用以避免缓存问题）
const CACHE_URLS = [];

// 安装事件
self.addEventListener('install', (event) => {
  console.log('[SW] 安装中...', CURRENT_VERSION);

  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log('[SW] 缓存已创建:', CACHE_NAME);
      // 不缓存任何资源，避免缓存问题
      return cache.addAll([]);
    })
  );

  // 立即激活新的 Service Worker
  self.skipWaiting();
});

// 激活事件
self.addEventListener('activate', (event) => {
  console.log('[SW] 激活中...', CURRENT_VERSION);

  event.waitUntil(
    Promise.all([
      // 清理旧缓存
      caches.keys().then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => {
            if (cacheName.startsWith(CACHE_PREFIX) && cacheName !== CACHE_NAME) {
              console.log('[SW] 删除旧缓存:', cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      }),
      // 控制所有客户端
      self.clients.claim()
    ]).then(() => {
      console.log('[SW] 激活完成，准备通知客户端');

      // 通知所有客户端有新版本
      return self.clients.matchAll().then((clients) => {
        clients.forEach((client) => {
          console.log('[SW] 通知客户端刷新:', client.url);
          // 发送消息，通知客户端刷新
          client.postMessage({
            type: 'NEW_VERSION_AVAILABLE',
            version: CURRENT_VERSION,
            message: '发现新版本，正在自动刷新...'
          });
        });
      });
    })
  );
});

// 拦截请求（目前直接通过网络请求，不缓存）
self.addEventListener('fetch', (event) => {
  // 不使用缓存，直接通过网络请求
  event.respondWith(
    fetch(event.request).catch((error) => {
      console.error('[SW] 请求失败:', error);
      throw error;
    })
  );
});

// 监听来自客户端的消息
self.addEventListener('message', (event) => {
  console.log('[SW] 收到消息:', event.data);

  if (event.data && event.data.type === 'SKIP_WAITING') {
    console.log('[SW] 跳过等待，立即激活');
    self.skipWaiting();
  }
});
