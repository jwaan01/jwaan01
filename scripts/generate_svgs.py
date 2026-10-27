#!/usr/bin/env python3
"""Generate the animated SVGs used by the profile README.

Visual language: the "Hỏa Tuyến" design system (colour manga, shonen style:
sharp ink, diagonal koma panels, hard shadows, screentone, focus/speed lines,
SFX lettering) with crimson red as the primary colour.

Edit the CONTENT section, then run:  python3 scripts/generate_svgs.py
Requires: pip install fonttools brotli   (fonts are subset and embedded so
GitHub renders them inside its <img> sandbox).
"""
import base64
import io
import math
import random
import re
from html import escape, unescape
from pathlib import Path

from fontTools import subset
from fontTools.pens.boundsPen import BoundsPen
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent
OUT = ROOT.parent / "assets"
FONT_DIR = ROOT / "fonts"

# ----------------------------------------------------------------------------
# CONTENT
# ----------------------------------------------------------------------------
HANDLE = "JWAAN01"
REAL_NAME = ("QUAN", "HUYNH")
ROLES = [
    "Building premium web products for clients",
    "React · Node.js · Python · Docker",
    "From idea to deployment, clean architecture",
    "Fast, responsive, maintainable systems",
]
BUBBLE = [
    "I deliver full-stack products for real clients.",
    "React on the front, Node.js on the back —",
    "fast, responsive and built to be maintained.",
]
LANGUAGES = ["C", "C++", "C#", "Java", "JavaScript", "Python"]
TECH = ["React", "Node.js", "Python", "JavaScript", "Java", "C#", "C++",
        "C", "HTML", "CSS", "Docker", "Git", "GitHub", "VS Code"]
SERVICES = [
    ("Business Websites", ["Landing pages, company", "sites, conversion UX"], "globe"),
    ("Dashboards & Admin", ["Internal tools, analytics,", "workflow control"], "chart"),
    ("E-commerce Systems", ["Catalog, cart, checkout,", "order processing"], "cart"),
    ("API Integrations & Automation", ["Payments, third-party APIs,", "custom workflow automation"], "plug"),
    ("Performance & Refactoring", ["Speed optimization,", "maintainability, code cleanup"], "bolt"),
]
CONTACTS = [
    ("GitHub", "github.com/jwaan01"),
    ("Email", "aovkiz123@gmail.com"),
    ("LinkedIn", "Quan Huynh"),
]

# ----------------------------------------------------------------------------
# DESIGN TOKENS (Hỏa Tuyến, crimson as primary instead of blaze)
# ----------------------------------------------------------------------------
RED = "#e3203b"        # primary: text on it is white
RED_DEEP = "#b3121f"   # pressed / emphasis on paper
INK = "#0f0f14"
INK_MUTED = "#5a5a66"
PAPER = "#fbf8f1"
PAPER_2 = "#efeadf"
VOLT = "#ffd60a"       # SFX, combo, accents on night
NIGHT = "#16181f"
SLATE = "#2a2e38"
WHITE = "#ffffff"

FONTS = {
    # class: (family, file, weight, style)
    "sfx": ("HTSfx", "DelaGothicOne-Regular.woff2", 400, "normal"),
    "hd": ("HTHead", "BarlowCondensed-BlackItalic.woff2", 900, "italic"),
    "lb": ("HTLabel", "BarlowCondensed-ExtraBold.woff2", 800, "normal"),
    "bd": ("HTBody", "BeVietnamPro-Regular.woff2", 400, "normal"),
    "bd6": ("HTBodySemi", "BeVietnamPro-SemiBold.woff2", 600, "normal"),
    "dp": ("VDDisplay", "Anton-Regular.woff2", 400, "normal"),  # Vết Đỏ display
}
FALLBACK = {
    "sfx": "'Arial Black', Impact, sans-serif",
    "hd": "'Arial Narrow', Impact, sans-serif",
    "lb": "'Arial Narrow', Arial, sans-serif",
    "bd": "'Segoe UI', Arial, sans-serif",
    "bd6": "'Segoe UI', Arial, sans-serif",
    "dp": "Impact, 'Arial Narrow', sans-serif",
}
REDUCED = "@media (prefers-reduced-motion: reduce){*{animation-duration:0s!important;animation-delay:0s!important;animation-iteration-count:1!important}}"
POP = "cubic-bezier(.2,1.6,.4,1)"
SLAM = "cubic-bezier(.7,0,.2,1)"


_METRICS = {}


def text_width(cls, text, size, spacing=0.0):
    """Exact advance width of `text` in the embedded font (no guessing)."""
    if cls not in _METRICS:
        f = TTFont(FONT_DIR / FONTS[cls][1])
        _METRICS[cls] = (f.getBestCmap(), f["hmtx"].metrics, f["head"].unitsPerEm)
    cmap, hmtx, upm = _METRICS[cls]
    if cls in ("hd",):
        text = text.upper()
    if cls == "lb":
        text = text.upper()
        spacing = spacing or 2.0
    adv = sum(hmtx[cmap.get(ord(c), cmap[ord("?")])][0] for c in text)
    return adv * size / upm + spacing * max(len(text) - 1, 0)


_INK = {}


def ink_fractions(cls, text):
    """How much of the browser's line box above/below is empty (no ink).

    Lets the layout check compare real glyph extents instead of line boxes.
    """
    if cls not in _INK:
        f = TTFont(FONT_DIR / FONTS[cls][1])
        os2 = f["OS/2"]
        if os2.fsSelection & 128:
            asc, desc = os2.sTypoAscender, os2.sTypoDescender
        else:
            asc, desc = f["hhea"].ascent, f["hhea"].descent
        gs = f.getGlyphSet()
        _INK[cls] = (f.getBestCmap(), gs, asc, desc, {})
    cmap, gs, asc, desc, cache = _INK[cls]
    if cls in ("hd", "lb"):
        text = text.upper()
    top, bot = desc, asc
    for c in set(text) - {" "}:
        if c not in cache:
            pen = BoundsPen(gs)
            gs[cmap[ord(c)]].draw(pen)
            cache[c] = pen.bounds
        if cache[c]:
            bot, top = min(bot, cache[c][1]), max(top, cache[c][3])
    span = asc - desc
    return (asc - top) / span, (bot - desc) / span


def fit(cls, text, max_w, size, spacing=0.0):
    """Largest font size <= size whose text fits in max_w."""
    while size > 8 and text_width(cls, text, size, spacing) > max_w:
        size -= 0.5
    return size


SFX_TRACK = 0.05  # Dela Gothic sets glyphs touching; open it so ink strokes never cut a neighbour


def sfx_w(text, size):
    """Visible width of SFX lettering incl. skew and white outer stroke."""
    return text_width("sfx", text, size, size * SFX_TRACK) + size * 0.14 + size * 0.24


def e(s):
    return escape(s, quote=True)


def pts(*xy):
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in xy)


def para(x, y, w, h, sk):
    """Parallelogram leaning right, the system's basic cut."""
    return [(x + sk, y), (x + w, y), (x + w - sk, y + h), (x, y + h)]


def koma(points, fill, sw=5, sh=7, cls="", style=""):
    """Ink-outlined block with a hard, unblurred shadow."""
    p = pts(*points)
    shadow = f'<polygon points="{p}" fill="{INK}" transform="translate({sh} {sh})"/>' if sh else ""
    c = f' class="{cls}"' if cls else ""
    s = f' style="{style}"' if style else ""
    return (f'<g{c}{s}>{shadow}<polygon points="{p}" fill="{fill}" stroke="{INK}" '
            f'stroke-width="{sw}" stroke-linejoin="miter"/></g>')


def sfx(x, y, text, size, fill, s1=None, rotate=0, anchor="start", inner_cls="", alt="", box=None):
    """SFX lettering: inner ink stroke (~10% of size), outer white stroke 2.4x."""
    s1 = s1 or round(size * 0.1, 1)
    t = e(text)
    a = f'text-anchor="{anchor}"'
    ic = f' class="{inner_cls}"' if inner_cls else ""
    alt = f' data-alt="{alt}"' if alt else ""
    if box:
        alt += f' data-box="{" ".join(f"{v:.0f}" for v in box)}"'
    return (
        f'<g transform="translate({x} {y}) rotate({rotate}) skewX(-8)"><g{ic}>'
        f'<text {a} class="sfx" font-size="{size}" letter-spacing="{size * SFX_TRACK:.1f}" fill="{WHITE}" stroke="{WHITE}" stroke-width="{s1 * 2.4:.1f}" stroke-linejoin="round" data-pad="{s1 * 1.2:.1f}"{alt}>{t}</text>'
        f'<text {a} class="sfx" font-size="{size}" letter-spacing="{size * SFX_TRACK:.1f}" fill="{fill}" stroke="{INK}" stroke-width="{s1}" stroke-linejoin="round" paint-order="stroke" data-dup="1">{t}</text>'
        f"</g></g>"
    )


def focus_lines(cx, cy, r_in, r_out, n, color, seed=1):
    rnd = random.Random(seed)
    d = []
    for i in range(n):
        a = 2 * math.pi * i / n + rnd.uniform(-0.02, 0.02)
        da = math.radians(rnd.uniform(0.35, 1.5))
        ri = r_in * rnd.uniform(0.85, 1.6)
        x0, y0 = cx + ri * math.cos(a), cy + ri * math.sin(a)
        x1, y1 = cx + r_out * math.cos(a - da), cy + r_out * math.sin(a - da)
        x2, y2 = cx + r_out * math.cos(a + da), cy + r_out * math.sin(a + da)
        d.append(f"M{x0:.1f} {y0:.1f}L{x1:.1f} {y1:.1f}L{x2:.1f} {y2:.1f}Z")
    return f'<path d="{"".join(d)}" fill="{color}"/>'


