# Scelta architetturale: applicazione o Expert Advisor?

## Raccomandazione per questo progetto

**Partirei con un'applicazione Python**, composta da motore di ricerca/backtest e servizio paper, più dashboard web. È la scelta più adatta alle esigenze elencate (multi-asset, ricerca quant/ML, metriche, grafici, provider multipli e test automatizzati) e permette di mantenere strategia e risk manager fuori dalla UI. Nel breve termine può essere un'app locale, non un servizio pubblico.

Un **Expert Advisor (EA)** ha senso solo se il target esplicito è MetaTrader (per esempio MT5/MQL5) e servono integrazione con terminale, dati e simulatore Strategy Tester di quella piattaforma. Un EA non sostituisce la ricerca riproducibile, il data pipeline o un risk engine multi-provider; può aumentare la complessità e legare il sistema a una piattaforma.

## Percorso suggerito

1. Motore Python offline, fixture/test e backtest con costi.
2. Risk manager aggregato, ledger persistente e replay deterministico.
3. Dashboard app locale con equity, drawdown, PnL/costi, breakdown, esposizioni e audit di config/dati.
4. Provider dati e broker **mock/paper sandbox** documentati e verificati, con monitoraggio e riconciliazione.
5. Solo se necessario per MetaTrader, progettare un EA separato che replica una specifica congelata; verificare equivalenza dei segnali tramite test congiunti. In questa skill l'EA resta demo/tester, non live.

Non partire da API di produzione o da automazione ordini. Non esiste una scelta universalmente migliore: decidono mercato, piattaforma broker, vincoli di latenza, strumenti e competenze del team. Per l'ambito richiesto oggi, l'app Python è il punto di partenza più flessibile; EA è un adattatore/piattaforma secondaria quando MetaTrader è un requisito.
