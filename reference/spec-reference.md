# Spec Reference

Both generators take one JSON spec file and an output directory:

```
python3 scripts/make_quadrant.py spec.json --out DIR
python3 scripts/make_hypecycle.py spec.json --out DIR
```

Each writes `<name>.pptx`, `<name>.pdf` and `<name>.png` into DIR.
`<name>` is the spec's `name` field, or the spec file name when `name`
is absent. Spec files may carry full-line `//` comments (the templates
use them); the loader drops lines that start with `//` before parsing.

Common behavior:

- One slide per spec, 16:9 (13.333 x 7.5 in), white background.
- Every element is a native PowerPoint shape or text box; the PPTX is
  the editable master. PDF and PNG are rendered from it with
  LibreOffice and pdftoppm.
- Item labels are placed automatically and deterministically: each
  label tries candidate positions in a fixed order set by its
  `label_side` preference and takes the first that overlaps no dot, no
  earlier label and (hype cycle only) no part of the curve, staying
  inside the plot bounds where possible.
- A spec that fails validation prints `RESULT: INVALID` with the exact
  field at fault and builds nothing.

## Quadrant spec (make_quadrant.py)

| Field | Type | Required | Meaning |
|---|---|---|---|
| `name` | string | no | Output file base name. Default: the spec file name. |
| `title` | string | yes | Chart title, top left. |
| `subtitle` | string | no | One line under the title, muted. |
| `x_axis.label` | string | no | Label under the plot, centered. Convention: completeness of vision. |
| `y_axis.label` | string | no | Label left of the plot, rotated, read bottom to top. Convention: ability to execute. |
| `quadrants.top_right` | string | no | Quadrant name, default `Leaders`. Set to `""` to hide. |
| `quadrants.top_left` | string | no | Quadrant name, default `Challengers`. |
| `quadrants.bottom_right` | string | no | Quadrant name, default `Visionaries`. |
| `quadrants.bottom_left` | string | no | Quadrant name, default `Niche Players`. |
| `items` | array | yes | One entry per plotted item, at least one. |
| `items[].name` | string | yes | Item label next to its dot. |
| `items[].x` | number 0..1 | yes | Horizontal position. 0 is the left edge, 1 the right edge, 0.5 the vertical quadrant boundary. |
| `items[].y` | number 0..1 | yes | Vertical position. 0 is the bottom edge, 1 the top edge, 0.5 the horizontal quadrant boundary. |
| `items[].label_side` | string | no | `auto` (default), `left`, `right`, `above` or `below`. A preference, not a guarantee: the placer still avoids overlaps. |

Layout notes:

- The four quadrants get very light alternating shading; the midlines
  and border are light gray. Quadrant names sit in the quadrant
  corners, uppercase and muted.
- Small arrowheads cap the top of the y axis and the right end of the
  x axis, marking the direction of increase.

## Hype cycle spec (make_hypecycle.py)

| Field | Type | Required | Meaning |
|---|---|---|---|
| `name` | string | no | Output file base name. Default: the spec file name. |
| `title` | string | yes | Chart title, top left. |
| `subtitle` | string | no | One line under the title, muted. |
| `y_label` | string | no | Label left of the plot, rotated. Default: `Expectations`. |
| `items` | array | yes | One entry per placed item, at least one. |
| `items[].name` | string | yes | Item label next to its dot. |
| `items[].t` | number 0..1 | yes | Position along the curve, 0 at the left edge, 1 at the right edge. The dot is drawn on the curve at this t. |
| `items[].label_side` | string | no | `auto` (default), `left`, `right`, `above` or `below`. A preference, not a guarantee. |

The curve and phases are fixed, not spec fields:

- Curve anchors (t, expectation): (0.00, 0.10), (0.08, 0.38),
  (0.16, 0.78), (0.215, 1.00), (0.28, 0.80), (0.36, 0.52),
  (0.45, 0.345), (0.55, 0.40), (0.66, 0.55), (0.78, 0.685),
  (0.90, 0.74), (1.00, 0.755). A Catmull-Rom spline through these
  anchors is sampled at 240 points and drawn as a native freeform
  polyline, 2.5 pt navy.
- Phase bands (t ranges): Innovation Trigger 0.00 to 0.15, Peak of
  Inflated Expectations 0.15 to 0.35, Trough of Disillusionment 0.35
  to 0.60, Slope of Enlightenment 0.60 to 0.83, Plateau of
  Productivity 0.83 to 1.00. Bands are separated by dashed verticals
  and labeled under the axis.
- Position guide: about 0.05 sits in the innovation trigger, 0.21 at
  the peak, 0.45 at the trough floor, 0.68 on the slope, 0.90 on the
  plateau.

## Styling constants

Defined in `scripts/_common.py`, shared by both charts:

- Font: DejaVu Sans (title 24 pt bold, subtitle 13 pt, axis labels
  13 pt bold, item labels 11 pt, quadrant labels 12 pt bold uppercase,
  phase labels 10 pt).
- Colors: dots and curve navy #00249C, text ink #262A33, muted labels
  #666E7E, axes #9AA1B0, gridlines #D9DEE8, quadrant shading #F2F5FA
  and #FCFCFD on white.
- Item dots are 0.17 in circles with a thin white edge.
