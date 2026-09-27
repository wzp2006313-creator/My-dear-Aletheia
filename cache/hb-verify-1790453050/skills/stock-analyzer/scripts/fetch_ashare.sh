#!/bin/bash
# Fetch A-share stock data via Sina Finance APIs and save as CSV + JSON
# Usage: fetch_ashare.sh <ticker> <output_dir>

set -e

TICKER="$1"
OUTPUT_DIR="$2"

if [ -z "$TICKER" ] || [ -z "$OUTPUT_DIR" ]; then
    echo "Usage: fetch_ashare.sh <ticker> <output_dir>" >&2
    exit 1
fi

mkdir -p "$OUTPUT_DIR"

# Determine Sina symbol prefix
if [[ "$TICKER" == 6* ]]; then
    SYMBOL="sh${TICKER}"
else
    SYMBOL="sz${TICKER}"
fi

echo "Fetching current quote for ${TICKER}..."
QUOTE_RAW=$(curl -sL --max-time 10 "https://hq.sinajs.cn/list=${SYMBOL}" \
    -H "Referer: https://finance.sina.com.cn")

if [ -z "$QUOTE_RAW" ]; then
    echo "ERROR: Empty response from Sina quote API" >&2
    exit 1
fi

echo "$QUOTE_RAW" > "$OUTPUT_DIR/quote_raw.txt"

# Parse quote using Python helper
QUOTE_JSON=$(echo "$QUOTE_RAW" | python3 ~/.claude/skills/stock-analyzer/scripts/sina_data_helper.py parse-quote)
echo "$QUOTE_JSON" > "$OUTPUT_DIR/quote.json"

echo "Fetching historical K-line data for ${TICKER}..."
HISTORY_RAW=$(curl -sL --max-time 15 \
    "https://money.finance.sina.com.cn/quotes_service/api/json_v2.s/CN_MarketData.getKLineData?symbol=${TICKER}&scale=240&ma=no&datalen=300" \
    -H "Referer: https://finance.sina.com.cn")

if [ -z "$HISTORY_RAW" ]; then
    echo "ERROR: Empty response from Sina history API" >&2
    exit 1
fi

# Parse history and save as CSV
echo "$HISTORY_RAW" | python3 ~/.claude/skills/stock-analyzer/scripts/sina_data_helper.py parse-history > "$OUTPUT_DIR/history.json"

# Convert history to CSV and pickle for compute_indicators
python3 -c "
import json, csv, os, pandas as pd

with open('$OUTPUT_DIR/history.json') as f:
    data = json.load(f)

# Save CSV
with open('$OUTPUT_DIR/ohlcv.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['Date','Open','High','Low','Close','Volume'])
    writer.writeheader()
    writer.writerows(data)

# Save pickle for compute_indicators
df = pd.DataFrame(data)
df['Date'] = pd.to_datetime(df['Date'])
df = df.set_index('Date')
df.to_pickle('$OUTPUT_DIR/ohlcv.pkl')

print(f'Saved {len(data)} rows of OHLCV data')
"

# Build market_data.json summary
python3 -c "
import json

with open('$OUTPUT_DIR/quote.json') as f:
    quote = json.load(f)

with open('$OUTPUT_DIR/history.json') as f:
    history = json.load(f)

result = {
    'market': 'a-share',
    'ticker': '$TICKER',
    'info': {
        'name': quote['name'],
        'current_price': quote['price'],
        'open': quote['open'],
        'prev_close': quote['prev_close'],
        'high': quote['high'],
        'low': quote['low'],
        'volume': quote['volume'],
        'amount': quote['amount'],
        'quote_date': quote['date'],
        'quote_time': quote['time'],
    },
    'last_price': quote['price'],
    'data_points': len(history),
    'date_range': [history[0]['Date'], history[-1]['Date']] if history else [],
}

with open('$OUTPUT_DIR/market_data.json', 'w') as f:
    json.dump(result, f, ensure_ascii=False, indent=2, default=str)

print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
"

echo "Data saved to $OUTPUT_DIR"
