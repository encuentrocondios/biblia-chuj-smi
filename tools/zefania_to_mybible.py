#!/usr/bin/env python3
"""Zefania XML -> MyBible .SQLite3 module. Uso: zefania_to_mybible.py in.xml out.SQLite3"""
import sqlite3, sys, os, xml.etree.ElementTree as ET

# Zefania bnumber (1..66) -> MyBible book_number
def mb(n):
    if n <= 17: return n * 10
    if n <= 22: return (n + 4) * 10
    if n <= 25: return (n + 6) * 10
    return (n + 7) * 10

src, dst = sys.argv[1], sys.argv[2]
root = ET.parse(src).getroot()
if os.path.exists(dst): os.remove(dst)
db = sqlite3.connect(dst)
db.executescript("""
CREATE TABLE info (name TEXT, value TEXT);
CREATE TABLE books (book_number NUMERIC, short_name TEXT, long_name TEXT, book_color TEXT, is_present BOOLEAN);
CREATE TABLE verses (book_number NUMERIC, chapter NUMERIC, verse NUMERIC, text TEXT);
CREATE UNIQUE INDEX verses_index ON verses (book_number, chapter, verse);
""")
nv = 0
for b in root.iter('BIBLEBOOK'):
    num = mb(int(b.get('bnumber')))
    long_name = (b.get('bname') or '').strip().title()
    db.execute("INSERT INTO books VALUES (?,?,?,?,1)", (num, b.get('bsname') or long_name, long_name, '#ccccff' if num < 470 else '#ffcccc'))
    for c in b.iter('CHAPTER'):
        for v in c.iter('VERS'):
            t = ' '.join((v.text or '').split())
            if not t: continue
            db.execute("INSERT OR REPLACE INTO verses VALUES (?,?,?,?)", (num, int(c.get('cnumber')), int(v.get('vnumber')), t)); nv += 1
info = {
 'description': 'Biblia en Chuj de San Mateo Ixtatán',
 'detailed_info': 'La Santa Biblia en Chuj de San Mateo Ixtatán, revisada según la Gramática normativa Chuj de la ALMG. Iglesia Encuentro con Dios. Fuente: github.com/encuentrocondios/biblia-chuj-smi',
 'language': 'cac', 'russian_numbering': 'false', 'chapter_string': 'Capítulo %s',
 'origin': 'https://github.com/encuentrocondios/biblia-chuj-smi',
}
db.executemany("INSERT INTO info VALUES (?,?)", info.items())
db.commit(); db.execute("VACUUM"); db.close()
print(f"{nv} versículos -> {dst}")
