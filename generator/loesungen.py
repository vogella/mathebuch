"""
loesungen.py – Berechnet und rendert kompakte Lösungsseiten am Ende des Buchs.
"""
import sys
from reportlab.lib.colors import HexColor, white
from reportlab.lib.units import cm
from reportlab.lib.pagesizes import A4
from layout import FARBEN, draw_page_bg, draw_page_number

W, H = A4

# ── Lösungsberechnung pro Aufgabentyp ─────────────────────


def _solve_lückenaufgaben(abschnitt):
    results = []
    for aufg in abschnitt["aufgaben"]:
        a, op, b, erg = aufg
        if erg is None:
            erg = (a + b) if op == "+" else (a - b)
            results.append(str(erg))
        elif b is None:
            b = (erg - a) if op == "+" else (a - erg)
            results.append(str(b))
        elif a is None:
            a = (erg - b) if op == "+" else (erg + b)
            results.append(str(a))
        else:
            results.append("")
    return results


def _solve_nachbarzahlen(abschnitt):
    results = []
    for aufg in abschnitt["aufgaben"]:
        vor, zahl, nach = aufg
        parts = []
        if vor is None:
            parts.append(str(zahl - 1))
        if zahl is None:
            parts.append(str(vor + 1))
        if nach is None:
            parts.append(str((zahl if zahl is not None else vor + 1) + 1))
        results.append(",".join(parts))
    return results


def _solve_würfelzählen(abschnitt):
    results = []
    default_op = abschnitt.get("operator", "+")
    operatoren_list = abschnitt.get("operatoren", [])
    for idx, aufg in enumerate(abschnitt["aufgaben"]):
        if idx < len(operatoren_list):
            ops = [o.strip() for o in operatoren_list[idx].split(",")]
        else:
            ops = [default_op] * (len(aufg) - 1)
        val = aufg[0]
        for i in range(1, len(aufg)):
            op = ops[i - 1] if i - 1 < len(ops) else default_op
            if op == "+":
                val += aufg[i]
            else:  # − or -
                val -= aufg[i]
        results.append(str(val))
    return results


def _solve_rechenmauer(abschnitt):
    results = []
    for mauer in abschnitt["mauern"]:
        # Compute from bottom up
        rows = [list(r) for r in mauer]
        for ri in range(1, len(rows)):
            for bi in range(len(rows[ri])):
                if rows[ri][bi] is None:
                    rows[ri][bi] = rows[ri - 1][bi] + rows[ri - 1][bi + 1]
        # Collect non-given values
        wall_results = []
        for ri in range(len(mauer)):
            for bi in range(len(mauer[ri])):
                if mauer[ri][bi] is None:
                    wall_results.append(str(rows[ri][bi]))
        results.append(",".join(wall_results))
    return results


def _solve_vergleiche(abschnitt):
    results = []
    for aufg in abschnitt["aufgaben"]:
        l, r = aufg
        if l < r:
            results.append("<")
        elif l > r:
            results.append(">")
        else:
            results.append("=")
    return results


def _solve_kettenaufgaben(abschnitt):
    results = []
    for kette in abschnitt["aufgaben"]:
        try:
            tokens = kette.split()
            val = float(tokens[0])
            it = iter(tokens[1:])
            for op_str, num_str in zip(it, it):
                num = float(num_str)
                if op_str == '+':
                    val += num
                elif op_str in ('-', '−'):
                    val -= num
                elif op_str in ('*', '×'):
                    val *= num
                elif op_str in ('/', '÷'):
                    if num == 0:
                        raise ZeroDivisionError
                    val /= num
                else:
                    raise ValueError(f"Unknown operator: {op_str}")
            results.append(str(int(val)))
        except (ValueError, IndexError, ZeroDivisionError):
            results.append("?")
    return results


def _solve_tauschaufgaben(abschnitt):
    results = []
    for aufg in abschnitt["aufgaben"]:
        results.append(str(aufg[0] + aufg[1]))
    return results


