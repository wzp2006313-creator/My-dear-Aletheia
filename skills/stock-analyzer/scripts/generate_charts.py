#!/usr/bin/env python3
"""Generate technical analysis charts from OHLCV + indicator data."""

import argparse
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd


def set_chinese_font():
    """Try to set a Chinese-compatible font for chart labels."""
    for font_name in ["WenQuanYi Micro Hei", "Noto Sans CJK SC", "SimHei", "DejaVu Sans", "Arial"]:
        try:
            plt.rcParams["font.sans-serif"] = [font_name]
            plt.rcParams["axes.unicode_minus"] = False
            return font_name
        except Exception:
            continue
    plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial"]
    plt.rcParams["axes.unicode_minus"] = False


def generate_price_macd(df: pd.DataFrame, charts_dir: str):
    """Price chart with MA lines using matplotlib."""
    last_90 = df.tail(90)
    fig, ax = plt.subplots(figsize=(14, 6))
    ax.plot(last_90.index, last_90["Close"], label="Close", color="black", linewidth=1.5, zorder=5)
    for p, color in [(5, "blue"), (10, "orange"), (20, "green"), (60, "purple")]:
        col = f"MA{p}"
        if col in last_90.columns:
            ax.plot(last_90.index, last_90[col], label=f"MA{p}", color=color, linewidth=0.8, alpha=0.7)
    ax.legend(fontsize=8, loc="upper left")
    ax.set_title("Price & Moving Averages", fontsize=11)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d"))
    fig.autofmt_xdate()
    fig.savefig(os.path.join(charts_dir, "price_macd.png"), dpi=120, bbox_inches="tight")
    plt.close(fig)


def generate_macd_chart(df: pd.DataFrame, charts_dir: str):
    """MACD DIF/DEA/Histogram chart."""
    last_90 = df.tail(90)
    fig, ax = plt.subplots(figsize=(14, 4))
    dates = last_90.index
    ax.plot(dates, last_90["DIF"], label="DIF", color="blue", linewidth=1.2)
    ax.plot(dates, last_90["DEA"], label="DEA", color="orange", linewidth=1.2)
    colors = ["red" if v > 0 else "green" for v in last_90["MACD_HIST"]]
    ax.bar(dates, last_90["MACD_HIST"], color=colors, alpha=0.5, label="Histogram")
    ax.axhline(y=0, color="gray", linewidth=0.5, linestyle="--")
    ax.legend(fontsize=8)
    ax.set_title("MACD", fontsize=10)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d"))
    fig.autofmt_xdate()
    fig.savefig(os.path.join(charts_dir, "macd.png"), dpi=120, bbox_inches="tight")
    plt.close(fig)


def generate_rsi_chart(df: pd.DataFrame, charts_dir: str):
    """RSI chart with overbought/oversold zones."""
    last_90 = df.tail(90)
    fig, ax = plt.subplots(figsize=(14, 4))
    dates = last_90.index
    ax.axhspan(70, 100, alpha=0.1, color="red")
    ax.axhspan(0, 30, alpha=0.1, color="green")
    ax.axhline(y=70, color="red", linewidth=0.8, linestyle="--")
    ax.axhline(y=30, color="green", linewidth=0.8, linestyle="--")
    ax.axhline(y=50, color="gray", linewidth=0.5, linestyle="--")
    for period, color in [(6, "blue"), (12, "orange"), (24, "purple")]:
        col = f"RSI{period}"
        if col in last_90.columns:
            ax.plot(dates, last_90[col], label=f"RSI{period}", color=color, linewidth=1.2)
    ax.legend(fontsize=8)
    ax.set_title("RSI", fontsize=10)
    ax.set_ylim(0, 100)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d"))
    fig.autofmt_xdate()
    fig.savefig(os.path.join(charts_dir, "rsi.png"), dpi=120, bbox_inches="tight")
    plt.close(fig)


def generate_kdj_chart(df: pd.DataFrame, charts_dir: str):
    """KDJ chart."""
    last_90 = df.tail(90)
    fig, ax = plt.subplots(figsize=(14, 4))
    dates = last_90.index
    for col, color in [("K", "blue"), ("D", "orange"), ("J", "red")]:
        if col in last_90.columns:
            ax.plot(dates, last_90[col], label=col, color=color, linewidth=1.2)
    ax.axhline(y=80, color="red", linewidth=0.8, linestyle="--", alpha=0.5)
    ax.axhline(y=20, color="green", linewidth=0.8, linestyle="--", alpha=0.5)
    ax.legend(fontsize=8)
    ax.set_title("KDJ", fontsize=10)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d"))
    fig.autofmt_xdate()
    fig.savefig(os.path.join(charts_dir, "kdj.png"), dpi=120, bbox_inches="tight")
    plt.close(fig)


