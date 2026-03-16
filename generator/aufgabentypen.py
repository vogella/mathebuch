"""
aufgabentypen.py – Zeichenfunktionen für jeden Aufgabentyp
"""
from reportlab.lib.colors import HexColor, white
from reportlab.lib.units import cm
from reportlab.lib.pagesizes import A4
from layout import FARBEN, draw_answer_box, draw_section_label

W, H = A4


def _draw_beschreibung(c, abschnitt, start_y):
    """Draws optional beschreibung text below section label. Returns y offset."""
    beschreibung = abschnitt.get("beschreibung")
    if not beschreibung:
        return 0
    c.setFillColor(FARBEN["dunkel"])
    c.setFont("Helvetica", 10)
    max_w = W - 4*cm
    # Word-wrap
    words = beschreibung.split()
    lines = []
    line = ""
    for w in words:
        test = (line + " " + w).strip()
        if c.stringWidth(test, "Helvetica", 10) > max_w:
            lines.append(line)
            line = w
        else:
            line = test
    if line:
        lines.append(line)
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
            c.setFont("Helvetica-Bold", 12)
            c.drawString(2*cm, y, zeile[2:].strip())
            y -= 0.7*cm
        elif zeile.startswith("**"):
            # Bold example line
            c.setFillColor(FARBEN["dunkel"])
            c.setFont("Helvetica-Bold", 11)
            c.drawString(2.5*cm, y, zeile.strip().strip('*').strip())
            y -= 0.6*cm
        else:
            c.setFillColor(FARBEN["dunkel"])
            c.setFont("Helvetica", 10)
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
    halb = len(aufgaben) // 2
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


def _draw_filled_answer_box(c, x, y, text, w=1.6*cm, h=1.1*cm):
    """Answer box with a solution value shown inside."""
    draw_answer_box(c, x, y, w, h)
    c.setFillColor(FARBEN["gruen"])
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(x + w/2, y + h/2 - 0.2*cm, str(text))


def _draw_aufgabe_row(c, x, y, aufg, farb_key, loesung=None):
    a, op, b, ergebnis = aufg
    op_col = FARBEN[farb_key]
    dunkel = FARBEN["dunkel"]

    c.setFont("Helvetica-Bold", 20)
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
    beschreibung = abschnitt.get("beschreibung", "")
    hinweis = abschnitt.get("hinweis", "")
    y_offset = 0
    if beschreibung:
        c.setFillColor(FARBEN["dunkel"])
        c.setFont("Helvetica", 10)
        c.drawString(2*cm, start_y - 0.9*cm, beschreibung)
        y_offset += 0.6*cm
    if hinweis:
        c.setFillColor(FARBEN["grau"])
        c.setFont("Helvetica-Oblique", 9)
        c.drawString(2*cm, start_y - 0.9*cm - y_offset, hinweis)
        y_offset += 0.6*cm

    # Verbotene Zahlen mit rotem X
    verboten = abschnitt.get("verboten", [])
    if verboten:
        vx = 2*cm
        vy = start_y - 0.9*cm - y_offset
        c.setFont("Helvetica-Bold", 10)
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
            c.setFont("Helvetica-Bold", 12)
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
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(cx, ty - roof_size * 0.65, str(roof_num))
    # Felder
    box_w = 1.3*cm
    box_h = 1.1*cm
    bx = cx - roof_size
    by = ty - roof_size * 0.9 - box_h
    colors = [FARBEN["antwort"], HexColor("#FFF0E8")]
    for j in range(2):
        c.setFillColor(colors[j])
        c.setStrokeColor(FARBEN["orange"])
        c.setLineWidth(1.5)
        c.roundRect(bx + j * box_w, by, box_w, box_h, radius=4, fill=1, stroke=1)
        if loesung is not None:
            c.setFillColor(FARBEN["gruen"])
            c.setFont("Helvetica-Bold", 16)
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
        c.setFillColor(white if not is_answer else FARBEN["blau"])
        c.setFont("Helvetica-Bold", 13 if len(seg) <= 2 else 11)
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
        c.setFont("Helvetica-Bold", font_size)
        label = str(val) if val is not None else "?"
        c.drawCentredString(px, py - 0.15*cm, label)


