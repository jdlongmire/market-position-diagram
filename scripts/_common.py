"""Shared helpers for the market-position-diagram generators.

Both chart scripts build a single 16:9 slide with python-pptx, save the
PPTX as the editable master, then render a PDF and a PNG preview from it
with LibreOffice and pdftoppm, the same toolchain the
enterprise-architecture-diagram skill uses.

Label placement is deterministic. Each item dot is placed first; its label
then tries a fixed list of candidate positions (in an order set by the
item's label_side preference) and takes the first candidate that does not
overlap an already placed label or dot and stays inside the plot bounds.
If every candidate overlaps something, the candidate with the least total
overlap wins, so output never depends on randomness or iteration order.
"""

import json
import os
import re
import shutil
import subprocess

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt

SLIDE_W = 13.333
SLIDE_H = 7.5
FONT = "DejaVu Sans"

NAVY = RGBColor(0x00, 0x24, 0x9C)
INK = RGBColor(0x26, 0x2A, 0x33)
MUTED = RGBColor(0x66, 0x6E, 0x7E)
AXIS = RGBColor(0x9A, 0xA1, 0xB0)
GRID = RGBColor(0xD9, 0xDE, 0xE8)
QUAD_FILL_A = RGBColor(0xF2, 0xF5, 0xFA)
QUAD_FILL_B = RGBColor(0xFC, 0xFC, 0xFD)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)

DOT_D = 0.17          # item dot diameter, inches
LABEL_FONT = 11       # item label size, points
LABEL_GAP = 0.07      # gap between a dot and its label, inches
LABEL_H = 0.26        # label box height, inches


def load_spec(path):
    with open(path, "r", encoding="utf-8") as fh:
        text = fh.read()
    # Templates ship with // comment lines, like the
    # enterprise-architecture-diagram templates. Drop full-line comments
    # before parsing; string values are left untouched.
    lines = [ln for ln in text.splitlines()
             if not ln.lstrip().startswith("//")]
    return json.loads("\n".join(lines))


def spec_name(spec, spec_path):
    name = spec.get("name") or os.path.splitext(os.path.basename(spec_path))[0]
    return re.sub(r"[^A-Za-z0-9_-]+", "_", str(name))


def new_slide(prs_title, prs_subtitle):
    """Create a blank 16:9 deck with one slide and the title block drawn."""
    prs = Presentation()
    prs.slide_width = Inches(SLIDE_W)
    prs.slide_height = Inches(SLIDE_H)
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = WHITE
    add_text(slide, 0.55, 0.30, 12.23, 0.55, prs_title, 24, bold=True,
             color=INK, align=PP_ALIGN.LEFT)
    if prs_subtitle:
        add_text(slide, 0.55, 0.88, 12.23, 0.35, prs_subtitle, 13,
                 color=MUTED, align=PP_ALIGN.LEFT)
    return prs, slide


def add_text(slide, x, y, w, h, text, size, bold=False, color=INK,
             align=PP_ALIGN.LEFT, rotation=0, wrap=True):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    box.rotation = rotation
    tf = box.text_frame
    tf.word_wrap = wrap
    tf.margin_left = 0
    tf.margin_right = 0
    tf.margin_top = 0
    tf.margin_bottom = 0
    para = tf.paragraphs[0]
    para.alignment = align
    run = para.add_run()
    run.text = text
    font = run.font
    font.name = FONT
    font.size = Pt(size)
    font.bold = bold
    font.color.rgb = color
    return box


def est_text_width(text, size_pt, bold=False):
    """Rough rendered width of a single line, in inches.

    DejaVu Sans averages about 0.60 em per character at these sizes; the
    estimate is used only to size label boxes for collision testing, with
    padding added, never to lay out visible geometry.
    """
    factor = 0.63 if bold else 0.60
    return len(text) * size_pt * factor / 72.0 + 0.10


def _overlap_area(a, b):
    dx = min(a[0] + a[2], b[0] + b[2]) - max(a[0], b[0])
    dy = min(a[1] + a[3], b[1] + b[3]) - max(a[1], b[1])
    if dx <= 0 or dy <= 0:
        return 0.0
    return dx * dy


def _candidates(cx, cy, w, h, side):
    r = DOT_D / 2.0
    g = LABEL_GAP
    d = r * 0.72 + g * 0.72
    pos = {
        "right": (cx + r + g, cy - h / 2.0),
        "left": (cx - r - g - w, cy - h / 2.0),
        "above": (cx - w / 2.0, cy - r - g - h),
        "below": (cx - w / 2.0, cy + r + g),
        "above_right": (cx + d, cy - d - h),
        "below_right": (cx + d, cy + d),
        "above_left": (cx - d - w, cy - d - h),
        "below_left": (cx - d - w, cy + d),
    }
    orders = {
        "right": ["right", "above_right", "below_right", "above", "below",
                  "left", "above_left", "below_left"],
        "left": ["left", "above_left", "below_left", "above", "below",
                 "right", "above_right", "below_right"],
        "above": ["above", "above_right", "above_left", "right", "left",
                  "below", "below_right", "below_left"],
        "below": ["below", "below_right", "below_left", "right", "left",
                  "above", "above_right", "above_left"],
    }
    order = orders.get(side, orders["right"])
    return [(name, pos[name][0], pos[name][1]) for name in order]


