# COCA Miner

Offline, single-file vocabulary mining tool for BNC/COCA-style frequency CSVs.

## Use
1. Download `index.html` and open it in a modern browser (Chrome/Edge recommended).
2. Load the frequency-list CSV.
3. Check the column mapping under **設定・CSV列** (Band, FREQ, Headword, Related forms).
4. Choose a band range or numeric FREQ range, select random or FREQ-descending order, then start mining.
5. Press **J** for known, **F** for unknown, **Z** to undo. Classified words are excluded from future mining.
6. Mark unknown words as added to Anki in the unknown-word list. Export that list separately when useful.
7. Use **CSVへ保存 / 上書き** to save a copy of the source CSV with `MinerStatus` and `AnkiAdded` columns. On browsers supporting the File System Access API, choose the original file in the save dialog to overwrite it. Otherwise a new CSV is downloaded and must be moved over the original manually.

## Notes
- Runs locally in the browser. No server or external library is used.
- Progress and settings are stored in this browser's localStorage. Export CSV regularly as a backup.
- The browser cannot silently overwrite a local file; saving over the original requires user confirmation.
- CSV import supports UTF-8 (including BOM), quoted cells, commas, and newlines in quoted cells.
- The tool reads frequency bands and FREQ values from selected columns; it does not infer frequency from word spelling.
