#!/usr/bin/env python3
"""Genera la API JSON estática y empaqueta el visor.

Uso: python tools/build_api.py [--out output] [--chuj CHSM.xml] [--es SPARV.xml] [--visor visor]

Salida (compatible con la API anterior, solo con campos añadidos):
  books.json                  libros: name, short_name (+ number, testament, chapters, verses)
  {libro}/{capitulo}.json     capítulo: chapter, verses[{number,text}] (+ book, book_short, aligned, es_verses)
  {libro}.json                libro completo, compacto (lectura sin conexión y búsqueda)
  es/{libro}.json             Reina-Valera 1909 (dominio público) para comparar
  revision.json               capítulos cuyo conteo de versículos difiere del español
  version.json                fecha y cantidad de versículos
y copia el contenido de visor/ a la raíz de la salida.
"""
import argparse, json, os, shutil, sys, datetime
import xml.etree.ElementTree as ET


def read(path):
    """-> (libros ordenados, {bnumber: {chapter: {verse: text}}})"""
    root = ET.parse(path).getroot()
    books, data = [], {}
    for b in root.iter('BIBLEBOOK'):
        n = int(b.get('bnumber'))
        books.append({'number': n, 'name': b.get('bname', '').strip(), 'short_name': b.get('bsname', '').strip()})
        chapters = {}
        for c in b.iter('CHAPTER'):
            verses = {}
            for v in c.iter('VERS'):
                text = ' '.join((v.text or '').split())
                if text:                       # un versículo vacío no rompe la generación
                    verses[int(v.get('vnumber'))] = text
            chapters[int(c.get('cnumber'))] = verses
        data[n] = chapters
    return books, data


def dump(path, obj, indent=None):
    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=indent, separators=(',', ':') if indent is None else None)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='output'); ap.add_argument('--chuj', default='CHSM.xml')
    ap.add_argument('--es', default='SPARV.xml'); ap.add_argument('--visor', default='visor')
    a = ap.parse_args()

    books, ch = read(a.chuj)
    _, es = read(a.es)
    if os.path.isdir(a.out): shutil.rmtree(a.out)
    os.makedirs(a.out)

    index, revision, total = [], [], 0
    for b in books:
        n, short = b['number'], b['short_name']
        chapters = ch[n]
        compact, es_compact = [], []
        for c in sorted(chapters):
            verses = chapters[c]
            ev = es.get(n, {}).get(c, {})
            aligned = bool(ev) and sorted(verses) == sorted(ev)
            if ev and not aligned:
                revision.append({'book': short, 'chapter': c, 'chuj': len(verses), 'es': len(ev),
                                 'missing': sorted(set(ev) - set(verses)), 'extra': sorted(set(verses) - set(ev))})
            dump(os.path.join(a.out, short, f'{c}.json'), {
                'chapter': str(c), 'book': b['name'], 'book_short': short, 'aligned': aligned, 'es_verses': len(ev),
                'verses': [{'number': str(v), 'text': t} for v, t in sorted(verses.items())]}, indent=2)
            compact.append({'c': c, 'aligned': aligned, 'v': [[v, t] for v, t in sorted(verses.items())]})
            es_compact.append({'c': c, 'v': [[v, t] for v, t in sorted(ev.items())]})
            total += len(verses)
        dump(os.path.join(a.out, f'{short}.json'), {'name': b['name'], 'short_name': short, 'chapters': compact})
        dump(os.path.join(a.out, 'es', f'{short}.json'), {'name': b['name'], 'short_name': short, 'chapters': es_compact})
        index.append({'name': b['name'], 'short_name': short, 'number': n, 'testament': 'AT' if n <= 39 else 'NT',
                      'chapters': len(chapters), 'verses': sum(len(v) for v in chapters.values())})

    dump(os.path.join(a.out, 'books.json'), index, indent=2)
    dump(os.path.join(a.out, 'revision.json'), revision, indent=1)
    dump(os.path.join(a.out, 'version.json'), {
        'updated': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%MZ'),
        'verses': total, 'books': len(books), 'chapters_misaligned': len(revision),
        'source': os.path.basename(a.chuj), 'spanish': 'Reina-Valera 1909 (dominio público)'}, indent=2)

    if os.path.isdir(a.visor):
        for item in os.listdir(a.visor):
            s, d = os.path.join(a.visor, item), os.path.join(a.out, item)
            shutil.copytree(s, d) if os.path.isdir(s) else shutil.copy2(s, d)
        sw = os.path.join(a.out, 'sw.js')          # cada publicación renueva la caché de la aplicación
        if os.path.exists(sw):
            txt = open(sw, encoding='utf-8').read().replace('__BUILD__', datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d%H%M'))
            open(sw, 'w', encoding='utf-8').write(txt)
    open(os.path.join(a.out, '.nojekyll'), 'w').close()
    print(f'{len(books)} libros, {total} versículos, {len(revision)} capítulos con conteo distinto al español -> {a.out}/')


if __name__ == '__main__':
    sys.exit(main())
