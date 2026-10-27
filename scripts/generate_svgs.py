#!/usr/bin/env python3
"""Generate the animated SVGs used by the profile README.

Edit the CONTENT section below, then run:  python3 scripts/generate_svgs.py
Everything is plain SVG + CSS/SMIL animation, so it renders inside GitHub's
<img> sandbox without any external service.
"""
import math
import random
from html import escape
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets"

# ----------------------------------------------------------------------------
# CONTENT
# ----------------------------------------------------------------------------
NAME = "JWAAN01"
TAGLINE = "FREELANCE  FULL-STACK  DEVELOPER"
ROLES = [
    "Building premium web products for clients",
    "React  ·  Node.js  ·  Python  ·  Docker",
    "From idea to deployment with clean architecture",
    "Fast, responsive & maintainable systems",
]

TERMINAL = [
    ("cmd", "whoami"),
    ("out", "Quan Huynh — freelance full-stack engineer"),
    ("cmd", "cat focus.txt"),
    ("out", "Delivering full-stack products for real clients"),
    ("out", "React frontend + Node.js backend, production mindset"),
    ("out", "Fast, responsive, maintainable — clean architecture"),
    ("cmd", "ls ~/languages"),
    ("lang", "C  C++  C#  Java  JavaScript  Python"),
    ("cmd", "status --now"),
    ("ok", "Open for freelance & long-term collaborations"),
]

ORBIT_INNER = ["React", "Node.js", "Python", "Docker"]
ORBIT_OUTER = ["JavaScript", "Java", "C#", "C++", "C", "Git"]
STACK_ROWS = [
    ("Frontend", "#22D3EE", ["React", "JavaScript", "HTML", "CSS"]),
    ("Backend", "#34D399", ["Node.js", "Python", "Java", "C#"]),
    ("Systems", "#A78BFA", ["C", "C++", "Docker", "Git"]),
]

SERVICES = [
    ("Business Websites", "Landing pages, company sites, UX", "#22C55E", "globe"),
    ("Dashboards & Admin", "Internal tools, analytics, workflows", "#3B82F6", "chart"),
    ("E-commerce Systems", "Catalog, cart, checkout, orders", "#A855F7", "cart"),
    ("API Integrations & Automation", "Payments, third-party APIs, custom workflow automation", "#06B6D4", "plug"),
    ("Performance & Refactoring", "Speed optimization, maintainability, code cleanup", "#F97316", "bolt"),
]

CONTACTS = [
    ("GitHub", "github.com/jwaan01", "#3B82F6"),
    ("Email", "aovkiz123@gmail.com", "#22C55E"),
    ("LinkedIn", "Quan Huynh", "#0EA5E9"),
]

# ----------------------------------------------------------------------------
# SHARED
# ----------------------------------------------------------------------------
SANS = "'Segoe UI', Ubuntu, 'Helvetica Neue', Arial, sans-serif"
MONO = "'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace"
REDUCED = "@media (prefers-reduced-motion: reduce){*{animation-duration:0s!important;animation-delay:0s!important}}"


def e(s):
    return escape(s, quote=True)


def svg(w, h, label, body, style):
    return (
        f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" fill="none" '
        f'xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{e(label)}">\n'
        f"<title>{e(label)}</title>\n<style>\n{style}\n{REDUCED}\n</style>\n{body}\n</svg>\n"
    )


def rounded_rect_path(x, y, w, h, r):
    return (
        f"M{x + r},{y} H{x + w - r} A{r},{r} 0 0 1 {x + w},{y + r} V{y + h - r} "
        f"A{r},{r} 0 0 1 {x + w - r},{y + h} H{x + r} A{r},{r} 0 0 1 {x},{y + h - r} "
        f"V{y + r} A{r},{r} 0 0 1 {x + r},{y} Z"
    )


def comet_border(x, y, w, h, r, color, dur, delay):
    """A bright segment that keeps travelling around a rounded border."""
    d = rounded_rect_path(x, y, w, h, r)
    return (
        f'<path d="{d}" stroke="{color}" stroke-opacity="0.28" stroke-width="1.2"/>'
        f'<path d="{d}" pathLength="1000" class="comet" stroke="{color}" stroke-width="2.4" '
        f'stroke-linecap="round" filter="url(#glow)" '
        f'style="animation-duration:{dur}s;animation-delay:{delay}s"/>'
    )


GLOW_FILTER = (
    '<filter id="glow" x="-50%" y="-50%" width="200%" height="200%">'
    '<feGaussianBlur stdDeviation="3" result="b"/>'
    '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
)
COMET_CSS = (
    ".comet{stroke-dasharray:90 910;stroke-dashoffset:1000;"
    "animation:comet linear infinite}"
    "@keyframes comet{to{stroke-dashoffset:0}}"
)

