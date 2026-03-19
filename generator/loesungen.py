"""
loesungen.py – Berechnet und rendert kompakte Lösungsseiten am Ende des Buchs.
"""
import re
import sys
import math
from itertools import permutations

from reportlab.lib.colors import HexColor, white
from reportlab.lib.units import cm
from reportlab.lib.pagesizes import A4
from layout import FARBEN, draw_page_bg, draw_page_number, FONT, FONT_BOLD

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
        rows = [list(r) for r in mauer]
        # Iteratively fill in values (both up and down) until no more progress
        changed = True
        while changed:
            changed = False
            for ri in range(1, len(rows)):
                for bi in range(len(rows[ri])):
                    # Up: sum of two below
                    if rows[ri][bi] is None and rows[ri - 1][bi] is not None and rows[ri - 1][bi + 1] is not None:
                        rows[ri][bi] = rows[ri - 1][bi] + rows[ri - 1][bi + 1]
                        changed = True
                    # Down-left: parent minus right child
                    if rows[ri][bi] is not None and rows[ri - 1][bi] is None and rows[ri - 1][bi + 1] is not None:
                        rows[ri - 1][bi] = rows[ri][bi] - rows[ri - 1][bi + 1]
                        changed = True
                    # Down-right: parent minus left child
                    if rows[ri][bi] is not None and rows[ri - 1][bi + 1] is None and rows[ri - 1][bi] is not None:
                        rows[ri - 1][bi + 1] = rows[ri][bi] - rows[ri - 1][bi]
                        changed = True
        # Collect non-given values
        wall_results = []
        for ri in range(len(mauer)):
            for bi in range(len(mauer[ri])):
                if mauer[ri][bi] is None:
                    wall_results.append(str(rows[ri][bi]) if rows[ri][bi] is not None else "?")
        results.append(",".join(wall_results))
    return results


def _eval_simple_expr(val):
    """Evaluate a value that may be a number or a simple arithmetic string."""
    if isinstance(val, (int, float)):
        return val
    if isinstance(val, str):
        tokens = val.replace("−", "-").replace("×", "*").replace("÷", "/").split()
        result = float(tokens[0])
        it = iter(tokens[1:])
        for op, num in zip(it, it):
            n = float(num)
            if op == '+':
                result += n
            elif op == '-':
                result -= n
            elif op == '*':
                result *= n
            elif op == '/':
                if n == 0:
                    raise ZeroDivisionError
                result /= n
            else:
                raise ValueError(f"Unknown operator: {op}")
        return result
    return val


def _solve_vergleiche(abschnitt):
    results = []
    for aufg in abschnitt["aufgaben"]:
        l, r = aufg
        try:
            lv = _eval_simple_expr(l)
            rv = _eval_simple_expr(r)
        except (ValueError, ZeroDivisionError, IndexError):
            results.append("?")
            continue
        if lv < rv:
            results.append("<")
        elif lv > rv:
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


