#!/usr/bin/env sh
# Start COCA Miner and keep the server running in this terminal.
# server.py reads port and browser-launch settings from config.json.
set -eu
cd "$(dirname "$0")"
exec python3 server.py
