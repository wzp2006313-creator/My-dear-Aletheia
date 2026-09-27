#!/usr/bin/env python3
"""Compute technical indicators from OHLCV data."""

import argparse
import json
import os
import sys

import numpy as np
import pandas as pd


def compute_ma(df: pd.DataFrame) -> pd.DataFrame:
    for period in [5, 10, 20, 60, 120, 250]:
        col = f"MA{period}"
        df[col] = df["Close"].rolling(window=period).mean()
    return df


def compute_macd(df: pd.DataFrame) -> pd.DataFrame:
    ema12 = df["Close"].ewm(span=12, adjust=False).mean()
    ema26 = df["Close"].ewm(span=26, adjust=False).mean()
    df["DIF"] = ema12 - ema26
    df["DEA"] = df["DIF"].ewm(span=9, adjust=False).mean()
    df["MACD_HIST"] = 2 * (df["DIF"] - df["DEA"])
    return df


def compute_rsi(df: pd.DataFrame, periods=(6, 12, 24)) -> pd.DataFrame:
    for period in periods:
        delta = df["Close"].diff()
        gain = delta.where(delta > 0, 0.0)
        loss = (-delta).where(delta < 0, 0.0)
        avg_gain = gain.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
        rs = avg_gain / avg_loss.replace(0, np.nan)
        df[f"RSI{period}"] = 100 - 100 / (1 + rs)
    return df


def compute_kdj(df: pd.DataFrame, n=9, m1=3, m2=3) -> pd.DataFrame:
    low_n = df["Low"].rolling(window=n).min()
    high_n = df["High"].rolling(window=n).max()
    rsv = (df["Close"] - low_n) / (high_n - low_n).replace(0, np.nan) * 100
    df["K"] = rsv.ewm(alpha=1 / m1, adjust=False).mean()
    df["D"] = df["K"].ewm(alpha=1 / m2, adjust=False).mean()
    df["J"] = 3 * df["K"] - 2 * df["D"]
    return df


def compute_bollinger(df: pd.DataFrame, period=20, std_dev=2) -> pd.DataFrame:
    df["BOLL_MID"] = df["Close"].rolling(window=period).mean()
    rolling_std = df["Close"].rolling(window=period).std()
    df["BOLL_UPPER"] = df["BOLL_MID"] + std_dev * rolling_std
    df["BOLL_LOWER"] = df["BOLL_MID"] - std_dev * rolling_std
    return df


def compute_atr(df: pd.DataFrame, period=14) -> pd.DataFrame:
    high = df["High"]
    low = df["Low"]
    prev_close = df["Close"].shift(1)
    tr = pd.concat([
        high - low,
        (high - prev_close).abs(),
        (low - prev_close).abs()
    ], axis=1).max(axis=1)
    df["ATR"] = tr.ewm(alpha=1 / period, adjust=False).mean()
    return df


def compute_volume_ma(df: pd.DataFrame) -> pd.DataFrame:
    vol_col = "Volume" if "Volume" in df.columns else "成交量"
    for period in [5, 10]:
        df[f"VolMA{period}"] = df[vol_col].rolling(window=period).mean()
    return df


def main():
    parser = argparse.ArgumentParser(description="Compute technical indicators")
    parser.add_argument("--data-dir", required=True, help="Directory containing ohlcv.pkl")
    args = parser.parse_args()

    pkl_path = os.path.join(args.data_dir, "ohlcv.pkl")
    csv_path = os.path.join(args.data_dir, "ohlcv.csv")

    if os.path.exists(pkl_path):
        df = pd.read_pickle(pkl_path)
    elif os.path.exists(csv_path):
        df = pd.read_csv(csv_path, parse_dates=["Date"])
        df = df.set_index("Date")
        # Save as pickle for chart generation
        df.to_pickle(pkl_path)
    else:
        print(f"Error: No ohlcv.pkl or ohlcv.csv found in {args.data_dir}", file=sys.stderr)
        sys.exit(1)

    # Normalize column names and handle Date as index or column
    col_map = {}
    has_date_col = False
    for c in df.columns:
        cl = c.lower()
        if cl in ("close", "收盘"):
            col_map[c] = "Close"
        elif cl in ("open", "开盘"):
            col_map[c] = "Open"
        elif cl in ("high", "最高"):
            col_map[c] = "High"
        elif cl in ("low", "最低"):
            col_map[c] = "Low"
        elif cl in ("volume", "成交量"):
            col_map[c] = "Volume"
        elif cl in ("date", "日期"):
            col_map[c] = "Date"
            has_date_col = True
    df = df.rename(columns=col_map)

    # If Date is in columns, set it as index and keep as column
    if has_date_col:
        if "Date" in df.columns:
            df.index = pd.to_datetime(df["Date"])
    elif df.index.name and df.index.name.lower() in ("date", "日期"):
        df.index.name = "Date"
    elif not df.index.name:
        df.index.name = "Date"

    # Compute all indicators
    df = compute_ma(df)
    df = compute_macd(df)
    df = compute_rsi(df)
    df = compute_kdj(df)
    df = compute_bollinger(df)
    df = compute_atr(df)
    df = compute_volume_ma(df)

    # Save as JSON (last 60 rows for readability) + full pickle
    df.to_pickle(os.path.join(args.data_dir, "indicators.pkl"))

    # Extract latest values for report consumption
    latest = df.iloc[-1]
    summary = {
        "last_close": _f(latest.get("Close")),
        "ma": {p: _f(latest.get(f"MA{p}")) for p in [5, 10, 20, 60, 120, 250]},
        "macd": {
            "dif": _f(latest.get("DIF")),
            "dea": _f(latest.get("DEA")),
            "histogram": _f(latest.get("MACD_HIST")),
        },
        "rsi": {p: _f(latest.get(f"RSI{p}")) for p in [6, 12, 24]},
        "kdj": {"k": _f(latest.get("K")), "d": _f(latest.get("D")), "j": _f(latest.get("J"))},
        "bollinger": {
            "upper": _f(latest.get("BOLL_UPPER")),
            "mid": _f(latest.get("BOLL_MID")),
            "lower": _f(latest.get("BOLL_LOWER")),
        },
        "atr": _f(latest.get("ATR")),
        "volume_ma": {p: _f(latest.get(f"VolMA{p}")) for p in [5, 10]},
        "latest_volume": _f(latest.get("Volume")),
        "date_range": [str(df.index[0].date()), str(df.index[-1].date())],
    }

    # Recent 5-day trend for divergence detection
    recent = df.tail(5)[["Close", "Volume", "DIF", "DEA", "RSI6", "RSI12", "K", "D", "J"]].copy()
    recent["Date"] = [str(d.date()) for d in recent.index]
    summary["recent_5d"] = recent.to_dict(orient="records")

    # Recent 20-day for pattern analysis
    recent20 = df.tail(20)[["Open", "High", "Low", "Close", "Volume"]].copy()
    recent20["Date"] = [str(d.date()) for d in recent20.index]
    summary["recent_20d_ohlcv"] = recent20.to_dict(orient="records")

    with open(os.path.join(args.data_dir, "indicators.json"), "w") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2, default=str)

    print(json.dumps(summary, ensure_ascii=False, indent=2, default=str))


def _f(val):
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return None
    return round(float(val), 4)


if __name__ == "__main__":
    main()
