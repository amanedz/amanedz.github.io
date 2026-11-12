"""VOLTCUT v2 — an aggressive cyberpunk display typeface, generated from geometry.

Run:  python3 build.py   (needs: pip install fonttools brotli skia-pathops)

Heavy, extended, all-caps. Every glyph is built from straight-edged primitives
(chamfered boxes, polygons, diagonal strokes) merged with boolean ops.
Signature details: 45-degree "speed" chamfers, razor-thin counters, stencil
gaps that detach stems from bowls/bars, and spikes that break the baseline.

Styles written: Regular / Oblique / Slit / Slit Oblique / Glitch (TTF + WOFF2).
"""
import math
import os

import pathops
from pathops import Path, PathOp
from fontTools.fontBuilder import FontBuilder
from fontTools.misc.timeTools import timestampNow
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")

UPM = 1000
H = 700           # cap height
S = 172           # vertical stem
T = 140           # horizontal bar
C = 150           # big chamfer
c = 40            # small chamfer
G = 30            # stencil gap
SB = 36           # side bearing (tight)
MID0, MID1 = H / 2 - T / 2, H / 2 + T / 2
W = 780           # standard (extended) body width


# ---------------------------------------------------------------- primitives
def poly(pts):
    p = Path()
    p.moveTo(*pts[0])
    for pt in pts[1:]:
        p.lineTo(*pt)
    p.close()
    return p


def box(x0, y0, x1, y1, tl=0, tr=0, br=0, bl=0):
    """Rectangle with optional 45-degree corner chamfers."""
    pts = []
    pts += [(x0, y1 - tl), (x0 + tl, y1)] if tl else [(x0, y1)]
    pts += [(x1 - tr, y1), (x1, y1 - tr)] if tr else [(x1, y1)]
    pts += [(x1, y0 + br), (x1 - br, y0)] if br else [(x1, y0)]
    pts += [(x0 + bl, y0), (x0, y0 + bl)] if bl else [(x0, y0)]
    return poly(pts)


def diag(x0, y0, x1, y1, w=S):
    """Diagonal stroke with horizontal end cuts and visual weight ~w."""
    dx, dy = x1 - x0, y1 - y0
    hw = w / 2 * math.hypot(dx, dy) / abs(dy)
    return poly([(x0 - hw, y0), (x0 + hw, y0), (x1 + hw, y1), (x1 - hw, y1)])


def U(*paths):
    out = Path()
    for p in paths:
        out = pathops.op(out, p, PathOp.UNION)
    return out


def D(a, *paths):
    for p in paths:
        a = pathops.op(a, p, PathOp.DIFFERENCE)
    return a


def I(a, b):
    return pathops.op(a, b, PathOp.INTERSECTION)


def band(p, y0, y1):
    return I(p, box(-1000, y0, 3000, y1))


def clip(p, w, lo=0, hi=H):
    return I(p, box(-400, lo, w + 400, hi))


def moved(p, dx=0, dy=0):
    out = Path()
    p.draw(TransformPen(out.getPen(), (1, 0, 0, 1, dx, dy)))
    return out


def frame(w, tl=C, tr=0, br=C, bl=0, itl=c, itr=0, ibr=c, ibl=0):
    return D(box(0, 0, w, H, tl, tr, br, bl), box(S, T, w - S, H - T, itl, itr, ibr, ibl))


def stem(tl=C, br=0, x=0):
    return box(x, 0, x + S, H, tl=tl, br=br)


# ---------------------------------------------------------------- glyphs
GL = {}  # name -> (width, path)


def glyph(name, w):
    def deco(fn):
        GL[name] = (w, fn(w))
        return fn
    return deco


# Letters --------------------------------------------------------------------
@glyph("A", W)
def _(w):
    # lambda form: slanted left flank, flat roof, right stem, no crossbar
    k = w * 0.40
    outer = poly([(0, 0), (k, H), (w, H), (w, 0)])
    inner = poly([(S * 1.15, -1), (k + S * 0.55, H - T), (w - S, H - T), (w - S, -1)])
    return U(D(outer, inner), poly([(w - S, 0), (w, 0), (w, -90)]))

