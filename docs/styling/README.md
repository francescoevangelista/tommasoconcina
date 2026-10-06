# Styling · ricostruzione dai layout Tommy

Aggiornamento locale del 6 ottobre 2026, branch `tommy-layouts-sept17`.

## Risultato

- `CURATED.stylingGeneral`: 62 fotografie dalle 10 schermate generali.
- `CURATED.women`: 33 fotografie dalle 5 schermate Women.
- `CURATED.men`: 28 fotografie dalle 5 schermate Men.
- `CURATED.rolex`: 4 slider dalla schermata Rolex Work.
- `PROJECT_CANVAS.rolex`: 34 fotografie complete dalle pagine 2–9 disponibili.

Desktop: coordinate misurate sui JPG 2049 × 2952, riportate al canvas di riferimento largo 1111 px e scalate insieme alla finestra. Mobile fino a 860 px: una colonna, immagini complete, ordine delle righe da sinistra a destra. Le ripetizioni ai bordi sono eliminate: resta una sola fotografia nella posizione della prima occorrenza, come confermato da Francesco. Le porzioni continuate in una schermata successiva completano la fotografia precedente.

Gli screenshot sono usati per estrarre le singole immagini, non come bitmap dell'intera pagina. Le fotografie già disponibili nella stessa variante sono riutilizzate. Le altre sono provvisorie, come autorizzato: vedi [master da richiedere](MASTER-DA-RICHIEDERE.md). Non sono state generate fotografie. Testi già dentro le fotografie/pubblicità restano nelle immagini; le note rosse di lavorazione sono escluse dall'interfaccia.

Rolex: autoplay ogni 7,5 secondi, click e tastiera desktop, swipe orizzontale mobile, senza frecce. Autoplay in pausa su hover/focus, fuori schermo, in tab non visibile o quando la pagina Work non è attiva. La preferenza di movimento ridotto disabilita autoplay e transizioni. Il click conseguente a uno swipe non fa avanzare due volte. Lo scorrimento verticale non cambia fotografia.

## Verifiche

35 combinazioni di pagina/larghezza: 390, 430, 768, 1024, 1111, 1440 e 1920 px sulle cinque viste. Controllati quantità, ordine, contenimento orizzontale, dimensioni riservate al caricamento, singola colonna e proporzioni intere su mobile. Su desktop lo scostamento tra coordinate specificate e rettangoli browser è inferiore a 0,01 px, compatibile con l'arrotondamento del browser. Questo valore verifica il rendering delle coordinate: non è una dichiarazione di identità di ogni pixel del mockup.

Confrontati i 29 JPG originali con le catture integrali a 1111 px. Il menu esistente mantiene i filtri navigabili; nei mockup la sua evidenziazione è statica. Nelle sovrapposizioni tra schermate, alcune fotografie cambiano anche posizione orizzontale: è applicata la scelta autorizzata di mantenere la prima posizione, quindi le ripetizioni successive non vengono imitate. La pagina 1 Rolex e i due annunci parziali della parte precedente visibili sul bordo superiore della pagina 2 non sono stati inventati.

- 103 asset locali verificati via HTTP: tutti 200, nessun 404.
- Nessun errore/warning di console nel browser sulle viste controllate.
- Hash routing verificato per le cinque viste, apertura del progetto e ritorno attraverso i filtri.
- Click e autoplay verificati nel browser; passaggio Rolex desktop/mobile verificato nello stesso documento.
- Swipe, ritorno, click sintetico, scroll verticale, annullamento touch, tastiera, pause e movimento ridotto verificati con i reali gestori del sito in un test senza dipendenze. Non eseguita prova su telefono fisico.
- Catalogo `P`, Work generale, Creative Direction e composizioni/art degli altri progetti confrontati con la versione iniziale: invariati.
- Sintassi JavaScript e `git diff --check`: passati.

Nella prima verifica della versione precedente risultava un 404 di `favicon.ico`, già assente dal repository: non fa parte dei nuovi asset Styling e non è stato modificato in questo intervento.

## Prove e file

[Panoramica](qa/review-overview.jpg) · [Confronto Styling generale](qa/compare-stylingGeneral.jpg) · [Women](qa/compare-women.jpg) · [Men](qa/compare-men.jpg) · [Rolex Work](qa/compare-rolex.jpg) · [Progetto Rolex](qa/compare-rolexProject.jpg).

[Manifest di coordinate e provenienza](manifest.json) · [Matrice browser](qa/browser-matrix.json) · [Verifica geometria/ordine](qa/geometry-check.json) · [Verifica perimetro](qa/scope-check.json) · [Click e autoplay](qa/browser-interactions.json) · [Controllo HTTP](assets-http-check.json).

Il test degli slider è in `tests/styling-interactions.cjs` ed è eseguibile con Node, senza installare pacchetti. Le modifiche sono locali e non sono state committate, inviate a GitHub, pubblicate su Vercel o unite a `main`.