def _draw_tipp_box(c, x, y, tipp_zeilen):
    """Draws a tip box with custom lines of text."""
    box_h = max(3*cm, (len(tipp_zeilen) + 1) * 0.65*cm + 1*cm)
    c.setFillColor(HexColor("#FFFBEA"))
    c.setStrokeColor(FARBEN["yellow"])
    c.setLineWidth(1.5)
    c.roundRect(x, y - box_h/2, 6*cm, box_h, radius=8, fill=1, stroke=1)
    c.setFillColor(FARBEN["dunkel"])
    c.setFont("Helvetica-Bold", 11)
    top_y = y + box_h/2 - 1*cm
    c.drawString(x + 0.5*cm, top_y, "💡 Tipp:")
    c.setFont("Helvetica", 10)
    for j, line in enumerate(tipp_zeilen):
        c.drawString(x + 0.5*cm, top_y - (j+1)*0.65*cm, line)


def draw_magisches_dreieck(c, abschnitt, farb_key, start_y):
    draw_section_label(c, abschnitt["titel"], farb_key, start_y)
    y_off = _draw_beschreibung(c, abschnitt, start_y)

    hinweis_text = abschnitt.get("hinweis", "")
    if hinweis_text:
        c.setFillColor(FARBEN["dunkel"])
        c.setFont("Helvetica", 10)
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
        c.setFont("Helvetica-Bold", 11)
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
        c.setFont("Helvetica-Bold", 18)
        lbl = str(val) if val is not None else "?"
        c.drawCentredString(cx + cell/2, cy + cell/2 - 0.2*cm, lbl)

    # Sum indicators on the right and bottom
    c.setFillColor(FARBEN["dunkel"])
    c.setFont("Helvetica-Bold", 12)
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
        c.setFont("Helvetica-Bold", 11)
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
                c.setFont("Helvetica-Bold", 18)
                c.drawCentredString(cx + 0.4*cm, y0 - dice_size * 0.6, op_char)
                cx += 0.8*cm
            _draw_würfel(c, cx, y0 - dice_size, wert, dice_size)
            cx += dice_size

        # Equals sign and answer box
        c.setFillColor(FARBEN[farb_key])
        c.setFont("Helvetica-Bold", 18)
        c.drawCentredString(cx + 0.5*cm, y0 - dice_size * 0.6, "=")
        loesungen = abschnitt.get("loesungen", [])
        if idx < len(loesungen):
            _draw_filled_answer_box(c, cx + 0.9*cm, y0 - dice_size * 0.85,
                                    loesungen[idx], w=1.3*cm, h=1.1*cm)
        else:
            draw_answer_box(c, cx + 0.9*cm, y0 - dice_size * 0.85, w=1.3*cm, h=1.1*cm)

    total_rows = (len(aufgaben) + cols - 1) // cols
    return row_y - total_rows * row_h - 0.3*cm


# ── Rechenmauer ───────────────────────────────────────────

