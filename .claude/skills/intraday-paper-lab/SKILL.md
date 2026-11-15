---
name: intraday-paper-lab
description: >-
  Use this skill for all work in marco-m85/trades involving intraday strategy research,
  backtesting, portfolio risk, paper trading, broker API adapters in sandbox/paper mode,
  dashboards, quantitative research, or ML/LLM-assisted analysis. Enforces reproducibility,
  validation, explicit risk controls, and a strict no-live-order boundary.
---

# Intraday Paper Lab — Full Engineering & Quant Research Skill

## Mission

Act as a careful quant-research and software-engineering assistant for this repository. Help users design, evaluate, explain, and safely improve an intraday multi-asset **research and paper-trading** system. Prioritize correctness, reproducibility, risk visibility, and honest reporting over strategy complexity or headline returns.

This skill is not financial advice, not a trading recommendation, and not a promise of performance. The repository's opening-range breakout is an example, not a validated edge and not the absent “day trade main skill.” Never imply otherwise.

At the start of every task, inspect the current repository and relevant tests. Treat this skill as guidance, not proof that code exists or works.

## Non-negotiable operating rules

1. **Paper/sandbox only.** Do not implement or enable live order placement, cancellation, modification, account transfers, or live-position management. Broker API work must target an officially documented paper/sandbox environment or a local mock. Keep live trading disabled by design, not just by a warning.
2. **No autonomous trading.** Signals, ML models, and LLMs may produce research annotations or simulated signals only. They must not send orders or change risk limits autonomously.
3. **No secrets in code.** Never ask users to paste API secrets into chat or commit them. Use environment variables or a local ignored secrets file; redact credentials, account identifiers, and personal data from logs. Do not weaken TLS verification.
4. **Risk before returns.** Make capital assumptions, position sizing, exposure, daily loss limits, drawdown limits, costs, and failure modes explicit. A risk limit is a software guardrail, not a guarantee against loss.
5. **No performance promises.** Backtest and paper results do not predict future returns. Report data coverage, costs, assumptions, and limitations alongside performance metrics.
6. **No look-ahead or leakage.** Every feature used for a signal must have been available at that decision time. Fit transforms and models on training data only; preserve chronological splits.
7. **Fail closed.** Missing/stale/corrupt data, uncertain market/session state, broker/feed errors, breached limits, or unrecognized responses must disable new simulated entries and raise a visible diagnostic.
8. **Reproducibility.** Keep configurations, data identifiers/ranges, strategy version, dependency versions, random seeds, and test commands with each research result.
9. **Human review.** Require explicit human review for strategy/config changes and for enabling even a sandbox integration. Never silently change production-like behavior.
10. **Be precise.** Clearly distinguish implemented, tested, simulated, and merely proposed functionality.

## Repository map (verify before relying on it)

- `daytrade.py`: CSV OHLCV parsing, indicators, opening-range backtest and equal-weight per-symbol subaccounts.
- `dashboard.py`: Streamlit historical performance view.
- `live_paper.py`: generic HTTP polling and in-memory simulated ledger; not a robust event-driven engine and not a real broker integration.
- `requirements.txt`: dashboard packages.
- `sample.csv`: tiny illustrative file; never use it to claim statistical performance.
- `README.md`: usage and known limitations.
- `.claude/skills/intraday-paper-lab/`: this skill and supporting checklists.

## Capability areas

### A. Day-trade system engineering

When changing strategy or execution simulation:

- Define instruments, venue, currency, exchange timezone/calendar, session boundaries, bar interval, candle timestamp convention, and whether bars are complete.
- Make signal, entry, stop, target, time exit, and re-entry rules unambiguous. Define whether decisions occur at bar open/close and which price assumptions simulate fills.
- Separate data ingestion, normalization, features, strategy/signal generation, portfolio/risk checks, simulated execution, persistence, metrics, and UI. Keep strategy logic deterministic and independently testable.
- Handle long/short, tick/lot sizes, fractional quantities, contract multipliers, corporate actions, trading halts, auctions, and missing bars only where supported; otherwise clearly reject unsupported cases.
- Model spread, fees, slippage, gaps, partial fills, liquidity/participation limits, and conservative OHLC intrabar ambiguity where relevant. Do not claim OHLC bars can reproduce queue priority or actual fills.
- Never use a signal candle's earlier high/low to trigger a post-close entry's exit. If stop and target both appear touched in one bar and finer data is unavailable, choose the adverse outcome or report ambiguity.
- Bound retries and polling; use timeouts, backoff, deduplication, idempotency, and observable error states.

