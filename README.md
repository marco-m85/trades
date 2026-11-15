# Sistema intraday (prototipo)

Questo repository non contiene il file o la documentazione del **“day trade main skill”** menzionato nella richiesta: al momento c'era solo un README minimale. Perciò ho aggiunto un prototipo autonomo basato su una strategia esplicita e sostituibile, senza attribuirla a quel materiale: **breakout dell'opening range**.

## Cosa fa

- Legge barre OHLCV da CSV.
- Calcola il massimo/minimo dei primi 15 minuti dalla sessione indicata.
- Conferma un breakout alla chiusura della barra e simula l'ingresso a quel prezzo.
- Imposta stop sull'estremo opposto dell'opening range e target predefinito a 2R.
- Dimensiona la posizione con rischio predefinito dello 0,5% dell'equity, esposizione massima 100%, limite perdita giornaliera 2% e un trade per sessione.
- Applica commissioni e slippage configurabili; se stop e target sono entrambi toccati nella stessa barra, assume lo stop (ipotesi conservativa).
- Chiude le posizioni entro la fine dei dati della sessione e produce riepilogo e log CSV.

## Avvio

Richiede Python 3.10+ e non ha dipendenze esterne.

```bash
python daytrade.py dati.csv --cash 10000 --open 09:30 --range-minutes 15 --output trades.csv
```

Il CSV deve avere intestazioni `timestamp,open,high,low,close` e può includere `volume`. I timestamp devono essere ISO 8601 coerenti con il fuso orario della borsa, ad esempio `2026-01-05T09:30:00`. Usa barre intraday ordinate, senza duplicati e con una convenzione temporale coerente. L'orario di apertura va impostato sul mercato e sui dati usati.

Parametri principali: `--risk 0.005`, `--daily-loss 0.02`, `--target-r 2`, `--max-exposure 1`, `--fee-bps 1`, `--slippage-bps 1`, `--long-only`.

## Limiti importanti

È solo un **backtester su CSV**, non invia ordini e non integra broker o feed dati. I risultati storici non prevedono rendimenti futuri; spread, liquidità, gap, tasse, fusi orari, split e qualità dei dati possono cambiare radicalmente l'esito. Prima di considerare qualsiasi uso reale servono validazione indipendente, test out-of-sample, gestione dei dati e dei rischi specifici del mercato, oltre a paper trading. Non è consulenza finanziaria.

Per implementare fedelmente il “day trade main skill”, aggiungi o indica il file/contenuto della skill e i mercati, timeframe, orari e regole operative desiderati.
