// うちのコ日常アルバム - Service Worker
const CACHE_NAME = 'uchi-no-ko-v1';
const PRECACHE_URLS = ['/'];

// インストール：基本リソースをキャッシュ
self.addEventListener('install', event => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(PRECACHE_URLS))
  );
});

// アクティベート：古いキャッシュを削除
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

// フェッチ：ネットワーク優先、失敗時はキャッシュ
self.addEventListener('fetch', event => {
  // Streamlit WebSocket は除外
  if (event.request.url.includes('/_stcore/') || 
      event.request.url.includes('/stream')) {
    return;
  }
  event.respondWith(
    fetch(event.request).catch(() => caches.match(event.request))
  );
});