# ----------------------------------------------------------------------------
# HERO
# ----------------------------------------------------------------------------
def hero():
    W, H = 1000, 360
    rnd = random.Random(7)
    cx, horizon = W / 2, 268

    particles = []
    for _ in range(38):
        x, y = rnd.uniform(20, W - 20), rnd.uniform(30, horizon)
        r = rnd.choice([0.8, 1.1, 1.4, 1.8])
        c = rnd.choice(["#67E8F9", "#6EE7B7", "#C4B5FD", "#F9A8D4", "#E2E8F0"])
        particles.append(
            f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r}" fill="{c}" class="pt" '
            f'style="animation-duration:{rnd.uniform(4, 9):.1f}s;animation-delay:-{rnd.uniform(0, 9):.1f}s"/>'
        )

    floor = []
    for i in range(-12, 13):
        floor.append(f'<line x1="{cx}" y1="{horizon}" x2="{cx + i * 95}" y2="{H}"/>')
    for i in range(7):
        floor.append(f'<line x1="0" x2="{W}" y1="{horizon}" y2="{horizon}" class="hl" style="animation-delay:{i * 0.5}s"/>')

    roles = []
    n = len(ROLES)
    for i, text in enumerate(ROLES):
        roles.append(
            f'<text x="{cx}" y="252" text-anchor="middle" class="role" '
            f'style="animation-delay:{3 + i * 3.5}s">{e(text)}</text>'
        )
    cycle = n * 3.5

    # Equalizer bars top-right
    eq = "".join(
        f'<rect x="{900 + i * 7}" y="30" width="4" height="18" rx="1.5" fill="#34D399" class="eq" '
        f'style="animation-delay:-{i * 0.23:.2f}s;animation-duration:{0.8 + (i % 3) * 0.25:.2f}s"/>'
        for i in range(8)
    )

    style = f"""
.name{{font:800 96px {SANS};letter-spacing:14px}}
.draw{{fill:url(#ng);fill-opacity:0;stroke:url(#ng);stroke-width:1.6;stroke-dasharray:420;stroke-dashoffset:420;
  animation:draw 2.4s cubic-bezier(.6,0,.2,1) .3s forwards, fillin 1s ease 2.1s forwards, pulse 4s ease-in-out 3.2s infinite}}
@keyframes draw{{to{{stroke-dashoffset:0}}}}
@keyframes fillin{{to{{fill-opacity:1}}}}
@keyframes pulse{{0%,100%{{filter:drop-shadow(0 0 6px rgba(34,211,238,.35))}}50%{{filter:drop-shadow(0 0 18px rgba(52,211,153,.75))}}}}
.gl{{opacity:0;animation:glitch 6s steps(1) 3.5s infinite}}
.gl2{{animation-delay:3.56s}}
@keyframes glitch{{0%,88%,100%{{opacity:0;transform:none}}89%{{opacity:.75;transform:translate(-6px,1px)}}90%{{opacity:.6;transform:translate(5px,-2px)}}91%{{opacity:.75;transform:translate(-3px,0)}}92%{{opacity:0}}}}
.tag{{font:600 17px {SANS};letter-spacing:7px;fill:#94A3B8;opacity:0;animation:up .9s ease 2.4s forwards}}
@keyframes up{{from{{opacity:0;transform:translateY(12px)}}to{{opacity:1;transform:none}}}}
.role{{font:500 19px {MONO};fill:#A5F3FC;opacity:0;animation:role {cycle}s ease infinite}}
@keyframes role{{0%{{opacity:0;transform:translateY(10px)}}4%,{100 / n - 4:.1f}%{{opacity:1;transform:none}}{100 / n:.1f}%,100%{{opacity:0;transform:translateY(-10px)}}}}
.pt{{animation:float ease-in-out infinite alternate}}
@keyframes float{{from{{transform:translateY(0);opacity:.15}}to{{transform:translateY(-26px);opacity:.9}}}}
.blob{{animation:drift 14s ease-in-out infinite alternate}}
@keyframes drift{{from{{transform:translate(0,0)}}to{{transform:translate(60px,-25px)}}}}
.floor line{{stroke:#22D3EE;stroke-opacity:.18;stroke-width:1}}
.hl{{animation:hl 3.5s cubic-bezier(.55,0,1,.45) infinite;opacity:0}}
@keyframes hl{{0%{{transform:translateY(0);opacity:0}}20%{{opacity:1}}100%{{transform:translateY({H - horizon}px);opacity:1}}}}
.scan{{animation:scan 5s linear infinite}}
@keyframes scan{{from{{transform:translateY(-40px)}}to{{transform:translateY({H + 40}px)}}}}
.hud{{font:600 12px {MONO};letter-spacing:2px;fill:#64748B}}
.dot{{animation:blink 1.6s ease-in-out infinite}}
@keyframes blink{{50%{{opacity:.2}}}}
.ring{{transform-origin:24px 39px;animation:ping 1.6s ease-out infinite}}
@keyframes ping{{from{{transform:scale(1);opacity:.8}}to{{transform:scale(3.2);opacity:0}}}}
.eq{{transform-box:fill-box;transform-origin:bottom;animation:eq ease-in-out infinite alternate}}
@keyframes eq{{from{{transform:scaleY(.2)}}to{{transform:scaleY(1)}}}}
.corner{{stroke:#22D3EE;stroke-width:2;stroke-opacity:.6;fill:none}}
"""

    body = f"""
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="0" y2="{H}" gradientUnits="userSpaceOnUse">
    <stop stop-color="#050816"/><stop offset=".7" stop-color="#0B1430"/><stop offset="1" stop-color="#0F1F3D"/>
  </linearGradient>
  <linearGradient id="ng" x1="0" y1="0" x2="500" y2="0" gradientUnits="userSpaceOnUse" spreadMethod="reflect">
    <stop stop-color="#22D3EE"/><stop offset=".5" stop-color="#34D399"/><stop offset="1" stop-color="#A78BFA"/>
    <animateTransform attributeName="gradientTransform" type="translate" from="0 0" to="1000 0" dur="6s" repeatCount="indefinite"/>
  </linearGradient>
  <linearGradient id="scan" x1="0" y1="0" x2="0" y2="1">
    <stop stop-color="#22D3EE" stop-opacity="0"/><stop offset=".5" stop-color="#22D3EE" stop-opacity=".12"/><stop offset="1" stop-color="#22D3EE" stop-opacity="0"/>
  </linearGradient>
  <linearGradient id="fade" x1="0" y1="{horizon}" x2="0" y2="{H}" gradientUnits="userSpaceOnUse">
    <stop stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#fff"/>
  </linearGradient>
  <mask id="floorMask"><rect x="0" y="{horizon}" width="{W}" height="{H - horizon}" fill="url(#fade)"/></mask>
  <filter id="blur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="55"/></filter>
  <clipPath id="frame"><rect width="{W}" height="{H}" rx="22"/></clipPath>
</defs>
<g clip-path="url(#frame)">
  <rect width="{W}" height="{H}" fill="url(#bg)"/>
  <g filter="url(#blur)" opacity=".55">
    <circle class="blob" cx="230" cy="110" r="130" fill="#0EA5E9"/>
    <circle class="blob" cx="760" cy="90" r="120" fill="#7C3AED" style="animation-delay:-5s;animation-direction:alternate-reverse"/>
    <circle class="blob" cx="520" cy="250" r="110" fill="#10B981" style="animation-delay:-9s"/>
  </g>
  <g>{''.join(particles)}</g>
  <g class="floor" mask="url(#floorMask)">{''.join(floor)}</g>
  <line x1="0" x2="{W}" y1="{horizon}" y2="{horizon}" stroke="#22D3EE" stroke-opacity=".5"/>
  <rect class="scan" x="0" y="0" width="{W}" height="40" fill="url(#scan)"/>

  <g>
    <circle class="ring" cx="24" cy="39" r="5" fill="none" stroke="#34D399"/>
    <circle class="dot" cx="24" cy="39" r="5" fill="#34D399"/>
    <text x="38" y="44" class="hud" fill="#6EE7B7" style="fill:#6EE7B7">AVAILABLE FOR FREELANCE</text>
  </g>
  {eq}
  <text x="{W - 24}" y="66" text-anchor="end" class="hud">SYS.ONLINE</text>
  <path class="corner" d="M14 92 V14 H92"/><path class="corner" d="M{W - 14} {H - 92} V{H - 14} H{W - 92}"/>

  <text x="{cx}" y="168" text-anchor="middle" class="name gl" fill="#F472B6" opacity="0">{NAME}</text>
  <text x="{cx}" y="168" text-anchor="middle" class="name gl gl2" fill="#22D3EE" opacity="0">{NAME}</text>
  <text x="{cx}" y="168" text-anchor="middle" class="name draw">{NAME}</text>
  <text x="{cx}" y="210" text-anchor="middle" class="tag" xml:space="preserve">{e(TAGLINE)}</text>
  {''.join(roles)}
</g>
"""
    return svg(W, H, f"{NAME} — Freelance Full-Stack Developer", body, style)


