"""VOLTCUT — a cyberpunk display typeface, generated from geometry.

Run:  python3 build.py   (needs: pip install fonttools brotli skia-pathops)

Every glyph is built from straight-edged primitives (chamfered boxes and
diagonal strokes), merged with boolean ops, then written out as
Regular / Oblique / Slit (striped) / Slit Oblique, in TTF + WOFF2.
"""
import math
import os

import pathops
from pathops import Path, PathOp
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")

UPM = 1000
H = 700          # cap height
S = 128          # vertical stem
T = 108          # horizontal bar
C = 112          # big chamfer
c = 46           # inner chamfer
SB = 58          # side bearing
MID0, MID1 = H / 2 - T / 2, H / 2 + T / 2
DESC = -150


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
    L = math.hypot(dx, dy)
    hw = w / 2 * L / abs(dy)  # horizontal half-width
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


def clipcap(p, w, lo=0, hi=H):
    return I(p, box(-400, lo, w + 400, hi))


def frame(w, tl=C, tr=0, br=C, bl=0, itl=c, itr=0, ibr=c, ibl=0):
    return D(box(0, 0, w, H, tl, tr, br, bl), box(S, T, w - S, H - T, itl, itr, ibr, ibl))


# ---------------------------------------------------------------- glyphs
G = {}  # name -> (width, path)


def glyph(name, w):
    def deco(fn):
        G[name] = (w, fn(w))
        return fn
    return deco


W0 = 620   # standard body width
WN = 560   # narrow
WW = 800   # wide

@glyph("A", 680)
def _(w):
    a = diag(S * 0.55, 0, w / 2, H + 40)
    b = diag(w / 2, H + 40, w - S * 0.55, 0)
    bar = box(w * 0.22, 150, w * 0.78, 150 + T)
    return clipcap(U(a, b, bar), w)

@glyph("B", W0)
def _(w):
    b = D(box(0, 0, w, H, tl=C, tr=c * 1.6, br=C),
          box(S, MID1, w - S, H - T),
          box(S, T, w - S, MID0, br=c),
          poly([(w + 1, MID1 + 10), (w - S * 0.5, H / 2), (w + 1, MID0 - 10)]))
    return b

@glyph("C", W0)
def _(w):
    return D(frame(w, tl=C, br=0, bl=C, tr=0, itl=c, ibr=0, ibl=c),
             box(w - S - 1, T, w + 1, H - T))

@glyph("D", W0)
def _(w):
    return frame(w, tl=0, tr=C, br=C, bl=0, itl=0, itr=c, ibr=c)

@glyph("E", 560)
def _(w):
    return D(box(0, 0, w, H, tl=C),
             box(S, T, w + 1, MID0), box(S, MID1, w + 1, H - T),
             box(w * 0.8, MID0 - 1, w + 1, MID1 + 1))

@glyph("F", 540)
def _(w):
    return D(box(0, 0, w, H, tl=C),
             box(S, -1, w + 1, MID0), box(S, MID1, w + 1, H - T),
             box(w * 0.8, MID0 - 1, w + 1, MID1 + 1))

@glyph("G", W0)
def _(w):
    f = D(frame(w, tl=C, br=C, bl=0, itl=c, ibr=c), box(w - S - 1, MID1, w + 1, H - T))
    return U(f, box(w * 0.46, MID0, w, MID1))

@glyph("H", W0)
def _(w):
    return U(box(0, 0, S, H, tl=C * 0.8), box(w - S, 0, w, H, br=C * 0.8), box(0, MID0, w, MID1))

@glyph("I", S)
def _(w):
    return box(0, 0, S, H, tl=C * 0.8, br=C * 0.8)

@glyph("J", 580)
def _(w):
    return D(frame(w, tl=0, br=C, bl=C, tr=C * 0.8, itl=0, ibr=c, ibl=c),
             box(S, T, w - S, H + 1), box(-1, H * 0.42, S + 1, H + 1))

@glyph("K", 640)
def _(w):
    up = diag(S + 40, H / 2, w - S * 0.55, H + 10)
    lo = diag(S + 40, H / 2, w - S * 0.55, -10)
    return U(box(0, 0, S, H, tl=C * 0.8), clipcap(U(up, lo, box(S - 1, MID0, S + 120, MID1)), w))