def draw_rechenmauer(c, abschnitt, farb_key, start_y):
    """Number wall: each brick = sum of the two below it."""
    draw_section_label(c, abschnitt["titel"], farb_key, start_y)
    y_off = _draw_beschreibung(c, abschnitt, start_y)

    mauern = abschnitt["mauern"]  # list of walls, each a list of rows bottom-to-top
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
            c.setFont("Helvetica-Bold", 11)
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
                    c.setFont("Helvetica-Bold", 16)
                    c.drawCentredString(bx + brick_w/2, ry + brick_h/2 - 0.2*cm, str(val))

        # Remember this wall as reference for the next (Lösung) wall
        aufgabe_mauer = rows

    bottom_y = start_y - top_offset - (max(len(m) for m in mauern) - 1) * brick_h
    return bottom_y - brick_h - 0.5*cm


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
        c.setFont("Helvetica-Bold", 18)
        c.drawRightString(x + 2.5*cm, y, str(links))
        # Circle for >, < or =
        circle_x = x + 3.3*cm
        c.setFillColor(FARBEN["antwort"])
        c.setStrokeColor(FARBEN[farb_key])
        c.setLineWidth(1.5)
        c.circle(circle_x, y + 0.2*cm, 0.5*cm, fill=1, stroke=1)
        if loes is not None:
            c.setFillColor(FARBEN["gruen"])
            c.setFont("Helvetica-Bold", 18)
            c.drawCentredString(circle_x, y + 0.02*cm, str(loes))
        c.setFillColor(FARBEN["dunkel"])
        c.setFont("Helvetica-Bold", 18)
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
    halb = (len(aufgaben) + 1) // 2

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
                c.setFont("Helvetica-Bold", 18)
                c.drawCentredString(bx + box_w/2, y0 - box_h/2 - 0.2*cm, str(val))
            elif loes is not None and j < len(loes) and loes[j] is not None:
                # Show solution in green
                c.setFillColor(FARBEN["gruen"])
                c.setFont("Helvetica-Bold", 18)
                c.drawCentredString(bx + box_w/2, y0 - box_h/2 - 0.2*cm, str(loes[j]))

        # Arrows between boxes
        c.setStrokeColor(FARBEN["hellgrau"])
        c.setLineWidth(2)
        for j in range(2):
            ax = x0 + (j + 1) * box_w + j * gap + gap/2
            c.line(ax, y0 - box_h/2, ax + gap, y0 - box_h/2)

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
    row_h = 2.8*cm
    circle_r = 0.55*cm
    row_y = start_y - 1.5*cm - y_off

    for idx, aufg in enumerate(aufgaben):
        zahl, t1, t2 = aufg
        col = idx % cols
        row = idx // cols
        cx = 1.5*cm + col * col_w + col_w / 2
        y0 = row_y - row * row_h

        # Top circle (the number)
        c.setFillColor(FARBEN[farb_key])
        c.circle(cx, y0, circle_r, fill=1, stroke=0)
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(cx, y0 - 0.2*cm, str(zahl))

        # Lines down to two parts
        left_cx = cx - 1.0*cm
        right_cx = cx + 1.0*cm
        part_y = y0 - 1.8*cm
        c.setStrokeColor(FARBEN["hellgrau"])
        c.setLineWidth(2)
        c.line(cx, y0 - circle_r, left_cx, part_y + circle_r)
        c.line(cx, y0 - circle_r, right_cx, part_y + circle_r)

        # Left part
        is_blank_l = t1 is None
        c.setFillColor(FARBEN["antwort"] if is_blank_l else FARBEN[farb_key])
        c.setStrokeColor(FARBEN[farb_key] if is_blank_l else HexColor("#00000000"))
        c.setLineWidth(1.5)
        c.circle(left_cx, part_y, circle_r, fill=1, stroke=1 if is_blank_l else 0)
        c.setFillColor(FARBEN["blau"] if is_blank_l else white)
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(left_cx, part_y - 0.2*cm,
                            str(t1) if t1 is not None else "?")

        # Right part
        is_blank_r = t2 is None
        c.setFillColor(FARBEN["antwort"] if is_blank_r else FARBEN[farb_key])
        c.setStrokeColor(FARBEN[farb_key] if is_blank_r else HexColor("#00000000"))
        c.setLineWidth(1.5)
        c.circle(right_cx, part_y, circle_r, fill=1, stroke=1 if is_blank_r else 0)
        c.setFillColor(FARBEN["blau"] if is_blank_r else white)
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(right_cx, part_y - 0.2*cm,
                            str(t2) if t2 is not None else "?")

    total_rows = (len(aufgaben) + cols - 1) // cols
    return row_y - total_rows * row_h - 0.3*cm


# ── Kettenaufgaben ────────────────────────────────────────

def draw_kettenaufgaben(c, abschnitt, farb_key, start_y):
    """Chain calculations: 3 + 2 − 1 + 4 = ?"""
    draw_section_label(c, abschnitt["titel"], farb_key, start_y)
    y_off = _draw_beschreibung(c, abschnitt, start_y)

    aufgaben = abschnitt["aufgaben"]  # list of strings like "3 + 2 − 1 + 4"
    loesungen = abschnitt.get("loesungen", [])
    row_y = start_y - 1.5*cm - y_off
    row_h = 1.5*cm

    for idx, kette in enumerate(aufgaben):
        y = row_y - idx * row_h
        c.setFillColor(FARBEN["dunkel"])
        c.setFont("Helvetica-Bold", 18)

        # Number the exercise
        c.setFillColor(FARBEN[farb_key])
        c.setFont("Helvetica-Bold", 12)
        c.drawString(1.8*cm, y + 0.05*cm, f"{idx + 1}.")

        # The chain expression
        c.setFillColor(FARBEN["dunkel"])
        c.setFont("Helvetica-Bold", 18)
        c.drawString(2.8*cm, y, kette)

        # = and answer box
        text_w = c.stringWidth(kette, "Helvetica-Bold", 18)
        eq_x = 2.8*cm + text_w + 0.5*cm
        c.setFillColor(FARBEN[farb_key])
        c.drawString(eq_x, y, "=")
        if idx < len(loesungen):
            _draw_filled_answer_box(c, eq_x + 1.0*cm, y - 0.25*cm,
                                    loesungen[idx], w=1.6*cm, h=1.1*cm)
        else:
            draw_answer_box(c, eq_x + 1.0*cm, y - 0.25*cm, w=1.6*cm, h=1.1*cm)

    return row_y - len(aufgaben) * row_h - 0.3*cm