# ----------------------------------------------------------------------------
# TERMINAL
# ----------------------------------------------------------------------------
def terminal():
    W = 1000
    LH, TOP, X = 34, 92, 40
    H = TOP + LH * len(TERMINAL) + 60
    CW = 10.2  # forced glyph advance via textLength => deterministic typing
    T = 22.0  # full loop length in seconds
    pct = lambda s: f"{s / T * 100:.2f}%"

    rows, keyframes = [], []
    t = 0.8
    for i, (kind, text) in enumerate(TERMINAL):
        y = TOP + i * LH
        if kind == "cmd":
            prompt = "❯"
            px = X + 24
            n = len(text)
            w = n * CW
            dur = 0.07 * n
            start, end = t, t + dur
            k = f"k{i}"
            keyframes.append(
                f"@keyframes {k}{{0%,{pct(start)}{{transform:scaleX(0);animation-timing-function:steps({n},end)}}"
                f"{pct(end)},100%{{transform:scaleX(1)}}}}"
                f"@keyframes c{k}{{0%,{pct(start - 0.3)}{{opacity:0;transform:translateX(0)}}"
                f"{pct(start)}{{opacity:1;transform:translateX(0);animation-timing-function:steps({n},end)}}"
                f"{pct(end)}{{opacity:1;transform:translateX({w}px)}}{pct(end + 0.25)},100%{{opacity:0;transform:translateX({w}px)}}}}"
            )
            rows.append(
                f'<g>'
                f'<text x="{X}" y="{y}" class="mono prompt" style="opacity:0;animation:s{i} {T}s infinite">{prompt}</text>'
                f'<clipPath id="cp{i}"><rect x="{px}" y="{y - 20}" width="{w + 2}" height="28" '
                f'style="transform-origin:{px}px 0;animation:{k} {T}s infinite"/></clipPath>'
                f'<text x="{px}" y="{y}" class="mono cmd" textLength="{w}" lengthAdjust="spacingAndGlyphs" clip-path="url(#cp{i})">{e(text)}</text>'
                f'<rect x="{px + 1}" y="{y - 16}" width="9" height="20" fill="#34D399" '
                f'style="opacity:0;animation:c{k} {T}s infinite"/>'
                f"</g>"
            )
            keyframes.append(
                f"@keyframes s{i}{{0%,{pct(start - .3)}{{opacity:0}}{pct(start - .29)},100%{{opacity:1}}}}"
            )
            t = end + 0.45
        else:
            start = t
            fill = {"out": "#CBD5E1", "lang": "#FBBF24", "ok": "#6EE7B7"}[kind]
            prefix = "●  " if kind == "ok" else ""
            keyframes.append(
                f"@keyframes o{i}{{0%,{pct(start)}{{opacity:0;transform:translateX(-8px)}}"
                f"{pct(start + .25)},100%{{opacity:1;transform:none}}}}"
            )
            rows.append(
                f'<text x="{X + 24}" y="{y}" class="mono" fill="{fill}" xml:space="preserve" '
                f'style="opacity:0;animation:o{i} {T}s ease infinite">{e(prefix + text)}</text>'
            )
            t += 0.35 if kind != "ok" else 0.6
    # final idle prompt with blinking cursor
    fy = TOP + len(TERMINAL) * LH
    keyframes.append(
        f"@keyframes fin{{0%,{pct(t)}{{opacity:0}}{pct(t + .01)},100%{{opacity:1}}}}"
    )
    rows.append(
        f'<g style="opacity:0;animation:fin {T}s infinite">'
        f'<text x="{X}" y="{fy}" class="mono" fill="#34D399">❯</text>'
        f'<rect x="{X + 25}" y="{fy - 16}" width="9" height="20" fill="#34D399" class="blink"/></g>'
    )
    assert t < T - 3, "terminal script is longer than the loop"

    style = f"""
.mono{{font:500 17px {MONO}}}
.prompt{{fill:#34D399}}
.cmd{{fill:#F8FAFC}}
.blink{{animation:blink 1s steps(1) infinite}}
@keyframes blink{{50%{{opacity:0}}}}
.content{{animation:out {T}s infinite}}
@keyframes out{{0%,{pct(T - 1.2)}{{opacity:1}}100%{{opacity:0}}}}
.title{{font:600 13px {MONO};fill:#64748B;letter-spacing:1px}}
.glare{{animation:glare 7s ease-in-out infinite}}
@keyframes glare{{0%{{transform:translateX(-300px)}}60%,100%{{transform:translateX({W + 300}px)}}}}
{''.join(keyframes)}
"""
    body = f"""
<defs>
  <linearGradient id="tb" x1="0" y1="0" x2="{W}" y2="{H}" gradientUnits="userSpaceOnUse">
    <stop stop-color="#0B1220"/><stop offset="1" stop-color="#0F172A"/>
  </linearGradient>
  <linearGradient id="gl" x1="0" y1="0" x2="1" y2="0">
    <stop stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".05"/><stop offset="1" stop-color="#fff" stop-opacity="0"/>
  </linearGradient>
  <clipPath id="win"><rect width="{W}" height="{H}" rx="18"/></clipPath>
  <pattern id="lines" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#fff" fill-opacity=".018"/></pattern>
</defs>
<g clip-path="url(#win)">
  <rect width="{W}" height="{H}" fill="url(#tb)"/>
  <rect width="{W}" height="44" fill="#111827"/>
  <circle cx="26" cy="22" r="7" fill="#EF4444"/><circle cx="50" cy="22" r="7" fill="#F59E0B"/><circle cx="74" cy="22" r="7" fill="#22C55E"/>
  <text x="{W / 2}" y="27" text-anchor="middle" class="title">jwaan01@dev: ~/about-me</text>
  <rect width="{W}" height="{H}" fill="url(#lines)"/>
  <g class="content">{''.join(rows)}</g>
  <rect class="glare" x="0" y="0" width="240" height="{H}" fill="url(#gl)" transform="skewX(-20)"/>
</g>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="18" stroke="#1F2937"/>
"""
    return svg(W, H, "About me terminal", body, style)


