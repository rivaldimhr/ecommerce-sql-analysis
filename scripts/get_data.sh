#!/bin/sh
# Ambil dataset Olist (MIT License) dari repositori resmi olist/work-at-olist-data.
set -e
DEST="${1:-data/raw}"
if [ -f "$DEST/olist_orders_dataset.csv" ]; then echo "Data sudah ada di $DEST"; exit 0; fi
TMP=$(mktemp -d)
git clone -q --depth 1 https://github.com/olist/work-at-olist-data.git "$TMP/olist"
mkdir -p "$DEST"
cp "$TMP"/olist/datasets/*.csv "$DEST"/
rm -rf "$TMP"
echo "Data disalin ke $DEST"
