const CACHE_VERSION = "neustart-immocheck-v8.320";

self.addEventListener("install", () => {
  self.skipWaiting();
});

self.addEventListener("activate", event => {
  event.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.map(key => caches.delete(key))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", event => {
  event.respondWith(
    (() => {
      const request = event.request;
      const url = new URL(request.url);
      // A network-first service worker still uses the browser HTTP cache unless
      // it explicitly bypasses it. Fresh HTML must reference the current assets.
      const fresh = request.method === "GET" && url.origin === self.location.origin
        && (request.mode === "navigate" || ["document", "script", "style"].includes(request.destination));
      return fetch(request, fresh ? {cache:"no-store"} : undefined)
        .catch(() => caches.match(request));
    })()
  );
});
// V8.198 fresh deploy trigger
// V8.198 fresh deploy trigger 2
// V8.198 fresh deploy trigger 3
// V8.319 deployment trigger