def speed_lines(x, y, w, h, n, color, seed=2, cls="spd"):
    rnd = random.Random(seed)
    out = []
    for _ in range(n):
        yy = rnd.uniform(y, y + h)
        ln = rnd.uniform(w * 0.2, w * 0.6)
        th = rnd.choice([1.2, 1.6, 2.4, 3.2])
        xx = rnd.uniform(x, x + w - ln)
        out.append(
            f'<rect x="{xx:.0f}" y="{yy:.0f}" width="{ln:.0f}" height="{th}" fill="{color}" class="{cls}" '
            f'style="animation-delay:-{rnd.uniform(0, 1.2):.2f}s;animation-duration:{rnd.uniform(.7, 1.3):.2f}s"/>'
        )
    return "".join(out)


def burst(cx, cy, r_out, r_in, spikes, fill, seed=3):
    rnd = random.Random(seed)
    p = []
    for i in range(spikes * 2):
        a = math.pi * i / spikes - math.pi / 2
        r = r_out * rnd.uniform(0.86, 1.08) if i % 2 == 0 else r_in * rnd.uniform(0.92, 1.05)
        p.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return koma(p, fill, 5, 7)


TONE_DEFS = (
    f'<pattern id="tone" width="7" height="7" patternUnits="userSpaceOnUse"><circle cx="3.5" cy="3.5" r="1.3" fill="{INK}"/></pattern>'
    f'<pattern id="toneW" width="7" height="7" patternUnits="userSpaceOnUse"><circle cx="3.5" cy="3.5" r="1.3" fill="{WHITE}"/></pattern>'
    f'<pattern id="toneF" width="5" height="5" patternUnits="userSpaceOnUse"><circle cx="2.5" cy="2.5" r=".9" fill="{INK}"/></pattern>'
    '<linearGradient id="fadeUp" x1="0" y1="1" x2="0" y2="0"><stop stop-color="#fff"/><stop offset=".75" stop-color="#fff" stop-opacity="0"/></linearGradient>'
)

BASE_CSS = f"""
.sfx{{font-family:HTSfx,{FALLBACK['sfx']}}}
.hd{{font-family:HTHead,{FALLBACK['hd']};font-weight:900;font-style:italic;text-transform:uppercase}}
.lb{{font-family:HTLabel,{FALLBACK['lb']};font-weight:800;text-transform:uppercase;letter-spacing:2px}}
.bd{{font-family:HTBody,{FALLBACK['bd']};font-weight:400}}
.bd6{{font-family:HTBodySemi,{FALLBACK['bd6']};font-weight:600}}
.dp{{font-family:VDDisplay,{FALLBACK['dp']};font-weight:400}}
.fb{{transform-box:fill-box;transform-origin:center}}
.spd{{animation:spd linear infinite}}
@keyframes spd{{from{{transform:translateX(160px);opacity:0}}20%{{opacity:1}}to{{transform:translateX(-220px);opacity:0}}}}
.jit{{animation:jit .32s steps(1) infinite}}
@keyframes jit{{0%{{transform:translate(0,0)}}25%{{transform:translate(2px,-1px)}}50%{{transform:translate(-1px,2px)}}75%{{transform:translate(-2px,-1px)}}}}
.spin{{transform-box:fill-box;transform-origin:center;animation:spin 40s linear infinite}}
@keyframes spin{{to{{transform:rotate(360deg)}}}}
.flick{{animation:flick 1.6s steps(2) infinite}}
@keyframes flick{{50%{{opacity:.55}}}}
.blink{{animation:blink 1s steps(1) infinite}}
@keyframes blink{{50%{{opacity:.15}}}}
@keyframes pop{{from{{opacity:0;transform:scale(1.6)}}to{{opacity:1;transform:scale(1)}}}}
@keyframes stamp{{0%{{opacity:0;transform:scale(2.2) rotate(-6deg)}}60%{{opacity:1;transform:scale(.94)}}100%{{opacity:1;transform:none}}}}
@keyframes slamL{{from{{transform:translateX(-120%)}}to{{transform:none}}}}
@keyframes slamR{{from{{transform:translateX(110%)}}to{{transform:none}}}}
@keyframes rise{{from{{opacity:0;transform:translateY(26px)}}to{{opacity:1;transform:none}}}}
@keyframes shake{{0%,100%{{transform:none}}20%{{transform:translate(-6px,3px)}}40%{{transform:translate(5px,-4px)}}60%{{transform:translate(-3px,2px)}}80%{{transform:translate(2px,-1px)}}}}
"""


def font_css(body):
    """Subset each font used in `body` to exactly the characters drawn."""
    chars = set(" ")
    for m in re.findall(r">([^<>]+)<", body):
        t = unescape(m)
        chars |= set(t) | set(t.upper()) | set(t.lower())
    rules = []
    for cls, (family, file, weight, style) in FONTS.items():
        if not re.search(rf'class="(?:[^"]* )?{cls}(?: [^"]*)?"', body):
            continue
        font = TTFont(FONT_DIR / file)
        cmap = font.getBestCmap()
        used = set()
        for m in re.findall(rf'class="(?:[^"]* )?{cls}(?: [^"]*)?"[^>]*>([^<]+)<', body):
            t = unescape(m)
            used |= set(t.upper() if cls in ("hd", "lb") else t)
        missing = sorted(c for c in used if ord(c) not in cmap)
        assert not missing, f"{file} has no glyph for {missing}"
        opts = subset.Options()
        opts.flavor = "woff2"
        opts.hinting = False
        opts.desubroutinize = True
        opts.name_IDs = []
        opts.notdef_outline = True
        sub = subset.Subsetter(opts)
        sub.populate(unicodes=[ord(c) for c in chars])
        sub.subset(font)
        buf = io.BytesIO()
        font.flavor = "woff2"
        font.save(buf)
        b64 = base64.b64encode(buf.getvalue()).decode()
        rules.append(
            f"@font-face{{font-family:{family};font-weight:{weight};font-style:{style};"
            f"src:url(data:font/woff2;base64,{b64}) format('woff2')}}"
        )
    return "".join(rules)


def _tag_ink(m):
    attrs, cls, text = m.group(1), m.group(2), m.group(3)
    ti, bi = ink_fractions(cls, unescape(text))
    return f'<text {attrs} data-ink="{ti:.3f} {bi:.3f}">{text}</text>'


def svg(w, h, label, body, css, defs=""):
    body = re.sub(r'<text ([^>]*class="(sfx|hd|lb|bd6|bd|dp)\b[^"]*"[^>]*)>([^<]*)</text>', _tag_ink, body)
    return (
        f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" fill="none" '
        f'xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{e(label)}">\n'
        f"<title>{e(label)}</title>\n"
        f"<style>{font_css(body)}\n{BASE_CSS}\n{css}\n{REDUCED}</style>\n"
        f"<defs>{TONE_DEFS}{defs}</defs>\n{body}\n</svg>\n"
    )


def page(w, h, inner):
    """A manga page: paper, fine tone, heavy panel frame."""
    return (
        f'<rect width="{w}" height="{h}" fill="{PAPER}"/>'
        f'{inner}'
        f'<rect x="3" y="3" width="{w - 6}" height="{h - 6}" stroke="{PAPER}" stroke-width="6"/>'
        f'<rect x="9.5" y="9.5" width="{w - 19}" height="{h - 19}" stroke="{INK}" stroke-width="7"/>'
    )


def chapter_tag(x, y, text, fill=INK, color=VOLT, cls=""):
    w = text_width("lb", text, 17) + 40
    c = f' class="{cls}"' if cls else ""
    return (
        f'<g{c}><polygon points="{pts(*para(x, y, w, 30, 8))}" fill="{fill}"/>'
        f'<text x="{x + w / 2:.0f}" y="{y + 21}" text-anchor="middle" class="lb" font-size="17" fill="{color}" data-box="{x + 8} {y} {x + w - 8} {y + 30}">{e(text)}</text></g>'
    )


# ----------------------------------------------------------------------------
# ICONS (filled, Phosphor-like silhouettes drawn on a 32px grid, centred)
# ----------------------------------------------------------------------------
ICONS = {
    "globe": '<circle r="13" fill="none" stroke="currentColor" stroke-width="3.5"/><ellipse rx="5.5" ry="13" fill="none" stroke="currentColor" stroke-width="3"/><path d="M-13 0H13M-11 -6.5H11M-11 6.5H11" stroke="currentColor" stroke-width="2.6"/>',
    "chart": '<path d="M-14 13H14" stroke="currentColor" stroke-width="3.5"/><rect x="-12" y="-1" width="6" height="12" fill="currentColor"/><rect x="-3" y="-8" width="6" height="19" fill="currentColor"/><rect x="6" y="-14" width="6" height="25" fill="currentColor"/>',
    "cart": '<path d="M-15 -12H-9L-4 7H10L14 -6H-7" fill="none" stroke="currentColor" stroke-width="3.5" stroke-linejoin="round"/><path d="M-6 -6H14L10 7H-4Z" fill="currentColor"/><circle cx="-2" cy="12.5" r="3" fill="currentColor"/><circle cx="8" cy="12.5" r="3" fill="currentColor"/>',
    "plug": '<path d="M-6 -15V-6M6 -15V-6" stroke="currentColor" stroke-width="4" stroke-linecap="round"/><path d="M-11 -7H11V0A11 11 0 0 1 -11 0Z" fill="currentColor"/><path d="M0 9V15" stroke="currentColor" stroke-width="4" stroke-linecap="round"/>',
    "bolt": '<path d="M3 -16L-11 2H-1L-4 16L11 -3H1Z" fill="currentColor"/>',
}


def icon(name, x, y, color, scale=1.0):
    return f'<g transform="translate({x} {y}) scale({scale})" color="{color}">{ICONS[name]}</g>'


