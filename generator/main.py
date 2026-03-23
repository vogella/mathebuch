"""
main.py – Liest alle YAML-Dateien aus aufgaben/ und erzeugt das PDF.

Aufruf:
    python3 main.py
    python3 main.py --output mein_buch.pdf
"""
import sys
import os
import glob
import argparse
import math
import yaml
import random

# Generator-Ordner zum Suchpfad hinzufügen
sys.path.insert(0, os.path.dirname(__file__))

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.colors import white
from layout import (draw_page_bg, draw_header, draw_emoji,
                    draw_page_number, FARBEN, RAND_FARBEN,
                    FONT, FONT_BOLD, FONT_ITALIC)
from illustrationen import (draw_euli, draw_euli_mit_sprechblase,
                            draw_separator_illustration)
from aufgabentypen import (draw_erklaerung, draw_lückenaufgaben,
                           draw_zahlenhaus, draw_rechenraupe,
                           draw_magisches_dreieck, draw_magische_dreiecke,
                           draw_magisches_quadrat, draw_würfelzählen,
                           draw_rechenmauer, draw_vergleiche,
                           draw_nachbarzahlen, draw_zahlzerlegung,
                           draw_kettenaufgaben, draw_tauschaufgaben,
                           draw_verdoppeln_halbieren,
                           draw_zahlenstrahl, draw_punktefeld,
                           draw_zahlen_ordnen, draw_vervielfachen,
                           draw_rechenweg_labyrinth, draw_zahlenraetsel,
                           draw_einkaufen, draw_kalender_raetsel,
                           draw_textaufgaben, draw_wuerfel_zuordnen,
                           draw_schatzsuche, draw_labyrinth_flucht,
                           draw_zahlenkreis, draw_dungeon_flucht, draw_dungeon_abenteuer,
                           draw_zehneruebergang, draw_gerade_ungerade,
                           draw_rechenquadrat_2x2, draw_muster_fortsetzen,
                           draw_motivation,
                           draw_umkehraufgaben, draw_zahlen_schreiben,
                           draw_formen_zaehlen, draw_symmetrie,
                           draw_bonbon_fabrik,
                           draw_einkaufen_euro_cent,
                           draw_karten_rechnen, draw_karten_ziel_summe,
                           draw_karten_geheim,
                           draw_muenzen_zaehlen, draw_muenzen_legen)
W, H = A4

# Mapping Typ-String → Zeichenfunktion
TYPEN = {
    "erklaerung":        draw_erklaerung,
    "lückenaufgaben":    draw_lückenaufgaben,
    "zahlenhaus":       draw_zahlenhaus,
    "rechenraupe":      draw_rechenraupe,
    "magisches_dreieck":  draw_magisches_dreieck,
    "magische_dreiecke":  draw_magische_dreiecke,
    "magisches_quadrat":  draw_magisches_quadrat,
    "würfelzählen":       draw_würfelzählen,
    "rechenmauer":        draw_rechenmauer,
    "vergleiche":         draw_vergleiche,
    "nachbarzahlen":      draw_nachbarzahlen,
    "zahlzerlegung":      draw_zahlzerlegung,
    "kettenaufgaben":     draw_kettenaufgaben,
    "tauschaufgaben":     draw_tauschaufgaben,
    "verdoppeln_halbieren": draw_verdoppeln_halbieren,
    "zahlenstrahl":       draw_zahlenstrahl,
    "punktefeld":         draw_punktefeld,
    "zahlen_ordnen":      draw_zahlen_ordnen,
    "vervielfachen":      draw_vervielfachen,
    "rechenweg_labyrinth": draw_rechenweg_labyrinth,
    "zahlenraetsel":      draw_zahlenraetsel,
    "einkaufen":          draw_einkaufen,
    "kalender_raetsel":   draw_kalender_raetsel,
    "textaufgaben":       draw_textaufgaben,
    "wuerfel_zuordnen":   draw_wuerfel_zuordnen,
    "schatzsuche":        draw_schatzsuche,
    "labyrinth_flucht":   draw_labyrinth_flucht,
    "zahlenkreis":        draw_zahlenkreis,
    "dungeon_flucht":     draw_dungeon_flucht,
    "dungeon_abenteuer":  draw_dungeon_abenteuer,
    "zehneruebergang":    draw_zehneruebergang,
    "gerade_ungerade":    draw_gerade_ungerade,
    "rechenquadrat_2x2":  draw_rechenquadrat_2x2,
    "muster_fortsetzen":  draw_muster_fortsetzen,
    "motivation":         draw_motivation,
    "umkehraufgaben":     draw_umkehraufgaben,
    "zahlen_schreiben":   draw_zahlen_schreiben,
    "formen_zaehlen":     draw_formen_zaehlen,
    "symmetrie":          draw_symmetrie,
    "bonbon_fabrik":      draw_bonbon_fabrik,
    "einkaufen_euro_cent": draw_einkaufen_euro_cent,
    "karten_rechnen":     draw_karten_rechnen,
    "karten_ziel_summe":  draw_karten_ziel_summe,
    "karten_geheim":      draw_karten_geheim,
    "muenzen_zaehlen":    draw_muenzen_zaehlen,
    "muenzen_legen":      draw_muenzen_legen,
}

TRENNLINIE_Y = H - 15.5   # Y-Position der Trennlinie zwischen Abschnitten

# ── Trennseiten-Konfiguration ────────────────────────────────────────
TRENNSEITEN_INFO = {
    5:  {"titel": "Rechnen bis 5",  "farbe": "gruen",  "emoji": "✋",
         "untertitel": "Los geht's mit den ersten Zahlen!"},
    10: {"titel": "Rechnen bis 10", "farbe": "blau",   "emoji": "⭐",
         "untertitel": "Jetzt wird es spannend!"},
    20: {"titel": "Rechnen bis 20", "farbe": "orange",  "emoji": "🚀",
         "untertitel": "Du bist schon ein Rechen-Profi!"},
}

# ── Inhaltsverzeichnis-Layout ────────────────────────────────────────
TOC_LINE_HEIGHT = 0.55 * cm
TOC_START_Y = H - 5.0 * cm
TOC_MIN_Y = 2.5 * cm
TOC_SECTION_GAP = 0.15 * cm
TOC_NEW_PAGE_START_Y = H - 3.5 * cm
TOC_SECTION_FONT_SIZE = 11
TOC_ENTRY_FONT_SIZE = 9

# TOC Grouping definition
CHAPTER_GROUPS = [
    ("Willkommen & Grundlagen", ["k00", "k01"]),
    ("Zahlen bis 5",            ["k09", "k10", "k11"]),
    ("Plus und Minus bis 5",    ["k12", "k13", "k16"]),
    ("Rätsel & Spiele bis 5",   ["k14", "k15", "k18", "k19"]),
    ("Zahlen bis 10",           ["k19c", "k22", "k23", "k26", "k28", "k37", "k38"]),
    ("Rechnen bis 10",          ["k20", "k24", "k25", "k30", "k31", "k32"]),
    ("Entdeckungen bis 10",     ["k27", "k33", "k34", "k35", "k36", "k39"]),
    ("Geometrie & Muster",      ["k15b", "k29", "k29b", "k44", "k52d", "k57b"]),
    ("Zahlen bis 20",           ["k40", "k41", "k42", "k43", "k50"]),
    ("Rechnen bis 20",          ["k45", "k46", "k51", "k52", "k54", "k63"]),
    ("Sachrechnen & Alltag",    ["k56", "k59", "k60", "k65"]),
    ("Knobel-Aufgaben",         ["k53", "k55", "k57", "k58"]),
    ("Dungeon-Abenteuer",       ["k18_dungeon", "k36_dungeon", "k61", "k62"])
]


