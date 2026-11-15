/* Biblia Chuj · visor. Lee la API estática: books.json, {libro}/{n}.json, {libro}.json, es/{libro}.json */
(() => {
'use strict';
const $ = (s, r = document) => r.querySelector(s);
const LS = {
  get: (k, d) => { try { const v = localStorage.getItem(k); return v === null ? d : JSON.parse(v); } catch { return d; } },
  set: (k, v) => { try { localStorage.setItem(k, JSON.stringify(v)); } catch {} },
};
const SIZES = [1.05, 1.15, 1.25, 1.45, 1.7];          // rem
const NOMBRES_FIX = { 'GALATAS': 'Gálatas' };
const apos = t => t.replace(/['’]/g, 'ʼ');            // el apóstrofo es una letra del chuj: ʼ no parte palabras
const disp = t => apos(t).replace(/(^|\s)--(?=\S)/g, '$1—');   // la raya de diálogo se muestra como —; el dato no cambia
const nombre = b => NOMBRES_FIX[b.name] || b.name.toLowerCase().replace(/(^|\s)(\S)/g, (_, a, c) => a + c.toUpperCase());
const esc = s => s.replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

const forzado = new URLSearchParams(location.search).get('tema');
const st = { books: [], by: {}, es: LS.get('es', false), size: LS.get('size', 2), tema: forzado || LS.get('tema', 'auto'), sel: new Set(), cur: null, idx: null };
const el = { ref: $('#ref-text'), lec: $('#lectura'), lib: $('#libros'), bus: $('#buscar'), est: $('#estado'), acc: $('#acciones'), accRef: $('#acc-ref'),
  prev: $('#rail-prev'), next: $('#rail-next'), libros: $('#rail-libros'), rail: $('#rail') };

/* ---------- datos ---------- */
async function getJSON(url) { const r = await fetch(url); if (!r.ok) throw new Error(url + ' ' + r.status); return r.json(); }
const bookCache = new Map(), esCache = new Map();
async function getBook(short, es = false) {
  const c = es ? esCache : bookCache; if (!c.has(short)) c.set(short, getJSON(`${es ? 'es/' : ''}${short}.json`).catch(e => { c.delete(short); throw e; }));
  return c.get(short);
}
async function getChapter(short, n) {
  try { return await getJSON(`${short}/${n}.json`); }
  catch { const b = await getBook(short), ch = b.chapters.find(c => c.c === n); if (!ch) throw new Error('capítulo'); // sin red: sale del libro guardado
    return { chapter: String(n), aligned: ch.aligned, verses: ch.v.map(([number, text]) => ({ number: String(number), text })) }; }
}

/* ---------- preferencias ---------- */
function aplicarPrefs() {
  document.documentElement.style.setProperty('--leer', SIZES[st.size] + 'rem');
  document.documentElement.dataset.tema = st.tema;
  $('#size-out').textContent = `${st.size + 1} de ${SIZES.length}`;
  $('#size-down').disabled = st.size === 0; $('#size-up').disabled = st.size === SIZES.length - 1;
  $('#es-toggle').checked = st.es;
  const r = document.querySelector(`input[name=tema][value=${st.tema}]`); if (r) r.checked = true;
  const tc = document.querySelector('meta[name=theme-color]');
  tc.content = getComputedStyle(document.documentElement).getPropertyValue('--sal-negra').trim() || '#1F1A17';
}
$('#size-down').onclick = () => { st.size = Math.max(0, st.size - 1); LS.set('size', st.size); aplicarPrefs(); };
$('#size-up').onclick = () => { st.size = Math.min(SIZES.length - 1, st.size + 1); LS.set('size', st.size); aplicarPrefs(); };
document.querySelectorAll('input[name=tema]').forEach(i => i.onchange = () => { st.tema = i.value; LS.set('tema', st.tema); aplicarPrefs(); });
$('#es-toggle').onchange = e => { st.es = e.target.checked; LS.set('es', st.es); if (st.cur) leer(st.cur.short, st.cur.n, st.cur.v, true); };

/* ---------- vistas ---------- */
function vista(cual) {
  el.lec.hidden = cual !== 'lec'; el.lib.hidden = cual !== 'lib'; el.bus.hidden = cual !== 'bus';
  el.est.textContent = ''; el.est.className = 'estado'; cerrarAcciones();
  el.rail.querySelectorAll('a').forEach(a => a.removeAttribute('aria-current'));
  el.prev.style.visibility = el.next.style.visibility = cual === 'lec' ? '' : 'hidden';   // en Libros y Buscar solo queda «Libros»
}
function mensaje(txt, error, reintentar) {
  el.est.className = 'estado' + (error ? ' error' : ''); el.est.textContent = txt;
  if (reintentar) { const b = document.createElement('button'); b.className = 'btn'; b.textContent = 'Reintentar'; b.onclick = reintentar; el.est.append(document.createElement('br'), b); }
}
const ruta = (short, n, v) => `#/${short}/${n}${v ? '/' + v : ''}`;

async function leer(short, n, v, mantener) {
  const b = st.by[short]; if (!b) return irInicio();
  n = Math.min(Math.max(1, n), b.chapters);
  vista('lec'); if (!mantener) { el.lec.hidden = true; mensaje('Cargando…'); }
  let data, es = null;
  try { data = await getChapter(short, n); }
  catch { el.lec.hidden = true; return mensaje('No se pudo cargar este capítulo. Si no tienes señal, abre «Libros» → el libro → «Guardar sin conexión» cuando la tengas.', true, () => leer(short, n, v)); }
  if (st.es && data.aligned) { try { const eb = await getBook(short, true); es = eb.chapters.find(c => c.c === n); } catch {} }
  const esMap = es ? Object.fromEntries(es.v.map(([a, t]) => [a, t])) : null;
  st.cur = { short, n, v }; LS.set('ultimo', { short, n });
  const nm = nombre(b);
  el.ref.textContent = `${nm} ${n}`; $('#ref').setAttribute('aria-label', `${nm} ${n}, elegir libro y capítulo`); document.title = `${nm} ${n} · Biblia Chuj`;
  let html = `<h1>${esc(nm)} <span class="cap">${n}</span></h1>`;
  if (st.es && !data.aligned) html += `<p class="aviso" lang="es"><strong>Sin comparación.</strong> Este capítulo tiene ${data.verses.length} versículos y el español ${data.es_verses || 'otro número de'}: no coinciden, y mostrarlos juntos sería engañoso.</p>`;
  html += data.verses.map(x => `<p class="v" id="v${x.number}" data-n="${x.number}"><button class="n" type="button" aria-pressed="false" title="Seleccionar versículo ${x.number}">${x.number}</button><span class="t">${esc(disp(x.text))}</span>${esMap && esMap[x.number] ? `<span class="es" lang="es">${esc(esMap[x.number])}</span>` : ''}</p>`).join('');
  el.lec.innerHTML = html; el.lec.hidden = false; el.est.textContent = '';
  el.lec.classList.remove('entra'); void el.lec.offsetWidth; if (!mantener) el.lec.classList.add('entra');
  st.sel.clear();
  if (v) { const t = $('#v' + v); if (t) { setSel([String(v)]); t.scrollIntoView({ block: 'center' }); } } else if (!mantener) window.scrollTo(0, 0);
  rail(short, n); prefetch(short, n);
}
function rail(short, n) {
  const b = st.by[short], i = st.books.indexOf(b);
  const ant = n > 1 ? [short, n - 1] : i > 0 ? [st.books[i - 1].short_name, st.books[i - 1].chapters] : null;
  const sig = n < b.chapters ? [short, n + 1] : i < st.books.length - 1 ? [st.books[i + 1].short_name, 1] : null;
  const f = (a, x, lbl) => { a.querySelector('span').textContent = x ? `${x[0]} ${x[1]}` : ''; if (x) { a.href = ruta(x[0], x[1]); a.setAttribute('aria-label', `${x[0]} ${x[1]}, ${lbl.toLowerCase()} (${nombre(st.by[x[0]])} ${x[1]})`); a.removeAttribute('aria-disabled'); } else a.setAttribute('aria-disabled', 'true'); };
  f(el.prev, ant, 'Capítulo anterior'); f(el.next, sig, 'Capítulo siguiente');
  el.libros.href = '#/libros/' + short;
}
function prefetch(short, n) { const b = st.by[short]; if (n < b.chapters) fetch(`${short}/${n + 1}.json`).catch(() => {}); }

/* selección de versículos */
function setSel(list) {
  st.sel = new Set(list);
  el.lec.querySelectorAll('.v').forEach(p => { const on = st.sel.has(p.dataset.n); p.classList.toggle('sel', on); p.querySelector('.n').setAttribute('aria-pressed', on); });
  if (!st.sel.size) return cerrarAcciones();
  const nums = [...st.sel].map(Number).sort((a, b) => a - b), b = st.by[st.cur.short];
  el.accRef.textContent = `${b.short_name} ${st.cur.n}:${nums.length > 1 ? nums[0] + '–' + nums[nums.length - 1] : nums[0]}`;
  el.acc.hidden = false;
}
function cerrarAcciones() { el.acc.hidden = true; st.sel.clear(); el.lec.querySelectorAll('.v.sel').forEach(p => { p.classList.remove('sel'); p.querySelector('.n').setAttribute('aria-pressed', 'false'); }); }
el.lec.addEventListener('click', e => { const p = e.target.closest('.v'); if (!p) return; const s = new Set(st.sel); s.has(p.dataset.n) ? s.delete(p.dataset.n) : s.add(p.dataset.n); setSel([...s]); });
function textoSel() {
  const nums = [...st.sel].map(Number).sort((a, b) => a - b);
  const txt = nums.map(n => `${nums.length > 1 ? n + ' ' : ''}${$('#v' + n + ' .t').textContent}`).join(' ');
  const url = location.origin + location.pathname + ruta(st.cur.short, st.cur.n, nums[0]);
  return { txt: `«${txt}»\n${$('#acc-ref').textContent} · Biblia Chuj San Mateo Ixtatán`, url };
}
$('#acc-copiar').onclick = async () => { const { txt, url } = textoSel(); try { await navigator.clipboard.writeText(txt + '\n' + url); $('#acc-ref').textContent = 'Copiado'; } catch { $('#acc-ref').textContent = 'No se pudo copiar'; } setTimeout(() => st.sel.size && setSel([...st.sel]), 1400); };
$('#acc-compartir').onclick = async () => { const { txt, url } = textoSel(); if (navigator.share) { try { await navigator.share({ text: txt, url }); } catch {} } else $('#acc-copiar').click(); };
$('#acc-cerrar').onclick = cerrarAcciones;

/* ---------- selector: retícula de cristales ---------- */
function libros(short) {
  vista('lib'); el.ref.textContent = 'Libros'; $('#ref').setAttribute('aria-label', 'Libros'); document.title = 'Libros · Biblia Chuj';
  el.libros.setAttribute('aria-current', 'page'); window.scrollTo(0, 0);
  const ult = LS.get('ultimo', null);
  if (short && st.by[short]) {
    const b = st.by[short], nm = nombre(b);
    el.lib.innerHTML = `<h1>${esc(nm)}</h1><p class="sub">${b.chapters} ${b.chapters === 1 ? 'capítulo' : 'capítulos'} · ${b.verses} versículos</p>
      <div class="retic caps entra" role="list">${Array.from({ length: b.chapters }, (_, i) => `<a class="celda" role="listitem" style="--i:${Math.min(i, 40)}" href="${ruta(short, i + 1)}"${ult && ult.short === short && ult.n === i + 1 ? ' aria-current="true"' : ''}>${i + 1}</a>`).join('')}</div>
      <button class="btn" id="guardar-libro" type="button"><svg class="ico" aria-hidden="true"><use href="#i-down"/></svg>Guardar este libro sin conexión</button><p class="nota" id="guardar-estado" role="status"></p>
      <p><a href="#/libros">Todos los libros</a></p>`;
    $('#guardar-libro').onclick = async () => { const s = $('#guardar-estado'); s.textContent = 'Guardando…'; try { await getBook(short); if (st.es) await getBook(short, true); s.textContent = 'Listo: este libro se puede leer sin conexión.'; } catch { s.textContent = 'No se pudo guardar. Revisa tu conexión.'; } };
    return;
  }
  const grupo = (t, lista) => `<h2>${t}</h2><div class="retic entra" role="list">${lista.map((b, i) => `<a class="celda${ult && ult.short === b.short_name ? ' ultimo' : ''}" role="listitem" style="--i:${Math.min(i, 40)}" href="#/libros/${b.short_name}" data-q="${esc((nombre(b) + ' ' + b.short_name).toLowerCase())}"><span class="cod">${esc(b.short_name)}</span><span class="nom">${esc(nombre(b))}</span></a>`).join('')}</div>`;
  el.lib.innerHTML = `<h1>Libros</h1><p class="sub">La Santa Biblia en chuj de San Mateo Ixtatán</p>
    ${ult && st.by[ult.short] ? `<a class="seguir" href="${ruta(ult.short, ult.n)}"><span><small>Seguir leyendo</small>${esc(nombre(st.by[ult.short]))} ${ult.n}</span><svg class="ico" aria-hidden="true"><use href="#i-next"/></svg></a>` : ''}
    <h2>Buscar un libro</h2><input class="filtro" id="filtro" type="search" placeholder="Por ejemplo: Juan" autocomplete="off" aria-label="Filtrar libros">
    <p class="sin-res" id="sin-res" hidden>Ningún libro con ese nombre.</p><div id="grupos">${grupo('Antiguo Testamento', st.books.filter(b => b.testament === 'AT'))}${grupo('Nuevo Testamento', st.books.filter(b => b.testament === 'NT'))}</div>`;
  $('#filtro').oninput = e => { const q = e.target.value.trim().toLowerCase(); let hay = 0; el.lib.querySelectorAll('.celda').forEach(c => { c.hidden = !!q && !c.dataset.q.includes(q); if (!c.hidden) hay++; }); el.lib.querySelectorAll('#grupos h2').forEach(h => h.hidden = !!q && !h.nextElementSibling.querySelector('.celda:not([hidden])')); $('#sin-res').hidden = hay > 0; };
}

/* ---------- búsqueda ---------- */
const APOS = /['’ʼ]/;
function plegar(s) { let f = '', m = []; for (let i = 0; i < s.length; i++) { const c = s[i]; if (APOS.test(c)) continue; const d = c.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase(); for (const x of d) { f += x; m.push(i); } } return { f, m }; }
async function indice(progreso) {
  if (st.idx) return st.idx; const idx = []; let n = 0;
  await Promise.all(st.books.map(async b => { const d = await getBook(b.short_name); d.chapters.forEach(c => c.v.forEach(([v, t]) => idx.push({ s: b.short_name, c: c.c, v, t, p: plegar(t) }))); progreso(++n, st.books.length); }));
  idx.sort((a, b) => st.by[a.s].number - st.by[b.s].number || a.c - b.c || a.v - b.v); return (st.idx = idx);
}
function buscar(q) {
  vista('bus'); el.ref.textContent = 'Buscar'; $('#ref').setAttribute('aria-label', 'Buscar, ir a libros'); document.title = 'Buscar · Biblia Chuj'; el.libros.setAttribute('aria-current', 'page');
  el.bus.innerHTML = `<form class="campo" role="search"><input type="search" id="q" placeholder="Una palabra en chuj" autocomplete="off" autocapitalize="off" spellcheck="false" aria-label="Buscar en la Biblia" value="${esc(q || '')}"></form><p class="info" id="info" role="status"></p><ul class="res" id="res"></ul>`;
  const inp = $('#q'), info = $('#info'), res = $('#res'); let t;
  const run = async () => {
    const termino = plegar(inp.value.trim()).f.split(/\s+/).filter(Boolean); history.replaceState(null, '', '#/buscar' + (inp.value.trim() ? '/' + encodeURIComponent(inp.value.trim()) : ''));
    if (!termino.length) { info.textContent = 'Se ignoran mayúsculas, tildes y apóstrofos: «b\'itanek» y «bitanek» dan lo mismo.'; res.innerHTML = ''; return; }
    let idx; try { idx = await indice((a, b) => info.textContent = `Preparando la búsqueda… ${a} de ${b} libros`); } catch { info.textContent = 'No se pudo cargar el texto para buscar. Revisa tu conexión.'; return; }
    if (inp.value.trim() === '' ) return;
    const hits = []; for (const e of idx) { if (termino.every(w => e.p.f.includes(w))) hits.push(e); }
    const mostrar = hits.slice(0, 150);
    info.textContent = hits.length ? `${hits.length} ${hits.length === 1 ? 'versículo' : 'versículos'}${hits.length > 150 ? ' · se muestran los primeros 150' : ''}` : 'Sin resultados.';
    res.innerHTML = mostrar.map(e => {
      const rg = []; termino.forEach(w => { let i = -1; while ((i = e.p.f.indexOf(w, i + 1)) !== -1) rg.push([e.p.m[i], e.p.m[i + w.length - 1] + 1]); });
      rg.sort((a, b) => a[0] - b[0]); let o = '', pos = 0; for (const [a, b] of rg) { if (a < pos) continue; o += esc(disp(e.t.slice(pos, a))) + '<mark>' + esc(disp(e.t.slice(a, b))) + '</mark>'; pos = b; } o += esc(disp(e.t.slice(pos)));
      return `<li><a href="${ruta(e.s, e.c, e.v)}"><div class="r">${esc(nombre(st.by[e.s]))} ${e.c}:${e.v}</div><div class="x" lang="cac">${o}</div></a></li>`; }).join('');
  };
  inp.oninput = () => { clearTimeout(t); t = setTimeout(run, 220); }; $('form', el.bus).onsubmit = e => { e.preventDefault(); run(); };
  inp.focus(); run();
}

/* ---------- rutas ---------- */
function irInicio() { const u = LS.get('ultimo', null); location.replace(u && st.by[u.short] ? ruta(u.short, u.n) : ruta(st.books[0].short_name, 1)); }
function rutear() {
  if (!st.books.length) return;
  const p = decodeURIComponent(location.hash.replace(/^#\/?/, '')).split('/');
  if (p[0] === 'libros') return libros(p[1]);
  if (p[0] === 'buscar') return buscar(p.slice(1).join('/'));
  if (p[0] && st.by[p[0]]) return leer(p[0], parseInt(p[1], 10) || 1, p[2] ? parseInt(p[2], 10) : null);
  irInicio();
}
addEventListener('hashchange', rutear);
addEventListener('keydown', e => { if (e.altKey || e.ctrlKey || e.metaKey || e.shiftKey || el.lec.hidden || /INPUT|TEXTAREA/.test(document.activeElement.tagName)) return; if (e.key === 'ArrowLeft' && !el.prev.hasAttribute('aria-disabled')) el.prev.click(); if (e.key === 'ArrowRight' && !el.next.hasAttribute('aria-disabled')) el.next.click(); if (e.key === 'Escape') cerrarAcciones(); });

/* ---------- sin conexión e instalación ---------- */
let pedirInstalar;
addEventListener('beforeinstallprompt', e => { e.preventDefault(); pedirInstalar = e; $('#fila-instalar').hidden = false; });
$('#btn-instalar').onclick = async () => { if (!pedirInstalar) return; pedirInstalar.prompt(); await pedirInstalar.userChoice; pedirInstalar = null; $('#fila-instalar').hidden = true; };
addEventListener('appinstalled', () => { $('#fila-instalar').hidden = true; });
if (/iphone|ipad/i.test(navigator.userAgent) && !navigator.standalone) $('#ios-tip').hidden = false;
$('#btn-offline').onclick = async () => {
  const s = $('#offline-estado'), btn = $('#btn-offline'); btn.disabled = true; let n = 0;
  try { for (const b of st.books) { await getBook(b.short_name); if (st.es) await getBook(b.short_name, true); s.textContent = `Guardando… ${++n} de ${st.books.length} libros`; } s.textContent = 'Listo: toda la Biblia se puede leer sin conexión.'; LS.set('offline', true); }
  catch { s.textContent = 'No se pudo terminar. Inténtalo de nuevo con mejor señal.'; } btn.disabled = false;
};
if (LS.get('offline', false)) $('#offline-estado').textContent = 'Esta Biblia ya está guardada en tu teléfono.';
if ('serviceWorker' in navigator) addEventListener('load', () => navigator.serviceWorker.register('sw.js').catch(() => {}));

/* ---------- arranque ---------- */
(async () => {
  aplicarPrefs();
  try { st.books = await getJSON('books.json'); }
  catch { return mensaje('No se pudo cargar la lista de libros. Revisa tu conexión.', true, () => location.reload()); }
  st.books.forEach(b => { b.chapters = b.chapters || 0; st.by[b.short_name] = b; });
  getJSON('version.json').then(v => { $('#version').textContent = `Texto del ${new Date(v.updated).toLocaleDateString('es', { day: 'numeric', month: 'short', year: 'numeric' })}`; }).catch(() => {});
  rutear();
})();
})();