# ----------------------------------------------------------------------------
# TECH ORBIT
# ----------------------------------------------------------------------------
def orbit():
    W, H = 1000, 400
    cx, cy = 230, 200
    R1, R2 = 100, 168

    def ring(items, r, cls, offset):
        out = []
        for i, label in enumerate(items):
            a = 2 * math.pi * i / len(items) + offset
            x, y = cx + r * math.cos(a), cy + r * math.sin(a)
            w = 16 + len(label) * 8.6
            out.append(
                f'<g transform="translate({x:.1f} {y:.1f})"><g class="{cls}-c">'
                f'<rect x="{-w / 2:.1f}" y="-14" width="{w:.1f}" height="28" rx="14" fill="#0B1220" stroke="url(#chip)" stroke-width="1.4"/>'
                f'<text y="5" text-anchor="middle" class="chip">{e(label)}</text></g></g>'
            )
        return "".join(out)

    rows = []
    for r, (title, color, items) in enumerate(STACK_ROWS):
        y = 150 + r * 82
        rows.append(
            f'<text x="500" y="{y}" class="cat" fill="{color}" style="animation-delay:{.3 + r * .35:.2f}s">{e(title)}</text>'
            f'<line x1="500" y1="{y + 12}" x2="950" y2="{y + 12}" stroke="{color}" stroke-opacity=".25"/>'
            f'<line x1="500" y1="{y + 12}" x2="950" y2="{y + 12}" stroke="{color}" stroke-width="2" class="bar" '
            f'style="animation-delay:{.4 + r * .35:.2f}s"/>'
        )
        x = 500
        for j, item in enumerate(items):
            w = 22 + len(item) * 8.4
            d = 0.7 + r * 0.35 + j * 0.12
            rows.append(
                f'<g class="pill" style="animation-delay:{d:.2f}s">'
                f'<rect x="{x}" y="{y + 24}" width="{w:.1f}" height="28" rx="8" fill="{color}" fill-opacity=".1" stroke="{color}" stroke-opacity=".55"/>'
                f'<text x="{x + w / 2:.1f}" y="{y + 43}" text-anchor="middle" class="pt">{e(item)}</text></g>'
            )
            x += w + 10

    style = f"""
.r1{{transform-origin:{cx}px {cy}px;animation:spin 24s linear infinite}}
.r2{{transform-origin:{cx}px {cy}px;animation:spin 36s linear infinite reverse}}
.r1-c{{animation:spin 24s linear infinite reverse}}
.r2-c{{animation:spin 36s linear infinite}}
@keyframes spin{{to{{transform:rotate(360deg)}}}}
.chip{{font:600 13px {MONO};fill:#E2E8F0}}
.core{{transform-origin:{cx}px {cy}px;animation:breathe 3s ease-in-out infinite}}
@keyframes breathe{{50%{{transform:scale(1.08)}}}}
.ping{{transform-origin:{cx}px {cy}px;animation:ping 3s ease-out infinite}}
@keyframes ping{{from{{transform:scale(.6);opacity:.7}}to{{transform:scale(2.6);opacity:0}}}}
.track{{stroke-dasharray:4 8;animation:dash 20s linear infinite}}
@keyframes dash{{to{{stroke-dashoffset:-240}}}}
.h{{font:700 30px {SANS};fill:#F1F5F9}}
.sub{{font:400 15px {SANS};fill:#94A3B8}}
.cat{{font:700 15px {MONO};letter-spacing:3px;opacity:0;animation:fadeup .6s ease forwards}}
.bar{{stroke-dasharray:450;stroke-dashoffset:450;animation:bar 1.2s cubic-bezier(.6,0,.2,1) forwards}}
@keyframes bar{{to{{stroke-dashoffset:0}}}}
.pill{{opacity:0;animation:fadeup .5s cubic-bezier(.2,.8,.2,1.2) forwards}}
.pt{{font:600 13px {MONO};fill:#E2E8F0}}
@keyframes fadeup{{from{{opacity:0;transform:translateY(10px)}}to{{opacity:1;transform:none}}}}
.sweep{{transform-origin:{cx}px {cy}px;animation:spin 6s linear infinite}}
"""
    body = f"""
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="{W}" y2="{H}" gradientUnits="userSpaceOnUse">
    <stop stop-color="#0B1020"/><stop offset="1" stop-color="#111827"/>
  </linearGradient>
  <linearGradient id="chip" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#22D3EE"/><stop offset="1" stop-color="#A78BFA"/></linearGradient>
  <radialGradient id="coreG"><stop stop-color="#34D399"/><stop offset=".6" stop-color="#0EA5E9"/><stop offset="1" stop-color="#0EA5E9" stop-opacity="0"/></radialGradient>
  <linearGradient id="sw" x1="0" y1="0" x2="1" y2="0"><stop stop-color="#22D3EE" stop-opacity="0"/><stop offset="1" stop-color="#22D3EE" stop-opacity=".35"/></linearGradient>
  {GLOW_FILTER}
</defs>
<rect width="{W}" height="{H}" rx="22" fill="url(#bg)"/>
<path class="sweep" d="M{cx} {cy} L{cx + R2 + 20} {cy} A{R2 + 20} {R2 + 20} 0 0 0 {cx + (R2 + 20) * math.cos(-0.6):.1f} {cy + (R2 + 20) * math.sin(-0.6):.1f} Z" fill="url(#sw)" opacity=".5"/>
<circle cx="{cx}" cy="{cy}" r="{R1}" stroke="#22D3EE" stroke-opacity=".35" class="track"/>
<circle cx="{cx}" cy="{cy}" r="{R2}" stroke="#A78BFA" stroke-opacity=".3" class="track" style="animation-direction:reverse"/>
<circle cx="{cx}" cy="{cy}" r="34" fill="none" stroke="#34D399" class="ping"/>
<circle cx="{cx}" cy="{cy}" r="34" fill="none" stroke="#34D399" class="ping" style="animation-delay:1.5s"/>
<g class="core" filter="url(#glow)">
  <circle cx="{cx}" cy="{cy}" r="42" fill="url(#coreG)" opacity=".55"/>
  <circle cx="{cx}" cy="{cy}" r="30" fill="#0B1220" stroke="#34D399" stroke-width="2"/>
  <text x="{cx}" y="{cy + 7}" text-anchor="middle" font-family="{MONO}" font-weight="700" font-size="20" fill="#6EE7B7">&lt;/&gt;</text>
</g>
<g class="r1">{ring(ORBIT_INNER, R1, "r1", 0)}</g>
<g class="r2">{ring(ORBIT_OUTER, R2, "r2", 0.4)}</g>
<text x="500" y="70" class="h">Tech Arsenal</text>
<text x="500" y="98" class="sub">The stack I use to ship production-grade products</text>
{''.join(rows)}
"""
    return svg(W, H, "Tech stack", body, style + COMET_CSS)


