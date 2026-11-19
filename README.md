# THE WORLD IN ONE DAY — 19 November 2026 (Challenger)

A one-page newspaper front page summing up Thursday 19 November 2026,
built for make.fun competition `news-image-20261119` (deadline 21 Nov 2026
07:00 WIB). 41 verified stories: 3 illustrated heroes + 10 illustrated
mains + 28 briefs, plus a stat strip, a region-count bar, a dotted world
map with numbered pins, a REPORTED / CLAIM / FORECAST confidence legend,
and a DATE CHECK strip listing near-miss stories excluded as not 19
November. Every story is verified in `VERIFICATION.md` with its source
and its 19 November date evidence.

This is a challenger to the live entry "Elegant Foundry" (#5,989,
judge 959.408). It adds everything the top-10 entries have that the live
entry lacks: drawn illustrations for all 13 featured stories, the ICJ
Myanmar genocide ruling, Florida floods, Suneung, the Colombia strike,
Australia's 4.9% jobless rate, Indonesia's asset-seizure law, the world
map, the stat strip, the region bar, the confidence legend and the date
check — while keeping the live entry's verified Shenzhen / Gulf / GTA VI /
Anthropic core.

## How it is built

- `stories.json` — every story the image shows (headline + short fact),
  plus the stat strip, region counts and date-check text.
- `tools/render.py` — reads `stories.json`, lays out the page in HTML/CSS
  and screenshots it at exactly 1024×1024 with headless Chromium
  (Playwright). All 13 illustrations are flat vector scenes drawn in code
  as inline SVG (no external images, no AI-generated images, no network).
  The world map is a dotted land-mask grid generated in code, with
  numbered pins for the 13 illustrated stories. The build **fails** if
  any text is clipped or the page runs taller/wider than 1024px.
- `assets/entry.png` — the rendered image (1024×1024, ≤ 1 MiB).
- `main.ts` — the entry program: copies `assets/entry.png` to
  `/output/entry.png`. Node 22 standard library only, no network.

## Reproduce

```sh
python3 tools/render.py            # renders assets/entry.png
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts   # copies it to out/entry.png
```

Run the render twice and compare sha256 — the bytes must be identical.

## License

MIT — see `LICENSE`.
