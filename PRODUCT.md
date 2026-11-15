# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack
Plain HTML/CSS/JS, no build step, published on GitHub Pages alongside the JSON API (user's answer, 15-nov-2026). Installable as a PWA.

## Users
Chuj speakers from San Mateo Ixtatán (Huehuetenango, Guatemala) reading the Bible on their phones, personally and at church, often with weak or no signal. Secondary: the translation team of the church Encuentro con Dios, who read to review the text.

## Product Purpose
A reader for La Santa Biblia en Chuj de San Mateo Ixtatán, published by the church Encuentro con Dios from the repository encuentrocondios/biblia-chuj-smi. It reads the static JSON API (books.json, {libro}/{capitulo}.json) so the text can be read in any browser without installing anything, and installed as an app. Success: someone opens a chapter in their own language and keeps reading, even offline.

## Positioning
The Chuj text of San Mateo Ixtatán, spelled per the ALMG standard alphabet (Gramática normativa Chuj, 2007), read directly from the church's own repository: the text a neighboring reader (MyBible module, generic Bible apps) would not carry in this reviewed orthography.

## Operating Context
Text lives in CHSM_fixed.xml (Zefania XML) in the repo; a GitHub Action converts it to JSON on the `json` branch, which GitHub Pages serves (books.json with name and short_name; one file per chapter with chapter and verses[number,text]). The MyBible module is published separately as a release. The translation is under active review by speakers, so the text changes.

## Capabilities and Constraints
- 66 books, 29,991 verses; about 1,100 verses of the Spanish canon are absent in the Chuj text, and some chapters are offset (open issue #5: Lucas 23 is one verse ahead).
- Letters used by the text include the apostrophe in b', t', k', tz', ch' and the digraph nh; the reader must render these without breaking words at the apostrophe.
- Spanish comparison: the user asked for Reina-Valera 1960 as an optional toggle, off by default. RVR1960 is copyrighted (Sociedades Bíblicas Unidas) and is not in the repo; the repo carries Reina-Valera 1909 (public domain). Open decision: only 1909 can be shipped without permission.
- Proper names keep their Spanish spelling (David, Jehová, Cristo) by decision of the church.

## Brand Commitments
Name: Biblia Chuj San Mateo Ixtatán. Publisher: Iglesia Encuentro con Dios. No logo or brand palette has been provided.

## Evidence on Hand
Full text in CHSM_fixed.xml, Spanish RV 1909 in SPARV.xml, ALMG grammar PDFs in the private repo aalonzolu/chuj_translate. No logo, photography, or testimonials exist; none should be invented.

## Product Principles
1. The text is the product: reading comfort beats every other feature.
2. Works where connectivity is poor: what was read once stays readable.
3. Respect the orthography: apostrophes and digraphs are letters, never artifacts.
4. Honest about gaps: missing or offset verses are shown as such, never papered over.
5. Small and durable: no dependencies a church volunteer cannot maintain.

## Accessibility & Inclusion
Primary audience reads on mid-range Android phones in bright light and often with reduced vision; text size must be adjustable and contrast high. Interface language is Spanish (readers are bilingual); Chuj is the content language.
