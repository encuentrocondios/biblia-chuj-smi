#!/usr/bin/env python3
"""Aplica tools/decisiones.tsv al texto. Uso: aplicar_decisiones.py CHSM.xml salida.xml cambios.csv"""
import re, sys, csv, os, collections
import xml.etree.ElementTree as ET
TOK = re.compile(r"[^\W\d_][\w'’]*")
reglas = []
for l in open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'decisiones.tsv'), encoding='utf-8'):
    if l.strip() and not l.startswith('#'):
        p = l.rstrip('\n').split('\t')
        if p[0] != 'queda': reglas.append((p[0], p[1], p[2]))
def caso(orig, nuevo): return nuevo[0].upper() + nuevo[1:] if orig[0].isupper() else nuevo
def aplicar(w):
    lw = w.lower()
    for tipo, a, b in reglas:
        if tipo == 'palabra' and lw == a: lw = b
        elif tipo == 'minuscula' and w == a: lw = b
        elif tipo == 'inicio' and lw.startswith(a): lw = b + lw[len(a):]
        elif tipo == 'fin' and lw.endswith(a): lw = lw[:-len(a)] + b
        elif tipo == 'contiene' and a in lw: lw = lw.replace(a, b)
    return caso(w, lw) if lw != w.lower() else w
src, out_p, csv_p = sys.argv[1:4]
tree = ET.parse(src); cambios = collections.Counter()
for v in tree.getroot().iter('VERS'):
    def sub(m):
        w = m.group(0); n = aplicar(w)
        if n != w: cambios[(w, n)] += 1
        return n
    v.text = TOK.sub(sub, (v.text or '').replace('’', "'"))
tree.write(out_p, encoding='utf-8', xml_declaration=True)
with open(csv_p, 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f); w.writerow(['antes', 'despues', 'veces'])
    for (a, b), n in sorted(cambios.items(), key=lambda r: -r[1]): w.writerow([a, b, n])
print(f"{sum(cambios.values())} usos / {len(cambios)} formas:", ' '.join(f"{a}>{b}:{n}" for (a, b), n in sorted(cambios.items(), key=lambda r: -r[1])[:30]))
