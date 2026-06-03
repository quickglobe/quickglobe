#!/usr/bin/env python3
"""Generate the quickglobe icon set from a single source of truth.

The mark is a circular blueprint "globe": blue ink meridians/parallels on a
paper disc, with transparent corners so the favicon reads as a circle (not a
square). Run from the repo root:

    python3 tools/generate-icons.py

Requires cairosvg + pillow (pip install cairosvg pillow).

Outputs (repo root):
  favicon.svg                     master, circular, transparent corners
  favicon-16x16/32x32/48x48.png   circular, transparent corners
  favicon.ico                     multi-res 16/32/48
  android-chrome-192x192/512.png  circular, transparent corners
  apple-touch-icon.png            globe on a SOLID paper square (no alpha) —
                                  iOS masks it into a rounded square (squircle),
                                  so it can't be a literal circle; the solid
                                  background keeps iOS's mask corners clean.
"""
import io
import math

import cairosvg
from PIL import Image

INK = "#1f6feb"               # blueprint blue
PAPER_A = "rgb(238, 235, 228)"  # disc highlight (upper-left)
PAPER_B = "#f4efe4"             # disc / page paper
PAPER_SOLID = "#f4efe4"         # flat fill behind apple-touch-icon


def globe_svg(size=512, margin_ratio=0.06, solid_bg=False, weight=1.0,
              detail="full"):
    """Return an SVG string for a circular globe sized to `size`.

    margin_ratio: gap between the globe ring and the canvas edge (as a
        fraction of half the canvas). Bigger margin = more breathing room
        (used for apple-touch where iOS rounds the corners).
    solid_bg: fill the whole square with paper (no transparency). Used only
        for apple-touch-icon so iOS's squircle mask has no black/clear corners.
    weight: stroke multiplier — bump above 1.0 so tiny favicons stay legible.
    detail: "full" (all meridians/parallels) or "min" (sparse grid for 16px).
    """
    C = size / 2.0
    R = C * (1 - margin_ratio)

    ring_w = 0.030 * R * weight   # heavy globe outline
    grid_w = 0.0208 * R * weight  # meridian / parallel lines
    grid_op = 0.79 if weight <= 1.05 else 1.0
    meridian_rxf = (0.30, 0.62) if detail == "full" else (0.55,)
    parallels = (0, 16, 38, 62) if detail == "full" else (0, 40)
    uid = "qg"               # gradient/clip id prefix

    def f(x):
        return round(x, 3)

    parts = []
    parts.append(
        f'<svg viewBox="0 0 {size} {size}" '
        f'xmlns="http://www.w3.org/2000/svg">'
    )

    # --- defs: paper disc gradient, blue "lit" highlight, clip path ---
    parts.append("<defs>")
    parts.append(
        f'<radialGradient id="{uid}_bg" cx="38%" cy="32%" r="90%">'
        f'<stop offset="0%" stop-color="{PAPER_A}"/>'
        f'<stop offset="55%" stop-color="{PAPER_B}"/>'
        f'<stop offset="100%" stop-color="{PAPER_B}"/>'
        f"</radialGradient>"
    )
    parts.append(
        f'<radialGradient id="{uid}_lit" cx="36%" cy="30%" r="78%">'
        f'<stop offset="0%" stop-color="rgba(31, 111, 235, 0.168)"/>'
        f'<stop offset="55%" stop-color="rgba(31, 111, 235, 0.048)"/>'
        f'<stop offset="100%" stop-color="rgba(31, 111, 235, 0)"/>'
        f"</radialGradient>"
    )
    parts.append(
        f'<clipPath id="{uid}_clip"><circle cx="{f(C)}" cy="{f(C)}" '
        f'r="{f(R)}"/></clipPath>'
    )
    parts.append("</defs>")

    # --- optional solid square background (apple-touch only) ---
    if solid_bg:
        parts.append(f'<rect width="{size}" height="{size}" fill="{PAPER_SOLID}"/>')

    # --- the paper disc ---
    parts.append(f'<circle cx="{f(C)}" cy="{f(C)}" r="{f(R)}" fill="url(#{uid}_bg)"/>')

    # --- meridians + parallels, slightly tilted, clipped to the disc ---
    parts.append(f'<g clip-path="url(#{uid}_clip)">')
    parts.append(f'<g transform="rotate(-7 {f(C)} {f(C)})">')
    parts.append(
        f'<circle cx="{f(C)}" cy="{f(C)}" r="{f(R)}" fill="url(#{uid}_lit)"/>'
    )

    line = (
        f'stroke="{INK}" stroke-width="{f(grid_w)}" fill="none" '
        f'opacity="{grid_op}"'
    )
    # central meridian
    parts.append(
        f'<line x1="{f(C)}" y1="{f(C - R)}" x2="{f(C)}" y2="{f(C + R)}" {line}/>'
    )
    # meridian ellipses (vertical), rx as fraction of R
    for rxf in meridian_rxf:
        parts.append(
            f'<ellipse cx="{f(C)}" cy="{f(C)}" rx="{f(rxf * R)}" '
            f'ry="{f(R)}" {line}/>'
        )
    # parallels (horizontal), latitude ellipses; tilt factor 0.16
    tilt = 0.16
    for lat in parallels:
        rx = R * math.cos(math.radians(lat))
        ry = rx * tilt
        dy = R * math.sin(math.radians(lat))
        for cy in {C - dy, C + dy}:
            parts.append(
                f'<ellipse cx="{f(C)}" cy="{f(cy)}" rx="{f(rx)}" '
                f'ry="{f(ry)}" {line}/>'
            )
    parts.append("</g>")  # rotate
    parts.append("</g>")  # clip

    # --- heavy globe outline ring ---
    parts.append(
        f'<circle cx="{f(C)}" cy="{f(C)}" r="{f(R)}" fill="none" '
        f'stroke="{INK}" stroke-width="{f(ring_w)}"/>'
    )
    # --- upper-left shine arc on the ring ---
    a0, a1 = math.radians(200), math.radians(290)
    x0, y0 = C + R * math.cos(a0), C + R * math.sin(a0)
    x1, y1 = C + R * math.cos(a1), C + R * math.sin(a1)
    parts.append(
        f'<path d="M {f(x0)} {f(y0)} A {f(R)} {f(R)} 0 0 1 {f(x1)} {f(y1)}" '
        f'fill="none" stroke="rgba(31, 111, 235, 0.95)" '
        f'stroke-width="{f(ring_w * 1.3)}" stroke-linecap="round" opacity="0.4"/>'
    )

    parts.append("</svg>")
    return "".join(parts)