# ----------------------------------------------------------------------------
# CH.0 — HERO / TITLE SCREEN
# ----------------------------------------------------------------------------
def hero():
    W, H = 1000, 400
    slab = [(590, 0), (W, 0), (W, H), (505, H)]
    edge = [(578, 0), (W, 0), (W, H), (493, H)]
    role_size = min(fit("bd6", r, 400, 19) for r in ROLES)
    name_size = 84
    while sfx_w(HANDLE, name_size) > 470:
        name_size -= 1
    sub_size = fit("hd", "Freelance Full-Stack Developer", 440, 31, 1)
    tag_w = text_width("lb", "Available for freelance", 18) + 64
    roles = "".join(
        f'<text x="64" y="299" class="bd6 role" font-size="{role_size}" fill="{INK}" data-alt="role" data-box="54 266 474 316" '
        f'style="animation-delay:{1.6 + i * 3}s">{e(r)}</text>'
        for i, r in enumerate(ROLES)
    )
    cyc = len(ROLES) * 3
    n = len(ROLES)
    css = f"""
.slab{{animation:slamR .55s {SLAM} .1s both}}
.name{{animation:pop .45s {POP} .55s both}}
.shk{{animation:impact 6s linear .95s infinite}}
@keyframes impact{{0%,8%,100%{{transform:none}}1.5%{{transform:translate(-7px,4px)}}3%{{transform:translate(6px,-4px)}}4.5%{{transform:translate(-4px,2px)}}6%{{transform:translate(2px,-1px)}}}}
.flash{{opacity:0;animation:flash 6s linear .95s infinite}}
@keyframes flash{{0%{{opacity:.85}}5%,100%{{opacity:0}}}}
.punch{{animation:punch 6s {POP} .95s infinite}}
@keyframes punch{{0%{{transform:scale(1.04) rotate(-1deg)}}6%,100%{{transform:none}}}}
.restamp{{animation:restamp 6s {POP} .95s infinite}}
@keyframes restamp{{0%{{transform:scale(1.25) rotate(8deg)}}7%,100%{{transform:none}}}}
.sub{{animation:rise .5s ease 1s both}}
.box{{animation:rise .5s ease 1.2s both}}
.tag0{{animation:rise .5s ease 1.35s both}}
.bst{{animation:stamp .5s {POP} .9s both}}
.bstb{{animation:beat 1.2s ease-in-out 1.6s infinite}}
@keyframes beat{{0%,100%{{transform:scale(1) rotate(0)}}50%{{transform:scale(1.06) rotate(-2deg)}}}}
.s1{{animation:stamp .45s {POP} 1.3s both}}
.s2{{animation:stamp .45s {POP} 1.55s both}}
.role{{opacity:0;animation:role {cyc}s steps(1) infinite}}
@keyframes role{{0%{{opacity:1}}{100 / n:.2f}%,100%{{opacity:0}}}}
.wipe{{animation:wipe 3s {SLAM} 1.6s infinite}}
@keyframes wipe{{0%{{transform:translateX(0)}}12%,100%{{transform:translateX(520px)}}}}
"""
    body = page(W, H, f"""
<g class="shk">
  <g opacity=".3">{speed_lines(360, 42, 170, 30, 6, INK, 5)}{speed_lines(60, 326, 420, 14, 7, INK, 6)}</g>
  <g class="slab">
    <polygon points="{pts(*edge)}" fill="{INK}"/>
    <polygon points="{pts(*slab)}" fill="{RED}"/>
    <g clip-path="url(#cslab)">
      <g class="spin"><g class="flick" opacity=".55">{focus_lines(790, 200, 130, 620, 120, WHITE, 11)}</g></g>
      <rect x="480" y="0" width="520" height="{H}" fill="url(#tone)" opacity=".35" mask="url(#mfade2)"/>
    </g>
    <rect class="flash" x="480" y="0" width="520" height="{H}" fill="{WHITE}" clip-path="url(#cslab)"/>
    <g class="bst fb"><g class="restamp fb"><g class="bstb fb">
      {burst(790, 200, 132, 92, 15, VOLT, 9)}
      <text x="790" y="226" text-anchor="middle" class="sfx" font-size="{fit("sfx", "</>", 120, 72)}" fill="{INK}" data-box="725 150 855 250">&lt;/&gt;</text>
    </g></g></g>
    <g class="s1 fb"><g class="jit">{sfx(960, 84, "DOOM", 42, WHITE, 5, 8, "end", box=(600, 15, 985, 110))}</g></g>
    <g class="s2 fb"><g class="jit" style="animation-delay:-.16s">{sfx(660, 372, "FULL STACK!!", 32, VOLT, 4, -6, box=(560, 300, 985, 385))}</g></g>
  </g>

  <g class="tag0">
    <polygon points="{pts(*para(44, 40, tag_w, 34, 9))}" fill="{INK}"/>
    <circle cx="68" cy="57" r="6" fill="{VOLT}" class="blink"/>
    <text x="84" y="64" class="lb" font-size="18" fill="{VOLT}" data-box="53 40 {44 + tag_w - 9} 74">Available for freelance</text>
  </g>
  <g class="name fb"><g class="punch fb">{sfx(46, 182, HANDLE, name_size, RED, 9, box=(20, 80, 578 - 85 * 182 / 400 - 12, 215))}</g></g>
  <text x="50" y="232" data-box="20 190 {578 - 85 * 232 / 400 - 20:.0f} 245" class="hd sub" font-size="{sub_size}" fill="{INK}" letter-spacing="1">Freelance Full-Stack Developer</text>
  <g class="box">
    {koma(para(44, 266, 440, 50, 10), WHITE, 5, 6)}
    <g clip-path="url(#cbox)">{roles}<rect class="wipe" x="40" y="268" width="440" height="46" fill="{RED}"/></g>
  </g>
  <text x="48" y="360" class="bd" font-size="15" fill="{INK_MUTED}">Chapter 0 · Quan Huynh · github.com/jwaan01</text>
</g>
""")
    defs = (
        f'<clipPath id="cslab"><polygon points="{pts(*slab)}"/></clipPath>'
        f'<clipPath id="cbox"><polygon points="{pts(*para(47, 269, 434, 44, 10))}"/></clipPath>'
        f'<mask id="mfade"><rect width="540" height="{H}" fill="url(#fadeUp)"/></mask>'
        f'<mask id="mfade2"><rect x="480" width="520" height="{H}" fill="url(#fadeUp)"/></mask>'
    )
    return svg(W, H, f"{HANDLE} — Freelance Full-Stack Developer", body, css, defs)


# ----------------------------------------------------------------------------
# CH.1 — ABOUT (three-panel manga page)
# ----------------------------------------------------------------------------
def about():
    W, H = 1000, 440
    top, bot = 20, H - 20
    ex = lambda y, off=0: 440 - 64 * (y - top) / (bot - top) + off   # A's right edge
    A = [(20, top), (ex(top), top), (ex(bot), bot), (20, bot)]
    mid = 222
    B = [(ex(top, 12), top), (W - 20, top), (W - 20, mid - 5), (ex(mid - 5, 12), mid - 5)]
    C = [(ex(mid + 5, 12), mid + 5), (W - 20, mid + 5), (W - 20, bot), (ex(bot, 12), bot)]

    name_size = 82
    while max(sfx_w(n, name_size) for n in REAL_NAME) > 336:
        name_size -= 1
    eng = "Freelance full-stack engineer"
    eng_size = fit("hd", eng, 290, 23)
    bub_size = min(fit("bd6", t, 370, 17) for t in BUBBLE)
    badge_size = 22
    def badges_w(sz):
        return sum(text_width("hd", l, sz) + 30 for l in LANGUAGES) + 9 * (len(LANGUAGES) - 1)
    while badges_w(badge_size) > (W - 34) - ex(mid + 108, 26):
        badge_size -= .5
    badges = []
    x = ex(mid + 108, 26)
    for i, lang in enumerate(LANGUAGES):
        w = text_width("hd", lang, badge_size) + 30
        fill, col = (RED, WHITE) if i % 2 == 0 else (PAPER, INK)
        badges.append(
            f'<g class="bdg fb" style="animation-delay:{1.7 + i * .14:.2f}s"><g class="hop fb" style="animation-delay:{2.6 + i * .5:.1f}s">'
            f'{koma(para(x, mid + 108, w, 42, 9), fill, 4, 4)}'
            f'<text x="{x + w / 2:.0f}" y="{mid + 137}" data-box="{x + 9} {mid + 108} {x + w - 9} {mid + 150}" text-anchor="middle" class="hd" font-size="{badge_size}" fill="{col}">{e(lang)}</text></g></g>'
        )
        x += w + 9

    lines = "".join(
        f'<g clip-path="url(#ln{i})"><text x="616" y="{96 + i * 26}" data-box="405 48 827 180" text-anchor="middle" class="bd6" font-size="{bub_size}" fill="{INK}">{e(t)}</text></g>'
        for i, t in enumerate(BUBBLE)
    )
    line_clips = "".join(
        f'<clipPath id="ln{i}"><rect x="380" y="{77 + i * 26}" width="480" height="26" class="type" style="animation-delay:{1.1 + i * .55:.2f}s"/></clipPath>'
        for i in range(len(BUBBLE))
    )
    bubble_path = (
        "M616 36 C772 36 848 68 848 116 C848 164 772 196 616 196 C568 196 530 192 500 184 "
        "L450 208 L468 174 C414 160 388 140 388 116 C388 68 460 36 616 36 Z"
    )
    css = f"""
.pa{{animation:slamL .5s {SLAM} .05s both}}
.pb{{animation:slamR .5s {SLAM} .25s both}}
.pc{{animation:slamR .5s {SLAM} .4s both}}
.nm{{animation:stamp .5s {POP} .6s both}}
.bub{{animation:pop .45s {POP} .8s both}}
.bob{{animation:bob 3s ease-in-out 1.4s infinite}}
@keyframes bob{{50%{{transform:translateY(-4px)}}}}
.type{{transform-box:fill-box;transform-origin:left;animation:type .6s steps(24) both}}
@keyframes type{{from{{transform:scaleX(0)}}to{{transform:scaleX(1)}}}}
.bdg{{animation:stamp .4s {POP} both}}
.lv{{animation:stamp .5s {POP} 2.7s both}}
.hop{{animation:hop {len(LANGUAGES) * .5 + 1:.1f}s {POP} infinite}}
@keyframes hop{{0%{{transform:translateY(-10px) scale(1.04) rotate(-2deg)}}10%,100%{{transform:none}}}}
.nmb{{animation:punch2 5s {POP} 3s infinite}}
@keyframes punch2{{0%{{transform:scale(1.025)}}8%,100%{{transform:none}}}}
"""
    body = page(W, H, f"""
<g class="pa">
  {koma(A, RED, 6, 0)}
  <g clip-path="url(#cA)">
    <g class="spin"><g class="flick" opacity=".35">{focus_lines(220, 230, 90, 520, 90, WHITE, 4)}</g></g>
    <rect width="460" height="{H}" fill="url(#tone)" opacity=".3" mask="url(#mA)"/>
  </g>
  {chapter_tag(40, 38, "Chapter 01 · About")}
  <g class="nm fb"><g class="nmb fb">{sfx(40, 170, REAL_NAME[0], name_size, WHITE, 8, box=(22, 76, ex(180) - 10, 200))}{sfx(40, 262, REAL_NAME[1], name_size, VOLT, 8, box=(22, 168, ex(280) - 10, 296))}</g></g>
  <g transform="translate(40 300)">{koma(para(0, 0, 320, 44, 9), INK, 0, 0)}
    <text x="160" y="30" data-box="49 300 351 344" text-anchor="middle" class="hd" font-size="{eng_size}" fill="{WHITE}">{eng}</text></g>
  <text x="44" y="378" class="lb" font-size="15" fill="{WHITE}" opacity=".9">Ships to production</text>
</g>
<g class="pb">
  {koma(B, WHITE, 6, 0)}
  <g clip-path="url(#cB)"><rect x="400" width="600" height="{mid}" fill="url(#toneF)" opacity=".35" mask="url(#mB)"/></g>
  <g class="bub fb"><g class="bob">
    <path d="{bubble_path}" fill="{INK}" transform="translate(6 6)"/>
    <path d="{bubble_path}" fill="{WHITE}" stroke="{INK}" stroke-width="5" stroke-linejoin="round"/>
    <text x="616" y="68" text-anchor="middle" class="lb" font-size="15" fill="{RED_DEEP}">{HANDLE}</text>
    {lines}
  </g></g>
  <g class="lv fb"><g class="jit">{sfx(890, 120, "!!", 64, RED, 6, 10, box=(850, 26, 974, 210))}</g></g>
</g>
<g class="pc">
  {koma(C, NIGHT, 6, 0)}
  <g clip-path="url(#cC)">
    <g opacity=".18">{speed_lines(ex(H - 40, 30), mid + 166, 520, 26, 9, WHITE, 8)}</g>
  </g>
  <text x="{ex(mid + 60, 36):.0f}" y="{mid + 62}" class="lb" font-size="20" fill="{VOLT}">Languages mastered</text>
  <text x="{ex(mid + 60, 36) + text_width("lb", "Languages mastered", 20) + 14:.0f}" y="{mid + 62}" class="bd" font-size="15" fill="{PAPER_2}">— six and counting</text>
  {''.join(badges)}
</g>
""")
    defs = (
        f'<clipPath id="cA"><polygon points="{pts(*A)}"/></clipPath>'
        f'<clipPath id="cB"><polygon points="{pts(*B)}"/></clipPath>'
        f'<clipPath id="cC"><polygon points="{pts(*C)}"/></clipPath>'
        f'<mask id="mA"><rect width="460" height="{H}" fill="url(#fadeUp)"/></mask>'
        f'<mask id="mB"><rect x="400" width="600" height="{mid}" fill="url(#fadeUp)"/></mask>'
        f"{line_clips}"
    )
    return svg(W, H, "About me", body, css, defs)