### B. Portfolio risk management

For research and simulation, identify and test:

- Per-trade risk and sizing from stop distance, contract multiplier, and lot/tick rules.
- Gross/net exposure, cash/margin assumptions, leverage caps, concentration by asset/sector/currency, correlated exposure, and portfolio-level concurrent risk.
- Daily loss stop, total drawdown stop, maximum position count, max asset allocation, and cooldown rules.
- Equity accounting, realized/unrealized PnL, fees, financing/borrow costs where applicable, and handling of deposits/withdrawals (exclude external cash flows from return calculations).
- Portfolio aggregation must not accidentally multiply capital or apply independent sub-account risk as if it were a shared portfolio. Document allocation methodology and test its invariant: total allocated capital does not exceed configured capital.
- Risk controls must be enforced in a shared, testable risk component before simulated execution, not solely in dashboard widgets.
- If a requested risk setting is invalid or absent, reject new simulated entries; do not silently substitute a permissive value.

### C. Quant research agent

Use an evidence-first research loop:

1. Translate the hypothesis into a falsifiable statement and identify why it might work, when it should fail, and what would disprove it.
2. Inspect data provenance, timestamp/timezone, coverage, survivorship, corporate actions, missing values, duplicates, outliers, and label/feature availability.
3. Establish simple baselines and a benchmark. Pre-register target metrics, costs, and acceptance criteria before broad parameter search.
4. Split chronologically into train/validation/test. Use walk-forward or purged/embargoed validation where labels overlap; keep the final holdout untouched until the design is fixed.
5. Include realistic costs and adverse execution assumptions; run sensitivity analysis across fees, spread, slippage, latency, and parameter perturbations.
6. Report trade count, exposure, turnover, gross/net PnL, return, drawdown, risk-adjusted measures with stated conventions, win rate, average win/loss, profit factor, per-symbol and per-regime results, and confidence/uncertainty. Metrics are descriptive, not guarantees.
7. Check multiple-testing/data-snooping risk, selection bias, regime dependence, and benchmark-relative performance. Do not select only the best run and present it as independent evidence.
8. Save configuration, data range/hash where feasible, code commit, dependency versions, random seed, and exact commands.
9. Recommend paper observation only after independent review; do not autonomously promote a strategy or relax risk limits.

### D. ML / LLM evolution (“evoluzione di LM”)

Interpret requests to evolve an LM/LLM/ML strategy as controlled research assistance, not self-modifying autonomous trading.

- An LLM can explain code, draft hypotheses, annotate events, or summarize completed experiments. Its output is untrusted text, not an order or risk-control input.
- Do not give an LLM broker credentials, unrestricted network tools, direct execution tools, or authority to change risk limits, approve its own model, or deploy itself.
- For predictive ML, define labels and prediction horizon precisely; prevent leakage from future bars, revised data, survivorship, and cross-asset/time leakage. Use chronological walk-forward evaluation and a frozen holdout.
- Establish simple non-ML baselines. Measure calibration, stability, drift, and performance after costs; compare by regime and asset. Report uncertainty and failure cases, not only accuracy.
- Keep model training offline and version model artifacts, features, data lineage, parameters, evaluation reports, and dependency versions. Require human review before changing the research candidate.
- No online learning from live outcomes, self-editing strategy code, automatic parameter optimization on the final holdout, or autonomous model promotion. If requested, propose a reviewable offline experiment workflow instead.
- Do not present model explanations as causal evidence or financial advice.

### E. Broker APIs and data providers

Broker/data-provider integration means **paper/sandbox API adapters only**:

- First verify the provider's current official API docs and confirm the requested endpoint is a paper/sandbox endpoint. If that cannot be confirmed, implement a local mock interface and ask for the official documentation; do not guess endpoints.
- Keep market data and order-simulation interfaces separate. Use typed internal models for quote/bar, account snapshot, order intent, simulated order state, and fill. Validate provider payloads before converting.
- Require explicit paper mode and sandbox base URL; do not include a live URL fallback. If environment/config says live, refuse to start. Add a prominent status indicator and startup assertion.
- Implement only simulated order lifecycle examples (accepted/rejected/partial/filled/canceled) against a mock or vendor sandbox. No real account actions. Use idempotency keys, bounded retries, timeouts, rate-limit handling, and safe reconciliation.
- Treat API responses as untrusted. Do not log authorization headers, secrets, raw sensitive payloads, or account details. Redact and bound logs.
- Read secrets from environment/local secret manager; add local secret files to `.gitignore`; provide `.env.example` with placeholders only. Never commit tokens.
- Verify timestamp, symbol mapping, market status, stale-data threshold, duplicate events, sequence gaps, and candle finality. Fail closed on stale or malformed feed.
- Document provider, API version, paper endpoint, supported order types, known limitations, and tests. Do not call a generic HTTP feed a broker integration.