@glyph("L", 540)
def _(w):
    return D(box(0, 0, w, H, tl=C * 0.8, br=C * 0.8), box(S, T, w + 1, H + 1))

@glyph("M", WW)
def _(w):
    m = (w - S) / 2
    return D(box(0, 0, w, H, tl=C, tr=C),
             box(S, -1, m, H - T), box(m + S, -1, w - S, H - T),
             box(m - 1, -1, m + S + 1, H * 0.3))

@glyph("N", 660)
def _(w):
    d = diag(S * 0.55 + 20, H, w - S * 0.55 - 20, 0, w=S * 1.05)
    return I(U(box(0, 0, S, H), box(w - S, 0, w, H), d), box(0, 0, w, H, tl=C * 0.8, br=C * 0.8))

@glyph("O", W0 + 40)
def _(w):
    return frame(w)

@glyph("P", W0 - 20)
def _(w):
    bowl = D(box(0, MID0, w, H, tl=C, br=C * 0.8), box(S, MID1, w - S, H - T, br=c))
    return U(bowl, box(0, 0, S, H, tl=C))

@glyph("Q", W0 + 40)
def _(w):
    return U(frame(w, br=0), box(w * 0.56, -110, w, T, br=C * 0.7))

@glyph("R", W0)
def _(w):
    bowl = D(box(0, MID0, w, H, tl=C, br=C * 0.8), box(S, MID1, w - S, H - T, br=c))
    leg = clipcap(diag(w * 0.42, H / 2, w - S * 0.55, -10), w, 0, MID0 + 1)
    return U(bowl, box(0, 0, S, H, tl=C), leg)

@glyph("S", W0)
def _(w):
    return D(box(0, 0, w, H, tl=C, br=C),
             box(S, MID1, w + 1, H - T, tl=c), box(-1, T, w - S, MID0, br=c))

@glyph("T", 640)
def _(w):
    return U(box(0, H - T, w, H, tl=C * 0.8), box(w / 2 - S / 2, 0, w / 2 + S / 2, H, br=c))

@glyph("U", W0)
def _(w):
    return D(frame(w, tl=C * 0.8, tr=0, br=C, bl=0), box(S, T + 1, w - S, H + 1))

@glyph("V", 680)
def _(w):
    a = diag(S * 0.55, H, w / 2, -40)
    b = diag(w / 2, -40, w - S * 0.55, H)
    return clipcap(U(a, b), w)

@glyph("W", WW + 40)
def _(w):
    m = (w - S) / 2
    return D(box(0, 0, w, H, tl=C, br=C),
             box(S, T, m, H + 1), box(m + S, T, w - S, H + 1),
             box(m - 1, H * 0.7, m + S + 1, H + 1))

@glyph("X", 680)
def _(w):
    return clipcap(U(diag(S * 0.55, H, w - S * 0.55, 0), diag(S * 0.55, 0, w - S * 0.55, H)), w)

@glyph("Y", 680)
def _(w):
    a = diag(S * 0.55, H, w / 2, H * 0.42)
    b = diag(w - S * 0.55, H, w / 2, H * 0.42)
    return U(clipcap(U(a, b), w), box(w / 2 - S / 2, 0, w / 2 + S / 2, H * 0.45, br=c))

@glyph("Z", W0)
def _(w):
    d = diag(S * 0.6, T, w - S * 0.6, H - T, w=S * 1.05)
    return U(box(0, H - T, w, H, tl=C * 0.8), box(0, 0, w, T, br=C * 0.8), d)

# ---- digits
@glyph("zero", WN)
def _(w):
    return U(frame(w), box(w / 2 - 30, H * 0.36, w / 2 + 30, H * 0.64))

@glyph("one", 340)
def _(w):
    return U(box(w - S, 0, w, H, br=c), box(0, H - T, w, H, tl=C * 0.8), box(0, H - T - 90, T, H))

@glyph("two", WN)
def _(w):
    return D(box(0, 0, w, H, tr=C, bl=C),
             box(-1, MID1, w - S, H - T, tr=c), box(S, T, w + 1, MID0, bl=c))

