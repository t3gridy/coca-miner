# COCA Miner

A local-first vocabulary mining GUI for BNC/COCA-style frequency lists.

## Features

- Mine words from a static CSV by frequency band or numeric FREQ range.
- Mark words as known or unknown; judged words are excluded from later sessions.
- Review, search, filter, sort, and bulk-update the unknown-word list.
- View known-rate estimates, confidence intervals, band coverage, receptive vocabulary estimates, and FREQ summaries.
- Automatically save decisions and settings to a local `progress.json`.
- Import/export progress as JSON and export word lists as CSV.

## Files

- `index.html` — GUI and mining logic.
- `words.csv` — static source data (25,002 rows). The app treats it as read-only.
- `server.py` — dependency-free local server and progress API.
- `config.json` — local server settings.
- `progress.json` — created locally; contains decisions, discovery timestamps, column mappings, and settings. It is ignored by Git.

## Recommended: GUI + local server

Python 3.10+ is recommended; no third-party packages are required.

1. Download or clone this repository.
2. On Windows, double-click `start.bat`. On macOS/Linux, run `sh start.sh` or `python3 server.py` in a terminal.
3. The browser opens at `http://127.0.0.1:8766/`. If it does not, open that address manually.
4. Load `words.csv` and mine words. The server creates `progress.json` next to `server.py` when needed and saves decisions and settings automatically.
5. Stop the server with `Ctrl+C`. The next launch restores your progress.

The server binds to `127.0.0.1` by default and is intended for use on the same computer. The default port is `8766` to avoid conflicting with AnkiConnect, which commonly uses `8765`. Change `port` in `config.json` if needed. Set `open_browser` to `false` to disable automatic browser launch.

Writes use an atomic file replacement to reduce the chance of a partially written progress file. Keep `progress.json` if you want to preserve your progress.

## Configuration

`config.json`:

```json
{
  "host": "127.0.0.1",
  "port": 8766,
  "open_browser": true,
  "progress_file": "progress.json"
}
```

- `host`: bind address. The current server version accepts loopback addresses only (`127.0.0.1` or `localhost`).
- `port`: HTTP port (1–65535).
- `open_browser`: automatically open the GUI when the server starts.
- `progress_file`: progress filename in the app directory.

For temporary port overrides, set the `COCA_MINER_PORT` environment variable.

## Browser-only alternative

You can open the GUI from a trusted HTTPS origin, such as a configured GitHub Pages site. Use **progress.json を作成 / 接続** and **progress.json を開く** where the File System Access API is supported. Otherwise, use the JSON import/export controls.

## Controls

- **F** — mark as known.
- **J** — mark as unknown.
- **Z** — undo the last decision.

Known and unknown words already judged are excluded from subsequent mining candidates. In the unknown-word list, the selected Band filter and sort order are saved in `progress.json`.

## Data format

`words.csv` is expected to contain columns for `Band`, `Headword`, `Related forms`, and `FREQ`. Column names can be mapped in the settings tab. The app treats the CSV as read-only.

`progress.json` stores:

- `decisions`: known/unknown judgments.
- `unknownAt`: timestamps for words marked unknown.
- `cols`: selected CSV column mappings.
- `settings`: mining options, statistics ranges, and unknown-list filters/sort order.

The app ignores legacy `ankiAdded` data when loading older progress files and no longer writes that property. Older `cocaMiner.v1` browser-local data can be migrated once into the current progress format.

CSV import supports UTF-8/BOM, quoted cells, commas, and newline characters inside quoted fields.
