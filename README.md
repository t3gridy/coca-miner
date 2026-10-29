# COCA Miner

A local-first vocabulary mining GUI for BNC/COCA-style frequency lists.

## Files

- `index.html` — the GUI and mining logic.
- `words.csv` — static source data (25,002 rows). The app does not modify this file.
- `progress.json` — your decisions, Anki-added flags, column mapping, and settings. This file is created by you and is not committed to the repository.

## Start

1. Open the app from a trusted HTTPS origin (for example, a configured GitHub Pages site) to let it fetch `words.csv` automatically. When opening a downloaded `index.html` directly from disk, use **別のCSV** to select `words.csv`; browsers generally block fetching sibling files from a `file://` page.
2. Press **progress.json を作成 / 接続** and create or select your `progress.json`. In Chrome or Edge on a supported secure origin, decisions and settings are automatically written to this file.
3. On a later visit, press **progress.json を開く** and select the same file to restore your progress and reconnect auto-save. File handles are not assumed to persist across browser sessions.
4. Choose a Band range or numeric FREQ range and start mining. Press **J** for known, **F** for unknown, and **Z** to undo.
5. In the unknown-word list, mark terms as added to Anki. Export the unknown-word list or a progress CSV as needed.

## Data format

`words.csv` has four columns: `Band`, `Headword`, `Related forms`, and `FREQ`. It is treated as read-only by the app.

`progress.json` contains the known/unknown decisions, Anki flags, settings, and selected column mapping. No progress is written to the GitHub repository. The app does not continuously use localStorage; if an older version's `cocaMiner.v1` data is still present in the same browser, it makes a one-time in-memory migration so you can save that state to `progress.json`.

## Browser compatibility and fallback

The File System Access API is supported in current Chromium-based browsers such as Chrome and Edge when the page is served from a secure context. Where it is unavailable, import/export `progress.json` manually using the JSON controls. Nothing is silently uploaded to GitHub or sent to a server.

CSV import supports UTF-8/BOM, quoted cells, commas, and newline characters inside quoted fields.