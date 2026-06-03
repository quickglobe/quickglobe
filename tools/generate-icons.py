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


# --- The full "quickglobe" composition: globe + left-trailing motion swooshes.
# Lifted verbatim from the original hand-authored favicon so the approved look
# is preserved exactly. Globe is centred at (250,250) r=168 in a 500 viewBox;
# the swooshes trail off to the left (down to x~36). Used for the LARGE icons
# only — at tiny sizes the swooshes muddy the mark, so favicon.ico / 16 / 32 /
# 48 use the clean bold globe from globe_svg() instead.
ORIG_DEFS = (
    '<radialGradient id="g1732985003_bg" cx="38%" cy="32%" r="90%">'
    '<stop offset="0%" stop-color="rgb(238, 235, 228)"/>'
    '<stop offset="55%" stop-color="#f4efe4"/>'
    '<stop offset="100%" stop-color="#f4efe4"/></radialGradient>'
    '<radialGradient id="g1732985003_lit" cx="36%" cy="30%" r="78%">'
    '<stop offset="0%" stop-color="rgba(31, 111, 235, 0.168)"/>'
    '<stop offset="55%" stop-color="rgba(31, 111, 235, 0.048)"/>'
    '<stop offset="100%" stop-color="rgba(31, 111, 235, 0)"/></radialGradient>'
    '<clipPath id="g1732985003_clip"><circle cx="250" cy="250" r="168"/></clipPath>'
)
ORIG_BODY = (
    '<circle cx="250" cy="250" r="184" fill="#1f6feb" opacity="0.04"/>'
    '<g transform="rotate(-7 250 250)">'
    '<path d="M 130.5274226711539 380.08750211791164 A 145.84908645689342 23.33585383310295 0 0 1 130.52742267115383 353.31771035631147" fill="none" stroke="#1f6feb" stroke-width="3.69" stroke-linecap="round" opacity="0.6"/>'
    '<path d="M 105.4297987398842 377.98446199552495 A 160.84908645689342 25.735853833102947 0 0 1 105.4297987398842 355.4207504786981" fill="none" stroke="#1f6feb" stroke-width="2.88" stroke-linecap="round" opacity="0.34"/>'
    '<path d="M 81.83468228951781 374.9287337861256 A 175.84908645689342 28.135853833102946 0 0 1 81.83468228951781 358.4764786880975" fill="none" stroke="#1f6feb" stroke-width="2.07" stroke-linecap="round" opacity="0.16"/>'
    '<path d="M 100.20300883100563 324.24162126553847 A 182.8683602920326 29.25893764672522 0 0 1 100.20300883100555 290.67714689188625" fill="none" stroke="#1f6feb" stroke-width="3.69" stroke-linecap="round" opacity="0.6"/>'
    '<path d="M 72.15709581854259 321.33774888103113 A 197.8683602920326 31.658937646725217 0 0 1 72.15709581854256 293.58101927639353" fill="none" stroke="#1f6feb" stroke-width="2.88" stroke-linecap="round" opacity="0.34"/>'
    '<path d="M 46.432974658676244 317.4172537395308 A 212.8683602920326 34.05893764672522 0 0 1 46.432974658676244 297.5015144178939" fill="none" stroke="#1f6feb" stroke-width="2.07" stroke-linecap="round" opacity="0.16"/>'
    '<path d="M 91.90365545222463 267.7120403545203 A 193 30.88 0 0 1 91.90365545222454 232.2879596454797" fill="none" stroke="#1f6feb" stroke-width="3.69" stroke-linecap="round" opacity="0.6"/>'
    '<path d="M 63.05083836977326 264.5889917651405 A 208 33.28 0 0 1 63.05083836977323 235.4110082348595" fill="none" stroke="#1f6feb" stroke-width="2.88" stroke-linecap="round" opacity="0.34"/>'
    '<path d="M 36.7440394202431 260.43182242450723 A 223 35.68 0 0 1 36.74403942024307 239.56817757549277" fill="none" stroke="#1f6feb" stroke-width="2.07" stroke-linecap="round" opacity="0.16"/>'
    '<path d="M 100.20300883100563 209.3228531081138 A 182.8683602920326 29.25893764672522 0 0 1 100.20300883100555 175.75837873446156" fill="none" stroke="#1f6feb" stroke-width="3.69" stroke-linecap="round" opacity="0.6"/>'
    '<path d="M 72.15709581854259 206.4189807236065 A 197.8683602920326 31.658937646725217 0 0 1 72.15709581854256 178.66225111896884" fill="none" stroke="#1f6feb" stroke-width="2.88" stroke-linecap="round" opacity="0.34"/>'
    '<path d="M 46.432974658676244 202.49848558210613 A 212.8683602920326 34.05893764672522 0 0 1 46.432974658676244 182.58274626046924" fill="none" stroke="#1f6feb" stroke-width="2.07" stroke-linecap="round" opacity="0.16"/>'
    '<path d="M 130.5274226711539 146.68228964368856 A 145.84908645689342 23.33585383310295 0 0 1 130.52742267115383 119.91249788208839" fill="none" stroke="#1f6feb" stroke-width="3.69" stroke-linecap="round" opacity="0.6"/>'
    '<path d="M 105.4297987398842 144.57924952130188 A 160.84908645689342 25.735853833102947 0 0 1 105.4297987398842 122.01553800447508" fill="none" stroke="#1f6feb" stroke-width="2.88" stroke-linecap="round" opacity="0.34"/>'
    '<path d="M 81.83468228951781 141.52352131190253 A 175.84908645689342 28.135853833102946 0 0 1 81.83468228951781 125.07126621387442" fill="none" stroke="#1f6feb" stroke-width="2.07" stroke-linecap="round" opacity="0.16"/>'
    '<circle cx="250" cy="250" r="168" fill="url(#g1732985003_lit)"/>'
    '<g clip-path="url(#g1732985003_clip)">'
    '<line x1="250" y1="82" x2="250" y2="418" stroke="#1f6feb" stroke-width="3.5" opacity="0.79"/>'
    '<ellipse cx="250" cy="250" rx="50.4" ry="168" fill="none" stroke="#1f6feb" stroke-width="3.5" opacity="0.79"/>'
    '<ellipse cx="250" cy="250" rx="104.16" ry="168" fill="none" stroke="#1f6feb" stroke-width="3.5" opacity="0.79"/>'
    '<ellipse cx="250" cy="250" rx="168" ry="26.88" fill="none" stroke="#1f6feb" stroke-width="3.5" opacity="0.79"/>'
    '<ellipse cx="250" cy="398.3351956002997" rx="78.87122254802966" ry="12.619395607684746" fill="none" stroke="#1f6feb" stroke-width="3.5" opacity="0.79"/>'
    '<ellipse cx="250" cy="353.43112785471055" rx="132.3858066059293" ry="21.18172905694869" fill="none" stroke="#1f6feb" stroke-width="3.5" opacity="0.79"/>'
    '<ellipse cx="250" cy="296.3070757772559" rx="161.49196491763757" ry="25.838714386822012" fill="none" stroke="#1f6feb" stroke-width="3.5" opacity="0.79"/>'
    '<ellipse cx="250" cy="203.69292422274413" rx="161.49196491763757" ry="25.838714386822012" fill="none" stroke="#1f6feb" stroke-width="3.5" opacity="0.79"/>'
    '<ellipse cx="250" cy="146.56887214528942" rx="132.3858066059293" ry="21.18172905694869" fill="none" stroke="#1f6feb" stroke-width="3.5" opacity="0.79"/>'
    '<ellipse cx="250" cy="101.66480439970027" rx="78.87122254802966" ry="12.619395607684746" fill="none" stroke="#1f6feb" stroke-width="3.5" opacity="0.79"/>'
    '</g></g>'
    '<circle cx="250" cy="250" r="168" fill="none" stroke="#1f6feb" stroke-width="5"/>'
    '<path d="M 92.1316397079674 192.54061592128767 A 168 168 0 0 1 307.4593840787122 92.13163970796737" fill="none" stroke="rgba(31, 111, 235, 0.95)" stroke-width="6.5" stroke-linecap="round" opacity="0.4"/>'
)

