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
from layout import (draw_page_bg, draw_header, draw_name_date,
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
                           draw_textaufgaben)

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
    "textaufgaben":       draw_textaufgaben,
}

TRENNLINIE_Y = H - 15.5   # Y-Position der Trennlinie zwischen Abschnitten


def render_titelseite(c):
    """Titelseite mit Buchtitel, Namensfeld und Malblock."""
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

    # Malblock: "Male dich selbst!"
    mal_y = name_y - 3.5 * cm
    c.setFillColor(FARBEN["dunkel"])
    c.setFont("Helvetica-Bold", 14)
    c.drawString(2.5 * cm, mal_y + 0.2 * cm, "Male dich selbst:")
    # Großer Rahmen zum Malen
    box_h = 10 * cm
    c.setStrokeColor(FARBEN["hellgrau"])
    c.setFillColor(white)
    c.setLineWidth(1.5)
    c.setDash(4, 4)
    c.roundRect(2.5 * cm, mal_y - box_h, W - 5 * cm, box_h,
                radius=10, fill=1, stroke=1)
    c.setDash()  # Reset dash


def render_inhaltsverzeichnis(c, alle_kapitel, seiten_offset):
    """Inhaltsverzeichnis auf einer Seite."""
    draw_page_bg(c)

    # Header
    c.setFillColor(FARBEN["orange"])
    c.roundRect(1.5 * cm, H - 3.5 * cm, W - 3 * cm, 2.2 * cm,
                radius=12, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(W / 2, H - 2.5 * cm, "Inhaltsverzeichnis")

    y = H - 5.0 * cm
    line_h = 0.75 * cm

    for seite_nr, (dateiname, kap_data) in enumerate(alle_kapitel, start=seiten_offset):
        kap = kap_data["kapitel"]
        titel = kap["titel"]
        emoji = kap.get("emoji", "")
        farb_key = kap.get("farbe", "blau")

        if y < 2.5 * cm:
            break

        # Emoji
        c.setFillColor(FARBEN[farb_key])
        c.setFont("Helvetica-Bold", 12)
        c.drawString(2 * cm, y, emoji)

        # Titel
        c.setFillColor(FARBEN["dunkel"])
        c.setFont("Helvetica", 11)
        c.drawString(3.2 * cm, y, titel)

        # Gepunktete Linie
        titel_w = c.stringWidth(titel, "Helvetica", 11)
        dot_start = 3.2 * cm + titel_w + 0.3 * cm
        dot_end = W - 3.5 * cm
        if dot_end > dot_start:
            c.setFillColor(FARBEN["hellgrau"])
            c.setFont("Helvetica", 8)
            dots = ""
            while c.stringWidth(dots + " .", "Helvetica", 8) < (dot_end - dot_start):
                dots += " ."
            c.drawString(dot_start, y, dots)

        # Seitennummer
        c.setFillColor(FARBEN[farb_key])
        c.setFont("Helvetica-Bold", 11)
        c.drawRightString(W - 2 * cm, y, str(seite_nr))

        y -= line_h



def lade_kapitel(pfad):
    with open(pfad, encoding="utf-8") as f:
        return yaml.safe_load(f)


def zeichne_trennlinie(c, y):
    c.setStrokeColor(FARBEN["hellgrau"])
    c.setLineWidth(1)
    c.line(1.5*cm, y, W - 1.5*cm, y)


def render_kapitel(c, kapitel_data, seitennummer):
    """Rendert ein Kapitel auf eine PDF-Seite."""
    kap  = kapitel_data["kapitel"]
    farbe = kap.get("farbe", "blau")
    ist_erklaerung = kap.get("erklaerungsseite", False)

    draw_page_bg(c)
    draw_header(c, kap["titel"], kap["untertitel"], kap["emoji"], farbe)
    if not ist_erklaerung:
        draw_name_date(c)

    # Startposition: ohne Name/Datum-Felder mehr Platz
    y = H - 5.5*cm if ist_erklaerung else H - 7.0*cm
    abschnitte = kapitel_data.get("abschnitte", [])

    for i, abschnitt in enumerate(abschnitte):
        typ = abschnitt.get("typ")
        fn  = TYPEN.get(typ)
        if fn is None:
            print(f"  Warnung: Unbekannter Typ '{typ}', wird übersprungen.", file=sys.stderr)
            continue

        # Trennlinie zwischen Abschnitten (nicht vor dem ersten)
        if i > 0:
            zeichne_trennlinie(c, y + 0.5*cm)
            y -= 1.2*cm

        y = fn(c, abschnitt, farbe, y)

    draw_page_number(c, seitennummer, show_stars=not ist_erklaerung)


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

    c = canvas.Canvas(output_path, pagesize=A4)

    # Alle Kapitel vorladen
    alle_kapitel = []
    for yaml_file in yaml_files:
        data = lade_kapitel(yaml_file)
        alle_kapitel.append((os.path.basename(yaml_file), data))

    # Seiten-Offset: Titelseite + Inhaltsverzeichnis = 2 Seiten
    seiten_offset = 3  # Kapitel starten ab Seite 3

    # Titelseite
    print("  Rendere Titelseite ...")
    render_titelseite(c)
    c.showPage()

    # Inhaltsverzeichnis
    print("  Rendere Inhaltsverzeichnis ...")
    render_inhaltsverzeichnis(c, alle_kapitel, seiten_offset)
    c.showPage()

    # Kapitel
    for i, (dateiname, data) in enumerate(alle_kapitel):
        seite = seiten_offset + i
        print(f"  Rendere Seite {seite}: {dateiname} ...")
        render_kapitel(c, data, seite)
        c.showPage()

    # Lösungsseiten am Ende
    from loesungen import render_loesungsseiten
    loes_start = seiten_offset + len(alle_kapitel)
    print("  Rendere Lösungsseiten ...")
    n_loes = render_loesungsseiten(c, alle_kapitel, loes_start)
    if n_loes > 0:
        c.showPage()
    print(f"  → {n_loes} Lösungsseite(n)")

    c.save()
    print(f"\n✓ PDF gespeichert: {output_path}")


if __name__ == "__main__":
    main()
