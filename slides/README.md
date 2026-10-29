# From PDF to Structure (Slidev)

A short, non-technical deck about **what PDF segmentation is for** — no UI walkthrough, no
architecture. Demo document: `A/HRC/PRST/35/1` (`68548.pdf`, 3 pages, 52 segments).

Theme: [`slidev-theme-mokkapps`](https://github.com/mokkapps/slidev-theme-mokkapps).

## Run it

```bash
cd slides
bun install
bun run dev        # http://localhost:3030   (run from this directory)
```

`bun run dev` only works from `slides/` — the repo root has no `package.json`.

## Build for GitHub Pages

Pages serves the `/docs` folder of this repo.

```bash
cd slides
bun run build      # -> ../docs, base /pdf-document-layout-analysis/, plus .nojekyll
```

If the repository is renamed, change `--base` in `package.json`.

## Record the video

```bash
cd slides
bunx slidev export --format png --output ../.slides-export
ffmpeg -framerate 1/6 -i ../.slides-export/%d.png \
       -c:v libx264 -pix_fmt yuv420p ../segmentation-demo.mp4
```

11 slides at 6 s each ≈ 1:06. Every slide has speaker notes (`p` in dev mode).

## Figures

All figures come from the running service on the demo document, **VGT** (`Fast Mode` off).

- `overlay/input-p1.png` — the untouched PDF page
- `overlay/output-p1.png` — the same page annotated by `POST /visualize`
- `detail-band.png` — masthead close-up, cut from the annotated PDF at natural whitespace
- `filter-toc.png` — page 1 with **Section header** blocks kept, everything else faded
- `filter-text.png` — page 1 with **Text** blocks kept, everything else faded

The two filter figures are drawn from the segmentation JSON at 200 dpi, then the kept blocks are
pasted back over a heavily faded page. Both share the same crop rectangle so the two slides line up.

Regenerate the source data:

```bash
curl -X POST http://127.0.0.1:5060 -F 'file=@68548.pdf' -F 'fast=false' > segments.json
curl -X POST http://127.0.0.1:5060/visualize -F 'file=@68548.pdf' -F 'fast=false' -o viz.pdf
pdftoppm -r 200 -png viz.pdf page
```