# Disc that encloses the globe + swooshes with a small cream border. The
# content is slightly off-centre (swooshes extend left), so the disc centre is
# nudged left of the globe centre to balance the margin.
DISC_CX, DISC_CY, DISC_R = 228, 250, 207


def swoosh_disc_svg():
    """Circular cream disc with the full globe+swoosh mark, transparent corners."""
    return (
        '<svg viewBox="0 0 500 500" xmlns="http://www.w3.org/2000/svg">'
        f'<defs>{ORIG_DEFS}'
        f'<clipPath id="qg_disc"><circle cx="{DISC_CX}" cy="{DISC_CY}" '
        f'r="{DISC_R}"/></clipPath></defs>'
        f'<circle cx="{DISC_CX}" cy="{DISC_CY}" r="{DISC_R}" '
        'fill="url(#g1732985003_bg)"/>'
        f'<g clip-path="url(#qg_disc)">{ORIG_BODY}</g>'
        '</svg>'
    )


def swoosh_square_svg():
    """Full mark on a solid cream square — for apple-touch (iOS rounds it)."""
    return (
        '<svg viewBox="0 0 500 500" xmlns="http://www.w3.org/2000/svg">'
        f'<defs>{ORIG_DEFS}</defs>'
        '<rect width="500" height="500" fill="url(#g1732985003_bg)"/>'
        f'{ORIG_BODY}'
        '</svg>'
    )


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
    # Master SVG — circular cream disc with the full globe + motion swooshes,
    # transparent corners. This is the large/canonical mark.
    master = swoosh_disc_svg()
    with open("favicon.svg", "w") as fh:
        fh.write('<?xml version="1.0" encoding="UTF-8"?>\n' + master + "\n")
    print("  favicon.svg  (master, circular, with swooshes)")

    # Large PWA rasters use the swoosh mark too.
    render_png(master, "android-chrome-192x192.png", 192)
    render_png(master, "android-chrome-512x512.png", 512)

    # Small favicons: clean bold globe (no swooshes — they'd muddy at this
    # size). Bolder strokes / sparser grid so the rings survive in a tab.
    small = {
        16: globe_svg(size=512, margin_ratio=0.05, weight=2.4, detail="min"),
        32: globe_svg(size=512, margin_ratio=0.05, weight=1.6, detail="full"),
        48: globe_svg(size=512, margin_ratio=0.05, weight=1.3, detail="full"),
    }
    for px in (16, 32, 48):
        render_png(small[px], f"favicon-{px}x{px}.png", px)

    # favicon.ico (multi-resolution from the clean small PNGs).
    sizes = [16, 32, 48]
    imgs = [Image.open(f"favicon-{s}x{s}.png").convert("RGBA") for s in sizes]
    imgs[0].save("favicon.ico", format="ICO", sizes=[(s, s) for s in sizes])
    print("  favicon.ico  (16/32/48, clean)")

    # apple-touch-icon: full swoosh mark on a solid cream square (no alpha) so
    # iOS's rounded-square mask has clean corners.
    render_flat_png(swoosh_square_svg(), "apple-touch-icon.png", 180, PAPER_SOLID)


if __name__ == "__main__":
    main()
