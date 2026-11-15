# Architettura e confini

## Flusso logico

`DataSource -> Normalizer/Validator -> Bar Store -> Features -> Strategy -> RiskManager -> Paper Execution -> Ledger/Metrics -> Dashboard`

Il controllo di rischio è server-side/core, non una semplice opzione UI. Le interfacce sono separate affinché backtest, replay e paper sandbox riutilizzino le stesse regole senza confondere simulazione e ordini live.

## Componenti

- **DataSource**: CSV, fixture o provider adapter documentato. Non decide segnali.
- **Normalizer/Validator**: normalizza simboli e tempo; rifiuta schema, timezone, prezzi o barre non valide.
- **Bar Store**: deduplica usando chiave strumento+timestamp e conserva provenienza/completezza.
- **Features**: calcola solo su informazioni disponibili al timestamp di decisione.
- **Strategy**: output immutabile `Signal` (strumento, side, timestamp, motivi, versione); non accede a credenziali o broker.
- **RiskManager**: valuta capitale, size, esposizione, limiti giornalieri/portafoglio e ritorna approve/reject con motivazione.
- **Paper Execution**: mock deterministico o sandbox ufficiale; vietato endpoint live.
- **Ledger**: ordini simulati, fill ipotetici, costi e equity; persistenza e deduplicazione esplicite.
- **Metrics/Dashboard**: calcola metriche da ledger e mostra ipotesi e qualità dati.

## Stati di esempio

Barra: `received -> validated -> finalized` oppure `rejected`.
Intento paper: `created -> risk_rejected | submitted_to_sandbox -> accepted/rejected -> partial/filled/canceled`.
Usa idempotency key e transizioni consentite; non assumere che una richiesta HTTP riuscita equivalga a fill.

## Fail-closed

Disabilita nuove entrate simulate se feed stale, calendario/mercato sconosciuto, schema non valido, storage non disponibile, rischio non calcolabile o errore non riconciliato. Mantieni stato/errore visibile. Non alterare automaticamente limiti o usare prezzi sostitutivi.

## Maturità

1. Ricerca offline e fixture deterministiche.
2. Backtest validato cronologicamente con costi.
3. Replay/event-driven e ledger persistente.
4. Paper sandbox ufficiale con monitoraggio e riconciliazione.

Ogni fase richiede revisione e test prima di proseguire. Nessuna fase abilita trading live. Non dichiarare robustezza di produzione senza requisiti, audit e verifiche reali.