# ----------------------------------------------------------------------------
# SERVICE / CONTACT CARDS
# ----------------------------------------------------------------------------
ICONS = {
    "globe": '<circle r="11"/><ellipse rx="5" ry="11"/><line x1="-11" x2="11"/>',
    "chart": '<path d="M-11 11 V-11 M-11 11 H11"/><path d="M-6 5 L-1 -2 L3 2 L10 -7"/>',
    "cart": '<path d="M-12 -9 H-8 L-4 6 H8 L11 -4 H-6"/><circle cx="-2" cy="10" r="1.6"/><circle cx="6" cy="10" r="1.6"/>',
    "plug": '<path d="M-5 -12 V-5 M5 -12 V-5 M-9 -5 H9 V1 A9 9 0 0 1 -9 1 Z M0 10 V14"/>',
    "bolt": '<path d="M2 -12 L-8 2 H0 L-2 12 L8 -2 H0 Z"/>',
    "github": '<path d="M0 -11 A11 11 0 0 0 -3.5 10.4 V6 C-7 7 -8 4 -9 3 M3.5 10.4 V5 C3.5 3 3 2 2 1.5 C6 1 8 -1 8 -5 C8 -7 7 -8 6.5 -8.5 C7 -10 6.5 -11 6.5 -11 C5 -11 3.5 -10 3 -9.5 A12 12 0 0 0 -3 -9.5 C-3.5 -10 -5 -11 -6.5 -11 C-6.5 -11 -7 -10 -6.5 -8.5 C-7 -8 -8 -7 -8 -5 C-8 -1 -6 1 -2 1.5"/>',
    "mail": '<rect x="-12" y="-8" width="24" height="16" rx="3"/><path d="M-12 -6 L0 3 L12 -6"/>',
    "in": '<rect x="-11" y="-11" width="22" height="22" rx="4"/><path d="M-6 -2 V6 M-6 -6 V-5.5 M-1 6 V-2 M-1 1 C-1 -2 5 -3 5 1 V6"/>',
}


