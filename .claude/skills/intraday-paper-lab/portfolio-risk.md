# Portfolio risk management (ricerca e simulazione)

## Prima di valutare un trade

1. Calcola rischio monetario da equity eleggibile * frazione rischio, rispettando stop distance, multiplier, tick e lot size.
2. Applica cap di esposizione/cash/leva e liquidità simulata; quantità arrotondata non deve eccedere il rischio autorizzato.
3. Valuta rischio aperto aggregato, esposizione per asset/settore/currency e posizioni correlate, non solo il singolo simbolo.
4. Applica limiti giornalieri e drawdown su equity coerente (realizzato o mark-to-market dichiarato), con reset sessione definito dal calendario exchange.
5. Rifiuta ingresso se input critico manca o non è affidabile.

## Invarianti da testare

- Allocazione totale <= capitale configurato.
- Esposizione lorda/netta entro i limiti impostati.
- Una perdita giornaliera al limite impedisce nuovi ingressi nella sessione.
- Commissioni/slippage entrano nel PnL netto e nell'equity successiva.
- Quantità <= sizing da rischio e quantità valida per il contratto.
- Una posizione non resta aperta oltre la sessione se la strategia dichiara flat overnight.
- Deposit/withdrawal non si confondono con rendimento.
- Un simbolo non riceve capitale duplicato per barre duplicate o simboli alias.

## Report rischio

Riporta metodo di allocazione (subaccount o pool condiviso), capitale iniziale, rischio per trade, esposizione, leva ipotizzata, daily stop, max drawdown e frequenza di marking. Identifica correlazione e rischi non modellati. Un limite simulato non limita perdite reali o gap oltre lo stop.
