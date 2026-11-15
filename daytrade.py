#!/usr/bin/env python3
"""Educational multi-asset intraday backtester. No connection to a real broker."""
from __future__ import annotations

import argparse
import csv
import json
from dataclasses import asdict, dataclass
from datetime import datetime, time, timedelta
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class Bar:
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float = 0.0
    symbol: str = "DEFAULT"


@dataclass
class Trade:
    symbol: str
    date: str
    side: str
    entry_time: str
    exit_time: str
    entry: float
    exit: float
    stop: float
    target: float
    quantity: float
    gross_pnl: float
    fees: float
    net_pnl: float
    exit_reason: str
    equity_after: float


def load_bars(path: str | Path) -> list[Bar]:
    bars: list[Bar] = []
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        required = {"timestamp", "open", "high", "low", "close"}
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise ValueError(f"CSV must contain columns: {', '.join(sorted(required))}")
        for line, row in enumerate(reader, 2):
            try:
                ts = datetime.fromisoformat(row["timestamp"].strip())
                o, h, l, c = (float(row[k]) for k in ("open", "high", "low", "close"))
                v = float(row.get("volume") or 0)
                symbol = (row.get("symbol") or "DEFAULT").strip().upper()
            except (TypeError, ValueError) as exc:
                raise ValueError(f"Invalid CSV line {line}: {exc}") from exc
            if not symbol or min(o, h, l, c) <= 0 or h < max(o, c, l) or l > min(o, c, h) or v < 0:
                raise ValueError(f"Invalid OHLCV/symbol values on CSV line {line}")
            bars.append(Bar(ts, o, h, l, c, v, symbol))
    bars.sort(key=lambda b: (b.timestamp, b.symbol))
    keys = [(b.timestamp, b.symbol) for b in bars]
    if len(set(keys)) != len(keys):
        raise ValueError("CSV contains duplicate timestamps for a symbol")
    return bars


def _ema(values: list[float], period: int) -> list[float]:
    alpha = 2 / (period + 1)
    result = []
    value = values[0]
    for x in values:
        value = alpha * x + (1 - alpha) * value
        result.append(value)
    return result


def _indicators(bars: list[Bar], atr_period: int, fast: int, slow: int, volume_period: int):
    closes = [b.close for b in bars]
    ema_fast, ema_slow = _ema(closes, fast), _ema(closes, slow)
    true_ranges = []
    for i, b in enumerate(bars):
        prev = bars[i - 1].close if i else b.close
        true_ranges.append(max(b.high - b.low, abs(b.high - prev), abs(b.low - prev)))
    atr = []
    for i in range(len(bars)):
        window = true_ranges[max(0, i - atr_period + 1):i + 1]
        atr.append(sum(window) / len(window))
    volumes = []
    for i in range(len(bars)):
        window = [x.volume for x in bars[max(0, i - volume_period):i] if x.volume > 0]
        volumes.append(sum(window) / len(window) if window else 0)
    return ema_fast, ema_slow, atr, volumes


