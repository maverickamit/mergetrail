# MergeTrail UI

Vite + React source for the review surface. `npm run build` writes into
`src/mergetrail/static/` so the Python server can ship the UI in one process.

`npm run dev` proxies `/review` and `/files` to `http://127.0.0.1:8765`.
