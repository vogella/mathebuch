"""
aufgabentypen.py – Zeichenfunktionen für jeden Aufgabentyp
"""
import random as _rnd
import math
from reportlab.lib.colors import HexColor, white
from reportlab.lib.units import cm
from reportlab.lib.pagesizes import A4
from layout import FARBEN, draw_answer_box, draw_section_label, FONT, FONT_BOLD, FONT_ITALIC

W, H = A4


def _wrap_text(c, text, font_name, font_size, max_width):
    """Word-wrap text to fit within max_width. Returns list of lines."""
    words = text.split()
    lines = []
    line = ""
    for w in words:
        test = (line + " " + w).strip()
        if c.stringWidth(test, font_name, font_size) > max_width:
            lines.append(line)
            line = w
        else:
            line = test
    if line:
        lines.append(line)
    return lines


def _draw_zerlegung_part(c, cx, cy, circle_r, val, is_blank, is_loesung, farb_key):
    """Draw a single part circle in a Zahlzerlegung exercise."""
    if is_blank:
        c.setFillColor(FARBEN["antwort"])
        c.setStrokeColor(FARBEN[farb_key])
        c.setLineWidth(1.5)
        c.circle(cx, cy, circle_r, fill=1, stroke=1)
    elif is_loesung:
        c.setFillColor(FARBEN["antwort"])
        c.setStrokeColor(FARBEN[farb_key])
        c.setLineWidth(1.5)
        c.circle(cx, cy, circle_r, fill=1, stroke=1)
        c.setFillColor(FARBEN["gruen"])
        c.setFont(FONT_BOLD, 16)
        c.drawCentredString(cx, cy - 0.2*cm, str(val))
    else:
        c.setFillColor(FARBEN[farb_key])
        c.circle(cx, cy, circle_r, fill=1, stroke=0)
        c.setFillColor(white)
        c.setFont(FONT_BOLD, 16)
        c.drawCentredString(cx, cy - 0.2*cm, str(val))


def _draw_beschreibung(c, abschnitt, start_y):
    """Draws optional beschreibung text below section label. Returns y offset."""
    beschreibung = abschnitt.get("beschreibung")
    if not beschreibung:
        return 0
    c.setFillColor(FARBEN["dunkel"])
    c.setFont(FONT, 10)
    max_w = W - 4*cm
    # Word-wrap with explicit \n support
    lines = []
    for paragraph in beschreibung.split("\n"):
        wrapped = _wrap_text(c, paragraph, FONT, 10, max_w)
        if wrapped:
            lines.extend(wrapped)
        else:
            lines.append("")
    for i, l in enumerate(lines):
        c.drawString(2*cm, start_y - 0.9*cm - i * 0.45*cm, l)
    return 0.45*cm * len(lines) + 0.25*cm


# ── Erklärung ─────────────────────────────────────────────

def draw_erklaerung(c, abschnitt, farb_key, start_y):
    """Draws an explanation block with title and text lines."""
    draw_section_label(c, abschnitt["titel"], farb_key, start_y)

    zeilen = abschnitt.get("zeilen", [])
    y = start_y - 1.2*cm

    for zeile in zeilen:
        if zeile.startswith("##"):
            # Sub-heading
            c.setFillColor(FARBEN[farb_key])
            c.setFont(FONT_BOLD, 12)
            c.drawString(2*cm, y, zeile[2:].strip())
            y -= 0.7*cm
        elif zeile.startswith("**"):
            # Bold example line
            c.setFillColor(FARBEN["dunkel"])
            c.setFont(FONT_BOLD, 11)
            c.drawString(2.5*cm, y, zeile.strip().strip('*').strip())
            y -= 0.6*cm
        else:
            c.setFillColor(FARBEN["dunkel"])
            c.setFont(FONT, 10)
            c.drawString(2.5*cm, y, zeile)
            y -= 0.55*cm

    return y - 0.3*cm


# ── Lückenaufgaben ─────────────────────────────────────────

def draw_lückenaufgaben(c, abschnitt, farb_key, start_y):
    """
    Zeichnet zwei Spalten mit Lückenaufgaben.
    Jede Aufgabe ist [a, op, b, ergebnis], wobei None = Lücke.
    """
    draw_section_label(c, abschnitt["titel"], farb_key, start_y)
    y_off = _draw_beschreibung(c, abschnitt, start_y)

    aufgaben = abschnitt["aufgaben"]
    loesungen = abschnitt.get("loesungen", [None] * len(aufgaben))
    halb = (len(aufgaben) + 1) // 2
    col1 = aufgaben[:halb]
    col2 = aufgaben[halb:]
    loes1 = loesungen[:halb]
    loes2 = loesungen[halb:]

    row_y = start_y - 1.5*cm - y_off
    row_h = 1.5*cm

    for i, aufg in enumerate(col1):
        _draw_aufgabe_row(c, 1.8*cm, row_y - i * row_h, aufg, farb_key, loes1[i])
    for i, aufg in enumerate(col2):
        _draw_aufgabe_row(c, 11*cm, row_y - i * row_h, aufg, farb_key, loes2[i])

    return row_y - halb * row_h - 0.5*cm   # nächste freie Y-Position


def _draw_filled_answer_box(c, x, y, text, w=2.0*cm, h=1.5*cm):
    """Answer box with a solution value shown inside."""
    draw_answer_box(c, x, y, w, h)
    c.setFillColor(FARBEN["gruen"])
    c.setFont(FONT_BOLD, 16)
    c.drawCentredString(x + w/2, y + h/2 - 0.2*cm, str(text))


def _draw_aufgabe_row(c, x, y, aufg, farb_key, loesung=None):
    a, op, b, ergebnis = aufg
    op_col = FARBEN[farb_key]
    dunkel = FARBEN["dunkel"]

    c.setFont(FONT_BOLD, 20)
    x0 = x

    # a
    if a is not None:
        c.setFillColor(dunkel)
        c.drawCentredString(x0 + 0.6*cm, y, str(a))
        x0 += 1.5*cm
    else:
        if loesung is not None:
            _draw_filled_answer_box(c, x0, y - 0.25*cm, loesung[0])
        else:
            draw_answer_box(c, x0, y - 0.25*cm)
        x0 += 1.9*cm

    # Operator
    c.setFillColor(op_col)
    c.drawCentredString(x0, y, str(op))
    x0 += 1.1*cm

    # b
    if b is not None:
        c.setFillColor(dunkel)
        c.drawCentredString(x0 + 0.6*cm, y, str(b))
        x0 += 1.5*cm
    else:
        if loesung is not None:
            _draw_filled_answer_box(c, x0, y - 0.25*cm, loesung[1])
        else:
            draw_answer_box(c, x0, y - 0.25*cm)
        x0 += 2.3*cm

    # =
    c.setFillColor(op_col)
    c.drawCentredString(x0, y, "=")
    x0 += 1.0*cm

    # Ergebnis
    if ergebnis is not None:
        c.setFillColor(dunkel)
        c.drawCentredString(x0 + 0.6*cm, y, str(ergebnis))
    else:
        if loesung is not None:
            _draw_filled_answer_box(c, x0, y - 0.25*cm, loesung[2])
        else:
            draw_answer_box(c, x0, y - 0.25*cm)


# ── Zahlenhaus ─────────────────────────────────────────────

def draw_zahlenhaus(c, abschnitt, farb_key, start_y):
    draw_section_label(c, abschnitt["titel"], farb_key, start_y)

    # Optional description and hint text
    y_offset = _draw_beschreibung(c, abschnitt, start_y)

    hinweis = abschnitt.get("hinweis", "")
    if hinweis:
        c.setFillColor(FARBEN["grau"])
        c.setFont(FONT_ITALIC, 9)
        c.drawString(2*cm, start_y - 0.9*cm - y_offset, hinweis)
        y_offset += 0.6*cm

    # Verbotene Zahlen mit rotem X
    verboten = abschnitt.get("verboten", [])
    if verboten:
        vx = 2*cm
        vy = start_y - 0.9*cm - y_offset
        c.setFont(FONT_BOLD, 10)
        c.setFillColor(FARBEN["dunkel"])
        c.drawString(vx, vy, "Verboten:")
        vx += 2.2*cm
        for vz in verboten:
            # Circle background
            c.setFillColor(FARBEN["hellgrau"])
            c.circle(vx + 0.4*cm, vy + 0.15*cm, 0.4*cm, fill=1, stroke=0)
            # Red X behind the number
            c.setStrokeColor(HexColor("#FF0000"))
            c.setLineWidth(2.5)
            c.line(vx + 0.05*cm, vy - 0.2*cm, vx + 0.75*cm, vy + 0.5*cm)
            c.line(vx + 0.05*cm, vy + 0.5*cm, vx + 0.75*cm, vy - 0.2*cm)
            # Number drawn on top of the X
            c.setFillColor(FARBEN["dunkel"])
            c.setFont(FONT_BOLD, 12)
            c.drawCentredString(vx + 0.4*cm, vy, str(vz))
            vx += 1.2*cm
        y_offset += 0.8*cm

    dachzahlen = abschnitt["dachzahlen"]
    loesungen = abschnitt.get("loesungen", [None] * len(dachzahlen))
    spacing = (W - 3*cm) / len(dachzahlen)
    hy = start_y - 2.8*cm - y_offset

    for i, dach in enumerate(dachzahlen):
        cx = 1.5*cm + spacing * i + spacing / 2
        _draw_ein_zahlenhaus(c, cx, hy, dach, loesungen[i])

    return hy - 3.5*cm


