# Prompt iniziale per Claude Code

Copia questo prompt dopo aver aperto il repository `marco-m85/trades` in Claude Code.

```text
Leggi prima `.claude/skills/intraday-paper-lab/SKILL.md` e i riferimenti pertinenti nella stessa cartella. Poi ispeziona il repository, il codice e i test esistenti: non presumere che la documentazione descriva ancora esattamente l'implementazione.

Voglio lavorare su questo progetto come sistema di ricerca quantitativa, backtest e paper trading. Mantieni il perimetro rigorosamente offline/mock/paper sandbox: non implementare, abilitare o suggerire invio di ordini reali; non chiedere né esporre credenziali.

Richiesta: [DESCRIVI QUI L'ATTIVITÀ]

Prima di modificare:
1. Riassumi obiettivo, assunzioni, file coinvolti, criteri di accettazione e rischi di look-ahead, dati stale, sizing e over-allocation.
2. Se una specifica è ambigua e cambia il comportamento, esplicita l'interpretazione e chiedi conferma solo se non è possibile procedere in sicurezza. In particolare, per il breakeven, non confondere +10% del valore nominale con +10% del rischio iniziale (0,1R).
3. Proponi un piano breve e testabile.

Implementa solo il necessario, separando dati, feature, strategia, risk manager, broker mock, persistenza e dashboard. Usa errori fail-closed, validazione degli input, idempotenza e nessun fallback verso endpoint live. Per ogni modifica alla strategia includi test deterministici per long/short, stop, target, breakeven, collisioni intrabar, costi e chiusura sessione, dove pertinenti.

Per ricerca ML usa split temporali, baseline, feature disponibili al timestamp decisionale, holdout intatto e report dei costi; niente auto-apprendimento, auto-promozione o ordini generati da LLM.

Esegui i test e controlli disponibili; nel report indica i comandi effettivamente eseguiti e il loro esito. Non dichiarare test superati se non li hai eseguiti. Aggiorna la documentazione. Concludi usando il modello `output-template.md`, indicando cosa è implementato, cosa è solo proposto, limiti, istruzioni di verifica e stato paper/sandbox. Nessuna promessa di rendimento o consulenza finanziaria.
```

## Suggerimento specifico per breakeven

Se la richiesta è “sposta lo stop a pareggio quando l'operazione è positiva del 10%”, chiarisci quale denominatore usare. Per questa skill il default di ricerca raccomandato è: attivare il breakeven quando il massimo profitto non realizzato raggiunge `+0.1R` (10% del rischio iniziale), quindi spostare lo stop al prezzo d'ingresso. Il trigger deve essere configurabile e il report deve dire che commissioni, spread e gap possono lasciare un PnL netto negativo anche con stop al prezzo d'ingresso. Se l'utente intende +10% sul prezzo o sul valore nominale, chiedi conferma prima di implementarlo.
