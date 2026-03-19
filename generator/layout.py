"""
layout.py – Farben, Schriften, gemeinsame Zeichenfunktionen
"""
import math
import os
import tempfile

from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.colors import HexColor, white
from reportlab.lib.units import cm
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

W, H = A4

# ── Schriften registrieren ────────────────────────────────────
pdfmetrics.registerFont(TTFont("Andika", "/usr/share/fonts/truetype/andika/Andika-Regular.ttf"))
pdfmetrics.registerFont(TTFont("Andika-Bold", "/usr/share/fonts/truetype/andika/Andika-Bold.ttf"))
pdfmetrics.registerFont(TTFont("Andika-Italic", "/usr/share/fonts/truetype/andika/Andika-Italic.ttf"))
pdfmetrics.registerFont(TTFont("Andika-BoldItalic", "/usr/share/fonts/truetype/andika/Andika-BoldItalic.ttf"))

pdfmetrics.registerFontFamily(
    "Andika",
    normal="Andika",
    bold="Andika-Bold",
    italic="Andika-Italic",
    boldItalic="Andika-BoldItalic",
)

# Schrift-Konstanten (zentral, damit alle Module dieselben Namen nutzen)
FONT = "Andika"
FONT_BOLD = "Andika-Bold"
FONT_ITALIC = "Andika-Italic"

# ── Emoji-Rendering via Pillow ────────────────────────────────
_EMOJI_FONT_PATH = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
_EMOJI_FONT_SIZE = 109  # NotoColorEmoji is a bitmap font – only 109px works
_emoji_cache: dict[str, str] = {}
_emoji_tmpdir = tempfile.mkdtemp(prefix="mathebuch_emoji_")