# ----------------------------------------------------------------------------
# CH.2 — TECH ARSENAL (skill slots + combo counter)
# ----------------------------------------------------------------------------
def tech():
    W, H = 1000, 404
    step, hold = 0.32, 2.6
    T = len(TECH) * step + hold
    pc = lambda s: f"{s / T * 100:.2f}%"
    sw, sh_, gap, sk = 124, 70, 12, 10
    x0 = (W - (7 * sw + 6 * gap)) / 2
    slots, kf = [], []
    for i, name in enumerate(TECH):
        r, c = divmod(i, 7)
        x, y = x0 + c * (sw + gap), 150 + r * (sh_ + 26)
        on = i * step
        kf.append(
            f"@keyframes h{i}{{0%,{pc(on)}{{opacity:0}}{pc(on + .01)},{pc(T - .5)}{{opacity:1}}100%{{opacity:0}}}}"
        )
        size = fit("hd", name, sw - 36, 24)
        slots.append(
            f'<g class="slot fb" style="animation-delay:{.3 + i * .05:.2f}s">'
            f'{koma(para(x, y, sw, sh_, sk), NIGHT, 5, 6)}'
            f'<g style="opacity:0;animation:h{i} {T:.2f}s infinite">'
            f'<polygon points="{pts(*para(x, y, sw, sh_, sk))}" fill="{INK}" transform="translate(6 6)"/>'
            f'<polygon points="{pts(*para(x, y, sw, sh_, sk))}" fill="{RED}" stroke="{INK}" stroke-width="5"/>'
            f'<polygon points="{pts(*para(x, y, sw, sh_, sk))}" fill="url(#toneW)" opacity=".25"/></g>'
            f'<text x="{x + sw / 2:.0f}" y="{y + sh_ / 2 + 8:.0f}" data-box="{x + sk} {y} {x + sw - sk} {y + sh_ - 10}" text-anchor="middle" class="hd" font-size="{size}" fill="{WHITE}">{e(name)}</text>'
            f'<polygon points="{pts(*para(x + sw / 2 - 16, y + sh_ - 8, 32, 18, 5))}" fill="{VOLT}" stroke="{INK}" stroke-width="2.5"/>'
            f'<text x="{x + sw / 2:.0f}" y="{y + sh_ + 6}" text-anchor="middle" class="lb" font-size="13" letter-spacing="0" fill="{INK}">{i + 1:02d}</text>'
            f"</g>"
        )
    counters = []
    for i in range(len(TECH)):
        on, off = i * step, (i + 1) * step if i < len(TECH) - 1 else T - .5
        kf.append(
            f"@keyframes n{i}{{0%,{pc(on)}{{opacity:0}}{pc(on + .01)},{pc(off)}{{opacity:1}}{pc(off + .01)},100%{{opacity:0}}}}"
        )
        counters.append(
            f'<g style="opacity:0;animation:n{i} {T:.2f}s infinite">{sfx(812, 104, str(i + 1), 64, VOLT, 7, -5, "end", alt="cnt", box=(640, 16, 822, 140))}</g>'
        )
    full = len(TECH) * step
    kf.append(f"@keyframes fc{{0%,{pc(full)}{{opacity:0;transform:scale(2)}}{pc(full + .25)},{pc(T - .5)}{{opacity:1;transform:scale(1)}}100%{{opacity:0}}}}")
    css = f"""
.slot{{animation:rise .45s {POP} both}}
.hdr{{animation:slamL .5s {SLAM} both}}
.hl{{transform-box:fill-box;transform-origin:left;animation:hl .5s {SLAM} .35s both}}
@keyframes hl{{from{{transform:scaleX(0)}}to{{transform:scaleX(1)}}}}
.fc{{transform-box:fill-box;transform-origin:center;opacity:0;animation:fc {T:.2f}s infinite}}
{''.join(kf)}
"""
    body = page(W, H, f"""
<rect x="0" y="0" width="{W}" height="{H}" fill="url(#toneF)" opacity=".25" mask="url(#mT)"/>
<g class="hdr">
  {chapter_tag(40, 30, "Chapter 02 · Arsenal")}
  <polygon class="hl" points="{pts(*para(38, 74, text_width("hd", "Tech Arsenal", 50) + 16, 26, 8))}" fill="{RED}"/>
  <text x="44" y="104" class="hd" font-size="50" fill="{INK}">Tech Arsenal</text>
  <text x="{44 + text_width("hd", "Tech Arsenal", 50) + 34:.0f}" y="100" class="bd" font-size="16" fill="{INK_MUTED}">Every slot loaded. Ready to deploy.</text>
</g>
{''.join(counters)}
<g>{sfx(836, 104, "HIT!!", 34, RED, 4, -5, box=(826, 16, 985, 140))}</g>
<g class="fc">{sfx(W / 2, 376, "FULL COMBO!", 30, VOLT, 4, -3, "middle", box=(300, 336, 700, 389))}</g>
{''.join(slots)}
""")
    defs = f'<mask id="mT"><rect width="{W}" height="{H}" fill="url(#fadeUp)"/></mask>'
    return svg(W, H, "Tech arsenal: " + ", ".join(TECH), body, css, defs)


