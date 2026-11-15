# Claude skill: Intraday Paper Lab

Skill project-local: `.claude/skills/intraday-paper-lab/SKILL.md`.

Per iniziare rapidamente, copia `.claude/skills/intraday-paper-lab/prompts/initial-prompt.md`. Per impostazioni persistenti usa `prompts/system-and-project-instructions.md` o `prompts/compact-instructions.md`.

La skill completa comprende checklist, architettura, ricerca quant/ML/LLM supervisionata, risk management multi-asset, mock e paper sandbox, strategia intraday con stop/target/breakeven e requisiti per dashboard. Vedi i riferimenti collegati in `SKILL.md`.

## Broker, app e EA

Il broker è solo mock locale o sandbox/paper ufficiale verificato. Non è stato aggiunto un provider broker concreto né l'invio di ordini live. Per il progetto attuale è raccomandata un'app Python con dashboard; un EA è appropriato solo se MetaTrader è un requisito e deve restare in tester/demo secondo le regole della skill. Vedi `app-vs-expert-advisor.md`.

## Breakeven al 10%

La specifica deve distinguere 10% del rischio iniziale (0,1R) da 10% del prezzo/notional. La skill propone 0,1R come default di ricerca configurabile, non garantisce PnL netto nullo; chiedere chiarimento se l'utente intende un'altra base di calcolo.
