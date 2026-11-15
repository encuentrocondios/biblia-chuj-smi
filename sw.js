/* Service worker: la app abre sin red y lo ya leído sigue disponible. 202611152019 lo reemplaza tools/build_api.py en cada publicación. */
const BUILD = '202611152019';
const SHELL = `chuj-shell-${BUILD}`, DATA = 'chuj-data';
const PRE = ['./', 'index.html', 'app.css', 'app.js', 'manifest.webmanifest', 'books.json', 'version.json', 'icons/icon.svg', 'icons/icon-192.png',
  'fonts/literata-latin.woff2', 'fonts/literata-italic-latin.woff2', 'fonts/atkinson-latin.woff2'];
self.addEventListener('install', e => e.waitUntil(caches.open(SHELL).then(c => c.addAll(PRE)).then(() => self.skipWaiting())));
self.addEventListener('activate', e => e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k.startsWith('chuj-shell-') && k !== SHELL).map(k => caches.delete(k)))).then(() => self.clients.claim())));
self.addEventListener('fetch', e => {
  const r = e.request, u = new URL(r.url);
  if (r.method !== 'GET' || u.origin !== location.origin) return;
  const esDato = u.pathname.endsWith('.json') && !u.pathname.endsWith('manifest.webmanifest');
  if (esDato) {  // texto: se sirve lo guardado al instante y se actualiza en segundo plano (la traducción cambia)
    e.respondWith(caches.open(DATA).then(async c => {
      const hit = (await c.match(r)) || (await caches.match(r)), red = fetch(r).then(x => { if (x.ok) c.put(r, x.clone()); return x; }).catch(() => hit);
      return hit || red;
    }));
  } else {       // aplicación: de la caché, con red como respaldo
    e.respondWith(caches.match(r, { ignoreSearch: true }).then(hit => hit || fetch(r).then(x => { if (x.ok) caches.open(SHELL).then(c => c.put(r, x.clone())); return x; }).catch(() => caches.match('index.html'))));
  }
});
