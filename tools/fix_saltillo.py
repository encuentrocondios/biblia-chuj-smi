#!/usr/bin/env python3
"""Saltillo entre vocales: en chuj dos vocales no van juntas (ALMG: lu'um, cha'anh, k'o'ol).

- Dos vocales IGUALES en una palabra chuj -> se inserta el saltillo (k'een -> k'e'en).
- Dos vocales DISTINTAS -> solo las palabras de tools/saltillo_almg.tsv, que la ALMG trae con saltillo
  (yaelal -> ya'elal). Las demás quedan para revisión: a veces va h (k'ual / k'uhal) o es un préstamo.
- Préstamo terminado en vocal + sufijo chuj (-al, -il, -ok): saltillo en la frontera (spuertail -> spuerta'il;
  la ALMG trae anma'il). Dentro de la palabra española no se toca nada (tiempo, israel).
- Raíces con forma propia en la ALMG: tiknaik -> tikne'ik («ahora»), yaelal -> yahelal («enfermedad», Gramática normativa).
No se tocan palabras españolas ni nombres propios.
Uso: fix_saltillo.py CHSM_fixed.xml SPARV.xml salida.xml cambios.csv
"""
import re, sys, csv, os, collections, unicodedata
import xml.etree.ElementTree as ET
TOK = re.compile(r"[^\W\d_][\w'’]*")
ALFA = re.compile(r"^(?:b'|ch'?|k'?|t'?|tz'?|nh|[aeioujlmnprswxyh'])+$")
FIN = '.;:?!¿¡"“«-—'
def plain(s): return ''.join(c for c in unicodedata.normalize('NFD', s.casefold()) if unicodedata.category(c) != 'Mn')

src, es_p, out_p, csv_p = sys.argv[1:5]
es = {plain(w) for v in ET.parse(es_p).getroot().iter('VERS') for w in TOK.findall(v.text or '')}
def espanol(w):
    p = plain(w)
    return p in es or any(p[i:] in es for i in (1, 2) if len(p) - i >= 5) or any(p[:-i] in es for i in (2, 3, 4) if len(p) - i >= 5)
lista = {}
for l in open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'saltillo_almg.tsv'), encoding='utf-8'):
    if l.strip() and not l.startswith('#'): a, b = l.rstrip('\n').split('\t'); lista[a] = b

tree = ET.parse(src); vs = list(tree.getroot().iter('VERS'))
cnt = collections.Counter(); nom = collections.Counter()
for v in vs:
    t = (v.text or '').replace('’', "'")
    for m in TOK.finditer(t):
        w = m.group(0); pre = t[:m.start()].rstrip()
        if w[0].isupper() and pre and pre[-1] not in FIN: nom[w.lower()] += 1
        else: cnt[w.lower()] += 1
RAICES = {"tiknaik": "tikne'ik", "ya'elal": "yahelal", "yaelal": "yahelal"}
PRE = ['eyet', 'yet', 'wet', 'ket', 'et', 'ey', 'ko', 'he', 'in', 's', 'y', 'w', 'k', 'e', 'a', '']
ADAPT = {'kaxa', 'palta', 'ora', 'anima', 'xila', 'mexa'}          # préstamos ya adaptados al chuj
def sufijo(w):
    for m in re.finditer(r"(?=[aeiouáéíóú](al|il|ok))", w):
        i = m.start(); stem = w[:i + 1]
        for p in PRE:
            if stem.startswith(p):
                r = plain(stem[len(p):])
                if (len(r) >= 4 and r in es) or r in ADAPT: return stem + "'" + w[i + 1:]
    return None
mapa = {}
for w, n in cnt.items():
    if nom[w] > n or len(w) < 2: continue
    g = w
    for a, b in RAICES.items(): g = g.replace(a, b)
    g = sufijo(g) or g
    if g != w: mapa[w] = g
for w, n in cnt.items():
    if nom[w] > n or len(w) < 2 or not ALFA.match(w) or espanol(w): continue
    g = lista.get(w) or re.sub(r"([aeiou])(?=\1)", r"\1'", w)
    if g != w and w not in mapa: mapa[w] = g
cambios = collections.Counter()
for v in vs:
    t = (v.text or '').replace('’', "'")
    def sub(m):
        w = m.group(0); g = mapa.get(w.lower())
        if not g: return w
        pre = t[:m.start()].rstrip()
        if w[0].isupper() and pre and pre[-1] not in FIN: return w          # nombre propio a mitad de oración
        n = (g[0].upper() + g[1:]) if w[0].isupper() else g
        cambios[(w, n)] += 1; return n
    v.text = TOK.sub(sub, t)
tree.write(out_p, encoding='utf-8', xml_declaration=True)
with open(csv_p, 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f); w.writerow(['antes', 'despues', 'veces'])
    for (a, b), n in sorted(cambios.items(), key=lambda r: -r[1]): w.writerow([a, b, n])
print(f"{sum(cambios.values())} usos / {len(cambios)} formas")
