"""
layout.py – Farben, Schriften, gemeinsame Zeichenfunktionen
"""
import math
import os
import tempfile
import atexit
import shutil

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
FONT_MONO = "Courier-Bold"

# ── Emoji-Rendering via Pillow ────────────────────────────────
_EMOJI_FONT_PATH = os.environ.get("MATHEBUCH_EMOJI_FONT", "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf")
_EMOJI_FONT_SIZE = 109  # NotoColorEmoji is a bitmap font – only 109px works
_emoji_cache: dict[str, str] = {}
_emoji_tmpdir = tempfile.mkdtemp(prefix="mathebuch_emoji_")


def _cleanup_emoji_tmpdir():
    """Removes the temporary directory for emoji images on exit."""
    if os.path.exists(_emoji_tmpdir):
        shutil.rmtree(_emoji_tmpdir)


atexit.register(_cleanup_emoji_tmpdir)


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
    # Illustrationsfarben
    "euli_body":    HexColor("#8B6914"),
    "euli_belly":   HexColor("#F5DEB3"),
    "euli_wing":    HexColor("#7A5C10"),
    "hand_skin":    HexColor("#FDBCB4"),
    "hand_outline": HexColor("#D4967E"),
    "gold_dark":    HexColor("#E6B800"),
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


def draw_header(c, titel, untertitel, emoji, farb_key, erklaerung_seite=None):
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
    # Verweis auf Erklärungsseite
    if erklaerung_seite is not None:
        ref_text = f"Erklärung: S.{erklaerung_seite}"
        c.setFont(FONT, 8)
        tw = c.stringWidth(ref_text, FONT, 8)
        rx = W - 1.5*cm - tw - 0.5*cm
        ry = H - 1.55*cm
        # Small rounded background
        c.setFillColor(white)
        c.setStrokeColor(white)
        c.roundRect(rx - 0.15*cm, ry - 0.12*cm, tw + 0.3*cm, 0.5*cm,
                    radius=4, fill=1, stroke=0)
        c.setFillColor(col)
        c.drawString(rx, ry, ref_text)


def draw_section_label(c, text, farb_key, y, schwierigkeit=0):
    """Farbige Abschnittsüberschrift mit optionaler Schwierigkeitsanzeige (1-3 Sterne)."""
    c.setFillColor(FARBEN[farb_key])
    c.roundRect(1.5*cm, y, 10*cm, 0.8*cm, radius=6, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont(FONT_BOLD, 12)
    c.drawString(2.0*cm, y + 0.22*cm, text)
    # Schwierigkeitssterne rechts neben dem Label
    if schwierigkeit and 1 <= schwierigkeit <= 3:
        star_x = 11.8*cm
        star_cy = y + 0.4*cm
        c.setFillColor(FARBEN["yellow"])
        for i in range(schwierigkeit):
            _draw_star_shape(c, star_x + i * 0.5*cm, star_cy, 0.16*cm, 0.07*cm)
        # Leere Sterne für die restlichen
        c.setFillColor(FARBEN["hellgrau"])
        for i in range(schwierigkeit, 3):
            _draw_star_shape(c, star_x + i * 0.5*cm, star_cy, 0.16*cm, 0.07*cm)


def draw_answer_box(c, x, y, w=2.0*cm, h=1.5*cm):
    """Zeichnet ein hellblaues Feld für die Lösung."""
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
    c.drawCentredString(W / 2, 1.0*cm, str(n))
    if show_stars:
        draw_stars(c, W - 7*cm, 1.5*cm)
        # Kleiner Pokal neben den Sternen
        from illustrationen import draw_mini_pokal
        draw_mini_pokal(c, W - 7.5*cm, 1.7*cm, size=0.8)


def draw_follows_arrow(c, x, y, size=0.6*cm, color=None):
    """Draws a 'follows' arrow (==>) manually using lines and a triangle."""
    if color:
        c.setStrokeColor(color)
        c.setFillColor(color)
    
    c.setLineWidth(2.5)
    # The arrow is composed of two parallel lines and a triangle tip
    # Vertical center is at 'y + 0.15*cm' to roughly align with text baseline center
    base_y = y + 0.18*cm
    
    # Draw double line part
    c.line(x, base_y - 0.06*cm, x + size * 0.6, base_y - 0.06*cm)
    c.line(x, base_y + 0.06*cm, x + size * 0.6, base_y + 0.06*cm)
    
    # Draw triangle tip
    tip_x = x + size
    tip_y = base_y
    path = c.beginPath()
    path.moveTo(x + size * 0.5, base_y + size * 0.3)
    path.lineTo(tip_x, tip_y)
    path.lineTo(x + size * 0.5, base_y - size * 0.3)
    path.close()
    c.drawPath(path, fill=1, stroke=1)


def draw_rotation_arrow(c, cx, cy, radius, start_angle, extent, color=None):
    """Draws a curved rotation arrow along an arc."""
    if color:
        c.setStrokeColor(color)
        c.setFillColor(color)
    
    c.setLineWidth(1.5)
    # Draw the arc
    c.arc(cx - radius, cy - radius, cx + radius, cy + radius,
          startAng=start_angle, extent=extent)
    
    # Draw arrow tip at the end of the arc
    # Calculate end position
    end_angle_rad = math.radians(start_angle + extent)
    tx = cx + radius * math.cos(end_angle_rad)
    ty = cy + radius * math.sin(end_angle_rad)
    
    # Simple triangle tip oriented tangent to the circle
    c.saveState()
    c.translate(tx, ty)
    # Flip tip direction for clockwise (negative extent) vs counter-clockwise
    if extent >= 0:
        c.rotate(start_angle + extent + 90)
    else:
        c.rotate(start_angle + extent - 90)

    tip_size = 0.25*cm
    path = c.beginPath()
    path.moveTo(-tip_size/2, 0)
    path.lineTo(tip_size/2, 0)
    path.lineTo(0, tip_size)
    path.close()
    c.drawPath(path, fill=1, stroke=1)
    c.restoreState()