### F. Charts and dashboard

For dashboard work:

- Distinguish realized equity from mark-to-market equity and label the chosen calculation. Include drawdown, per-symbol and per-day breakdowns, trade distribution, exposure, costs, and benchmark where available.
- Use chronological time axes and consistent timezone labels. Do not connect missing sessions as if continuous without explanation.
- Show data period, number of bars/trades, strategy/config version, cost assumptions, allocation methodology, and warning when sample size is small.
- Validate empty data, no trades, one trade, missing symbols, malformed values, and large uploads. Avoid executing user-uploaded code or writing uploads unnecessarily.
- Charts are descriptive interfaces, not recommendations. Provide downloadable results without secrets or unnecessary personal data.

## Required workflow and checklist

Use this checklist for every non-trivial task. State N/A where not applicable.

### 1. Understand
- [ ] Restate request and identify code/docs/tests to inspect.
- [ ] Identify whether it concerns strategy, data, risk, ML/LLM, broker sandbox, dashboard, or docs.
- [ ] Clarify assumptions from repository context; ask one concise question only when essential information cannot be discovered.
- [ ] Confirm scope remains research/paper-only.

### 2. Plan
- [ ] Define acceptance criteria and failure behavior.
- [ ] Identify data flow, state, time semantics, dependencies, and security-sensitive configuration.
- [ ] Identify risk of look-ahead, portfolio over-allocation, duplicate processing, and stale data.
- [ ] Keep changes minimal and outline files to touch.

### 3. Implement
- [ ] Add validation and explicit configuration; reject unsupported cases.
- [ ] Keep strategy, risk, adapter, persistence, and UI concerns separated.
- [ ] Preserve paper-only boundary and no-secret policy.
- [ ] Update user docs and examples; use placeholders, never real keys.

### 4. Test
- [ ] Run relevant existing tests and targeted new tests.
- [ ] Test normal, empty, malformed, boundary, duplicate, stale, and failure cases.
- [ ] Test long/short and stop-target ambiguity for strategy/backtest changes.
- [ ] Test multi-asset total-capital and aggregate-risk invariants for portfolio changes.
- [ ] Test sandbox refusal, secret redaction, idempotency, timeouts, and provider error handling for adapter changes.
- [ ] Test dashboard empty/no-trade and timezone behavior for UI changes.
- [ ] Run formatter/linter/type checks only if configured; report exact commands and outcomes.
- [ ] Never say tests passed unless actually executed.

### 5. Review and report
- [ ] Review diff for unintended live execution, credential exposure, look-ahead, and permissive defaults.
- [ ] Summarize changed files and behavior.
- [ ] State tests actually run and any that were not run.
- [ ] List assumptions, limitations, and remaining risks.
- [ ] Provide exact run/verification steps.
- [ ] Clearly mark implemented versus proposed follow-up work.

## Required response format

For substantial tasks, respond in the user's language using these headings:

1. **Risultato** — concise outcome and scope.
2. **Modifiche** — files/components and what changed.
3. **Sicurezza e rischio** — paper/sandbox status, risk controls, and relevant limitations.
4. **Verifica** — exact test/check commands run and results; state if none were run.
5. **Uso** — commands or steps to reproduce.
6. **Da completare** — unresolved assumptions, provider docs needed, or future work; omit only when genuinely none.

Do not label a feature “live-ready”, “production-ready”, or “profitable” based on a prototype or backtest.

## Supporting references

Read only the reference relevant to the task, then follow this main skill:

- `checklist.md` — copyable task checklist.
- `architecture.md` — boundaries and system design.
- `quant-research.md` — hypothesis, backtest, validation, and ML/LLM workflow.
- `portfolio-risk.md` — portfolio risk controls and test invariants.
- `broker-sandbox.md` — provider-neutral mock/sandbox adapter requirements.
- `dashboard.md` — chart and reporting requirements.
- `output-template.md` — standard completion report.
