#!/usr/bin/env python3
"""Ortografía ALMG (1987): sin c, qu, v en palabras chuj.
Una palabra se deja intacta (y se reporta) si parece nombre propio o préstamo:
aparece en el versículo equivalente de Reina-Valera (SPARV.xml), por igualdad o por prefijo de 5 letras.
Uso: fix_chuj_ortografia.py CHSM.xml SPARV.xml salida.xml cambios.csv pendientes.csv"""
import re, sys, csv, unicodedata, collections
import xml.etree.ElementTree as ET

TOK = re.compile(r"[^\W\d_][\w'’]*")
BAD = re.compile(r"[cC](?![hH])|[vV]|[qQ][uU](?=[eiéíEIÉÍ])")

def norm(s):
    # Pliega acentos y ortografías antiguas del español (ch/qu/c -> k, v -> b, z -> s, letras dobles) para comparar nombres
    s = ''.join(c for c in unicodedata.normalize('NFD', s.casefold()) if unicodedata.category(c) != 'Mn')
    s = s.replace('ch', 'k').replace('qu', 'k').replace('c', 'k').replace('v', 'b').replace('z', 's').replace("’", "'")
    return re.sub(r'(.)\1+', r'\1', s)

def load(p):
    d = {}
    root = p if isinstance(p, ET.Element) else ET.parse(p).getroot()
    for b in root.iter('BIBLEBOOK'):
        for c in b.iter('CHAPTER'):
            for v in c.iter('VERS'): d[(b.get('bnumber'), c.get('cnumber'), v.get('vnumber'))] = v
    return d

# Daños del intento anterior de corrección (regex con \b que partía en el apóstrofo): d'a -> d'ha, b'a -> b'ha, t'a -> t'ha...
ARTIFACTS = {"d'ha","b'ha","sb'ha","t'ha","snhusjitz'ha","lheb'heb'ok","stz'ha","yaxk'ha","nhustz'ha","nhusjitz'ha","nhusantz'ha",
             "quilkob'ha","mheb'haxo","k'haxo","ch'akb'ha","snhustz'ha","tz'ha","snhusjipaxtz'ha","kunhkunhb'haxo","nhuschajtz'ha","nab'ha","snhusantz'ha","nhusjoktz'ha"}
# Nombres propios que el intento anterior adaptó (David -> Dawid...): se devuelven a su ortografía original
NAME_REVERT = {'Dawid':'David','Ewa':'Eva','Sarwia':'Sarvia','Níniwe':'Nínive','Askalón':'Ascalón','Hawila':'Havila','Azmawet':'Azmavet',
               'Sekanías':'Secanías','Silwano':'Silvano','Ticwa':'Ticva','Bigwai':'Bigvai','Arwad':'Arvad','Hawot':'Havot',
               'Parwaim':'Parvaim','Dodawa':'Dodava','Bawai':'Bavai','Nikanor':'Nicanor'}
# Cortas y ambiguas con palabras chuj: solo si el versículo en español trae el nombre
NAME_REVERT_COND = {'Ewa':'Eva','Ewi':'Evi','Awa':'Ava','Sewa':'Seva'}

# Correcciones de palabra completa respaldadas por la ALMG (Gramática descriptiva: «Hatoni» = «Eso es»; «haton» aparece 30 veces y «aton» ninguna)
WORD_FIXES = {'aton': 'haton', 'atoni': 'hatoni',
              # confirmadas por el usuario el 15-nov-2026 y atestiguadas con h en la ALMG (uke', oye', olan y owal NO llevan h)
              'axo': 'haxo', "ata'": "hata'", 'ato': 'hato', "et'ok": "het'ok", "eyet'ok": "heyet'ok", "anheja'": "hanheja'", 'alan': 'halan', 'oyan': 'hoyan',
              'axonhej': 'haxonhej', 'alani': 'halani', "anhejtona'": "hanhejtona'",
              # el usuario (15-nov-2026): «la ALMG manda» para las de un solo registro
              'ilani': 'hilani', 'achxo': 'hachxo', 'eyaj': 'heyaj', 'eyik': 'heyik', "eyila'": "heyila'", 'ama': 'hama', 'eyilani': 'heyilani',
              'elxi': 'helxi', 'into': 'hinto', 'eyilnak': 'heyilnak', "et'nak": "het'nak", 'inye': 'hinye', "uxluche'": "huxluche'", "ab'nak": "hab'nak", 'ilnak': 'hilnak'}

