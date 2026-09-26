#!/usr/bin/env python3
"""Fetch market data (OHLCV + fundamentals) for a given ticker and market.

Uses curl via subprocess since Python's DNS resolution may be restricted
in some environments, while curl works fine.
"""

import argparse
import csv
import io
import json
import os
import re
import subprocess
import sys
import time


def curl_fetch(url: str, headers: dict = None, max_time: int = 15) -> str:
    """Fetch URL content via curl."""
    cmd = ["curl", "-sL", "--max-time", str(max_time)]
    if headers:
        for k, v in headers.items():
            cmd.extend(["-H", f"{k}: {v}"])
    cmd.append(url)
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=max_time + 5)
    if result.returncode != 0:
        raise RuntimeError(f"curl failed: {result.stderr[:200]}")
    return result.stdout


def fetch_a_share_quote(ticker: str) -> dict:
    """Fetch current quote from Sina Finance API."""
    # Determine prefix: sh for 6xxxxx, sz for 0xxxxx/3xxxxx
    if ticker.startswith("6"):
        symbol = f"sh{ticker}"
    else:
        symbol = f"sz{ticker}"

    text = curl_fetch(
        f"https://hq.sinajs.cn/list={symbol}",
        headers={"Referer": "https://finance.sina.com.cn"},
    )

    # Parse: var hq_sh600519="name,open,prev_close,price,high,low,...";
    match = re.search(r'"([^"]+)"', text)
    if not match:
        raise RuntimeError(f"Failed to fetch quote for {ticker}: {text[:200]}")

    fields = match.group(1).split(",")
    if len(fields) < 32:
        raise RuntimeError(f"Incomplete quote data for {ticker}")

    return {
        "name": fields[0],
        "open": _f(fields[1]),
        "prev_close": _f(fields[2]),
        "price": _f(fields[3]),
        "high": _f(fields[4]),
        "low": _f(fields[5]),
        "volume": _f(fields[8]),      # shares
        "amount": _f(fields[9]),      # amount in yuan
        "date": fields[30],
        "time": fields[31],
    }


def fetch_a_share_history(ticker: str) -> list:
    """Fetch historical K-line data from Sina (last ~300 days)."""
    if ticker.startswith("6"):
        symbol = f"sh{ticker}"
    else:
        symbol = f"sz{ticker}"

    text = curl_fetch(
        f"https://money.finance.sina.com.cn/quotes_service/api/json_v2.s"
        f"/CN_MarketData.getKLineData?symbol={symbol}&scale=240&ma=no&datalen=300",
        headers={"Referer": "https://finance.sina.com.cn"},
    )

    if not text.strip().startswith("["):
        raise RuntimeError(f"Failed to fetch history for {ticker}: {text[:200]}")

    raw = json.loads(text)
    df_rows = []
    for row in raw:
        df_rows.append({
            "Date": row.get("day", ""),
            "Open": _f(row.get("open")),
            "High": _f(row.get("high")),
            "Low": _f(row.get("low")),
            "Close": _f(row.get("close")),
            "Volume": _f(row.get("volume")),
        })
    return df_rows


def fetch_a_share_fundamentals(ticker: str) -> dict:
    """Fetch A-share fundamental data from Sina."""
    if ticker.startswith("6"):
        symbol = f"sh{ticker}"
    else:
        symbol = f"sz{ticker}"

    info = {}

    # Try to get real-time fundamentals
    try:
        text = curl_fetch(
            f"https://hq.sinajs.cn/list={symbol}",
            headers={"Referer": "https://finance.sina.com.cn"},
        )
        match = re.search(r'"([^"]+)"', text)
        if match:
            fields = match.group(1).split(",")
            if len(fields) >= 33:
                info["pe_ttm"] = _f(fields[39]) if len(fields) > 39 else None
                info["pb"] = _f(fields[46]) if len(fields) > 46 else None
    except Exception:
        pass

    # Try to get sector info
    try:
        text = curl_fetch(
            f"https://money.finance.sina.com.cn/corp/go.php/vFD_Finance"
            f"/stockid/{ticker}/ctrl/part/displaytype/4.phtml",
            headers={"Referer": "https://finance.sina.com.cn"},
        )
        # Extract key financial metrics from HTML (simplified)
        # For now, just flag that we got something
        if "资产负债表" in text or "净利润" in text:
            info["has_financial_data"] = True
    except Exception:
        pass

    return info