def backtest_symbol(
    bars: Iterable[Bar], *, initial_cash: float = 10_000, risk_fraction: float = .005,
    target_r: float = 2, daily_loss_fraction: float = .02, max_exposure_fraction: float = 1,
    opening_time: time = time(9, 30), opening_range_minutes: int = 15,
    fee_bps: float = 1, slippage_bps: float = 1, allow_short: bool = True,
    atr_period: int = 14, fast_ema: int = 9, slow_ema: int = 21,
    volume_period: int = 20, min_atr_pct: float = .001, max_atr_pct: float = .03,
    min_range_atr: float = .25, max_range_atr: float = 2.5,
) -> tuple[list[Trade], float]:
    """Opening-range breakout confirmed by EMA trend, VWAP and volume.

    ATR% and opening-range/ATR filters avoid extremely quiet/volatile sessions.
    Signal is evaluated at bar close; exits start on the next bar. Stop wins when a
    bar touches both stop and target. All timestamps should use the exchange timezone.
    """
    if initial_cash <= 0 or not 0 < risk_fraction <= 1:
        raise ValueError("initial_cash must be positive and risk_fraction in (0, 1]")
    if not 0 < daily_loss_fraction <= 1 or not 0 < max_exposure_fraction <= 1:
        raise ValueError("daily loss and exposure fractions must be in (0, 1]")
    if target_r <= 0 or opening_range_minutes <= 0 or min_atr_pct < 0 or max_atr_pct <= min_atr_pct:
        raise ValueError("Invalid target, opening range, or ATR% bounds")
    if min(fee_bps, slippage_bps) < 0 or min(atr_period, fast_ema, slow_ema, volume_period) < 1:
        raise ValueError("Fees/slippage must be non-negative and indicator periods positive")
    seq = sorted(bars, key=lambda x: x.timestamp)
    if not seq:
        return [], initial_cash
    for a, b in zip(seq, seq[1:]):
        if a.timestamp == b.timestamp:
            raise ValueError("Duplicate timestamps for a symbol")
    ef, es, atrs, avgs = _indicators(seq, atr_period, fast_ema, slow_ema, volume_period)
    by_day: dict[object, list[int]] = {}
    for i, bar in enumerate(seq):
        by_day.setdefault(bar.timestamp.date(), []).append(i)
    equity, trades = initial_cash, []
    for day, indices in by_day.items():
        session_start = datetime.combine(day, opening_time)
        range_end = session_start + timedelta(minutes=opening_range_minutes)
        range_idxs = [i for i in indices if session_start <= seq[i].timestamp < range_end]
        if not range_idxs:
            continue
        hi = max(seq[i].high for i in range_idxs)
        lo = min(seq[i].low for i in range_idxs)
        if hi <= lo:
            continue
        candidates = [i for i in indices if seq[i].timestamp >= range_end]
        start_equity, pos = equity, None
        for n, i in enumerate(candidates):
            bar = seq[i]
            if pos is None:
                if equity <= start_equity * (1 - daily_loss_fraction):
                    break
                atr = atrs[i]
                atr_pct = atr / bar.close
                range_atr = (hi - lo) / atr if atr else float("inf")
                if not (min_atr_pct <= atr_pct <= max_atr_pct and min_range_atr <= range_atr <= max_range_atr):
                    continue
                if avgs[i] and bar.volume < avgs[i]:
                    continue
                long_signal = bar.close > hi and ef[i] > es[i] and bar.close > hi  # VWAP check below
                short_signal = allow_short and bar.close < lo and ef[i] < es[i]
                # Session VWAP is computed only through the current completed bar.
                session_vol = sum(seq[j].volume for j in indices if seq[j].timestamp.date() == day and seq[j].timestamp <= bar.timestamp)
                session_vwap = (sum(((seq[j].high + seq[j].low + seq[j].close) / 3) * seq[j].volume
                                    for j in indices if seq[j].timestamp.date() == day and seq[j].timestamp <= bar.timestamp)
                               / session_vol) if session_vol else bar.close
                long_signal = long_signal and bar.close > session_vwap
                short_signal = short_signal and bar.close < session_vwap
                if not long_signal and not short_signal:
                    continue
                side = "long" if long_signal else "short"
                entry = bar.close * (1 + slippage_bps / 10_000 if side == "long" else 1 - slippage_bps / 10_000)
                stop = lo if side == "long" else hi
                unit_risk = entry - stop if side == "long" else stop - entry
                if unit_risk <= 0:
                    continue
                qty = min(equity * risk_fraction / unit_risk, equity * max_exposure_fraction / entry)
                if qty <= 0:
                    continue
                target = entry + target_r * unit_risk if side == "long" else entry - target_r * unit_risk
                pos = (side, entry, stop, target, qty, bar.timestamp)
                continue
            side, entry, stop, target, qty, entry_ts = pos
            hit_stop = bar.low <= stop if side == "long" else bar.high >= stop
            hit_target = bar.high >= target if side == "long" else bar.low <= target
            if hit_stop or hit_target or n == len(candidates) - 1:
                reason = "stop" if hit_stop else "target" if hit_target else "session_close"
                raw_exit = stop if hit_stop else target if hit_target else bar.close
                exit_price = raw_exit * (1 - slippage_bps / 10_000 if side == "long" else 1 + slippage_bps / 10_000)
                gross = (exit_price - entry) * qty * (1 if side == "long" else -1)
                fees = (entry + exit_price) * qty * fee_bps / 10_000
                net = gross - fees
                equity += net
                trades.append(Trade(seq[0].symbol, str(day), side, entry_ts.isoformat(), bar.timestamp.isoformat(),
                                    entry, exit_price, stop, target, qty, gross, fees, net, reason, equity))
                pos = None
                break  # max one position/trade per asset per session
    return trades, equity


