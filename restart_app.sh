#!/bin/bash

# Script to properly restart Streamlit with cache clearing

echo "Stopping Streamlit..."
pkill -f "streamlit run"

echo "Clearing Python cache..."
python3 clear_cache.py

echo "Clearing Streamlit cache..."
rm -rf ~/.streamlit/cache

echo "Starting Streamlit..."
streamlit run app.py --server.runOnSave true

echo "Application restarted!"
