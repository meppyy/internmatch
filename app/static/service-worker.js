const CACHE_NAME = "internmatch-static-v1";

const STATIC_ASSETS = [
    "/static/css/app.css",
    "/static/css/landing.css",
    "/static/js/navigation.js",
    "/static/icons/icon-192.png",
    "/static/icons/icon-512.png",
    "/static/offline.html"
];

// Install and cache public static assets.
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => cache.addAll(STATIC_ASSETS))
            .then(() => self.skipWaiting())
    );
});

// Remove outdated caches.
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((keys) =>
            Promise.all(
                keys
                    .filter((key) => key.startsWith("internmatch-static-")
                        && key !== CACHE_NAME)
                    .map((key) => caches.delete(key))
            )
        ).then(() => self.clients.claim())
    );
});

// Never cache authenticated pages or user-specific information.
self.addEventListener('fetch', (event) => {
    const request = event.request;
    const url = new URL(request.url);

    if (request.method !== "GET" || url.origin !== self.location.origin) {
        return;
    }

    // Network-first for pages, with a generic offline fallback.
    if (request.mode === "navigate") {
        event.respondWith(
            fetch(request).catch(() => caches.match("/static/offline.html"))
        );
        return;
    }

    // Cache-first for explicitly listed public static assets.
    if (STATIC_ASSETS.includes(url.pathname)) {
        event.respondWith(
            caches.match(request).then((cached) =>
                cached || fetch(request)
            )
        );
    }
});