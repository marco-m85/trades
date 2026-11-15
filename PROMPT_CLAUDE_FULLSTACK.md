# PROMPT MASTER — App full stack intraday, dashboard e broker mock

Copia tutto il blocco seguente in Claude Code dopo aver aperto una cartella/repository vuoto. Se il repository non è vuoto, chiedi prima di sovrascrivere file esistenti. Il prompt chiede a Claude di creare il software; non abilita trading live.

```text
Agisci come senior software engineer, quantitative researcher e reviewer di sicurezza. Crea da zero, nella cartella corrente, una applicazione full stack per ricerca, backtest storico e paper trading intraday. Deve essere un prototipo educativo, locale e deterministico. Non è consulenza finanziaria.

## Vincoli non negoziabili
- Nessun broker reale, nessun endpoint broker, nessuna API di trading, nessun ordine live. Il broker deve essere un mock locale che simula stati e fill.
- Non creare una modalità live, URL live di fallback, codice d'ordine reale o funzionalità che possa raggiungere conti reali.
- Nessuna credenziale richiesta. Non aggiungere segreti, token o account ID. Usa `.env.example` solo con placeholder non sensibili se necessario e ignora `.env` con `.gitignore`.
- Non chiamare una strategia profittevole e non promettere risultati. Backtest/paper non predicono risultati futuri.
- Fail closed: dati invalidi/stale, configurazione non valida, stato incerto o errore DB impediscono nuovi intenti simulati e producono un messaggio chiaro.
- Evita look-ahead e leakage. Ogni feature deve essere disponibile al timestamp della decisione.
- Prima di implementare, ispeziona la cartella e i tool disponibili. Non cancellare o sovrascrivere materiale esistente senza conferma.

## Scelte di stack
Usa una soluzione full stack semplice, locale e documentabile:
- Backend: Python 3.11+, FastAPI, Pydantic, SQLAlchemy 2 e SQLite.
- Frontend/dashboard: React + TypeScript + Vite, grafici con una libreria attiva e mantenuta (ad esempio Recharts), client HTTP tipizzato.
- Test: pytest per backend e Vitest/Testing Library per frontend; test API con TestClient/httpx.
- Dev environment: Docker Compose opzionale ma documentato; deve avviare solo servizi locali, senza broker o feed esterni.
- Dipendenze con versioni ragionevolmente limitate e installazione riproducibile.
- Se l'ambiente non supporta uno stack o un comando, dichiaralo e adotta la più piccola alternativa mantenendo API/UI separate.

## Architettura
Crea una struttura modulare equivalente a:

backend/
  app/main.py
  app/api/ (routes e schemi)
  app/core/ (config, logging, errors)
  app/data/ (CSV import e validation)
  app/domain/ (Bar, Signal, Position, Order, Fill, Portfolio, Trade)
  app/strategy/ (indicatori e strategia)
  app/risk/ (position sizing e limiti aggregati)
  app/execution/ (interfaccia e broker mock deterministico)
  app/analytics/ (metriche e report)
  app/storage/ (modelli, repository, migrazioni semplici)
  tests/
frontend/
  src/api/
  src/components/
  src/pages/
  src/types/
  tests/
README.md
.env.example
.gitignore
docker-compose.yml

Mantieni separati ingestion, feature/strategy, portfolio risk, broker mock, persistenza, analytics e UI. La strategia crea Signal; RiskManager approva o rifiuta; solo dopo il broker mock simula l'intento. La UI non può bypassare il risk manager.

## Funzionalità applicative
1. Import CSV storico OHLCV con colonne richieste `timestamp,open,high,low,close` e opzionali `volume,symbol`; default symbol solo se documentato. Validare timestamp ISO 8601, OHLC coerenti, prezzi positivi, volumi non negativi, simboli e duplicati symbol+timestamp. Rifiutare timezone miste o ambigue; chiedere/registrare timezone exchange e convenzione timestamp.
2. Backtest multi-asset e replay storico deterministico.
3. Strategia di ricerca configurabile: breakout opening range; EMA fast/slow; VWAP sessione; volume relativo; filtri ATR% e opening-range/ATR; long/short configurabili; massimo una posizione per asset/sessione; nessuna posizione overnight se configurato.
4. Stop iniziale, target R, uscita di fine sessione, commissioni, spread e slippage configurabili. Bar OHLC non risolve la sequenza intrabar: se stop e target sono entrambi toccati, assumere stop-first o dichiarare ambiguità in modo conservativo. Un segnale confermato a close non può essere riempito retroattivamente a un prezzo precedente della stessa barra.
5. Breakeven configurabile e disabilitabile. Per il termine “+10% in positivo” NON assumere automaticamente il significato: implementa il parametro denominato `breakeven_trigger_r`, descrivi +0.1R come interpretazione proposta (10% del rischio iniziale), e nel README/UI specifica che è diversa dal +10% sul prezzo o sul notional. Se il prodotto deve applicare il comportamento senza ulteriore chiarimento, usa +0.1R solo come default esplicito e modificabile, mai come interpretazione implicita. Sposta lo stop al prezzo d'ingresso solo dopo che il massimo profitto non realizzato supera la soglia; dopo attivazione non arretrare lo stop. Per barre OHLC, applica lo stop aggiornato dalla barra successiva, salvo granularità capace di stabilire la sequenza. Commissioni, spread, gap e slippage possono produrre perdita netta anche con stop a entry.
6. Risk manager centrale: quantità basata su equity, rischio per trade, distanza stop, multiplier/tick/lot se supportati; limiti di rischio per trade, capitale allocato, esposizione per asset/portafoglio, numero posizioni, perdita giornaliera e drawdown. L'allocazione multi-asset non deve duplicare capitale. Se multiplier/tick/lot non sono disponibili, documentare la semplificazione e rifiutare strumenti per cui la size non è calcolabile in modo sicuro.
7. Broker mock locale: ledger persistente SQLite; stati simulati `created`, `risk_rejected`, `accepted`, `rejected`, `partial`, `filled`, `canceled`; fill deterministici secondo regole documentate; idempotency key; niente richieste di rete o invio ordini. Distingui ordini simulati da trade/fill ipotetici.
8. Dashboard: overview, equity, drawdown, PnL lordo/netto e costi, metriche, breakdown per asset/sessione/direzione, distribuzione trade, esposizione e rischio, tabella e download CSV. Distingui realized da mark-to-market; non inventare MTM se manca la serie prezzi. Mostra periodo/fonte dati, timezone, configurazione, costi, numero trade e avvisi per campioni piccoli/dati mancanti.
9. API REST documentata con OpenAPI. Endpoint minimi: health, import/validazione dati, elenco dataset, avvio backtest, stato/risultati backtest, metriche, trade, configurazione strategia validata, paper orders/fills mock, risk snapshot. Proteggi gli endpoint da input malevoli e limiti dimensione upload; CORS solo per l'origine frontend locale configurata. Non esporre filesystem arbitrario.
10. UI con selezione dataset/configurazione, avvio backtest/replay, stato paper ben visibile, grafici e diagnostica. Nessun bottone “live”. Non visualizzare segnali come raccomandazioni.

## ML e ricerca quant
Non aggiungere ML complesso senza necessità. Prepara confini/contratti per feature future; se implementi feature engineering, deve essere point-in-time. Per ogni ricerca: ipotesi falsificabile, baseline, split temporale/walk-forward, holdout intatto, preprocessing fit solo sul training, sensitivity a costi e report riproducibile. Niente auto-tuning sul test, self-modifying code, online learning automatico, auto-promozione o ordini generati da LLM.

## Test e qualità richiesti
Scrivi test per:
- CSV valido, vuoto, malformato, OHLC incoerente, timestamp ambiguo/misto, duplicato multi-asset.
- Segnale long e short senza look-ahead; indicatori e opening range.
- stop, target, collisione intrabar stop-first, chiusura sessione, costi e slippage.
- breakeven non raggiunto, trigger raggiunto long/short, stop breakeven dalla barra successiva, gap/costi.
- sizing, lotto, capitale condiviso, rischio/esposizione aggregata e daily-loss stop.
- broker mock idempotente, transizioni consentite, reject/partial/fill, persistenza e zero chiamate di rete.
- API: errori di validazione, dataset non trovato, limiti input; dashboard: empty/no-trade, una trade, filtri e download.
- frontend: stati loading/error/empty, chiamate API e render metriche/grafici.

Esegui i test effettivamente disponibili e riporta i comandi e gli esiti reali. Non inventare passaggi CI. Aggiungi dati di esempio sintetici chiaramente etichettati come tali. Non usare dati o risultati di esempio per affermare performance.

## Metodo di lavoro richiesto
1. Ispeziona repo/ambiente e presenta un piano breve con struttura file e criteri di accettazione.
2. Implementa un MVP completo in fasi: scaffold/config; data validation; dominio/strategy; risk manager; mock broker/SQLite; API; dashboard; test; documentazione.
3. Dopo ogni fase esegui test pertinenti e correggi i problemi. Se non puoi eseguire un comando, segnala il motivo e fornisci il comando per l'utente.
4. Rivedi il diff per endpoint live, segreti, CORS permissivo, upload non limitati, look-ahead, over-allocation, race/idempotency e metriche fuorvianti.
5. Aggiorna README con setup, comandi, schema CSV, API, architettura, assunzioni, limiti, breakeven e modalità esclusivamente mock/paper.

## Output finale obbligatorio
Rispondi in italiano con:
- Risultato e architettura implementata.
- Albero file essenziale.
- Comandi esatti per avvio locale (backend, frontend, Docker se presente) e test.
- API principali e flusso CSV -> backtest -> mock broker -> dashboard.
- Cosa è stato testato realmente e risultati.
- Limiti e funzionalità non incluse.
- Evidenza chiara: broker solo mock locale, nessun ordine live, nessuna promessa di rendimento.

Inizia ispezionando la cartella corrente e proponendo il piano. Poi procedi all'implementazione senza fermarti per approvazione dopo ogni file; fermati e chiedi conferma solo se rischi di sovrascrivere/eliminare dati esistenti o se una decisione indispensabile non può essere risolta in modo sicuro.
```
