"""
layout.py – Farben, Schriften, gemeinsame Zeichenfunktionen
"""
from reportlab.lib.colors import HexColor, white
from reportlab.lib.units import cm
from reportlab.lib.pagesizes import A4

W, H = A4

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
    "grau":     HexColor("#AAAAAA"),
    "hellgrau": HexColor("#DDDDDD"),
}

RAND_FARBEN = [
    FARBEN["yellow"], FARBEN["orange"], FARBEN["blau"],
    FARBEN["gruen"],  FARBEN["pink"],   FARBEN["purple"],
]


def draw_page_bg(c):
    """Cremefarbener Hintergrund mit buntem Randmuster."""
    c.setFillColor(FARBEN["bg"])
    c.rect(0, 0, W, H, fill=1, stroke=0)
    sq = 18
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
    c.setFillColor(FARBEN["dunkel"])
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(2.8*cm, H - 2.55*cm, emoji)
    # Texte
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 20)
    c.drawString(4.2*cm, H - 2.2*cm, titel)
    c.setFont("Helvetica", 12)
    c.drawString(4.2*cm, H - 2.8*cm, untertitel)


def draw_name_date(c):
    """Name- und Datumsfelder."""
    y = H - 4.5*cm
    c.setStrokeColor(FARBEN["hellgrau"])
    c.setFillColor(white)
    c.roundRect(1.5*cm, y - 0.7*cm, 8*cm,   0.9*cm, radius=6, fill=1, stroke=1)
    c.roundRect(11*cm,  y - 0.7*cm, 8.5*cm, 0.9*cm, radius=6, fill=1, stroke=1)
    c.setFillColor(FARBEN["grau"])
    c.setFont("Helvetica", 9)
    c.drawString(1.8*cm, y - 0.2*cm, "Name:")
    c.drawString(11.3*cm, y - 0.2*cm, "Datum:")


def draw_section_label(c, text, farb_key, y):
    """Farbige Abschnittsüberschrift."""
    c.setFillColor(FARBEN[farb_key])
    c.roundRect(1.5*cm, y, 10*cm, 0.8*cm, radius=6, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2*cm, y + 0.18*cm, text)


def draw_answer_box(c, x, y, w=1.6*cm, h=1.1*cm):
    """Hellblaues Antwortfeld."""
    c.setFillColor(FARBEN["antwort"])
    c.setStrokeColor(FARBEN["blau"])
    c.setLineWidth(1.5)
    c.roundRect(x, y, w, h, radius=5, fill=1, stroke=1)


def draw_stars(c, x, y):
    """Drei Sterne-Bewertungsfelder."""
    c.setFillColor(FARBEN["grau"])
    c.setFont("Helvetica", 9)
    c.drawString(x, y, "Wie war's?")
    for i in range(3):
        c.setFillColor(white)
        c.setStrokeColor(FARBEN["hellgrau"])
        c.setLineWidth(1)
        c.rect(x + 2*cm + i*1.1*cm, y - 0.15*cm, 0.9*cm, 0.85*cm, fill=1, stroke=1)
        c.setFillColor(FARBEN["yellow"])
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(x + 2.45*cm + i*1.1*cm, y + 0.08*cm, "★")


def draw_page_number(c, n, show_stars=True):
    c.setFillColor(FARBEN["dunkel"])
    c.setFont("Helvetica", 9)
    c.drawCentredString(W / 2, 1.2*cm, str(n))
    if show_stars:
        draw_stars(c, W - 7*cm, 1.8*cm)