def icon(name, x, y, color, cls="ic"):
    return (
        f'<g transform="translate({x} {y})"><g class="{cls}" stroke="{color}" stroke-width="2" '
        f'stroke-linecap="round" stroke-linejoin="round" fill="none">{ICONS[name]}</g></g>'
    )


CARD_CSS = f"""
.h{{font:700 32px {SANS};fill:#F1F5F9}}
.sub{{font:400 15px {SANS};fill:#94A3B8}}
.ct{{font:700 18px {SANS};fill:#F8FAFC}}
.cd{{font:400 14px {SANS};fill:#94A3B8}}
.card{{opacity:0;animation:rise .8s cubic-bezier(.2,.8,.2,1) forwards}}
@keyframes rise{{from{{opacity:0;transform:translateY(24px)}}to{{opacity:1;transform:none}}}}
.ic{{animation:bob 3s ease-in-out infinite}}
@keyframes bob{{50%{{transform:translateY(-3px)}}}}
.ul{{stroke-dasharray:120;stroke-dashoffset:120;animation:ul 1s ease .3s forwards}}
@keyframes ul{{to{{stroke-dashoffset:0}}}}
.shine{{animation:shine 6s ease-in-out infinite}}
@keyframes shine{{0%{{transform:translateX(-400px) skewX(-20deg)}}50%,100%{{transform:translateX(1400px) skewX(-20deg)}}}}
"""