def _solve_verdoppeln_halbieren(abschnitt):
    results = []
    for aufg in abschnitt["aufgaben"]:
        zahl, typ = aufg
        if typ == "doppelt":
            results.append(str(zahl * 2))
        else:
            results.append(str(zahl // 2))
    return results


def _solve_zahlenstrahl(abschnitt):
    results = []
    for strahl in abschnitt["strahlen"]:
        von = strahl["von"]
        werte = strahl.get("werte", [])
        missing = []
        for i, val in enumerate(werte):
            if val is None:
                missing.append(str(von + i))
        results.append(",".join(missing))
    return results


def _solve_punktefeld(abschnitt):
    return [str(a) for a in abschnitt["aufgaben"]]


def _solve_zahlzerlegung(abschnitt):
    results = []
    for aufg in abschnitt["aufgaben"]:
        zahl, t1, t2 = aufg
        parts = []
        if t1 is None and t2 is None:
            # Both missing - give one possible answer
            parts.append(f"{zahl // 2}+{zahl - zahl // 2}")
        elif t1 is None:
            parts.append(str(zahl - t2))
        elif t2 is None:
            parts.append(str(zahl - t1))
        results.append(",".join(parts))
    return results


def _solve_zahlen_ordnen(abschnitt):
    results = []
    for zahlen in abschnitt["aufgaben"]:
        results.append("<".join(str(z) for z in sorted(zahlen)))
    return results


def _solve_zahlenhaus(abschnitt):
    verboten = set(abschnitt.get("verboten", []))
    results = []
    for dach in abschnitt["dachzahlen"]:
        pairs = []
        for a in range(0, dach + 1):
            b = dach - a
            if a != b and a not in verboten and b not in verboten and a < b:
                pairs.append(f"{a}+{b}")
        results.append(" ".join(pairs))
    return results


# ── Solver-Registry ───────────────────────────────────────

SOLVER = {
    "lückenaufgaben": _solve_lückenaufgaben,
    "nachbarzahlen": _solve_nachbarzahlen,
    "würfelzählen": _solve_würfelzählen,
    "rechenmauer": _solve_rechenmauer,
    "vergleiche": _solve_vergleiche,
    "kettenaufgaben": _solve_kettenaufgaben,
    "tauschaufgaben": _solve_tauschaufgaben,
    "verdoppeln_halbieren": _solve_verdoppeln_halbieren,
    "zahlenstrahl": _solve_zahlenstrahl,
    "punktefeld": _solve_punktefeld,
    "zahlzerlegung": _solve_zahlzerlegung,
    "zahlen_ordnen": _solve_zahlen_ordnen,
    "zahlenhaus": _solve_zahlenhaus,
}

# Types to skip (explanation, visual-only, or too complex for auto-solve)
SKIP_TYPES = {"erklaerung", "magisches_dreieck", "magische_dreiecke",
              "magisches_quadrat", "textaufgaben", "rechenraupe"}


# ── Rendering ─────────────────────────────────────────────

def render_loesungsseiten(c, alle_kapitel, start_seite):
    """Renders compact solution pages. Returns the number of pages added."""
    # Collect solutions per chapter
    kapitel_loesungen = []
    for seite_nr, (dateiname, kap_data) in enumerate(alle_kapitel, start=1):
        kap = kap_data["kapitel"]
        if kap.get("erklaerungsseite"):
            continue
        titel = kap["titel"]
        abschnitte = kap_data.get("abschnitte", [])
        sektionen = []
        for abschnitt in abschnitte:
            typ = abschnitt.get("typ", "")
            if typ in SKIP_TYPES:
                continue
            solver = SOLVER.get(typ)
            if solver is None:
                continue
            try:
                antworten = solver(abschnitt)
            except Exception as e:
                print(f"Warnung: Fehler bei der Lösungsberechnung für Typ '{typ}' in Seite '{dateiname}': {e}", file=sys.stderr)
                continue
            if antworten:
                label = abschnitt.get("titel", "")
                # Extract just the letter prefix (A, B, etc.)
                short_label = ""
                if label and len(label) >= 1:
                    first = label.strip().split()[0] if label.strip() else ""
                    if len(first) <= 2 and first.isalpha():
                        short_label = first
                sektionen.append((short_label, antworten))
        if sektionen:
            kapitel_loesungen.append((f"S.{seite_nr} {titel}", sektionen))

    if not kapitel_loesungen:
        return 0

    # Render
    pages = 0
    font_name = "Helvetica"
    font_bold = "Helvetica-Bold"
    font_size = 7.5
    line_h = 0.35 * cm
    col_margin = 1.5 * cm
    max_y = H - 3.0 * cm
    min_y = 2.0 * cm
    max_text_w = W - 3 * cm

    def new_page():
        nonlocal y, pages
        if pages > 0:
            c.showPage()
        draw_page_bg(c)
        # Header
        c.setFillColor(FARBEN["dunkel"])
        c.setFont(font_bold, 14)
        c.drawCentredString(W / 2, H - 2.2 * cm, "Lösungen")
        c.setStrokeColor(FARBEN["hellgrau"])
        c.setLineWidth(0.5)
        c.line(col_margin, H - 2.5 * cm, W - col_margin, H - 2.5 * cm)
        y = max_y
        pages += 1

    y = min_y  # force first new_page
    new_page()

    for kap_titel, sektionen in kapitel_loesungen:
        # Check if we need a new page
        needed = line_h * (1 + len(sektionen)) + 0.15 * cm
        if y - needed < min_y:
            draw_page_number(c, start_seite + pages - 1, show_stars=False)
            new_page()

        # Chapter title
        c.setFillColor(FARBEN["dunkel"])
        c.setFont(font_bold, 8)
        c.drawString(col_margin, y, kap_titel)
        y -= line_h

        # Section answers
        for short_label, antworten in sektionen:
            if y < min_y:
                draw_page_number(c, start_seite + pages - 1, show_stars=False)
                new_page()
            prefix = f"{short_label}: " if short_label else ""
            text = prefix + " · ".join(antworten)
            # Truncate if too wide
            c.setFont(font_name, font_size)
            while c.stringWidth(text, font_name, font_size) > max_text_w and len(text) > 20:
                text = text[:len(text) - 4] + "…"
            c.setFillColor(FARBEN["grau"])
            c.drawString(col_margin + 0.3 * cm, y, text)
            y -= line_h

        y -= 0.1 * cm  # small gap between chapters

    draw_page_number(c, start_seite + pages - 1, show_stars=False)
    return pages