@glyph("three", WN)
def _(w):
    return D(box(0, 0, w, H, tr=C, br=C),
             box(-1, MID1, w - S, H - T, tr=c), box(-1, T, w - S, MID0, br=c),
             box(-1, MID0 - 1, w * 0.3, MID1 + 1))

@glyph("four", WN + 20)
def _(w):
    y0 = H * 0.28
    return U(box(0, y0, S, H, tl=C * 0.8), box(0, y0, w, y0 + T), box(w - S - 40, 0, w - 40, H * 0.8, br=c))

@glyph("five", WN)
def _(w):
    return D(box(0, 0, w, H, br=C),
             box(S, MID1, w + 1, H - T), box(-1, T, w - S, MID0, br=c),
             poly([(w + 1, MID1 + 1), (w + 1, MID1 - C), (w - C, MID1 + 1)]))

@glyph("six", WN)
def _(w):
    return D(box(0, 0, w, H, tl=C, br=C),
             box(S, MID1, w + 1, H - T, tl=c), box(S, T, w - S, MID0, br=c))

@glyph("seven", WN + 20)
def _(w):
    return U(box(0, H - T, w, H, tl=C * 0.8), clipcap(diag(w - S * 0.55, H - T, w * 0.32, -10), w))

@glyph("eight", WN)
def _(w):
    notch = lambda x, s: poly([(x, MID1 + 10), (x + s * S * 0.5, H / 2), (x, MID0 - 10)])
    return D(box(0, 0, w, H, tl=C, tr=C, br=C, bl=C),
             box(S, MID1, w - S, H - T, tl=c), box(S, T, w - S, MID0, br=c),
             notch(w + 1, -1), notch(-1, 1))

@glyph("nine", WN)
def _(w):
    return D(box(0, 0, w, H, tl=C, br=C),
             box(S, MID1, w - S, H - T, tl=c), box(-1, T, w - S, MID0, br=c))

# ---- punctuation
@glyph("period", S)
def _(w):
    return box(0, 0, S, S, tl=c)

@glyph("comma", S)
def _(w):
    return U(box(0, 0, S, S, tl=c), poly([(S * 0.35, 0), (S, 0), (S * 0.3, -150), (-S * 0.3, -150)]))

@glyph("colon", S)
def _(w):
    return U(box(0, 0, S, S, tl=c), box(0, 420, S, 420 + S, tl=c))

@glyph("semicolon", S)
def _(w):
    return U(G["comma"][1], box(0, 420, S, 420 + S, tl=c))

@glyph("exclam", S)
def _(w):
    return U(box(0, 0, S, S, tl=c), box(0, S + 70, S, H, tl=C * 0.8))

@glyph("question", WN - 40)
def _(w):
    top = D(box(0, H * 0.38, w, H, tl=C, br=C * 0.7),
            box(S, H * 0.38 + T, w - S, H - T, br=c), box(-1, H * 0.38 - 1, w - S, H * 0.38 + T))
    return U(top, box(w / 2 - S / 2, H * 0.38, w / 2 + S / 2, H * 0.38 + T + 10),
             box(w / 2 - S / 2, H * 0.3, w / 2 + S / 2, H * 0.4), box(w / 2 - S / 2, 0, w / 2 + S / 2, S, tl=c))

@glyph("hyphen", 340)
def _(w):
    return box(0, MID0, w, MID1, tl=c)

@glyph("underscore", W0)
def _(w):
    return box(0, -170, w, -170 + T)

@glyph("slash", 420)
def _(w):
    return clipcap(diag(S * 0.55, -60, w - S * 0.55, H + 60), w, -60, H + 60)

@glyph("backslash", 420)
def _(w):
    return clipcap(diag(S * 0.55, H + 60, w - S * 0.55, -60), w, -60, H + 60)

@glyph("plus", 520)
def _(w):
    return U(box(0, MID0, w, MID1), box(w / 2 - S / 2, H / 2 - w / 2, w / 2 + S / 2, H / 2 + w / 2))

@glyph("equal", 520)
def _(w):
    return U(box(0, H / 2 + 30, w, H / 2 + 30 + T, tl=c), box(0, H / 2 - 30 - T, w, H / 2 - 30, br=c))

