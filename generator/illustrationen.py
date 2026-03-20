"""
illustrationen.py – Kindgerechte Illustrationen mit ReportLab-Zeichenprimitiven

Enthält:
- Eulen-Maskottchen (Euli)
- Hand-Illustrationen (Finger zählen)
- Zählbare Objekte (Sterne, Punkte)
- Pokal/Medaille für Sternebereiche
- Dekorative Eckverzierungen
"""
from reportlab.lib.colors import HexColor, white
from reportlab.lib.units import cm
from reportlab.lib.pagesizes import A4
import math

from layout import FARBEN, RAND_FARBEN, FONT_BOLD

W, H = A4

# ── Konfigurations-Konstanten ───────────────────────────────────────
THUMB_ROTATION_ANGLE = 30
STAR_INNER_RADIUS_FACTOR = 0.45
CORNER_DECORATION_LINE_WIDTH = 1.5


# ── Euli, das Eulen-Maskottchen ──────────────────────────────────────

def draw_euli(c, cx, cy, size=1.0):
    """Zeichnet eine einfache, freundliche Eule.

    cx, cy = Mittelpunkt; size = Skalierungsfaktor (1.0 ≈ 3cm hoch).
    """
    s = size
    body_color = FARBEN["euli_body"]
    belly_color = FARBEN["euli_belly"]
    eye_white = white
    pupil_color = FARBEN["dunkel"]
    beak_color = FARBEN["orange"]
    feet_color = beak_color

    # Körper (Ellipse als breites Oval)
    c.saveState()
    c.setFillColor(body_color)
    # Körper: breites Oval
    bw = 1.3 * cm * s
    bh = 1.6 * cm * s
    c.ellipse(cx - bw, cy - bh, cx + bw, cy + bh * 0.4, fill=1, stroke=0)

    # Bauch (helleres Oval)
    c.setFillColor(belly_color)
    belly_w = 0.9 * cm * s
    belly_h = 1.0 * cm * s
    c.ellipse(cx - belly_w, cy - bh + 0.2 * cm * s,
              cx + belly_w, cy - bh + belly_h + 0.2 * cm * s,
              fill=1, stroke=0)

    # Kopf (Kreis)
    head_cy = cy + bh * 0.2
    head_r = 1.1 * cm * s
    c.setFillColor(body_color)
    c.circle(cx, head_cy, head_r, fill=1, stroke=0)

    # Ohren (kleine Dreiecke)
    ear_size = 0.5 * cm * s
    for dx in [-0.7, 0.7]:
        ear_x = cx + dx * cm * s
        ear_base_y = head_cy + head_r * 0.6
        c.setFillColor(body_color)
        p = c.beginPath()
        p.moveTo(ear_x - ear_size * 0.5, ear_base_y)
        p.lineTo(ear_x, ear_base_y + ear_size)
        p.lineTo(ear_x + ear_size * 0.5, ear_base_y)
        p.close()
        c.drawPath(p, fill=1, stroke=0)

    # Augen (weiße Kreise mit Pupillen)
    eye_r = 0.38 * cm * s
    pupil_r = 0.18 * cm * s
    for dx in [-0.45, 0.45]:
        ex = cx + dx * cm * s
        ey = head_cy + 0.05 * cm * s
        c.setFillColor(eye_white)
        c.circle(ex, ey, eye_r, fill=1, stroke=0)
        # Pupille
        c.setFillColor(pupil_color)
        c.circle(ex + 0.04 * cm * s, ey + 0.02 * cm * s, pupil_r, fill=1, stroke=0)
        # Glanzpunkt
        c.setFillColor(eye_white)
        c.circle(ex + 0.1 * cm * s, ey + 0.1 * cm * s, 0.06 * cm * s, fill=1, stroke=0)

    # Schnabel
    c.setFillColor(beak_color)
    p = c.beginPath()
    beak_top_y = head_cy - 0.2 * cm * s
    p.moveTo(cx - 0.2 * cm * s, beak_top_y)
    p.lineTo(cx, beak_top_y - 0.3 * cm * s)
    p.lineTo(cx + 0.2 * cm * s, beak_top_y)
    p.close()
    c.drawPath(p, fill=1, stroke=0)

    # Füße
    c.setFillColor(feet_color)
    for dx in [-0.35, 0.35]:
        fx = cx + dx * cm * s
        fy = cy - bh - 0.05 * cm * s
        for toe_dx in [-0.12, 0.0, 0.12]:
            c.circle(fx + toe_dx * cm * s, fy, 0.07 * cm * s, fill=1, stroke=0)

    # Flügel (kleine Bögen an den Seiten)
    c.setFillColor(FARBEN["euli_wing"])
    for side in [-1, 1]:
        wing_x = cx + side * bw * 0.85
        wing_cy = cy - 0.3 * cm * s
        wing_w = 0.35 * cm * s
        wing_h = 0.8 * cm * s
        c.ellipse(wing_x - wing_w, wing_cy - wing_h,
                  wing_x + wing_w, wing_cy + wing_h,
                  fill=1, stroke=0)

    c.restoreState()