# q' (ortografía antigua) = k'. Ante e/i se escribía q'u: suk'uq'ui -> suk'uk'i. También se deshace «k'ue/k'ui»,
# resto de un reemplazo anterior que dejó la u (b'ak'uinh -> b'ak'inh). La ALMG no tiene ningún k'ue/k'ui.
GLOTAL_Q = [(re.compile(r"[qQ]'[uU](?=[eiéíEIÉÍ])"), lambda m: "K'" if m.group(0)[0] == 'Q' else "k'"),
            (re.compile(r"[qQ]'"), lambda m: "K'" if m.group(0)[0] == 'Q' else "k'"),
            (re.compile(r"(?<=[kK]')[uU](?=[eiéíEIÉÍ])"), lambda m: '')]
def fix_glotal(w):
    if w == "sk'uej": return w
    for rx, rep in GLOTAL_Q: w = rx.sub(rep, w)
    return w

def fix(w):
    def qu(m): return 'K' if m.group(0)[0] == 'Q' else 'k'
    w = re.sub(r"[qQ][uU](?=[eiéíEIÉÍ])", qu, w)
    w = re.sub(r"[cC](?![hH])", lambda m: 'K' if m.group(0) == 'C' else 'k', w)
    w = re.sub(r"[vV]", lambda m: 'W' if m.group(0) == 'V' else 'w', w)
    return w

def is_spanish(w, es_words):
    n = norm(w)
    if n in es_words: return True
    if len(n) >= 5:
        p = n[:5]
        return any(len(e) >= 5 and e[:5] == p for e in es_words)
    return False

inp, es, outp, ch_csv, pend_csv = sys.argv[1:6]
chuj = ET.parse(inp); es_v = load(es)
changes = collections.Counter(); pending = collections.Counter()
verses = load(chuj.getroot())
# Pasada 1: una forma que coincide con el español en CUALQUIER versículo se protege en todos (nombres, préstamos)
protected = set()
# Nombres propios: capitalizada, sin forma minúscula, y mayormente en medio de oración
low = set(); capn = collections.Counter(); midn = collections.Counter()
for v in verses.values():
    t = v.text or ''
    for m in TOK.finditer(t):
        w = m.group(0)
        if not w[0].isupper(): low.add(norm(w)); continue
        capn[w] += 1
        pre = t[:m.start()].rstrip()
        if pre and pre[-1] not in '.;:?!¿¡"“«': midn[w] += 1
protected = set()
# Lista manual de nombres/préstamos (una por línea) junto al script, si existe
import os
extra = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'nombres.txt')
if os.path.exists(extra):
    protected |= {l.strip() for l in open(extra, encoding='utf-8') if l.strip() and not l.startswith('#')}
for key, v in verses.items():
    esw = {norm(x) for x in TOK.findall(es_v[key].text or '')} if key in es_v else set()
    for w in TOK.findall(v.text or ''):
        if BAD.search(w) and is_spanish(w, esw): protected.add(w)
for key, v in verses.items():
    t = v.text or ''
    esw = {norm(x) for x in TOK.findall(es_v[key].text or '')} if key in es_v else set()
    es_plain = {''.join(c for c in unicodedata.normalize('NFD', x.casefold()) if unicodedata.category(c) != 'Mn') for x in TOK.findall(es_v[key].text or '')} if key in es_v else set()
    def sub0(m):
        w = m.group(0).replace('’', "'")
        if w.casefold() in ARTIFACTS: w = re.sub(r"(?<=')[hH]", '', w)
        w = fix_glotal(w.replace("d'", "t'").replace("D'", "T'"))
        if w.casefold() in WORD_FIXES: w = ('H' if w[0].isupper() else 'h') + WORD_FIXES[w.casefold()][1:]
        if w in NAME_REVERT: return NAME_REVERT[w]
        if w in NAME_REVERT_COND and NAME_REVERT_COND[w].casefold() in es_plain: return NAME_REVERT_COND[w]
        if not BAD.search(w): return w
        if w in protected: pending[w] += 1; return w
        return fix(w)
    def sub(m):
        o, n = m.group(0), sub0(m)
        if n != o: changes[(o, n)] += 1
        return n
    v.text = TOK.sub(sub, t).replace('’', "'")  # un solo apóstrofo (') en todo el texto
chuj.write(outp, encoding='utf-8', xml_declaration=True)
with open(ch_csv, 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f); w.writerow(['antes', 'despues', 'veces'])
    for (a, b), c in sorted(changes.items(), key=lambda x: -x[1]): w.writerow([a, b, c])
with open(pend_csv, 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f); w.writerow(['palabra', 'veces'])
    for a, c in sorted(pending.items(), key=lambda x: -x[1]): w.writerow([a, c])
print(f"cambios: {sum(changes.values())} usos / {len(changes)} formas; pendientes (nombres/préstamos): {sum(pending.values())} usos / {len(pending)} formas")