def generate_volume_chart(df: pd.DataFrame, charts_dir: str):
    """Volume chart with volume MA."""
    last_90 = df.tail(90)
    vol_col = "Volume" if "Volume" in last_90.columns else "成交量"
    fig, ax = plt.subplots(figsize=(14, 4))
    dates = last_90.index
    close = last_90.get("Close", last_90.iloc[:, 3])
    colors = ["red" if c >= o else "green" for c, o in zip(last_90.get("Close", []), last_90.get("Open", []))]
    ax.bar(dates, last_90[vol_col], color=colors, alpha=0.7)
    for p, color in [(5, "blue"), (10, "orange")]:
        col = f"VolMA{p}"
        if col in last_90.columns:
            ax.plot(dates, last_90[col], label=f"VolMA{p}", color=color, linewidth=1.5)
    ax.legend(fontsize=8)
    ax.set_title("Volume", fontsize=10)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d"))
    fig.autofmt_xdate()
    fig.savefig(os.path.join(charts_dir, "volume.png"), dpi=120, bbox_inches="tight")
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description="Generate technical analysis charts")
    parser.add_argument("--data-dir", required=True, help="Directory containing ohlcv.pkl")
    parser.add_argument("--charts-dir", required=True, help="Output directory for chart images")
    args = parser.parse_args()

    os.makedirs(args.charts_dir, exist_ok=True)
    set_chinese_font()

    # Use ohlcv.pkl for price chart (has Volume), indicators.pkl for indicator charts
    ohlcv_path = os.path.join(args.data_dir, "ohlcv.pkl")
    ind_path = os.path.join(args.data_dir, "indicators.pkl")

    if not os.path.exists(ohlcv_path) and not os.path.exists(ind_path):
        print(f"Error: No pkl data found in {args.data_dir}", file=sys.stderr)
        sys.exit(1)

    ohlcv_df = None
    ind_df = None

    if os.path.exists(ohlcv_path):
        ohlcv_df = pd.read_pickle(ohlcv_path)
    if os.path.exists(ind_path):
        ind_df = pd.read_pickle(ind_path)

    df = ind_df if ind_df is not None else ohlcv_df

    # Normalize columns
    col_map = {}
    for c in df.columns:
        cl = c.lower()
        if cl in ("close", "收盘"): col_map[c] = "Close"
        elif cl in ("open", "开盘"): col_map[c] = "Open"
        elif cl in ("high", "最高"): col_map[c] = "High"
        elif cl in ("low", "最低"): col_map[c] = "Low"
        elif cl in ("volume", "成交量"): col_map[c] = "Volume"
        elif cl in ("date", "日期"): col_map[c] = "Date"
    df = df.rename(columns=col_map)
    if "Date" in df.columns:
        df.index = pd.to_datetime(df["Date"])

    try:
        price_df = ohlcv_df if ohlcv_df is not None else df
        generate_price_macd(price_df, args.charts_dir)
    except Exception as e:
        print(f"Price chart failed: {e}", file=sys.stderr)

    try:
        ind_for_chart = ind_df if ind_df is not None else df
        generate_macd_chart(ind_for_chart, args.charts_dir)
    except Exception as e:
        print(f"MACD chart failed: {e}", file=sys.stderr)

    try:
        ind_for_chart = ind_df if ind_df is not None else df
        generate_rsi_chart(ind_for_chart, args.charts_dir)
    except Exception as e:
        print(f"RSI chart failed: {e}", file=sys.stderr)

    try:
        ind_for_chart = ind_df if ind_df is not None else df
        generate_kdj_chart(ind_for_chart, args.charts_dir)
    except Exception as e:
        print(f"KDJ chart failed: {e}", file=sys.stderr)

    try:
        vol_df = ohlcv_df if ohlcv_df is not None else df
        generate_volume_chart(vol_df, args.charts_dir)
    except Exception as e:
        print(f"Volume chart failed: {e}", file=sys.stderr)

    print(f"Charts saved to {args.charts_dir}")


if __name__ == "__main__":
    main()
