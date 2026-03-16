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
from layout import (draw_page_bg, draw_header, draw_name_date,
                    draw_page_number, FARBEN)
from aufgabentypen import (draw_erklaerung, draw_lückenaufgaben,
                           draw_zahlenhaus, draw_rechenraupe,
                           draw_magisches_dreieck, draw_magische_dreiecke,
                           draw_magisches_quadrat, draw_würfelzählen,
                           draw_rechenmauer, draw_vergleiche,
                           draw_nachbarzahlen, draw_zahlzerlegung,
                           draw_kettenaufgaben, draw_tauschaufgaben,
                           draw_verdoppeln_halbieren,
                           draw_zahlenstrahl, draw_punktefeld,
                           draw_zahlen_ordnen, draw_textaufgaben)

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
    "textaufgaben":       draw_textaufgaben,
}

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

    alle_kapitel = []
    for i, yaml_file in enumerate(yaml_files, start=1):
        print(f"  Rendere Seite {i}: {os.path.basename(yaml_file)} ...")
        data = lade_kapitel(yaml_file)
        alle_kapitel.append((os.path.basename(yaml_file), data))
        render_kapitel(c, data, i)
        c.showPage()

    # Lösungsseiten am Ende
    from loesungen import render_loesungsseiten
    print("  Rendere Lösungsseiten ...")
    n_loes = render_loesungsseiten(c, alle_kapitel, len(yaml_files) + 1)
    print(f"  → {n_loes} Lösungsseite(n)")

    c.save()
    print(f"\n✓ PDF gespeichert: {output_path}")


if __name__ == "__main__":
    main()
