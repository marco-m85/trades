# Strategia intraday — specifica di ricerca

Questa è una specifica per strategia simulata, non un consiglio operativo. Prima di implementarla, controlla il comportamento del codice esistente e formalizza configurazioni e assunzioni.

## Segnale candidato

Il prototipo può usare breakout dell'opening range, conferma trend (EMA), VWAP, volume e filtro ATR. Ogni filtro deve poter essere abilitato/configurato e misurato con ablation rispetto a baseline semplice. Non aggiungere filtri solo perché migliorano il backtest sullo stesso periodo: misura overfitting e stabilità fuori campione.

Specificare per ogni asset:
- calendario e timezone IANA; apertura/chiusura e sessioni abbreviate;
- intervallo barre e convenzione timestamp; barra completa o in formazione;
- range iniziale e regola breakout/ritest;
- condizioni long/short e regole per segnali simultanei;
- entry simulata, stop iniziale, target, uscita temporale e no-overnight;
- volume/ATR/VWAP e comportamento se dato mancante;
- massimo ingressi e cooldown.

## Stop, target e breakeven

- Stop iniziale e target sono calcolati al momento dell'entry, con `R = rischio monetario iniziale / unità` coerente con multiplier e quantità.
- Il target è espresso come multiplo configurato del rischio iniziale e lo stop non deve allargarsi automaticamente.
- Parametro `breakeven_trigger_r` configurabile. Interpretazione predefinita proposta per “+10% in positivo”: `0.1R`, cioè massimo profitto non realizzato almeno pari al 10% del rischio iniziale. Al trigger, lo stop diventa il prezzo medio d'ingresso; applicare fees/spread per distinguere prezzo breakeven da PnL netto breakeven.
- Se l'utente intende guadagno del 10% sul prezzo d'ingresso o sul notional, fermarsi e chiarire il denominatore: non è equivalente a 0.1R.
- Il breakeven è one-way: una volta attivato non si disattiva e non peggiora il rischio. Non garantisce fill all'entry in presenza di gap, latenza o slippage.
- Testare long e short, trigger non raggiunto, trigger raggiunto, gap attraverso lo stop, costi, collisione stop/target e sequenza intrabar. Con sola barra OHLC, se il livello trigger e lo stop breakeven cadono nella stessa barra, la sequenza è ignota: per default attiva il nuovo stop dalla barra successiva e spiega l'assunzione.

## Regole di simulazione

Il segnale a close non può essere eseguito retroattivamente al prezzo più favorevole della stessa barra. OHLC non identifica ordine dei prezzi intrabar. Se stop e target sono entrambi toccati nella stessa barra, usa stop-first o una granularità più fine; registra l'ipotesi. Uscite per fine sessione e gap devono avere regole esplicite. Simula costi e liquidità, senza chiamare simulazione un fill reale.

## Validazione

Baseline, cronologia/walk-forward, test holdout, breakdown per asset/regime, sensitivity costi/slippage e ablation. Riporta numero di esperimenti e metriche, non soltanto il best run. Nessun sistema di segnali è qualificato da un piccolo CSV di esempio.
