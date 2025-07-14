// sw.js - Service Worker com cache de vídeos e progresso em tempo real

const CACHE_NAME = 'matola-videos';

self.addEventListener('install', event => {
  self.skipWaiting();
  event.waitUntil(caches.open(CACHE_NAME));
});

self.addEventListener('activate', event => {
  clients.claim();
});

// Intercepta requisições .mp4 e serve do cache, se possível
self.addEventListener('fetch', event => {
  const url = event.request.url;
  if (url.endsWith('.mp4')) {
    event.respondWith(
      caches.open(CACHE_NAME).then(async cache => {
        const cached = await cache.match(event.request);
        if (cached) return cached;

        try {
          const response = await fetch(event.request);
          if (response.ok) {
            cache.put(event.request, response.clone());
          }
          return response;
        } catch (err) {
          return new Response("Erro ao carregar vídeo", { status: 503 });
        }
      })
    );
  }
});

// Recebe comandos para baixar vídeos e envia progresso ao frontend
self.addEventListener('message', async event => {
  if (event.data && event.data.type === 'precache-video') {
    const videoUrl = event.data.url;
    const videoName = videoUrl.split('/').pop();

    try {
      const response = await fetch(videoUrl);
      if (!response.ok || !response.body) throw new Error('Stream inválido');

      const contentLength = response.headers.get('content-length');
      const totalBytes = parseInt(contentLength, 10);
      let bytesDownloaded = 0;
      const reader = response.body.getReader();
      const chunks = [];

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        chunks.push(value);
        bytesDownloaded += value.length;

        const progress = Math.floor((bytesDownloaded / totalBytes) * 100);
        notifyClients({
          type: 'download-progress',
          video: videoName,
          progress,
          done: false,
          totalBytes,
          bytesDownloaded
        });
      }

      const fullBlob = new Blob(chunks);
      const cache = await caches.open(CACHE_NAME);
      await cache.put(videoUrl, new Response(fullBlob));

      notifyClients({
        type: 'download-progress',
        video: videoName,
        progress: 100,
        done: true,
        totalBytes,
        bytesDownloaded
      });

    } catch (err) {
      console.error('Erro no download do vídeo:', err);
    }
  }
});

// Envia mensagem para todos os clientes conectados
function notifyClients(data) {
  self.clients.matchAll().then(clients => {
    clients.forEach(client => client.postMessage(data));
  });
}