# ----------------------------------------------------------------------------
# CH.3 — SERVICES (koma cards, attract-mode highlight)
# ----------------------------------------------------------------------------
def services():
    W, H = 1000, 450
    T_each = 1.8
    T = T_each * len(SERVICES)
    pc = lambda s: f"{s / T * 100:.2f}%"
    boxes = [(36, 128, 296, 132), (352, 128, 296, 132), (668, 128, 296, 132),
             (36, 286, 454, 132), (510, 286, 454, 132)]
    cards, kf = [], []
    for i, ((title, desc, ic), (x, y, w, h)) in enumerate(zip(SERVICES, boxes)):
        s, en = i * T_each, (i + 1) * T_each
        kf.append(
            f"@keyframes a{i}{{0%,{pc(s)}{{transform:none}}{pc(s + .12)},{pc(en - .1)}{{transform:translate(-4px,-4px)}}{pc(en)},100%{{transform:none}}}}"
            f"@keyframes b{i}{{0%,{pc(s)}{{opacity:0}}{pc(s + .1)},{pc(en - .1)}{{opacity:1}}{pc(en)},100%{{opacity:0}}}}"
        )
        P = para(x, y, w, h, 14)
        dsz = min(fit("bd", d, w - 84 - 30, 15) for d in desc)
        cell = para(x + 18, y + 20, 52, 50, 7)
        anim_a = f"animation:a{i} {T}s ease infinite"
        anim_b = f"opacity:0;animation:b{i} {T}s infinite"
        cards.append(
            f'<g class="card" style="animation-delay:{.25 + i * .12:.2f}s"><g style="{anim_a}">'
            f'<polygon points="{pts(*P)}" fill="{INK}" transform="translate(7 7)"/>'
            f'<polygon points="{pts(*P)}" fill="{INK}" transform="translate(11 11)" style="{anim_b}"/>'
            f'<polygon points="{pts(*P)}" fill="{WHITE}" stroke="{INK}" stroke-width="5"/>'

            f'{koma(cell, INK, 0, 0)}'
            f'<polygon points="{pts(*cell)}" fill="{RED}" style="{anim_b}"/>'
            f'{icon(ic, x + 44, y + 45, WHITE, .85)}'
            f'<text x="{x + 84}" y="{y + 46}" data-box="{x + 80} {y} {x + w - 16} {y + h}" class="hd" font-size="{fit("hd", title, w - 84 - 30, 25)}" fill="{INK}">{e(title.upper())}</text>'
            f'<polygon points="{pts(*para(x + 84, y + 56, 60, 5, 2))}" fill="{RED}"/>'
            f'<text x="{x + 84}" y="{y + 86}" data-box="{x + 74} {y} {x + w - 16} {y + h}" class="bd" font-size="{dsz}" fill="{INK_MUTED}">{e(desc[0])}</text>'
            f'<text x="{x + 84}" y="{y + 108}" data-box="{x + 74} {y} {x + w - 18} {y + h}" class="bd" font-size="{dsz}" fill="{INK_MUTED}">{e(desc[1])}</text>'
            f"</g></g>"
        )
    clips = "".join(f'<clipPath id="cc{i}"><polygon points="{pts(*para(x, y, w, h, 14))}"/></clipPath>'
                    for i, (x, y, w, h) in enumerate(boxes))
    css = f"""
.card{{animation:rise .5s {POP} both}}
.hdr{{animation:slamL .5s {SLAM} both}}
.hl{{transform-box:fill-box;transform-origin:left;animation:hl .5s {SLAM} .35s both}}
@keyframes hl{{from{{transform:scaleX(0)}}to{{transform:scaleX(1)}}}}
.st{{animation:stamp .5s {POP} 1s both}}
{''.join(kf)}
"""
    body = page(W, H, f"""
<g class="hdr">
  {chapter_tag(40, 30, "Chapter 03 · Commissions")}
  <polygon class="hl" points="{pts(*para(38, 74, text_width("hd", "Freelance Services", 50) + 16, 26, 8))}" fill="{RED}"/>
  <text x="44" y="104" class="hd" font-size="50" fill="{INK}">Freelance Services</text>
</g>
<g class="st fb">{sfx(948, 92, "OPEN!", 46, VOLT, 5, 6, "end", box=(700, 15, 985, 122))}</g>
{''.join(cards)}
""")
    return svg(W, H, "Freelance services: " + ", ".join(s[0] for s in SERVICES), body, css, clips)


# ----------------------------------------------------------------------------
# CH.4 — CONTACT (title-screen menu)
# ----------------------------------------------------------------------------
def contact():
    W, H = 1000, 400
    slab = [(640, 0), (W, 0), (W, H), (555, H)]
    edge = [(628, 0), (W, 0), (W, H), (543, H)]
    T_each = 2.2
    T = T_each * len(CONTACTS)
    pc = lambda s: f"{s / T * 100:.2f}%"
    rows, kf = [], []
    vx = 66 + max(text_width("hd", l, 30) for l, _ in CONTACTS) + 28
    vsize = min(fit("bd6", v, 40 + 470 - 30 - (vx + 18), 17) for _, v in CONTACTS)
    for i, (label, value) in enumerate(CONTACTS):
        y = 214 + i * 58
        s, en = i * T_each, (i + 1) * T_each
        kf.append(
            f"@keyframes m{i}{{0%,{pc(s)}{{opacity:0}}{pc(s + .01)},{pc(en)}{{opacity:1}}{pc(en + .01)},100%{{opacity:0}}}}"
            f"@keyframes k{i}{{0%,{pc(s)}{{opacity:1}}{pc(s + .01)},{pc(en)}{{opacity:0}}{pc(en + .01)},100%{{opacity:1}}}}"
        )
        P = para(40, y, 470, 48, 10)
        rows.append(
            f'<g class="row" style="animation-delay:{.9 + i * .15:.2f}s">'
            f'<g style="animation:k{i} {T}s infinite">'
            f'<text x="66" y="{y + 34}" class="hd" font-size="30" fill="{INK}" data-alt="m{i}">{e(label)}</text>'
            f'<text x="{vx}" y="{y + 32}" class="bd" font-size="{vsize}" fill="{INK_MUTED}" data-alt="m{i}">{e(value)}</text></g>'
            f'<g style="opacity:0;animation:m{i} {T}s infinite">'
            f'<polygon points="{pts(*P)}" fill="{INK}" transform="translate(9 9)"/>'
            f'<polygon points="{pts(*P)}" fill="{RED}" stroke="{INK}" stroke-width="5"/>'
            f'<g clip-path="url(#cr{i})" opacity=".35">{speed_lines(vx + 18 + text_width("bd6", value, vsize) + 16, y + 6, 490 - (vx + 18 + text_width("bd6", value, vsize) + 16), 36, 5, WHITE, 40 + i)}</g>'
            f'<path d="M56 {y + 14} L72 {y + 24} L56 {y + 34} Z" fill="{WHITE}"/>'
            f'<text x="84" y="{y + 34}" class="hd" font-size="30" fill="{WHITE}" data-alt="m{i}" data-box="50 {y} 500 {y + 48}">{e(label)}</text>'
            f'<text x="{vx + 18}" y="{y + 32}" class="bd6" font-size="{vsize}" fill="{WHITE}" data-alt="m{i}" data-box="50 {y} 498 {y + 48}">{e(value)}</text></g>'
            f"</g>"
        )
    clips = "".join(f'<clipPath id="cr{i}"><polygon points="{pts(*para(40, 214 + i * 58, 470, 48, 10))}"/></clipPath>'
                    for i in range(len(CONTACTS)))
    css = f"""
.slab{{animation:slamR .55s {SLAM} .1s both}}
.t1{{animation:pop .45s {POP} .45s both}}
.t2{{animation:pop .45s {POP} .65s both}}
.row{{animation:rise .45s ease both}}
.bst{{animation:stamp .5s {POP} 1s both}}
.bstb{{animation:beat 1s ease-in-out 1.6s infinite}}
@keyframes beat{{0%,100%{{transform:scale(1)}}50%{{transform:scale(1.07) rotate(3deg)}}}}
{''.join(kf)}
"""
    body = page(W, H, f"""
<g class="slab">
  <polygon points="{pts(*edge)}" fill="{INK}"/>
  <polygon points="{pts(*slab)}" fill="{RED}"/>
  <g clip-path="url(#cs)">
    <g class="spin"><g class="flick" opacity=".5">{focus_lines(800, 200, 110, 560, 110, WHITE, 21)}</g></g>
    <rect x="540" width="460" height="{H}" fill="url(#tone)" opacity=".35" mask="url(#mS)"/>
  </g>
  <g class="bst fb"><g class="bstb fb">
    {burst(800, 196, 118, 84, 13, VOLT, 31)}
    <text x="800" y="{196 + fit("sfx", "GO!!", 116, 68) * .36:.0f}" text-anchor="middle" class="sfx" font-size="{fit("sfx", "GO!!", 116, 68)}" fill="{INK}" data-box="738 150 862 242">GO!!</text>
  </g></g>
</g>
{chapter_tag(40, 30, "Final Chapter · Contact")}
<g class="t1 fb">{sfx(44, 128, "LET'S BUILD", 58, RED, 6, box=(20, 50, 560, 145))}</g>
<g class="t2 fb">{sfx(44, 188, "SOMETHING!", 46, WHITE, 5, box=(20, 140, 560, 205))}</g>
{''.join(rows)}
""")
    defs = (
        f'<clipPath id="cs"><polygon points="{pts(*slab)}"/></clipPath>'
        f'<mask id="mS"><rect x="540" width="460" height="{H}" fill="url(#fadeUp)"/></mask>'
        f"{clips}"
    )
    return svg(W, H, "Contact: " + ", ".join(f"{a} {b}" for a, b in CONTACTS), body, css, defs)


# ----------------------------------------------------------------------------
# SECTION HEADER for the snake, DIVIDER, FOOTER
# ----------------------------------------------------------------------------
def training_header():
    W, H = 1000, 124
    css = f"""
.hdr{{animation:slamL .5s {SLAM} both}}
.hl{{transform-box:fill-box;transform-origin:left;animation:hl .5s {SLAM} .35s both}}
@keyframes hl{{from{{transform:scaleX(0)}}to{{transform:scaleX(1)}}}}
"""
    body = page(W, H, f"""
<g opacity=".3">{speed_lines(420, 28, 300, 22, 6, INK, 77)}</g>
<g class="hdr">
  {chapter_tag(40, 28, "Chapter 04 · Training Arc")}
  <polygon class="hl" points="{pts(*para(38, 70, text_width("hd", "Daily Training", 44) + 14, 24, 8))}" fill="{RED}"/>
  <text x="44" y="100" class="hd" font-size="44" fill="{INK}">Daily Training</text>
  <text x="{44 + text_width("hd", "Daily Training", 44) + 30:.0f}" y="96" class="bd" font-size="16" fill="{INK_MUTED}">Every commit is a rep. The snake eats them all.</text>
</g>
<g class="jit">{sfx(956, 84, "GRIND", 38, VOLT, 4, -6, "end", box=(700, 15, 985, 109))}</g>
""")
    return svg(W, H, "Training arc: contribution graph", body, css)


