"""Build a 2x2 market-position quadrant chart from a JSON spec.

Usage:
    python3 scripts/make_quadrant.py spec.json --out DIR

Writes <name>.pptx (the editable master), <name>.pdf and <name>.png into
DIR, where <name> is the spec's "name" field or the spec file name.

Coordinates: each item has x and y in 0..1. x increases to the right
(completeness of vision), y increases upward (ability to execute). The
four quadrant names default to the classic set (Leaders top right,
Challengers top left, Visionaries bottom right, Niche Players bottom
left) and can be renamed or blanked in the spec.
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt

from _common import (AXIS, DOT_D, GRID, INK, MUTED, NAVY, QUAD_FILL_A,
                     QUAD_FILL_B, add_text, draw_dot, est_text_width, export,
                     fail, load_spec, new_slide, place_label, report,
                     spec_name)

# Plot rectangle in inches: the chart area inside the axes.
PLOT_X = 1.50
PLOT_Y = 1.62
PLOT_W = 10.35
PLOT_H = 5.05

DEFAULT_QUADRANTS = {
    "top_right": "Leaders",
    "top_left": "Challengers",
    "bottom_right": "Visionaries",
    "bottom_left": "Niche Players",
}


def _rect(slide, x, y, w, h, fill=None, line=None, line_w=0.75):
    shp = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y),
                                 Inches(w), Inches(h))
    if fill is None:
        shp.fill.background()
    else:
        shp.fill.solid()
        shp.fill.fore_color.rgb = fill
    if line is None:
        shp.line.fill.background()
    else:
        shp.line.color.rgb = line
        shp.line.width = Pt(line_w)
    shp.shadow.inherit = False
    return shp


def _validate(spec):
    if not spec.get("title"):
        fail("spec needs a title")
    items = spec.get("items")
    if not isinstance(items, list) or not items:
        fail("spec needs a non-empty items list")
    for i, item in enumerate(items):
        if not item.get("name"):
            fail("items[%d] needs a name" % i)
        for key in ("x", "y"):
            val = item.get(key)
            if not isinstance(val, (int, float)) or not 0.0 <= val <= 1.0:
                fail("items[%d].%s must be a number in 0..1" % (i, key))
        side = item.get("label_side", "auto")
        if side not in ("auto", "left", "right", "above", "below"):
            fail("items[%d].label_side must be auto, left, right, above "
                 "or below" % i)


def build(spec):
    _validate(spec)
    prs, slide = new_slide(spec["title"], spec.get("subtitle"))

    quadrants = dict(DEFAULT_QUADRANTS)
    for key, val in (spec.get("quadrants") or {}).items():
        if key in quadrants:
            quadrants[key] = val

    hw = PLOT_W / 2.0
    hh = PLOT_H / 2.0
    # Quadrant shading: alternating very light fills, then gridlines.
    _rect(slide, PLOT_X, PLOT_Y, hw, hh, fill=QUAD_FILL_A)              # TL
    _rect(slide, PLOT_X + hw, PLOT_Y, hw, hh, fill=QUAD_FILL_B)         # TR
    _rect(slide, PLOT_X, PLOT_Y + hh, hw, hh, fill=QUAD_FILL_B)         # BL
    _rect(slide, PLOT_X + hw, PLOT_Y + hh, hw, hh, fill=QUAD_FILL_A)    # BR
    mid_x = PLOT_X + hw
    mid_y = PLOT_Y + hh
    _rect(slide, mid_x - 0.006, PLOT_Y, 0.012, PLOT_H, fill=GRID)
    _rect(slide, PLOT_X, mid_y - 0.006, PLOT_W, 0.012, fill=GRID)
    _rect(slide, PLOT_X, PLOT_Y, PLOT_W, PLOT_H, fill=None, line=AXIS,
          line_w=1.0)

    # Axis arrowheads: up at the top of the y axis, right at the x axis end.
    for (ax, ay, rot) in ((PLOT_X - 0.07, PLOT_Y - 0.16, 0),
                          (PLOT_X + PLOT_W + 0.02, PLOT_Y + PLOT_H - 0.07, 90)):
        tri = slide.shapes.add_shape(MSO_SHAPE.ISOSCELES_TRIANGLE,
                                     Inches(ax), Inches(ay), Inches(0.14),
                                     Inches(0.14))
        tri.rotation = rot
        tri.fill.solid()
        tri.fill.fore_color.rgb = AXIS
        tri.line.fill.background()
        tri.shadow.inherit = False

    # Quadrant labels in the quadrant corners, muted.
    inset = 0.14
    label_specs = [
        ("top_left", PLOT_X + inset, PLOT_Y + inset, PP_ALIGN.LEFT),
        ("top_right", PLOT_X + PLOT_W - inset - 3.0, PLOT_Y + inset,
         PP_ALIGN.RIGHT),
        ("bottom_left", PLOT_X + inset, PLOT_Y + PLOT_H - inset - 0.3,
         PP_ALIGN.LEFT),
        ("bottom_right", PLOT_X + PLOT_W - inset - 3.0,
         PLOT_Y + PLOT_H - inset - 0.3, PP_ALIGN.RIGHT),
    ]
    for key, lx, ly, align in label_specs:
        text = quadrants.get(key) or ""
        if text:
            add_text(slide, lx, ly, 3.0, 0.3, text.upper(), 12, bold=True,
                     color=MUTED, align=align)

    # Axis labels.
    x_label = (spec.get("x_axis") or {}).get("label", "")
    if x_label:
        add_text(slide, PLOT_X, PLOT_Y + PLOT_H + 0.14, PLOT_W, 0.32,
                 x_label, 13, bold=True, color=INK, align=PP_ALIGN.CENTER)
    y_label = (spec.get("y_axis") or {}).get("label", "")
    if y_label:
        w = est_text_width(y_label, 13, bold=True)
        add_text(slide, PLOT_X - 0.62 - w / 2.0, PLOT_Y + PLOT_H / 2.0 - 0.16,
                 w, 0.32, y_label, 13, bold=True, color=INK,
                 align=PP_ALIGN.CENTER, rotation=270, wrap=False)

    # Items: dots first as collision obstacles, then labels.
    placed = []
    points = []
    for item in spec["items"]:
        cx = PLOT_X + float(item["x"]) * PLOT_W
        cy = PLOT_Y + (1.0 - float(item["y"])) * PLOT_H
        points.append((item, cx, cy))
        placed.append((cx - DOT_D / 2.0, cy - DOT_D / 2.0, DOT_D, DOT_D))
    bounds = (PLOT_X - 0.15, PLOT_Y - 0.10, PLOT_W + 0.30, PLOT_H + 0.20)
    labels = []
    for item, cx, cy in points:
        draw_dot(slide, cx, cy)
    for item, cx, cy in points:
        side = item.get("label_side", "auto")
        pref = "right" if side == "auto" else side
        lx, ly, lw, lh, align = place_label(placed, cx, cy, item["name"],
                                            pref, bounds)
        labels.append((item["name"], lx, ly, lw, lh, align))
    for text, lx, ly, lw, lh, align in labels:
        add_text(slide, lx, ly, lw, lh, text, 11, color=INK, align=align,
                 wrap=False)
    return prs


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("spec", help="path to the JSON spec")
    parser.add_argument("--out", required=True, help="output directory")
    args = parser.parse_args(argv)
    spec = load_spec(args.spec)
    prs = build(spec)
    name = spec_name(spec, args.spec)
    pptx_path, pdf_path, png_path = export(prs, args.out, name)
    report(name, pptx_path, pdf_path, png_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