@glyph("B", W)
def _(w):
    x = S + G
    bowl = D(box(x, 0, w, H, tr=c * 2, br=C),
             box(x - 1, T, w - S, MID0), box(x - 1, MID1, w - S, H - T),
             poly([(w + 1, MID1 - 10), (w - S * 0.55, H / 2), (w + 1, MID0 + 10)]))
    return U(stem(), bowl)

@glyph("C", W)
def _(w):
    return D(box(0, 0, w, H, tl=C, tr=T * 0.7, br=T * 0.7, bl=C * 0.5),
             box(S, T, w + 1, H - T, tl=c))

@glyph("D", W)
def _(w):
    x = S + G
    return U(stem(), D(box(x, 0, w, H, tr=C, br=C), box(x - 1, T, w - S, H - T, tr=c)))

@glyph("E", W - 60)
def _(w):
    x = S + G
    return U(stem(), box(x, H - T, w, H), box(x, MID0, w * 0.84, MID1, tr=c),
             box(x, 0, w, T, br=T * 0.8))

@glyph("F", W - 80)
def _(w):
    x = S + G
    return U(stem(), box(x, H - T, w, H, br=T * 0.8), box(x, MID0, w * 0.84, MID1, tr=c))

@glyph("G", W)
def _(w):
    g = D(box(0, 0, w, H, tl=C, br=C, tr=T * 0.7),
          box(S, T, w - S, H - T, tl=c), box(w - S - 1, MID1 - 1, w + 1, H - T))
    return U(g, box(w * 0.48, MID0, w, MID1))

@glyph("H", W)
def _(w):
    return U(stem(), stem(tl=0, br=C, x=w - S), box(S + G, MID0, w - S - G, MID1))

@glyph("I", S)
def _(w):
    return box(0, 0, S, H, tl=C * 0.9, br=C * 0.9)

@glyph("J", W - 60)
def _(w):
    j = D(box(0, 0, w, H, br=C, bl=C * 0.5), box(-1, T, w - S, H + 1))
    return U(j, box(0, T + G, S, H * 0.45, tl=c))

@glyph("K", W)
def _(w):
    x = S + G
    arms = U(diag(x + 70, H / 2, w - S * 0.55, H + 20), diag(x + 70, H / 2, w - S * 0.55, -20))
    arms = I(arms, box(x, 0, w + 200, H))
    spike = poly([(w - S * 1.05, 0), (w, 0), (w + 30, -90)])
    return U(stem(), clip(arms, w), spike)

@glyph("L", W - 80)
def _(w):
    return U(stem(), box(0, 0, w, T, br=T * 0.9))

@glyph("M", W + 200)
def _(w):
    m = (w - S) / 2
    return D(box(0, 0, w, H, tl=C, tr=C),
             box(S, -1, m, H - T), box(m + S, -1, w - S, H - T),
             box(m - 1, -1, m + S + 1, H * 0.34))

@glyph("N", W)
def _(w):
    n = D(box(0, 0, w, H, tl=C, br=C * 0.6), box(S, -1, w - S, H - T))
    return U(n, poly([(S, H - T), (S + T, H - T), (S, H - T - T)]))

@glyph("O", W)
def _(w):
    return frame(w)

@glyph("P", W)
def _(w):
    x = S + G
    return U(stem(), D(box(x, MID0, w, H, br=C), box(x - 1, MID1, w - S, H - T, br=c)))

@glyph("Q", W)
def _(w):
    return U(frame(w, br=0), poly([(w * 0.45, T), (w, T), (w + 40, -110), (w * 0.45, 0)]))

@glyph("R", W)
def _(w):
    x = S + G
    bowl = D(box(x, MID0, w, H, br=C * 0.6), box(x - 1, MID1, w - S, H - T, br=c))
    leg = poly([(w - S, MID0 - G), (w, MID0 - G), (w + 30, -100), (w - S, 0)])
    return U(stem(), bowl, leg)

@glyph("S", W)
def _(w):
    return D(box(0, 0, w, H, tl=C, br=C),
             box(S, MID1, w + 1, H - T, tl=c), box(-1, T, w - S, MID0, br=c))

