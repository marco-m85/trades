# Intraday Paper Lab

Prototipo educativo di backtest multi-asset e paper trading. Non invia ordini reali. Il repository non contiene il “day trade main skill”: la strategia qui implementata è un esempio trasparente, non una traduzione di una skill mancante.

## Strategia e filtri

Breakout dell'opening range, confermato da EMA veloce/lenta, prezzo dal lato coerente del VWAP intraday e volume almeno pari alla media recente. Il filtro ATR esclude sessioni sotto/sopra le soglie ATR% e opening range troppo piccolo/grande rispetto all'ATR. Parametri indicatori: ATR 14, EMA 9/21 e media volume 20 barre. Stop sul bordo opposto dell'opening range; target predefinito 2R. Al massimo un trade per asset e giornata. Se una barra tocca sia stop sia target, il backtest assume stop (conservativo).

Il CSV accetta `timestamp,open,high,low,close` e colonne opzionali `volume,symbol`; senza `symbol` usa DEFAULT. Timestamp ISO 8601 coerenti col fuso orario della borsa. Esempio: `2026-01-05T09:30:00`. Per più asset, ripeti le barre con il rispettivo symbol. Il capitale viene allocato in parti uguali a sotto-conti indipendenti per asset; ciascuno ha il rischio per trade e il limite giornaliero configurati.

## Backtest

Python 3.10+:

```bash
python daytrade.py sample.csv --cash 10000 --open 09:30 --range-minutes 15 --output trades.csv
```

## Dashboard performance

```bash
pip install -r requirements.txt
streamlit run dashboard.py
```

Carica CSV e visualizza equity curve, PnL per asset, distribuzione dei risultati, statistiche e trade log esportabile.

## Feed HTTP e broker simulato

`live_paper.py` interroga un endpoint HTTP configurato dall'utente, senza dipendere da un provider specifico. L'endpoint deve restituire candele completate nel formato:

```json
{"bars":[{"symbol":"XYZ","timestamp":"2026-01-05T09:30:00","open":100,"high":101,"low":99,"close":100.5,"volume":1200}]}
```

Esempio:

```bash
export FEED_TOKEN='token-del-provider'
python live_paper.py --url 'https://provider.example/api/bars' --token-env FEED_TOKEN --interval 15
```

Usa `--once` per un singolo polling. Il runner riprocessa la storia ricevuta e registra nel ledger locale solo trade chiusi; il ledger è in memoria e si azzera al riavvio. Il feed deve fornire barre coerenti, completate e in orario exchange. Il client è generico: va adattato allo schema, autenticazione, rate limits e licenza del provider. Non è un feed incluso.

## Rischi e limiti

Solo ricerca storica e paper simulation: non c'è integrazione con broker, invio ordini, gestione di posizioni live o garanzia di esecuzione. Il backtest è sensibile a dati, fuso orario, spread, gap, liquidità, corporate actions e ipotesi di slippage. Controlla la qualità delle barre, testa out-of-sample e fai paper trading prima di qualunque valutazione ulteriore. Performance passate non predicono risultati futuri; non è consulenza finanziaria. Il feed live non rende il sistema adatto al trading reale.