def card_shell(W, H, title, subtitle, inner, extra_css="", accent="#22D3EE"):
    body = f"""
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="{W}" y2="{H}" gradientUnits="userSpaceOnUse">
    <stop stop-color="#0B1020"/><stop offset="1" stop-color="#1E293B"/>
  </linearGradient>
  <linearGradient id="cardF" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#0B1220"/><stop offset="1" stop-color="#111827"/></linearGradient>
  <linearGradient id="sh" x1="0" y1="0" x2="1" y2="0"><stop stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".06"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
  <clipPath id="clip"><rect width="{W}" height="{H}" rx="22"/></clipPath>
  {GLOW_FILTER}
</defs>
<g clip-path="url(#clip)">
  <rect width="{W}" height="{H}" fill="url(#bg)"/>
  <text x="48" y="60" class="h">{e(title)}</text>
  <line x1="48" y1="74" x2="168" y2="74" stroke="{accent}" stroke-width="3" stroke-linecap="round" class="ul"/>
  <text x="48" y="100" class="sub">{e(subtitle)}</text>
  {inner}
  <rect class="shine" x="0" y="0" width="160" height="{H}" fill="url(#sh)"/>
</g>
"""
    return svg(W, H, title, body, CARD_CSS + COMET_CSS + extra_css)


def services():
    W, H = 1100, 350
    boxes = [(40, 126, 320), (390, 126, 320), (740, 126, 320), (40, 228, 495), (565, 228, 495)]
    inner = []
    for i, ((title, desc, color, ic), (x, y, w)) in enumerate(zip(SERVICES, boxes)):
        h = 84
        inner.append(
            f'<g class="card" style="animation-delay:{.2 + i * .15:.2f}s">'
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="url(#cardF)"/>'
            f'{comet_border(x, y, w, h, 14, color, 5 + i * .7, -i * 1.3)}'
            f'<circle cx="{x + 38}" cy="{y + 42}" r="22" fill="{color}" fill-opacity=".12"/>'
            f'{icon(ic, x + 38, y + 42, color)}'
            f'<text x="{x + 74}" y="{y + 37}" class="ct">{e(title)}</text>'
            f'<text x="{x + 74}" y="{y + 60}" class="cd">{e(desc)}</text></g>'
        )
    return card_shell(W, H, "Freelance Services", "Production-focused solutions for startup and business clients", "".join(inner))


