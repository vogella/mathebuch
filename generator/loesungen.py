"""
loesungen.py – Berechnet und rendert kompakte Lösungsseiten am Ende des Buchs.
"""
import re
import sys
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
        bis = strahl["bis"]
        werte = strahl.get("werte", [])
        
        sequence = []
        for i in range(bis - von + 1):
            val = werte[i] if i < len(werte) else None
            num = von + i
            if val is None:
                # Missing value in the original task, show in brackets in solution
                sequence.append(f"({num})")
            else:
                sequence.append(str(num))
        results.append(" ".join(sequence))
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
    return []


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
    for idx, aufg in enumerate(abschnitt["aufgaben"]):
        n = len(aufg)
        # Find any known value
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
        base = (start_val // 10) * 10

        # Calculate full circle values
        full = []
        for i in range(n):
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


def _solve_dungeon_abenteuer(abschnitt):
    results = []
    for aufg in abschnitt.get("aufgaben", []):
        grid = aufg["grid"]
        entrance_col = aufg.get("eingang", 0)
        current_val = grid[0][entrance_col]

        path_values = [current_val]
        for op_str in aufg.get("pfad", []):
            parts = op_str.split()
            if len(parts) == 2:
                op, val_str = parts[0], parts[1]
                try:
                    val = int(val_str)
                    if op == "+":
                        current_val += val
                    elif op == "-":
                        current_val -= val
                except ValueError:
                    pass
            path_values.append(current_val)
        results.append(path_values)
    return results


def _solve_rechenweg_labyrinth(abschnitt):
    results = []
    for aufg in abschnitt.get("aufgaben", []):
        spalten = aufg.get("spalten", [])
        ziel = aufg.get("zielsumme", 0)

        # We need to find one number per column that sums to 'ziel'
        def find_path(col_idx, current_sum, current_path):
            if col_idx == len(spalten):
                return current_path if current_sum == ziel else None
            for row_idx, val in enumerate(spalten[col_idx]):
                res = find_path(col_idx + 1, current_sum + val, current_path + [row_idx])
                if res is not None:
                    return res
            return None

        path = find_path(0, 0, [])
        if path is not None:
            # Return the actual values picked, not just row indices
            values = [spalten[ci][ri] for ci, ri in enumerate(path)]
            results.append(f"{'+'.join(map(str, values))}={ziel}")
        else:
            results.append("?")
    return results


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


def _solve_muster_fortsetzen(abschnitt):
    # If explicit solutions are provided, use them
    loesungen = abschnitt.get("loesungen", [])
    if loesungen:
        results = []
        for res in loesungen:
            parts = []
            for v in res:
                if isinstance(v, str) and ":" in v:
                    shape, color = v.split(":")
                    parts.append(f"{shape[0]}{color[0]}")
                else:
                    parts.append(str(v))
            results.append(",".join(parts))
        return results

    # Otherwise, calculate from the pattern
    results = []
    for aufg in abschnitt["aufgaben"]:
        muster = aufg.get("muster") or aufg.get("elemente", [])
        # Find the constant difference from the known (non-None) numeric values
        known = [(i, v) for i, v in enumerate(muster) if v is not None and isinstance(v, (int, float))]
        if len(known) >= 2:
            idx1, v1 = known[0]
            idx2, v2 = known[1]
            diff = (v2 - v1) // (idx2 - idx1)
        else:
            results.append("")
            continue

        filled = list(muster)
        ref_idx, ref_val = known[0]
        for i in range(len(filled)):
            if filled[i] is None:
                filled[i] = ref_val + (i - ref_idx) * diff

        missing = [str(filled[i]) for i, v in enumerate(muster) if v is None]
        results.append(",".join(missing))
    return results


def _solve_gerade_ungerade(abschnitt):
    modus = abschnitt.get("modus", "einkreisen")
    if modus in ("einkreisen", "sortieren"):
        zahlen = abschnitt.get("zahlen", [])
        gerade = [z for z in zahlen if z % 2 == 0]
        ungerade = [z for z in zahlen if z % 2 != 0]
        return [f"G:{','.join(str(x) for x in gerade)} U:{','.join(str(x) for x in ungerade)}"]
    elif modus == "muster":
        muster_list = abschnitt.get("muster", [])
        results = []
        for m in muster_list:
            if not (m.get("start") and m.get("luecken") and "schritt" in m):
                continue

            row = []
            last_num = m["start"][-1]
            schritt = m["schritt"]
            luecken = m["luecken"]
            for i in range(1, luecken + 1):
                row.append(last_num + i * schritt)
            results.append(",".join(str(x) for x in row))
        return results
    return []


def _solve_rechenquadrat_2x2(abschnitt):
    results = []
    for q in abschnitt.get("quadrate", []):
        res = q.get("loesung", [])
        results.append(",".join(str(v) for v in res))
    return results


def _solve_umkehraufgaben(abschnitt):
    """
    For each [a, op, b, result]:
    - "+": inverse rows are (result-b)=a and (result-a)=b
    - "-": inverse rows are (result+b)=a and (b+result)=a
    Returns a list of [ans1, ans2] pairs.
    """
    results = []
    for aufg in abschnitt["aufgaben"]:
        a, op, b, result = aufg
        if op == "+":
            ans1 = result - b   # = a
            ans2 = result - a   # = b
        else:  # "−" or "-"
            ans1 = a            # result + b = a
            ans2 = a            # b + result = a
        results.append([ans1, ans2])
    return results


def _solve_zahlen_schreiben(abschnitt):
    """No computed answer needed for digit tracing."""
    return [str(d) for d in abschnitt["aufgaben"]]


def _solve_formen_zaehlen(abschnitt):
    """Count shapes and return answers."""
    results = []
    for aufg in abschnitt.get("aufgaben", []):
        formen = aufg["formen"]
        fragen = aufg.get("fragen", [])
        answers = []
        for frage in fragen:
            target_shape = frage["form"]
            target_color = frage.get("farbe")
            count = 0
            for f in formen:
                shape, color = f.split(":")
                if shape == target_shape:
                    if target_color is None or color == target_color:
                        count += 1
            answers.append(str(count))
        results.append(", ".join(answers))
    return results


def _solve_symmetrie(abschnitt):
    """Solve symmetry by counting how many null fields need to be filled."""
    results = []
    for aufg in abschnitt.get("aufgaben", []):
        raster = aufg["raster"]
        achse = aufg.get("achse", "vertikal")
        zeilen = len(raster)
        if not zeilen or not raster[0]:
            results.append("0 Felder")
            continue
        spalten = len(raster[0])

        fill_count = 0
        if achse == "vertikal":
            for r in range(zeilen):
                for col in range(spalten // 2):
                    mirrored_c = spalten - 1 - col
                    if raster[r][col] == 1 and raster[r][mirrored_c] is None:
                        fill_count += 1
                    elif raster[r][col] is None and raster[r][mirrored_c] == 1:
                        fill_count += 1
        else:
            for col in range(spalten):
                for r in range(zeilen // 2):
                    mirrored_r = zeilen - 1 - r
                    if raster[r][col] == 1 and raster[mirrored_r][col] is None:
                        fill_count += 1
                    elif raster[r][col] is None and raster[mirrored_r][col] == 1:
                        fill_count += 1

        results.append(f"{fill_count} Felder ausmalen")
    return results


def _solve_bonbon_fabrik(abschnitt):
    results = []
    for aufg in abschnitt["aufgaben"]:
        fabriken = aufg["fabriken"]
        budget = aufg["budget"]
        n = len(fabriken)
        best_menge = 0
        best_kosten = float('inf')
        best_mask = 0
        # Brute force all subsets (max 6 factories = 64 subsets)
        for mask in range(1, 1 << n):
            kosten = sum(fabriken[i]["kosten"] for i in range(n) if mask & (1 << i))
            menge = sum(fabriken[i]["menge"] for i in range(n) if mask & (1 << i))
            if kosten <= budget:
                if menge > best_menge or (menge == best_menge and kosten < best_kosten):
                    best_menge = menge
                    best_kosten = kosten
                    best_mask = mask
        if best_mask == 0:
            best_kosten = 0
        names = [fabriken[i]["name"] for i in range(n) if best_mask & (1 << i)]
        results.append(f"{best_kosten}€, {best_menge} Stück ({', '.join(names)})")
    return results


def _solve_einkaufen_euro_cent(abschnitt):
    results = []
    for aufg in abschnitt["aufgaben"]:
        artikel = aufg["artikel"]
        euro_sum = sum(a["euro"] for a in artikel)
        cent_sum = sum(a["cent"] for a in artikel)
        results.append(f"{euro_sum}€ {cent_sum}ct")
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
    "rechenweg_labyrinth": _solve_rechenweg_labyrinth,
    "zahlenkreis":        _solve_zahlenkreis,
    "dungeon_flucht":     _solve_dungeon_flucht,
    "dungeon_abenteuer":  _solve_dungeon_abenteuer,
    "zehneruebergang":    _solve_zehneruebergang,

    "gerade_ungerade":    _solve_gerade_ungerade,
    "rechenquadrat_2x2":  _solve_rechenquadrat_2x2,
    "muster_fortsetzen":  _solve_muster_fortsetzen,
    "motivation":         lambda ab: [],
    "umkehraufgaben":     _solve_umkehraufgaben,
    "zahlen_schreiben":   _solve_zahlen_schreiben,
    "formen_zaehlen":     _solve_formen_zaehlen,
    "symmetrie":          _solve_symmetrie,
    "bonbon_fabrik":       _solve_bonbon_fabrik,
    "einkaufen_euro_cent": _solve_einkaufen_euro_cent,
}

# Types to skip (explanation, visual-only)
SKIP_TYPES = {"erklaerung", "wuerfel_zuordnen", "motivation"}


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
    font_name = FONT
    font_bold = FONT_BOLD
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
            formatted = [",".join(map(str, a)) if isinstance(a, (list, tuple)) else str(a)
                         for a in antworten]
            text = prefix + " | ".join(formatted)
            # Truncate if too wide
            c.setFont(font_name, font_size)
            while c.stringWidth(text, font_name, font_size) > max_text_w and len(text) > 20:
                text = text[:len(text) - 4] + "..."
            c.setFillColor(FARBEN["grau"])
            c.drawString(col_margin + 0.3 * cm, y, text)
            y -= line_h

        y -= 0.1 * cm  # small gap between chapters

    draw_page_number(c, start_seite + pages - 1, show_stars=False)
    return pages