@glyph("T", W)
def _(w):
    return U(box(0, H - T, w, H, tl=C), box(w / 2 - S / 2, 0, w / 2 + S / 2, H - T - G, br=c))

@glyph("U", W)
def _(w):
    return D(box(0, 0, w, H, tl=C * 0.7, br=C), box(S, T, w - S, H + 1, bl=c))

@glyph("V", W)
def _(w):
    k = 0.38
    outer = poly([(0, H), (w, H), (w * (1 - k), 0), (w * k, 0)])
    off = S * 1.2
    yb = T * 1.25
    lx = lambda y: off + w * k * (1 - y / H)
    inner = poly([(off, H + 1), (w - off, H + 1), (w - lx(yb), yb), (lx(yb), yb)])
    return D(outer, inner)

@glyph("W", W + 220)
def _(w):
    m = (w - S) / 2
    return D(box(0, 0, w, H, bl=C, br=C),
             box(S, T, m, H + 1), box(m + S, T, w - S, H + 1),
             box(m - 1, H * 0.62, m + S + 1, H + 1))

@glyph("X", W)
def _(w):
    x = clip(U(diag(S * 0.6, H, w - S * 0.6, 0, w=S * 1.1), diag(S * 0.6, 0, w - S * 0.6, H, w=S * 1.1)), w)
    return D(x, box(-1, H / 2 - G / 2, w + 1, H / 2 + G / 2))

@glyph("Y", W)
def _(w):
    y0 = H * 0.42
    k = 0.30
    outer = poly([(0, H), (w, H), (w * (1 - k), y0), (w * k, y0)])
    off = S * 1.2
    lx = lambda y: off + (w * k) * (H - y) / (H - y0)
    yb = y0 + T
    inner = poly([(off, H + 1), (w - off, H + 1), (w - lx(yb), yb), (lx(yb), yb)])
    return U(D(outer, inner), box(w / 2 - S / 2, 0, w / 2 + S / 2, y0 - G, br=c))

@glyph("Z", W)
def _(w):
    d = clip(diag(S * 0.6, 0, w - S * 0.6, H, w=S * 1.15), w, T + G, H - T - G)
    return U(box(0, H - T, w, H, tl=C), box(0, 0, w, T, br=C), d)

# Digits ---------------------------------------------------------------------
WD = 700

@glyph("zero", WD)
def _(w):
    sl = I(diag(S + 40, T, w - S - 40, H - T, w=T * 0.8), box(S + G, T + G, w - S - G, H - T - G))
    return U(frame(w), sl)

@glyph("one", 400)
def _(w):
    return U(box(w - S, 0, w, H, br=c), box(0, H - T, w - S - G, H, tl=C * 0.7))

@glyph("two", WD)
def _(w):
    return D(box(0, 0, w, H, tr=C, bl=C),
             box(-1, MID1, w - S, H - T, tr=c), box(S, T, w + 1, MID0, bl=c))

@glyph("three", WD)
def _(w):
    return D(box(0, 0, w, H, tr=C, br=C),
             box(-1, MID1, w - S, H - T, tr=c), box(-1, T, w - S, MID0, br=c),
             box(-1, MID0 - 1, w * 0.3, MID1 + 1))

@glyph("four", WD)
def _(w):
    y0 = H * 0.26
    return U(box(0, y0, S, H, tl=C * 0.8), box(0, y0, w, y0 + T, br=c),
             box(w - S * 1.6, 0, w - S * 0.6, H, br=c))

@glyph("five", WD)
def _(w):
    return D(box(0, 0, w, H, br=C),
             box(S, MID1, w + 1, H - T), box(-1, T, w - S, MID0, br=c),
             poly([(w + 1, MID1 + 1), (w + 1, MID1 - C), (w - C, MID1 + 1)]))

@glyph("six", WD)
def _(w):
    return D(box(0, 0, w, H, tl=C, br=C),
             box(S, MID1, w + 1, H - T, tl=c), box(S, T, w - S, MID0, br=c))

@glyph("seven", WD)
def _(w):
    return U(box(0, H - T, w, H, tl=C * 0.8),
             clip(diag(w - S * 0.6, H - T - G, w * 0.30, -10, w=S * 1.05), w, 0, H - T - G))

