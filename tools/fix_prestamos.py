#!/usr/bin/env python3
"""Devuelve su ortografía española a los préstamos y nombres propios que quedaron con k/w
(«nakional» -> «nacional», «sakerdote» -> «sacerdote», «Koat» -> «Coat»).

Regla: palabra española tal cual -> ortografía española; prefijos y sufijos chuj conservan
el alfabeto de la ALMG (s-nación, sacerdote-ok, w-aceite, k-et-creyente-al). Los préstamos
adaptados que la ALMG escribe con k (alkal, kalnel, koxtal, mantekat) y los de forma no
española (serwil, kostil, wentena) no se tocan.

Necesita el texto original como referencia:  git show 2b5b0d3:CHSM.xml > original.xml
Uso: fix_prestamos.py CHSM.xml original.xml SPARV.xml salida.xml cambios.csv
"""
import re, sys, csv, collections, unicodedata
import xml.etree.ElementTree as ET

TOK = re.compile(r"[^\W\d_][\w'’]*")
BAD = re.compile(r"[cC](?![hH])|[vV]|[qQ][uU](?=[eiéíEIÉÍ])")

STEMS = """sacerdote nacional nación nacion creyente aceite bronce incienso cuarto palacio carruaje candil calle cadena
centímetro circuncidar circuncidado circuncisión camello cebada carreta carrera siclos siclo ciclo cuartel ciento cien acacia
anciano criada mercado corredor vinagre cuenta topacio avestruz llave cimiento crisólito crisoprasa cincho diácono tanque cepo
cena jacinto cigüeña coraza cuerda ónice centeno octavo crema cítara queja cincel negocio licenciado ejército nueces casia
estacte cebolla cincuenta cocina comandante castañuelas castaño castigo cinco cuarzo policía violín centavo nueve cristiano
cristal epicúreo estoico escuela dracma secretario codos parque corona coronel capitán capitan caporal capital carta cortina
culto quintal marco cuchara estaca esquina veneno copia leviatán levita canela campana campamento arquita cobre comino coral
tamarisco culantro máquina avena cálamo sicómoro navaja junco barco olivo caro
cananeo caldeo amalecita heveo saduceo cereteo quereteo ceneo araceo arvadeo cenezeo aveo maacateo cadmoneo caftoritas
casluhítas sucateo egipcio nicolaíta quenita""".split()
# partes de nombres compuestos que van en minúscula (Cades-barnea, Abel-bet-maaca...): solo palabra exacta
NAME_PARTS = set("cades neceb queramim decar casis maaca hataava melec sabactani marcabot jaacán merodac azmavet amalec berac cazín equed car".split())
# nombres que la comparación con el español no detecta sola
NAMES_EXTRA = set("""Cafira Iques Berenice Carnaim Merodac Quelub Jecutiel Melec Cedma Vaheb Parnac Evi Sicrón Emec Quislot Catat
Carta Secú Cedema Equer Jorcoam Malquiram Hamolequet Saquías Savsa Suca Ecbatana Hacatán Casifia Quelal VAW Coa Ticio Esceva
Estaquis Evodia Quimam""".split())
PREFIX = re.compile(r"^(tzey|tz|ey|in|ko|co|he|ha|qu|s|y|w|v|k|c|e|a|x)?(et)?$")

def plain(s): return ''.join(c for c in unicodedata.normalize('NFD', s.casefold()) if unicodedata.category(c) != 'Mn')
STEMS_P = sorted({plain(s) for s in STEMS}, key=len, reverse=True)
PARTS_P = {plain(s) for s in NAME_PARTS}

def fix(w):
    w = re.sub(r"[qQ][uU](?=[eiéíEIÉÍ])", lambda m: 'K' if m.group(0)[0] == 'Q' else 'k', w)
    w = re.sub(r"[cC](?![hH])", lambda m: 'K' if m.group(0) == 'C' else 'k', w)
    return re.sub(r"[vV]", lambda m: 'W' if m.group(0) == 'V' else 'w', w)

def fold(s):
    s = plain(s)
    for a, b in (('ch', 'k'), ('qu', 'k'), ('c', 'k'), ('v', 'b'), ('w', 'b'), ('z', 's'), ('th', 't'), ('ph', 'f'), ('y', 'i'), ('h', '')): s = s.replace(a, b)
    return re.sub(r'(.)\1+', r'\1', s)

def verses(root):
    d = {}
    for b in root.iter('BIBLEBOOK'):
        for c in b.iter('CHAPTER'):
            for v in c.iter('VERS'): d[(b.get('bnumber'), c.get('cnumber'), v.get('vnumber'))] = v
    return d

def restore(x):
    """x = forma original. Devuelve la forma correcta, o None si no es préstamo."""
    p = plain(x)
    if p in PARTS_P and x[0].islower(): return x
    for s in STEMS_P:
        i = p.find(s)
        if 0 <= i <= 6 and PREFIX.match(p[:i]):
            return fix(x[:i]) + x[i:i + len(s)] + fix(x[i + len(s):])
    return None

cur_p, orig_p, es_p, out_p, csv_p = sys.argv[1:6]
tree = ET.parse(cur_p); cur = verses(tree.getroot()); orig = verses(ET.parse(orig_p).getroot()); es = verses(ET.parse(es_p).getroot())

# mapa de respaldo por tipo: forma actual -> forma original más frecuente
cnt = collections.Counter(w.replace('’', "'") for v in orig.values() for w in TOK.findall(v.text or ''))
back = {}
for x, n in cnt.most_common():
    if BAD.search(x): back.setdefault(fix(x), x)

# nombres propios: con mayúscula y presentes (plegando ortografías) en el mismo capítulo del español
es_ch = collections.defaultdict(set)
for (b, c, _), v in es.items():
    es_ch[(b, c)].update(fold(w) for w in TOK.findall(v.text or '') if w[0].isupper() and len(w) > 2)
low_now = {w for v in cur.values() for w in TOK.findall(v.text or '') if w[0].islower()}
tot = collections.Counter(); hit = collections.Counter()
for (b, c, _), v in cur.items():
    for w in TOK.findall(v.text or ''):
        x = back.get(w)
        if x and x[0].isupper() and x != w:
            tot[w] += 1; f = fold(x); e = es_ch[(b, c)]
            if f in e or any(len(f) >= 5 and g[:5] == f[:5] and abs(len(g) - len(f)) <= 2 for g in e): hit[w] += 1
names = {w for w in tot if hit[w] / tot[w] >= 0.5 and w.lower() not in low_now} | {fix(n) for n in NAMES_EXTRA}

changes = collections.Counter()
for key, v in cur.items():
    o_tokens = [w.replace('’', "'") for w in TOK.findall(orig[key].text or '')] if key in orig else []
    def sub(m):
        y = m.group(0)
        x = next((o for o in o_tokens if o != y and fix(o) == y), None) or back.get(y)
        if not x or x == y: return y
        new = x if (y in names and x[0].isupper()) else restore(x)
        if new and new != y: changes[(y, new)] += 1; return new
        return y
    v.text = TOK.sub(sub, v.text or '')
tree.write(out_p, encoding='utf-8', xml_declaration=True)
with open(csv_p, 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f); w.writerow(['antes', 'despues', 'veces'])
    for (a, b), n in sorted(changes.items(), key=lambda r: -r[1]): w.writerow([a, b, n])
print(f"{sum(changes.values())} usos / {len(changes)} formas")
