# Checklist operativa della skill

## Prima di modificare
- [ ] Leggi codice, README e test pertinenti; verifica che i percorsi descritti esistano.
- [ ] Classifica il lavoro: strategia, dati, rischio, quant/ML/LLM, broker sandbox, dashboard o documentazione.
- [ ] Definisci comportamento atteso, criteri di accettazione e comportamento in errore.
- [ ] Verifica la modalità paper/sandbox e l'assenza di invio ordini reali.
- [ ] Pianifica un cambiamento piccolo e testabile.

## Durante l'implementazione
- [ ] Convalida input, timestamp, timezone, simboli, prezzi, quantità e payload esterni.
- [ ] Evita look-ahead, leakage, elaborazione doppia e allocazioni superiori al capitale.
- [ ] Mantieni separati strategia, risk manager, dati, simulazione ordini, storage e UI.
- [ ] Segreti solo da variabili d'ambiente/secret manager; redazione nei log.
- [ ] Aggiorna documentazione ed esempi con valori fittizi.

## Test per area
- [ ] Backtest: long/short, collisione stop-target, uscita sessione, commissioni/slippage.
- [ ] Multi-asset: simboli indipendenti, capitale complessivo, esposizione aggregata.
- [ ] Dati/feed: CSV vuoto/malformato, duplicati, barre stale/incomplete, timeout, schema errato.
- [ ] Broker sandbox: modalità live rifiutata, idempotenza, errori, retry limitati, secret redaction.
- [ ] ML/LLM: split temporale, holdout mai usato per tuning, baseline e riproducibilità.
- [ ] Dashboard: zero trade, un trade, dati mancanti, timezone, periodi non continui.
- [ ] Esegui solo test e controlli disponibili; annota esattamente i comandi e i risultati.

## Prima della risposta
- [ ] Rileggi diff e cerca ordini reali, fallback live, segreti, look-ahead e default permissivi.
- [ ] Spiega cosa è implementato e cosa è solo proposto.
- [ ] Riporta limiti, assunzioni e passi di verifica; non promettere rendimento.