@glyph("bracketleft", 300)
def _(w):
    return D(box(0, -100, w, H + 100, tl=C * 0.8), box(S, -100 + T, w + 1, H + 100 - T))

@glyph("bracketright", 300)
def _(w):
    return D(box(0, -100, w, H + 100, br=C * 0.8), box(-1, -100 + T, w - S, H + 100 - T))

@glyph("parenleft", 280)
def _(w):
    return D(box(0, -100, w, H + 100, tl=C, bl=C), box(S, -100 + T, w + 1, H + 100 - T, tl=c, bl=c))

@glyph("parenright", 280)
def _(w):
    return D(box(0, -100, w, H + 100, tr=C, br=C), box(-1, -100 + T, w - S, H + 100 - T, tr=c, br=c))

@glyph("quotesingle", S)
def _(w):
    return box(0, H - 240, S, H + 0, tl=c)

@glyph("quotedbl", S * 2 + 60)
def _(w):
    return U(box(0, H - 240, S, H, tl=c), box(S + 60, H - 240, w, H, tl=c))

@glyph("numbersign", 640)
def _(w):
    v1 = diag(w * 0.32, 0, w * 0.42, H, w=T)
    v2 = diag(w * 0.62, 0, w * 0.72, H, w=T)
    return clipcap(U(v1, v2, box(0, 180, w, 180 + T), box(0, 420, w, 420 + T)), w)

@glyph("ampersand", 680)
def _(w):
    # squared ampersand: a stacked bracket form with an outgoing arm
    top = D(box(40, MID0, w - 180, H, tl=C, br=c), box(40 + S, MID1, w - 180 - S, H - T))
    bot = D(box(0, 0, w - 120, MID1, tl=C * 0.6, br=C * 0.8), box(S, T, w - 120 - S, MID0, br=c),
            box(w - 120 - S - 1, MID0 - 1, w, MID1 + 1))
    arm = box(w - 200, MID0, w, MID1, br=c)
    return U(top, bot, arm)

@glyph("at", 760)
def _(w):
    outer = D(box(0, -60, w, H, tl=C, br=C), box(S * 0.8, -60 + T * 0.8, w - S * 0.8, H - T * 0.8, tl=c, br=c))
    inner = D(box(w * 0.3, H * 0.22, w - S * 0.8 + 1, H * 0.7, tl=c), box(w * 0.3 + T * 0.8, H * 0.22 + T * 0.8, w - S * 0.8 - T * 0.8, H * 0.7 - T * 0.8))
    return U(outer, inner)

@glyph("asterisk", 460)
def _(w):
    cy = H - 170
    arms = [box(w / 2 - 50, cy - 170, w / 2 + 50, cy + 170)]
    for ang in (60, -60):
        a = math.radians(ang)
        dx, dy = math.sin(a) * 170, math.cos(a) * 170
        nx, ny = math.cos(a) * 50, -math.sin(a) * 50
        cx = w / 2
        arms.append(poly([(cx - dx - nx, cy - dy - ny), (cx - dx + nx, cy - dy + ny),
                          (cx + dx + nx, cy + dy + ny), (cx + dx - nx, cy + dy - ny)]))
    return U(*arms)

@glyph("less", 520)
def _(w):
    return U(clipcap(diag(w - 40, H / 2 + 250, 60, H / 2 - 10, w=T * 1.1), w, H / 2, H / 2 + 250),
             clipcap(diag(60, H / 2 + 10, w - 40, H / 2 - 250, w=T * 1.1), w, H / 2 - 250, H / 2))

@glyph("greater", 520)
def _(w):
    return U(clipcap(diag(40, H / 2 + 250, w - 60, H / 2 - 10, w=T * 1.1), w, H / 2, H / 2 + 250),
             clipcap(diag(w - 60, H / 2 + 10, 40, H / 2 - 250, w=T * 1.1), w, H / 2 - 250, H / 2))

@glyph("percent", 640)
def _(w):
    o1 = D(box(0, H - 260, 230, H, tl=c), box(T * 0.8, H - 260 + T * 0.8, 230 - T * 0.8, H - T * 0.8))
    o2 = D(box(w - 230, 0, w, 260, br=c), box(w - 230 + T * 0.8, T * 0.8, w - T * 0.8, 260 - T * 0.8))
    return U(o1, o2, clipcap(diag(80, -20, w - 80, H + 20, w=T), w))