@glyph("eight", WD)
def _(w):
    notch = lambda x, s: poly([(x, MID1 - 10), (x + s * S * 0.55, H / 2), (x, MID0 + 10)])
    return D(box(0, 0, w, H, tl=C, tr=C, br=C, bl=C),
             box(S, MID1, w - S, H - T, tl=c), box(S, T, w - S, MID0, br=c),
             notch(w + 1, -1), notch(-1, 1))

@glyph("nine", WD)
def _(w):
    return D(box(0, 0, w, H, tl=C, br=C),
             box(S, MID1, w - S, H - T, tl=c), box(-1, T, w - S, MID0, br=c))

# Punctuation ----------------------------------------------------------------
@glyph("period", S)
def _(w):
    return box(0, 0, S, T, tl=c)

@glyph("comma", S)
def _(w):
    return U(box(0, 0, S, T, tl=c), poly([(S * 0.35, 0), (S, 0), (S * 0.3, -150), (-S * 0.3, -150)]))

@glyph("colon", S)
def _(w):
    return U(box(0, 0, S, T, tl=c), box(0, 420, S, 420 + T, tl=c))

@glyph("semicolon", S)
def _(w):
    return U(GL["comma"][1], box(0, 420, S, 420 + T, tl=c))

@glyph("exclam", S)
def _(w):
    return U(box(0, 0, S, T, tl=c), box(0, T + G * 2, S, H, tl=C * 0.8))

@glyph("question", 620)
def _(w):
    y = H * 0.36
    top = D(box(0, y, w, H, tl=C, br=C * 0.7),
            box(S, y + T, w - S, H - T, br=c), box(-1, y - 1, w - S, y + T))
    return U(top, box(w / 2 - S / 2, y, w / 2 + S / 2, y + T + 10),
             box(w / 2 - S / 2, T + G * 2, w / 2 + S / 2, y + 1), box(w / 2 - S / 2, 0, w / 2 + S / 2, T, tl=c))

@glyph("hyphen", 380)
def _(w):
    return box(0, MID0, w, MID1, tl=c, br=c)

@glyph("underscore", W)
def _(w):
    return box(0, -190, w, -190 + T * 0.8)

@glyph("slash", 480)
def _(w):
    return clip(diag(S * 0.6, -60, w - S * 0.6, H + 60), w, -60, H + 60)

@glyph("backslash", 480)
def _(w):
    return clip(diag(S * 0.6, H + 60, w - S * 0.6, -60), w, -60, H + 60)

@glyph("plus", 560)
def _(w):
    return U(box(0, MID0, w, MID1), box(w / 2 - S / 2, H / 2 - w / 2, w / 2 + S / 2, H / 2 + w / 2))

@glyph("equal", 560)
def _(w):
    return U(box(0, H / 2 + 25, w, H / 2 + 25 + T, tl=c), box(0, H / 2 - 25 - T, w, H / 2 - 25, br=c))

@glyph("bracketleft", 330)
def _(w):
    return D(box(0, -100, w, H + 100, tl=C * 0.8), box(S, -100 + T, w + 1, H + 100 - T))

@glyph("bracketright", 330)
def _(w):
    return D(box(0, -100, w, H + 100, br=C * 0.8), box(-1, -100 + T, w - S, H + 100 - T))

@glyph("parenleft", 320)
def _(w):
    return D(box(0, -100, w, H + 100, tl=C, bl=C), box(S, -100 + T, w + 1, H + 100 - T, tl=c, bl=c))

@glyph("parenright", 320)
def _(w):
    return D(box(0, -100, w, H + 100, tr=C, br=C), box(-1, -100 + T, w - S, H + 100 - T, tr=c, br=c))

@glyph("quotesingle", S)
def _(w):
    return box(0, H - 260, S, H, tl=c)

@glyph("quotedbl", S * 2 + 50)
def _(w):
    return U(box(0, H - 260, S, H, tl=c), box(S + 50, H - 260, w, H, tl=c))

@glyph("numbersign", 700)
def _(w):
    v1 = diag(w * 0.32, 0, w * 0.42, H, w=T)
    v2 = diag(w * 0.62, 0, w * 0.72, H, w=T)
    return clip(U(v1, v2, box(0, 170, w, 170 + T * 0.9), box(0, 420, w, 420 + T * 0.9)), w)

