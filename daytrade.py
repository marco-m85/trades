#!/usr/bin/env python3
"""Educational, CSV-based intraday opening-range backtester (no broker connection)."""
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


@dataclass
class Trade:
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
    """Load timestamp,open,high,low,close[,volume] CSV bars; timestamps are local/naive."""
    bars: list[Bar] = []
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        required = {"timestamp", "open", "high", "low", "close"}
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise ValueError(f"CSV must contain columns: {', '.join(sorted(required))}")
        for line, row in enumerate(reader, start=2):
            try:
                ts = datetime.fromisoformat(row["timestamp"].strip())
                o, h, l, c = (float(row[k]) for k in ("open", "high", "low", "close"))
                v = float(row.get("volume") or 0)
            except (TypeError, ValueError) as exc:
                raise ValueError(f"Invalid value on CSV line {line}: {exc}") from exc
            if min(o, h, l, c) <= 0 or h < max(o, c, l) or l > min(o, c, h) or v < 0:
                raise ValueError(f"Invalid OHLCV values on CSV line {line}")
            bars.append(Bar(ts, o, h, l, c, v))
    bars.sort(key=lambda b: b.timestamp)
    if len({b.timestamp for b in bars}) != len(bars):
        raise ValueError("CSV contains duplicate timestamps")
    return bars


def _execution_price(price: float, side: str, action: str, slippage_bps: float) -> float:
    # Adverse slippage: buy fills higher, sell fills lower.
    is_buy = (side == "long" and action == "entry") or (side == "short" and action == "exit")
    factor = 1 + slippage_bps / 10_000 if is_buy else 1 - slippage_bps / 10_000
    return price * factor


def backtest(
    bars: Iterable[Bar], *, initial_cash: float = 10_000, risk_fraction: float = 0.005,
    target_r: float = 2.0, daily_loss_fraction: float = 0.02,
    max_exposure_fraction: float = 1.0, opening_time: time = time(9, 30),
    opening_range_minutes: int = 15, fee_bps: float = 1.0,
    slippage_bps: float = 1.0, allow_short: bool = True,
) -> tuple[list[Trade], float]:
    """Backtest a one-trade-per-day opening-range breakout with no overnight positions.

    A breakout is confirmed at bar close and filled at that close. Exit checks begin
    on the following bar. If stop and target both fall within one bar, stop is used
    (conservative assumption). Bars should use consistent, exchange-local timestamps.
    """
    if initial_cash <= 0 or not 0 < risk_fraction <= 1:
        raise ValueError("initial_cash must be positive and risk_fraction in (0, 1]")
    if not 0 < daily_loss_fraction <= 1 or not 0 < max_exposure_fraction <= 1:
        raise ValueError("daily_loss_fraction and max_exposure_fraction must be in (0, 1]")
    if target_r <= 0 or opening_range_minutes <= 0 or fee_bps < 0 or slippage_bps < 0:
        raise ValueError("target_r/range must be positive and fees/slippage non-negative")

    by_day: dict[object, list[Bar]] = {}
    for bar in sorted(bars, key=lambda x: x.timestamp):
        by_day.setdefault(bar.timestamp.date(), []).append(bar)

    equity = initial_cash
    trades: list[Trade] = []
    for day, day_bars in by_day.items():
        session_start = datetime.combine(day, opening_time)
        range_end = session_start + timedelta(minutes=opening_range_minutes)
        range_bars = [b for b in day_bars if session_start <= b.timestamp < range_end]
        if not range_bars:
            continue
        range_high = max(b.high for b in range_bars)
        range_low = min(b.low for b in range_bars)
        if range_high <= range_low:
            continue
        candidates = [b for b in day_bars if b.timestamp >= range_end]
        day_start_equity = equity
        position = None
        trade = None
        for idx, bar in enumerate(candidates):
            if position is None:
                if equity <= day_start_equity * (1 - daily_loss_fraction):
                    break
                long_signal = bar.close > range_high and bar.high > range_high
                short_signal = allow_short and bar.close < range_low and bar.low < range_low
                if not long_signal and not short_signal:
                    continue
                side = "long" if long_signal else "short"
                raw_entry = bar.close
                entry = _execution_price(raw_entry, side, "entry", slippage_bps)
                stop = range_low if side == "long" else range_high
                risk_per_unit = entry - stop if side == "long" else stop - entry
                if risk_per_unit <= 0:
                    continue
                qty_by_risk = equity * risk_fraction / risk_per_unit
                qty_by_exposure = equity * max_exposure_fraction / entry
                quantity = min(qty_by_risk, qty_by_exposure)
                if quantity <= 0:
                    continue
                risk_amount = risk_per_unit * quantity
                target = entry + target_r * risk_per_unit if side == "long" else entry - target_r * risk_per_unit
                position = {"side": side, "entry": entry, "stop": stop, "target": target,
                            "quantity": quantity, "entry_time": bar.timestamp}
                trade = None
                continue  # Do not use the signal bar's earlier high/low to trigger an exit.

            side = position["side"]
            if side == "long":
                hit_stop, hit_target = bar.low <= position["stop"], bar.high >= position["target"]
            else:
                hit_stop, hit_target = bar.high >= position["stop"], bar.low <= position["target"]
            if hit_stop or hit_target:
                reason = "stop" if hit_stop else "target"  # stop wins if both touched
                raw_exit = position["stop"] if hit_stop else position["target"]
            elif idx == len(candidates) - 1:
                reason, raw_exit = "session_close", bar.close
            else:
                continue
            exit_price = _execution_price(raw_exit, side, "exit", slippage_bps)
            sign = 1 if side == "long" else -1
            gross = (exit_price - position["entry"]) * position["quantity"] * sign
            fees = (position["entry"] + exit_price) * position["quantity"] * fee_bps / 10_000
            net = gross - fees
            equity += net
            trades.append(Trade(
                date=str(day), side=side,
                entry_time=position["entry_time"].isoformat(), exit_time=bar.timestamp.isoformat(),
                entry=position["entry"], exit=exit_price, stop=position["stop"],
                target=position["target"], quantity=position["quantity"], gross_pnl=gross,
                fees=fees, net_pnl=net, exit_reason=reason, equity_after=equity,
            ))
            position = None
            break  # Strictly one trade per session.
        # If data ends before any exit check (e.g. signal on last bar), do not invent a fill.
        # Ordinarily positions are closed on the last candidate bar above.
    return trades, equity


