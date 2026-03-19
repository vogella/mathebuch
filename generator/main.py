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
import yaml

# Generator-Ordner zum Suchpfad hinzufügen
sys.path.insert(0, os.path.dirname(__file__))

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.colors import white
from layout import (draw_page_bg, draw_header,
                    draw_page_number, FARBEN, RAND_FARBEN)
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
                           draw_zahlenkreis, draw_dungeon_flucht,
                           draw_zehneruebergang)

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
    "zehneruebergang":    draw_zehneruebergang,
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
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 48)
    c.drawCentredString(W / 2, center_y - 0.5 * cm, info["emoji"])

    # Titel
    titel_y = center_y - 5 * cm
    c.setFillColor(farbe)
    c.roundRect(2 * cm, titel_y - 0.5 * cm, W - 4 * cm, 2.2 * cm,
                radius=15, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 30)
    c.drawCentredString(W / 2, titel_y + 0.2 * cm, info["titel"])

    # Untertitel
    c.setFillColor(FARBEN["dunkel"])
    c.setFont("Helvetica", 16)
    c.drawCentredString(W / 2, titel_y - 2 * cm, info["untertitel"])

    # Deko-Punkte
    deko = RAND_FARBEN
    total_w = (len(deko) - 1) * 2.5 * cm
    start_x = W / 2 - total_w / 2
    for i, col in enumerate(deko):
        c.setFillColor(col)
        c.circle(start_x + i * 2.5 * cm, titel_y - 4 * cm, 0.5 * cm, fill=1, stroke=0)


def render_titelseite(c):
    """Titelseite mit Buchtitel, Namensfeld, persönlichen Feldern und Malblock."""
    draw_page_bg(c)

    # Großer bunter Titel
    y_top = H - 4 * cm
    c.setFillColor(FARBEN["blau"])
    c.roundRect(2 * cm, y_top, W - 4 * cm, 3 * cm, radius=15, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 30)
    c.drawCentredString(W / 2, y_top + 1.8 * cm, "Mein Mathebuch")
    c.setFont("Helvetica", 16)
    c.drawCentredString(W / 2, y_top + 0.6 * cm, "Klasse 1 – Rechnen macht Spaß!")

    # Bunte Deko-Kreise
    deko_colors = RAND_FARBEN
    for i, col in enumerate(deko_colors):
        cx = 2.5 * cm + i * 2.8 * cm
        c.setFillColor(col)
        c.circle(cx, y_top - 1.2 * cm, 0.4 * cm, fill=1, stroke=0)

    # Namensfeld
    name_y = y_top - 3.5 * cm
    c.setFillColor(FARBEN["dunkel"])
    c.setFont("Helvetica-Bold", 14)
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
    for i, (label, farbe) in enumerate(zip(felder, feld_farben)):
        fy = felder_y - i * (field_h + field_gap)
        c.setFillColor(FARBEN["dunkel"])
        c.setFont("Helvetica-Bold", 12)
        c.drawString(2.5 * cm, fy + 0.2 * cm, label)
        label_w = c.stringWidth(label, "Helvetica-Bold", 12)
        box_x = 2.5 * cm + label_w + 0.4 * cm
        box_w = W - 5 * cm - label_w - 0.4 * cm
        c.setStrokeColor(farbe)
        c.setFillColor(white)
        c.setLineWidth(2)
        c.roundRect(box_x, fy - 0.2 * cm, box_w, field_h,
                    radius=8, fill=1, stroke=1)

    # Malblock: "Male dich selbst!" (reduzierte Größe ~8cm)
    mal_y = felder_y - len(felder) * (field_h + field_gap) - 1.0 * cm
    c.setFillColor(FARBEN["dunkel"])
    c.setFont("Helvetica-Bold", 14)
    c.drawString(2.5 * cm, mal_y + 0.2 * cm, "Male dich selbst:")
    # Rahmen zum Malen (8×8cm statt vorher 10cm hoch)
    box_h = 6 * cm
    box_w = 8 * cm
    box_x = (W - box_w) / 2
    c.setStrokeColor(FARBEN["hellgrau"])
    c.setFillColor(white)
    c.setLineWidth(1.5)
    c.setDash(4, 4)
    c.roundRect(box_x, mal_y - box_h, box_w, box_h,
                radius=10, fill=1, stroke=1)
    c.setDash()  # Reset dash

    # Dekorative Mathe-Symbole um den Malblock
    math_symbols = ["+", "−", "×", "=", "1", "2", "3", "4", "5"]
    symbol_colors = RAND_FARBEN
    c.setFont("Helvetica-Bold", 18)
    # Symbole links vom Malblock
    for i, sym in enumerate(math_symbols[:4]):
        sy = mal_y - 0.5 * cm - i * 1.5 * cm
        c.setFillColor(symbol_colors[i % len(symbol_colors)])
        c.drawCentredString(box_x - 1.0 * cm, sy, sym)
    # Symbole rechts vom Malblock
    for i, sym in enumerate(math_symbols[4:]):
        sy = mal_y - 0.5 * cm - i * 1.2 * cm
        c.setFillColor(symbol_colors[(i + 4) % len(symbol_colors)])
        c.drawCentredString(box_x + box_w + 1.0 * cm, sy, sym)


