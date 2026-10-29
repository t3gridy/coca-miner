# COCA Miner

A local-first vocabulary mining GUI for BNC/COCA-style frequency lists.

## Files

- \`index.html\` — the GUI and mining logic.
- \`words.csv\` — static source data (25,002 rows). The app never modifies this file.
- \`server.py\` — dependency-free local server and progress API.
- \`config.json\` — local server settings, including port and automatic browser launch.
- \`progress.json\` — decisions, Anki-added flags, column mapping, and settings. Created locally and ignored by Git.

## Recommended: GUI + local server

Python 3.10+ is recommended; no third-party packages are required.

1. Download or clone this repository.
2. On Windows, double-click \`start.bat\`. On macOS/Linux, run \`sh start.sh\` or \`python3 server.py\` in a terminal.
3. The browser opens automatically at \`http://127.0.0.1:8766/\`. If it does not, open that address manually.
4. Mine words as usual. The app creates \`progress.json\` next to \`server.py\` on first launch and automatically saves decisions, Anki flags, column mappings, and settings.
5. Stop the server with \`Ctrl+C\`. The next launch restores the same progress automatically.

The server binds only to \`127.0.0.1\`, so it is intended for use on the same computer and is not exposed to your network. The default port is \`8766\` to avoid conflicting with AnkiConnect, which commonly uses \`8765\`. Change \`port\` in \`config.json\` if needed. Set \`open_browser\` to \`false\` to disable automatic browser launch. \`host\` is restricted to loopback addresses. The server stays running in the terminal until stopped with \`Ctrl+C\`.

Writes use an atomic file replacement to reduce the chance of a partially written progress file. Do not delete \`progress.json\` if you want to keep your progress.

## Configuration

\`config.json\`:

\`\`\`json
{
  "host": "127.0.0.1",
  "port": 8766,
  "open_browser": true,
  "progress_file": "progress.json"
}
\`\`\`

- \`host\`: local-only bind address; use \`127.0.0.1\` or \`localhost\`.
- \`port\`: HTTP port (1–65535).
- \`open_browser\`: automatically open the GUI when the server starts.
- \`progress_file\`: progress filename in the app directory.

For temporary port overrides, set the \`COCA_MINER_PORT\` environment variable.

## Browser-only alternative

You can still open the GUI from a trusted HTTPS origin, such as a configured GitHub Pages site. Use **progress.json を作成 / 接続** and **progress.json を開く** where the File System Access API is supported. Otherwise, use the JSON import/export controls.

## Controls

- **F** — mark as known.
- **J** — mark as unknown.
- **Z** — undo the last decision.

Known and unknown words already judged are excluded from subsequent mining candidates. Unknown words can be marked as added to Anki and exported as CSV.

## Data format

\`words.csv\` has four columns: \`Band\`, \`Headword\`, \`Related forms\`, and \`FREQ\`. It is treated as read-only by the app.

\`progress.json\` stores decisions, Anki flags, settings, and selected column mappings. It is not committed to the repository. The app can make a one-time in-memory migration from an older \`cocaMiner.v1\` localStorage entry so it can be saved to the progress file.

CSV import supports UTF-8/BOM, quoted cells, commas, and newline characters inside quoted fields.
