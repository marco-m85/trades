# ML feature engineering point-in-time

## Obiettivo

Costruire feature di ricerca per modelli offline, deterministiche e ricostruibili al timestamp decisionale. Il modello non genera ordini e non modifica i limiti di rischio.

## Specificare prima

- target/label, orizzonte, timestamp di osservazione e timestamp di disponibilità;
- unità di previsione (strumento/barra/sessione) e universo;
- costo/threshold per rendere la label economicamente interpretabile;
- trattamento di label sovrapposte, neutral class, class imbalance e dati rivisti.

## Feature

- Calcolare rolling statistiche esclusivamente con osservazioni disponibili fino a t; indicare se la barra t è chiusa.
- Lag espliciti per dati pubblicati con ritardo. Non usare dati di fine sessione, high/low futuri o valori aggiornati successivamente a t.
- Allineare feature cross-asset per timestamp e timezone; evitare forward-fill indiscriminato attraverso chiusure, halt o buchi.
- Normalizzazione, imputazione, selezione feature, PCA e encoding si fit-tano sul training fold e si applicano senza refit a validation/test.
- Audit per leakage tramite test di permutazione, controlli temporali e verifica di feature availability.
- Documentare sorgente, versione, semantica, unità, finestra, lag, null policy e trasformazione.

## Split e valutazione

Usare split cronologici e walk-forward. Se target/holding period si sovrappongono, usare purging/embargo appropriato. Il holdout finale resta intatto fino al congelamento del modello. Confrontare no-skill e baseline semplici; valutare metriche di classificazione/regressione pertinenti, calibrazione, turnover, PnL netto simulato, drawdown, stabilità per regime e incertezza. Accuracy non dimostra redditività.

## Versioning e controllo

Versionare schema feature, codice, dataset/provenienza, seed, parametri, modello e report. Allenamento offline riproducibile, approvazione umana e rollback. Vietati online learning non revisionato, self-modifying strategy, uso del test finale per tuning e promozione automatica. Gli output LLM vanno verificati da persona e non sono input autorizzati al broker o al risk manager.