def _draw_toc_section_header(c, y, text, line_h):
    """Draws a colored section header in the TOC."""
    c.setFillColor(FARBEN["blau"])
    c.roundRect(1.8 * cm, y - 0.15 * cm, W - 3.6 * cm, line_h,
                radius=6, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 12)
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
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(W / 2, H - 2.0 * cm, "Inhaltsverzeichnis (Fortsetzung)")
    return H - 3.5 * cm


def _draw_toc_dots(c, y, text, font_name, font_size):
    """Draws dotted lines for a TOC entry."""
    titel_w = c.stringWidth(text, font_name, font_size)
    dot_start = 3.5 * cm + titel_w + 0.3 * cm
    dot_end = W - 3.5 * cm
    if dot_end > dot_start:
        c.setFillColor(FARBEN["hellgrau"])
        c.setFont("Helvetica", 8)
        dot_w = c.stringWidth(" .", "Helvetica", 8)
        if dot_w > 0:
            num_dots = int((dot_end - dot_start) / dot_w)
            dots = " ." * num_dots
        else:
            dots = ""
        c.drawString(dot_start, y, dots)


def render_inhaltsverzeichnis(c, alle_kapitel, seiten_nummern):
    """Inhaltsverzeichnis mit automatischem Seitenumbruch.
    Gibt die Anzahl der verwendeten Seiten zurück."""
    draw_page_bg(c)
    toc_pages = 1

    # Header
    c.setFillColor(FARBEN["orange"])
    c.roundRect(1.5 * cm, H - 3.5 * cm, W - 3 * cm, 2.2 * cm,
                radius=12, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(W / 2, H - 2.5 * cm, "Inhaltsverzeichnis")

    y = H - 5.0 * cm
    line_h = 0.65 * cm
    min_y = 2.5 * cm

    erkl_header_shown = False
    erkl_seen = set()  # Avoid duplicate entries in TOC
    current_section = None
    skip_types = {"erklaerung"}  # Skip "Willkommen!" etc.

    for idx, (dateiname, kap_data) in enumerate(alle_kapitel):
        seite_nr = seiten_nummern[idx]
        kap = kap_data["kapitel"]
        titel = kap["titel"]
        emoji = kap.get("emoji", "")
        farb_key = kap.get("farbe", "blau")
        ist_erklaerung = kap.get("erklaerungsseite", False)
        zahlenraum = kap.get("zahlenraum", 20)

        # Erklärungsseiten: Überschrift + einzelne Aufgabentypen auflisten
        if ist_erklaerung:
            if not erkl_header_shown:
                y -= 0.15 * cm
                if y < min_y:
                    y = _toc_new_page(c)
                    toc_pages += 1
                y = _draw_toc_section_header(c, y, "So funktioniert's!", line_h)
                erkl_header_shown = True

            # Aufgabentypen dieser Erklärungsseite auflisten
            abschnitte = kap_data.get("abschnitte", [])
            for abschnitt in abschnitte:
                typ = abschnitt.get("typ", "")
                if typ in skip_types:
                    continue
                ab_titel = abschnitt.get("titel", typ)
                # Remove "– Aufgabe", "– Lösung" suffixes for cleaner TOC
                for suffix in [" – Aufgabe", " – Lösung", " – Aufgabe & Lösung"]:
                    ab_titel = ab_titel.replace(suffix, "")
                # Skip duplicates (e.g. Aufgabe + Lösung for same type)
                if ab_titel in erkl_seen:
                    continue
                erkl_seen.add(ab_titel)
                if y < min_y:
                    y = _toc_new_page(c)
                    toc_pages += 1

                c.setFillColor(FARBEN["grau"])
                c.setFont("Helvetica", 9)
                c.drawString(2.5 * cm, y, "📖")
                c.setFillColor(FARBEN["dunkel"])
                c.drawString(3.5 * cm, y, ab_titel)

                _draw_toc_dots(c, y, ab_titel, "Helvetica", 9)

                c.setFillColor(FARBEN["grau"])
                c.setFont("Helvetica", 9)
                c.drawRightString(W - 2 * cm, y, str(seite_nr))
                y -= line_h * 0.85
            continue

        # Section header based on zahlenraum
        section = _toc_section_for_zahlenraum(zahlenraum)
        if section != current_section:
            current_section = section
            section_titles = {5: "Rechnen bis 5", 10: "Rechnen bis 10", 20: "Rechnen bis 20"}
            y -= 0.15 * cm  # extra gap before section header
            if y < min_y:
                y = _toc_new_page(c)
                toc_pages += 1
            y = _draw_toc_section_header(c, y, section_titles[section], line_h)

        if y < min_y:
            y = _toc_new_page(c)
            toc_pages += 1

        # Emoji
        c.setFillColor(FARBEN[farb_key])
        c.setFont("Helvetica-Bold", 11)
        c.drawString(2.3 * cm, y, emoji)

        # Titel
        c.setFillColor(FARBEN["dunkel"])
        c.setFont("Helvetica", 10)
        c.drawString(3.5 * cm, y, titel)

        _draw_toc_dots(c, y, titel, "Helvetica", 10)

        # Seitennummer
        c.setFillColor(FARBEN[farb_key])
        c.setFont("Helvetica-Bold", 10)
        c.drawRightString(W - 2 * cm, y, str(seite_nr))

        y -= line_h

    return toc_pages




def lade_kapitel(pfad):
    with open(pfad, encoding="utf-8") as f:
        return yaml.safe_load(f)


def zeichne_trennlinie(c, y):
    c.setStrokeColor(FARBEN["hellgrau"])
    c.setLineWidth(1)
    c.line(1.5*cm, y, W - 1.5*cm, y)


MIN_Y = 2.5 * cm   # Untere Seitengrenze


def render_kapitel(c, kapitel_data, seitennummer):
    """Rendert ein Kapitel – bei Überlauf automatisch auf neue Seiten.
    Gibt die Anzahl genutzter Seiten zurück."""
    kap  = kapitel_data["kapitel"]
    farbe = kap.get("farbe", "blau")
    ist_erklaerung = kap.get("erklaerungsseite", False)
    titel = kap["titel"]
    untertitel = kap["untertitel"]
    emoji = kap["emoji"]

    pages = 0

    def neue_seite():
        nonlocal y, pages, seitennr_aktuell
        if pages > 0:
            draw_page_number(c, seitennr_aktuell, show_stars=not ist_erklaerung)
            c.showPage()
        draw_page_bg(c)
        draw_header(c, titel, untertitel, emoji, farbe)
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

        # Prüfe ob noch genug Platz ist (mindestens 4cm für einen Abschnitt)
        if y < MIN_Y + 4*cm and i > 0:
            neue_seite()

        # Trennlinie zwischen Abschnitten (nicht vor dem ersten auf der Seite)
        if i > 0 and y < H - 6*cm:
            zeichne_trennlinie(c, y + 0.5*cm)
            y -= 1.2*cm

        y = fn(c, abschnitt, farbe, y)

        # Falls der Abschnitt unter die Seitengrenze gezeichnet hat,
        # merken wir uns das – der nächste Abschnitt kommt auf eine neue Seite
        if y < MIN_Y:
            pass  # Nächster Durchlauf prüft und bricht um

    draw_page_number(c, seitennr_aktuell, show_stars=not ist_erklaerung)
    return pages


def main():
    parser = argparse.ArgumentParser(description="Mathebuch-Generator")
    parser.add_argument("--output", default="../output/mathebuch_klasse1.pdf",
                        help="Ausgabepfad für die PDF-Datei")
    parser.add_argument("--aufgaben", default="../aufgaben",
                        help="Ordner mit den YAML-Aufgabendateien")
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
    for i, (dateiname, data) in enumerate(alle_kapitel):
        n_pages = render_kapitel(probe_c, data, 1)  # Seitennummer egal
        probe_c.showPage()
        seiten_pro_kapitel.append(n_pages)

    # Probe-TOC um Seitenanzahl des Inhaltsverzeichnisses zu ermitteln
    # Vorläufige Seitennummern mit geschätztem Offset berechnen
    est_offset = 3
    est_seiten_nummern = []
    s = est_offset
    for i, n in enumerate(seiten_pro_kapitel):
        if i in trennseiten_pos:
            s += 1
        est_seiten_nummern.append(s)
        s += n
    toc_pages = render_inhaltsverzeichnis(probe_c, alle_kapitel, est_seiten_nummern)
    del probe_c, probe_buf

    # Seiten-Offset: Titelseite (1) + Inhaltsverzeichnis (toc_pages)
    # Kapitel starten auf der Seite danach.
    seiten_offset = 1 + toc_pages + 1

    # Seitennummern berechnen (mit Trennseiten)
    seiten_nummern = []
    aktuelle_seite = seiten_offset
    for i, n in enumerate(seiten_pro_kapitel):
        if i in trennseiten_pos:
            aktuelle_seite += 1  # Trennseite einfügen
        seiten_nummern.append(aktuelle_seite)
        aktuelle_seite += n

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

    # Kapitel (mit Trennseiten zwischen Hauptabschnitten)
    for i, (dateiname, data) in enumerate(alle_kapitel):
        if i in trennseiten_pos:
            section = trennseiten_pos[i]
            print(f"  Rendere Trennseite: {TRENNSEITEN_INFO[section]['titel']} ...")
            render_trennseite(c, section)
            c.showPage()
        print(f"  Rendere Seite {seiten_nummern[i]}: {dateiname} ...")
        render_kapitel(c, data, seiten_nummern[i])
        c.showPage()

    # Lösungsseiten am Ende
    from loesungen import render_loesungsseiten
    loes_start = aktuelle_seite
    print("  Rendere Lösungsseiten ...")
    n_loes = render_loesungsseiten(c, alle_kapitel, loes_start)
    if n_loes > 0:
        c.showPage()
    print(f"  → {n_loes} Lösungsseite(n)")

    c.save()
    print(f"\n✓ PDF gespeichert: {output_path}")


if __name__ == "__main__":
    main()
