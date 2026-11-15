# Broker/data API: solo mock o paper sandbox

## Gate prima dello sviluppo

- Identifica provider, versione API e documentazione ufficiale corrente.
- Conferma per iscritto/documentazione che endpoint e credenziali sono paper/sandbox.
- Se endpoint/ambiente non è chiaro, fermati al mock locale e chiedi documentazione; non inventare URL.
- Verifica che config live causi un rifiuto esplicito, non un fallback.

## Interfacce minime

Separare `MarketDataProvider` da `PaperExecutionProvider`. Modelli interni validati: `Bar/Quote`, `AccountSnapshot` fittizio, `OrderIntent`, `OrderUpdate`, `PaperFill`. L'engine strategy produce intenti, RiskManager approva/rifiuta, adapter sandbox esegue soltanto dopo l'approvazione.

## Requisiti

- Base URL sandbox hard-coded/configurata esplicitamente; niente endpoint live predefinito.
- Modalità paper esplicita e controllo all'avvio che abortisce se non paper.
- Timeout, retry limitati con backoff, rate limit handling e idempotency key.
- Gestione di reject, partial fill, cancel, timeout ambiguo e riconciliazione senza duplicare eventi.
- Validazione schema, timestamp, simbolo, mercato aperto, freshness, sequence e completezza barra.
- TLS verifica certificati; niente bypass della verifica.
- Token solo via env/secret manager; `.env` escluso da git; mai stampare header, token o account ID.
- Kill switch paper, logging redatto e messaggi visibili; errori critici bloccano nuovi intenti.
- Mock deterministico per test; nessuna richiesta di rete nei test unitari.

## Acceptance tests

- Modalità live/config sconosciuta -> avvio rifiutato.
- Token assente/scaduto, payload malformato, feed stale, timeout, 429/5xx -> errore chiaro, niente nuovi ingressi.
- Retry non produce duplicati; eventi ripetuti sono idempotenti.
- Stato timeout ambiguo viene riconciliato prima di riprovare.
- Partial fill e rifiuto aggiornano ledger e rischio coerentemente.
- Log e report non contengono segreti.

Non chiamare “integrazione broker” un feed HTTP di barre o un ledger in memoria. Non implementare ordini live.
