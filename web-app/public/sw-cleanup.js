/**
 * 临时 Service Worker - 用于清理所有缓存
 * 这个文件会在激活后自动清理所有缓存并注销自己
 */

console.log('[临时 SW] 临时清理 Service Worker 已加载');

// 安装时立即激活
self.addEventListener('install', (event) => {
  console.log('[临时 SW] 安装中...');
  self.skipWaiting();
});

// 激活时清理所有缓存
self.addEventListener('activate', (event) => {
  console.log('[临时 SW] 激活中，开始清理...');

  event.waitUntil(
    Promise.all([
      // 1. 清除所有缓存
      caches.keys().then((cacheNames) => {
        console.log('[临时 SW] 发现', cacheNames.length, '个缓存');
        return Promise.all(
          cacheNames.map((cacheName) => {
            console.log('[临时 SW] 删除缓存:', cacheName);
            return caches.delete(cacheName);
          })
        );
      }),
      // 2. 控制所有客户端
      self.clients.claim()
    ]).then(() => {
      console.log('[临时 SW] 缓存已清理，通知所有客户端刷新');

      // 3. 通知所有客户端刷新
      return self.clients.matchAll().then((clients) => {
        clients.forEach((client) => {
          console.log('[临时 SW] 通知客户端刷新:', client.url);
          client.postMessage({
            type: 'FORCE_REFRESH',
            message: '缓存已清理，请刷新页面'
          });
        });
      });
    })
  );
});

// 不拦截任何请求，直接通过网络请求
self.addEventListener('fetch', (event) => {
  event.respondWith(fetch(event.request));
});
