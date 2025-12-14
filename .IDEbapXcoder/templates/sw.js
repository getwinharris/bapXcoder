// bapX Coder Service Worker
// Note: For true offline functionality, static assets would need to be properly cached
// This service worker provides basic PWA functionality

const CACHE_NAME = 'bapxcoder-v1';
const urlsToCache = [
  '/',
  '/static/css/main.css',
  '/static/js/main.js'
];

self.addEventListener('install', function(event) {
  // Perform install steps
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(function(cache) {
        console.log('Opened cache');
        return cache.addAll(urlsToCache);
      })
  );
});

self.addEventListener('fetch', function(event) {
  event.respondWith(
    caches.match(event.request)
      .then(function(response) {
        // Return the cached response or fetch from network
        return response || fetch(event.request);
      }
    )
  );
});

// Listen for notification permission request
self.addEventListener('push', function(event) {
  console.log('Received a push notification', event);
});

// Handle notification click
self.addEventListener('notificationclick', function(event) {
  event.notification.close();
  event.waitUntil(
    clients.openWindow('/')
  );
});