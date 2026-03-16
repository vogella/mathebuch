# 📚 Mathebuch-Generator – Klasse 1

Einfaches Python-Werkzeug zum Erstellen eines druckfertigen Mathe-Übungsbuchs als PDF.
Du pflegst Aufgaben in einfachen YAML-Dateien, das Skript erzeugt automatisch schöne A4-Seiten.

---

## Projektstruktur

```
mathebuch/
├── aufgaben/                    ← Hier pflegst du die Inhalte
│   ├── kapitel1_addition.yaml
│   ├── kapitel2_subtraktion.yaml
│   └── kapitel3_gemischt.yaml
├── generator/                   ← Das Programm (nicht anfassen nötig)
│   ├── main.py
│   ├── layout.py
│   └── aufgabentypen.py
├── output/                      ← Hier landet das fertige PDF
│   └── mathebuch_klasse1.pdf
└── README.md
```

---

## Einrichtung (einmalig)

```bash
# 1. Python prüfen (Ubuntu hat es meist schon)
python3 --version

# 2. Virtuelle Umgebung erstellen
python3 -m venv .venv

# 3. Virtuelle Umgebung aktivieren
source .venv/bin/activate

# 4. Abhängigkeiten installieren
pip install reportlab pyyaml
```

> **Hinweis:** Die virtuelle Umgebung muss in jeder neuen Terminal-Sitzung erneut aktiviert werden:
> ```bash
> source .venv/bin/activate
> ```

---

## PDF erzeugen

```bash
# Virtuelle Umgebung aktivieren (falls noch nicht geschehen)
source .venv/bin/activate

# PDF generieren
cd generator
python3 main.py
```

Das fertige PDF liegt danach in `output/mathebuch_klasse1.pdf`.

**Eigenen Ausgabepfad angeben:**
```bash
python3 main.py --output /home/deinname/Desktop/buch.pdf
```

---

## Aufgaben bearbeiten

Öffne einfach eine YAML-Datei im `aufgaben/`-Ordner mit einem Texteditor.

### Neue Lückenaufgabe hinzufügen

```yaml
- typ: lückenaufgaben
  titel: "A  Wie viel ist das?"
  aufgaben:
    # Format: [a, operator, b, ergebnis]
    # null = Lücke (leeres Feld zum Ausfüllen)
    - [3, "+", 4, null]      # 3 + 4 = ___
    - [5, "+", null, 8]      # 5 + ___ = 8
    - [null, "+", 2, 9]      # ___ + 2 = 9
```

### Zahlenhaus anpassen

```yaml
- typ: zahlenhaus
  titel: "B  Zahlenhaus"
  dachzahlen: [5, 7, 8, 10]   # Beliebig viele Häuser
```

### Rechenraupe anpassen

```yaml
- typ: rechenraupe
  titel: "B  Rechenraupe"
  start: 15          # Startzahl
  schritte: ["-4", "+3", "-2"]   # Beliebig viele Schritte
```

### Neues Kapitel anlegen

Einfach eine neue YAML-Datei in `aufgaben/` erstellen.
Der Dateiname bestimmt die Reihenfolge (alphabetisch), also z. B.:

```
kapitel4_verdoppeln.yaml
```

Mindest-Struktur einer YAML-Datei:

```yaml
kapitel:
  titel: "Verdoppeln und Halbieren"
  untertitel: "Fülle die Lücken aus!"
  emoji: "✖️"
  farbe: "purple"   # gruen | pink | blau | orange | yellow | purple
  zahlenraum: 20

abschnitte:
  - typ: lückenaufgaben
    titel: "A  Verdopple die Zahl!"
    aufgaben:
      - [3, "+", 3, null]
      - [4, "+", 4, null]
      - [5, "+", 5, null]
```

---

## Verfügbare Aufgabentypen

| Typ | Beschreibung |
|-----|-------------|
| `lückenaufgaben` | Rechenaufgaben mit einer Lücke (a, b oder Ergebnis) |
| `zahlenhaus` | Zahl auf dem Dach, Zerlegungspaare in den Feldern |
| `rechenraupe` | Kette von Rechenoperationen |
| `magisches_dreieck` | Zahlen so einsetzen, dass alle Seiten gleich sind |

---

## Abhängigkeiten

| Paket | Wozu |
|-------|------|
| `reportlab` | PDF erzeugen |
| `pyyaml` | YAML-Dateien lesen |

Installieren mit:
```bash
pip install reportlab pyyaml
```
