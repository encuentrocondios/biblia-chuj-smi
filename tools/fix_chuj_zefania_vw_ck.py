# fix_chuj_zefania_vw_ck.py
import re, sys, argparse
import xml.etree.ElementTree as ET
from typing import Set, Tuple, List

# --- Reglas básicas ---
C_NOT_CH = re.compile(r'[cC](?![hH])')   # c/C que NO forman 'ch'
V_ALL    = re.compile(r'[vV]')           # toda v/V
TOKEN_RX = re.compile(r'\b[^\s]+\b', re.UNICODE)

# Puntuación a recortar para comparar con whitelist
PUNCT_EDGES = ".,;:!?¡¿()[]{}\"'«»“”‘’—–-"

# Gentilicios / formas frecuentes a proteger (case-insensitive)
SKIP_REGEXES: List[re.Pattern] = [
    re.compile(r'^\d*corinti(?:o|a)s?$', re.I),         # corintio(s/as), 1/2Corintios pegado
    re.compile(r'^colosense(?:s)?$', re.I),             # colosense(s)
    re.compile(r'^tesalonicense(?:s)?$', re.I),         # tesalonicense(s)
    re.compile(r'^macedon(?:ia|io|ios|ia(s)?)$', re.I), # macedonia/macEdonio(s)/macedonias
    re.compile(r'^capadoci(?:a|o|os|as)$', re.I),       # capadocia/capadocio(s)/capadocias
    # agrega más si los detectas en tu edición:
    # re.compile(r'^sirio(?:s|as)?$', re.I),
    # re.compile(r'^galac(?:ia|io|ios|ias)$', re.I),  # si usas "Galacia/Galacio(s)"
]

def load_whitelist(path: str) -> Set[str]:
    if not path: return set()
    with open(path, 'r', encoding='utf-8') as f:
        return {line.strip() for line in f if line.strip()}

def canon_for_compare(tok: str) -> str:
    """
    Normaliza un token para compararlo con whitelist:
    - recorta puntuación al borde
    - elimina dígitos iniciales (p.ej. '1Corintios' -> 'Corintios')
    - casefold (insensible a mayúsculas/minúsculas y acentos de forma robusta)
    """
    t = tok.strip(PUNCT_EDGES)
    t = re.sub(r'^\d+', '', t)      # quita números iniciales (1,2,3…)
    return t.casefold()

def expand_whitelist_cases(wl: Set[str]) -> Set[str]:
    """
    Crea una versión case-insensitive/normalizada de la whitelist
    (con y sin puntuación/dígitos al inicio).
    """
    out = set()
    for w in wl:
        # Tal cual
        out.add(canon_for_compare(w))
        # variantes de caja típicas (por si hay alguna diferencia)
        out.add(canon_for_compare(w.upper()))
        out.add(canon_for_compare(w.lower()))
        out.add(canon_for_compare(w.title()))
    return out

def token_is_protected(tok: str, wl_norm: Set[str]) -> bool:
    t_norm = canon_for_compare(tok)
    if t_norm in wl_norm:
        return True
    # ¿coincide algún patrón de gentilicio/forma especial?
    for rx in SKIP_REGEXES:
        if rx.match(t_norm):
            return True
    return False

def fix_token(tok: str, skip_title: bool, wl_norm: Set[str]) -> Tuple[str,int]:
    # Respeta whitelist y patrones
    if token_is_protected(tok, wl_norm):
        return tok, 0

    # Opcional: saltar posibles nombres propios por forma (TitleCase/MAYÚSCULAS)
    if skip_title and (tok.istitle() or tok.isupper()):
        return tok, 0

    changes = 0
    # 1) c/C -> k/K (cuando no es 'ch')
    def ck_repl(m): return 'K' if m.group(0).isupper() else 'k'
    new_tok, n1 = C_NOT_CH.subn(ck_repl, tok)
    changes += n1

    # 2) v/V -> w/W
    def vw_repl(m): return 'W' if m.group(0).isupper() else 'w'
    newer_tok, n2 = V_ALL.subn(vw_repl, new_tok)
    changes += n2

    return newer_tok, changes

def fix_text(s: str, skip_title: bool, wl_norm: Set[str]) -> Tuple[str,int]:
    if not s: return s, 0
    total = 0
    def sub_token(m):
        nonlocal total
        tok = m.group(0)
        new_tok, n = fix_token(tok, skip_title, wl_norm)
        total += n
        return new_tok
    return TOKEN_RX.sub(sub_token, s), total

def process_xml(inp: str, outp: str, skip_title: bool, wl: Set[str]) -> int:
    tree = ET.parse(inp); root = tree.getroot()
    wl_norm = expand_whitelist_cases(wl)
    total = 0
    for el in root.iter():
        # SOLO tocamos .text y .tail; jamás .tag ni .attrib
        if el.text:
            el.text, n = fix_text(el.text, skip_title, wl_norm); total += n
        if el.tail:
            el.tail, n = fix_text(el.tail, skip_title, wl_norm); total += n
    tree.write(outp, encoding='utf-8', xml_declaration=True)
    return total

def main():
    ap = argparse.ArgumentParser(description="Chuj: corrige v→w y c→k (sin tocar 'ch') en XML Zefania; protege whitelist y gentilicios.")
    ap.add_argument("input", help="CHSM.xml")
    ap.add_argument("output", help="CHSM_fixed.xml")
    ap.add_argument("--skip-titlecase", action="store_true",
                    help="No cambia tokens Tipo Título o MAYÚSCULAS (posibles nombres propios).")
    ap.add_argument("--whitelist", help="Archivo con nombres/formas a preservar (uno por línea).")
    args = ap.parse_args()
    wl = load_whitelist(args.whitelist)
    changes = process_xml(args.input, args.output, args.skip_titlecase, wl)
    print(f"Listo: {changes} reemplazos. Archivo: {args.output}")

if __name__ == "__main__":
    main()
