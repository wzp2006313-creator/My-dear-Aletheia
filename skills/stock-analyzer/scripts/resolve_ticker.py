#!/usr/bin/env python3
"""Resolve a user-provided stock identifier into a normalized ticker and market type."""

import json
import re
import sys


def resolve_ticker(raw_input: str) -> dict:
    raw = raw_input.strip()

    # Pattern: 6-digit Chinese stock code (A-shares)
    if re.match(r'^[036]\d{5}$', raw):
        return {"ticker": raw, "market": "a-share", "name": raw}

    # Pattern: HK stock — 4-5 digits with or without .HK suffix
    if re.match(r'^\d{4,5}\.HK$', raw, re.IGNORECASE):
        return {"ticker": raw.upper(), "market": "hk", "name": raw[:5]}
    if re.match(r'^0\d{3,4}$', raw):
        # e.g. 00700 → 0700.HK
        return {"ticker": raw.lstrip('0').zfill(4) + ".HK", "market": "hk", "name": raw}

    # Pattern: US stock — alphabetic ticker (1-5 chars), possibly with dots
    if re.match(r'^[A-Z]{1,5}$', raw.upper()):
        return {"ticker": raw.upper(), "market": "us", "name": raw.upper()}

    # Fallback: treat as-is, let caller search
    return {"ticker": raw, "market": "unknown", "name": raw}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: resolve_ticker.py <ticker_or_name>", file=sys.stderr)
        sys.exit(1)

    raw_input = sys.argv[1]
    result = resolve_ticker(raw_input)
    print(json.dumps(result, ensure_ascii=False))