def render_png(svg, out, px):
    cairosvg.svg2png(
        bytestring=svg.encode(), write_to=out,
        output_width=px, output_height=px,
    )
    print(f"  {out}  ({px}x{px})")


def render_flat_png(svg, out, px, bg):
    """Render then flatten onto a solid background (drop alpha) for iOS."""
    raw = cairosvg.svg2png(bytestring=svg.encode(), output_width=px, output_height=px)
    fg = Image.open(io.BytesIO(raw)).convert("RGBA")
    base = Image.new("RGBA", fg.size, bg)
    base.alpha_composite(fg)
    base.convert("RGB").save(out, "PNG")
    print(f"  {out}  ({px}x{px}, flattened, no alpha)")


def main():
    # Master SVG — circular, transparent corners, modest margin.
    master = globe_svg(size=512, margin_ratio=0.05, solid_bg=False)
    with open("favicon.svg", "w") as fh:
        fh.write('<?xml version="1.0" encoding="UTF-8"?>\n' + master + "\n")
    print("  favicon.svg  (master, circular)")

    # Transparent-corner rasters (browser tab + PWA). Small sizes get a
    # bolder, simplified globe so the rings don't vanish in a tab.
    small = {
        16: globe_svg(size=512, margin_ratio=0.05, weight=2.4, detail="min"),
        32: globe_svg(size=512, margin_ratio=0.05, weight=1.6, detail="full"),
        48: globe_svg(size=512, margin_ratio=0.05, weight=1.3, detail="full"),
    }
    for px in (16, 32, 48):
        render_png(small[px], f"favicon-{px}x{px}.png", px)
    render_png(master, "android-chrome-192x192.png", 192)
    render_png(master, "android-chrome-512x512.png", 512)

    # favicon.ico (multi-resolution from the PNGs).
    sizes = [16, 32, 48]
    imgs = [Image.open(f"favicon-{s}x{s}.png").convert("RGBA") for s in sizes]
    imgs[0].save("favicon.ico", format="ICO", sizes=[(s, s) for s in sizes])
    print("  favicon.ico  (16/32/48)")

    # apple-touch-icon: more margin (iOS rounds corners) + solid paper bg.
    apple = globe_svg(size=180, margin_ratio=0.12, solid_bg=True)
    render_flat_png(apple, "apple-touch-icon.png", 180, PAPER_SOLID)


if __name__ == "__main__":
    main()
