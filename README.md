# Client Acquisition Plan — Asset Pipeline

Rendering pipeline for Gro.X growth-plan visual assets.

## How it works

1. `logos/` — official brand marks (SVG)
2. `scripts/render.py` — generates all visual assets (SVG + PNG) from a prospect params file
3. `params/<prospect>.json` — per-prospect content (niche examples, search→page rows)
4. On every push to `scripts/`, `params/`, or `logos/`, a GitHub Action renders everything and commits the output to `svg/` and `png/`

## Output

- `png/static/` — assets identical for every Branch-A prospect (chain diagram, channel-fit heatmap, funnel scenario)
- `png/<slug>/` — prospect-specific assets (channel cards, search-matched pages)

Stable raw URLs (used by Gamma document generation):

```
https://raw.githubusercontent.com/edd1epark/client-acquisition-plan/main/png/static/<asset>.png
https://raw.githubusercontent.com/edd1epark/client-acquisition-plan/main/png/<slug>/<asset>.png
```

## Adding a prospect

Add `params/<slug>.json` (copy `params/tva.json` as a template) and push — the Action renders and commits the new assets automatically.
