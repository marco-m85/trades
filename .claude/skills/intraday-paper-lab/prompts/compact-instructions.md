# Istruzioni compatte per agente AI

```text
Lavora su marco-m85/trades come progetto quant di ricerca e paper trading. Prima leggi `.claude/skills/intraday-paper-lab/SKILL.md`, ispeziona codice e test attuali. Solo offline/mock/paper sandbox: mai ordini live, endpoint live, fallback live o segreti in chat/log/git. Nessuna consulenza o promessa di rendimento.

Flusso: dati validati -> feature point-in-time -> strategia deterministica -> RiskManager centrale -> esecuzione simulata/sandbox -> ledger -> metriche/dashboard. Fail closed per dati stale/invalidi, rischio incerto, errori API e limiti violati. Evita look-ahead/leakage; rispetta timestamp/timezone e costi, spread, slippage, gap e ambiguità OHLC. Multi-asset: capitale/esposizione aggregati non devono superare i cap.

Quant/ML: ipotesi falsificabile, baseline, split temporale/walk-forward, preprocessing solo training, holdout intatto, costi e sensitivity, risultati riproducibili e review umana. LLM solo assistente di ricerca; niente auto-tuning/promozione, self-modifying code o ordini autonomi.

Broker: solo mock locale o paper/sandbox confermato da documentazione ufficiale; niente URL/API inventati. Timeout, retry limitati, idempotenza, validazione e redazione segreti. Dashboard: equity realizzata vs MTM etichettata, drawdown, costi, breakdown, timezone, fonte/config e sample size; gestisci zero trade/dati invalidi.

Breakeven: chiarisci il denominatore del “10%”. Default documentato proposto: a massimo profitto non realizzato +0,1R, stop all'entry; non garantisce pareggio netto per costi/gap. In OHLC, stop aggiornato da barra successiva salvo sequenza verificabile. Se intende +10% del prezzo/notional, chiedi conferma.

Segui checklist e test pertinenti; esegui davvero i controlli disponibili. Aggiorna docs. Rispondi nella lingua utente con risultato, file, sicurezza/rischi, comandi e risultati test, uso e limiti; separa implementato da proposto e non dichiarare mai live-ready/profittevole senza evidenza.
```