def divider():
    W, H = 1000, 36
    css = (
        ".run{animation:run 2.6s cubic-bezier(.7,0,.3,1) infinite}"
        "@keyframes run{from{transform:translateX(-200px)}to{transform:translateX(1100px)}}"
    )
    body = f"""
<polygon points="{pts(*para(0, 6, W, 24, 0))}" fill="{PAPER}" stroke="{INK}" stroke-width="4"/>
<g clip-path="url(#cd)"><g class="run"><polygon points="{pts(*para(0, 8, 180, 20, 10))}" fill="{RED}"/></g></g>
<g transform="translate({W / 2} 18)">{koma(para(-50, -15, 100, 30, 9), VOLT, 4, 4)}</g>
<text x="{W / 2}" y="24" data-box="{W / 2 - 41} 3 {W / 2 + 41} 33" text-anchor="middle" class="lb" font-size="16" fill="{INK}">NEXT</text>
"""
    return svg(W, H, "divider", body, css, f'<clipPath id="cd"><rect x="2" y="8" width="{W - 4}" height="20"/></clipPath>')


def footer():
    W, H = 1000, 170
    arrow = [(60, 58), (640, 58), (640, 34), (720, 90), (640, 146), (640, 122), (60, 122), (84, 90)]
    css = f"""
.arr{{animation:arr 7s {SLAM} infinite}}
@keyframes arr{{0%{{transform:translateX(-780px)}}10%,88%{{transform:none}}100%{{transform:translateX(1100px)}}}}
.push{{animation:push 1.2s ease-in-out infinite}}
@keyframes push{{50%{{transform:translateX(8px)}}}}
.cont{{animation:cont 7s steps(1) infinite}}
@keyframes cont{{0%,12%{{opacity:0}}13%,88%{{opacity:1}}89%,100%{{opacity:0}}}}
"""
    body = page(W, H, f"""
<rect width="{W}" height="{H}" fill="url(#toneF)" opacity=".3" mask="url(#mF)"/>
<g class="arr"><g class="push">
  {koma(arrow, RED, 6, 8)}
  <g clip-path="url(#ca)" opacity=".3">{speed_lines(90, 64, 540, 8, 4, WHITE, 90)}{speed_lines(90, 110, 540, 8, 4, WHITE, 91)}</g>
  <text x="360" y="104" data-box="90 58 640 122" text-anchor="middle" class="hd" font-size="{fit("hd", "To be continued", 470, 42, 3)}" fill="{WHITE}" letter-spacing="3">To be continued</text>
</g></g>
<g class="cont">{sfx(950, 112, "...", 60, VOLT, 6, 0, "end")}</g>
<text x="{W - 40}" y="150" text-anchor="end" class="lb" font-size="14" fill="{INK_MUTED}">Thanks for reading · {HANDLE}</text>
""")
    defs = (
        f'<clipPath id="ca"><polygon points="{pts(*arrow)}"/></clipPath>'
        f'<mask id="mF"><rect width="{W}" height="{H}" fill="url(#fadeUp)"/></mask>'
    )
    return svg(W, H, "To be continued", body, css, defs)


# ----------------------------------------------------------------------------
# INTERLUDE — NIGHT RUN (self-playing endless runner)
# Vết Đỏ night palette (ink / red / white, cyan as a <5% signal) drawn with
# Hỏa Tuyến effects (SFX lettering, speed lines, bursts).
# ----------------------------------------------------------------------------
VD_RED, VD_RED_DEEP = "#e8112d", "#a80a1f"
VD_INK, VD_INK2, VD_INK3 = "#0b0b0d", "#1d1d22", "#2a2a30"
VD_ASH, VD_MUTE, VD_CYAN = "#8a8a93", "#b9b9c2", "#00d2e0"

RUN_EVENTS = [            # (kind, time the obstacle reaches the runner, label)
    ("wall", 2.9, ["DEADLINE"]),
    ("bug", 4.5, None),
    ("coins", 5.9, None),
    ("wall", 7.4, ["MERGE", "CONFLICT"]),
    ("bug", 9.0, None),
    ("coins", 10.3, None),
]