# ── Tauschaufgaben ────────────────────────────────────────

def draw_tauschaufgaben(c, abschnitt, farb_key, start_y):
    """Commutative property: show a + b = b + a."""
    draw_section_label(c, abschnitt["titel"], farb_key, start_y)
    y_off = _draw_beschreibung(c, abschnitt, start_y)

    aufgaben = abschnitt["aufgaben"]  # list of [a, b]
    loesungen = abschnitt.get("loesungen", [])
    row_y = start_y - 1.5*cm - y_off
    row_h = 1.5*cm

    for idx, aufg in enumerate(aufgaben):
        a, b = aufg
        y = row_y - idx * row_h
        summe = loesungen[idx] if idx < len(loesungen) else None

        c.setFont("Helvetica-Bold", 18)

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
                                    w=1.3*cm, h=1.1*cm)
        else:
            draw_answer_box(c, x + 3.5*cm, y - 0.25*cm, w=1.3*cm, h=1.1*cm)

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
                                    w=1.3*cm, h=1.1*cm)
        else:
            draw_answer_box(c, x2 + 3.5*cm, y - 0.25*cm, w=1.3*cm, h=1.1*cm)

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
    row_h = 1.5*cm
    halb_count = (len(aufgaben) + 1) // 2
    row_y = start_y - 1.5*cm - y_off

    for idx, aufg in enumerate(aufgaben):
        zahl, typ = aufg
        loes = loesungen[idx] if idx < len(loesungen) else None
        col = idx % cols
        row = idx // cols
        x = 1.8*cm + col * col_w
        y = row_y - row * row_h

        c.setFont("Helvetica-Bold", 18)

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
                                        w=1.3*cm, h=1.1*cm)
            else:
                draw_answer_box(c, x + 3.5*cm, y - 0.25*cm, w=1.3*cm, h=1.1*cm)
        else:  # halb
            c.setFillColor(FARBEN["dunkel"])
            c.drawString(x, y, str(zahl))
            text_w = c.stringWidth(str(zahl), "Helvetica-Bold", 18)
            c.setFillColor(FARBEN[farb_key])
            c.setFont("Helvetica-Bold", 18)
            c.drawString(x + text_w + 0.3*cm, y, "÷ 2 =")
            if loes is not None:
                _draw_filled_answer_box(c, x + text_w + 2.5*cm, y - 0.25*cm,
                                        loes, w=1.3*cm, h=1.1*cm)
            else:
                draw_answer_box(c, x + text_w + 2.5*cm, y - 0.25*cm,
                                w=1.3*cm, h=1.1*cm)

    total_rows = (len(aufgaben) + cols - 1) // cols
    return row_y - total_rows * row_h - 0.3*cm


# ── Zahlenstrahl ──────────────────────────────────────────

def draw_zahlenstrahl(c, abschnitt, farb_key, start_y):
    """Number line with some numbers missing."""
    draw_section_label(c, abschnitt["titel"], farb_key, start_y)
    y_off = _draw_beschreibung(c, abschnitt, start_y)

    strahlen = abschnitt["strahlen"]  # list of {von, bis, werte}
    row_h = 2.5*cm
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
                # Blank answer box
                c.setFillColor(FARBEN["antwort"])
                c.setStrokeColor(FARBEN[farb_key])
                c.setLineWidth(1)
                c.roundRect(tx - 0.5*cm, y - 1.0*cm, 1.0*cm, 0.7*cm,
                            radius=3, fill=1, stroke=1)
                # Show solution if available
                if i < len(strahl_loes) and strahl_loes[i] is not None:
                    c.setFillColor(FARBEN["gruen"])
                    c.setFont("Helvetica-Bold", 12)
                    c.drawCentredString(tx, y - 0.75*cm, str(strahl_loes[i]))
            else:
                c.setFillColor(FARBEN["dunkel"])
                c.setFont("Helvetica-Bold", 12)
                c.drawCentredString(tx, y - 0.8*cm, str(val))

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
    row_h = rows_frame * cell + 2.0*cm
    row_y = start_y - 1.5*cm - y_off

    for idx, anzahl in enumerate(aufgaben):
        col = idx % grid_cols
        row = idx // grid_cols
        x0 = 1.5*cm + col * grid_col_w + 0.3*cm
        y0 = row_y - row * row_h

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

                # Fill if within count
                if dot_idx < anzahl:
                    c.setFillColor(FARBEN[farb_key])
                    c.circle(cx, cy, dot_r, fill=1, stroke=0)

        # Answer box below
        frame_bottom = y0 - rows_frame * cell
        loesungen = abschnitt.get("loesungen", [])
        if idx < len(loesungen):
            _draw_filled_answer_box(c, x0 + 0.5*cm, frame_bottom - 1.0*cm,
                                    loesungen[idx], w=1.3*cm, h=0.9*cm)
        else:
            draw_answer_box(c, x0 + 0.5*cm, frame_bottom - 1.0*cm,
                            w=1.3*cm, h=0.9*cm)
        c.setFillColor(FARBEN["grau"])
        c.setFont("Helvetica", 9)
        c.drawString(x0 + 2.0*cm, frame_bottom - 0.6*cm, "Punkte")

    total_rows = (len(aufgaben) + grid_cols - 1) // grid_cols
    return row_y - total_rows * row_h - 0.3*cm