def _solve_vervielfachen(abschnitt):
    results = []
    for aufg in abschnitt["aufgaben"]:
        zahl, ziel = aufg
        results.append(str(ziel // zahl))
    return results


def _solve_rechenraupe(abschnitt):
    results = []
    val = abschnitt["start"]
    for schritt in abschnitt["schritte"]:
        s = schritt.replace("−", "-")
        if s.startswith("+"):
            val += int(s[1:])
        elif s.startswith("-"):
            val -= int(s[1:])
        results.append(str(val))
    return results


def _solve_single_dreieck(werte, ziel, zahlen):
    """Solve a single magic triangle given values, target sum, and available numbers."""
    blanks = [i for i, v in enumerate(werte) if v is None]
    used = set(v for v in werte if v is not None)
    available = [z for z in zahlen if z not in used]

    for perm in permutations(available, len(blanks)):
        trial = list(werte)
        for i, idx in enumerate(blanks):
            trial[idx] = perm[i]
        if (trial[0] + trial[3] + trial[1] == ziel and
                trial[1] + trial[4] + trial[2] == ziel and
                trial[2] + trial[5] + trial[0] == ziel):
            return ",".join(str(trial[i]) for i in blanks)
    return None


def _solve_magisches_dreieck(abschnitt):
    # Handle "magische_dreiecke" type with a list of triangles
    dreiecke = abschnitt.get("dreiecke")
    if dreiecke:
        results = []
        for dreieck in dreiecke:
            werte = list(dreieck.get("werte", []))
            ziel = dreieck.get("zielsumme", 0)
            zahlen = list(range(1, 7))  # default 1-6
            result = _solve_single_dreieck(werte, ziel, zahlen)
            if result:
                results.append(result)
        return results

    # Handle single "magisches_dreieck" type
    werte = list(abschnitt.get("werte", []))
    hinweis = abschnitt.get("hinweis", "")
    m = re.search(r"(\d+)[–-](\d+)", hinweis)
    if m:
        zahlen = list(range(int(m.group(1)), int(m.group(2)) + 1))
    else:
        zahlen = list(range(1, 7))  # default 1-6

    beschreibung = abschnitt.get("beschreibung", "")
    m2 = re.search(r"Summe\s+(\d+)", beschreibung)
    if m2:
        ziel = int(m2.group(1))
    else:
        return []

    result = _solve_single_dreieck(werte, ziel, zahlen)
    return [result] if result else []


def _solve_magisches_quadrat(abschnitt):
    werte = list(abschnitt.get("werte", []))
    ziel = abschnitt.get("zielsumme", 15)
    given = {i: v for i, v in enumerate(werte) if v is not None}
    blanks = [i for i, v in enumerate(werte) if v is None]
    used = set(given.values())
    zahlen = [z for z in range(1, 10) if z not in used]

    lines = [[0, 1, 2], [3, 4, 5], [6, 7, 8],
             [0, 3, 6], [1, 4, 7], [2, 5, 8],
             [0, 4, 8], [2, 4, 6]]

    for perm in permutations(zahlen, len(blanks)):
        trial = list(werte)
        for i, idx in enumerate(blanks):
            trial[idx] = perm[i]
        if all(sum(trial[j] for j in line) == ziel for line in lines):
            return [",".join(str(trial[i]) for i in blanks)]
    return []


def _solve_textaufgaben(abschnitt):
    loesungen = abschnitt.get("loesungen", [])
    if loesungen:
        return [str(l) for l in loesungen]
    
    # Fallback: check individual tasks for "antwort" field
    aufgaben = abschnitt.get("aufgaben", [])
    results = []
    for a in aufgaben:
        if "antwort" in a:
            results.append(str(a["antwort"]))
    return results


def _solve_schatzsuche(abschnitt):
    results = []
    for aufg in abschnitt["aufgaben"]:
        start = aufg["start"]
        val = start
        intermediates = []
        for s in aufg["schritte"]:
            op = s[0]
            num = int(s[1:])
            val = val + num if op == "+" else val - num
            intermediates.append(str(val))
        results.append(",".join(intermediates))
    return results


def _solve_zahlenkreis(abschnitt):
    results = []
    labels = abschnitt.get("labels", [])
    for idx, aufg in enumerate(abschnitt.get("aufgaben", [])):
        n = len(aufg)
        # Find any non-None value to use as start
        start_idx = -1
        start_val = -1
        for i, v in enumerate(aufg):
            if v is not None:
                start_idx = i
                start_val = v
                break
        
        if start_idx == -1:
            results.append("")
            continue
            
        # Determine direction from label
        label = labels[idx] if idx < len(labels) else "Immer einer mehr"
        direction = 1 if "mehr" in label.lower() else -1
        
        # Determine base (0 for range 0-9, 10 for 10-19)
        base = 0 if start_val < 10 else 10
        
        # Calculate full circle values
        # The circle always has n nodes, usually 10
        full = []
        for i in range(n):
            # Calculate value at index i based on start_val at start_idx
            # Relative offset from start_idx is (i - start_idx)
            val = ((start_val - base + (i - start_idx) * direction) % n) + base
            full.append(val)
        
        missing = []
        for i in range(n):
            if aufg[i] is None:
                missing.append(str(full[i]))
        results.append(",".join(missing))
    return results


def _solve_dungeon_flucht(abschnitt):
    return [str(aufg["antwort"]) for aufg in abschnitt["aufgaben"]]


def _solve_zehneruebergang(abschnitt):
    results = []
    for aufg in abschnitt["aufgaben"]:
        a, op, b = aufg
        if op == "+":
            step1 = 10 - a       # how much to add to reach 10
            step2 = b - step1    # remainder after reaching 10
            total = a + b
        else:  # "-"
            step1 = a - 10       # how much to subtract to reach 10
            step2 = b - step1    # remainder after reaching 10
            total = a - b
        results.append([step1, step2, total])
    return results


def _solve_gerade_ungerade(abschnitt):
    results = []
    modus = abschnitt.get("modus", "sortieren")
    aufgaben = abschnitt.get("aufgaben", [])

    for aufg in aufgaben:
        if modus == "sortieren":
            zahlen = aufg["zahlen"]
            gerade = [z for z in zahlen if z % 2 == 0]
            ungerade = [z for z in zahlen if z % 2 != 0]
            results.append([gerade, ungerade])
        elif modus == "malen":
            zahlen = aufg["zahlen"]
            res = ["G" if z % 2 == 0 else "U" for z in zahlen]
            results.append(res)
        elif modus == "muster":
            start = aufg["start"]
            n_luecken = aufg["lücken"]
            # Assume constant difference based on first two elements
            diff = start[1] - start[0] if len(start) >= 2 else 2
            last = start[-1]
            luecken_res = []
            for i in range(1, n_luecken + 1):
                luecken_res.append(str(last + i * diff))
            results.append(luecken_res)
    return results


def _solve_rechenquadrat_2x2(abschnitt):
    results = []
    for q in abschnitt.get("quadrate", []):
        res = q.get("loesung", [])
        results.append(",".join(str(v) for v in res))
    return results


def _solve_muster_fortsetzen(abschnitt):
    results = []
    loesungen = abschnitt.get("loesungen", [])
    for res in loesungen:
        # res can be list of numbers or list of strings "shape:color"
        parts = []
        for v in res:
            if isinstance(v, str) and ":" in v:
                # For shapes, just use the first letter of shape and color for brevity
                shape, color = v.split(":")
                parts.append(f"{shape[0]}{color[0]}")
            else:
                parts.append(str(v))
        results.append(",".join(parts))
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
    "vervielfachen": _solve_vervielfachen,
    "rechenraupe": _solve_rechenraupe,
    "magisches_dreieck": _solve_magisches_dreieck,
    "magische_dreiecke": _solve_magisches_dreieck,
    "magisches_quadrat": _solve_magisches_quadrat,
    "textaufgaben": _solve_textaufgaben,
    "zahlenraetsel": _solve_textaufgaben,
    "einkaufen": _solve_textaufgaben,
    "kalender_raetsel": _solve_textaufgaben,
    "schatzsuche": _solve_schatzsuche,
    "labyrinth_flucht": _solve_schatzsuche,
    "zahlenkreis": _solve_zahlenkreis,
    "dungeon_flucht":     _solve_dungeon_flucht,
    "zehneruebergang":    _solve_zehneruebergang,
    "gerade_ungerade":    _solve_gerade_ungerade,
    "rechenquadrat_2x2":  _solve_rechenquadrat_2x2,
    "muster_fortsetzen":  _solve_muster_fortsetzen,
}
# Types to skip (explanation, visual-only)
SKIP_TYPES = {"erklaerung", "wuerfel_zuordnen"}


# ── Rendering ─────────────────────────────────────────────

def render_loesungsseiten(c, alle_kapitel, start_seite):
    """Renders readable solution pages. Returns the number of pages added."""
    # Collect solutions per chapter
    kapitel_loesungen = []
    for seite_nr, (dateiname, kap_data) in enumerate(alle_kapitel, start=1):
        kap = kap_data["kapitel"]
        if kap.get("erklaerungsseite"):
            continue
        titel = kap["titel"]
        emoji = kap.get("emoji", "")
        farbe = kap.get("farbe", "blau")
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
            kapitel_loesungen.append((seite_nr, titel, emoji, farbe, sektionen))

    if not kapitel_loesungen:
        return 0

    # Render
    pages = 0
    font_name = FONT
    font_bold = FONT_BOLD
    
    # Styling constants
    FONT_SIZE = 9
    TITLE_SIZE = 9.5
    EMOJI_FONT_SIZE = 12
    LINE_H = 0.45 * cm
    COL_MARGIN = 1.5 * cm
    MAX_Y = H - 3.0 * cm
    MIN_Y = 2.0 * cm
    MAX_TEXT_W = W - 3.5 * cm
    ALT_BG = HexColor("#F5F5F5")  # light gray for alternating chapters
    ANSWER_INDENT = 0.4 * cm
    CHAPTER_GAP = 0.2 * cm

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
        c.line(COL_MARGIN, H - 2.5 * cm, W - COL_MARGIN, H - 2.5 * cm)
        y = MAX_Y
        pages += 1

    y = MIN_Y  # force first new_page
    new_page()

    for kap_idx, (seite_nr, titel, emoji, farbe, sektionen) in enumerate(kapitel_loesungen):
        # Calculate total height needed for this chapter block
        needed = LINE_H * (1 + len(sektionen)) + 0.3 * cm
        if y - needed < MIN_Y:
            draw_page_number(c, start_seite + pages - 1, show_stars=False)
            new_page()

        # Draw alternating light gray background for every other chapter
        if kap_idx % 2 == 1:
            # Refactor calculation for clarity without changing the output
            content_h = LINE_H * (1 + len(sektionen))
            padding_top = 0.3 * LINE_H + 0.1 * cm
            padding_bottom = 0.15 * cm - 0.3 * LINE_H

            rect_h = content_h + padding_top + padding_bottom
            rect_y = y - content_h - padding_bottom
            
            c.setFillColor(ALT_BG)
            c.rect(COL_MARGIN - 0.2 * cm, rect_y,
                   W - 2 * COL_MARGIN + 0.4 * cm, rect_h,
                   fill=1, stroke=0)

        # Chapter title with emoji and color accent
        farb_col = FARBEN.get(farbe, FARBEN["blau"])
        emoji_str = f"{emoji} " if emoji else ""
        # Draw emoji in chapter color
        c.setFillColor(farb_col)
        c.setFont(font_bold, EMOJI_FONT_SIZE)
        emoji_w = c.stringWidth(emoji_str, font_bold, EMOJI_FONT_SIZE) if emoji_str else 0
        c.drawString(COL_MARGIN, y, emoji_str)
        # Draw chapter reference in dark color
        c.setFillColor(FARBEN["dunkel"])
        c.setFont(font_bold, TITLE_SIZE)
        c.drawString(COL_MARGIN + emoji_w, y, f"Seite {seite_nr}, {titel}")
        y -= LINE_H

        # Section answers
        for short_label, antworten in sektionen:
            if y < MIN_Y:
                draw_page_number(c, start_seite + pages - 1, show_stars=False)
                new_page()
            
            prefix = f"Aufgabe {short_label}: " if short_label else ""
            
            # Format answers: join nested lists with commas
            formatted_antworten = []
            for a in antworten:
                if isinstance(a, (list, tuple)):
                    formatted_antworten.append(",".join(map(str, a)))
                else:
                    formatted_antworten.append(str(a))
            
            text = prefix + " · ".join(formatted_antworten)
            
            # Truncate if too wide
            c.setFont(font_name, FONT_SIZE)
            while c.stringWidth(text, font_name, FONT_SIZE) > MAX_TEXT_W and len(text) > 20:
                text = text[:len(text) - 4] + "…"
            c.setFillColor(FARBEN["dunkel"])
            c.drawString(COL_MARGIN + ANSWER_INDENT, y, text)
            y -= LINE_H

        y -= CHAPTER_GAP  # gap between chapters

    draw_page_number(c, start_seite + pages - 1, show_stars=False)
    return pages
