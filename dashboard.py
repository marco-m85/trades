from __future__ import annotations

import io
from datetime import time

import pandas as pd
import plotly.express as px
import streamlit as st

from daytrade import Bar, Trade, backtest_portfolio, load_bars, summarize

st.set_page_config(page_title="Intraday Paper Lab", layout="wide")
st.title("Intraday Paper Lab")
st.caption("Ricerca e simulazione storica multi-asset — nessun ordine reale viene inviato.")

uploaded = st.file_uploader("Carica CSV OHLCV", type=["csv"])
if not uploaded:
    st.info("Formato richiesto: timestamp,open,high,low,close[,volume,symbol]. Senza symbol viene usato DEFAULT.")
    st.stop()
try:
    bars = load_bars(io.BytesIO(uploaded.getvalue()))
except (ValueError, OSError) as exc:
    st.error(str(exc)); st.stop()

with st.sidebar:
    st.header("Strategia e rischio")
    cash = st.number_input("Capitale totale", min_value=100.0, value=10_000.0)
    risk = st.slider("Rischio per trade / sotto-conto", .001, .02, .005, .001)
    target = st.slider("Target (R)", .5, 5.0, 2.0, .25)
    daily_loss = st.slider("Stop giornaliero", .005, .05, .02, .005)
    exposure = st.slider("Esposizione max per asset", .1, 1.0, 1.0, .1)
    open_str = st.text_input("Apertura sessione (ora exchange)", "09:30")
    range_mins = st.number_input("Opening range (minuti)", 5, 120, 15, 5)
    min_atr = st.number_input("ATR% minimo", min_value=0.0, value=.001, format="%.4f")
    max_atr = st.number_input("ATR% massimo", min_value=.001, value=.03, format="%.4f")
    fee = st.number_input("Commissioni (bps per lato)", min_value=0.0, value=1.0)
    slip = st.number_input("Slippage (bps)", min_value=0.0, value=1.0)

try:
    trades, final = backtest_portfolio(bars, initial_cash=cash, risk_fraction=risk,
        target_r=target, daily_loss_fraction=daily_loss, max_exposure_fraction=exposure,
        opening_time=time.fromisoformat(open_str), opening_range_minutes=int(range_mins),
        min_atr_pct=min_atr, max_atr_pct=max_atr, fee_bps=fee, slippage_bps=slip)
except ValueError as exc:
    st.error(str(exc)); st.stop()

metrics = summarize(trades, final, cash)
cols = st.columns(5)
for col, label, value in zip(cols, ["Equity finale", "PnL netto", "Return %", "Trade", "Win rate"],
    [f"{final:,.2f}", f"{metrics['net_pnl']:,.2f}", f"{metrics['return_pct']:.2f}%", str(len(trades)), f"{metrics['win_rate_pct']:.1f}%"]):
    col.metric(label, value)
if trades:
    df = pd.DataFrame([t.__dict__ for t in trades])
    df["exit_time"] = pd.to_datetime(df["exit_time"])
    df["entry_time"] = pd.to_datetime(df["entry_time"])
    st.subheader("Performance")
    daily = df.groupby("date", as_index=False)["net_pnl"].sum()
    daily["equity"] = cash + daily["net_pnl"].cumsum()
    st.plotly_chart(px.line(daily, x="date", y="equity", title="Equity curve (PnL cumulato)"), use_container_width=True)
    left, right = st.columns(2)
    left.plotly_chart(px.bar(df.groupby("symbol", as_index=False)["net_pnl"].sum(), x="symbol", y="net_pnl", title="PnL per asset"), use_container_width=True)
    right.plotly_chart(px.histogram(df, x="net_pnl", color="side", title="Distribuzione PnL trade"), use_container_width=True)
    st.dataframe(df.sort_values("entry_time", ascending=False), use_container_width=True)
    st.download_button("Scarica trade log CSV", df.to_csv(index=False), "trades.csv", "text/csv")
else:
    st.warning("Nessun trade con questi dati e filtri. Verifica sessione, timeframe e soglie volatilità.")
st.caption("Il portafoglio divide il capitale in sotto-conti uguali per asset. Backtest indicativo: slippage, spread, liquidità, survivorship bias e dati errati possono alterare i risultati. Non è consulenza finanziaria.")
