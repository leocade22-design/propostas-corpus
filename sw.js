// IMPORTANTE: ao publicar uma versão nova, mude VERSAO aqui e a constante
// APP_VERSION no index.html (as duas juntas). É a mudança neste arquivo que faz o
// navegador perceber que existe versão nova e reinstalar o service worker.
const VERSAO = '2026.08.20-10';
const CACHE_NAME = 'propostas-corpus-' + VERSAO;

const ARQUIVOS_PARA_CACHE = [
  './',
  './index.html',
  './manifest.json',
  './modelos.js',
  './vendor/jszip.min.js',
  './icons/icon-192.png',
  './icons/icon-512.png',
  './icons/icon-512-maskable.png'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    // cache: 'reload' garante que a instalação pegue os arquivos da REDE, e não
    // uma cópia velha do cache HTTP do navegador
    caches.open(CACHE_NAME).then((cache) =>
      cache.addAll(ARQUIVOS_PARA_CACHE.map((url) => new Request(url, { cache: 'reload' })))
    )
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys()
      .then((nomes) => Promise.all(nomes.filter((n) => n !== CACHE_NAME).map((n) => caches.delete(n))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('message', (event) => {
  if (event.data === 'ATIVAR_AGORA') self.skipWaiting();
});

// Network-first de verdade: o segredo é o cache: 'no-store'. Sem ele, o fetch aqui
// dentro ainda passa pelo cache HTTP do navegador — e o GitHub Pages manda
// max-age=600, o que faria o app continuar servindo a versão antiga mesmo online.
// O cache local só entra em cena quando não há internet.
//
// A consulta de CNPJ (BrasilAPI / Minha Receita) é de outra origem e passa direto,
// sem cache: ou tem internet e responde, ou o próprio app avisa e você digita à mão.
self.addEventListener('fetch', (event) => {
  if (event.request.method !== 'GET') return;

  const url = new URL(event.request.url);
  if (url.origin !== self.location.origin) return;

  event.respondWith(
    fetch(new Request(event.request.url, {
      cache: 'no-store',
      credentials: 'same-origin',
      redirect: 'follow'
    }))
      .then((resposta) => {
        if (resposta && resposta.status === 200 && resposta.type === 'basic') {
          const clone = resposta.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
        }
        return resposta;
      })
      // offline: cai pro que estiver guardado; navegação sem cache volta pro index
      .catch(() => caches.match(event.request).then((c) =>
        c || (event.request.mode === 'navigate' ? caches.match('./index.html') : undefined)
      ))
  );
});
