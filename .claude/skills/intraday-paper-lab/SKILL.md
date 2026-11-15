---
name: intraday-paper-lab
description: >-
  Use this skill when working in the marco-m85/trades repository or when asked to
  understand, run, test, review, or safely extend its educational intraday multi-asset
  backtester, Streamlit performance dashboard, or HTTP-feed paper-trading prototype.
  This skill is for research and paper simulation only; it must never be used to
  place or recommend real trades.
---

# Intraday Paper Lab

Assist with this repository as an educational research and paper-simulation project. Start by inspecting the current repository files; do not assume the implementation still matches this document. The strategy is an example opening-range breakout and is **not** the missing “day trade main skill” mentioned earlier in the repository conversation.

## Safety boundaries

- Never connect to a real brokerage, submit/cancel/modify live orders, or provide instructions that turn the paper runner into live execution.
- Do not describe signals as recommendations, predictions, or guaranteed returns. Explain that this is software research, not financial advice.
- Keep any new execution adapter simulated and local unless the user specifically requests a different safe, non-live demonstration. Do not request or expose brokerage credentials or API secrets.
- Do not claim that a backtest or paper result predicts future performance. Call out assumptions, missing market microstructure, data quality, session/time-zone, liquidity, gap, spread, and slippage risks.
- Prefer conservative assumptions. When a bar touches both stop and target, the current backtest treats the stop as hit first.

## Project map

- `daytrade.py`: OHLCV CSV parsing, indicators, opening-range strategy, independent per-symbol backtests, and summary/trade CSV output.
- `dashboard.py`: Streamlit dashboard for uploaded historical CSV files and performance charts.
- `live_paper.py`: generic HTTP JSON polling example and in-memory simulated ledger. It does not provide a market-data vendor or real broker integration.
- `requirements.txt`: dashboard dependencies.
- `sample.csv`: small demonstration dataset.
- `README.md`: installation, usage, data format, and limitations.

## Current strategy model

The example implementation uses an opening range (default 15 minutes), breakout confirmation, fast/slow EMA trend agreement, session VWAP, a recent-volume comparison, and ATR-based volatility/range filters. Stops are placed at the opposite opening-range boundary; the target is expressed as a multiple of initial risk (default 2R). It limits risk and exposure per independent asset sub-account, uses one trade per asset per session, and simulates fees and adverse slippage. These are configurable example rules, not investment recommendations.

When describing or changing a signal, make the exact rule and any look-ahead or bar-timing assumptions explicit. Indicators must use only data available at the signal bar. Do not infer signal quality from the small bundled sample.

## Data contract

CSV columns: required `timestamp,open,high,low,close`; optional `volume,symbol`. If omitted, symbol defaults to `DEFAULT`. Timestamps should be ISO 8601 and consistent with the relevant exchange's session/time zone. Multi-asset records need one symbol per bar. Validate OHLC relationships, positive prices, duplicate symbol/timestamp pairs, and missing or malformed data. Never silently mix time zones or asset bars.

The generic HTTP paper feed expects JSON with a `bars` list; each row contains `symbol,timestamp,open,high,low,close` and optional `volume`. Treat provider-specific schemas, authentication, rate limits, candle-finalization rules, and data licensing as integration work, not as already supported functionality.

## Working practices

1. Inspect relevant source and tests before editing; preserve the paper-only boundary.
2. Prefer small changes with explicit configuration and validation. Keep strategy logic separate from UI/feed adapters where practical.
3. For backtest changes, test long and short cases, stop/target collisions, end-of-session closure, multiple symbols, empty data, malformed CSV, and fee/slippage behavior as relevant.
4. For dashboard changes, test empty and non-empty trades and ensure uploaded-file handling works without writing user uploads to disk.
5. For feed/ledger changes, test repeated polls, duplicate bars, stale/incomplete candles, network errors, and restart semantics. Clearly distinguish provisional signals from finalized simulated trades.
6. Run available tests and static checks, and report which were actually run. Do not claim unrun tests passed.
7. Update `README.md` when command-line behavior, CSV schemas, dependencies, or safety limitations change.

## Important implementation caveats

Verify these against source before relying on them; fix or report them if they affect the requested task:

- Portfolio backtests allocate equal, independent sub-accounts per symbol; they are not a shared portfolio-level risk allocator.
- The paper polling example rebuilds a backtest from fetched history. Do not mistake its results for robust event-driven order/position state or production-grade real-time simulation. Confirm that a trade is genuinely finalized before recording it as a fill.
- Indicators, session clock assumptions, and the data provider's bar timestamp convention need validation for each asset/market.

## Response style

Respond in the user's language. State what changed and how to verify it. Distinguish implemented functionality from suggestions or limitations, and never imply that the system can place live trades.