@glyph("ampersand", 760)
def _(w):
    top = D(box(40, MID0, w - 200, H, tl=C, br=c), box(40 + S, MID1, w - 200 - S, H - T))
    bot = D(box(0, 0, w - 130, MID1, tl=C * 0.6, br=C * 0.8), box(S, T, w - 130 - S, MID0, br=c),
            box(w - 130 - S - 1, MID0 - 1, w, MID1 + 1))
    return U(top, bot, box(w - 220, MID0, w, MID1, br=c))

@glyph("at", 820)
def _(w):
    outer = D(box(0, -60, w, H, tl=C, br=C), box(S * 0.8, -60 + T * 0.8, w - S * 0.8, H - T * 0.8, tl=c, br=c))
    inner = D(box(w * 0.3, H * 0.2, w - S * 0.8 + 1, H * 0.72, tl=c),
              box(w * 0.3 + T * 0.8, H * 0.2 + T * 0.8, w - S * 0.8 - T * 0.8, H * 0.72 - T * 0.8))
    return U(outer, inner)

@glyph("asterisk", 480)
def _(w):
    cy, r, t = H - 180, 180, 55
    arms = [box(w / 2 - t, cy - r, w / 2 + t, cy + r)]
    for ang in (60, -60):
        a = math.radians(ang)
        dx, dy, nx, ny = math.sin(a) * r, math.cos(a) * r, math.cos(a) * t, -math.sin(a) * t
        cx = w / 2
        arms.append(poly([(cx - dx - nx, cy - dy - ny), (cx - dx + nx, cy - dy + ny),
                          (cx + dx + nx, cy + dy + ny), (cx + dx - nx, cy + dy - ny)]))
    return U(*arms)

@glyph("less", 560)
def _(w):
    return U(clip(diag(w - 40, H / 2 + 260, 60, H / 2 - 10, w=T * 1.1), w, H / 2, H / 2 + 260),
             clip(diag(60, H / 2 + 10, w - 40, H / 2 - 260, w=T * 1.1), w, H / 2 - 260, H / 2))

@glyph("greater", 560)
def _(w):
    return U(clip(diag(40, H / 2 + 260, w - 60, H / 2 - 10, w=T * 1.1), w, H / 2, H / 2 + 260),
             clip(diag(w - 60, H / 2 + 10, 40, H / 2 - 260, w=T * 1.1), w, H / 2 - 260, H / 2))

@glyph("percent", 700)
def _(w):
    o1 = D(box(0, H - 270, 250, H, tl=c), box(T * 0.75, H - 270 + T * 0.75, 250 - T * 0.75, H - T * 0.75))
    o2 = D(box(w - 250, 0, w, 270, br=c), box(w - 250 + T * 0.75, T * 0.75, w - T * 0.75, 270 - T * 0.75))
    return U(o1, o2, clip(diag(90, -20, w - 90, H + 20, w=T), w))

@glyph("dollar", W)
def _(w):
    s = D(box(0, 40, w, H - 40, tl=C, br=C),
          box(S, MID1, w + 1, H - 40 - T * 0.85, tl=c), box(-1, 40 + T * 0.85, w - S, MID0, br=c))
    return U(s, box(w / 2 - 40, -70, w / 2 + 40, H + 70))

@glyph("bar", S)
def _(w):
    return box(0, -130, S, H + 130)


LETTERS = [chr(i) for i in range(ord("A"), ord("Z") + 1)]
NAMES = {
    "0": "zero", "1": "one", "2": "two", "3": "three", "4": "four", "5": "five", "6": "six",
    "7": "seven", "8": "eight", "9": "nine", ".": "period", ",": "comma", ":": "colon",
    ";": "semicolon", "!": "exclam", "?": "question", "-": "hyphen", "_": "underscore",
    "/": "slash", "\\": "backslash", "+": "plus", "=": "equal", "[": "bracketleft",
    "]": "bracketright", "(": "parenleft", ")": "parenright", "'": "quotesingle",
    '"': "quotedbl", "#": "numbersign", "&": "ampersand", "@": "at", "*": "asterisk",
    "<": "less", ">": "greater", "%": "percent", "$": "dollar", "|": "bar",
}


