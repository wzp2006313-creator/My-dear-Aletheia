#!/usr/bin/env python3
"""
Generate curl commands for fetching stock data.
This script outputs shell commands that should be executed (not via Python subprocess).
The skill should use these commands to fetch data, then call this script to parse results.
"""

import json
import sys


def get_a_share_quote_cmd(ticker: str) -> str:
    """Return curl command for A-share current quote."""
    if ticker.startswith("6"):
        symbol = f"sh{ticker}"
    else:
        symbol = f"sz{ticker}"
    return f'curl -sL --max-time 10 "https://hq.sinajs.cn/list={symbol}" -H "Referer: https://finance.sina.com.cn"'


def get_a_share_history_cmd(ticker: str) -> str:
    """Return curl command for A-share historical K-line data."""
    return f'curl -sL --max-time 15 "https://money.finance.sina.com.cn/quotes_service/api/json_v2.s/CN_MarketData.getKLineData?symbol={ticker}&scale=240&ma=no&datalen=300" -H "Referer: https://finance.sina.com.cn"'


def parse_a_share_quote(text: str) -> dict:
    """Parse Sina quote response."""
    import re
    match = re.search(r'"([^"]+)"', text)
    if not match:
        raise RuntimeError(f"Failed to parse quote: {text[:200]}")

    fields = match.group(1).split(",")
    if len(fields) < 32:
        raise RuntimeError(f"Incomplete quote data")

    return {
        "name": fields[0],
        "open": _f(fields[1]),
        "prev_close": _f(fields[2]),
        "price": _f(fields[3]),
        "high": _f(fields[4]),
        "low": _f(fields[5]),
        "volume": _f(fields[8]),
        "amount": _f(fields[9]),
        "date": fields[30],
        "time": fields[31],
    }


def parse_a_share_history(text: str) -> list:
    """Parse Sina K-line JSON response."""
    import json as _json
    raw = _json.loads(text)
    rows = []
    for row in raw:
        rows.append({
            "Date": row.get("day", ""),
            "Open": _f(row.get("open")),
            "High": _f(row.get("high")),
            "Low": _f(row.get("low")),
            "Close": _f(row.get("close")),
            "Volume": _f(row.get("volume")),
        })
    return rows


def _f(val):
    if val is None or val == "":
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: sina_data_helper.py <quote|history> <ticker>")
        sys.exit(1)

    action = sys.argv[1]
    ticker = sys.argv[2] if len(sys.argv) > 2 else "600519"

    if action == "quote-cmd":
        print(get_a_share_quote_cmd(ticker))
    elif action == "history-cmd":
        print(get_a_share_history_cmd(ticker))
    elif action == "parse-quote":
        # Sina data is GBK-encoded
        import io
        raw_bytes = sys.stdin.buffer.read()
        try:
            text = raw_bytes.decode('gbk')
        except UnicodeDecodeError:
            text = raw_bytes.decode('utf-8', errors='replace')
        result = parse_a_share_quote(text)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif action == "parse-history":
        text = sys.stdin.read()
        rows = parse_a_share_history(text)
        print(json.dumps(rows, ensure_ascii=False, indent=2))
    else:
        print(f"Unknown action: {action}")
        sys.exit(1)
