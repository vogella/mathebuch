            # Draw blanks
            for i in range(n_blanks):
                if loes and i < len(loes):
                    _draw_filled_answer_box(c, x, row_y - 0.5*cm, str(loes[i]), w=box_w, h=box_h)
                else:
                    draw_answer_box(c, x, row_y - 0.5*cm, w=box_w, h=box_h)
                x += box_w + 0.3*cm
                
            row_y -= 1.8*cm

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
                c.setFont("Helvetica-Bold", 14)
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
                c.setFont("Helvetica", 10)
                c.drawString(cx + 4.5 * cm, cy, "Gerade?")
                draw_answer_box(c, cx + 6.0 * cm, cy - 0.3 * cm, w=0.8 * cm, h=0.7 * cm)
                
            row_y -= (len(zahlen) + 1) // 2 * row_h
            
    return row_y