def backtest_portfolio(bars: Iterable[Bar], **kwargs) -> tuple[list[Trade], float]:
    """Equal-weight independent paper subaccounts; avoids leverage across symbols."""
    grouped: dict[str, list[Bar]] = {}
    for bar in bars:
        grouped.setdefault(bar.symbol, []).append(bar)
    if not grouped:
        return [], float(kwargs.get("initial_cash", 10_000))
    total_cash = float(kwargs.get("initial_cash", 10_000))
    per_asset = total_cash / len(grouped)
    args = dict(kwargs)
    args["initial_cash"] = per_asset
    all_trades, final_total = [], 0.0
    for symbol in sorted(grouped):
        result, final = backtest_symbol(grouped[symbol], **args)
        all_trades.extend(result)
        final_total += final
    return sorted(all_trades, key=lambda t: (t.entry_time, t.symbol)), final_total


def summarize(trades: list[Trade], final_equity: float, initial_cash: float) -> dict:
    wins = [t for t in trades if t.net_pnl > 0]
    losses = [t for t in trades if t.net_pnl < 0]
    gp, gl = sum(t.net_pnl for t in wins), -sum(t.net_pnl for t in losses)
    return {"initial_cash": initial_cash, "final_equity": final_equity, "net_pnl": final_equity - initial_cash,
            "return_pct": (final_equity / initial_cash - 1) * 100, "trades": len(trades),
            "wins": len(wins), "losses": len(losses), "win_rate_pct": len(wins) / len(trades) * 100 if trades else 0,
            "profit_factor": gp / gl if gl else None}


def main() -> None:
    p = argparse.ArgumentParser(description="Multi-asset intraday CSV backtester (paper only)")
    p.add_argument("csv")
    p.add_argument("--cash", type=float, default=10_000)
    p.add_argument("--risk", type=float, default=.005)
    p.add_argument("--target-r", type=float, default=2)
    p.add_argument("--daily-loss", type=float, default=.02)
    p.add_argument("--max-exposure", type=float, default=1)
    p.add_argument("--open", default="09:30")
    p.add_argument("--range-minutes", type=int, default=15)
    p.add_argument("--fee-bps", type=float, default=1)
    p.add_argument("--slippage-bps", type=float, default=1)
    p.add_argument("--min-atr-pct", type=float, default=.001)
    p.add_argument("--max-atr-pct", type=float, default=.03)
    p.add_argument("--long-only", action="store_true")
    p.add_argument("--output", default="trades.csv")
    args = p.parse_args()
    try:
        trades, final = backtest_portfolio(load_bars(args.csv), initial_cash=args.cash,
            risk_fraction=args.risk, target_r=args.target_r, daily_loss_fraction=args.daily_loss,
            max_exposure_fraction=args.max_exposure, opening_time=time.fromisoformat(args.open),
            opening_range_minutes=args.range_minutes, fee_bps=args.fee_bps, slippage_bps=args.slippage_bps,
            min_atr_pct=args.min_atr_pct, max_atr_pct=args.max_atr_pct, allow_short=not args.long_only)
    except (OSError, ValueError) as exc:
        p.error(str(exc))
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(Trade.__dataclass_fields__))
        writer.writeheader(); writer.writerows(asdict(t) for t in trades)
    print(json.dumps(summarize(trades, final, args.cash), indent=2))
    print(f"Trade log: {args.output}")


if __name__ == "__main__":
    main()