@glyph("dollar", W0)
def _(w):
    s = D(box(0, 40, w, H - 40, tl=C, br=C),
          box(S, MID1, w + 1, H - 40 - T, tl=c), box(-1, 40 + T, w - S, MID0, br=c))
    return U(s, box(w / 2 - 35, -60, w / 2 + 35, H + 60))

@glyph("bar", S)
def _(w):
    return box(0, -120, S, H + 120)


ALIAS = {chr(i): chr(i) for i in range(ord("A"), ord("Z") + 1)}
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
SLITS = [(176, 202), (498, 524)]  # cut between the bar levels -> striped "Slit" style


def slit(p, w):
    return D(p, *[box(-300, a, w + 300, b) for a, b in SLITS])


def to_glyph(path, dx, skew):
    path = Path(path)
    path.simplify(clockwise=True)
    pen = TTGlyphPen(None)
    m = (1, 0, math.tan(math.radians(skew)), 1, dx, 0)
    path.draw(TransformPen(pen, m))
    return pen.glyph()


def build(style, slitted=False, skew=0.0):
    family = "Voltcut"
    glyphs, metrics, cmap = {}, {}, {}
    order = [".notdef", "space"] + list(G.keys())

    nd = D(box(0, 0, 500, H), box(60, 60, 440, H - 60))
    glyphs[".notdef"] = to_glyph(nd, SB, skew)
    metrics[".notdef"] = (500 + 2 * SB, SB)
    glyphs["space"] = TTGlyphPen(None).glyph()
    metrics["space"] = (300, 0)
    cmap[0x20] = "space"
    cmap[0xA0] = "space"

    for name, (w, p) in G.items():
        if slitted:
            p = slit(p, w)
        glyphs[name] = to_glyph(p, SB, skew)
        metrics[name] = (int(round(w + 2 * SB)), SB)
    for ch in ALIAS:
        cmap[ord(ch)] = ch
        cmap[ord(ch.lower())] = ch  # all-caps design: lowercase maps to caps
    for ch, n in NAMES.items():
        cmap[ord(ch)] = n

    fb = FontBuilder(UPM, isTTF=True)
    fb.setupGlyphOrder(order)
    fb.setupCharacterMap(cmap)
    fb.setupGlyf(glyphs)
    # recompute lsb from real bounds
    glyf = fb.font["glyf"]
    hm = {}
    for n in order:
        g = glyf[n]
        g.recalcBounds(glyf)
        hm[n] = (metrics[n][0], getattr(g, "xMin", 0))
    fb.setupHorizontalMetrics(hm)
    fb.setupHorizontalHeader(ascent=900, descent=-250)
    full = f"{family} {style}"
    ps = f"{family}-{style.replace(' ', '')}"
    fb.setupNameTable({
        "familyName": family, "styleName": style, "uniqueFontIdentifier": f"{ps}-1.000",
        "fullName": full, "psName": ps, "version": "Version 1.000",
        "copyright": "Copyright (c) 2026 amanedz", "licenseDescription": "SIL Open Font License 1.1",
    })
    fb.setupOS2(sTypoAscender=900, sTypoDescender=-250, sTypoLineGap=100, usWinAscent=1000,
                usWinDescent=300, sxHeight=H, sCapHeight=H, achVendID="NONE",
                fsSelection=(0x01 if skew else 0x40), usWeightClass=700)
    fb.setupPost(italicAngle=-skew)
    from fontTools.misc.timeTools import timestampNow
    fb.setupHead(unitsPerEm=UPM, macStyle=(0x2 if skew else 0) | 0x1, created=timestampNow(), modified=timestampNow())

    os.makedirs(OUT, exist_ok=True)
    ttf = os.path.join(OUT, f"{ps}.ttf")
    fb.save(ttf)
    f = TTFont(ttf)
    f.flavor = "woff2"
    f.save(os.path.join(OUT, f"{ps}.woff2"))
    print("wrote", ttf, len(G), "glyphs")


if __name__ == "__main__":
    build("Regular")
    build("Oblique", skew=12)
    build("Slit", slitted=True)
    build("Slit Oblique", slitted=True, skew=12)