def game():
    W, H = 1000, 340
    GY, RX = 272, 300          # ground line, runner x (clear of the HUD title)
    T, V = 12.0, 360.0         # loop length (s), world speed (px/s)
    X0, X1 = W + 70, -90       # where movers enter / leave
    pc = lambda t: f"{(t % T) / T * 100:.3f}%"
    rnd = random.Random(42)
    css, defs = [], []

    # ---------- parallax city (tiles of exactly W px, drawn twice) ----------
    def skyline(seed, hmin, hmax, fill, windows):
        r = random.Random(seed)
        out, x = [], 0
        while x < W:
            w = r.randint(46, 110)
            w = min(w, W - x) if W - x < 60 else w
            h = r.randint(hmin, hmax)
            out.append(f'<rect x="{x}" y="{GY - h}" width="{w}" height="{h}" fill="{fill}"/>')
            if r.random() < .35:
                out.append(f'<rect x="{x + w // 2 - 2}" y="{GY - h - 18}" width="3" height="18" fill="{fill}"/>')
            if windows:
                out.append(f'<rect x="{x}" y="{GY - h}" width="{w}" height="3" fill="{WHITE}" opacity=".35"/>')
                for wy in range(GY - h + 14, GY - 10, 16):
                    for wx in range(x + 8, x + w - 10, 14):
                        q = r.random()
                        if q < .16:
                            c = VD_CYAN if q < .02 else VD_RED
                            out.append(f'<rect x="{wx}" y="{wy}" width="6" height="8" fill="{c}" opacity=".85"/>')
            x += w + (r.randint(4, 18) if windows else 0)
        g = "".join(out)
        return g + f'<g transform="translate({W} 0)">{g}</g>'

    def layer(content, dur, cls):
        css.append(f".{cls}{{animation:{cls} {dur:.2f}s linear infinite}}"
                   f"@keyframes {cls}{{to{{transform:translateX(-{W}px)}}}}")
        return f'<g class="{cls}">{content}</g>'

    far = layer(skyline(3, 90, 190, "#15151a", False), W / (V * .18), "lyf")
    mid = layer(skyline(8, 50, 130, VD_INK2, True), W / (V * .45), "lym")

    # ---------- ground ----------
    css.append(f".gnd{{animation:gnd {40 / V:.3f}s linear infinite}}@keyframes gnd{{to{{transform:translateX(-40px)}}}}"
               f".mrk{{animation:mrk {160 / V:.3f}s linear infinite}}@keyframes mrk{{to{{transform:translateX(-160px)}}}}")
    defs.append(f'<pattern id="stripe" width="40" height="40" patternUnits="userSpaceOnUse">'
                f'<path d="M-10 40 L18 0 M10 40 L38 0 M30 40 L58 0" stroke="{VD_INK2}" stroke-width="6"/></pattern>')
    marks = "".join(f'<rect x="{x}" y="{GY + 10}" width="44" height="4" fill="{WHITE}" opacity=".5"/>' for x in range(0, W + 200, 160))
    ground = (f'<rect x="0" y="{GY}" width="{W}" height="{H - GY}" fill="{VD_INK}"/>'
              f'<g class="gnd"><rect x="0" y="{GY + 4}" width="{W + 40}" height="{H - GY}" fill="url(#stripe)"/></g>'
              f'<g class="mrk">{marks}</g>'
              f'<rect x="0" y="{GY - 2}" width="{W}" height="4" fill="{WHITE}"/>')

    # ---------- movers (obstacles / enemies / coins) ----------
    movers, run_kf, flip_kf, slash_kf, pops = [], [], [], [], []
    shake_kf, flash_kf = [], []
    jumps, slashes, grabs = [], [], []

    def mover(mid_, t_hit, hit_dx, inner, vanish=False):
        xh = RX + hit_dx
        te = t_hit - (X0 - xh) / V
        travel = (X0 - X1) / V
        p_end = travel / T * 100
        kf = (f"@keyframes mv{mid_}{{0%{{transform:translateX({X0}px)}}{p_end:.3f}%,100%{{transform:translateX({X1}px)}}}}")
        anim = f"mv{mid_} {T}s linear {te - T:.3f}s infinite"
        if vanish:
            p_hit = (t_hit - te) / T * 100
            kf += (f"@keyframes vs{mid_}{{0%,{p_hit:.3f}%{{opacity:1}}{p_hit + .01:.3f}%,100%{{opacity:0}}}}")
            anim += f",vs{mid_} {T}s linear {te - T:.3f}s infinite"
        css.append(kf)
        movers.append(f'<g style="animation:{anim}">{inner}</g>')

    for n, (kind, t, label) in enumerate(RUN_EVENTS):
        if kind == "wall":
            tall = len(label) > 1
            w, h = 84, 74 if tall else 62
            size = min(fit("dp", l, w - 18, 24) for l in label)
            lines = "".join(
                f'<text x="0" y="{-h + 26 + k * 26 if tall else -h / 2 + 10:.0f}" text-anchor="middle" class="dp" font-size="{size}" '
                f'fill="{VD_INK}" data-alt="wall{n}" data-skip="1">{e(l)}</text>' for k, l in enumerate(label))
            inner = (f'<g transform="rotate(-4 0 {-h / 2})">'
                     f'<rect x="{-w / 2 + 7}" y="{-h + 7}" width="{w}" height="{h}" fill="{VD_RED}"/>'
                     f'<rect x="{-w / 2}" y="{-h}" width="{w}" height="{h}" fill="{WHITE}" stroke="{VD_INK}" stroke-width="3"/>{lines}</g>'
                     f'<rect x="-30" y="-6" width="60" height="6" fill="{VD_INK3}"/>')
            mover(n, t, 0, f'<g transform="translate(0 {GY})">{inner}</g>')
            jumps.append((t, tall))
        elif kind == "bug":
            body = (f'<g class="hov">'
                    f'<polygon points="-30,0 -14,-20 14,-20 30,0 14,20 -14,20" fill="{VD_RED}" stroke="{WHITE}" stroke-width="3"/>'
                    f'<rect x="-22" y="-30" width="16" height="4" fill="{WHITE}" class="rot"/><rect x="6" y="-30" width="16" height="4" fill="{WHITE}" class="rot"/>'
                    f'<rect x="-14" y="-6" width="28" height="9" fill="{VD_INK}"/><rect x="2" y="-4" width="8" height="5" fill="{VD_CYAN}" class="blink"/>'
                    f'<text x="0" y="17" text-anchor="middle" class="dp" font-size="11" fill="{WHITE}" data-skip="1" data-alt="bug">BUG</text></g>')
            mover(n, t, 62, f'<g transform="translate(0 {GY - 64})">{body}</g>', vanish=True)
            slashes.append(t)
        else:
            for k in range(3):
                d = (f'<g transform="translate(0 {GY - 40})"><g class="spinc">'
                     f'<polygon points="0,-11 9,0 0,11 -9,0" fill="{VD_CYAN}" stroke="{WHITE}" stroke-width="2"/></g></g>')
                mover(f"{n}_{k}", t + k * .13, 12, d, vanish=True)
                grabs.append(t + k * .13)

    # ---------- runner timeline ----------
    JH = 100
    for t, tall in jumps:
        t0, t1 = t - .34, t + .34
        run_kf += [(t0, "translateY(0)", "cubic-bezier(.2,.7,.4,1)"),
                   (t, f"translateY(-{JH + (10 if tall else 0)}px)", "cubic-bezier(.6,0,.8,.3)"),
                   (t1, "translateY(0)", "linear")]
        if tall:
            flip_kf += [(t0 + .02, "rotate(0deg)", "cubic-bezier(.3,0,.7,1)"), (t1 - .04, "rotate(360deg)", "steps(1)"),
                        (t1 - .03, "rotate(0deg)", "linear")]
        pops.append(("dodge", t))
    for t in slashes:
        ts = t - .06
        slash_kf += [(ts - .1, "rotate(0deg)", "cubic-bezier(.7,0,.3,1)"), (ts + .02, "rotate(225deg)", "linear"),
                     (ts + .22, "rotate(225deg)", "ease-in-out"), (ts + .45, "rotate(0deg)", "linear")]
        shake_kf += [(t - .01, "translate(0,0)"), (t, "translate(-6px,3px)"), (t + .05, "translate(5px,-3px)"), (t + .1, "translate(-3px,2px)"), (t + .16, "translate(0,0)")]
        flash_kf += [(t - .01, "0"), (t, ".22"), (t + .14, "0")]
        pops.append(("slash", t))
    for t in grabs:
        pops.append(("grab", t))

    def kf_block(name, frames, prop="transform", rest="none", eps=.02):
        frames = sorted(frames)
        out = [f"0%{{{prop}:{rest}}}"]
        for item in frames:
            t, v = item[0], item[1]
            tf = f";animation-timing-function:{item[2]}" if len(item) > 2 else ""
            out.append(f"{pc(t)}{{{prop}:{v}{tf}}}")
        out.append(f"100%{{{prop}:{rest}}}")
        return f"@keyframes {name}{{{''.join(out)}}}"

    css.append(kf_block("jump", run_kf, rest="translateY(0)"))
    css.append(kf_block("flip", flip_kf, rest="rotate(0deg)"))
    css.append(kf_block("slash", slash_kf, rest="rotate(0deg)"))
    css.append(kf_block("shk", [(a, b) for a, b in shake_kf]))
    css.append(kf_block("rfl", flash_kf, prop="opacity", rest="0"))
    css.append(f".jmp{{animation:jump {T}s infinite}}.flp{{transform-origin:0px -44px;animation:flip {T}s infinite}}"
               f".sla{{transform-origin:7px -60px;animation:slash {T}s infinite}}.wrld{{animation:shk {T}s infinite}}"
               f".rfl{{opacity:0;animation:rfl {T}s infinite}}")

    # ---------- the runner (geometric ninja silhouette, white outline) ----------
    css.append(".lgA{transform-origin:0px -34px;animation:leg .38s ease-in-out infinite alternate}"
               ".lgB{transform-origin:0px -34px;animation:leg .38s ease-in-out -.38s infinite alternate}"
               "@keyframes leg{from{transform:rotate(-38deg)}to{transform:rotate(34deg)}}"
               ".bob{animation:bob2 .19s ease-in-out infinite alternate}@keyframes bob2{to{transform:translateY(-3px)}}"
               ".hov{animation:hov .6s ease-in-out infinite alternate}@keyframes hov{to{transform:translateY(-6px)}}"
               ".rot{animation:blink .12s steps(1) infinite}"
               ".spinc{animation:spc .8s linear infinite}@keyframes spc{50%{transform:scaleX(.25)}}")

    def body(col, outline=True):
        o = WHITE if outline else col
        ow = 4 if outline else 0
        leg = f'<polyline points="0,-34 5,-17 -2,0 6,0" fill="none" stroke-linecap="square" stroke-linejoin="miter"'
        legs = (f'<g class="lgA">{leg} stroke="{o}" stroke-width="{9 + ow}"/>{leg} stroke="{col}" stroke-width="9"/></g>'
                f'<g class="lgB">{leg} stroke="{o}" stroke-width="{9 + ow}"/>{leg} stroke="{col}" stroke-width="9"/></g>')
        torso = f'<polygon points="-9,-35 10,-35 18,-64 -1,-71" fill="{col}" stroke="{o}" stroke-width="{ow}" stroke-linejoin="miter"/>'
        head = (f'<path d="M1 -76 C1 -90 21 -93 23 -79 C24 -70 16 -67 9 -68 L2 -70 Z" fill="{col}" stroke="{o}" stroke-width="{ow}" stroke-linejoin="round"/>'
                + (f'<polygon points="12,-81 23,-80 22,-76 12,-77" fill="{WHITE}"/>' if outline else ""))
        band = (f'<polygon points="-12,-60 -4,-66 6,-40 -2,-36" fill="{VD_INK2}" stroke="{WHITE}" stroke-width="2"/>' if outline else "")
        arm = (f'<g class="sla"><line x1="7" y1="-60" x2="20" y2="-48" stroke="{o}" stroke-width="{7 + ow}" stroke-linecap="square"/>'
               f'<line x1="7" y1="-60" x2="20" y2="-48" stroke="{col}" stroke-width="7"/>'
               + (f'<line x1="20" y1="-48" x2="-26" y2="-30" stroke="{WHITE}" stroke-width="3.5"/>'
                  f'<line x1="20" y1="-48" x2="12" y2="-45" stroke="{VD_RED}" stroke-width="5"/>' if outline else "")
               + "</g>")
        return f'<g class="bob">{band}{legs}{torso}{head}{arm}</g>'

    scarf = (f'<path fill="{VD_RED}" stroke="{VD_INK}" stroke-width="1.5" d="M3 -70 C-14 -74 -28 -66 -50 -72 L-46 -62 C-28 -58 -14 -64 4 -63 Z">'
             f'<animate attributeName="d" dur=".42s" repeatCount="indefinite" values="'
             f'M3 -70 C-14 -74 -28 -66 -50 -72 L-46 -62 C-28 -58 -14 -64 4 -63 Z;'
             f'M3 -70 C-14 -68 -30 -78 -52 -66 L-46 -58 C-28 -68 -14 -60 4 -63 Z;'
             f'M3 -70 C-14 -74 -28 -66 -50 -72 L-46 -62 C-28 -58 -14 -64 4 -63 Z"/></path>')
    crescent_pts = []
    for k in range(0, 21):
        a = math.radians(-120 + k * 7.5)
        crescent_pts.append((7 + 62 * math.cos(a), -60 + 62 * math.sin(a)))
    for k in range(20, -1, -1):
        a = math.radians(-112 + k * 6.6)
        crescent_pts.append((7 + 46 * math.cos(a) + 6, -60 + 46 * math.sin(a)))
    arc_kf = []
    for t in slashes:
        arc_kf += [(t - .09, "0"), (t - .07, "1"), (t + .12, "0")]
    css.append(kf_block("arc", arc_kf, prop="opacity", rest="0") + f".arc{{opacity:0;animation:arc {T}s infinite}}")
    runner = (
        f'<g transform="translate({RX} {GY}) scale(1.15)"><g class="jmp"><g class="flp">'
        f'<g opacity=".18" transform="translate(-30 0)">{body(VD_RED, False)}</g>'
        f'<g opacity=".38" transform="translate(-15 0)">{body(VD_RED, False)}</g>'
        f'{scarf}<g class="runner-body">{body(VD_INK)}</g>'
        f'<polygon class="arc" points="{pts(*crescent_pts)}" fill="{WHITE}" stroke="{VD_RED}" stroke-width="2"/>'
        f'</g></g></g>'
    )

    rd = random.Random(9)
    dust = "".join(
        f'<rect x="{RX - 8 + rd.uniform(-4, 4):.0f}" y="{GY - 5 - rd.uniform(0, 6):.0f}" width="{rd.choice([3, 4, 5])}" height="3" fill="{WHITE}" class="dst" '
        f'style="animation-delay:-{k * .09:.2f}s"/>' for k in range(6))
    css.append(".dst{animation:dst .54s linear infinite}@keyframes dst{from{transform:translateX(0);opacity:.8}to{transform:translateX(-60px) translateY(-8px);opacity:0}}")
    land_kf = []
    for t, tall in jumps:
        t1 = t + .34
        land_kf += [(t1 - .01, "0"), (t1, "1"), (t1 + .3, "0")]
    css.append(kf_block("land", land_kf, prop="opacity", rest="0") + f".lnd{{opacity:0;animation:land {T}s infinite}}")
    puff = "".join(f'<polygon points="{pts(*para(RX + dx, GY - 10, 22, 8, 4))}" fill="{WHITE}"/>' for dx in (-46, -20, 18))
    effects = f'<g>{dust}</g><g class="lnd">{puff}</g>'
    spark_kf = []
    for t in grabs:
        spark_kf += [(t - .01, "0"), (t, "1"), (t + .12, "0")]
    css.append(kf_block("spk", spark_kf, prop="opacity", rest="0") + f".spk{{opacity:0;animation:spk {T}s infinite}}")
    spark = "".join(
        f'<line x1="{RX + 12 + 10 * math.cos(math.radians(a)):.1f}" y1="{GY - 40 + 10 * math.sin(math.radians(a)):.1f}" '
        f'x2="{RX + 12 + 22 * math.cos(math.radians(a)):.1f}" y2="{GY - 40 + 22 * math.sin(math.radians(a)):.1f}" stroke="{VD_CYAN}" stroke-width="3"/>'
        for a in range(0, 360, 45))
    effects += f'<g class="spk">{spark}</g>'

    # ---------- popups (SFX, score) ----------
    pop_svg = []
    slash_x, slash_y = RX + 190, 134
    for kind, t in pops:
        a, b = t - .02, t + .75
        name = f"p{len(pop_svg)}"
        css.append(f"@keyframes {name}{{0%,{pc(a)}{{opacity:0;transform:translateY(8px) scale(1.4)}}"
                   f"{pc(a + .08)}{{opacity:1;transform:none}}{pc(b - .2)}{{opacity:1;transform:translateY(-14px)}}"
                   f"{pc(b)},100%{{opacity:0;transform:translateY(-20px)}}}}")
        st = f'class="fb" style="opacity:0;animation:{name} {T}s infinite"'
        if kind == "slash":
            pop_svg.append(f'<g {st}>{sfx(slash_x, slash_y, "SLASH!!", 40, WHITE, 4, -6, "middle", alt="slash")}</g>')
            pop_svg.append(f'<g {st}><text x="{RX + 112}" y="{GY - 40}" class="dp" font-size="30" fill="{VD_CYAN}" data-alt="p100">+100</text></g>')
            pop_svg.append(f'<g {st}>{burst(RX + 62, GY - 64, 46, 28, 10, VD_RED, 5)}</g>')
        elif kind == "dodge":
            pop_svg.append(f'<g {st}><g transform="rotate(-4 {RX + 150} 186)">'
                           f'<rect x="{RX + 106}" y="{171}" width="96" height="28" fill="{VD_RED}"/>'
                           f'<rect x="{RX + 100}" y="{165}" width="96" height="28" fill="{WHITE}"/>'
                           f'<text x="{RX + 148}" y="187" text-anchor="middle" class="hd" font-size="20" fill="{VD_INK}" data-alt="dodge">Dodge!</text></g></g>')
        else:
            pop_svg.append(f'<g {st}><text x="{RX + 50}" y="{GY - 94}" class="dp" font-size="20" fill="{VD_CYAN}" data-alt="p10">+10</text></g>')

    # ---------- HUD ----------
    title = "NIGHT RUN"
    tw = text_width("dp", title, 30) + 34
    hud_title = (f'<g transform="rotate(-4 40 40)">'
                 f'<rect x="{38 + 7}" y="{24 + 7}" width="{tw}" height="44" fill="{VD_RED}"/>'
                 f'<rect x="38" y="24" width="{tw}" height="44" fill="{WHITE}"/>'
                 f'<text x="{38 + tw / 2:.0f}" y="58" text-anchor="middle" class="dp" font-size="30" fill="{VD_INK}" data-box="38 18 {38 + tw:.0f} 80">{title}</text></g>'
                 f'<text x="44" y="100" class="hd" font-size="15" letter-spacing="1.5" fill="{VD_MUTE}">Auto-play · Interlude</text>')
    # odometer: N(t) = N0 + t/STEP, each column a rolling strip
    STEP, N0, DIG, CW, DH = .12, 12480, 6, 22, 40
    ox = W - 52 - DIG * CW
    off = N0 * STEP
    cols = []
    for k in range(DIG):
        dur = STEP * 10 ** (k + 1)
        delay = -(off % dur)
        x = ox + (DIG - 1 - k) * CW + CW / 2
        strip = "".join(f'<text x="{x:.0f}" y="{62 + i * DH}" text-anchor="middle" class="dp" font-size="32" fill="{WHITE}" data-skip="1">{i % 10}</text>' for i in range(11))
        css.append(f".od{k}{{animation:odo {dur:.2f}s steps(10) {delay:.2f}s infinite}}")
        cols.append(f'<g clip-path="url(#odw)"><g class="od{k}">{strip}</g></g>')
    css.append(f"@keyframes odo{{to{{transform:translateY(-{10 * DH}px)}}}}")
    defs.append(f'<clipPath id="odw"><rect x="{ox}" y="28" width="{DIG * CW}" height="42"/></clipPath>')
    hud_dist = (f'<polygon points="{pts(*para(ox - 22, 24, DIG * CW + 64, 50, 12))}" fill="{VD_INK2}" stroke="{WHITE}" stroke-width="3"/>'
                f'{"".join(cols)}'
                f'<text x="{ox + DIG * CW + 6}" y="62" class="dp" font-size="18" fill="{VD_RED}">M</text>'
                f'<text x="{ox + DIG * CW + 34}" y="92" text-anchor="end" class="hd" font-size="15" letter-spacing="1.5" fill="{VD_MUTE}">Distance</text>')
    # HP (8 segments) and SP (fills over the loop)
    segs = "".join(f'<polygon points="{pts(*para(88 + i * 22, 300, 18, 16, 5))}" fill="{VD_RED}" stroke="{WHITE}" stroke-width="2"/>' for i in range(8))
    css.append(f".spf{{transform-box:fill-box;transform-origin:left;animation:spf {T / 2}s linear infinite}}"
               f"@keyframes spf{{from{{transform:scaleX(.05)}}90%{{transform:scaleX(1)}}to{{transform:scaleX(1)}}}}"
               f".spm{{animation:spm {T / 2}s steps(1) infinite}}@keyframes spm{{0%{{opacity:0}}90%{{opacity:1}}}}")
    sp_x = W - 300
    hud_bot = (f'<polygon points="{pts(*para(30, 290, 268, 36, 10))}" fill="{VD_INK2}"/>'
               f'<text x="48" y="315" class="hd" font-size="20" fill="{WHITE}">HP</text>{segs}'
               f'<polygon points="{pts(*para(sp_x, 290, 268, 36, 10))}" fill="{VD_INK2}"/>'
               f'<text x="{sp_x + 18}" y="315" class="hd" font-size="20" fill="{VD_CYAN}">SP</text>'
               f'<polygon points="{pts(*para(sp_x + 54, 300, 160, 16, 5))}" fill="{VD_INK}" stroke="{WHITE}" stroke-width="2"/>'
               f'<polygon class="spf" points="{pts(*para(sp_x + 56, 302, 156, 12, 4))}" fill="{VD_CYAN}"/>'
               f'<text x="{sp_x + 222}" y="315" class="hd spm" font-size="18" fill="{VD_CYAN}">MAX</text>')

    # ---------- backdrop: red slash slab, moon, halftone ----------
    defs.append(f'<pattern id="half" width="14" height="14" patternUnits="userSpaceOnUse"><circle cx="7" cy="7" r="4.9" fill="{VD_RED}"/></pattern>'
                f'<linearGradient id="hf" x1="0" y1="0" x2="1" y2="0"><stop stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#fff"/></linearGradient>'
                f'<mask id="hm"><rect x="300" y="0" width="300" height="{GY}" fill="url(#hf)"/></mask>'
                f'<clipPath id="gframe"><rect width="{W}" height="{H}"/></clipPath>')
    css.append(".moon{animation:moon 4s ease-in-out infinite alternate}@keyframes moon{to{transform:translateY(-6px)}}")
    backdrop = (f'<rect width="{W}" height="{H}" fill="{VD_INK}"/>'
                f'<rect x="300" y="0" width="300" height="{GY}" fill="url(#half)" mask="url(#hm)" opacity=".35"/>'
                f'<polygon points="{pts((600, 0), (850, 0), (720, GY), (470, GY))}" fill="{VD_RED}"/>'
                f'<polygon points="{pts((862, 0), (890, 0), (760, GY), (732, GY))}" fill="{VD_RED_DEEP}"/>'
                f'<g class="moon"><circle cx="{709}" cy="{106}" r="44" fill="{VD_INK}"/><circle cx="700" cy="97" r="44" fill="{WHITE}"/></g>')

    body_svg = f"""
<g clip-path="url(#gframe)">
  {backdrop}
  <g class="wrld">
    {far}{mid}
    <g opacity=".14">{speed_lines(0, 120, W, 120, 16, WHITE, 61)}</g>
    {ground}
    {''.join(movers)}
    {effects}
    {runner}
    {''.join(pop_svg)}
  </g>
  <rect class="rfl" width="{W}" height="{H}" fill="{VD_RED}"/>
  {hud_title}{hud_dist}{hud_bot}
  <rect x="2.5" y="2.5" width="{W - 5}" height="{H - 5}" stroke="{WHITE}" stroke-width="5"/>
</g>
"""
    return svg(W, H, "Night Run: a self-playing endless runner. The ninja jumps DEADLINE and MERGE CONFLICT walls, slashes BUG drones and grabs commits.",
               body_svg, "\n".join(css), "".join(defs))


def main():
    OUT.mkdir(exist_ok=True)
    files = {
        "hero.svg": hero(),
        "night-run.svg": game(),
        "about.svg": about(),
        "tech-arsenal.svg": tech(),
        "freelance-services.svg": services(),
        "training-header.svg": training_header(),
        "contact-card.svg": contact(),
        "divider.svg": divider(),
        "footer.svg": footer(),
    }
    for name, content in files.items():
        (OUT / name).write_text(content, encoding="utf-8")
        print(f"wrote assets/{name} ({len(content) // 1024} KB)")


if __name__ == "__main__":
    main()
