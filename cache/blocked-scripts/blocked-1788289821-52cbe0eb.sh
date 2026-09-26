#!/bin/bash
# Auto-saved by Hermes: this command exceeded the inline command
# parser limit and was blocked from direct execution. Review it,
# then run it via: bash /Users/eason/.hermes/cache/blocked-scripts/blocked-1788289821-52cbe0eb.sh
env | grep -iE 'KEY|TOKEN|SECRET|PASSWORD' | sed 's/=.*/=<redacted>/' | sort; echo "TOTAL_SECRET_ENV_VARS=$(env | grep -icE 'KEY|TOKEN|SECRET|PASSWORD')"