def draw_euli_mit_sprechblase(c, cx, cy, text, size=0.8):
    """Zeichnet Euli mit einer Sprechblase."""
    draw_euli(c, cx, cy, size=size)

    # Sprechblase rechts oben
    bub_x = cx + 1.8 * cm * size
    bub_y = cy + 1.2 * cm * size
    bub_w = 4.0 * cm
    bub_h = 1.0 * cm

    c.saveState()
    c.setFillColor(white)
    c.setStrokeColor(FARBEN["hellgrau"])
    c.setLineWidth(1)
    c.roundRect(bub_x, bub_y - bub_h / 2, bub_w, bub_h, radius=8, fill=1, stroke=1)

    # Kleines Dreieck als Pfeil zur Eule
    c.setFillColor(white)
    p = c.beginPath()
    p.moveTo(bub_x, bub_y - 0.1 * cm)
    p.lineTo(bub_x - 0.3 * cm, bub_y - 0.3 * cm)
    p.lineTo(bub_x, bub_y - 0.4 * cm)
    p.close()
    c.drawPath(p, fill=1, stroke=0)

    # Text
    c.setFillColor(FARBEN["dunkel"])
    c.setFont(FONT_BOLD, 9)
    c.drawCentredString(bub_x + bub_w / 2, bub_y - 0.12 * cm, text)
    c.restoreState()


# ── Hand-Illustrationen (Finger zählen) ─────────────────────────────

def draw_hand(c, cx, cy, num_fingers=5, size=1.0):
    """Zeichnet eine stilisierte Hand mit num_fingers ausgestreckten Fingern.

    num_fingers: 1-5 Finger, die gezeigt werden.
    """
    s = size
    skin = FARBEN["hand_skin"]
    outline = FARBEN["hand_outline"]

    c.saveState()
    c.setFillColor(skin)
    c.setStrokeColor(outline)
    c.setLineWidth(1.5 * s)

    # Handfläche
    palm_w = 1.0 * cm * s
    palm_h = 1.0 * cm * s
    c.roundRect(cx - palm_w / 2, cy - palm_h / 2, palm_w, palm_h,
                radius=4 * s, fill=1, stroke=1)

    # Finger
    finger_w = 0.18 * cm * s
    finger_h_up = 0.7 * cm * s     # ausgestreckt
    finger_h_down = 0.2 * cm * s   # eingeklappt
    finger_positions = [-0.35, -0.17, 0.0, 0.17, 0.35]

    for i, fx_offset in enumerate(finger_positions):
        fx = cx + fx_offset * cm * s
        is_up = (i < num_fingers)
        fh = finger_h_up if is_up else finger_h_down
        fy = cy + palm_h / 2

        c.roundRect(fx - finger_w / 2, fy, finger_w, fh,
                    radius=2 * s, fill=1, stroke=1)

    # Daumen (seitlich, immer ausgestreckt wenn num_fingers >= 1)
    if num_fingers >= 1:
        thumb_w = 0.2 * cm * s
        thumb_h = 0.5 * cm * s
        tx = cx - palm_w / 2 - thumb_w * 0.3
        ty = cy + 0.1 * cm * s
        c.saveState()
        c.translate(tx, ty)
        c.rotate(THUMB_ROTATION_ANGLE)
        c.roundRect(-thumb_w / 2, 0, thumb_w, thumb_h,
                    radius=2 * s, fill=1, stroke=1)
        c.restoreState()

    c.restoreState()


def draw_zwei_haende(c, cx, cy, size=1.0):
    """Zeichnet zwei Hände mit je 5 Fingern (= 10 Finger)."""
    gap = 1.5 * cm * size
    draw_hand(c, cx - gap, cy, num_fingers=5, size=size)
    draw_hand(c, cx + gap, cy, num_fingers=5, size=size)


# ── Zählbare Objekte ─────────────────────────────────────────────────

def draw_zaehlbare_sterne(c, cx, cy, count=20, size=1.0):
    """Zeichnet eine Gruppe von kleinen Sternen in Reihen zum Zählen."""
    s = size
    cols = min(count, 10)
    rows = math.ceil(count / 10)
    gap_x = 0.7 * cm * s
    gap_y = 0.8 * cm * s
    star_r = 0.22 * cm * s

    total_w = (cols - 1) * gap_x
    total_h = (rows - 1) * gap_y

    colors = [FARBEN["yellow"], FARBEN["orange"], FARBEN["pink"],
              FARBEN["gruen"], FARBEN["blau"], FARBEN["purple"]]

    drawn = 0
    for row in range(rows):
        items_in_row = min(cols, count - drawn)
        row_w = (items_in_row - 1) * gap_x
        for col in range(items_in_row):
            sx = cx - row_w / 2 + col * gap_x
            sy = cy + total_h / 2 - row * gap_y
            color = colors[(row * cols + col) % len(colors)]
            _draw_star(c, sx, sy, star_r, color)
            drawn += 1