def place_label(placed, cx, cy, text, side, bounds, size=LABEL_FONT,
                obstacles=()):
    """Choose a label box for the dot at (cx, cy); record and return it.

    placed is a list of (x, y, w, h) rects already used by dots and labels.
    obstacles are extra rects scored against but not recorded (for
    example, segments of the hype cycle curve, so a label never sits on
    the line). bounds is the (x, y, w, h) rect labels should stay
    inside. Returns (x, y, w, h, align) in inches.
    """
    w = est_text_width(text, size)
    h = LABEL_H
    bx, by, bw, bh = bounds
    best = None
    for name, x, y in _candidates(cx, cy, w, h, side):
        rect = (x, y, w, h)
        outside = 0.0
        if x < bx:
            outside += (bx - x) * h
        if y < by:
            outside += (by - y) * w
        if x + w > bx + bw:
            outside += (x + w - bx - bw) * h
        if y + h > by + bh:
            outside += (y + h - by - bh) * w
        score = outside * 4.0
        for other in placed:
            score += _overlap_area(rect, other)
        for other in obstacles:
            score += _overlap_area(rect, other)
        if best is None or score < best[0]:
            best = (score, x, y, name)
        if score == 0.0:
            break
    _, x, y, name = best
    placed.append((x, y, w, h))
    if name.endswith("left"):
        align = PP_ALIGN.RIGHT
    elif name.endswith("right"):
        align = PP_ALIGN.LEFT
    elif name in ("above", "below"):
        align = PP_ALIGN.CENTER
    else:
        align = PP_ALIGN.LEFT if name == "right" else PP_ALIGN.RIGHT
    return x, y, w, h, align


def draw_dot(slide, cx, cy):
    from pptx.enum.shapes import MSO_SHAPE
    dot = slide.shapes.add_shape(
        MSO_SHAPE.OVAL, Inches(cx - DOT_D / 2.0), Inches(cy - DOT_D / 2.0),
        Inches(DOT_D), Inches(DOT_D))
    dot.fill.solid()
    dot.fill.fore_color.rgb = NAVY
    dot.line.color.rgb = WHITE
    dot.line.width = Pt(1.0)
    dot.shadow.inherit = False
    return dot


def _strip_shape_styles(prs):
    """Remove the default <p:style> element from every shape.

    python-pptx adds a style element whose effectRef points at a theme
    effect (a drop shadow). The charts set every fill and line
    explicitly, so the style element is dropped to keep renders flat.
    """
    from pptx.oxml.ns import qn
    for slide in prs.slides:
        for shp in slide.shapes:
            el = shp._element.find(qn("p:style"))
            if el is not None:
                shp._element.remove(el)


def export(prs, outdir, name):
    """Save the PPTX master, then render PDF and PNG from it.

    Returns (pptx_path, pdf_path, png_path); pdf/png are None if the
    external tools are missing or the render fails.
    """
    _strip_shape_styles(prs)
    os.makedirs(outdir, exist_ok=True)
    pptx_path = os.path.join(outdir, name + ".pptx")
    prs.save(pptx_path)
    pdf_path = None
    png_path = None
    soffice = shutil.which("soffice") or "/usr/bin/soffice"
    if os.path.exists(soffice):
        try:
            subprocess.run(
                [soffice, "--headless", "--convert-to", "pdf",
                 "--outdir", outdir, pptx_path],
                check=True, capture_output=True, timeout=300)
            candidate = os.path.join(outdir, name + ".pdf")
            if os.path.exists(candidate):
                pdf_path = candidate
        except Exception:
            pdf_path = None
    if pdf_path and shutil.which("pdftoppm"):
        try:
            subprocess.run(
                ["pdftoppm", "-png", "-r", "150", "-singlefile",
                 pdf_path, os.path.join(outdir, name)],
                check=True, capture_output=True, timeout=180)
            candidate = os.path.join(outdir, name + ".png")
            if os.path.exists(candidate):
                png_path = candidate
        except Exception:
            png_path = None
    return pptx_path, pdf_path, png_path


def report(name, pptx_path, pdf_path, png_path):
    print("RESULT: PASS")
    print("PPTX: " + pptx_path)
    if pdf_path:
        print("PDF: " + pdf_path)
    if png_path:
        print("PNG: " + png_path)


def fail(message):
    print("RESULT: INVALID")
    print("ERROR: " + message)
    raise SystemExit(1)
