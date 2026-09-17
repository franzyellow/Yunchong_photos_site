# AGENTS.md

Personal static photo site. No build step, no framework, no tests/lint/CI. Plain HTML/CSS/JS + one Python upload script.

## Commands

- Preview locally: `uv run python -m http.server` (or any static server). JS does `fetch('photos.json')`, so opening `index.html` via `file://` will not work.
- Upload a year of photos: `uv run main.py photo_selection/<year>`. Python env is uv-managed (3.12, `uv.lock`).
- Deploy: push to `main` on GitHub → GitHub Pages (`franzyellow.github.io/Yunchong_photos_site`). No CI pipeline.

## Architecture

- `photos.json` is the single source of data: top-level keys are album names (usually a year), each an array of `{src, thumb, caption}` with R2 URLs. `index.html`/`main.js` render album cards; `year.html?y=<key>` + `year.js` render one album with a lightbox.
- `main.py` uploads originals + generated thumbnails (1000px max edge, EXIF-rotation fixed) to Cloudflare R2 via boto3, then **appends** entries to `photos.json`. The folder name becomes both the R2 path prefix (`<year>/full|thumb/...`) and the `photos.json` key.
- `photo_selection/` is the gitignored local staging area for source images. Never commit photos or `.env`.

## Gotchas

- Upload needs `.env` with `R2_ACCESS_KEY_ID` / `R2_SECRET_ACCESS_KEY` (gitignored). Nothing else in the repo needs secrets.
- Captions in `photos.json` are hand-edited after upload (the script only seeds them with the filename stem). Re-running `main.py` on an existing year **skips files already in `photos.json`** (matched by filename), so you can drop new photos into an existing year folder and re-run safely. To re-upload a file, delete its entry from `photos.json` first. Dedup is based on `photos.json`, not R2 — if an upload run dies midway, re-running re-uploads everything not yet recorded.
- `main.py` accepts `.heic` in its file filter, but Pillow cannot decode HEIC, so thumbnail generation crashes on HEIC files. Convert to JPEG first.
- `main.js` sorts albums numerically (`b - a`); non-numeric keys like `"2020-2021"` produce NaN and keep insertion order. Keep this in mind when adding multi-year albums or touching the sort.