def _render_emoji_to_file(emoji_char: str) -> str:
    """Renders a single emoji character to a temp PNG file, returns its path."""
    if emoji_char in _emoji_cache:
        return _emoji_cache[emoji_char]
    font = ImageFont.truetype(_EMOJI_FONT_PATH, _EMOJI_FONT_SIZE)
    # Measure the emoji
    bbox = font.getbbox(emoji_char)
    img_w = bbox[2] - bbox[0] + 20
    img_h = bbox[3] - bbox[1] + 20
    img = Image.new("RGBA", (img_w, img_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.text((-bbox[0] + 10, -bbox[1] + 10), emoji_char, font=font, embedded_color=True)
    # Crop to content
    content_bbox = img.getbbox()
    if content_bbox:
        img = img.crop(content_bbox)
    codepoints = "_".join(f"{ord(ch):x}" for ch in emoji_char)
    path = os.path.join(_emoji_tmpdir, f"emoji_{codepoints}.png")
    img.save(path)
    _emoji_cache[emoji_char] = path
    return path


def draw_emoji(c, emoji_char, cx, cy, size):
    """Draws an emoji centered at (cx, cy) with the given size (in points)."""
    path = _render_emoji_to_file(emoji_char)
    half = size / 2
    c.drawImage(path, cx - half, cy - half, width=size, height=size,
                preserveAspectRatio=True, mask="auto")


# ── Farbpalette ────────────────────────────────────────────
FARBEN = {
    "bg":       HexColor("#FFFDF5"),
    "yellow":   HexColor("#FFD94A"),
    "orange":   HexColor("#FF8C42"),
    "blau":     HexColor("#4ABFFF"),
    "gruen":    HexColor("#62D67A"),
    "pink":     HexColor("#FF6B9D"),
    "purple":   HexColor("#A78BFA"),
    "dunkel":   HexColor("#2D2A3E"),
    "antwort":  HexColor("#E8F4FF"),
    "grau":       HexColor("#AAAAAA"),
    "hellgrau":   HexColor("#DDDDDD"),
    "hellorange": HexColor("#FFF0E8"),
    "tipp_bg":    HexColor("#FFFBEA"),
}

RAND_FARBEN = [
    FARBEN["yellow"], FARBEN["orange"], FARBEN["blau"],
    FARBEN["gruen"],  FARBEN["pink"],   FARBEN["purple"],
]


def draw_page_bg(c):
    """Cremefarbener Hintergrund mit buntem Randmuster."""
    c.setFillColor(FARBEN["bg"])
    c.rect(0, 0, W, H, fill=1, stroke=0)
    sq = 18  # border square size in points
    colors = RAND_FARBEN * 2
    for i, col in enumerate(colors):
        c.setFillColor(col)
        c.rect(i * sq,          H - sq, sq, sq, fill=1, stroke=0)
        c.rect(W - (i+1)*sq,    H - sq, sq, sq, fill=1, stroke=0)
        c.rect(i * sq,          0,      sq, sq, fill=1, stroke=0)
        c.rect(W - (i+1)*sq,    0,      sq, sq, fill=1, stroke=0)


def draw_header(c, titel, untertitel, emoji, farb_key):
    """Farbiges Banner mit Titel oben auf der Seite."""
    col = FARBEN[farb_key]
    c.setFillColor(col)
    c.roundRect(1.5*cm, H - 3.5*cm, W - 3*cm, 2.2*cm, radius=12, fill=1, stroke=0)
    # Emoji-Kreis
    c.setFillColor(white)
    c.circle(2.8*cm, H - 2.4*cm, 0.7*cm, fill=1, stroke=0)
    draw_emoji(c, emoji, 2.8*cm, H - 2.4*cm, 0.9*cm)
    # Texte
    c.setFillColor(white)
    c.setFont(FONT_BOLD, 20)
    c.drawString(4.2*cm, H - 2.2*cm, titel)
    c.setFont(FONT, 12)
    c.drawString(4.2*cm, H - 2.8*cm, untertitel)


def draw_section_label(c, text, farb_key, y):
    """Farbige Abschnittsüberschrift."""
    c.setFillColor(FARBEN[farb_key])
    c.roundRect(1.5*cm, y, 10*cm, 0.8*cm, radius=6, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont(FONT_BOLD, 12)
    c.drawString(2*cm, y + 0.18*cm, text)


def draw_answer_box(c, x, y, w=1.6*cm, h=1.1*cm):
    """Hellblaues Antwortfeld."""
    c.setFillColor(FARBEN["antwort"])
    c.setStrokeColor(FARBEN["blau"])
    c.setLineWidth(1.5)
    c.roundRect(x, y, w, h, radius=5, fill=1, stroke=1)


def _draw_star_shape(c, cx, cy, outer_r, inner_r):
    """Draws a 5-pointed star polygon centered at (cx, cy)."""
    points = []
    for i in range(10):
        angle = math.radians(90 + i * 36)
        r = outer_r if i % 2 == 0 else inner_r
        points.append(cx + r * math.cos(angle))
        points.append(cy + r * math.sin(angle))
    p = c.beginPath()
    p.moveTo(points[0], points[1])
    for j in range(2, len(points), 2):
        p.lineTo(points[j], points[j + 1])
    p.close()
    c.drawPath(p, fill=1, stroke=0)


def draw_stars(c, x, y):
    """Drei Sterne-Bewertungsfelder."""
    c.setFillColor(FARBEN["grau"])
    c.setFont(FONT, 9)
    c.drawString(x, y, "Wie war's?")
    for i in range(3):
        c.setFillColor(white)
        c.setStrokeColor(FARBEN["hellgrau"])
        c.setLineWidth(1)
        c.rect(x + 2*cm + i*1.1*cm, y - 0.15*cm, 0.9*cm, 0.85*cm, fill=1, stroke=1)
        c.setFillColor(FARBEN["yellow"])
        _draw_star_shape(c, x + 2.45*cm + i*1.1*cm, y + 0.2*cm, 0.22*cm, 0.09*cm)


def draw_page_number(c, n, show_stars=True):
    c.setFillColor(FARBEN["dunkel"])
    c.setFont(FONT, 9)
    c.drawCentredString(W / 2, 1.2*cm, str(n))
    if show_stars:
        draw_stars(c, W - 7*cm, 1.8*cm)
