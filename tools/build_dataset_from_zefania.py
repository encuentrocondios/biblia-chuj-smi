#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
build_dataset_from_zefania.py

Uso:
  python build_dataset_from_zefania.py \
    --chuj CHSMI_fixed.xml \
    --es   LAT.xml \
    --out  data/parallel.csv \
    --logs logs/

Salida:
  - data/parallel.csv         (es, ch, ref, book_code, book_name_es, book_name_ch)
  - logs/unmatched_ch.csv
  - logs/unmatched_es.csv
  - logs/diff_by_book.csv
  - logs/diff_by_chapter.csv
"""

import argparse
import csv
import os
import re
import unicodedata
import xml.etree.ElementTree as ET
from collections import defaultdict, Counter
from pathlib import Path

import pandas as pd


# ---------------------------
# Utilidades de normalización
# ---------------------------


ROMAN_RE = re.compile(r"^(?i:M{0,4}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3}))$")

ORDINAL_MAP = {
    # ordinales comunes
    "PRIMERO":"1","PRIMERA":"1","1A":"1","1º":"1","1ª":"1","I":"1",
    "SEGUNDO":"2","SEGUNDA":"2","2A":"2","2º":"2","2ª":"2","II":"2",
    "TERCERO":"3","TERCERA":"3","3A":"3","3º":"3","3ª":"3","III":"3",
}

FILLER_TOKENS = {
    # quitar palabras que no forman parte del nombre canónico
    "EVANGELIO","SEGUN","SEGÚN","SANTO","SANTA","SAN","STA","ST","SN","S",
    "DEL","DE","APOSTOL","APÓSTOL","CARTA","EPISTOLA","EPÍSTOLA"
}

NUM_PREFIXES = {
    # español
    "PRIMERO": "1", "PRIMERA": "1", "1A": "1", "1º": "1", "1ª": "1",
    "SEGUNDO": "2", "SEGUNDA": "2", "2A": "2", "2º": "2", "2ª": "2",
    "TERCERO": "3", "TERCERA": "3", "3A": "3", "3º": "3", "3ª": "3",
    # a veces ponen "I", "II", "III"
    "I": "1", "II": "2", "III": "3",
}

def strip_accents(s: str) -> str:
    return "".join(ch for ch in unicodedata.normalize("NFD", s)
                   if unicodedata.category(ch) != "Mn")

def normalize_book_title(name: str) -> str:
    """
    Devuelve un código canónico (p.ej., MAT, 1PE, JUA, ABD, etc.).
    Soporta '1 Samuel', '2 Reyes', '1 Corintios', '1 Tesalonicenses',
    '1 Timoteo', '1/2 Pedro', variantes con 'San', 'Carta de', etc.
    """
    if not name:
        return ""

    s = strip_accents(name).upper()
    s = re.sub(r"[^\w\s]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    if not s:
        return ""

    toks = s.split()

    # ---- 1) Detecta ordinal (ahora también '1', '2', '3') ----
    ordinal = ""
    head = toks[0]
    if head in {"1","2","3"}:
        ordinal = head
        toks = toks[1:]
    elif head in ORDINAL_MAP:  # PRIMERA/SEGUNDA/TERCERA/1ª/1º/I/II/III
        ordinal = ORDINAL_MAP[head]
        toks = toks[1:]
    elif ROMAN_RE.match(head or ""):
        romans = {"I":"1","II":"2","III":"3"}
        ordinal = romans.get(head, "")
        toks = toks[1:]

    # ---- 2) Quita “relleno” (SAN/STA/SANTO/SANTA/EVANGELIO/SEGUN/DE/DEL/...) ----
    toks = [t for t in toks if t not in FILLER_TOKENS]

    base = "".join(toks)  # p.ej. 'SAMUEL', 'REYES', 'CRONICAS', 'CORINTIOS', 'PEDRO', 'JUAN'

    BOOK_ALIASES = {
        # Pentateuco
        "GENESIS":"GEN","GEN":"GEN","GN":"GEN",
        "EXODO":"EXO","EX":"EXO",
        "LEVITICO":"LEV","LEV":"LEV",
        "NUMEROS":"NUM","NUM":"NUM",
        "DEUTERONOMIO":"DEU","DEUT":"DEU","DT":"DEU",
        # Históricos
        "JOSUE":"JOS","JOS":"JOS",
        "JUECES":"JUE","JUE":"JUE",
        "RUT":"RUT",
        "SAMUEL":"SA",           # usa ordinal -> 1SA/2SA
        "REYES":"RE",            # usa ordinal -> 1RE/2RE
        "CRONICAS":"CR",         # usa ordinal -> 1CR/2CR
        "ESDRAS":"ESD",
        "NEHEMIAS":"NEH",
        "ESTER":"EST",
        # Poéticos / sapienciales
        "JOB":"JOB",
        "SALMOS":"SAL","SALMO":"SAL","SAL":"SAL","PSA":"SAL",
        "PROVERBIOS":"PRO","PR":"PRO",
        "ECLESIASTES":"ECL","QOHELET":"ECL","COHELET":"ECL",
        "CANTARDELOSCANTARES":"CAN","CANTARES":"CAN","CANTAR":"CAN","CANT":"CAN",
        # Profetas mayores
        "ISAIAS":"ISA",
        "JEREMIAS":"JER",
        "LAMENTACIONES":"LAM",
        "EZEQUIEL":"EZE",
        "DANIEL":"DAN",
        # Profetas menores
        "OSEAS":"OSE",
        "JOEL":"JOE",
        "AMOS":"AMO",
        "ABDIAS":"ABD","ABDIA":"ABD","OBDIAS":"ABD","ABD":"ABD",
        "JONAS":"JON",
        "MIQUEAS":"MIQ",
        "NAHUM":"NAH",
        "HABACUC":"HAB",
        "SOFONIAS":"SOF",
        "HAGEO":"HAG",
        "ZACARIAS":"ZAC",
        "MALAQUIAS":"MAL",
        # Deuterocanónicos (si aplica en tu corpus)
        "TOBIAS":"TOB",
        "JUDIT":"JDT",
        "BARUC":"BAR",
        "SABIDURIA":"SAB","SAB":"SAB",
        "ECLESIASTICO":"SIR","SIRACIDA":"SIR","SIRACIDES":"SIR","SIR":"SIR",
        "MACABEOS":"MA",         # usa ordinal -> 1MA/2MA
        # Evangelios + Hechos
        "MATEO":"MAT","SANMATEO":"MAT",
        "MARCOS":"MAR","SANMARCOS":"MAR",
        "LUCAS":"LUC","SANLUCAS":"LUC",
        "JUAN":"JUA","SANJUAN":"JUA",  # ojo: sin ordinal => Evangelio
        "HECHOS":"HCH","HECHOSDELOSAPOSTOLES":"HCH","HCH":"HCH",
        # Paulinas
        "ROMANOS":"ROM","RM":"ROM",
        "CORINTIOS":"CO",        # usa ordinal -> 1CO/2CO
        "GALATAS":"GAL",
        "EFESIOS":"EFE",
        "FILIPENSES":"FLP",
        "COLOSENSES":"COL",
        "TESALONICENSES":"TS",   # usa ordinal -> 1TS/2TS
        "TIMOTEO":"TI",          # usa ordinal -> 1TI/2TI
        "TITO":"TIT",
        "FILEMON":"FLM",
        # Generales
        "HEBREOS":"HEB",
        "SANTIAGO":"STG","SANT":"STG",
        "PEDRO":"PE","SANPEDRO":"PE",  # usa ordinal -> 1PE/2PE
        "JUDAS":"JUD","SANJUDAS":"JUD",
        "APOCALIPSIS":"APO","REVELACION":"APO","REVELACIONES":"APO","AP":"APO",
    }

    # ---- 3) Series que requieren ordinal para el código final ----
    if base in {"SAMUEL","REYES","CRONICAS","CORINTIOS","TESALONICENSES","TIMOTEO","MACABEOS","PEDRO","JUAN"} and ordinal:
        root = BOOK_ALIASES.get(base, base)
        # 'JUAN' con ordinal son las cartas: 1JN/2JN/3JN (no el Evangelio)
        if base == "JUAN":
            return f"{ordinal}JN"
        return f"{ordinal}{root}"

    # ---- 4) Alias directo (incluye “SAN MATEO”, “SAN JUDAS”, “ABDÍAS”, etc.) ----
    if base in BOOK_ALIASES:
        return BOOK_ALIASES[base]

    # ---- 5) Caso residual: “SANXXXX” sin ordinal (por si quedó) ----
    if base.startswith("SAN") and base[3:] in BOOK_ALIASES:
        return BOOK_ALIASES[base[3:]]

    # ---- 6) Fallback -> nombre sin espacios (quedará reportado como “no reconocido”) ----
    return base
# ---------------------------
# Parseadores de tus formatos
# ---------------------------

def itertext(elem):
    # Une todo el texto dentro del elemento (incluye hijos)
    return "".join(elem.itertext()).strip()

def parse_chuj_xml(path: str):
    """
    Formato (ejemplo):
    <XMLBIBLE>
      <BIBLEBOOK bnumber="1" bname="GÉNESIS" bsname="Gn">
        <CHAPTER knumber="1">  # a veces cnumber, a veces knumber
          <VERS vnumber="1">En el principio...</VERS>
    Devuelve lista de dicts: book_code, book_name, book_idx, chapter, verse, text
    """
    tree = ET.parse(path)
    root = tree.getroot()
    rows = []
    book_idx = 0
    for b in root.findall(".//BIBLEBOOK"):
        book_idx += 1
        bnum = b.get("bnumber")  # puede venir, pero no confiamos 100%
        bname = b.get("bname") or b.get("bsname") or ""
        book_code = normalize_book_title(bname or "")
        for c in b.findall("./CHAPTER"):
            cnum = c.get("cnumber") or c.get("knumber") or "0"
            try:
                cnum = int(cnum)
            except:
                continue
            verses = list(c.findall("./VERS")) or list(c.findall("./VERSE"))
            for v in verses:
                vnum = v.get("vnumber") or "0"
                try:
                    vnum = int(vnum)
                except:
                    continue
                text = itertext(v)
                if not text:
                    continue
                rows.append({
                    "book_code": book_code,
                    "book_name": bname,
                    "book_idx": int(bnum) if (bnum and bnum.isdigit()) else book_idx,
                    "chapter": cnum,
                    "verse": vnum,
                    "text": text,
                })
    return pd.DataFrame(rows)

def parse_lat_xml(path: str):
    """
    Formato (ejemplo):
    <bible>
      <b n="Génesis">
        <c n="1">
          <v n="1">En el principio...</v>
    Devuelve lista de dicts: book_code, book_name, book_idx, chapter, verse, text
    """
    tree = ET.parse(path)
    root = tree.getroot()
    rows = []
    book_idx = 0
    for b in root.findall(".//b"):
        book_idx += 1
        bname = b.get("n") or ""
        book_code = normalize_book_title(bname)
        for c in b.findall("./c"):
            cnum = c.get("n") or "0"
            try:
                cnum = int(cnum)
            except:
                continue
            for v in c.findall("./v"):
                vnum = v.get("n") or "0"
                try:
                    vnum = int(vnum)
                except:
                    continue
                text = itertext(v)
                if not text:
                    continue
                rows.append({
                    "book_code": book_code,
                    "book_name": bname,
                    "book_idx": book_idx,  # no viene número → usamos el orden
                    "chapter": cnum,
                    "verse": vnum,
                    "text": text,
                })
    return pd.DataFrame(rows)


# --------------
# Pipeline / CLI
# --------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--chuj", required=True, help="Ruta a CHSMI_fixed.xml")
    ap.add_argument("--es",   required=True, help="Ruta a LAT.xml (Español Latinoamericano)")
    ap.add_argument("--out",  default="data/parallel.csv", help="CSV paralelo de salida")
    ap.add_argument("--logs", default="logs", help="Carpeta para logs")
    args = ap.parse_args()

    Path(args.logs).mkdir(parents=True, exist_ok=True)
    Path(os.path.dirname(args.out) or ".").mkdir(parents=True, exist_ok=True)

    print("Leyendo CHUJ:", args.chuj)
    ch = parse_chuj_xml(args.chuj)
    print("  Versos CHUJ:", len(ch))

    print("Leyendo ESP :", args.es)
    es = parse_lat_xml(args.es)
    print("  Versos ESP :", len(es))

    # Reporte de títulos no mapeados (book_code "raro")
    bad_ch = ch[ch["book_code"].str.len() > 5]["book_name"].unique().tolist()
    bad_es = es[es["book_code"].str.len() > 5]["book_name"].unique().tolist()
    if bad_ch:
        print("AVISO: Títulos CHUJ no reconocidos (revisar mapeo):", bad_ch)
    if bad_es:
        print("AVISO: Títulos ESP no reconocidos (revisar mapeo):", bad_es)

    # Llave canónica por versículo
    ch["key"] = ch.apply(lambda r: (r["book_code"], int(r["chapter"]), int(r["verse"])), axis=1)
    es["key"] = es.apply(lambda r: (r["book_code"], int(r["chapter"]), int(r["verse"])), axis=1)

    # Emparejar por key exacta (libro/ capítulo/ versículo)
    ch_keys = set(ch["key"])
    es_keys = set(es["key"])
    common = ch_keys & es_keys
    only_ch = ch_keys - es_keys
    only_es = es_keys - ch_keys

    # Logs de versos no emparejados
    if only_ch:
        df_only_ch = ch[ch["key"].isin(only_ch)].copy()
        df_only_ch.sort_values(["book_code","chapter","verse"]).to_csv(
            os.path.join(args.logs, "unmatched_ch.csv"),
            index=False, quoting=csv.QUOTE_MINIMAL
        )
        print(f"Log: {len(df_only_ch)} versos presentes SOLO en CHUJ → logs/unmatched_ch.csv")
    else:
        print("No hay versos exclusivos de CHUJ. ✅")

    if only_es:
        df_only_es = es[es["key"].isin(only_es)].copy()
        df_only_es.sort_values(["book_code","chapter","verse"]).to_csv(
            os.path.join(args.logs, "unmatched_es.csv"),
            index=False, quoting=csv.QUOTE_MINIMAL
        )
        print(f"Log: {len(df_only_es)} versos presentes SOLO en ESP  → logs/unmatched_es.csv")
    else:
        print("No hay versos exclusivos de ESP. ✅")

    # Paralelo final (solo intersección)
    ch_m = ch[["key","text","book_name"]].rename(columns={"text":"ch","book_name":"book_name_ch"})
    es_m = es[["key","text","book_name"]].rename(columns={"text":"es","book_name":"book_name_es"})
    par = es_m.merge(ch_m, on="key", how="inner")
    par["book_code"] = par["key"].apply(lambda x: x[0])
    par["chapter"]   = par["key"].apply(lambda x: x[1])
    par["verse"]     = par["key"].apply(lambda x: x[2])
    par["ref"]       = par.apply(lambda r: f"{r['book_name_es'] or r['book_code']} {r['chapter']}:{r['verse']}", axis=1)
    par = par.sort_values(["book_code","chapter","verse"])
    # columnas de salida
    out_cols = ["es","ch","ref","book_code","book_name_es","book_name_ch","chapter","verse"]
    par[out_cols].to_csv(args.out, index=False)
    print(f"✅ Dataset paralelo: {len(par)} líneas → {args.out}")

    # --------------- Resúmenes para “prueba de integración” ---------------

    # Conteos por libro (capítulos y versos) en cada idioma
    def counts_by_book(df):
        by_chap = df.groupby(["book_code","chapter"])["verse"].nunique().reset_index(name="verses")
        chap_counts = by_chap.groupby("book_code")["chapter"].nunique().rename("chapters")
        verse_counts = df.groupby("book_code")["verse"].count().rename("verses_total")
        return chap_counts.to_frame().join(verse_counts, how="outer").reset_index()

    ch_count = counts_by_book(ch).rename(columns={"chapters":"chapters_ch","verses_total":"verses_total_ch"})
    es_count = counts_by_book(es).rename(columns={"chapters":"chapters_es","verses_total":"verses_total_es"})
    diff_book = ch_count.merge(es_count, on="book_code", how="outer")
    diff_book["chapters_delta"] = diff_book["chapters_ch"].fillna(0).astype(int) - diff_book["chapters_es"].fillna(0).astype(int)
    diff_book["verses_delta"]   = diff_book["verses_total_ch"].fillna(0).astype(int) - diff_book["verses_total_es"].fillna(0).astype(int)
    diff_book.sort_values("book_code").to_csv(os.path.join(args.logs, "diff_by_book.csv"), index=False)
    print("Resumen por libro → logs/diff_by_book.csv")

    # Diferencias por libro+capítulo (cuántos versos por cap en cada lado)
    ch_cap = ch.groupby(["book_code","chapter"])["verse"].nunique().reset_index(name="verses_ch")
    es_cap = es.groupby(["book_code","chapter"])["verse"].nunique().reset_index(name="verses_es")
    diff_cap = ch_cap.merge(es_cap, on=["book_code","chapter"], how="outer").fillna(0)
    diff_cap["verses_delta"] = diff_cap["verses_ch"].astype(int) - diff_cap["verses_es"].astype(int)
    diff_cap = diff_cap.sort_values(["book_code","chapter"])
    diff_cap.to_csv(os.path.join(args.logs, "diff_by_chapter.csv"), index=False)
    print("Resumen por libro/capítulo → logs/diff_by_chapter.csv")

    # Mensaje final claro
    tot_common = len(common)
    print("\n=== RESUMEN ===")
    print(f"Pares ES↔CH emparejados: {tot_common}")
    print(f"Solo CHUJ: {len(only_ch)} | Solo ESP: {len(only_es)}")
    print("Revisa los CSVs en la carpeta de logs para ver dónde no coinciden capítulos/versículos.\n")


if __name__ == "__main__":
    main()