def summarize(trades: list[Trade], final_equity: float, initial_cash: float) -> dict:
    wins = [t for t in trades if t.net_pnl > 0]
    losses = [t for t in trades if t.net_pnl < 0]
    gross_profit = sum(t.net_pnl for t in wins)
    gross_loss = -sum(t.net_pnl for t in losses)
    return {
        "initial_cash": initial_cash, "final_equity": final_equity,
        "net_pnl": final_equity - initial_cash,
        "return_pct": (final_equity / initial_cash - 1) * 100,
        "trades": len(trades), "wins": len(wins), "losses": len(losses),
        "win_rate_pct": len(wins) / len(trades) * 100 if trades else 0.0,
        "profit_factor": gross_profit / gross_loss if gross_loss else None,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Paper/backtest-only intraday opening-range strategy")
    parser.add_argument("csv", help="OHLCV CSV with timestamp,open,high,low,close[,volume]")
    parser.add_argument("--cash", type=float, default=10_000)
    parser.add_argument("--risk", type=float, default=0.005, help="risk per trade as equity fraction (default 0.005 = 0.5%%)")
    parser.add_argument("--target-r", type=float, default=2.0)
    parser.add_argument("--daily-loss", type=float, default=0.02)
    parser.add_argument("--max-exposure", type=float, default=1.0)
    parser.add_argument("--open", default="09:30", help="exchange-local session open, HH:MM")
    parser.add_argument("--range-minutes", type=int, default=15)
    parser.add_argument("--fee-bps", type=float, default=1.0)
    parser.add_argument("--slippage-bps", type=float, default=1.0)
    parser.add_argument("--long-only", action="store_true")
    parser.add_argument("--output", default="trades.csv", help="output trade log CSV")
    args = parser.parse_args()
    try:
        opening_time = time.fromisoformat(args.open)
        trades, final_equity = backtest(
            load_bars(args.csv), initial_cash=args.cash, risk_fraction=args.risk,
            target_r=args.target_r, daily_loss_fraction=args.daily_loss,
            max_exposure_fraction=args.max_exposure, opening_time=opening_time,
            opening_range_minutes=args.range_minutes, fee_bps=args.fee_bps,
            slippage_bps=args.slippage_bps, allow_short=not args.long_only,
        )
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(asdict(trades[0]).keys()) if trades else list(Trade.__dataclass_fields__))
        writer.writeheader()
        writer.writerows(asdict(t) for t in trades)
    print(json.dumps(summarize(trades, final_equity, args.cash), indent=2))
    print(f"Trade log: {args.output}")


if __name__ == "__main__":
    main()
