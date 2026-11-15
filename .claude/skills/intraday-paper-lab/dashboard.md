# Dashboard performance completa — requisiti

## Pagine/viste

1. **Overview**: capitale iniziale/finale, PnL netto e lordo, costi, return non annualizzato o annualizzazione motivata, trade count, win rate, expectancy, profit factor e stato dataset.
2. **Equity & drawdown**: equity realizzata e mark-to-market separate; drawdown in valore/% con frequenza e formula dichiarata; underwater chart.
3. **Trade analysis**: distribuzione PnL/R, holding time, long/short, cause exit (stop, target, breakeven, time), MFE/MAE se dati disponibili; nessuna MFE/MAE inventata da soli fill.
4. **Portfolio**: esposizione lorda/netta, utilizzo capitale, rischio aperto, PnL e concentrazione per simbolo/settore/regime, correlazioni solo con dati sufficienti.
5. **Sessione e costi**: breakdown per giorno/ora, fees, spread/slippage modellati e sensitivity.
6. **Data/research audit**: sorgente, timezone, periodo, coverage, barre mancanti, config/commit/strategia, split e benchmark.

## Definizioni

- Indicare chiaramente realized vs MTM e prezzi/valutazioni usati.
- Il breakeven è categoria di uscita separata: stop a entry non significa PnL netto zero dopo commissioni, spread o slippage.
- Equity cumulata deve rispettare la metodologia di allocazione del backtest; non sommare subaccount come capitale duplicato.
- Non annualizzare se periodo/cadenza non è affidabile.

## UX, sicurezza e test

Filtri data/asset/sessione devono essere trasparenti e non alterare i dati sorgente. Mostrare avvisi per pochi trade, dati incompleti e metriche non calcolabili. Zero trade, un trade, null, timezone, valori estremi e file grandi devono essere gestiti. Export solo di dati necessari, mai segreti/identificativi account. Testare le metriche con fixture calcolabili a mano e mantenere grafici descrittivi, senza consigli di acquisto/vendita.