def fetch_us_hk_quote(ticker: str) -> dict:
    """Fetch US/HK quote via WebSearch-compatible approach."""
    # yfinance uses Yahoo Finance which may have DNS issues
    # Try direct curl to Yahoo Finance
    try:
        text = curl_fetch(
            f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
            f"?range=1y&interval=1d",
            max_time=15,
        )
        data = json.loads(text)
        result = data["chart"]["result"][0]
        meta = result["meta"]
        timestamps = result["timestamp"]
        quote = result["indicators"]["quote"][0]

        rows = []
        for i, ts in enumerate(timestamps):
            rows.append({
                "Date": time.strftime("%Y-%m-%d", time.gmtime(ts)),
                "Open": _f(quote.get("open", [None] * len(timestamps))[i]),
                "High": _f(quote.get("high", [None] * len(timestamps))[i]),
                "Low": _f(quote.get("low", [None] * len(timestamps))[i]),
                "Close": _f(quote.get("close", [None] * len(timestamps))[i]),
                "Volume": _f(quote.get("volume", [None] * len(timestamps))[i]),
            })

        return rows, {
            "name": meta.get("shortName", ticker),
            "currency": meta.get("currency", ""),
            "market_cap": meta.get("marketCap"),
            "pe_ratio": meta.get("trailingPE"),
            "52w_high": meta.get("fiftyTwoWeekHigh"),
            "52w_low": meta.get("fiftyTwoWeekLow"),
        }
    except Exception as e:
        raise RuntimeError(f"Yahoo Finance fetch failed for {ticker}: {e}")


def _f(val):
    if val is None or val == "":
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def main():
    parser = argparse.ArgumentParser(description="Fetch market data for a stock")
    parser.add_argument("--ticker", required=True, help="Stock ticker symbol")
    parser.add_argument("--market", required=True, choices=["a-share", "us", "hk"], help="Market type")
    parser.add_argument("--output-dir", required=True, help="Output directory for data files")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    result = {
        "market": args.market,
        "ticker": args.ticker,
        "info": {},
        "last_price": None,
        "data_points": 0,
        "date_range": [],
    }

    try:
        if args.market == "a-share":
            # Fetch current quote
            quote = fetch_a_share_quote(args.ticker)
            result["info"] = {
                "name": quote["name"],
                "current_price": quote["price"],
                "open": quote["open"],
                "prev_close": quote["prev_close"],
                "high": quote["high"],
                "low": quote["low"],
                "volume": quote["volume"],
                "amount": quote["amount"],
                "quote_date": quote["date"],
                "quote_time": quote["time"],
            }
            result["last_price"] = quote["price"]

            # Fetch historical K-line
            history = fetch_a_share_history(args.ticker)

            # Fetch fundamentals
            fundamentals = fetch_a_share_fundamentals(args.ticker)
            result["info"].update(fundamentals)

            # Save as CSV for pickle compatibility
            if history:
                csv_path = os.path.join(args.output_dir, "ohlcv.csv")
                with open(csv_path, "w", newline="") as f:
                    writer = csv.DictWriter(f, fieldnames=["Date", "Open", "High", "Low", "Close", "Volume"])
                    writer.writeheader()
                    writer.writerows(history)

                # Also save as pickle for compute_indicators
                import pandas as pd
                df = pd.DataFrame(history)
                df["Date"] = pd.to_datetime(df["Date"])
                df = df.set_index("Date")
                df.to_pickle(os.path.join(args.output_dir, "ohlcv.pkl"))

                result["data_points"] = len(history)
                result["date_range"] = [history[0]["Date"], history[-1]["Date"]]

        else:
            # US/HK stocks via Yahoo Finance
            history, info = fetch_us_hk_quote(args.ticker)
            result["info"] = info
            result["last_price"] = info.get("pe_ratio")  # will be overwritten

            if history:
                import pandas as pd
                df = pd.DataFrame(history)
                df["Date"] = pd.to_datetime(df["Date"])
                df = df.set_index("Date")
                df.to_pickle(os.path.join(args.output_dir, "ohlcv.pkl"))

                csv_path = os.path.join(args.output_dir, "ohlcv.csv")
                df.reset_index().to_csv(csv_path, index=False)

                result["data_points"] = len(history)
                result["date_range"] = [history[0]["Date"], history[-1]["Date"]]
                result["last_price"] = history[-1]["Close"]

    except Exception as e:
        result["error"] = str(e)
        with open(os.path.join(args.output_dir, "market_data.json"), "w") as f:
            json.dump(result, f, ensure_ascii=False, indent=2, default=str)
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
        sys.exit(1)

    with open(os.path.join(args.output_dir, "market_data.json"), "w") as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=str)

    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