# ---------------------------------------------------------------- styles
# Slits sit in the vertical-only zones between the three bar levels.
SLITS = [(T + 52, T + 80), (MID1 + 52, MID1 + 80)]


def slit(p, w):
    return D(p, *[box(-300, a, w + 300, b) for a, b in SLITS])


def glitch(p, w):
    """Cut into horizontal bands and knock them sideways, like a torn scanline."""
    cuts = [(-400, 232, 0), (232, 300, 70), (300, 470, -34), (470, 492, 120), (492, 1200, 18)]
    return U(*[moved(band(p, a, b), dx) for a, b, dx in cuts])


def to_glyph(path, dx, skew):
    path = Path(path)
    path.simplify(clockwise=True)
    pen = TTGlyphPen(None)
    path.draw(TransformPen(pen, (1, 0, math.tan(math.radians(skew)), 1, dx, 0)))
    return pen.glyph()


def build(style, fx=None, skew=0.0):
    family = "Voltcut"
    glyphs, adv, cmap = {}, {}, {}
    order = [".notdef", "space"] + list(GL.keys())

    glyphs[".notdef"] = to_glyph(D(box(0, 0, 500, H), box(60, 60, 440, H - 60)), SB, skew)
    adv[".notdef"] = 500 + 2 * SB
    glyphs["space"] = TTGlyphPen(None).glyph()
    adv["space"] = 280
    cmap[0x20] = cmap[0xA0] = "space"

    pad = 60 if fx is glitch else 0  # glitched bands stick out sideways
    for name, (w, p) in GL.items():
        if fx:
            p = fx(p, w)
        glyphs[name] = to_glyph(p, SB + pad / 2, skew)
        adv[name] = int(round(w + 2 * SB + pad))
    for ch in LETTERS:
        cmap[ord(ch)] = ch
        cmap[ord(ch.lower())] = ch  # all-caps design: lowercase maps to caps
    for ch, n in NAMES.items():
        cmap[ord(ch)] = n

    fb = FontBuilder(UPM, isTTF=True)
    fb.setupGlyphOrder(order)
    fb.setupCharacterMap(cmap)
    fb.setupGlyf(glyphs)
    glyf = fb.font["glyf"]
    hm = {}
    for n in order:
        g = glyf[n]
        g.recalcBounds(glyf)
        hm[n] = (adv[n], getattr(g, "xMin", 0))
    fb.setupHorizontalMetrics(hm)
    fb.setupHorizontalHeader(ascent=900, descent=-250)
    ps = f"{family}-{style.replace(' ', '')}"
    fb.setupNameTable({
        "familyName": family, "styleName": style, "uniqueFontIdentifier": f"{ps}-2.000",
        "fullName": f"{family} {style}", "psName": ps, "version": "Version 2.000",
        "copyright": "Copyright (c) 2026 amanedz", "licenseDescription": "SIL Open Font License 1.1",
    })
    fb.setupOS2(sTypoAscender=900, sTypoDescender=-250, sTypoLineGap=100, usWinAscent=1000,
                usWinDescent=300, sxHeight=H, sCapHeight=H, achVendID="NONE",
                fsSelection=(0x01 if skew else 0x40), usWeightClass=900)
    fb.setupPost(italicAngle=-skew)
    fb.setupHead(unitsPerEm=UPM, macStyle=(0x2 if skew else 0) | 0x1,
                 created=timestampNow(), modified=timestampNow())

    os.makedirs(OUT, exist_ok=True)
    ttf = os.path.join(OUT, f"{ps}.ttf")
    fb.save(ttf)
    f = TTFont(ttf)
    f.flavor = "woff2"
    f.save(os.path.join(OUT, f"{ps}.woff2"))
    print("wrote", ttf, len(GL), "glyphs")


if __name__ == "__main__":
    build("Regular")
    build("Oblique", skew=12)
    build("Slit", fx=slit)
    build("Slit Oblique", fx=slit, skew=12)
    build("Glitch", fx=glitch)