# ── Zahlen ordnen ─────────────────────────────────────────

def draw_zahlen_ordnen(c, abschnitt, farb_key, start_y):
    """Sort numbers from smallest to largest (or reverse)."""
    draw_section_label(c, abschnitt["titel"], farb_key, start_y)
    y_off = _draw_beschreibung(c, abschnitt, start_y)

    aufgaben = abschnitt["aufgaben"]  # list of lists of numbers
    loesungen = abschnitt.get("loesungen", [])
    row_h = 2.2*cm
    row_y = start_y - 1.5*cm - y_off
    box_w = 1.3*cm
    box_h = 1.1*cm

    for idx, zahlen in enumerate(aufgaben):
        y = row_y - idx * row_h
        count = len(zahlen)
        loes = loesungen[idx] if idx < len(loesungen) else None

        # Show the unsorted numbers in colored circles
        c.setFillColor(FARBEN[farb_key])
        c.setFont("Helvetica-Bold", 12)
        c.drawString(1.8*cm, y + 0.05*cm, f"{idx + 1}.")

        x = 2.8*cm
        for z in zahlen:
            c.setFillColor(FARBEN[farb_key])
            c.circle(x + 0.5*cm, y + 0.1*cm, 0.45*cm, fill=1, stroke=0)
            c.setFillColor(white)
            c.setFont("Helvetica-Bold", 14)
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
            c.roundRect(bx, y - 0.4*cm, box_w, box_h, radius=4, fill=1, stroke=1)
            # Show solution in green if available
            if loes is not None and i < len(loes):
                c.setFillColor(FARBEN["gruen"])
                c.setFont("Helvetica-Bold", 16)
                c.drawCentredString(bx + box_w/2, y - 0.05*cm, str(loes[i]))
            if i < count - 1:
                c.setFillColor(FARBEN["dunkel"])
                c.setFont("Helvetica-Bold", 16)
                c.drawCentredString(bx + box_w + 0.25*cm, y - 0.05*cm, "<")
            bx += box_w + 0.5*cm

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
        c.setFont("Helvetica-Bold", 12)
        c.drawString(1.8*cm, y, f"{idx + 1}.")

        # Problem text with proper word wrap using stringWidth
        c.setFillColor(FARBEN["dunkel"])
        c.setFont("Helvetica", 11)
        max_w = W - 4.3*cm  # 2.8cm left indent + 1.5cm right margin
        words = text.split()
        lines = []
        line = ""
        for w in words:
            test = (line + " " + w).strip()
            if c.stringWidth(test, "Helvetica", 11) > max_w:
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
            c.setFont("Helvetica-Oblique", 9)
            c.drawString(2.8*cm, y - len(lines) * 0.5*cm - 0.15*cm, hinweis)

        # Rechnung + Antwort
        bottom = y - len(lines) * 0.5*cm - 0.8*cm
        c.setFillColor(FARBEN["grau"])
        c.setFont("Helvetica", 9)
        c.drawString(2.8*cm, bottom + 0.3*cm, "Rechnung:")
        draw_answer_box(c, 5.0*cm, bottom, w=4*cm, h=0.9*cm)
        c.setFillColor(FARBEN["grau"])
        c.setFont("Helvetica", 9)
        c.drawString(10*cm, bottom + 0.3*cm, "Antwort:")
        draw_answer_box(c, 12*cm, bottom, w=6*cm, h=0.9*cm)

        # Advance y dynamically based on actual content height
        y = bottom - 0.5*cm

    return y
