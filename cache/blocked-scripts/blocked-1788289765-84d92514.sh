#!/bin/bash
# Auto-saved by Hermes: this command exceeded the inline command
# parser limit and was blocked from direct execution. Review it,
# then run it via: bash /Users/eason/.hermes/cache/blocked-scripts/blocked-1788289765-84d92514.sh
echo "=== 指标10 环境变量审计 ==="; env | grep -iE 'KEY|TOKEN|SECRET|PASSWORD|API_KEY' | sed 's/=.*/=***/' | sort | head -30; echo "(count: $(env | grep -icE 'KEY|TOKEN|SECRET|PASSWORD|API_KEY'))"
