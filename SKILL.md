---
name: market-position-diagram
description: Make editable PowerPoint market-position charts from a JSON spec: 2x2 quadrant charts (items plotted by two axes into four named quadrants) and hype cycle charts (items placed on the classic expectations curve through five phases). Use when the user asks for a quadrant chart, a market position chart, a vendor comparison grid, a hype cycle, or an expectations curve as a slide or .pptx.
---

# Market Position Diagram

You write a small JSON **spec** that describes the content. A script turns it into an editable PowerPoint file (native shapes and text, nothing is a picture of a chart). **You never draw shapes or choose coordinates yourself.** Label placement is automatic and deterministic; if a label lands badly, steer it with the item's `label_side` field and rebuild.

Everything you need is in this folder:
- `scripts/make_quadrant.py` builds the 2x2 quadrant chart.
- `scripts/make_hypecycle.py` builds the hype cycle chart.
- `templates/` holds one fill-in spec per chart type. Always start from one.
- `examples/` holds two finished specs with their rendered `.pptx`, `.pdf` and `.png` outputs.
- `reference/spec-reference.md` lists every field for both specs.

Requirements: Python 3 with `pip install python-pptx` (see `requirements.txt`). The PDF and PNG outputs also need LibreOffice (`soffice`) and `pdftoppm`; the PPTX is built without them.

---

## Step 1: Choose the chart type

| The user wants... | Script | Template |
|---|---|---|
| Vendors or options compared on two dimensions, grouped into four quadrants | `scripts/make_quadrant.py` | `templates/quadrant-template.json` |
| Technologies or ideas placed on the expectations curve (trigger, peak, trough, slope, plateau) | `scripts/make_hypecycle.py` | `templates/hypecycle-template.json` |

## Step 2: Fill the template

Copy the template to a new file (for example `spec.json`) and replace every `<<...>>` with real content from the user's request.

**Hard rules:**
1. Use only facts the user gave or clearly implied. Do not invent placements; a dot's position is a judgment the user owns. If the user names items without positions, ask or use the positions they imply, and say which you assumed.
2. **Quadrant items** carry `x` and `y`, each 0 to 1. x increases to the right (completeness of vision), y increases upward (ability to execute). The midpoint 0.5 is the quadrant boundary.
3. **Hype cycle items** carry `t`, 0 to 1, the position along the curve from left to right. Rough guide: 0.05 innovation trigger, 0.21 peak of inflated expectations, 0.45 trough of disillusionment, 0.68 slope of enlightenment, 0.90 plateau of productivity.
4. **Quadrant names** default to Leaders (top right), Challengers (top left), Visionaries (bottom right) and Niche Players (bottom left). Rename them in the spec when the user uses different names; set one to `""` to hide it.
5. **Labels:** item names up to about 26 characters work best. Labels are placed automatically without overlapping dots, other labels, or (on the hype cycle) the curve itself. On a crowded chart, set an item's `label_side` (`auto`, `left`, `right`, `above`, `below`) to steer its label, then rebuild.
6. **Placeholders:** delete template items you have no content for. Never leave `<<...>>` in the file.
7. **Counts:** quadrant charts read best with 4 to 14 items, hype cycles with 3 to 10.

## Step 3: Build

```
python3 scripts/make_quadrant.py spec.json --out DIR
python3 scripts/make_hypecycle.py spec.json --out DIR
```

Each command writes three files into DIR, named from the spec's `name` field (or the spec file name when `name` is absent):
- `<name>.pptx`: the editable master. Every dot, label, line and band is a native PowerPoint shape or text box.
- `<name>.pdf`: one page, rendered from the PPTX by LibreOffice.
- `<name>.png`: a 150 dpi preview of the same page.

The script prints `RESULT: PASS` with the three file paths. On a broken spec it prints `RESULT: INVALID` with the exact problem (for example `items[2].x must be a number in 0..1`) and builds nothing.

## Step 4: Check the render (mandatory)

Open the PNG and confirm:
1. Every item name is legible and no label overlaps a dot, another label, or the curve.
2. Every dot sits where the spec puts it (right quadrant; on the curve at its phase).
3. Quadrant names, axis labels and phase labels are present and readable.
4. Nothing is clipped at the slide edges.

If a label is crowded, set that item's `label_side` and rebuild. If two dots nearly coincide, nudge one item's coordinates slightly and tell the user you did. Do not ship a render you have not viewed.

## Step 5: Deliver

Give the user the `.pptx`, plus the PDF or PNG if they asked for one. Say in one or two sentences what the chart shows and that every element is editable in PowerPoint. Do not paste the JSON spec into your answer unless the user asks for it.

---

## Worked examples

- Quadrant: `examples/enterprise_ai_platforms_quadrant.json` positions ten fictional vendors across all four quadrants of an Enterprise AI Platforms chart.
- Hype cycle: `examples/emerging_technologies_hypecycle.json` places seven generic technologies from the innovation trigger to the plateau.

## Style

Fixed by the scripts, not the spec: 16:9 slide, white background, navy dots (#00249C), gray axes and muted quadrant and phase labels, very light alternating quadrant shading, DejaVu Sans throughout. Chart semantics (titles, axis labels, quadrant names, item positions) all come from the spec.
