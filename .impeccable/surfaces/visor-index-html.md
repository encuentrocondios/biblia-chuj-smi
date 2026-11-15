---
version: 1
slug: "visor-index-html"
primary_target: "visor/index.html"
related_targets: []
---

# Surface brief: visor/index.html

Scope: single-page Bible reader (PWA), Read mode. Visitor: Chuj speaker on a mid-range Android phone, often offline, reading chapters; secondary: translation reviewers searching words.
Job: open a book/chapter, read comfortably, continue where they left off, adjust text size, install.
Content: real text from the JSON API (books.json, {short}/{n}.json, per-book {short}.json). Optional Spanish toggle (Reina-Valera 1909; RV1960 not shippable for copyright), shown only where verse counts match.
Unresolved: RV1960 permission; ~296 chapters have verse counts that differ from the Spanish canon.

## Direction contract

THESIS: A Bible reader that belongs to San Mateo Ixtatán by its salt, not by borrowed textile motifs: a mineral frame around a calm reading column. Refuses the cream-and-serif "old book" default and the generic Bible-app blue.
OWN-WORLD: Black salt (atz'am k'ik') slab #1F1A17 for masthead and rail with salt-white lettering; reading ground cool salt white #F3F5F4, ink #1A1715; one ember accent #C4501B from the boiling hearth for verse numbers, current place and focus; mist-grey #5E6A6C for secondary text. Dark mode = the black-salt slab as ground. Book picker is a lattice of square crystal cells with 1px mortar and notched corners. Literata (reading, display at heavy weight), Atkinson Hyperlegible Next (controls). Apostrophe drawn as the letter U+02BC.
STORY: The reader understands within a second where they are (book, chapter), reads without anything performing behind the text, and trusts the app to still work in the mountains.
FIRST VIEWPORT: 390x844: slim black-salt masthead (book+chapter pill, search, text-size); chapter title in Literata 800 at ~44px with the book name small above is forbidden as kicker, so the title is the single line "Salmo 95"; verses at 20px/1.7 in a 36-ch measure scaled by size setting; verse numbers in ember; bottom rail in black salt with prev, Libros, next.
FORM: seed: 72e2ae430ee30364 (direction roll; the build follows the assigned direction «atz'am k'ik'»).
SIGNATURE: the salt-crystal lattice picker: books as a lattice of faceted cells (opposite corners cut, 2px mortar; 3 columns on phones for 44px+ tap targets), chapters as the same cells inside the chosen book; the cell you last read carries the ember mark.
