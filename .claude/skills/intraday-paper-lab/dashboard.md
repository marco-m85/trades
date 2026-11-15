# Dashboard e grafici

## Vista minima

- Equity curve con capitale/allocazione e periodo chiaramente indicati.
- Drawdown curve e massimo drawdown con definizione dichiarata.
- PnL netto/lordo e costi; metriche campione (numero trade e barre).
- Breakdown per simbolo, sessione/giorno, direzione e regime se disponibile.
- Distribuzione PnL/trade, esposizione, turnover e tabella trade.
- Benchmark solo se dataset e metodologia sono compatibili.

## Regole

- Distingui realized e mark-to-market equity. Non inventare mark-to-market se manca la serie prezzi.
- Usa timestamp cronologici, timezone esplicita e gap visibili/non fuorvianti.
- Visualizza strategia/config version, fonte e intervallo dati, assunzioni fees/slippage e metodologia di allocazione.
- Mostra avviso per campione ridotto, dati mancanti o metriche non calcolabili.
- Gestisci zero trade, dataset vuoto, un asset, molti asset, timestamp invalidi e upload grande.
- Grafici descrittivi, senza call to action, previsioni o raccomandazioni.
- Non esporre token/account IDs o dati personali nei grafici, export o log.

## Test UI

Fixture note con equity/PnL attesi; dataset vuoto e no-trade; timezone e session boundaries; download CSV senza colonne segrete; errori di schema mostrati senza crash.