def _get_group_for_chapter(filename):
    fname = os.path.basename(filename)
    for group_name, prefixes in CHAPTER_GROUPS:
        for p in prefixes:
            if fname.startswith(p):
                return group_name
    return None


def _get_chapter_section(kap_data):
    """Returns section key for a chapter: 'erklaerung', 5, 10, or 20."""
    kap = kap_data["kapitel"]
    if kap.get("erklaerungsseite", False):
        return "erklaerung"
    return _toc_section_for_zahlenraum(kap.get("zahlenraum", 20))


def _berechne_trennseiten(alle_kapitel):
    """Returns dict of chapter indices -> section where a separator page should be inserted BEFORE."""
    positionen = {}
    prev_section = None
    for i, (_, data) in enumerate(alle_kapitel):
        section = _get_chapter_section(data)
        if prev_section is not None and section != prev_section and section in TRENNSEITEN_INFO:
            positionen[i] = section
        prev_section = section
    return positionen


def render_trennseite(c, section):
    """Rendert eine Trennseite zwischen Hauptabschnitten."""
    info = TRENNSEITEN_INFO[section]
    draw_page_bg(c)

    farbe = FARBEN[info["farbe"]]
    center_y = H / 2 + 2 * cm

    # Großer farbiger Kreis
    c.setFillColor(farbe)
    c.circle(W / 2, center_y, 3 * cm, fill=1, stroke=0)

    # Emoji im Kreis
    draw_emoji(c, info["emoji"], W / 2, center_y, 2.5 * cm)

    # Titel
    titel_y = center_y - 5 * cm
    c.setFillColor(farbe)
    c.roundRect(2 * cm, titel_y - 0.5 * cm, W - 4 * cm, 2.2 * cm,
                radius=15, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont(FONT_BOLD, 30)
    c.drawCentredString(W / 2, titel_y + 0.2 * cm, info["titel"])

    # Untertitel
    c.setFillColor(FARBEN["dunkel"])
    c.setFont(FONT, 16)
    c.drawCentredString(W / 2, titel_y - 2 * cm, info["untertitel"])

    # Thematische Illustration für den Zahlenraum
    illust_y = titel_y - 4.5 * cm
    draw_separator_illustration(c, section, W / 2, illust_y, size=1.0)

    # Euli-Maskottchen unten auf der Trennseite
    draw_euli(c, W / 2, illust_y - 4.5 * cm, size=0.6)


def _draw_titelseite_previews(c, top_y):
    """Draws small decorative previews of exercise types on the title page."""
    # Layout: 5 previews in a row, evenly spaced
    # Each preview has a small illustration and a label below
    margin = 1.5 * cm
    usable_w = W - 2 * margin
    n_items = 5
    item_w = usable_w / n_items
    label_font_size = 7
    preview_size = 1.5 * cm  # approximate size for each preview

    items = [
        ("Magisches\nDreieck", "blau", "_dreieck"),
        ("Magisches\nQuadrat", "gruen", "_quadrat"),
        ("Zahlen\nim Kreis", "orange", "_kreis"),
        ("Karten\naddieren", "pink", "_karten"),
        ("Schatz-\nsuche", "purple", "_schatz"),
    ]

    for idx, (label, farb_key, preview_type) in enumerate(items):
        cx = margin + idx * item_w + item_w / 2
        cy = top_y - 2.0 * cm

        # Draw subtle background circle
        c.setFillColor(FARBEN["bg"])
        c.setStrokeColor(FARBEN[farb_key])
        c.setLineWidth(1.5)
        c.circle(cx, cy, preview_size + 0.3 * cm, fill=1, stroke=1)

        if preview_type == "_dreieck":
            _draw_preview_dreieck(c, cx, cy, preview_size, farb_key)
        elif preview_type == "_quadrat":
            _draw_preview_quadrat(c, cx, cy, preview_size, farb_key)
        elif preview_type == "_kreis":
            _draw_preview_kreis(c, cx, cy, preview_size, farb_key)
        elif preview_type == "_karten":
            _draw_preview_karten(c, cx, cy, preview_size, farb_key)
        elif preview_type == "_schatz":
            _draw_preview_schatz(c, cx, cy, preview_size, farb_key)

        # Label below
        c.setFillColor(FARBEN["dunkel"])
        c.setFont(FONT_BOLD, label_font_size)
        lines = label.split("\n")
        for li, line in enumerate(lines):
            c.drawCentredString(cx, cy - preview_size - 0.7 * cm - li * 0.35 * cm, line)


def _draw_preview_dreieck(c, cx, cy, size, farb_key):
    """Draws a small magic triangle preview."""
    r = size * 0.7
    pts = [
        (cx, cy + r * 0.9),
        (cx - r * 0.85, cy - r * 0.5),
        (cx + r * 0.85, cy - r * 0.5),
    ]
    # Triangle lines
    c.setStrokeColor(FARBEN["orange"])
    c.setLineWidth(1.5)
    c.line(*pts[0], *pts[1])
    c.line(*pts[1], *pts[2])
    c.line(*pts[0], *pts[2])
    # Corner circles with numbers
    node_r = 0.28 * cm
    vals = [3, 5, 7]
    colors = [FARBEN["yellow"], FARBEN["blau"], FARBEN["gruen"]]
    for i, (px, py) in enumerate(pts):
        c.setFillColor(colors[i])
        c.circle(px, py, node_r, fill=1, stroke=0)
        c.setFillColor(white)
        c.setFont(FONT_BOLD, 8)
        c.drawCentredString(px, py - 0.1 * cm, str(vals[i]))
    # Midpoint circles (smaller, answer blanks)
    mids = [
        ((pts[0][0] + pts[1][0]) / 2, (pts[0][1] + pts[1][1]) / 2),
        ((pts[1][0] + pts[2][0]) / 2, (pts[1][1] + pts[2][1]) / 2),
        ((pts[0][0] + pts[2][0]) / 2, (pts[0][1] + pts[2][1]) / 2),
    ]
    for mx, my in mids:
        c.setFillColor(FARBEN["antwort"])
        c.setStrokeColor(FARBEN[farb_key])
        c.setLineWidth(0.8)
        c.circle(mx, my, 0.2 * cm, fill=1, stroke=1)
        c.setFillColor(FARBEN["grau"])
        c.setFont(FONT_BOLD, 6)
        c.drawCentredString(mx, my - 0.08 * cm, "?")


def _draw_preview_quadrat(c, cx, cy, size, farb_key):
    """Draws a small 3x3 magic square preview."""
    cell = size * 0.42
    grid_w = 3 * cell
    gx = cx - grid_w / 2
    gy = cy - grid_w / 2
    vals = [2, 7, 6, 9, 5, 1, 4, 3, 8]
    colors = [FARBEN["yellow"], FARBEN["blau"], FARBEN["gruen"],
              FARBEN["pink"], FARBEN["purple"], FARBEN["orange"],
              FARBEN["blau"], FARBEN["gruen"], FARBEN["yellow"]]
    for row in range(3):
        for col in range(3):
            x = gx + col * cell
            y = gy + (2 - row) * cell
            idx = row * 3 + col
            c.setFillColor(colors[idx])
            c.setStrokeColor(white)
            c.setLineWidth(0.5)
            c.roundRect(x, y, cell, cell, radius=2, fill=1, stroke=1)
            c.setFillColor(white)
            c.setFont(FONT_BOLD, 7)
            c.drawCentredString(x + cell / 2, y + cell / 2 - 0.1 * cm, str(vals[idx]))


def _draw_preview_kreis(c, cx, cy, size, farb_key):
    """Draws a small number circle preview."""
    radius = size * 0.6
    n_nodes = 6
    node_r = 0.22 * cm
    vals = [2, None, 5, None, 8, None]
    colors_list = [FARBEN["blau"], FARBEN["gruen"], FARBEN["orange"],
                   FARBEN["pink"], FARBEN["purple"], FARBEN["yellow"]]
    # Draw connecting lines
    c.setStrokeColor(FARBEN["hellgrau"])
    c.setLineWidth(1)
    for i in range(n_nodes):
        a1 = math.radians(90 - i * (360 / n_nodes))
        a2 = math.radians(90 - ((i + 1) % n_nodes) * (360 / n_nodes))
        x1 = cx + radius * math.cos(a1)
        y1 = cy + radius * math.sin(a1)
        x2 = cx + radius * math.cos(a2)
        y2 = cy + radius * math.sin(a2)
        c.line(x1, y1, x2, y2)
    # Draw nodes
    for i in range(n_nodes):
        angle = math.radians(90 - i * (360 / n_nodes))
        nx = cx + radius * math.cos(angle)
        ny = cy + radius * math.sin(angle)
        val = vals[i]
        if val is None:
            c.setFillColor(FARBEN["antwort"])
            c.setStrokeColor(FARBEN[farb_key])
            c.setLineWidth(0.8)
            c.circle(nx, ny, node_r, fill=1, stroke=1)
            c.setFillColor(FARBEN["grau"])
            c.setFont(FONT_BOLD, 6)
            c.drawCentredString(nx, ny - 0.08 * cm, "?")
        else:
            c.setFillColor(colors_list[i])
            c.circle(nx, ny, node_r, fill=1, stroke=0)
            c.setFillColor(white)
            c.setFont(FONT_BOLD, 7)
            c.drawCentredString(nx, ny - 0.08 * cm, str(val))


def _draw_preview_karten(c, cx, cy, size, farb_key):
    """Draws small playing cards preview."""
    card_w = size * 0.45
    card_h = size * 0.65
    gap = 0.15 * cm
    total_w = 2 * card_w + gap + 0.6 * cm  # 2 cards + operator + equals
    start_x = cx - total_w / 2
    card_y = cy - card_h / 2

    vals = [3, 5]
    card_colors = [FARBEN["pink"], FARBEN["blau"]]
    for i, (val, col) in enumerate(zip(vals, card_colors)):
        x = start_x + i * (card_w + gap + 0.3 * cm)
        c.setFillColor(white)
        c.setStrokeColor(col)
        c.setLineWidth(1.2)
        c.roundRect(x, card_y, card_w, card_h, radius=3, fill=1, stroke=1)
        c.setFillColor(col)
        c.setFont(FONT_BOLD, 11)
        c.drawCentredString(x + card_w / 2, card_y + card_h / 2 - 0.15 * cm, str(val))
        # Small corner number
        c.setFont(FONT_BOLD, 5)
        c.drawString(x + 0.08 * cm, card_y + card_h - 0.25 * cm, str(val))

    # Plus sign between cards
    c.setFillColor(FARBEN[farb_key])
    c.setFont(FONT_BOLD, 10)
    plus_x = start_x + card_w + gap / 2 + 0.15 * cm
    c.drawCentredString(plus_x, cy - 0.1 * cm, "+")

    # Equals and answer
    eq_x = start_x + 2 * card_w + gap + 0.45 * cm
    c.drawCentredString(eq_x, cy - 0.1 * cm, "=")
    c.setFillColor(FARBEN["antwort"])
    c.setStrokeColor(FARBEN[farb_key])
    c.setLineWidth(0.8)
    c.roundRect(eq_x + 0.15 * cm, card_y + 0.15 * cm, card_w * 0.7, card_h * 0.7,
                radius=3, fill=1, stroke=1)
    c.setFillColor(FARBEN["grau"])
    c.setFont(FONT_BOLD, 6)
    c.drawCentredString(eq_x + 0.15 * cm + card_w * 0.35, cy - 0.08 * cm, "?")


def _draw_preview_schatz(c, cx, cy, size, farb_key):
    """Draws a small treasure hunt path preview."""
    # Draw a zigzag path with nodes
    node_r = 0.2 * cm
    n_nodes = 5
    path_w = size * 1.2
    start_x = cx - path_w / 2
    step = path_w / (n_nodes - 1)

    positions = []
    for i in range(n_nodes):
        nx = start_x + i * step
        ny = cy + (0.25 * cm if i % 2 == 0 else -0.25 * cm)
        positions.append((nx, ny))

    # Draw path lines
    c.setStrokeColor(FARBEN["hellgrau"])
    c.setLineWidth(1.5)
    for i in range(len(positions) - 1):
        c.line(*positions[i], *positions[i + 1])

    # Draw operation labels between nodes
    ops = ["+2", "+3", "-1", "+4"]
    for i in range(len(positions) - 1):
        mx = (positions[i][0] + positions[i + 1][0]) / 2
        my = (positions[i][1] + positions[i + 1][1]) / 2 + 0.3 * cm
        c.setFillColor(FARBEN[farb_key])
        c.setFont(FONT_BOLD, 5)
        c.drawCentredString(mx, my, ops[i])

    # Draw nodes
    path_colors = [FARBEN["blau"], FARBEN["gruen"], FARBEN["orange"],
                   FARBEN["pink"], FARBEN["purple"]]
    node_vals = ["1", "?", "?", "?", ""]
    for i, (px, py) in enumerate(positions):
        if i == n_nodes - 1:
            # Treasure node (star/gold)
            c.setFillColor(FARBEN["yellow"])
            c.setStrokeColor(FARBEN["orange"])
            c.setLineWidth(1)
            # Draw a small star shape
            _draw_mini_star(c, px, py, node_r * 1.3)
        elif node_vals[i] == "?":
            c.setFillColor(FARBEN["antwort"])
            c.setStrokeColor(path_colors[i])
            c.setLineWidth(0.8)
            c.circle(px, py, node_r, fill=1, stroke=1)
            c.setFillColor(FARBEN["grau"])
            c.setFont(FONT_BOLD, 6)
            c.drawCentredString(px, py - 0.08 * cm, "?")
        else:
            c.setFillColor(path_colors[i])
            c.circle(px, py, node_r, fill=1, stroke=0)
            c.setFillColor(white)
            c.setFont(FONT_BOLD, 7)
            c.drawCentredString(px, py - 0.08 * cm, node_vals[i])


def _draw_mini_star(c, cx, cy, size):
    """Draws a small star (treasure icon) at (cx, cy)."""
    from reportlab.lib.colors import HexColor
    points = 5
    outer_r = size
    inner_r = size * 0.45
    path = c.beginPath()
    for i in range(points * 2):
        angle = math.radians(90 + i * (360 / (points * 2)))
        r = outer_r if i % 2 == 0 else inner_r
        x = cx + r * math.cos(angle)
        y = cy + r * math.sin(angle)
        if i == 0:
            path.moveTo(x, y)
        else:
            path.lineTo(x, y)
    path.close()
    c.drawPath(path, fill=1, stroke=1)


def render_titelseite(c):
    """Titelseite mit Buchtitel, Namensfeld, persönlichen Feldern und Malblock."""
    draw_page_bg(c)

    # Großer bunter Titel
    y_top = H - 4 * cm
    c.setFillColor(FARBEN["blau"])
    c.roundRect(2 * cm, y_top, W - 4 * cm, 3 * cm, radius=15, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont(FONT_BOLD, 30)
    c.drawCentredString(W / 2, y_top + 1.8 * cm, "Mein Mathebuch")
    c.setFont(FONT, 16)
    c.drawCentredString(W / 2, y_top + 0.6 * cm, "Klasse 1 – Rechnen macht Spaß!")

    # Bunte Deko-Kreise
    deko_colors = RAND_FARBEN
    for i, col in enumerate(deko_colors):
        cx = 2.5 * cm + i * 2.8 * cm
        c.setFillColor(col)
        c.circle(cx, y_top - 1.2 * cm, 0.4 * cm, fill=1, stroke=0)

    # Euli-Maskottchen mit Sprechblase
    draw_euli_mit_sprechblase(c, 3.5 * cm, y_top - 3.0 * cm,
                              "Rechnen macht Spass!", size=0.7)

    # Namensfeld
    name_y = y_top - 5.5 * cm
    c.setFillColor(FARBEN["dunkel"])
    c.setFont(FONT_BOLD, 14)
    c.drawString(2.5 * cm, name_y + 0.2 * cm, "Dieses Buch gehört:")
    c.setStrokeColor(FARBEN["blau"])
    c.setFillColor(white)
    c.setLineWidth(2)
    c.roundRect(2.5 * cm, name_y - 1.5 * cm, W - 5 * cm, 1.3 * cm,
                radius=8, fill=1, stroke=1)

    # Persönliche Eingabefelder
    felder_y = name_y - 3.2 * cm
    felder = ["Mein Alter:", "Meine Klasse:", "Mein Lieblingsfach:"]
    feld_farben = [FARBEN["gruen"], FARBEN["orange"], FARBEN["pink"]]
    field_h = 1.0 * cm
    field_gap = 0.4 * cm
    
    # Consistent starting position for all boxes
    max_label_w = 0
    for label in felder:
        max_label_w = max(max_label_w, c.stringWidth(label, FONT_BOLD, 12))
    box_start_x = 2.5 * cm + max_label_w + 0.6 * cm

    for i, (label, farbe) in enumerate(zip(felder, feld_farben)):
        fy = felder_y - i * (field_h + field_gap)
        c.setFillColor(FARBEN["dunkel"])
        c.setFont(FONT_BOLD, 12)
        c.drawString(2.5 * cm, fy + 0.2 * cm, label)
        
        box_w = W - 2.5 * cm - box_start_x
        c.setStrokeColor(farbe)
        c.setFillColor(white)
        c.setLineWidth(2)
        c.roundRect(box_start_x, fy - 0.2 * cm, box_w, field_h,
                    radius=8, fill=1, stroke=1)

    # Aufgaben-Vorschau: Kleine dekorative Previews von Aufgabentypen
    preview_y = felder_y - len(felder) * (field_h + field_gap) - 1.8 * cm
    c.setFillColor(FARBEN["dunkel"])
    c.setFont(FONT_BOLD, 14)
    c.drawCentredString(W / 2, preview_y + 0.2 * cm, "Was dich erwartet:")

    _draw_titelseite_previews(c, preview_y - 1.0 * cm)


def _draw_toc_section_header(c, y, text, line_h):
    """Draws a colored section header in the TOC."""
    c.setFillColor(FARBEN["blau"])
    c.roundRect(1.8 * cm, y - 0.15 * cm, W - 3.6 * cm, line_h,
                radius=6, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont(FONT_BOLD, TOC_SECTION_FONT_SIZE)
    c.drawString(2.3 * cm, y, text)
    return y - line_h - 0.15 * cm


def _toc_section_for_zahlenraum(zr):
    """Returns section key for grouping: 5, 10, or 20."""
    if zr <= 5:
        return 5
    elif zr <= 10:
        return 10
    else:
        return 20


def _toc_new_page(c):
    """Start a new TOC continuation page with background and subtitle."""
    c.showPage()
    draw_page_bg(c)
    c.setFillColor(FARBEN["grau"])
    c.setFont(FONT_BOLD, 12)
    c.drawCentredString(W / 2, H - 2.0 * cm, "Inhaltsverzeichnis (Fortsetzung)")
    return TOC_NEW_PAGE_START_Y


def _draw_toc_dots(c, y, text, font_name, font_size):
    """Draws dotted lines for a TOC entry."""
    titel_w = c.stringWidth(text, font_name, font_size)
    dot_start = 3.5 * cm + titel_w + 0.3 * cm
    dot_end = W - 3.5 * cm
    if dot_end > dot_start:
        c.setFillColor(FARBEN["hellgrau"])
        c.setFont(FONT, 8)
        dot_w = c.stringWidth(" .", FONT, 8)
        if dot_w > 0:
            num_dots = int((dot_end - dot_start) / dot_w)
            dots = " ." * num_dots
        else:
            dots = ""
        c.drawString(dot_start, y, dots)


def render_inhaltsverzeichnis(c, alle_kapitel, seiten_nummern):
    """Inhaltsverzeichnis mit automatischem Seitenumbruch und Gruppierung.
    Gibt die Anzahl der verwendeten Seiten zurück."""
    draw_page_bg(c)
    toc_pages = 1

    # Header
    c.setFillColor(FARBEN["orange"])
    c.roundRect(1.5 * cm, H - 3.5 * cm, W - 3 * cm, 2.2 * cm,
                radius=12, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont(FONT_BOLD, 20)
    c.drawCentredString(W / 2, H - 2.5 * cm, "Inhaltsverzeichnis")

    y = H - 5.0 * cm
    line_h = 0.55 * cm
    min_y = 2.5 * cm

    current_section = None
    seen_groups = set()

    # Pass 1: Collect grouped entries
    grouped_entries = []
    for idx, (dateiname, kap_data) in enumerate(alle_kapitel):
        seite_nr = seiten_nummern[idx]
        kap = kap_data["kapitel"]
        ist_erkl = kap.get("erklaerungsseite", False)
        
        if ist_erkl:
            group_name = "So funktioniert's!"
            group_emoji = "📖"
        else:
            group_name = _get_group_for_chapter(dateiname)
            group_emoji = kap.get("emoji", "⭐")
            if not group_name:
                zr = kap.get("zahlenraum", 20)
                group_name = f"Rechnen bis {zr}"
        
        if group_name not in seen_groups:
            seen_groups.add(group_name)
            grouped_entries.append({
                "titel": group_name,
                "seite": seite_nr,
                "emoji": group_emoji,
                "farbe": kap.get("farbe", "blau"),
                "zahlenraum": kap.get("zahlenraum", 20),
                "ist_erkl": ist_erkl
            })

    # Pass 2: Render
    for entry in grouped_entries:
        if y < min_y:
            y = _toc_new_page(c)
            toc_pages += 1

        # Section header based on zahlenraum
        if not entry["ist_erkl"]:
            section = _toc_section_for_zahlenraum(entry["zahlenraum"])
            if section != current_section:
                current_section = section
                section_titles = {5: "Zahlenraum bis 5", 10: "Zahlenraum bis 10", 20: "Zahlenraum bis 20"}
                y -= TOC_SECTION_GAP
                if y < min_y:
                    y = _toc_new_page(c)
                    toc_pages += 1
                y = _draw_toc_section_header(c, y, section_titles[section], line_h)

        if y < min_y:
            y = _toc_new_page(c)
            toc_pages += 1

        # Emoji
        draw_emoji(c, entry["emoji"], 2.6 * cm, y + 0.15 * cm, 0.5 * cm)

        # Titel
        c.setFillColor(FARBEN["dunkel"])
        c.setFont(FONT, TOC_ENTRY_FONT_SIZE)
        c.drawString(3.5 * cm, y, entry["titel"])

        _draw_toc_dots(c, y, entry["titel"], FONT, TOC_ENTRY_FONT_SIZE)

        # Seitennummer
        c.setFillColor(FARBEN[entry["farbe"]])
        c.setFont(FONT_BOLD, TOC_ENTRY_FONT_SIZE)
        c.drawRightString(W - 2 * cm, y, str(entry["seite"]))

        y -= line_h

    return toc_pages


def render_geschafft_seite(c, seite_nr):
    """Rendert eine 'Geschafft!'-Abschlussseite vor den Lösungen."""
    draw_page_bg(c)

    # Großer bunter Titel
    c.setFillColor(FARBEN["pink"])
    c.roundRect(2 * cm, H - 6 * cm, W - 4 * cm, 3.5 * cm, radius=15, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont(FONT_BOLD, 40)
    c.drawCentredString(W / 2, H - 4.2 * cm, "GESCHAFFT!")
    c.setFont(FONT_BOLD, 20)
    c.drawCentredString(W / 2, H - 5.3 * cm, "Du bist ein Mathe-Profi!")

    # Sterne / Konfetti-Deko
    confetti_count = 30
    _rnd = random.Random(42) # Deterministic for layout stability
    for _ in range(confetti_count):
        c.setFillColor(random.choice(RAND_FARBEN))
        sz = _rnd.uniform(0.1, 0.4) * cm
        cx = _rnd.uniform(1 * cm, W - 1 * cm)
        cy = _rnd.uniform(1 * cm, H - 7 * cm)
        c.circle(cx, cy, sz, fill=1, stroke=0)

    # Urkunde-Bereich
    u_y = H - 10 * cm
    c.setFillColor(FARBEN["dunkel"])
    c.setFont(FONT_BOLD, 18)
    c.drawCentredString(W / 2, u_y, "Herzlichen Glückwunsch!")
    
    c.setFont(FONT, 14)
    msg = "Du hast alle Aufgaben in diesem Buch erfolgreich gelöst."
    c.drawCentredString(W / 2, u_y - 1.2 * cm, msg)

    # Namensfeld für die Urkunde
    box_w = 12 * cm
    box_h = 1.5 * cm
    bx = (W - box_w) / 2
    by = u_y - 4 * cm
    c.setStrokeColor(FARBEN["orange"])
    c.setLineWidth(2)
    c.roundRect(bx, by, box_w, box_h, radius=10, fill=0, stroke=1)
    
    c.setFillColor(FARBEN["grau"])
    c.setFont(FONT, 10)
    c.drawString(bx + 0.3 * cm, by + box_h + 0.2 * cm, "Name des Mathe-Profis:")
    c.setFillColor(FARBEN["grau"])
    c.setFont(FONT, 10)
    c.drawString(bx + 0.3 * cm, by - 0.5 * cm, "Fertig geworden am:")
    c.setStrokeColor(FARBEN["orange"])
    c.setLineWidth(2)
    c.roundRect(bx, by - box_h - 0.8 * cm, box_w, box_h, radius=10, fill=0, stroke=1)

    # Stempel "Matheprofi der ersten Klasse"
    stamp_cx = W / 2
    stamp_cy = by - box_h - 0.8 * cm - 2.5 * cm
    stamp_r = 2.2 * cm
    # Äußerer Kreis
    c.setStrokeColor(FARBEN["pink"])
    c.setLineWidth(3)
    c.circle(stamp_cx, stamp_cy, stamp_r, fill=0, stroke=1)
    # Innerer Kreis
    c.setLineWidth(1.5)
    c.circle(stamp_cx, stamp_cy, stamp_r - 0.25 * cm, fill=0, stroke=1)
    # Stern oben
    draw_emoji(c, "⭐", stamp_cx, stamp_cy + 0.9 * cm, 0.7 * cm)
    # Text im Stempel
    c.setFillColor(FARBEN["pink"])
    c.setFont(FONT_BOLD, 11)
    c.drawCentredString(stamp_cx, stamp_cy + 0.1 * cm, "Matheprofi")
    c.setFont(FONT_BOLD, 10)
    c.drawCentredString(stamp_cx, stamp_cy - 0.5 * cm, "der ersten Klasse")
    # Kleine Sterne links und rechts
    draw_emoji(c, "⭐", stamp_cx - 1.4 * cm, stamp_cy - 0.2 * cm, 0.4 * cm)
    draw_emoji(c, "⭐", stamp_cx + 1.4 * cm, stamp_cy - 0.2 * cm, 0.4 * cm)

    draw_page_number(c, seite_nr, show_stars=False)


def draw_urkunde_seite(c):
    """Rendert eine Urkunde/Zertifikat-Seite als letztes Blatt des Buches."""
    from illustrationen import draw_euli, draw_mini_pokal

    draw_page_bg(c)

    # ── Festlicher Header ──────────────────────────────────────────
    c.setFillColor(FARBEN["yellow"])
    c.roundRect(1.5 * cm, H - 4.5 * cm, W - 3 * cm, 3.2 * cm,
                radius=15, fill=1, stroke=0)
    c.setFillColor(FARBEN["dunkel"])
    c.setFont(FONT_BOLD, 36)
    c.drawCentredString(W / 2, H - 2.8 * cm, "Geschafft!")
    draw_emoji(c, "\U0001f389", 3.0 * cm, H - 2.8 * cm, 1.2 * cm)
    draw_emoji(c, "\U0001f389", W - 3.0 * cm, H - 2.8 * cm, 1.2 * cm)
    c.setFont(FONT_BOLD, 14)
    c.setFillColor(FARBEN["dunkel"])
    c.drawCentredString(W / 2, H - 4.0 * cm, "Urkunde")

    # ── Zertifikat-Rahmen ──────────────────────────────────────────
    frame_x = 1.8 * cm
    frame_y = 3.0 * cm
    frame_w = W - 3.6 * cm
    frame_h = H - 8.5 * cm

    # Doppelter Rahmen
    c.setStrokeColor(FARBEN["orange"])
    c.setLineWidth(3)
    c.roundRect(frame_x, frame_y, frame_w, frame_h, radius=12, fill=0, stroke=1)
    c.setStrokeColor(FARBEN["yellow"])
    c.setLineWidth(1.5)
    c.roundRect(frame_x + 0.2 * cm, frame_y + 0.2 * cm,
                frame_w - 0.4 * cm, frame_h - 0.4 * cm,
                radius=10, fill=0, stroke=1)

    # ── Zertifikats-Text ───────────────────────────────────────────
    text_y = frame_y + frame_h - 1.5 * cm

    c.setFillColor(FARBEN["dunkel"])
    c.setFont(FONT_BOLD, 16)
    c.drawCentredString(W / 2, text_y, "Ich,")

    # Namenszeile mit Linie
    text_y -= 1.4 * cm
    line_w = 10 * cm
    line_x = (W - line_w) / 2
    c.setStrokeColor(FARBEN["dunkel"])
    c.setLineWidth(1)
    c.line(line_x, text_y, line_x + line_w, text_y)
    c.setFillColor(FARBEN["grau"])
    c.setFont(FONT_ITALIC, 9)
    c.drawCentredString(W / 2, text_y - 0.4 * cm, "(Name eintragen)")

    text_y -= 1.2 * cm
    c.setFillColor(FARBEN["dunkel"])
    c.setFont(FONT_BOLD, 16)
    c.drawCentredString(W / 2, text_y, "habe das Mathebuch geschafft!")

    # ── "Das kannst du jetzt alles!" ───────────────────────────────
    text_y -= 1.8 * cm
    c.setFillColor(FARBEN["pink"])
    c.setFont(FONT_BOLD, 14)
    c.drawCentredString(W / 2, text_y, "Das kannst du jetzt alles!")

    skills = [
        ("Zahlen bis 20 lesen und schreiben", "gruen"),
        ("Plus und Minus rechnen", "blau"),
        ("Formen erkennen und z\u00e4hlen", "purple"),
        ("Zahlenr\u00e4tsel l\u00f6sen", "orange"),
        ("Rechengeschichten verstehen", "pink"),
    ]

    text_y -= 0.7 * cm
    for skill_text, farb_key in skills:
        draw_emoji(c, "\u2705", 4.0 * cm, text_y + 0.1 * cm, 0.45 * cm)
        c.setFillColor(FARBEN[farb_key])
        c.setFont(FONT, 12)
        c.drawString(4.8 * cm, text_y, skill_text)
        text_y -= 0.65 * cm

    # ── Euli mit Pokal ─────────────────────────────────────────────
    euli_cx = W / 2
    euli_cy = text_y - 1.5 * cm
    draw_euli(c, euli_cx, euli_cy, size=0.9)
    # Pokal neben Euli
    draw_mini_pokal(c, euli_cx + 2.0 * cm, euli_cy + 0.8 * cm, size=2.5)
    draw_mini_pokal(c, euli_cx - 2.0 * cm, euli_cy + 0.8 * cm, size=2.5)

    # ── Datumszeile ────────────────────────────────────────────────
    datum_y = frame_y + 1.2 * cm
    c.setFillColor(FARBEN["dunkel"])
    c.setFont(FONT, 12)
    c.drawString(3.5 * cm, datum_y, "Datum:")
    date_line_x = 5.8 * cm
    date_line_w = 8 * cm
    c.setStrokeColor(FARBEN["dunkel"])
    c.setLineWidth(1)
    c.line(date_line_x, datum_y, date_line_x + date_line_w, datum_y)


def _render_fortschritt_header(c):
    """Zeichnet den Header der Fortschrittsseite."""
    draw_page_bg(c)
    c.setFillColor(FARBEN["purple"])
    c.roundRect(1.5 * cm, H - 3.5 * cm, W - 3 * cm, 2.2 * cm,
                radius=12, fill=1, stroke=0)
    # Kompass-Emoji links im Header
    c.setFillColor(white)
    c.circle(2.8 * cm, H - 2.4 * cm, 0.7 * cm, fill=1, stroke=0)
    draw_emoji(c, "\U0001f5fa", 2.8 * cm, H - 2.4 * cm, 0.9 * cm)
    c.setFillColor(white)
    c.setFont(FONT_BOLD, 20)
    c.drawCentredString(W / 2 + 0.5 * cm, H - 2.2 * cm, "Meine Mathe-Reise")
    c.setFont(FONT, 12)
    c.drawCentredString(W / 2 + 0.5 * cm, H - 2.8 * cm,
                        "Dein Weg durch das Mathebuch")

    c.setFillColor(FARBEN["dunkel"])
    c.setFont(FONT, 10)
    c.drawCentredString(W / 2, H - 4.2 * cm,
                        "Kreuze jedes Kapitel an, wenn du es geschafft hast!")


def _draw_path_segment(c, x1, y1, x2, y2, color):
    """Zeichnet ein gestricheltes Pfadsegment zwischen zwei Stationen."""
    c.saveState()
    c.setStrokeColor(color)
    c.setLineWidth(2)
    c.setDash(4, 4)
    c.line(x1, y1, x2, y2)
    c.setDash()
    c.restoreState()


def _draw_station(c, cx, cy, emoji, titel, farbe, nr):
    """Zeichnet eine Station auf der Reise-Karte.

    cx, cy: Mittelpunkt der Station
    emoji: Kapitel-Emoji
    titel: Kurzform des Kapiteltitels
    farbe: Farbschlüssel
    nr: Stationsnummer
    """
    color = FARBEN.get(farbe, FARBEN["blau"])

    # Farbiger Kreis als Station
    c.setFillColor(color)
    c.circle(cx, cy, 0.45 * cm, fill=1, stroke=0)

    # Emoji in der Station
    draw_emoji(c, emoji, cx, cy, 0.55 * cm)

    # Checkbox (leeres Kästchen) rechts neben der Station
    box_size = 0.35 * cm
    box_x = cx + 0.6 * cm
    box_y = cy - box_size / 2
    c.setFillColor(white)
    c.setStrokeColor(color)
    c.setLineWidth(1.5)
    c.rect(box_x, box_y, box_size, box_size, fill=1, stroke=1)

    # Stationsnummer (klein, über der Station)
    c.setFillColor(FARBEN["grau"])
    c.setFont(FONT, 7)
    c.drawCentredString(cx, cy + 0.65 * cm, str(nr))

    # Titel unter der Station (gekürzt)
    c.setFillColor(FARBEN["dunkel"])
    c.setFont(FONT, 7)
    max_w = 3.0 * cm
    t = titel
    if c.stringWidth(t, FONT, 7) > max_w:
        while c.stringWidth(t + "…", FONT, 7) > max_w and len(t) > 3:
            t = t[:-1]
        t = t + "…"
    c.drawCentredString(cx, cy - 0.7 * cm, t)


def draw_fortschritts_seite(c, alle_kapitel):
    """Rendert eine visuelle Fortschritts-Übersicht als Reise-Karte.

    Zeigt die CHAPTER_GROUPS als Stationen auf einem gewundenen Pfad.
    Jede Gruppe hat ein Emoji, einen Kurztitel und ein Ankreuz-Kästchen.
    Gibt die Anzahl der verwendeten Seiten zurück.
    """
    _render_fortschritt_header(c)
    pages = 1

    # Build lookup: chapter key prefix -> kapitel data (single pass)
    kapitel_lookup = {}
    for dateiname, data in alle_kapitel:
        kap = data["kapitel"]
        kapitel_lookup[dateiname] = kap

    # Sammle Gruppen-Einträge basierend auf CHAPTER_GROUPS
    gruppen_eintraege = []
    for group_name, prefixes in CHAPTER_GROUPS:
        # Finde das erste passende Kapitel für Emoji und Farbe
        emoji = "\u2b50"
        farbe = "blau"
        for p in prefixes:
            for fname, kap in kapitel_lookup.items():
                if fname.startswith(p):
                    emoji = kap.get("emoji", "\u2b50")
                    farbe = kap.get("farbe", "blau")
                    break
            else:
                continue
            break

        gruppen_eintraege.append({
            "titel": group_name,
            "emoji": emoji,
            "farbe": farbe,
            "anzahl": len(prefixes),
        })

    # Layout: Schlängelnder Pfad von oben nach unten
    y_start = H - 5.2 * cm
    min_y = 2.8 * cm
    row_h = 1.8 * cm  # Vertikaler Abstand zwischen Stationen

    # Wir legen die Stationen in einem Zickzack-Muster an
    # Ungerade Reihen: links, gerade Reihen: rechts
    x_left = 4.5 * cm
    x_right = W - 4.5 * cm
    x_center = W / 2

    y = y_start
    prev_x = None
    prev_y = None
    station_nr = 0

    # Farben für die Pfadsegmente (wechselnd)
    pfad_farben = [FARBEN["yellow"], FARBEN["orange"], FARBEN["blau"],
                   FARBEN["gruen"], FARBEN["pink"], FARBEN["purple"]]

    for idx, gruppe in enumerate(gruppen_eintraege):
        # Prüfe ob Seitenumbruch nötig
        if y < min_y:
            c.showPage()
            _render_fortschritt_header(c)
            y = y_start
            prev_x = None
            prev_y = None
            pages += 1

        station_nr += 1

        # Zickzack: abwechselnd links und rechts
        if idx % 2 == 0:
            cx = x_left
        else:
            cx = x_right

        # Pfadsegment zur vorherigen Station zeichnen
        if prev_x is not None and prev_y is not None:
            pfad_farbe = pfad_farben[idx % len(pfad_farben)]
            _draw_path_segment(c, prev_x, prev_y, cx, y, pfad_farbe)

        # Station zeichnen
        _draw_station(c, cx, y, gruppe["emoji"], gruppe["titel"],
                      gruppe["farbe"], station_nr)

        # Anzahl der Kapitel in der Gruppe (kleiner Hinweis)
        c.setFillColor(FARBEN["grau"])
        c.setFont(FONT_ITALIC, 6)
        anz_text = f"({gruppe['anzahl']} Kapitel)"
        c.drawCentredString(cx, y - 0.95 * cm, anz_text)

        prev_x = cx
        prev_y = y
        y -= row_h

    # Ziel-Markierung am Ende: Pokal
    if prev_x is not None and prev_y is not None:
        ziel_y = y
        if ziel_y < min_y:
            # Zeichne das Ziel auf die letzte gültige Position
            ziel_y = prev_y - 1.4 * cm
        ziel_x = x_center
        _draw_path_segment(c, prev_x, prev_y, ziel_x, ziel_y,
                           FARBEN["yellow"])
        # Pokal-Emoji als Ziel
        c.setFillColor(FARBEN["yellow"])
        c.circle(ziel_x, ziel_y, 0.55 * cm, fill=1, stroke=0)
        draw_emoji(c, "\U0001f3c6", ziel_x, ziel_y, 0.7 * cm)
        c.setFillColor(FARBEN["dunkel"])
        c.setFont(FONT_BOLD, 9)
        c.drawCentredString(ziel_x, ziel_y - 0.8 * cm, "Geschafft!")

    # Euli unten rechts als Ermutigung
    euli_x = W - 3.5 * cm
    euli_y = 2.8 * cm
    draw_euli(c, euli_x, euli_y, size=0.4)

    return pages


def lade_kapitel(pfad):
    with open(pfad, encoding="utf-8") as f:
        return yaml.safe_load(f)


def zeichne_trennlinie(c, y):
    c.setStrokeColor(FARBEN["hellgrau"])
    c.setLineWidth(1)
    c.line(1.5*cm, y, W - 1.5*cm, y)


MIN_Y = 3.0 * cm   # Untere Seitengrenze (Platz für Sterne + Seitenzahl)


def render_kapitel(c, kapitel_data, seitennummer, audit=False, erklaerung_seite=None):
    """Rendert ein Kapitel – bei Überlauf automatisch auf neue Seiten.
    Gibt die Anzahl genutzter Seiten zurück.
    Bei audit=True wird zusätzlich eine Liste von Überlauf-Verletzungen zurückgegeben."""
    kap  = kapitel_data["kapitel"]
    farbe = kap.get("farbe", "blau")
    ist_erklaerung = kap.get("erklaerungsseite", False)
    titel = kap["titel"]
    untertitel = kap["untertitel"]
    emoji = kap["emoji"]

    pages = 0
    ueberlauf_liste = []
    max_inhalt_hoehe = H - 5.5*cm - MIN_Y  # Verfügbare Höhe pro Seite

    def neue_seite():
        nonlocal y, pages, seitennr_aktuell
        if pages > 0:
            draw_page_number(c, seitennr_aktuell, show_stars=not ist_erklaerung)
            c.showPage()
        draw_page_bg(c)
        draw_header(c, titel, untertitel, emoji, farbe,
                    erklaerung_seite=erklaerung_seite if not ist_erklaerung else None)
        y = H - 5.5*cm
        pages += 1
        seitennr_aktuell = seitennummer + pages - 1

    y = 0
    seitennr_aktuell = seitennummer
    neue_seite()

    abschnitte = kapitel_data.get("abschnitte", [])

    for i, abschnitt in enumerate(abschnitte):
        typ = abschnitt.get("typ")
        fn  = TYPEN.get(typ)
        if fn is None:
            print(f"  Warnung: Unbekannter Typ '{typ}', wird übersprungen.", file=sys.stderr)
            continue

        # Prüfe ob noch genug Platz ist oder neue Seite erzwungen wird
        erzwinge_neue_seite = abschnitt.get("neue_seite", False)
        if i > 0 and (erzwinge_neue_seite or y < MIN_Y + 5.0*cm):
            neue_seite()

        # Trennlinie zwischen Abschnitten (nicht vor dem ersten auf der Seite)
        if i > 0 and y < H - 6*cm:
            y -= 0.3*cm  # gap after previous content
            zeichne_trennlinie(c, y)
            y -= 0.5*cm  # gap before next section

        import aufgabentypen as _at
        _at._erklaerung_modus = ist_erklaerung
        y_vor = y
        y = fn(c, abschnitt, farbe, y)

        if audit:
            abschnitt_titel = abschnitt.get("titel", f"Abschnitt {i+1}")
            abschnitt_hoehe = y_vor - y

            # Prüfe Seitenüberlauf: y unterhalb MIN_Y
            if y < MIN_Y:
                ueberlauf_liste.append({
                    "kapitel": titel,
                    "abschnitt": abschnitt_titel,
                    "index": i,
                    "seite": seitennr_aktuell,
                    "y_position": y,
                    "typ": "ueberlauf",
                })

            # Prüfe atomaren Überlauf: Abschnitt passt auf keine Seite
            if abschnitt_hoehe > max_inhalt_hoehe:
                ueberlauf_liste.append({
                    "kapitel": titel,
                    "abschnitt": abschnitt_titel,
                    "index": i,
                    "seite": seitennr_aktuell,
                    "abschnitt_hoehe": abschnitt_hoehe,
                    "max_hoehe": max_inhalt_hoehe,
                    "typ": "atomar",
                })

        # Falls der Abschnitt unter die Seitengrenze gezeichnet hat,
        # merken wir uns das – der nächste Abschnitt kommt auf eine neue Seite
        if y < MIN_Y:
            pass  # Nächster Durchlauf prüft und bricht um

    draw_page_number(c, seitennr_aktuell, show_stars=not ist_erklaerung)

    if audit:
        return pages, ueberlauf_liste
    return pages


def main():
    parser = argparse.ArgumentParser(description="Mathebuch-Generator")
    parser.add_argument("--output", default="../output/mathebuch_klasse1.pdf",
                        help="Ausgabepfad für die PDF-Datei")
    parser.add_argument("--aufgaben", default="../aufgaben",
                        help="Ordner mit den YAML-Aufgabendateien")
    parser.add_argument("--audit-layout", action="store_true",
                        help="Prüft alle Kapitel auf Layout-Überläufe und gibt einen Bericht aus")
    args = parser.parse_args()

    # Skript-Verzeichnis als Basis
    base = os.path.dirname(os.path.abspath(__file__))
    aufgaben_dir = os.path.join(base, args.aufgaben)
    output_path  = os.path.join(base, args.output)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Alle YAML-Dateien alphabetisch sortiert einlesen
    yaml_files = sorted(glob.glob(os.path.join(aufgaben_dir, "*.yaml")))
    if not yaml_files:
        print(f"Keine YAML-Dateien in {aufgaben_dir} gefunden!")
        sys.exit(1)

    print(f"Gefundene Kapitel: {len(yaml_files)}")
    for f in yaml_files:
        print(f"  • {os.path.basename(f)}")

    # Alle Kapitel vorladen
    alle_kapitel = []
    for yaml_file in yaml_files:
        data = lade_kapitel(yaml_file)
        alle_kapitel.append((os.path.basename(yaml_file), data))

    # Trennseiten-Positionen bestimmen
    trennseiten_pos = _berechne_trennseiten(alle_kapitel)

    # ── Pass 1: Probe-Rendering um Seitenzahlen pro Kapitel zu ermitteln ──
    import io
    probe_buf = io.BytesIO()
    probe_c = canvas.Canvas(probe_buf, pagesize=A4)
    seiten_pro_kapitel = []
    alle_ueberlaufe = []
    for i, (dateiname, data) in enumerate(alle_kapitel):
        if args.audit_layout:
            n_pages, ueberlaufe = render_kapitel(probe_c, data, 1, audit=True)
            alle_ueberlaufe.extend(ueberlaufe)
        else:
            n_pages = render_kapitel(probe_c, data, 1)
        probe_c.showPage()
        seiten_pro_kapitel.append(n_pages)

    # Audit-Bericht ausgeben und ggf. beenden
    if args.audit_layout:
        print("=== Layout-Audit ===", file=sys.stderr)
        if alle_ueberlaufe:
            for v in alle_ueberlaufe:
                if v["typ"] == "atomar":
                    print(
                        f'FEHLER: Kapitel "{v["kapitel"]}" → Abschnitt "{v["abschnitt"]}" '
                        f'(Seite ~{v["seite"]})',
                        file=sys.stderr)
                    print(
                        f'  Atomarer Überlauf: Abschnittshöhe {v["abschnitt_hoehe"]/cm:.1f} cm '
                        f'> verfügbare {v["max_hoehe"]/cm:.1f} cm',
                        file=sys.stderr)
                else:
                    print(
                        f'FEHLER: Kapitel "{v["kapitel"]}" → Abschnitt "{v["abschnitt"]}" '
                        f'(Seite ~{v["seite"]})',
                        file=sys.stderr)
                    print(
                        f'  Überlauf: y = {v["y_position"]/cm:.1f} cm '
                        f'(unterhalb MIN_Y = {MIN_Y/cm:.1f} cm)',
                        file=sys.stderr)
            print(f"\n{len(alle_ueberlaufe)} Überlauf(e) gefunden. Exit-Code 1.", file=sys.stderr)
            sys.exit(1)
        else:
            print("Keine Überläufe gefunden. Alles in Ordnung!", file=sys.stderr)
            sys.exit(0)

    # Probe-TOC und Fortschritt um Seitenanzahlen zu ermitteln
    # Vorläufige Seitennummern mit geschätztem Offset berechnen
    est_offset = 4  # Titelseite (1) + Inhaltsverzeichnis (~2) + Fortschritt (~1)
    est_seiten_nummern = []
    s = est_offset
    for i, n in enumerate(seiten_pro_kapitel):
        if i in trennseiten_pos:
            s += 1
        est_seiten_nummern.append(s)
        s += n
    toc_pages = render_inhaltsverzeichnis(probe_c, alle_kapitel, est_seiten_nummern)
    probe_c.showPage()
    fortschritt_pages = draw_fortschritts_seite(probe_c, alle_kapitel)
    del probe_c, probe_buf

    # Seiten-Offset: Titelseite (1) + Inhaltsverzeichnis (toc_pages) + Fortschritt (fortschritt_pages)
    # Kapitel starten auf der Seite danach.
    seiten_offset = 1 + toc_pages + fortschritt_pages

    # Seitennummern berechnen (mit Trennseiten)
    seiten_nummern = []
    aktuelle_seite = seiten_offset
    for i, n in enumerate(seiten_pro_kapitel):
        if i in trennseiten_pos:
            aktuelle_seite += 1  # Trennseite einfügen
        seiten_nummern.append(aktuelle_seite)
        aktuelle_seite += n

    # ── Erklärungsseiten-Mapping: Aufgabentyp → Seitennummer ──
    # Durchsuche alle Erklärungsseiten und merke uns welche Typen dort erklärt werden
    typ_zu_erklaerung = {}
    for i, (dateiname, data) in enumerate(alle_kapitel):
        kap = data["kapitel"]
        if not kap.get("erklaerungsseite", False):
            continue
        seite = seiten_nummern[i]
        for abschnitt in data.get("abschnitte", []):
            typ = abschnitt.get("typ", "")
            if typ and typ != "erklaerung":
                typ_zu_erklaerung.setdefault(typ, seite)

    def _erklaerung_seite_fuer_kapitel(data):
        """Findet die passende Erklärungsseite für ein Kapitel."""
        kap = data["kapitel"]
        if kap.get("erklaerungsseite", False):
            return None
        for abschnitt in data.get("abschnitte", []):
            typ = abschnitt.get("typ", "")
            if typ in typ_zu_erklaerung:
                return typ_zu_erklaerung[typ]
        return None

    # ── Pass 2: Finales PDF mit korrekten Seitennummern ──
    c = canvas.Canvas(output_path, pagesize=A4)

    # Titelseite
    print("  Rendere Titelseite ...")
    render_titelseite(c)
    c.showPage()

    # Inhaltsverzeichnis
    print("  Rendere Inhaltsverzeichnis ...")
    render_inhaltsverzeichnis(c, alle_kapitel, seiten_nummern)
    c.showPage()

    # Fortschritt-Seite
    print("  Rendere Fortschritt-Seite ...")
    draw_fortschritts_seite(c, alle_kapitel)
    c.showPage()

    # Kapitel (mit Trennseiten zwischen Hauptabschnitten)
    for i, (dateiname, data) in enumerate(alle_kapitel):
        if i in trennseiten_pos:
            section = trennseiten_pos[i]
            print(f"  Rendere Trennseite: {TRENNSEITEN_INFO[section]['titel']} ...")
            render_trennseite(c, section)
            c.showPage()
        print(f"  Rendere Seite {seiten_nummern[i]}: {dateiname} ...")
        erkl_seite = _erklaerung_seite_fuer_kapitel(data)
        render_kapitel(c, data, seiten_nummern[i], erklaerung_seite=erkl_seite)
        c.showPage()

    # Lösungsseiten am Ende
    from loesungen import render_loesungsseiten
    loes_start = aktuelle_seite
    print("  Rendere Lösungsseiten ...")
    n_loes = render_loesungsseiten(c, alle_kapitel, loes_start)
    if n_loes > 0:
        c.showPage()
    print(f"  → {n_loes} Lösungsseite(n)")

    # Urkunde-Seite ganz am Ende
    print("  Rendere Urkunde-Seite ...")
    draw_urkunde_seite(c)
    c.showPage()

    c.save()
    print(f"\n✓ PDF gespeichert: {output_path}")


if __name__ == "__main__":
    main()