def contact():
    W, H = 1100, 240
    icons = ["github", "mail", "in"]
    inner = []
    for i, ((title, desc, color), ic) in enumerate(zip(CONTACTS, icons)):
        x, y, w, h = 40 + i * 350, 126, 320, 78
        inner.append(
            f'<g class="card" style="animation-delay:{.2 + i * .18:.2f}s">'
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="#0F172A"/>'
            f'{comet_border(x, y, w, h, 14, color, 4.5 + i * .6, -i * 1.5)}'
            f'<circle cx="{x + 38}" cy="{y + 39}" r="22" fill="none" stroke="{color}" class="pg" style="animation-delay:{i * .6:.1f}s;transform-origin:{x + 38}px {y + 39}px"/>'
            f'<circle cx="{x + 38}" cy="{y + 39}" r="22" fill="{color}" fill-opacity=".12"/>'
            f'{icon(ic, x + 38, y + 39, color)}'
            f'<text x="{x + 74}" y="{y + 34}" class="ct">{e(title)}</text>'
            f'<text x="{x + 74}" y="{y + 56}" class="cd">{e(desc)}</text></g>'
        )
    css = (
        ".pg{animation:pg 2.4s ease-out infinite}"
        "@keyframes pg{from{transform:scale(1);opacity:.7}to{transform:scale(1.7);opacity:0}}"
    )
    return card_shell(W, H, "Let's Build Something", "Open for freelance collaborations and long-term projects", "".join(inner), css, "#22C55E")


# ----------------------------------------------------------------------------
# DIVIDER / FOOTER
# ----------------------------------------------------------------------------
def divider():
    W, H = 1000, 24
    style = (
        ".run{animation:run 4s cubic-bezier(.6,0,.4,1) infinite}"
        "@keyframes run{from{transform:translateX(-260px)}to{transform:translateX(1000px)}}"
        ".d{animation:blink 2s ease-in-out infinite}@keyframes blink{50%{opacity:.3}}"
    )
    body = f"""
<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="0">
  <stop stop-color="#22D3EE" stop-opacity="0"/><stop offset=".5" stop-color="#34D399"/><stop offset="1" stop-color="#A78BFA" stop-opacity="0"/>
</linearGradient></defs>
<line x1="0" y1="12" x2="{W}" y2="12" stroke="#1E293B" stroke-width="2"/>
<rect class="run" x="0" y="10.5" width="260" height="3" rx="1.5" fill="url(#g)"/>
<rect class="d" x="{W / 2 - 5}" y="7" width="10" height="10" transform="rotate(45 {W / 2} 12)" fill="#0B1020" stroke="#34D399" stroke-width="2"/>
"""
    return svg(W, H, "divider", body, style)


def footer():
    W, H = 1000, 160

    def wave(amp, phase, base):
        pts = []
        for k in range(0, 11):
            x = k * 100
            y = base + amp * math.sin(k * 0.9 + phase)
            pts.append((x, y))
        d = f"M0 {H} L{pts[0][0]} {pts[0][1]:.1f} "
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            mx = (x0 + x1) / 2
            d += f"C{mx} {y0:.1f} {mx} {y1:.1f} {x1} {y1:.1f} "
        return d + f"L{W} {H} Z"

    layers = []
    for i, (color, op, amp, base, dur) in enumerate(
        [("#0EA5E9", .25, 14, 70, 7), ("#7C3AED", .3, 18, 88, 9), ("#10B981", .45, 12, 108, 6)]
    ):
        frames = ";".join(wave(amp, p, base) for p in (0, math.pi / 2, math.pi, 3 * math.pi / 2, 2 * math.pi))
        layers.append(
            f'<path d="{wave(amp, 0, base)}" fill="{color}" fill-opacity="{op}">'
            f'<animate attributeName="d" dur="{dur}s" repeatCount="indefinite" values="{frames}"/></path>'
        )
    style = f".t{{font:600 15px {MONO};letter-spacing:4px;fill:#94A3B8;animation:b 3s ease-in-out infinite}}@keyframes b{{50%{{opacity:.45}}}}"
    body = f"""
<defs><clipPath id="c"><rect width="{W}" height="{H}" rx="22"/></clipPath></defs>
<g clip-path="url(#c)">
<rect width="{W}" height="{H}" fill="#050816"/>
{''.join(layers)}
<text x="{W / 2}" y="42" text-anchor="middle" class="t">THANKS FOR STOPPING BY  ✦  LET'S SHIP SOMETHING</text>
</g>
"""
    return svg(W, H, "footer", body, style)


def main():
    OUT.mkdir(exist_ok=True)
    files = {
        "hero.svg": hero(),
        "about-terminal.svg": terminal(),
        "tech-orbit.svg": orbit(),
        "freelance-services.svg": services(),
        "contact-card.svg": contact(),
        "divider.svg": divider(),
        "footer.svg": footer(),
    }
    for name, content in files.items():
        (OUT / name).write_text(content, encoding="utf-8")
        print(f"wrote assets/{name} ({len(content) // 1024} KB)")


if __name__ == "__main__":
    main()
