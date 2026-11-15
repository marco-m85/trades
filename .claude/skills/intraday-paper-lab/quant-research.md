# Quant research, day-trade e ML/LLM

## Protocollo di ricerca

1. **Ipotesi**: scrivi una frase falsificabile, meccanismo atteso, regime previsto e ragioni per cui potrebbe fallire.
2. **Dati**: registra provider/provenienza, licenza, range, frequenza, timezone, convenzione timestamp, corporate actions, missing/duplicate/outlier e simboli inclusi/esclusi.
3. **Baseline**: confronto con nessun trade e regola semplice, più benchmark pertinente quando disponibile.
4. **Split temporale**: training -> validation -> holdout finale cronologico. Mai shuffle casuale di osservazioni temporali. Usa walk-forward/purging/embargo quando label o holding period si sovrappongono.
5. **Simulazione**: include commissioni, spread, slippage, gap, vincoli quantità/tick, liquidità, stop/target e close sessione. Descrivi cosa i dati OHLC non possono modellare.
6. **Robustezza**: sensitivity analysis dei costi e parametri; per asset, periodi e regimi; stabilità fuori campione. Registra tentativi totali per evidenziare multiple testing.
7. **Decisione**: criteri predefiniti; nessuna promozione automatica. Se risultati fragili o campione piccolo, dichiaralo e non suggerire deployment.
8. **Riproducibilità**: salva config, commit, versioni, seed, fonte/dataset hash (se consentito) e comandi.

## Metriche da definire

Mostra trade count e copertura dati; PnL lordo/netto e costi; equity e drawdown (definizione e frequenza); return e annualizzazione solo se giustificate; esposizione/turnover; expectancy, media/mediana, distribuzione win/loss; profit factor con gestione del denominatore zero; metriche rischio-rendimento solo con convenzioni esplicite; breakdown per simbolo/periodo/regime. Non usare win rate isolatamente. Esplicita incertezza e assenza di garanzia.

## LLM/ML evolutivo, ma supervisionato

- LLM: solo generazione/riassunto ipotesi, documentazione o annotazione. Gli output devono essere controllabili e non sono segnali affidabili per default.
- ML: baseline prima del modello; definisci target e orizzonte; allinea feature/label senza usare dati futuri o revisioni disponibili dopo il tempo decisionale.
- Preprocessing, feature selection e tuning vanno fittati solo nel training fold; il holdout finale resta intatto.
- Valuta calibration, class imbalance, drift, regime, costi, falsi positivi, stabilità e ablation; accuracy da sola non basta.
- Versiona codice, dataset, feature schema, modello e report. Riproduci la valutazione prima della revisione umana.
- No self-modifying code, online learning da risultati live, auto-tuning sul test finale, accesso LLM a credenziali/ordini o auto-approvazione del modello.
- L'evoluzione è una serie di esperimenti offline revisionati da una persona, con rollback e confronto a baseline.

## Scheda esperimento

- ID/titolo e data:
- Ipotesi e criterio di falsificazione:
- Universe, data source, periodo e timeframe:
- Regole del segnale e disponibilità informativa:
- Costi e assunzioni di fill:
- Allocazione/risk limit:
- Split e benchmark:
- Risultati netti, drawdown, esposizione e numero trade:
- Breakdown e sensitivity:
- Leakage/multiple-testing checks:
- Limiti e failure cases:
- Commit/config/seed/comando:
- Esito: scartato / da approfondire offline / candidato a paper test (revisione umana):
