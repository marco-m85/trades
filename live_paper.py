from __future__ import annotations

import argparse
import json
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from urllib.request import Request, urlopen

from daytrade import Bar, backtest_portfolio


class JsonPollingFeed:
    """Adapter for a user-supplied HTTP endpoint returning {'bars': [OHLCV objects]}.

    Each bar must include symbol,timestamp,open,high,low,close and optional volume.
    The endpoint/provider is responsible for market-data rights and completed candles.
    """
    def __init__(self, url: str, interval: int = 15, token: str | None = None):
        self.url, self.interval, self.token = url, interval, token

    def poll(self) -> list[Bar]:
        headers = {"Accept": "application/json", "User-Agent": "intraday-paper-lab/1.0"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        req = Request(self.url, headers=headers)
        with urlopen(req, timeout=15) as response:
            payload = json.loads(response.read().decode("utf-8"))
        bars = []
        for row in payload.get("bars", []):
            bars.append(Bar(datetime.fromisoformat(row["timestamp"]), float(row["open"]),
                float(row["high"]), float(row["low"]), float(row["close"]),
                float(row.get("volume", 0)), str(row["symbol"]).upper()))
        return bars


@dataclass
class PaperFill:
    symbol: str
    entry_time: str
    exit_time: str
    side: str
    entry: float
    exit: float
    quantity: float
    pnl: float
    exit_reason: str


class SimulatedBroker:
    """Local ledger only; records hypothetical completed trades, never routes orders."""
    def __init__(self, starting_cash: float):
        self.starting_cash = starting_cash
        self.fills: dict[tuple[str, str], PaperFill] = {}

    @property
    def cash(self) -> float:
        return self.starting_cash + sum(fill.pnl for fill in self.fills.values())

    def record(self, fill: PaperFill) -> None:
        self.fills[(fill.symbol, fill.entry_time)] = fill


def main() -> None:
    parser = argparse.ArgumentParser(description="Poll an OHLCV endpoint and maintain a local paper-trading ledger")
    parser.add_argument("--url", required=True, help="HTTP endpoint returning JSON {'bars': [...]} ")
    parser.add_argument("--token-env", help="environment variable containing provider token")
    parser.add_argument("--cash", type=float, default=10_000)
    parser.add_argument("--interval", type=int, default=15, help="poll interval seconds")
    parser.add_argument("--open", default="09:30", help="exchange-local session opening time")
    parser.add_argument("--range-minutes", type=int, default=15)
    parser.add_argument("--once", action="store_true", help="poll and report once")
    args = parser.parse_args()
    import os
    if args.interval < 1 or args.cash <= 0:
        parser.error("interval and cash must be positive")
    feed = JsonPollingFeed(args.url, args.interval, os.getenv(args.token_env) if args.token_env else None)
    broker = SimulatedBroker(args.cash)
    seen: set[tuple[str, str]] = set()
    history: dict[str, dict[datetime, Bar]] = {}
    print("Paper mode: no real orders are sent. Ctrl+C to stop.", flush=True)
    while True:
        try:
            for bar in feed.poll():
                history.setdefault(bar.symbol, {})[bar.timestamp] = bar
            all_bars = [b for values in history.values() for b in values.values()]
            if all_bars:
                trades, _ = backtest_portfolio(all_bars, initial_cash=args.cash,
                    opening_time=datetime.strptime(args.open, "%H:%M").time(),
                    opening_range_minutes=args.range_minutes)
                for trade in trades:
                    key = (trade.symbol, trade.entry_time)
                    if key not in seen:
                        seen.add(key)
                        broker.record(PaperFill(trade.symbol, trade.entry_time, trade.exit_time,
                            trade.side, trade.entry, trade.exit, trade.quantity, trade.net_pnl, trade.exit_reason))
                        print(json.dumps(asdict(broker.fills[key])), flush=True)
                print(json.dumps({"paper_cash": broker.cash, "recorded_trades": len(broker.fills)}), flush=True)
            if args.once:
                break
            time.sleep(args.interval)
        except KeyboardInterrupt:
            break
        except Exception as exc:
            print(f"Feed/backtest error: {exc}", flush=True)
            if args.once:
                raise
            time.sleep(args.interval)
    print(json.dumps({"paper_cash": broker.cash, "fills": [asdict(x) for x in broker.fills.values()]}, indent=2))


if __name__ == "__main__":
    main()
