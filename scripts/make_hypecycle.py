"""Build a hype cycle chart from a JSON spec.

Usage:
    python3 scripts/make_hypecycle.py spec.json --out DIR

Writes <name>.pptx (the editable master), <name>.pdf and <name>.png into
DIR, where <name> is the spec's "name" field or the spec file name.

Each item has a t in 0..1, its position along the curve from left to
right. The curve is the classic hype shape, built as a Catmull-Rom spline
through fixed anchor points (rise, peak, trough, recovery, plateau),
sampled at 240 points and drawn as a native freeform polyline, so the
slide stays editable. The five phases are drawn as bands under the
curve: Innovation Trigger, Peak of Inflated Expectations, Trough of
Disillusionment, Slope of Enlightenment, Plateau of Productivity.
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

from _common import (AXIS, DOT_D, GRID, INK, MUTED, NAVY, add_text,
                     draw_dot, est_text_width, export, fail, load_spec,
                     new_slide, place_label, report, spec_name)

# Plot rectangle in inches.
PLOT_X = 1.30
PLOT_Y = 1.62
PLOT_W = 10.95
PLOT_H = 4.50
PHASE_Y = PLOT_Y + PLOT_H + 0.22   # phase label band top

PHASES = [
    ("Innovation Trigger", 0.00, 0.15),
    ("Peak of Inflated Expectations", 0.15, 0.35),
    ("Trough of Disillusionment", 0.35, 0.60),
    ("Slope of Enlightenment", 0.60, 0.83),
    ("Plateau of Productivity", 0.83, 1.00),
]

# (t, expectation) anchors for the classic curve shape.
ANCHORS = [
    (0.00, 0.10), (0.08, 0.38), (0.16, 0.78), (0.215, 1.00),
    (0.28, 0.80), (0.36, 0.52), (0.45, 0.345), (0.55, 0.40),
    (0.66, 0.55), (0.78, 0.685), (0.90, 0.74), (1.00, 0.755),
]


def curve_y(t):
    """Expectation at position t, Catmull-Rom through ANCHORS."""
    pts = ANCHORS
    if t <= pts[0][0]:
        return pts[0][1]
    if t >= pts[-1][0]:
        return pts[-1][1]
    i = 0
    while i < len(pts) - 2 and t > pts[i + 1][0]:
        i += 1
    p0 = pts[max(i - 1, 0)]
    p1 = pts[i]
    p2 = pts[i + 1]
    p3 = pts[min(i + 2, len(pts) - 1)]
    u = (t - p1[0]) / (p2[0] - p1[0])
    u2 = u * u
    u3 = u2 * u
    y = 0.5 * ((2.0 * p1[1]) + (-p0[1] + p2[1]) * u
               + (2.0 * p0[1] - 5.0 * p1[1] + 4.0 * p2[1] - p3[1]) * u2
               + (-p0[1] + 3.0 * p1[1] - 3.0 * p2[1] + p3[1]) * u3)
    return max(0.03, min(1.02, y))


def _line(slide, x, y, w, h, color, weight=0.75, dash=None):
    shp = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y),
                                 Inches(w), Inches(h))
    shp.fill.solid()
    shp.fill.fore_color.rgb = color
    shp.line.fill.background()
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
        val = item.get("t")
        if not isinstance(val, (int, float)) or not 0.0 <= val <= 1.0:
            fail("items[%d].t must be a number in 0..1" % i)
        side = item.get("label_side", "auto")
        if side not in ("auto", "left", "right", "above", "below"):
            fail("items[%d].label_side must be auto, left, right, above "
                 "or below" % i)


def build(spec):
    _validate(spec)
    prs, slide = new_slide(spec["title"], spec.get("subtitle"))
    y_bottom = PLOT_Y + PLOT_H

    # Light horizontal gridlines.
    for frac in (0.25, 0.50, 0.75):
        gy = PLOT_Y + (1.0 - frac) * PLOT_H
        _line(slide, PLOT_X, gy, PLOT_W, 0.01, GRID)

    # Phase separators (dashed verticals) running into the label band.
    for _, start, _end in PHASES[1:]:
        sx = PLOT_X + start * PLOT_W
        sep = slide.shapes.add_connector(1, Inches(sx), Inches(PLOT_Y + 0.05),
                                         Inches(sx), Inches(PHASE_Y + 0.02))
        sep.line.color.rgb = GRID
        sep.line.width = Pt(0.75)
        ln = sep.line._get_or_add_ln()
        dash = ln.makeelement(qn("a:prstDash"), {"val": "dash"})
        ln.append(dash)
        sep.shadow.inherit = False

    # Axes: left and bottom.
    _line(slide, PLOT_X, PLOT_Y, 0.014, PLOT_H, AXIS)
    _line(slide, PLOT_X, y_bottom - 0.007, PLOT_W, 0.014, AXIS)

    # The curve as a sampled freeform polyline.
    samples = 240
    coords = []
    for i in range(samples + 1):
        t = i / samples
        px = PLOT_X + t * PLOT_W
        py = PLOT_Y + (1.0 - curve_y(t)) * PLOT_H
        coords.append((px, py))
    # This python-pptx version's freeform builder takes local coordinates
    # that are already EMU integers (it rounds each vertex to an int), so
    # pass EMU values with scale 1.0. Passing inches with a large scale
    # quantizes every vertex to a whole inch and draws a staircase.
    emu = [(int(round(px * 914400)), int(round(py * 914400)))
           for px, py in coords]
    builder = slide.shapes.build_freeform(emu[0][0], emu[0][1], scale=1.0)
    builder.add_line_segments(emu[1:], close=False)
    curve = builder.convert_to_shape()
    curve.fill.background()
    curve.line.color.rgb = NAVY
    curve.line.width = Pt(2.5)
    curve.shadow.inherit = False

    # Phase labels, centered in each band, wrapped over up to three lines.
    for text, start, end in PHASES:
        bx = PLOT_X + start * PLOT_W
        bw = (end - start) * PLOT_W
        add_text(slide, bx + 0.04, PHASE_Y + 0.04, bw - 0.08, 0.62, text,
                 10, color=MUTED, align=PP_ALIGN.CENTER)

    # Y axis label.
    y_label = spec.get("y_label", "Expectations")
    if y_label:
        w = est_text_width(y_label, 13, bold=True)
        add_text(slide, PLOT_X - 0.62 - w / 2.0, PLOT_Y + PLOT_H / 2.0 - 0.16,
                 w, 0.32, y_label, 13, bold=True, color=INK,
                 align=PP_ALIGN.CENTER, rotation=270, wrap=False)

    # Items: dots on the curve first as obstacles, then labels.
    placed = []
    points = []
    for item in spec["items"]:
        t = float(item["t"])
        cx = PLOT_X + t * PLOT_W
        cy = PLOT_Y + (1.0 - curve_y(t)) * PLOT_H
        points.append((item, cx, cy))
        placed.append((cx - DOT_D / 2.0, cy - DOT_D / 2.0, DOT_D, DOT_D))
    bounds = (PLOT_X - 0.10, 1.30, PLOT_W + 0.45, PLOT_H + 0.55)
    for item, cx, cy in points:
        draw_dot(slide, cx, cy)
    # The curve itself is an obstacle for labels: a flat stretch (the
    # plateau) would otherwise run straight through a right-side label.
    # Build one thin rect per coarse curve segment; segments close to an
    # item's own dot are skipped for that item.
    segments = []
    stride = 8
    for i in range(0, len(coords) - stride, stride):
        x1, y1 = coords[i]
        x2, y2 = coords[i + stride]
        segments.append((min(x1, x2) - 0.03, min(y1, y2) - 0.03,
                         abs(x2 - x1) + 0.06, abs(y2 - y1) + 0.06))
    labels = []
    for item, cx, cy in points:
        side = item.get("label_side", "auto")
        pref = "right" if side == "auto" else side
        obstacles = [s for s in segments
                     if abs(s[0] + s[2] / 2.0 - cx) > 0.20
                     or abs(s[1] + s[3] / 2.0 - cy) > 0.20]
        lx, ly, lw, lh, align = place_label(placed, cx, cy, item["name"],
                                            pref, bounds,
                                            obstacles=obstacles)
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