def _draw_star(c, cx, cy, r, color):
    """Zeichnet einen 5-zackigen Stern."""
    c.saveState()
    c.setFillColor(color)
    p = c.beginPath()
    for i in range(10):
        angle = math.radians(90 + i * 36)
        radius = r if i % 2 == 0 else r * STAR_INNER_RADIUS_FACTOR
        x = cx + radius * math.cos(angle)
        y = cy + radius * math.sin(angle)
        if i == 0:
            p.moveTo(x, y)
        else:
            p.lineTo(x, y)
    p.close()
    c.drawPath(p, fill=1, stroke=0)
    c.restoreState()


# ── Pokal / Medaille ─────────────────────────────────────────────────

def draw_mini_pokal(c, cx, cy, size=1.0):
    """Zeichnet einen kleinen Pokal neben dem Sterne-Bereich."""
    s = size
    gold = FARBEN["yellow"]
    gold_dark = FARBEN["gold_dark"]

    c.saveState()

    # Sockel
    c.setFillColor(gold_dark)
    base_w = 0.5 * cm * s
    base_h = 0.12 * cm * s
    c.rect(cx - base_w / 2, cy - 0.4 * cm * s, base_w, base_h, fill=1, stroke=0)

    # Stiel
    c.setFillColor(gold_dark)
    stem_w = 0.1 * cm * s
    stem_h = 0.25 * cm * s
    c.rect(cx - stem_w / 2, cy - 0.4 * cm * s + base_h,
           stem_w, stem_h, fill=1, stroke=0)

    # Kelch
    c.setFillColor(gold)
    cup_bottom_y = cy - 0.4 * cm * s + base_h + stem_h
    cup_w = 0.55 * cm * s
    cup_h = 0.45 * cm * s
    # Trapez-Form: unten schmal, oben breit
    p = c.beginPath()
    p.moveTo(cx - cup_w * 0.35, cup_bottom_y)
    p.lineTo(cx - cup_w * 0.5, cup_bottom_y + cup_h)
    p.lineTo(cx + cup_w * 0.5, cup_bottom_y + cup_h)
    p.lineTo(cx + cup_w * 0.35, cup_bottom_y)
    p.close()
    c.drawPath(p, fill=1, stroke=0)

    # Henkel
    c.setStrokeColor(gold_dark)
    c.setLineWidth(1.2 * s)
    for side in [-1, 1]:
        hx = cx + side * cup_w * 0.5
        handle_cy = cup_bottom_y + cup_h * 0.55
        c.arc(hx - 0.12 * cm * s * side, handle_cy - 0.15 * cm * s,
              hx + 0.12 * cm * s * side, handle_cy + 0.15 * cm * s,
              startAng=180 if side == 1 else 0, extent=180)

    # Kleiner Stern auf dem Pokal
    _draw_star(c, cx, cup_bottom_y + cup_h * 0.5, 0.08 * cm * s, white)

    c.restoreState()


# ── Dekorative Eckverzierungen ───────────────────────────────────────

def draw_eckverzierungen(c, farb_key="blau"):
    """Zeichnet dezente Kreisbögen und Punkte in den Ecken der Seite."""
    color = FARBEN[farb_key]
    light_color = FARBEN.get("hellgrau", FARBEN["grau"])

    c.saveState()
    c.setStrokeColor(color)
    c.setLineWidth(CORNER_DECORATION_LINE_WIDTH)

    r = 1.2 * cm
    inset = 0.6 * cm

    # Vier Ecken: Viertelkreis-Bogen + kleiner Punkt
    corners = [
        (inset, H - inset, 270, 90),          # oben-links
        (W - inset, H - inset, 180, 90),       # oben-rechts
        (inset, inset, 0, 90),                  # unten-links
        (W - inset, inset, 90, 90),             # unten-rechts
    ]

    for cx, cy, start, extent in corners:
        c.arc(cx - r, cy - r, cx + r, cy + r,
              startAng=start, extent=extent)

    # Kleine dekorative Punkte in den Ecken
    dot_r = 0.08 * cm
    c.setFillColor(color)
    dot_inset = 1.0 * cm
    for dx, dy in [(dot_inset, H - dot_inset), (W - dot_inset, H - dot_inset),
                   (dot_inset, dot_inset), (W - dot_inset, dot_inset)]:
        c.circle(dx, dy, dot_r, fill=1, stroke=0)

    c.restoreState()


# ── Separator-Seiten-Illustrationen ──────────────────────────────────

def draw_separator_illustration(c, section, cx, cy, size=1.0):
    """Zeichnet die passende Illustration für eine Trennseite.

    section: 5, 10, oder 20
    """
    if section == 5:
        draw_hand(c, cx, cy, num_fingers=5, size=size * 1.3)
    elif section == 10:
        draw_zwei_haende(c, cx, cy, size=size * 1.1)
    elif section == 20:
        draw_zaehlbare_sterne(c, cx, cy, count=20, size=size * 1.0)