def _draw_ein_zahlenhaus(c, cx, ty, roof_num, loesung=None):
    roof_size = 1.4*cm
    # Dach
    c.setFillColor(FARBEN["orange"])
    path = c.beginPath()
    path.moveTo(cx, ty)
    path.lineTo(cx - roof_size, ty - roof_size * 0.9)
    path.lineTo(cx + roof_size, ty - roof_size * 0.9)
    path.close()
    c.drawPath(path, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont(FONT_BOLD, 18)
    c.drawCentredString(cx, ty - roof_size * 0.65, str(roof_num))
    # Felder
    box_w = 1.6*cm
    box_h = 1.5*cm
    bx = cx - roof_size
    by = ty - roof_size * 0.9 - box_h
    colors = [FARBEN["antwort"], FARBEN["hellorange"]]
    for j in range(2):
        c.setFillColor(colors[j])
        c.setStrokeColor(FARBEN["orange"])
        c.setLineWidth(1.5)
        c.roundRect(bx + j * box_w, by, box_w, box_h, radius=4, fill=1, stroke=1)
        if loesung is not None:
            c.setFillColor(FARBEN["gruen"])
            c.setFont(FONT_BOLD, 16)
            c.drawCentredString(bx + j * box_w + box_w/2, by + box_h/2 - 0.2*cm,
                                str(loesung[j]))


# ── Rechenraupe ────────────────────────────────────────────

def draw_rechenraupe(c, abschnitt, farb_key, start_y):
    draw_section_label(c, abschnitt["titel"], farb_key, start_y)
    y_off = _draw_beschreibung(c, abschnitt, start_y)

    start_val = abschnitt["start"]
    schritte  = abschnitt["schritte"]
    loesungen = abschnitt.get("loesungen", [])

    # Segmente aufbauen: Zahl, Schritt, Zahl, Schritt, ...
    segmente = [str(start_val)]
    for i, s in enumerate(schritte):
        segmente.append(s)
        if i < len(loesungen):
            segmente.append(str(loesungen[i]))
        else:
            segmente.append("?")

    seg_colors = [FARBEN["gruen"]] + [FARBEN["orange"], FARBEN["blau"]] * len(schritte)

    r = 0.75*cm
    gap = 0.3*cm
    cx_start = 2.2*cm
    cy = start_y - 2.5*cm - y_off

    for i, (seg, col) in enumerate(zip(segmente, seg_colors)):
        cx = cx_start + i * (2*r + gap)
        if i > 0:
            c.setStrokeColor(FARBEN["hellgrau"])
            c.setLineWidth(3)
            c.line(cx - r - gap, cy, cx - r, cy)
        is_answer = seg == "?"
        c.setFillColor(FARBEN["antwort"] if is_answer else col)
        c.setStrokeColor(col if is_answer else HexColor("#00000000"))
        c.setLineWidth(2)
        c.circle(cx, cy, r, fill=1, stroke=1 if is_answer else 0)
        if not is_answer:
            c.setFillColor(white)
            c.setFont(FONT_BOLD, 13 if len(seg) <= 2 else 11)
            c.drawCentredString(cx, cy - 0.2*cm, seg)


    return cy - 2*cm


# ── Magisches Dreieck ──────────────────────────────────────

def _draw_ein_dreieck(c, tx, ty, r_tri, werte, node_r=0.6*cm):
    """Draws a single magic triangle centred at (tx, ty).
    werte: list of 6 values (corners then midpoints). None = answer blank.
    """
    pts = [
        (tx,           ty + r_tri * 1.1),
        (tx - r_tri,   ty - r_tri * 0.55),
        (tx + r_tri,   ty - r_tri * 0.55),
    ]
    mids = [
        ((pts[0][0]+pts[1][0])/2, (pts[0][1]+pts[1][1])/2),
        ((pts[1][0]+pts[2][0])/2, (pts[1][1]+pts[2][1])/2),
        ((pts[0][0]+pts[2][0])/2, (pts[0][1]+pts[2][1])/2),
    ]
    all_pos = pts + mids
    node_colors = [FARBEN["yellow"], FARBEN["blau"], FARBEN["gruen"],
                   FARBEN["pink"],   FARBEN["purple"], FARBEN["orange"]]

    c.setStrokeColor(FARBEN["orange"])
    c.setLineWidth(2.5)
    c.line(*pts[0], *pts[1])
    c.line(*pts[1], *pts[2])
    c.line(*pts[0], *pts[2])

    font_size = 13 if node_r >= 0.5*cm else 11
    for i, (px, py) in enumerate(all_pos):
        val = werte[i] if i < len(werte) else None
        is_blank = val is None
        c.setFillColor(node_colors[i] if not is_blank else FARBEN["antwort"])
        c.setStrokeColor(node_colors[i] if is_blank else HexColor("#00000000"))
        c.setLineWidth(1.5)
        c.circle(px, py, node_r, fill=1, stroke=1 if is_blank else 0)
        c.setFillColor(white if not is_blank else FARBEN["blau"])
        c.setFont(FONT_BOLD, font_size)
        label = str(val) if val is not None else "?"
        c.drawCentredString(px, py - 0.15*cm, label)


def _draw_tipp_box(c, x, y, tipp_zeilen):
    """Draws a tip box with custom lines of text."""
    box_h = max(3*cm, (len(tipp_zeilen) + 1) * 0.65*cm + 1*cm)
    c.setFillColor(FARBEN["tipp_bg"])
    c.setStrokeColor(FARBEN["yellow"])
    c.setLineWidth(1.5)
    c.roundRect(x, y - box_h/2, 6*cm, box_h, radius=8, fill=1, stroke=1)
    c.setFillColor(FARBEN["dunkel"])
    c.setFont(FONT_BOLD, 11)
    top_y = y + box_h/2 - 1*cm
    c.drawString(x + 0.5*cm, top_y, "💡 Tipp:")
    c.setFont(FONT, 10)
    for j, line in enumerate(tipp_zeilen):
        c.drawString(x + 0.5*cm, top_y - (j+1)*0.65*cm, line)


def draw_magisches_dreieck(c, abschnitt, farb_key, start_y):
    draw_section_label(c, abschnitt["titel"], farb_key, start_y)
    y_off = _draw_beschreibung(c, abschnitt, start_y)

    hinweis_text = abschnitt.get("hinweis", "")
    if hinweis_text:
        c.setFillColor(FARBEN["dunkel"])
        c.setFont(FONT, 10)
        c.drawString(2*cm, start_y - 0.9*cm - y_off, hinweis_text)
        y_off += 0.6*cm

    werte = abschnitt.get("werte", [None]*6)
    tipp_zeilen = abschnitt.get("tipp_zeilen", [])

    tx, ty = 8*cm, start_y - 6.5*cm - y_off
    r_tri = 3.5*cm
    _draw_ein_dreieck(c, tx, ty, r_tri, werte)

    if tipp_zeilen:
        _draw_tipp_box(c, 13.5*cm, ty, tipp_zeilen)

    return ty - 3*cm


def draw_magische_dreiecke(c, abschnitt, farb_key, start_y):
    """Draws multiple smaller magic triangles side by side."""
    draw_section_label(c, abschnitt["titel"], farb_key, start_y)
    y_off = _draw_beschreibung(c, abschnitt, start_y)

    dreiecke = abschnitt["dreiecke"]  # list of {zielsumme, werte}
    count = len(dreiecke)
    spacing = (W - 3*cm) / count
    r_tri = min(2.2*cm, spacing * 0.4)
    ty = start_y - 4.5*cm - y_off

    for i, dreieck in enumerate(dreiecke):
        tx = 1.5*cm + spacing * i + spacing / 2
        werte = dreieck.get("werte", [None]*6)
        zielsumme = dreieck.get("zielsumme", "")
        _draw_ein_dreieck(c, tx, ty, r_tri, werte, node_r=0.45*cm)
        # Label above triangle
        label = dreieck.get("label", f"Summe = {zielsumme}")
        c.setFillColor(FARBEN[farb_key])
        c.setFont(FONT_BOLD, 11)
        c.drawCentredString(tx, ty + r_tri * 1.1 + 0.7*cm, label)

    return ty - r_tri - 2*cm


# ── Magisches Quadrat ─────────────────────────────────────

def _draw_ein_quadrat(c, gx, gy, werte, zielsumme, farb_key, cell=1.8*cm, label=None):
    """Draws a single 3x3 magic square grid at position (gx, gy) bottom-left."""
    grid_w = 3 * cell
    node_colors = [
        FARBEN["yellow"], FARBEN["blau"],   FARBEN["gruen"],
        FARBEN["pink"],   FARBEN["purple"], FARBEN["orange"],
        FARBEN["blau"],   FARBEN["gruen"],  FARBEN["yellow"],
    ]

    for idx, val in enumerate(werte):
        row = idx // 3
        col = idx % 3
        cx = gx + col * cell
        cy = gy + (2 - row) * cell
        is_blank = val is None
        c.setFillColor(node_colors[idx] if not is_blank else FARBEN["antwort"])
        c.setStrokeColor(FARBEN[farb_key])
        c.setLineWidth(1.5)
        c.roundRect(cx, cy, cell, cell, radius=5, fill=1, stroke=1)
        c.setFillColor(white if not is_blank else FARBEN["blau"])
        c.setFont(FONT_BOLD, 18)
        lbl = str(val) if val is not None else "?"
        c.drawCentredString(cx + cell/2, cy + cell/2 - 0.2*cm, lbl)

    # Sum indicators on the right and bottom
    c.setFillColor(FARBEN["dunkel"])
    c.setFont(FONT_BOLD, 12)
    for row in range(3):
        cy = gy + (2 - row) * cell + cell/2
        c.drawString(gx + grid_w + 0.3*cm, cy - 0.15*cm, f"→ {zielsumme}")
    for col in range(3):
        cx = gx + col * cell + cell/2
        c.drawCentredString(cx, gy - 0.5*cm, f"↓ {zielsumme}")
    c.drawString(gx + grid_w + 0.3*cm, gy - 0.5*cm, f"↘ {zielsumme}")

    # Optional label above
    if label:
        c.setFillColor(FARBEN[farb_key])
        c.setFont(FONT_BOLD, 11)
        c.drawCentredString(gx + grid_w / 2, gy + 3 * cell + 0.3*cm, label)


def draw_magisches_quadrat(c, abschnitt, farb_key, start_y):
    """Draws a 3x3 magic square, or a pair side by side."""
    draw_section_label(c, abschnitt["titel"], farb_key, start_y)
    y_off = _draw_beschreibung(c, abschnitt, start_y)

    werte = abschnitt["werte"]  # 9 values, None = blank
    tipp_zeilen = abschnitt.get("tipp_zeilen", [])
    paar = abschnitt.get("paar")  # optional second quadrat
    zielsumme = abschnitt.get("zielsumme", "")

    cell = 1.8*cm
    grid_h = 3 * cell

    if paar:
        # Two squares side by side
        cell_s = 1.5*cm
        grid_h_s = 3 * cell_s
        gy = start_y - 2.2*cm - grid_h_s - y_off
        gx1 = 1.5*cm
        gx2 = W / 2 + 0.5*cm
        label1 = paar.get("label_links", "Aufgabe")
        label2 = paar.get("label_rechts", "Lösung")
        werte2 = paar["werte"]
        _draw_ein_quadrat(c, gx1, gy, werte, zielsumme, farb_key, cell_s, label1)
        _draw_ein_quadrat(c, gx2, gy, werte2, zielsumme, farb_key, cell_s, label2)
        return gy - 1.5*cm
    else:
        gx = 2.5*cm
        gy = start_y - 2.2*cm - grid_h - y_off
        _draw_ein_quadrat(c, gx, gy, werte, zielsumme, farb_key, cell)
        if tipp_zeilen:
            _draw_tipp_box(c, 14*cm, gy + grid_h/2, tipp_zeilen)
        return gy - 1.5*cm


# ── Würfelzählen ──────────────────────────────────────────

# Dot positions for dice faces 1–6, in a unit square [0,1]x[0,1]
_WÜRFEL_PUNKTE = {
    1: [(0.5, 0.5)],
    2: [(0.25, 0.75), (0.75, 0.25)],
    3: [(0.25, 0.75), (0.5, 0.5), (0.75, 0.25)],
    4: [(0.25, 0.75), (0.75, 0.75), (0.25, 0.25), (0.75, 0.25)],
    5: [(0.25, 0.75), (0.75, 0.75), (0.5, 0.5), (0.25, 0.25), (0.75, 0.25)],
    6: [(0.25, 0.75), (0.75, 0.75), (0.25, 0.5), (0.75, 0.5), (0.25, 0.25), (0.75, 0.25)],
}


def _draw_würfel(c, x, y, wert, size=1.4*cm):
    """Draws a single die at (x, y) bottom-left corner."""
    c.setFillColor(white)
    c.setStrokeColor(FARBEN["dunkel"])
    c.setLineWidth(1.5)
    c.roundRect(x, y, size, size, radius=4, fill=1, stroke=1)
    dot_r = size * 0.08
    padding = size * 0.15
    inner = size - 2 * padding
    c.setFillColor(FARBEN["dunkel"])
    for (dx, dy) in _WÜRFEL_PUNKTE[wert]:
        cx = x + padding + dx * inner
        cy = y + padding + dy * inner
        c.circle(cx, cy, dot_r, fill=1, stroke=0)


def draw_würfelzählen(c, abschnitt, farb_key, start_y):
    """Draws dice-counting exercises in a grid layout. Supports 2 or 3 dice."""
    draw_section_label(c, abschnitt["titel"], farb_key, start_y)
    y_off = _draw_beschreibung(c, abschnitt, start_y)

    aufgaben = abschnitt["aufgaben"]
    num_dice = len(aufgaben[0])
    default_op = abschnitt.get("operator", "+")
    operatoren_list = abschnitt.get("operatoren", [])

    # Adjust layout based on number of dice
    if num_dice >= 3:
        cols = 1
        dice_size = 1.5*cm
        row_h = 2.6*cm
    else:
        cols = 2
        dice_size = 1.6*cm
        row_h = 2.8*cm

    col_w = (W - 3*cm) / cols
    row_y = start_y - 1.8*cm - y_off

    for idx, aufg in enumerate(aufgaben):
        col = idx % cols
        row = idx // cols
        x0 = 1.5*cm + col * col_w
        y0 = row_y - row * row_h
        cx = x0

        # Per-task operators: "+" or "+, −" for multi-dice
        if idx < len(operatoren_list):
            task_ops = [o.strip() for o in operatoren_list[idx].split(",")]
        else:
            task_ops = [default_op] * (num_dice - 1)

        for di, wert in enumerate(aufg):
            if di > 0:
                # Operator between dice
                op_char = task_ops[di - 1] if di - 1 < len(task_ops) else default_op
                c.setFillColor(FARBEN[farb_key])
                c.setFont(FONT_BOLD, 18)
                c.drawCentredString(cx + 0.4*cm, y0 - dice_size * 0.6, op_char)
                cx += 0.8*cm
            _draw_würfel(c, cx, y0 - dice_size, wert, dice_size)
            cx += dice_size

        # Equals sign and answer box
        c.setFillColor(FARBEN[farb_key])
        c.setFont(FONT_BOLD, 18)
        c.drawCentredString(cx + 0.5*cm, y0 - dice_size * 0.6, "=")
        loesungen = abschnitt.get("loesungen", [])
        if idx < len(loesungen):
            _draw_filled_answer_box(c, cx + 0.9*cm, y0 - dice_size * 0.85,
                                    loesungen[idx], w=1.6*cm, h=1.5*cm)
        else:
            draw_answer_box(c, cx + 0.9*cm, y0 - dice_size * 0.85, w=1.6*cm, h=1.5*cm)

    total_rows = (len(aufgaben) + cols - 1) // cols
    return row_y - total_rows * row_h - 0.3*cm


# ── Rechenmauer ───────────────────────────────────────────

def draw_rechenmauer(c, abschnitt, farb_key, start_y):
    """Number wall: each brick = sum of the two below it."""
    draw_section_label(c, abschnitt["titel"], farb_key, start_y)
    y_off = _draw_beschreibung(c, abschnitt, start_y)

    mauern = abschnitt["mauern"]  # list of walls, each a list of rows bottom-to-top
    if not mauern:
        return start_y - (2.5*cm + y_off)
    count = len(mauern)
    spacing = (W - 3*cm) / count
    brick_w = 2.0*cm
    brick_h = 1.4*cm

    # Row colors: bottom row gets the first color, each row up gets the next
    row_colors = [FARBEN["gruen"], FARBEN["blau"], FARBEN["orange"], FARBEN["pink"],
                  FARBEN["purple"], FARBEN["yellow"]]

    mauer_labels = abschnitt.get("mauer_labels", [])

    # Build reference for solution walls: compare with previous (Aufgabe) wall
    # to find which cells were originally blank
    aufgabe_mauer = None

    top_offset = 2.5*cm + y_off
    for mi, mauer in enumerate(mauern):
        rows = mauer  # bottom row first
        num_rows = len(rows)
        base_cx = 1.5*cm + spacing * mi + spacing / 2
        base_y = start_y - top_offset - (num_rows - 1) * brick_h

        # Determine if this is a "Lösung" wall
        is_loesung = (mi < len(mauer_labels) and
                      mauer_labels[mi] == "Lösung" and
                      aufgabe_mauer is not None)

        # Optional label above the wall
        if mi < len(mauer_labels):
            c.setFillColor(FARBEN[farb_key])
            c.setFont(FONT_BOLD, 11)
            c.drawCentredString(base_cx, base_y + num_rows * brick_h + 0.3*cm,
                                mauer_labels[mi])

        for ri, row in enumerate(rows):
            num_bricks = len(row)
            row_w = num_bricks * brick_w
            rx = base_cx - row_w / 2
            ry = base_y + ri * brick_h
            row_col = row_colors[ri % len(row_colors)]

            for bi, val in enumerate(row):
                bx = rx + bi * brick_w
                is_blank = val is None
                # Check if this cell was blank in the Aufgabe wall
                is_solution_cell = (is_loesung and
                                    ri < len(aufgabe_mauer) and
                                    bi < len(aufgabe_mauer[ri]) and
                                    aufgabe_mauer[ri][bi] is None)
                if is_blank:
                    c.setFillColor(FARBEN["antwort"])
                    c.setStrokeColor(row_col)
                elif is_solution_cell:
                    c.setFillColor(FARBEN["antwort"])
                    c.setStrokeColor(row_col)
                else:
                    c.setFillColor(row_col)
                    c.setStrokeColor(row_col)
                c.setLineWidth(1.5)
                c.roundRect(bx, ry, brick_w, brick_h, radius=4, fill=1, stroke=1)
                if val is not None:
                    if is_solution_cell:
                        c.setFillColor(FARBEN["gruen"])
                    else:
                        c.setFillColor(white)
                    c.setFont(FONT_BOLD, 16)
                    c.drawCentredString(bx + brick_w/2, ry + brick_h/2 - 0.2*cm, str(val))

        # Remember this wall as reference for the next (Lösung) wall
        aufgabe_mauer = rows

    bottom_y = start_y - top_offset - (max(len(m) for m in mauern) - 1) * brick_h
    return bottom_y - 0.5*cm


# ── Größer/Kleiner/Gleich ─────────────────────────────────

def draw_vergleiche(c, abschnitt, farb_key, start_y):
    """Compare exercises: child fills in >, < or = between two values."""
    draw_section_label(c, abschnitt["titel"], farb_key, start_y)
    y_off = _draw_beschreibung(c, abschnitt, start_y)

    aufgaben = abschnitt["aufgaben"]  # list of [left, right]
    loesungen = abschnitt.get("loesungen", [])
    halb = (len(aufgaben) + 1) // 2
    col1 = aufgaben[:halb]
    col2 = aufgaben[halb:]
    loes1 = loesungen[:halb]
    loes2 = loesungen[halb:]

    row_y = start_y - 1.5*cm - y_off
    row_h = 1.4*cm

    def _draw_vergleich_row(x, y, aufg, loes=None):
        links, rechts = aufg
        c.setFillColor(FARBEN["dunkel"])
        c.setFont(FONT_BOLD, 18)
        c.drawRightString(x + 2.5*cm, y, str(links))
        # Circle for >, < or =
        circle_x = x + 3.3*cm
        c.setFillColor(FARBEN["antwort"])
        c.setStrokeColor(FARBEN[farb_key])
        c.setLineWidth(1.5)
        c.circle(circle_x, y + 0.2*cm, 0.5*cm, fill=1, stroke=1)
        if loes is not None:
            c.setFillColor(FARBEN["gruen"])
            c.setFont(FONT_BOLD, 18)
            c.drawCentredString(circle_x, y + 0.02*cm, str(loes))
        c.setFillColor(FARBEN["dunkel"])
        c.setFont(FONT_BOLD, 18)
        c.drawString(x + 4.1*cm, y, str(rechts))

    for i, aufg in enumerate(col1):
        loes = loes1[i] if i < len(loes1) else None
        _draw_vergleich_row(1.5*cm, row_y - i * row_h, aufg, loes)
    for i, aufg in enumerate(col2):
        loes = loes2[i] if i < len(loes2) else None
        _draw_vergleich_row(10.5*cm, row_y - i * row_h, aufg, loes)

    return row_y - halb * row_h - 0.3*cm


# ── Nachbarzahlen ─────────────────────────────────────────

def draw_nachbarzahlen(c, abschnitt, farb_key, start_y):
    """Fill in the number before and after a given number."""
    draw_section_label(c, abschnitt["titel"], farb_key, start_y)
    y_off = _draw_beschreibung(c, abschnitt, start_y)

    aufgaben = abschnitt["aufgaben"]  # list of [vor, zahl, nach] – None = blank
    loesungen = abschnitt.get("loesungen", [])
    box_w = 2.0*cm
    box_h = 1.5*cm
    gap = 0.4*cm
    cols = 2
    col_w = (W - 3*cm) / cols
    row_h = 2.3*cm

    row_y = start_y - 1.8*cm - y_off

    for idx, aufg in enumerate(aufgaben):
        col = idx % cols
        row = idx // cols
        x0 = 1.5*cm + col * col_w + 0.5*cm
        y0 = row_y - row * row_h
        loes = loesungen[idx] if idx < len(loesungen) else None

        for j, val in enumerate(aufg):
            bx = x0 + j * (box_w + gap)
            is_blank = val is None
            if is_blank:
                c.setFillColor(FARBEN["antwort"])
                c.setStrokeColor(FARBEN[farb_key])
            else:
                c.setFillColor(FARBEN[farb_key])
                c.setStrokeColor(FARBEN[farb_key])
            c.setLineWidth(1.5)
            c.roundRect(bx, y0 - box_h, box_w, box_h, radius=5, fill=1, stroke=1)
            if val is not None:
                c.setFillColor(white)
                c.setFont(FONT_BOLD, 18)
                c.drawCentredString(bx + box_w/2, y0 - box_h/2 - 0.2*cm, str(val))
            elif loes is not None and j < len(loes) and loes[j] is not None:
                # Show solution in green
                c.setFillColor(FARBEN["gruen"])
                c.setFont(FONT_BOLD, 18)
                c.drawCentredString(bx + box_w/2, y0 - box_h/2 - 0.2*cm, str(loes[j]))

        # Lines between boxes
        c.setStrokeColor(FARBEN["hellgrau"])
        c.setLineWidth(2)
        for j in range(2):
            line_start = x0 + (j + 1) * box_w + j * gap
            line_end = line_start + gap
            c.line(line_start, y0 - box_h/2, line_end, y0 - box_h/2)

    total_rows = (len(aufgaben) + cols - 1) // cols
    return row_y - total_rows * row_h - 0.3*cm


# ── Zahlzerlegung ─────────────────────────────────────────

def draw_zahlzerlegung(c, abschnitt, farb_key, start_y):
    """Number decomposition: a number splits into two parts."""
    draw_section_label(c, abschnitt["titel"], farb_key, start_y)
    y_off = _draw_beschreibung(c, abschnitt, start_y)

    aufgaben = abschnitt["aufgaben"]  # list of [zahl, teil1, teil2], None = blank
    cols = 3
    col_w = (W - 3*cm) / cols
    circle_r = 0.5*cm
    vert_gap = 1.5*cm  # vertical distance between top and bottom circles
    row_h = vert_gap + 2 * circle_r + 0.6*cm
    beschreibung_extra = 0.4*cm if y_off > 0 else 0
    row_y = start_y - 1.2*cm - y_off - beschreibung_extra

    zerlegung_labels = abschnitt.get("zerlegung_labels", [])

    for idx, aufg in enumerate(aufgaben):
        zahl, t1, t2 = aufg
        col = idx % cols
        row = idx // cols
        cx = 1.5*cm + col * col_w + col_w / 2
        y0 = row_y - row * row_h

        # Optional label above (e.g. "Aufgabe", "Lösung")
        if idx < len(zerlegung_labels):
            c.setFillColor(FARBEN["grau"])
            c.setFont(FONT_BOLD, 9)
            c.drawCentredString(cx, y0 + circle_r + 0.3*cm, zerlegung_labels[idx])

        # Top circle (the number)
        c.setFillColor(FARBEN[farb_key])
        c.circle(cx, y0, circle_r, fill=1, stroke=0)
        c.setFillColor(white)
        c.setFont(FONT_BOLD, 16)
        c.drawCentredString(cx, y0 - 0.2*cm, str(zahl))

        # Lines down to two parts
        left_cx = cx - 1.0*cm
        right_cx = cx + 1.0*cm
        part_y = y0 - vert_gap
        c.setStrokeColor(FARBEN["hellgrau"])
        c.setLineWidth(2)
        c.line(cx, y0 - circle_r, left_cx, part_y + circle_r)
        c.line(cx, y0 - circle_r, right_cx, part_y + circle_r)

        # Detect if this is a "Lösung" item (show answers in green)
        is_loesung = (idx < len(zerlegung_labels)
                      and zerlegung_labels[idx] == "Lösung")

        # Left part
        _draw_zerlegung_part(c, left_cx, part_y, circle_r,
                             t1, t1 is None, is_loesung, farb_key)

        # Right part
        _draw_zerlegung_part(c, right_cx, part_y, circle_r,
                             t2, t2 is None, is_loesung, farb_key)

    total_rows = (len(aufgaben) + cols - 1) // cols
    # Note: We omit the typical -0.3*cm padding here to prevent premature 
    # page breaks if Zahlzerlegung is the last item on a page.
    return row_y - total_rows * row_h


# ── Kettenaufgaben ────────────────────────────────────────

def draw_kettenaufgaben(c, abschnitt, farb_key, start_y):
    """Chain calculations: 3 + 2 − 1 + 4 = ? (Two columns)"""
    draw_section_label(c, abschnitt["titel"], farb_key, start_y)
    y_off = _draw_beschreibung(c, abschnitt, start_y)

    aufgaben = abschnitt["aufgaben"]  # list of strings like "3 + 2 − 1 + 4"
    loesungen = abschnitt.get("loesungen", [])
    
    # Calculate columns
    halb = (len(aufgaben) + 1) // 2
    col_w = (W - 3*cm) / 2
    row_y = start_y - 1.5*cm - y_off
    row_h = 2.0*cm

    for idx, kette in enumerate(aufgaben):
        col = 0 if idx < halb else 1
        row = idx if idx < halb else idx - halb

        x0 = 1.8*cm + col * col_w
        y = row_y - row * row_h

        # Number the exercise
        c.setFillColor(FARBEN[farb_key])
        c.setFont(FONT_BOLD, 12)
        c.drawString(x0, y + 0.05*cm, f"{idx + 1}.")

        # The chain expression
        c.setFillColor(FARBEN["dunkel"])
        c.setFont(FONT_BOLD, 18)
        c.drawString(x0 + 1.0*cm, y, kette)

        # = and answer box
        text_w = c.stringWidth(kette, FONT_BOLD, 18)
        eq_x = x0 + 1.0*cm + text_w + 0.5*cm
        c.setFillColor(FARBEN[farb_key])
        c.drawString(eq_x, y, "=")

        ans_x = eq_x + 1.0*cm
        if idx < len(loesungen):
            _draw_filled_answer_box(c, ans_x, y - 0.25*cm,
                                    loesungen[idx], w=1.6*cm, h=1.5*cm)
        else:
            draw_answer_box(c, ans_x, y - 0.25*cm, w=1.6*cm, h=1.5*cm)

    return row_y - halb * row_h - 0.3*cm


# ── Tauschaufgaben ────────────────────────────────────────

def draw_tauschaufgaben(c, abschnitt, farb_key, start_y):
    """Commutative property: show a + b = b + a."""
    draw_section_label(c, abschnitt["titel"], farb_key, start_y)
    y_off = _draw_beschreibung(c, abschnitt, start_y)

    aufgaben = abschnitt["aufgaben"]  # list of [a, b]
    loesungen = abschnitt.get("loesungen", [])
    row_y = start_y - 1.5*cm - y_off
    row_h = 2.0*cm

    for idx, aufg in enumerate(aufgaben):
        a, b = aufg
        y = row_y - idx * row_h
        summe = loesungen[idx] if idx < len(loesungen) else None

        c.setFont(FONT_BOLD, 18)

        # Left side: a + b = ___
        x = 1.8*cm
        c.setFillColor(FARBEN["dunkel"])
        c.drawCentredString(x + 0.5*cm, y, str(a))
        c.setFillColor(FARBEN[farb_key])
        c.drawCentredString(x + 1.3*cm, y, "+")
        c.setFillColor(FARBEN["dunkel"])
        c.drawCentredString(x + 2.1*cm, y, str(b))
        c.setFillColor(FARBEN[farb_key])
        c.drawCentredString(x + 3.0*cm, y, "=")
        if summe is not None:
            _draw_filled_answer_box(c, x + 3.5*cm, y - 0.25*cm, summe,
                                    w=1.6*cm, h=1.5*cm)
        else:
            draw_answer_box(c, x + 3.5*cm, y - 0.25*cm, w=1.6*cm, h=1.5*cm)

        # Right side: b + a = ___
        x2 = 10*cm
        c.setFillColor(FARBEN["dunkel"])
        c.drawCentredString(x2 + 0.5*cm, y, str(b))
        c.setFillColor(FARBEN[farb_key])
        c.drawCentredString(x2 + 1.3*cm, y, "+")
        c.setFillColor(FARBEN["dunkel"])
        c.drawCentredString(x2 + 2.1*cm, y, str(a))
        c.setFillColor(FARBEN[farb_key])
        c.drawCentredString(x2 + 3.0*cm, y, "=")
        if summe is not None:
            _draw_filled_answer_box(c, x2 + 3.5*cm, y - 0.25*cm, summe,
                                    w=1.6*cm, h=1.5*cm)
        else:
            draw_answer_box(c, x2 + 3.5*cm, y - 0.25*cm, w=1.6*cm, h=1.5*cm)

    return row_y - len(aufgaben) * row_h - 0.3*cm


# ── Verdoppeln & Halbieren ────────────────────────────────

def draw_verdoppeln_halbieren(c, abschnitt, farb_key, start_y):
    """Double or halve numbers."""
    draw_section_label(c, abschnitt["titel"], farb_key, start_y)
    y_off = _draw_beschreibung(c, abschnitt, start_y)

    aufgaben = abschnitt["aufgaben"]  # list of [zahl, typ] typ = "doppelt" or "halb"
    loesungen = abschnitt.get("loesungen", [])
    cols = 2
    col_w = (W - 3*cm) / cols
    row_h = 2.0*cm
    halb_count = (len(aufgaben) + 1) // 2
    row_y = start_y - 1.5*cm - y_off

    for idx, aufg in enumerate(aufgaben):
        zahl, typ = aufg
        loes = loesungen[idx] if idx < len(loesungen) else None
        col = idx % cols
        row = idx // cols
        x = 1.8*cm + col * col_w
        y = row_y - row * row_h

        c.setFont(FONT_BOLD, 18)

        if typ == "doppelt":
            c.setFillColor(FARBEN["dunkel"])
            c.drawCentredString(x + 0.5*cm, y, str(zahl))
            c.setFillColor(FARBEN[farb_key])
            c.drawCentredString(x + 1.3*cm, y, "+")
            c.setFillColor(FARBEN["dunkel"])
            c.drawCentredString(x + 2.1*cm, y, str(zahl))
            c.setFillColor(FARBEN[farb_key])
            c.drawCentredString(x + 3.0*cm, y, "=")
            if loes is not None:
                _draw_filled_answer_box(c, x + 3.5*cm, y - 0.25*cm, loes,
                                        w=1.6*cm, h=1.5*cm)
            else:
                draw_answer_box(c, x + 3.5*cm, y - 0.25*cm, w=1.6*cm, h=1.5*cm)
        else:  # halb
            c.setFillColor(FARBEN["dunkel"])
            c.drawString(x, y, str(zahl))
            text_w = c.stringWidth(str(zahl), FONT_BOLD, 18)
            c.setFillColor(FARBEN[farb_key])
            c.setFont(FONT_BOLD, 18)
            c.drawString(x + text_w + 0.3*cm, y, "÷ 2 =")
            if loes is not None:
                _draw_filled_answer_box(c, x + text_w + 2.5*cm, y - 0.25*cm,
                                        loes, w=1.6*cm, h=1.5*cm)
            else:
                draw_answer_box(c, x + text_w + 2.5*cm, y - 0.25*cm,
                                w=1.6*cm, h=1.5*cm)

    total_rows = (len(aufgaben) + cols - 1) // cols
    return row_y - total_rows * row_h - 0.3*cm


# ── Zahlenstrahl ──────────────────────────────────────────

def draw_zahlenstrahl(c, abschnitt, farb_key, start_y):
    """Number line with some numbers missing."""
    draw_section_label(c, abschnitt["titel"], farb_key, start_y)
    y_off = _draw_beschreibung(c, abschnitt, start_y)

    strahlen = abschnitt["strahlen"]  # list of {von, bis, werte}
    row_h = 3.0*cm
    row_y = start_y - 1.5*cm - y_off
    line_x = 2*cm
    line_w = W - 4*cm

    for si, strahl in enumerate(strahlen):
        von = strahl["von"]
        bis = strahl["bis"]
        werte = strahl.get("werte", [])  # list: number or null
        count = bis - von + 1
        y = row_y - si * row_h

        # Draw the line
        c.setStrokeColor(FARBEN["dunkel"])
        c.setLineWidth(2)
        c.line(line_x, y, line_x + line_w, y)

        # Arrow at the end
        c.line(line_x + line_w - 0.2*cm, y + 0.15*cm,
               line_x + line_w, y)
        c.line(line_x + line_w - 0.2*cm, y - 0.15*cm,
               line_x + line_w, y)

        step = line_w / (count - 1) if count > 1 else line_w
        for i in range(count):
            tx = line_x + i * step
            # Tick mark
            c.setStrokeColor(FARBEN["dunkel"])
            c.setLineWidth(1.5)
            c.line(tx, y - 0.2*cm, tx, y + 0.2*cm)

            val = werte[i] if i < len(werte) else von + i
            strahl_loes = strahl.get("loesungen", [])
            if val is None:
                # Blank answer box (1.4cm × 1.2cm, centered on tick)
                c.setFillColor(FARBEN["antwort"])
                c.setStrokeColor(FARBEN[farb_key])
                c.setLineWidth(1)
                c.roundRect(tx - 0.7*cm, y - 1.4*cm, 1.4*cm, 1.2*cm,
                            radius=3, fill=1, stroke=1)
                # Show solution if available
                if i < len(strahl_loes) and strahl_loes[i] is not None:
                    c.setFillColor(FARBEN["gruen"])
                    c.setFont(FONT_BOLD, 12)
                    c.drawCentredString(tx, y - 0.95*cm, str(strahl_loes[i]))
            else:
                c.setFillColor(FARBEN["dunkel"])
                c.setFont(FONT_BOLD, 12)
                c.drawCentredString(tx, y - 0.9*cm, str(val))

    return row_y - len(strahlen) * row_h - 0.3*cm


# ── Punktefeld (Zehnerfeld) ──────────────────────────────

def draw_punktefeld(c, abschnitt, farb_key, start_y):
    """10-frame dot grids: child counts the filled dots."""
    draw_section_label(c, abschnitt["titel"], farb_key, start_y)
    y_off = _draw_beschreibung(c, abschnitt, start_y)

    aufgaben = abschnitt["aufgaben"]  # list of integers (how many dots filled)
    felder = abschnitt.get("felder", 10)  # 10 or 20
    cols_per_row = 5
    rows_frame = felder // cols_per_row

    grid_cols = 3
    grid_col_w = (W - 3*cm) / grid_cols
    dot_r = 0.3*cm
    cell = 0.8*cm
    row_h = rows_frame * cell + 2.5*cm
    row_y = start_y - 1.5*cm - y_off

    # muster mode: dots are scattered, not sequential
    muster = abschnitt.get("muster", False)

    for idx, anzahl in enumerate(aufgaben):
        col = idx % grid_cols
        row = idx // grid_cols
        x0 = 1.5*cm + col * grid_col_w + 0.3*cm
        y0 = row_y - row * row_h

        # Determine which positions are filled
        if muster:
            _rnd.seed(anzahl * 100 + idx * 7 + felder)
            positions = list(range(felder))
            _rnd.shuffle(positions)
            filled = set(positions[:anzahl])
        else:
            filled = set(range(anzahl))

        # Draw the frame grid
        for r in range(rows_frame):
            for cc in range(cols_per_row):
                cx = x0 + cc * cell + cell/2
                cy = y0 - r * cell - cell/2
                dot_idx = r * cols_per_row + cc

                # Frame circle (always)
                c.setStrokeColor(FARBEN["hellgrau"])
                c.setLineWidth(1)
                c.setFillColor(white)
                c.circle(cx, cy, dot_r, fill=1, stroke=1)

                # Fill if in filled set
                if dot_idx in filled:
                    c.setFillColor(FARBEN[farb_key])
                    c.circle(cx, cy, dot_r, fill=1, stroke=0)

        # Answer box below
        frame_bottom = y0 - rows_frame * cell
        loesungen = abschnitt.get("loesungen", [])
        if idx < len(loesungen):
            _draw_filled_answer_box(c, x0 + 0.5*cm, frame_bottom - 1.7*cm,
                                    loesungen[idx], w=1.6*cm, h=1.5*cm)
        else:
            draw_answer_box(c, x0 + 0.5*cm, frame_bottom - 1.7*cm,
                            w=1.6*cm, h=1.5*cm)
        c.setFillColor(FARBEN["grau"])
        c.setFont(FONT, 9)
        c.drawString(x0 + 2.3*cm, frame_bottom - 1.0*cm, "Punkte")

    total_rows = (len(aufgaben) + grid_cols - 1) // grid_cols
    return row_y - total_rows * row_h - 0.3*cm


# ── Zahlen ordnen ─────────────────────────────────────────

def draw_zahlen_ordnen(c, abschnitt, farb_key, start_y):
    """Sort numbers from smallest to largest (or reverse)."""
    draw_section_label(c, abschnitt["titel"], farb_key, start_y)
    y_off = _draw_beschreibung(c, abschnitt, start_y)

    aufgaben = abschnitt["aufgaben"]  # list of lists of numbers
    loesungen = abschnitt.get("loesungen", [])
    row_h = 2.5*cm
    row_y = start_y - 1.5*cm - y_off
    box_w = 1.6*cm
    box_h = 1.5*cm

    for idx, zahlen in enumerate(aufgaben):
        y = row_y - idx * row_h
        count = len(zahlen)
        loes = loesungen[idx] if idx < len(loesungen) else None

        # Show the unsorted numbers in colored circles
        c.setFillColor(FARBEN[farb_key])
        c.setFont(FONT_BOLD, 12)
        c.drawString(1.8*cm, y + 0.05*cm, f"{idx + 1}.")

        x = 2.8*cm
        for z in zahlen:
            c.setFillColor(FARBEN[farb_key])
            c.circle(x + 0.5*cm, y + 0.1*cm, 0.45*cm, fill=1, stroke=0)
            c.setFillColor(white)
            c.setFont(FONT_BOLD, 14)
            c.drawCentredString(x + 0.5*cm, y - 0.08*cm, str(z))
            x += 1.2*cm

        # Arrow
        c.setStrokeColor(FARBEN["hellgrau"])
        c.setLineWidth(2)
        arrow_x = x + 0.3*cm
        c.line(arrow_x, y + 0.1*cm, arrow_x + 0.8*cm, y + 0.1*cm)
        c.line(arrow_x + 0.6*cm, y + 0.3*cm, arrow_x + 0.8*cm, y + 0.1*cm)
        c.line(arrow_x + 0.6*cm, y - 0.1*cm, arrow_x + 0.8*cm, y + 0.1*cm)

        # Boxes for the sorted answer
        bx = arrow_x + 1.3*cm
        for i in range(count):
            c.setFillColor(FARBEN["antwort"])
            c.setStrokeColor(FARBEN[farb_key])
            c.setLineWidth(1.5)
            c.roundRect(bx, y - 0.7*cm, box_w, box_h, radius=4, fill=1, stroke=1)
            # Show solution in green if available
            if loes is not None and i < len(loes):
                c.setFillColor(FARBEN["gruen"])
                c.setFont(FONT_BOLD, 16)
                c.drawCentredString(bx + box_w/2, y + 0.05*cm, str(loes[i]))
            if i < count - 1:
                c.setFillColor(FARBEN["dunkel"])
                c.setFont(FONT_BOLD, 16)
                c.drawCentredString(bx + box_w + 0.25*cm, y + 0.05*cm, "<")
            bx += box_w + 0.5*cm

    return row_y - len(aufgaben) * row_h - 0.3*cm


# ── Vervielfachen ────────────────────────────────────────

def draw_vervielfachen(c, abschnitt, farb_key, start_y):
    """How many times must you add a number to itself to reach a target?
    Line 1: zahl + [addition chain box] = ziel
    Line 2: zahl passt [___] mal in die ziel."""
    draw_section_label(c, abschnitt["titel"], farb_key, start_y)
    y_off = _draw_beschreibung(c, abschnitt, start_y)

    aufgaben = abschnitt["aufgaben"]  # list of [zahl, ziel]
    loesungen = abschnitt.get("loesungen", [])
    line_gap = 1.1*cm   # vertical gap between line 1 and line 2
    row_h = 2.5*cm      # total height per exercise (two lines + spacing)
    row_y = start_y - 1.5*cm - y_off

    for idx, aufg in enumerate(aufgaben):
        zahl, ziel = aufg
        loes = loesungen[idx] if idx < len(loesungen) else None
        x = 1.5*cm
        y = row_y - idx * row_h

        # ── Line 1: zahl + [___________] = ziel ──
        c.setFillColor(FARBEN["dunkel"])
        c.setFont(FONT_BOLD, 16)
        c.drawCentredString(x + 0.4*cm, y, str(zahl))

        c.setFillColor(FARBEN[farb_key])
        c.drawCentredString(x + 1.1*cm, y, "+")

        plus_box_w = 4.0*cm
        draw_answer_box(c, x + 1.5*cm, y - 0.65*cm, w=plus_box_w, h=1.5*cm)
        if loes is not None:
            addition_text = (" + ".join([str(zahl)] * (loes - 1)))
            c.setFillColor(FARBEN["gruen"])
            c.setFont(FONT_BOLD, 11)
            c.drawCentredString(x + 1.5*cm + plus_box_w / 2,
                                y - 0.05*cm, addition_text)

        c.setFillColor(FARBEN[farb_key])
        c.setFont(FONT_BOLD, 16)
        eq1_x = x + 1.5*cm + plus_box_w + 0.3*cm
        c.drawCentredString(eq1_x, y, "=")

        c.setFillColor(FARBEN["dunkel"])
        c.drawCentredString(eq1_x + 0.8*cm, y, str(ziel))

        # ── Line 2: zahl passt [___] mal in die ziel. ──
        y2 = y - line_gap
        px = x  # start x for "passt" line

        c.setFillColor(FARBEN["dunkel"])
        c.setFont(FONT_BOLD, 16)
        zahl_w = c.stringWidth(str(zahl), FONT_BOLD, 16)
        c.drawString(px, y2, str(zahl))
        px += zahl_w + 0.2*cm

        c.setFillColor(FARBEN["grau"])
        c.setFont(FONT, 14)
        passt_w = c.stringWidth("passt", FONT, 14)
        c.drawString(px, y2, "passt")
        px += passt_w + 0.2*cm

        BOX_W = 1.6*cm
        BOX_H = 0.9*cm
        if loes is not None:
            _draw_filled_answer_box(c, px, y2 - 0.3*cm, loes, w=BOX_W, h=BOX_H)
        else:
            draw_answer_box(c, px, y2 - 0.3*cm, w=BOX_W, h=BOX_H)
        px += BOX_W + 0.2*cm

        c.setFillColor(FARBEN["grau"])
        c.setFont(FONT, 14)
        mal_text = f"mal in die"
        mal_w = c.stringWidth(mal_text, FONT, 14)
        c.drawString(px, y2, mal_text)
        px += mal_w + 0.2*cm

        c.setFillColor(FARBEN["dunkel"])
        c.setFont(FONT_BOLD, 16)
        c.drawString(px, y2, f"{ziel}.")

    return row_y - len(aufgaben) * row_h - 0.3*cm


# ── Rechenweg-Labyrinth ──────────────────────────────────

def draw_rechenweg_labyrinth(c, abschnitt, farb_key, start_y):
    """Grid-based path puzzle: pick one number per column, find the path
    that sums to the target."""
    draw_section_label(c, abschnitt["titel"], farb_key, start_y)
    y_off = _draw_beschreibung(c, abschnitt, start_y)

    aufgaben = abschnitt["aufgaben"]
    loesungen = abschnitt.get("loesungen", [])
    row_y = start_y - 1.5*cm - y_off
    node_r = 0.5*cm
    node_colors = [FARBEN["blau"], FARBEN["gruen"], FARBEN["orange"],
                   FARBEN["pink"], FARBEN["purple"]]

    for ai, aufg in enumerate(aufgaben):
        spalten = aufg["spalten"]  # list of lists
        if not spalten:
            continue
        zielsumme = aufg["zielsumme"]
        loes = loesungen[ai] if ai < len(loesungen) else None
        num_cols = len(spalten)
        num_rows = max((len(s) for s in spalten), default=0)
        if num_rows == 0:
            continue

        grid_h = num_rows * 1.6*cm
        grid_top = row_y
        col_spacing = (W - 6*cm) / max(num_cols - 1, 1)

        # "Start" label
        c.setFillColor(FARBEN[farb_key])
        c.setFont(FONT_BOLD, 10)
        c.drawCentredString(1.8*cm, grid_top - grid_h / 2 + 0.1*cm, "Start")

        for ci, spalte in enumerate(spalten):
            if not spalte:
                continue
            col_x = 3*cm + ci * col_spacing
            col_color = node_colors[ci % len(node_colors)]
            for ri, val in enumerate(spalte):
                cy = grid_top - (ri + 0.5) * (grid_h / len(spalte))
                # Node circle
                c.setFillColor(col_color)
                c.circle(col_x, cy, node_r, fill=1, stroke=0)
                c.setFillColor(white)
                c.setFont(FONT_BOLD, 14)
                c.drawCentredString(col_x, cy - 0.15*cm, str(val))

            # Arrows to next column
            if ci < num_cols - 1:
                next_spalte = spalten[ci + 1]
                next_x = 3*cm + (ci + 1) * col_spacing
                for ri in range(len(spalte)):
                    sy = grid_top - (ri + 0.5) * (grid_h / len(spalte))
                    for nri in range(len(next_spalte)):
                        ny = grid_top - (nri + 0.5) * (grid_h / len(next_spalte))
                        c.setStrokeColor(FARBEN["hellgrau"])
                        c.setLineWidth(1)
                        c.line(col_x + node_r, sy, next_x - node_r, ny)

        # Target sum label (no answer box)
        target_x = 3*cm + (num_cols - 1) * col_spacing + 2*cm
        target_y = grid_top - grid_h / 2
        c.setFillColor(FARBEN[farb_key])
        c.setFont(FONT_BOLD, 14)
        c.drawCentredString(target_x, target_y + 0.5*cm, "Ziel:")
        c.drawCentredString(target_x, target_y - 0.2*cm, str(zielsumme))

        row_y = grid_top - grid_h - 0.8*cm

    return row_y - 0.3*cm


# ── Schatzsuche (Treasure Hunt Maze) ────────────────────

def _draw_maze_path(c, abschnitt, farb_key, start_y, modus="schatz"):
    """Shared renderer for maze-path exercises (schatzsuche & labyrinth_flucht).
    modus: 'schatz' = treasure hunt, 'flucht' = maze escape."""
    import math

    draw_section_label(c, abschnitt["titel"], farb_key, start_y)
    y_off = _draw_beschreibung(c, abschnitt, start_y)

    aufgaben = abschnitt["aufgaben"]
    loesungen = abschnitt.get("loesungen", [])
    row_y = start_y - 1.5*cm - y_off

    node_r = 0.55*cm
    answer_r = 0.5*cm
    gap = 0.15*cm
    path_colors = [FARBEN["blau"], FARBEN["gruen"], FARBEN["orange"],
                   FARBEN["pink"], FARBEN["purple"]]

    # Theme configuration
    if modus == "flucht":
        start_label = "Eingang"
        end_label = "Ausgang!"
        end_fill = FARBEN["gruen"]
        end_stroke = FARBEN["blau"]
    else:
        start_label = "Start"
        end_label = "Schatz!"
        end_fill = FARBEN["yellow"]
        end_stroke = FARBEN["orange"]

    for ai, aufg in enumerate(aufgaben):
        start_val = aufg["start"]
        schritte = aufg["schritte"]
        loes = loesungen[ai] if ai < len(loesungen) else None

        n_steps = len(schritte)
        total_nodes = 1 + n_steps * 2

        # Calculate how many nodes fit per row
        step_w = 2 * node_r + gap
        usable_w = W - 5*cm
        nodes_per_row = max(int(usable_w / step_w), 3)

        # Build rows of nodes (zigzag)
        rows = []
        remaining = list(range(total_nodes))
        while remaining:
            row = remaining[:nodes_per_row]
            remaining = remaining[nodes_per_row:]
            rows.append(row)

        # Split comma-separated solution string into list
        loes_parts = loes.split(',') if loes else []

        # Draw the maze path
        maze_top = row_y
        row_h = 2.2*cm
        x_left = 2.5*cm
        x_right = x_left + (nodes_per_row - 1) * step_w

        prev_cx, prev_cy = None, None

        for ri, row_indices in enumerate(rows):
            reverse = (ri % 2 == 1)
            if reverse:
                row_indices = list(reversed(row_indices))

            cy = maze_top - ri * row_h

            for ni_in_row, node_idx in enumerate(row_indices):
                cx = x_left + ni_in_row * step_w
                if reverse:
                    cx = x_right - ni_in_row * step_w

                # Draw path line from previous node
                if prev_cx is not None:
                    dx = cx - prev_cx
                    dy = cy - prev_cy
                    dist = math.sqrt(dx*dx + dy*dy)
                    if dist > 0:
                        c.setStrokeColor(FARBEN["hellgrau"])
                        c.setLineWidth(2)
                        c.setDash(3, 3)
                        nx, ny = dx/dist, dy/dist
                        c.line(prev_cx + nx*node_r, prev_cy + ny*node_r,
                               cx - nx*node_r, cy - ny*node_r)
                        c.setDash()

                # Determine what this node is
                if node_idx == 0:
                    # Start node
                    c.setFillColor(FARBEN[farb_key])
                    c.circle(cx, cy, node_r, fill=1, stroke=0)
                    c.setFillColor(white)
                    c.setFont(FONT_BOLD, 14)
                    c.drawCentredString(cx, cy - 0.18*cm, str(start_val))
                    c.setFillColor(FARBEN[farb_key])
                    c.setFont(FONT_BOLD, 8)
                    c.drawCentredString(cx, cy + node_r + 0.15*cm, start_label)
                elif node_idx % 2 == 1:
                    # Operation node
                    step_i = node_idx // 2
                    col = path_colors[step_i % len(path_colors)]
                    c.setFillColor(col)
                    c.circle(cx, cy, node_r * 0.85, fill=1, stroke=0)
                    c.setFillColor(white)
                    c.setFont(FONT_BOLD, 13)
                    c.drawCentredString(cx, cy - 0.18*cm, schritte[step_i])
                else:
                    # Answer node
                    answer_i = node_idx // 2 - 1
                    is_last = (node_idx == total_nodes - 1)

                    if is_last:
                        # End node - themed styling
                        c.setFillColor(end_fill)
                        c.setStrokeColor(end_stroke)
                        c.setLineWidth(2.5)
                        c.circle(cx, cy, node_r, fill=1, stroke=1)
                        c.setFont(FONT_BOLD, 8)
                        c.setFillColor(end_stroke)
                        c.drawCentredString(cx, cy + node_r + 0.15*cm, end_label)
                    else:
                        # Regular answer node
                        c.setFillColor(FARBEN["antwort"])
                        c.setStrokeColor(FARBEN[farb_key])
                        c.setLineWidth(1.5)
                        c.circle(cx, cy, answer_r, fill=1, stroke=1)

                    # Show solution if available
                    if loes_parts and answer_i < len(loes_parts):
                        c.setFillColor(FARBEN["gruen"])
                        c.setFont(FONT_BOLD, 13)
                        c.drawCentredString(cx, cy - 0.18*cm, loes_parts[answer_i])

                prev_cx, prev_cy = cx, cy

        row_y = maze_top - len(rows) * row_h

    return row_y - 0.3*cm


def draw_schatzsuche(c, abschnitt, farb_key, start_y):
    """Maze-style treasure hunt: follow a winding path with operations."""
    return _draw_maze_path(c, abschnitt, farb_key, start_y, modus="schatz")


def draw_labyrinth_flucht(c, abschnitt, farb_key, start_y):
    """Maze escape: follow a winding path with operations to find the exit."""
    return _draw_maze_path(c, abschnitt, farb_key, start_y, modus="flucht")


# ── Zahlenrätsel (Wer bin ich?) ─────────────────────────

def _draw_hinweis_boxen(c, boxen, farb_key, start_y):
    """Draws colored hint boxes. First row side by side, remaining full width below."""
    if not boxen:
        return 0
    colors = [FARBEN.get("blau"), FARBEN.get("gruen"), FARBEN.get("orange"),
              FARBEN.get("pink"), FARBEN.get("purple")]

    # First row: up to 2 boxes side by side
    first_row = boxen[:2]
    rest = boxen[2:]
    n = len(first_row)
    box_w = (W - 3.5*cm) / n
    box_h = 1.4*cm
    y = start_y - box_h
    total_h = box_h + 0.2*cm

    for i, box in enumerate(first_row):
        x = 1.8*cm + i * (box_w + 0.15*cm)
        bg = colors[i % len(colors)]
        c.setFillColor(bg)
        c.roundRect(x, y, box_w - 0.15*cm, box_h, radius=6, fill=1, stroke=0)
        c.setFillColor(white)
        c.setFont(FONT_BOLD, 9)
        c.drawString(x + 0.3*cm, y + box_h - 0.4*cm, box["titel"])
        c.setFont(FONT, 8)
        c.drawString(x + 0.3*cm, y + box_h - 0.85*cm, box["text"])

    # Remaining boxes: full width below
    for j, box in enumerate(rest):
        full_w = W - 3.6*cm
        row_h = 1.4*cm
        ry = y - (j + 1) * (row_h + 0.15*cm)
        bg = colors[(j + n) % len(colors)]
        c.setFillColor(bg)
        c.roundRect(1.8*cm, ry, full_w, row_h, radius=6, fill=1, stroke=0)
        c.setFillColor(white)
        c.setFont(FONT_BOLD, 9)
        c.drawString(2.1*cm, ry + row_h - 0.4*cm, box["titel"])
        # Text with word wrap
        c.setFont(FONT, 8)
        text = box["text"]
        max_w = full_w - 0.8*cm
        lines = _wrap_text(c, text, FONT, 8, max_w)
        for li, l in enumerate(lines):
            c.drawString(2.1*cm, ry + row_h - 0.85*cm - li * 0.35*cm, l)
        total_h += row_h + 0.15*cm

    return total_h


def draw_zahlenraetsel(c, abschnitt, farb_key, start_y):
    """Number riddles with text clues and an answer box."""
    draw_section_label(c, abschnitt["titel"], farb_key, start_y)
    y_off = _draw_beschreibung(c, abschnitt, start_y)

    # Optional hint boxes
    hinweis_boxen = abschnitt.get("hinweis_boxen", [])
    if hinweis_boxen:
        hb_h = _draw_hinweis_boxen(c, hinweis_boxen, farb_key, start_y - 1.0*cm - y_off)
        y_off += hb_h

    aufgaben = abschnitt["aufgaben"]  # list of {hinweise: [...], loesung: int}
    loesungen = abschnitt.get("loesungen", [])
    row_y = start_y - 1.5*cm - y_off
    row_h = 2.5*cm

    for idx, aufg in enumerate(aufgaben):
        hinweise = aufg["hinweise"]
        loes = loesungen[idx] if idx < len(loesungen) else None
        y = row_y - idx * row_h

        # Number label
        c.setFillColor(FARBEN[farb_key])
        c.setFont(FONT_BOLD, 12)
        c.drawString(1.8*cm, y, f"{idx + 1}.")

        # Clue lines
        c.setFillColor(FARBEN["dunkel"])
        c.setFont(FONT, 11)
        for li, hinweis in enumerate(hinweise):
            c.drawString(2.8*cm, y - li * 0.5*cm, f"• {hinweis}")

        # Answer box on the right side
        box_x = W - 4.5*cm
        box_cy = y - (len(hinweise) - 1) * 0.25*cm
        c.setFillColor(FARBEN["grau"])
        c.setFont(FONT_BOLD, 11)
        c.drawCentredString(box_x + 0.75*cm, box_cy + 1.0*cm, "Ich bin:")
        draw_answer_box(c, box_x, box_cy - 0.3*cm, w=2.0*cm, h=1.5*cm)

    return row_y - len(aufgaben) * row_h - 0.3*cm


# ── Einkaufen ───────────────────────────────────────────

def draw_einkaufen(c, abschnitt, farb_key, start_y):
    """Shopping exercises: calculate total price or change."""
    draw_section_label(c, abschnitt["titel"], farb_key, start_y)
    y_off = _draw_beschreibung(c, abschnitt, start_y)

    aufgaben = abschnitt["aufgaben"]
    loesungen = abschnitt.get("loesungen", [])
    row_y = start_y - 1.5*cm - y_off
    row_h = 2.8*cm

    for idx, aufg in enumerate(aufgaben):
        artikel = aufg["artikel"]  # list of {name, preis}
        frage = aufg.get("frage", "")
        loes = loesungen[idx] if idx < len(loesungen) else None
        y = row_y - idx * row_h

        # Number
        c.setFillColor(FARBEN[farb_key])
        c.setFont(FONT_BOLD, 12)
        c.drawString(1.8*cm, y, f"{idx + 1}.")

        # Price tags
        tag_x = 2.8*cm
        for art in artikel:
            name = art["name"]
            preis = art["preis"]
            # Draw a price tag
            tag_w = c.stringWidth(f"{name} {preis}€", FONT_BOLD, 11) + 0.8*cm
            c.setFillColor(FARBEN["yellow"])
            c.roundRect(tag_x, y - 0.3*cm, tag_w, 0.9*cm, radius=5, fill=1, stroke=0)
            c.setFillColor(FARBEN["dunkel"])
            c.setFont(FONT_BOLD, 11)
            c.drawString(tag_x + 0.3*cm, y - 0.05*cm, f"{name} {preis}€")
            tag_x += tag_w + 0.4*cm

        # Question
        q_y = y - 1.0*cm
        c.setFillColor(FARBEN["dunkel"])
        c.setFont(FONT, 10)
        c.drawString(2.8*cm, q_y, frage)

        # Answer box
        c.setFillColor(FARBEN["grau"])
        c.setFont(FONT, 9)
        c.drawString(2.8*cm, q_y - 0.7*cm, "Antwort:")
        draw_answer_box(c, 5*cm, q_y - 1.0*cm, w=2.0*cm, h=1.5*cm)

    return row_y - len(aufgaben) * row_h - 0.3*cm


# ── Kalender-Rätsel ─────────────────────────────────────

def draw_kalender_raetsel(c, abschnitt, farb_key, start_y):
    """Calendar/date puzzles with text and answer box."""
    draw_section_label(c, abschnitt["titel"], farb_key, start_y)
    y_off = _draw_beschreibung(c, abschnitt, start_y)

    aufgaben = abschnitt["aufgaben"]  # list of {text/frage}
    loesungen = abschnitt.get("loesungen", [])
    row_y = start_y - 1.5*cm - y_off
    row_h = 2.2*cm

    for idx, aufg in enumerate(aufgaben):
        text = aufg.get("text") or aufg.get("frage", "")
        loes = loesungen[idx] if idx < len(loesungen) else None
        y = row_y - idx * row_h

        # Number
        c.setFillColor(FARBEN[farb_key])
        c.setFont(FONT_BOLD, 12)
        c.drawString(1.8*cm, y, f"{idx + 1}.")

        # Text with word wrap
        c.setFillColor(FARBEN["dunkel"])
        c.setFont(FONT, 11)
        max_w = W - 5*cm
        lines = _wrap_text(c, text, FONT, 11, max_w)
        for li, l in enumerate(lines):
            c.drawString(2.8*cm, y - li * 0.45*cm, l)

        # Answer box (no solution shown, more spacing)
        box_y = y - len(lines) * 0.45*cm - 0.7*cm
        c.setFillColor(FARBEN["grau"])
        c.setFont(FONT, 9)
        c.drawString(2.8*cm, box_y + 0.3*cm, "Antwort:")
        draw_answer_box(c, 5*cm, box_y, w=2.5*cm, h=1.5*cm)

    return row_y - len(aufgaben) * row_h - 0.3*cm


# ── Textaufgaben ──────────────────────────────────────────

def draw_textaufgaben(c, abschnitt, farb_key, start_y):
    """Word problems with an answer box."""
    draw_section_label(c, abschnitt["titel"], farb_key, start_y)
    y_off = _draw_beschreibung(c, abschnitt, start_y)

    aufgaben = abschnitt["aufgaben"]  # list of {text, hinweis}
    y = start_y - 1.5*cm - y_off

    for idx, aufg in enumerate(aufgaben):
        text = aufg["text"]
        hinweis = aufg.get("hinweis", "")

        # Number
        c.setFillColor(FARBEN[farb_key])
        c.setFont(FONT_BOLD, 12)
        c.drawString(1.8*cm, y, f"{idx + 1}.")

        # Problem text with proper word wrap using stringWidth
        c.setFillColor(FARBEN["dunkel"])
        c.setFont(FONT, 11)
        max_w = W - 4.3*cm  # 2.8cm left indent + 1.5cm right margin
        words = text.split()
        lines = []
        line = ""
        for w in words:
            test = (line + " " + w).strip()
            if c.stringWidth(test, FONT, 11) > max_w:
                lines.append(line)
                line = w
            else:
                line = test
        if line:
            lines.append(line)

        for li, l in enumerate(lines):
            c.drawString(2.8*cm, y - li * 0.5*cm, l)

        # Hint
        if hinweis:
            c.setFillColor(FARBEN["grau"])
            c.setFont(FONT_ITALIC, 9)
            c.drawString(2.8*cm, y - len(lines) * 0.5*cm - 0.15*cm, hinweis)

        # Rechnung + Antwort
        bottom = y - len(lines) * 0.5*cm - 0.8*cm
        c.setFillColor(FARBEN["grau"])
        c.setFont(FONT, 9)
        c.drawString(2.8*cm, bottom + 0.3*cm, "Rechnung:")
        draw_answer_box(c, 5.0*cm, bottom, w=4*cm, h=1.5*cm)
        c.setFillColor(FARBEN["grau"])
        c.setFont(FONT, 9)
        c.drawString(10*cm, bottom + 0.3*cm, "Antwort:")
        draw_answer_box(c, 12*cm, bottom, w=6*cm, h=1.5*cm)

        # Advance y dynamically based on actual content height
        y = bottom - 0.5*cm

    return y


# ── Würfel zuordnen ──────────────────────────────────────

def draw_wuerfel_zuordnen(c, abschnitt, farb_key, start_y):
    """Connect numbers on the left with matching dice on the right.
    For 'doppel' mode, two dice per row (sum must match the number)."""

    draw_section_label(c, abschnitt["titel"], farb_key, start_y)
    y_off = _draw_beschreibung(c, abschnitt, start_y)

    aufgaben = abschnitt["aufgaben"]  # list of ints (single) or [a, b] (double)
    doppel = abschnitt.get("doppel", False)
    loesungen = abschnitt.get("loesungen", [])

    n = len(aufgaben)
    row_h = 1.8*cm
    base_y = start_y - 1.5*cm - y_off

    # Left side: numbers; Right side: dice (shuffled order)
    # Build pairs: index -> dice value(s)
    items = []
    for aufg in aufgaben:
        if doppel:
            items.append(tuple(aufg))  # (a, b)
        else:
            items.append((aufg,))

    # Shuffle right side for the exercise
    shuffled_indices = list(range(n))
    # Use a fixed seed based on content for reproducibility
    seed = sum(sum(t) for t in items)
    _rnd.seed(seed)
    _rnd.shuffle(shuffled_indices)

    left_x = 2.5*cm
    right_x = W - 5.5*cm if doppel else W - 4*cm
    dice_size = 1.3*cm

    # Draw left side: numbers
    for i in range(n):
        y = base_y - i * row_h
        c.setFillColor(FARBEN["dunkel"])
        c.setFont(FONT_BOLD, 20)
        if doppel:
            num = items[i][0] + items[i][1]
        else:
            num = items[i][0]
        c.drawCentredString(left_x, y - dice_size * 0.4, str(num))

    # Draw right side: dice (shuffled)
    for i in range(n):
        si = shuffled_indices[i]
        y = base_y - i * row_h
        if doppel:
            a, b = items[si]
            _draw_würfel(c, right_x, y - dice_size, a, dice_size)
            _draw_würfel(c, right_x + dice_size + 0.3*cm, y - dice_size, b, dice_size)
        else:
            val = items[si][0]
            _draw_würfel(c, right_x, y - dice_size, val, dice_size)

    # Draw solution lines if loesungen present
    if loesungen:
        c.setStrokeColor(FARBEN["gruen"])
        c.setLineWidth(1.5)
        for i in range(n):
            # Find where item i ended up on right side
            right_pos = shuffled_indices.index(i)
            ly = base_y - i * row_h - dice_size * 0.3
            ry = base_y - right_pos * row_h - dice_size * 0.3
            c.line(left_x + 1.0*cm + 3, ly,
                   (right_x - 0.3*cm) - 3, ry)

    return base_y - n * row_h - 0.3*cm


# ── Zahlenkreis ──────────────────────────────────────────

def draw_zahlenkreis(c, abschnitt, farb_key, start_y):
    """Draws numbers in a circular arrangement."""
    draw_section_label(c, abschnitt["titel"], farb_key, start_y)
    y_off = _draw_beschreibung(c, abschnitt, start_y)

    aufgaben = abschnitt["aufgaben"]
    loesungen = abschnitt.get("loesungen", [])
    task_labels = abschnitt.get("labels", [])
    
    cols = 2
    col_w = (W - 3*cm) / cols
    row_h = 5.0*cm
    row_y = start_y - 1.5*cm - y_off - 2.5*cm
    
    for idx, aufg in enumerate(aufgaben):
        col = idx % cols
        row = idx // cols
        cx = 1.5*cm + col * col_w + col_w/2
        cy = row_y - row * row_h
        
        radius_kreis = 1.6*cm
        node_r = 0.5*cm
        
        num_nodes = len(aufg)
        task_loes = loesungen[idx] if idx < len(loesungen) else None
        if isinstance(task_loes, str):
            task_loes = task_loes.split(',')

        # Optional label below circle
        if idx < len(task_labels):
            c.setFillColor(FARBEN["grau"])
            c.setFont(FONT_ITALIC, 10)
            c.drawCentredString(cx, cy - radius_kreis - 0.9*cm, task_labels[idx])

        # Draw lines between nodes
        c.setStrokeColor(FARBEN["hellgrau"])
        c.setLineWidth(1.5)
        for i in range(num_nodes):
            a1 = math.radians(90 - i * (360/num_nodes))
            a2 = math.radians(90 - ((i+1) % num_nodes) * (360/num_nodes))
            x1 = cx + radius_kreis * math.cos(a1)
            y1 = cy + radius_kreis * math.sin(a1)
            x2 = cx + radius_kreis * math.cos(a2)
            y2 = cy + radius_kreis * math.sin(a2)
            
            # Shorten line
            dx, dy = x2 - x1, y2 - y1
            dist = math.sqrt(dx*dx + dy*dy)
            if dist > 0:
                nx, ny = dx/dist, dy/dist
                c.line(x1 + nx * node_r, y1 + ny * node_r,
                       x2 - nx * node_r, y2 - ny * node_r)

        # Draw nodes
        loes_idx = 0
        for i in range(num_nodes):
            angle = math.radians(90 - i * (360/num_nodes))
            nx = cx + radius_kreis * math.cos(angle)
            ny = cy + radius_kreis * math.sin(angle)

            val = aufg[i]
            is_blank = val is None

            if is_blank:
                c.setFillColor(FARBEN["antwort"])
                c.setStrokeColor(FARBEN[farb_key])
                c.setLineWidth(1.5)
                c.circle(nx, ny, node_r, fill=1, stroke=1)
                if task_loes and loes_idx < len(task_loes):
                     c.setFillColor(FARBEN["gruen"])
                     c.setFont(FONT_BOLD, 14)
                     c.drawCentredString(nx, ny - 0.15*cm, str(task_loes[loes_idx]))
                     loes_idx += 1
            else:
                c.setFillColor(FARBEN[farb_key])
                c.circle(nx, ny, node_r, fill=1, stroke=0)
                c.setFillColor(white)
                c.setFont(FONT_BOLD, 14)
                c.drawCentredString(nx, ny - 0.15*cm, str(val))
                
    total_rows = (len(aufgaben) + cols - 1) // cols
    return row_y - total_rows * row_h + 1.5*cm


# ── Gerade und Ungerade ──────────────────────────────────────

def _draw_gerade_ungerade_einkreisen(c, abschnitt, farb_key, y):
    zahlen = abschnitt["zahlen"]
    loes = abschnitt.get("loesungen", {})
    gerade_set = set(loes.get("gerade", []))

    cols = 5
    cell_w = (W - 4*cm) / cols
    cell_h = 1.6*cm
    x_start = 2*cm

    for idx, z in enumerate(zahlen):
        col = idx % cols
        row = idx // cols
        cx = x_start + col * cell_w + cell_w / 2
        cy = y - row * cell_h

        # Draw number in circle
        r = 0.55*cm
        if loes:
            # Solution mode: color blue for even, pink for odd
            if z in gerade_set:
                c.setFillColor(FARBEN["blau"])
            else:
                c.setFillColor(FARBEN["pink"])
            c.circle(cx, cy, r, fill=1, stroke=0)
            c.setFillColor(white)
        else:
            c.setFillColor(FARBEN["antwort"])
            c.setStrokeColor(FARBEN["hellgrau"])
            c.setLineWidth(1.5)
            c.circle(cx, cy, r, fill=1, stroke=1)
            c.setFillColor(FARBEN["dunkel"])

        c.setFont(FONT_BOLD, 16)
        c.drawCentredString(cx, cy - 0.2*cm, str(z))

    total_rows = (len(zahlen) + cols - 1) // cols
    y -= total_rows * cell_h + 0.3*cm

    # Legend
    c.setFillColor(FARBEN["blau"])
    c.circle(2.5*cm, y, 0.3*cm, fill=1, stroke=0)
    c.setFillColor(FARBEN["dunkel"])
    c.setFont(FONT, 10)
    c.drawString(3.1*cm, y - 0.12*cm, "= gerade")

    c.setFillColor(FARBEN["pink"])
    c.circle(6*cm, y, 0.3*cm, fill=1, stroke=0)
    c.setFillColor(FARBEN["dunkel"])
    c.drawString(6.6*cm, y - 0.12*cm, "= ungerade")
    return y - 0.8*cm


def _draw_gerade_ungerade_sortieren(c, abschnitt, farb_key, y):
    zahlen = abschnitt["zahlen"]
    loes = abschnitt.get("loesungen", {})

    # Draw two column headers
    left_x = 2.5*cm
    right_x = W / 2 + 1*cm
    col_w = W / 2 - 3*cm
    header_h = 0.9*cm

    # "Gerade" header
    c.setFillColor(FARBEN["blau"])
    c.roundRect(left_x, y - header_h, col_w, header_h, radius=6, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont(FONT_BOLD, 14)
    c.drawCentredString(left_x + col_w / 2, y - header_h + 0.22*cm, "Gerade")

    # "Ungerade" header
    c.setFillColor(FARBEN["pink"])
    c.roundRect(right_x, y - header_h, col_w, header_h, radius=6, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont(FONT_BOLD, 14)
    c.drawCentredString(right_x + col_w / 2, y - header_h + 0.22*cm, "Ungerade")

    y -= header_h + 0.5*cm

    # Unsorted numbers displayed in colored circles
    cols = 8
    cell_w = (W - 4*cm) / cols
    cell_h = 1.4*cm
    x_start = 2*cm

    for idx, z in enumerate(zahlen):
        col = idx % cols
        row = idx // cols
        cx = x_start + col * cell_w + cell_w / 2
        cy = y - row * cell_h

        c.setFillColor(FARBEN[farb_key])
        c.circle(cx, cy, 0.5*cm, fill=1, stroke=0)
        c.setFillColor(white)
        c.setFont(FONT_BOLD, 14)
        c.drawCentredString(cx, cy - 0.18*cm, str(z))

    total_rows = (len(zahlen) + cols - 1) // cols
    y -= total_rows * cell_h + 0.3*cm

    # Draw answer boxes in two columns
    gerade_loes = loes.get("gerade", [])
    ungerade_loes = loes.get("ungerade", [])
    # FIX: ceiling division to avoid missing boxes for odd number of values
    max_count = max(len(gerade_loes), len(ungerade_loes), (len(zahlen) + 1) // 2)
    box_w = 1.1*cm
    box_h = 0.9*cm
    box_cols = 4
    box_spacing = 1.3*cm

    for i in range(max_count):
        col = i % box_cols
        row = i // box_cols
        bx_left = left_x + col * box_spacing
        bx_right = right_x + col * box_spacing
        by = y - row * 1.2*cm

        # Left column (gerade)
        c.setFillColor(FARBEN["antwort"])
        c.setStrokeColor(FARBEN["blau"])
        c.setLineWidth(1.5)
        c.roundRect(bx_left, by - box_h, box_w, box_h, radius=4, fill=1, stroke=1)
        if i < len(gerade_loes):
            c.setFillColor(FARBEN["gruen"])
            c.setFont(FONT_BOLD, 14)
            c.drawCentredString(bx_left + box_w / 2, by - box_h + 0.2*cm,
                                str(gerade_loes[i]))

        # Right column (ungerade)
        c.setFillColor(FARBEN["antwort"])
        c.setStrokeColor(FARBEN["pink"])
        c.setLineWidth(1.5)
        c.roundRect(bx_right, by - box_h, box_w, box_h, radius=4, fill=1, stroke=1)
        if i < len(ungerade_loes):
            c.setFillColor(FARBEN["gruen"])
            c.setFont(FONT_BOLD, 14)
            c.drawCentredString(bx_right + box_w / 2, by - box_h + 0.2*cm,
                                str(ungerade_loes[i]))

    total_box_rows = (max_count + box_cols - 1) // box_cols
    return y - total_box_rows * 1.2*cm - 0.3*cm


def _draw_gerade_ungerade_muster(c, abschnitt, farb_key, y):
    muster_list = abschnitt.get("muster", [])
    loes = abschnitt.get("loesungen", [])
    row_h = 1.6*cm

    for idx, m in enumerate(muster_list):
        start_nums = m["start"]
        luecken = m["luecken"]
        loes_row = loes[idx] if idx < len(loes) else []

        mx = 2.2*cm
        my = y - idx * row_h

        # Exercise number
        c.setFillColor(FARBEN[farb_key])
        c.setFont(FONT_BOLD, 12)
        c.drawString(1.8*cm, my - 0.15*cm, f"{idx + 1}.")

        # Given numbers
        c.setFillColor(FARBEN["dunkel"])
        c.setFont(FONT_BOLD, 18)
        for i, n in enumerate(start_nums):
            c.drawCentredString(mx + 1*cm + i * 1.5*cm, my - 0.15*cm, str(n))
            if i < len(start_nums) - 1 or luecken > 0:
                c.setFillColor(FARBEN["hellgrau"])
                c.drawCentredString(mx + 1*cm + i * 1.5*cm + 0.75*cm,
                                    my - 0.15*cm, ",")
                c.setFillColor(FARBEN["dunkel"])

        # Blank boxes for continuation
        bx = mx + 1*cm + len(start_nums) * 1.5*cm
        for j in range(luecken):
            draw_answer_box(c, bx + j * 1.8*cm - 0.55*cm, my - 0.5*cm,
                            w=1.3*cm, h=1.1*cm)
            if j < len(loes_row):
                c.setFillColor(FARBEN["gruen"])
                c.setFont(FONT_BOLD, 16)
                c.drawCentredString(bx + j * 1.8*cm + 0.1*cm, my - 0.15*cm,
                                    str(loes_row[j]))
            if j < luecken - 1:
                c.setFillColor(FARBEN["hellgrau"])
                c.setFont(FONT_BOLD, 18)
                c.drawCentredString(bx + j * 1.8*cm + 0.75*cm,
                                    my - 0.15*cm, ",")

    return y - len(muster_list) * row_h - 0.3*cm


def draw_gerade_ungerade(c, abschnitt, farb_key, start_y):
    """Even/odd exercises: circling, sorting, or pattern continuation."""
    draw_section_label(c, abschnitt["titel"], farb_key, start_y)
    y_off = _draw_beschreibung(c, abschnitt, start_y)

    modus = abschnitt.get("modus", "einkreisen")
    y = start_y - 1.5*cm - y_off

    if modus == "einkreisen":
        return _draw_gerade_ungerade_einkreisen(c, abschnitt, farb_key, y)
    elif modus == "sortieren":
        return _draw_gerade_ungerade_sortieren(c, abschnitt, farb_key, y)
    elif modus == "muster":
        return _draw_gerade_ungerade_muster(c, abschnitt, farb_key, y)
    return y



# ── Dungeon-Flucht ───────────────────────────────────────────

def draw_dungeon_flucht(c, abschnitt, farb_key, start_y):
    """Draws a number grid where the student solves a task, then traces
    cells containing the answer from entrance to exit."""
    draw_section_label(c, abschnitt["titel"], farb_key, start_y)
    y_off = _draw_beschreibung(c, abschnitt, start_y)

    aufgaben = abschnitt.get("aufgaben", [])
    loes = abschnitt.get("loesungen")
    cy = start_y - 1.5*cm - y_off

    for a_idx, aufg in enumerate(aufgaben):
        grid = aufg["grid"]
        aufgabe_text = aufg["aufgabe"]
        antwort = aufg["antwort"]
        rows = len(grid)
        cols = len(grid[0])

        cell = 1.2 * cm
        grid_w = cols * cell
        grid_h = rows * cell
        # Center the grid horizontally, with space for labels
        gx = (W - grid_w) / 2
        gy = cy - grid_h

        # Draw task text
        c.setFillColor(FARBEN["dunkel"])
        c.setFont(FONT_BOLD, 11)
        c.drawString(2 * cm, cy + 0.1 * cm, f"Rechne: {aufgabe_text} = ?")

        # Draw answer box next to task
        task_text_w = c.stringWidth(f"Rechne: {aufgabe_text} = ?", FONT_BOLD, 11)
        draw_answer_box(c, 2.3 * cm + task_text_w, cy - 0.4 * cm, w=1.6 * cm, h=1.5 * cm)
        if loes and a_idx < len(loes):
            c.setFillColor(FARBEN["gruen"])
            c.setFont(FONT_BOLD, 12)
            c.drawCentredString(2.3 * cm + task_text_w + 0.8 * cm,
                                cy + 0.05 * cm, str(loes[a_idx]))

        cy -= 1.2 * cm  # space below task text (increased for taller answer box)
        gy = cy - grid_h

        # Entrance arrow
        entrance_col = aufg.get("eingang", 0)
        ex = gx + entrance_col * cell + cell / 2
        c.setFillColor(FARBEN[farb_key])
        c.setFont(FONT_BOLD, 9)
        c.drawCentredString(ex, cy + 0.35 * cm, "▼ Eingang")

        # Draw grid
        for ri, row in enumerate(grid):
            for ci, val in enumerate(row):
                x0 = gx + ci * cell
                y0 = cy - ri * cell - cell

                # Cell background
                if val == antwort:
                    c.setFillColor(FARBEN["antwort"])
                else:
                    c.setFillColor(white)
                c.setStrokeColor(FARBEN["hellgrau"])
                c.setLineWidth(1)
                c.rect(x0, y0, cell, cell, fill=1, stroke=1)

                # Number
                c.setFillColor(FARBEN["dunkel"])
                c.setFont(FONT_BOLD, 13)
                c.drawCentredString(x0 + cell / 2, y0 + cell / 2 - 0.15 * cm,
                                    str(val))

        # Exit arrow
        exit_col = aufg.get("ausgang", cols - 1)
        ax = gx + exit_col * cell + cell / 2
        c.setFillColor(FARBEN[farb_key])
        c.setFont(FONT_BOLD, 9)
        c.drawCentredString(ax, gy - 0.35 * cm, "Ausgang ▼")

        cy = gy - 0.9 * cm

    return cy


# ── Dungeon-Abenteuer ───────────────────────────────────────────

def draw_dungeon_abenteuer(c, abschnitt, farb_key, start_y):
    """Draws a number grid where the student follows a sequence of math operations
    from cell to cell to find the path to the exit."""
    draw_section_label(c, abschnitt["titel"], farb_key, start_y)
    y_off = _draw_beschreibung(c, abschnitt, start_y)

    aufgaben = abschnitt.get("aufgaben", [])
    loesungen = abschnitt.get("loesungen")
    cy = start_y - 1.5 * cm - y_off

    for a_idx, aufg in enumerate(aufgaben):
        grid = aufg["grid"]
        pfad = aufg.get("pfad", [])
        entrance_col = aufg.get("eingang", 0)
        rows = len(grid)
        cols = len(grid[0])

        start_wert = grid[0][entrance_col]
        task_loes = loesungen[a_idx] if loesungen and a_idx < len(loesungen) else None

        cell = 1.2 * cm
        grid_w = cols * cell
        grid_h = rows * cell
        gx = (W - grid_w) / 2

        # Draw task/path description
        c.setFillColor(FARBEN["dunkel"])
        c.setFont(FONT_BOLD, 10)
        tx = 2 * cm
        txt = f"Start bei {start_wert}"
        c.drawString(tx, cy + 0.1 * cm, txt)
        tx += c.stringWidth(txt, FONT_BOLD, 10) + 0.3 * cm

        for i, op in enumerate(pfad):
            c.setFont(FONT, 10)
            c.drawString(tx, cy + 0.1 * cm, "➔")
            tx += 0.5 * cm
            c.setFont(FONT_BOLD, 10)
            c.drawString(tx, cy + 0.1 * cm, op)
            tx += c.stringWidth(op, FONT_BOLD, 10) + 0.2 * cm

        cy -= 0.7 * cm
        gy = cy - grid_h

        # Entrance arrow
        ex = gx + entrance_col * cell + cell / 2
        c.setFillColor(FARBEN[farb_key])
        c.setFont(FONT_BOLD, 9)
        c.drawCentredString(ex, cy + 0.35 * cm, "▼ Eingang")

        # Draw grid
        for ri, row in enumerate(grid):
            for ci, val in enumerate(row):
                x0 = gx + ci * cell
                y0 = cy - ri * cell - cell

                # Highlight the path if in solution mode
                if task_loes and val in task_loes:
                    c.setFillColor(FARBEN["antwort"])
                else:
                    c.setFillColor(white)

                c.setStrokeColor(FARBEN["hellgrau"])
                c.setLineWidth(1)
                c.rect(x0, y0, cell, cell, fill=1, stroke=1)

                # Number
                c.setFillColor(FARBEN["dunkel"])
                c.setFont(FONT_BOLD, 13)
                c.drawCentredString(x0 + cell / 2, y0 + cell / 2 - 0.15 * cm, str(val))

        # Exit arrow
        exit_col = aufg.get("ausgang", cols - 1)
        ax = gx + exit_col * cell + cell / 2
        c.setFillColor(FARBEN[farb_key])
        c.setFont(FONT_BOLD, 9)
        c.drawCentredString(ax, gy - 0.35 * cm, "Ausgang ▼")

        cy = gy - 0.9 * cm

    return cy


# ── Zehnerübergang ───────────────────────────────────────

def draw_zehneruebergang(c, abschnitt, farb_key, start_y):
    """
    Zeichnet Zehnerübergang-Aufgaben im Format:
    Addition:    a + b = a + ___ + ___ = ___
    Subtraktion: a - b = a - ___ - ___ = ___
    Die Zerlegung geht schrittweise über die 10.
    """
    draw_section_label(c, abschnitt["titel"], farb_key, start_y)
    y_off = _draw_beschreibung(c, abschnitt, start_y)

    aufgaben = abschnitt["aufgaben"]
    loesungen = abschnitt.get("loesungen", [None] * len(aufgaben))
    row_y = start_y - 1.5 * cm - y_off
    row_h = 2.2 * cm

    dunkel = FARBEN["dunkel"]
    op_col = FARBEN[farb_key]
    box_w = 1.6 * cm
    box_h = 1.5 * cm

    for idx, aufg in enumerate(aufgaben):
        a, op, b = aufg
        loes = loesungen[idx] if idx < len(loesungen) else None
        y = row_y - idx * row_h
        x = 1.8 * cm

        c.setFont(FONT_BOLD, 18)

        # a
        c.setFillColor(dunkel)
        c.drawCentredString(x + 0.5 * cm, y, str(a))
        x += 1.2 * cm

        # op
        c.setFillColor(op_col)
        c.drawCentredString(x + 0.3 * cm, y, op)
        x += 0.9 * cm

        # b
        c.setFillColor(dunkel)
        c.drawCentredString(x + 0.5 * cm, y, str(b))
        x += 1.2 * cm

        # =
        c.setFillColor(op_col)
        c.drawCentredString(x + 0.3 * cm, y, "=")
        x += 0.8 * cm

        # a (repeated)
        c.setFillColor(dunkel)
        c.drawCentredString(x + 0.5 * cm, y, str(a))
        x += 1.2 * cm

        # op
        c.setFillColor(op_col)
        c.drawCentredString(x + 0.3 * cm, y, op)
        x += 0.7 * cm

        # First blank: step1 (how much to reach 10)
        if loes is not None:
            _draw_filled_answer_box(c, x, y - 0.25 * cm, loes[0], w=box_w, h=box_h)
        else:
            draw_answer_box(c, x, y - 0.25 * cm, w=box_w, h=box_h)
        x += box_w + 0.3 * cm

        # op
        c.setFillColor(op_col)
        c.drawCentredString(x + 0.3 * cm, y, op)
        x += 0.7 * cm

        # Second blank: step2 (remainder)
        if loes is not None:
            _draw_filled_answer_box(c, x, y - 0.25 * cm, loes[1], w=box_w, h=box_h)
        else:
            draw_answer_box(c, x, y - 0.25 * cm, w=box_w, h=box_h)
        x += box_w + 0.3 * cm

        # =
        c.setFillColor(op_col)
        c.drawCentredString(x + 0.3 * cm, y, "=")
        x += 0.8 * cm

        # Third blank: final result
        if loes is not None:
            _draw_filled_answer_box(c, x, y - 0.25 * cm, loes[2], w=box_w, h=box_h)
        else:
            draw_answer_box(c, x, y - 0.25 * cm, w=box_w, h=box_h)

    return row_y - len(aufgaben) * row_h - 0.5 * cm


# ── Gerade und Ungerade Zahlen ──────────────────────────

def draw_gerade_ungerade(c, abschnitt, farb_key, start_y):
    """Sort and color even/odd numbers."""
    draw_section_label(c, abschnitt["titel"], farb_key, start_y)
    y_off = _draw_beschreibung(c, abschnitt, start_y)
    
    modus = abschnitt.get("modus", "sortieren") # sortieren, malen, muster
    aufgaben = abschnitt.get("aufgaben", [])
    loesungen = abschnitt.get("loesungen", [])
    row_y = start_y - 1.2*cm - y_off
    
    if modus == "sortieren":
        # Sort given numbers into two boxes: "Gerade" and "Ungerade"
        box_w = (W - 5*cm) / 2
        box_h = 2.5*cm
        
        for ai, aufg in enumerate(aufgaben):
            if row_y < 4*cm:
                return row_y
                
            zahlen = aufg["zahlen"]
            loes = loesungen[ai] if ai < len(loesungen) else None
            
            # Draw original numbers in a row
            c.setFont(FONT_BOLD, 14)
            c.setFillColor(FARBEN["dunkel"])
            num_str = "  ".join(map(str, zahlen))
            c.drawCentredString(W/2, row_y, num_str)
            row_y -= 0.8*cm
            
            # Draw the two boxes
            bx_gerade = 2*cm
            bx_ungerade = W/2 + 0.5*cm
            
            # Gerade Box
            c.setStrokeColor(FARBEN["blau"])
            c.roundRect(bx_gerade, row_y - box_h, box_w, box_h, radius=8, fill=0, stroke=1)
            c.setFillColor(FARBEN["blau"])
            c.setFont(FONT_BOLD, 10)
            c.drawString(bx_gerade + 0.3*cm, row_y - 0.4*cm, "Gerade")
            
            # Ungerade Box
            c.setStrokeColor(FARBEN["pink"])
            c.roundRect(bx_ungerade, row_y - box_h, box_w, box_h, radius=8, fill=0, stroke=1)
            c.setFillColor(FARBEN["pink"])
            c.setFont(FONT_BOLD, 10)
            c.drawString(bx_ungerade + 0.3*cm, row_y - 0.4*cm, "Ungerade")
            
            if loes:
                c.setFont(FONT_BOLD, 14)
                c.setFillColor(FARBEN["gruen"])
                c.drawCentredString(bx_gerade + box_w/2, row_y - 1.5*cm, ", ".join(map(str, loes[0])))
                c.drawCentredString(bx_ungerade + box_w/2, row_y - 1.5*cm, ", ".join(map(str, loes[1])))
            
            row_y -= box_h + 0.8*cm
            
    elif modus == "malen":
        # Color even blue and odd pink
        node_r = 0.6*cm
        spacing = 1.5*cm
        
        for ai, aufg in enumerate(aufgaben):
            zahlen = aufg["zahlen"]
            loes = loesungen[ai] if ai < len(loesungen) else None # list of colors
            
            c.setFont(FONT_BOLD, 10)
            c.setFillColor(FARBEN["grau"])
            c.drawString(2*cm, row_y + 0.5*cm, "Gerade = blau, Ungerade = pink")
            
            for i, z in enumerate(zahlen):
                cx = 2.5*cm + i * spacing
                c.setStrokeColor(FARBEN["hellgrau"])
                c.setLineWidth(1)
                
                fill_col = FARBEN["antwort"]
                if loes and i < len(loes):
                    fill_col = FARBEN["blau"] if loes[i] == "G" else FARBEN["pink"]
                
                c.setFillColor(fill_col)
                c.circle(cx, row_y, node_r, fill=1, stroke=1)
                
                c.setFillColor(FARBEN["dunkel"] if fill_col == FARBEN["antwort"] else white)
                c.setFont(FONT_BOLD, 14)
                c.drawCentredString(cx, row_y - 0.15*cm, str(z))
                
            row_y -= 2*cm

    elif modus == "muster":
        # Complete pattern: 2, 4, 6, ...
        for ai, aufg in enumerate(aufgaben):
            start_zahlen = aufg["start"]
            n_blanks = aufg["lücken"]
            loes = loesungen[ai] if ai < len(loesungen) else None
            
            x = 2*cm
            box_w = 1.4*cm
            box_h = 1.2*cm

            # Draw start numbers
            c.setFont(FONT_BOLD, 16)
            for z in start_zahlen:
                c.setFillColor(FARBEN[farb_key])
                c.roundRect(x, row_y - 0.6*cm, box_w, box_h, radius=4, fill=1, stroke=0)
                c.setFillColor(white)
                c.drawCentredString(x + box_w/2, row_y - 0.15*cm, str(z))
                x += box_w + 0.3*cm

            # Draw blanks
            for i in range(n_blanks):
                if loes and i < len(loes):
                    _draw_filled_answer_box(c, x, row_y - 0.6*cm, str(loes[i]), w=box_w, h=box_h)
                else:
                    draw_answer_box(c, x, row_y - 0.6*cm, w=box_w, h=box_h)
                x += box_w + 0.3*cm

            row_y -= 2.0*cm

    elif modus == "paare":
        # Visual representation: 2 columns of pairs
        row_h = 1.6 * cm
        dot_r = 0.2 * cm
        gap = 0.25 * cm
        
        for idx, aufg in enumerate(aufgaben):
            zahlen = aufg.get("zahlen", [])
            for z_idx, z in enumerate(zahlen):
                # Max 2 columns
                items_per_col = (len(zahlen) + 1) // 2
                col = z_idx // items_per_col
                row = z_idx % items_per_col
                cx = 2.2 * cm + col * 9 * cm
                cy = row_y - row * row_h
                
                c.setFillColor(FARBEN["dunkel"])
                c.setFont(FONT_BOLD, 14)
                c.drawString(cx, cy, f"{z}:")
                
                # Draw pairs
                dot_x = cx + 1.2 * cm
                for i in range(z):
                    pair_idx = i // 2
                    is_top = i % 2 == 0
                    dx = dot_x + pair_idx * (dot_r * 2 + gap)
                    dy = cy + (0.2 * cm if is_top else -0.2 * cm)
                    c.setFillColor(FARBEN[farb_key])
                    c.circle(dx, dy, dot_r, fill=1, stroke=0)
                    
                # Question text and box
                c.setFillColor(FARBEN["grau"])
                c.setFont(FONT, 10)
                c.drawString(cx + 4.5 * cm, cy, "Gerade?")
                draw_answer_box(c, cx + 6.0 * cm, cy - 0.6 * cm, w=1.4 * cm, h=1.2 * cm)
                
            row_y -= (len(zahlen) + 1) // 2 * row_h

    return row_y


# ── Rechenquadrat 2×2 ────────────────────────────────────

def draw_rechenquadrat_2x2(c, abschnitt, farb_key, start_y):
    """2x2 calculation square with row and column sums."""
    draw_section_label(c, abschnitt["titel"], farb_key, start_y)
    y_off = _draw_beschreibung(c, abschnitt, start_y)

    quadrate = abschnitt.get("quadrate", [])
    if not quadrate:
        return start_y - (2.5*cm + y_off)

    cell_size = 1.3*cm
    col_w = (W - 3*cm) / 3
    row_y = start_y - 2.5*cm - y_off

    for idx, q in enumerate(quadrate):
        col = idx % 3
        row = idx // 3
        x0 = 1.5*cm + col * col_w + (col_w - 3.5*cell_size)/2
        y0 = row_y - row * 4.5*cm

        werte = q["werte"]   # [a, b, c, d] in 2x2 grid
        summen = q["summen"] # [s_r1, s_r2, s_c1, s_c2]

        for r in range(2):
            for cl in range(2):
                val = werte[r*2 + cl]
                cx = x0 + cl * cell_size
                cy = y0 - r * cell_size
                c.setStrokeColor(FARBEN[farb_key])
                c.setLineWidth(1.5)
                c.rect(cx, cy, cell_size, cell_size, fill=0, stroke=1)
                if val is not None:
                    c.setFillColor(FARBEN["dunkel"])
                    c.setFont(FONT_BOLD, 14)
                    c.drawCentredString(cx + cell_size/2, cy + cell_size/2 - 0.15*cm, str(val))
                else:
                    draw_answer_box(c, cx + 0.1*cm, cy + 0.1*cm,
                                    w=cell_size - 0.2*cm, h=cell_size - 0.2*cm)

        c.setFillColor(FARBEN["grau"])
        c.setFont(FONT_ITALIC, 11)
        c.drawCentredString(x0 + 2.5*cell_size, y0 + cell_size/2 - 0.15*cm, str(summen[0]))
        c.drawCentredString(x0 + 2.5*cell_size, y0 - cell_size/2 - 0.15*cm, str(summen[1]))
        c.drawCentredString(x0 + cell_size/2,   y0 - 1.8*cell_size,          str(summen[2]))
        c.drawCentredString(x0 + 1.5*cell_size, y0 - 1.8*cell_size,          str(summen[3]))

        c.setDash(1, 2)
        c.line(x0 + 2.1*cell_size, y0 + cell_size/2, x0 + 2.1*cell_size, y0 - 1.5*cell_size)
        c.line(x0, y0 - 1.3*cell_size, x0 + 2.1*cell_size, y0 - 1.3*cell_size)
        c.setDash()

    total_rows = (len(quadrate) + 2) // 3
    return row_y - total_rows * 4.5*cm + 1.5*cm


# ── Muster fortsetzen ────────────────────────────────────

def draw_muster_fortsetzen(c, abschnitt, farb_key, start_y):
    """Draws pattern continuation exercises: students fill in missing values."""
    draw_section_label(c, abschnitt["titel"], farb_key, start_y)
    y_off = _draw_beschreibung(c, abschnitt, start_y)

    aufgaben = abschnitt["aufgaben"]
    box_w = 1.6 * cm
    box_h = 1.5 * cm
    gap = 0.3 * cm
    row_h = 2.3 * cm
    row_y = start_y - 1.8 * cm - y_off

    for idx, aufg in enumerate(aufgaben):
        muster = aufg.get("muster") or aufg.get("elemente", [])
        x0 = 1.8 * cm
        y0 = row_y - idx * row_h

        # Task number
        c.setFillColor(FARBEN["dunkel"])
        c.setFont("Helvetica-Bold", 11)
        c.drawString(x0 - 0.3 * cm, y0 - box_h / 2 - 0.15 * cm,
                     f"{idx + 1})")

        for j, val in enumerate(muster):
            bx = x0 + 0.5 * cm + j * (box_w + gap)
            is_blank = val is None

            if is_blank:
                # Answer box for blanks
                c.setFillColor(FARBEN["antwort"])
                c.setStrokeColor(FARBEN[farb_key])
                c.setLineWidth(1.5)
                c.roundRect(bx, y0 - box_h, box_w, box_h,
                            radius=5, fill=1, stroke=1)
            else:
                # Filled box with value
                c.setFillColor(FARBEN[farb_key])
                c.setStrokeColor(FARBEN[farb_key])
                c.setLineWidth(1.5)
                c.roundRect(bx, y0 - box_h, box_w, box_h,
                            radius=5, fill=1, stroke=1)
                c.setFillColor(white)
                c.setFont("Helvetica-Bold", 16)
                c.drawCentredString(bx + box_w / 2,
                                    y0 - box_h / 2 - 0.2 * cm,
                                    str(val))

            # Arrow between boxes (except after last)
            if j < len(muster) - 1:
                arrow_x = bx + box_w + 0.02 * cm
                arrow_y = y0 - box_h / 2
                c.setStrokeColor(FARBEN["hellgrau"])
                c.setLineWidth(1.5)
                c.line(arrow_x, arrow_y,
                       arrow_x + gap - 0.04 * cm, arrow_y)

    total_rows = len(aufgaben)
    return row_y - total_rows * row_h - 0.3 * cm


# ── Motivation / Lob / Fakten ──────────────────────────────

def draw_motivation(c, abschnitt, farb_key, start_y):
    """Zeichnet eine motivierende Callout-Box (Lob, Fakt oder Mini-Aufgabe).

    YAML-Format:
        typ: motivation
        modus: "lob"   # oder "fakt" oder "aufgabe"
        emoji: "⭐"
        titel: "Super gemacht!"
        text: "Du machst das toll! Weiter so!"
    """
    from layout import draw_emoji

    modus = abschnitt.get("modus", "lob")
    emoji = abschnitt.get("emoji", "⭐")
    titel = abschnitt.get("titel", "")
    text = abschnitt.get("text", "")

    # Farbschema je nach Modus
    if modus == "fakt":
        bg_color = HexColor("#E6F4FF")
        border_color = FARBEN["blau"]
    elif modus == "aufgabe":
        bg_color = HexColor("#E6FFE6")
        border_color = FARBEN["gruen"]
    else:  # "lob" und Standard
        bg_color = HexColor("#FFF9E6")
        border_color = FARBEN["orange"]

    BOX_W = 15 * cm
    BOX_X = (W - BOX_W) / 2
    BORDER_W = 0.35 * cm
    PADDING_H = 0.5 * cm
    PADDING_V = 0.45 * cm
    EMOJI_SIZE = 24
    TITEL_SIZE = 14
    TEXT_SIZE = 12

    # Textbereich-Breite: Box abzüglich linkem Rand (Emoji + Border) und Padding
    EMOJI_LEFT_MARGIN = 0.9 * cm
    BORDER_RIGHT_MARGIN = 0.3 * cm
    TEXT_PADDING_H = PADDING_H

    text_x = BOX_X + BORDER_W + EMOJI_LEFT_MARGIN + BORDER_RIGHT_MARGIN
    text_max_w = BOX_W - BORDER_W - EMOJI_LEFT_MARGIN - BORDER_RIGHT_MARGIN - TEXT_PADDING_H

    # Texthöhe berechnen (Titel + umgebrochener Text)
    titel_h = (TITEL_SIZE + 4) / 72 * 2.54 * cm
    text_lines = _wrap_text(c, text, FONT, TEXT_SIZE, text_max_w) if text else []
    line_h = (TEXT_SIZE + 3) / 72 * 2.54 * cm
    text_block_h = len(text_lines) * line_h

    box_h = PADDING_V + titel_h + (0.2 * cm if text_lines else 0) + text_block_h + PADDING_V

    # Hintergrund-Rechteck
    c.setFillColor(bg_color)
    c.setStrokeColor(border_color)
    c.setLineWidth(0)
    c.roundRect(BOX_X, start_y - box_h, BOX_W, box_h, radius=8, fill=1, stroke=0)

    # Linker farbiger Rand
    c.setFillColor(border_color)
    c.roundRect(BOX_X, start_y - box_h, BORDER_W, box_h, radius=4, fill=1, stroke=0)

    # Emoji links
    emoji_cx = BOX_X + BORDER_W + 0.55 * cm
    emoji_cy = start_y - box_h / 2
    draw_emoji(c, emoji, emoji_cx, emoji_cy, EMOJI_SIZE)

    # Titel (fett)
    titel_y = start_y - PADDING_V - titel_h * 0.75
    c.setFillColor(FARBEN["dunkel"])
    c.setFont(FONT_BOLD, TITEL_SIZE)
    c.drawString(text_x, titel_y, titel)

    # Beschreibungstext (normal, umgebrochen)
    text_y = titel_y - titel_h * 0.5 - (0.15 * cm if text_lines else 0)
    c.setFont(FONT, TEXT_SIZE)
    for line in text_lines:
        c.drawString(text_x, text_y, line)
        text_y -= line_h

    return start_y - box_h - 0.4 * cm
