// Guarda el juego en el celular: abre al instante y funciona sin conexión.
// build.sh reemplaza 3171772721; cada versión nueva usa su propia caché y borra las viejas.
const VERSION = "3171772721";
const CACHE = "cristina-" + VERSION;
const FILES = [
  "./",
  "prince.js?v=" + VERSION,
  "prince.wasm?v=" + VERSION,
  "prince.data?v=" + VERSION,
  "manifest.json",
  "favicon.ico",
  "favicon-32.png",
  "icon-192.png",
  "icon-512.png",
  "apple-touch-icon.png",
  "promo.png",
];

self.addEventListener("install", (event) => {
  event.waitUntil(caches.open(CACHE).then((cache) => cache.addAll(FILES)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (event) => {
  event.waitUntil((async () => {
    for (const key of await caches.keys()) {
      if (key !== CACHE) await caches.delete(key);
    }
    await self.clients.claim();
  })());
});

self.addEventListener("fetch", (event) => {
  const request = event.request;
  if (request.method !== "GET" || new URL(request.url).origin !== self.location.origin) return;
  if (request.mode === "navigate") {
    // la página, primero de la red (para recibir versiones nuevas); sin conexión, la guardada
    event.respondWith(
      fetch(request)
        .then((response) => {
          const copy = response.clone();
          caches.open(CACHE).then((cache) => cache.put("./", copy));
          return response;
        })
        .catch(() => caches.match("./"))
    );
    return;
  }
  // el resto, de la caché de esta versión (los archivos del juego llevan ?v=)
  event.respondWith(
    caches.open(CACHE).then(async (cache) => {
      const hit = await cache.match(request);
      if (hit) return hit;
      const response = await fetch(request);
      if (response.ok) cache.put(request, response.clone());
      return response;
    })
  );
});
