# -*- coding: utf-8 -*-
"""
Gerador de Carrossel LinkedIn - Matheus Zacche
===============================================
Layouts suportados:
  "numbered"    - cards com numero 01/02 + titulo + descricao
  "categorias"  - cards com pill de categoria + bullet list
  "timeline"    - linha vertical com circulos + pill + texto (ex: fluxo)
  "comparativo" - dois cards lado a lado (ex: evite vs faca, sem vs com)
"""

import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# ============================================================================
# PATHS
# ============================================================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR  = os.path.dirname(SCRIPT_DIR)
ASSETS_DIR = os.path.join(SKILL_DIR, "assets")
OUTPUT_DIR = os.path.join(SKILL_DIR, "output")

PHOTO_PATH   = os.path.join(ASSETS_DIR, "foto_matheus.jpeg")
FONT_REGULAR = os.path.join(ASSETS_DIR, "NotoSans-Regular.ttf")
FONT_BOLD    = os.path.join(ASSETS_DIR, "NotoSans-Bold.ttf")

# ============================================================================
# DESIGN TOKENS
# ============================================================================
W        = 1080
H        = 1350
PAD      = 56
HEADER_H = 120
FOOTER_H = 50
BANNER_H = 80

BG       = "#1a1a2e"
CARD_BG  = "#2a2a4a"   # mais visivel que o anterior
WHITE    = "#ffffff"
GRAY     = "#a0a0b8"
DIM_GRAY = "#5a5a7a"
SEP      = "#2a2a48"
DARK_BG  = "#141428"
PILL_TXT = "#0a0a1e"   # texto escuro sobre pill colorida


# ============================================================================
# FONTES
# ============================================================================
def font(bold=False, size=24):
    path = FONT_BOLD if bold else FONT_REGULAR
    try:
        return ImageFont.truetype(path, size)
    except (OSError, IOError):
        try:
            return ImageFont.truetype("arialbd.ttf" if bold else "arial.ttf", size)
        except (OSError, IOError):
            return ImageFont.load_default()


# ============================================================================
# COR
# ============================================================================
def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def tint(base_hex, color_hex, alpha=0.18):
    br, bg, bb = hex_rgb(base_hex)
    cr, cg, cb = hex_rgb(color_hex)
    return (
        int(br + (cr - br) * alpha),
        int(bg + (cg - bg) * alpha),
        int(bb + (cb - bb) * alpha),
    )


# ============================================================================
# UTILITARIOS DE TEXTO
# ============================================================================
def bb(draw, text, fnt):
    return draw.textbbox((0, 0), text, font=fnt)


def tw(draw, text, fnt):
    b = bb(draw, text, fnt)
    return b[2] - b[0]


def th_val(draw, text, fnt):
    b = bb(draw, text, fnt)
    return b[3] - b[1]


def put(draw, text, x, y, fnt, fill=WHITE):
    """Desenha texto compensando offset interno da fonte."""
    b = bb(draw, text, fnt)
    draw.text((x - b[0], y - b[1]), text, font=fnt, fill=fill)


def put_center(draw, text, cx, y, fnt, fill=WHITE):
    b = bb(draw, text, fnt)
    put(draw, text, cx - (b[2] - b[0]) // 2, y, fnt, fill)


def wrap_lines(draw, text, fnt, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if tw(draw, test, fnt) <= max_w:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines or [""]


def draw_wrapped(draw, text, x, y, fnt, fill, max_w, line_gap=8):
    """Desenha texto com wrap. Retorna Y apos ultima linha."""
    for line in wrap_lines(draw, text, fnt, max_w):
        put(draw, line, x, y, fnt, fill)
        y += th_val(draw, line, fnt) + line_gap
    return y


def draw_wrapped_center(draw, text, cx, y, fnt, fill, max_w, line_gap=8):
    for line in wrap_lines(draw, text, fnt, max_w):
        put_center(draw, line, cx, y, fnt, fill)
        y += th_val(draw, line, fnt) + line_gap
    return y


def measure_wrapped(draw, text, fnt, max_w, line_gap=8):
    lines = wrap_lines(draw, text, fnt, max_w)
    return sum(th_val(draw, l, fnt) + line_gap for l in lines)


# ============================================================================
# FOTO CIRCULAR
# ============================================================================
def circular_photo(size=56):
    try:
        img = Image.open(PHOTO_PATH).convert("RGBA")
        pw, ph = img.size
        side = min(pw, ph)
        img = img.crop(((pw - side) // 2, 0, (pw - side) // 2 + side, side))
        img = img.resize((size, size), Image.LANCZOS)
        mask = Image.new("L", (size, size), 0)
        ImageDraw.Draw(mask).ellipse((0, 0, size, size), fill=255)
        img.putalpha(mask)
        return img
    except Exception:
        ph = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        ImageDraw.Draw(ph).ellipse((0, 0, size, size), fill="#00d4aa")
        return ph


# ============================================================================
# HEADER
# ============================================================================
def draw_header(img, draw):
    PHOTO_SZ = 52
    py = 18
    nx = PAD + PHOTO_SZ + 14

    photo = circular_photo(PHOTO_SZ)
    img.paste(photo, (PAD, py), photo)

    fn = font(True, 26)
    put(draw, "Matheus Zacche", nx, py + 4, fn, WHITE)
    name_end = nx + tw(draw, "Matheus Zacche", fn)

    bcx = name_end + 16
    bcy = py + 4 + th_val(draw, "Matheus Zacche", fn) // 2
    br  = 10
    draw.ellipse((bcx-br, bcy-br, bcx+br, bcy+br), fill="#1a8cff")
    cf = font(True, 13)
    b  = bb(draw, "v", cf)
    draw.text((bcx - (b[2]-b[0])//2 - b[0], bcy - (b[3]-b[1])//2 - b[1]),
              "v", font=cf, fill=WHITE)

    hf = font(False, 19)
    put(draw, "@matheus.zacche", nx, py + 38, hf, GRAY)

    df   = font(False, 20)
    dots = "• • •"
    put(draw, dots, W - PAD - tw(draw, dots, df), py + 16, df, GRAY)

    sep_y = py + PHOTO_SZ + 14
    draw.line([(PAD, sep_y), (W - PAD, sep_y)], fill=SEP, width=1)


# ============================================================================
# PROGRESS BAR
# ============================================================================
def draw_progress(draw, cur, total, color):
    by = H - FOOTER_H + 16
    bh = 4
    bx = PAD
    bw = W - 2 * PAD

    draw.rounded_rectangle((bx, by, bx+bw, by+bh), radius=2, fill=DIM_GRAY)
    filled = int(bw * cur / total)
    if filled > 0:
        draw.rounded_rectangle((bx, by, bx+filled, by+bh), radius=2, fill=color)

    pf = font(False, 17)
    pt = f"{cur}/{total}"
    put(draw, pt, W - PAD - tw(draw, pt, pf), by + bh + 5, pf, GRAY)


# ============================================================================
# BANNER DE DESTAQUE
# Fundo escuro + texto na cor de destaque (igual ao template de referencia)
# ============================================================================
def draw_banner(draw, text, color, y_bottom):
    """Desenha banner. Retorna y_top do banner."""
    bx = PAD
    bw = W - 2 * PAD
    by = y_bottom - BANNER_H

    draw.rounded_rectangle((bx, by, bx+bw, by+BANNER_H),
                            radius=10, fill=tint(DARK_BG, color, 0.35))
    draw.rounded_rectangle((bx, by, bx+bw, by+BANNER_H),
                            radius=10, outline=color, width=1)

    bf    = font(True, 23)
    lines = wrap_lines(draw, text, bf, bw - 48)
    total_h = sum(th_val(draw, l, bf) + 6 for l in lines)
    ty = by + (BANNER_H - total_h) // 2
    for line in lines:
        put_center(draw, line, bx + bw // 2, ty, bf, color)  # texto na cor de destaque
        ty += th_val(draw, line, bf) + 6

    return by


# ============================================================================
# PILL
# Por padrao: fundo solido na cor, texto escuro (igual ao template de referencia)
# filled=False: apenas contorno (para uso interno em cards)
# ============================================================================
def draw_pill(draw, label, x, y, color, fnt=None, filled=True):
    """Desenha pill. Retorna (x_right, height)."""
    if fnt is None:
        fnt = font(True, 16)
    ph, pv = 12, 6
    lw     = tw(draw, label, fnt)
    lh     = th_val(draw, label, fnt)
    pw     = lw + ph * 2
    pill_h = lh + pv * 2

    if filled:
        draw.rounded_rectangle((x, y, x+pw, y+pill_h), radius=6, fill=color)
        put(draw, label, x + ph, y + pv, fnt, PILL_TXT)
    else:
        draw.rounded_rectangle((x, y, x+pw, y+pill_h),
                                radius=6, fill=tint(DARK_BG, color, 0.20),
                                outline=color, width=1)
        put(draw, label, x + ph, y + pv, fnt, color)

    return x + pw, pill_h


# ============================================================================
# TITULO COM UNDERLINE PROPORCIONAL
# ============================================================================
def draw_slide_title(draw, titulo, y, color, fnt_size=34, pill_label=None,
                     pill_color=None):
    """
    Desenha pill (opcional) + titulo + underline proporcional ao texto.
    Retorna y apos o underline.
    """
    if pill_label:
        pf = font(True, 16)
        _, ph = draw_pill(draw, pill_label, PAD, y, pill_color or color, pf)
        y += ph + 14

    title_f = font(True, fnt_size)
    first_line = wrap_lines(draw, titulo, title_f, W - 2*PAD)[0]
    underline_w = min(tw(draw, first_line, title_f), W - 2*PAD)

    y = draw_wrapped(draw, titulo, PAD, y, title_f, WHITE, W - 2*PAD, 4)
    draw.rounded_rectangle((PAD, y + 4, PAD + underline_w, y + 8),
                            radius=3, fill=color)
    return y + 22


# ============================================================================
# CIRCULOS DECORATIVOS (capa)
# ============================================================================
def draw_deco_circles(img, color):
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    r, g, b = hex_rgb(color)

    d.ellipse((-160, H-280, 160, H+100), fill=(r, g, b, 28))
    d.ellipse((-80,  H-180, 80,  H+20),  fill=(r, g, b, 18))
    d.ellipse((W-160, H-280, W+160, H+100), fill=(r, g, b, 22))
    d.ellipse((W-60, -60, W+120, 120),   fill=(r, g, b, 15))

    blurred = overlay.filter(ImageFilter.GaussianBlur(radius=50))
    img.paste(blurred, (0, 0), blurred)


# ============================================================================
# SLIDE 1: CAPA
# ============================================================================
def slide_capa(num, total, titulo_destaque, titulo_branco, subtitulo,
               pills, preview_cards, color, abstract=None):
    img  = Image.new("RGB", (W, H), BG)
    draw_deco_circles(img, color)
    draw = ImageDraw.Draw(img)
    draw_header(img, draw)

    y = HEADER_H + 16

    # Pills (fundo solido)
    if pills:
        pf     = font(True, 16)
        x      = PAD
        ph_max = 0
        for label in pills:
            x_right, ph = draw_pill(draw, label, x, y, color, pf, filled=True)
            ph_max = max(ph_max, ph)
            x = x_right + 10
        y += ph_max + 20

    # Titulo colorido
    tf = font(True, 52)
    if titulo_destaque:
        for line in titulo_destaque.split("\n"):
            y = draw_wrapped(draw, line, PAD, y, tf, color, W - 2*PAD, 4)
        y += 2

    # Titulo branco
    if titulo_branco:
        for line in titulo_branco.split("\n"):
            y = draw_wrapped(draw, line, PAD, y, tf, WHITE, W - 2*PAD, 4)

    # Underline proporcional
    first_line = wrap_lines(draw, titulo_branco or titulo_destaque or "", tf, W-2*PAD)[0]
    ul_w = min(tw(draw, first_line, tf), W - 2*PAD)
    draw.rounded_rectangle((PAD, y+6, PAD+ul_w, y+10), radius=3, fill=color)
    y += 26

    # Subtitulo
    if subtitulo:
        sf = font(False, 26)
        y  = draw_wrapped(draw, subtitulo, PAD, y, sf, GRAY, W - 2*PAD, 7)

    y += 28

    # Abstract highlight box (content-fit — sem preencher o espaco todo)
    if abstract:
        bx = PAD
        bw = W - 2 * PAD
        af    = font(True, 34)
        lines = wrap_lines(draw, abstract, af, bw - 80)
        lh    = sum(th_val(draw, l, af) + 12 for l in lines)
        box_h = lh + 36   # padding top + bottom

        draw.rounded_rectangle((bx, y, bx+bw, y+box_h),
                                radius=14, fill=tint(DARK_BG, color, 0.14))
        draw.rounded_rectangle((bx, y, bx+bw, y+box_h),
                                radius=14, outline=color, width=1)
        draw.rounded_rectangle((bx, y, bx+5, y+box_h), radius=2, fill=color)

        ay = y + 18
        for line in lines:
            put_center(draw, line, bx + bw//2, ay, af, WHITE)
            ay += th_val(draw, line, af) + 12

        y += box_h + 24

    # Preview cards posicionados acima do footer
    preview_h  = 200 if (preview_cards and len(preview_cards) >= 2) else 0
    footer_top = H - FOOTER_H - 14
    if preview_h:
        y = footer_top - preview_h - 8

    # Preview cards
    if preview_cards and len(preview_cards) >= 2:
        card_y = y
        card_w = (W - 2*PAD - 20) // 2
        card_h = 176
        gap    = 20
        arrow_x = PAD + card_w + gap // 2

        for i, pc in enumerate(preview_cards[:2]):
            cx       = PAD + i * (card_w + gap)
            pc_color = pc.get("cor", color)

            draw.rounded_rectangle((cx, card_y, cx+card_w, card_y+card_h),
                                   radius=12, fill=tint(DARK_BG, pc_color, 0.15))
            draw.rounded_rectangle((cx, card_y, cx+card_w, card_y+card_h),
                                   radius=12, outline=pc_color, width=1)

            if_fnt = font(True, 34)
            icon   = pc.get("icone", "")
            if icon:
                put_center(draw, icon, cx + card_w//2, card_y + 20, if_fnt, pc_color)

            tif = font(True, 22)
            put_center(draw, pc.get("titulo", ""), cx + card_w//2,
                       card_y + 76, tif, WHITE)

            sif = font(False, 18)
            for j, sub in enumerate(pc.get("subs", [])):
                put_center(draw, sub, cx + card_w//2,
                           card_y + 108 + j * 26, sif, GRAY)

        af = font(False, 28)
        put_center(draw, ">", arrow_x, card_y + card_h // 2 - 10, af, GRAY)

    draw_progress(draw, num, total, color)
    return img


# ============================================================================
# LAYOUT "numbered"
# Cards que preenchem toda a area com numero colorido + titulo + descricao
# ============================================================================
def slide_numbered(num, total, titulo, slide_pill, itens, banner_text, color):
    img  = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    draw_header(img, draw)

    banner_top = draw_banner(draw, banner_text, color, H - FOOTER_H - 8)
    y = draw_slide_title(draw, titulo, HEADER_H + 12, color,
                         fnt_size=34, pill_label=slide_pill, pill_color=color)

    area_h   = banner_top - y - 12
    n        = len(itens)
    card_gap = 12
    cw       = W - 2 * PAD

    num_f  = font(True, 38)
    tit_f  = font(True, 22)
    desc_f = font(False, 19)

    pill_f = font(True, 16)

    # Altura: max(natural, piso proporcional) para ~75% de preenchimento
    def _num_card_h_natural(item):
        num_str    = "01"
        nw_        = tw(draw, num_str, num_f)
        max_txt_w_ = cw - (PAD + 22 + nw_ + 20 - PAD) - 16
        t_h_ = th_val(draw, item.get("titulo","A"), tit_f) if item.get("titulo") else 0
        p_h_ = (th_val(draw, item.get("pill","x"), pill_f) + 10 + 8) if item.get("pill") else 0
        d_h_ = measure_wrapped(draw, item.get("texto",""), desc_f, max_txt_w_, 5) if item.get("texto") else 0
        gap_ = 6 if (item.get("titulo") and (item.get("pill") or item.get("texto"))) else 0
        return t_h_ + p_h_ + gap_ + d_h_ + 40

    target_fill = area_h * 3 // 4
    floor_h = max(80, (target_fill - card_gap * max(n-1, 0)) // max(n, 1))
    card_heights = [max(_num_card_h_natural(item), floor_h) for item in itens]

    for i, item in enumerate(itens):
        card_h = card_heights[i]
        cx     = PAD
        cy     = y + sum(card_heights[:i]) + card_gap * i

        draw.rounded_rectangle((cx, cy, cx+cw, cy+card_h),
                                radius=12, fill=CARD_BG)
        draw.rounded_rectangle((cx, cy, cx+4, cy+card_h),
                                radius=2, fill=color)

        # Numero na cor de destaque
        num_str = f"{i+1:02d}"
        nw      = tw(draw, num_str, num_f)
        nh      = th_val(draw, num_str, num_f)
        num_x   = cx + 22
        put(draw, num_str, num_x, cy + (card_h - nh) // 2, num_f, color)

        # Texto centralizado verticalmente
        tx        = num_x + nw + 20
        max_txt_w = cw - (tx - cx) - 16

        titulo_item = item.get("titulo", "")
        pill_item   = item.get("pill", "")
        pill_color  = item.get("pill_cor", color)
        desc_item   = item.get("texto", "")

        t_h    = th_val(draw, titulo_item or "A", tit_f) if titulo_item else 0
        p_h    = (th_val(draw, pill_item, pill_f) + 10 + 8) if pill_item else 0
        d_h    = measure_wrapped(draw, desc_item, desc_f, max_txt_w, 5) if desc_item else 0
        gap_td = 6 if (titulo_item and (pill_item or desc_item)) else 0
        block  = t_h + gap_td + p_h + d_h
        ty     = cy + (card_h - block) // 2

        if titulo_item:
            put(draw, titulo_item, tx, ty, tit_f, WHITE)
            ty += t_h + gap_td
        if pill_item:
            draw_pill(draw, pill_item, tx, ty, pill_color, pill_f, filled=True)
            ty += p_h
        if desc_item:
            draw_wrapped(draw, desc_item, tx, ty, desc_f, GRAY, max_txt_w, 5)

    draw_progress(draw, num, total, color)
    return img


# ============================================================================
# LAYOUT "categorias"
# Cards com pill de categoria (outlined) + bullet list
# ============================================================================
def _measure_categorias_card(draw, item, cw, label_f, bullet_f, card_pad=16):
    h = card_pad
    if item.get("label"):
        lh = th_val(draw, item["label"], label_f)
        h += lh + 6*2 + 12   # pill_h + gap
    for bullet in item.get("bullets", []):
        h += measure_wrapped(draw, bullet, bullet_f, cw - 52, 4) + 9
    h += card_pad
    return h


def slide_categorias(num, total, titulo, itens, banner_text, color):
    img  = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    draw_header(img, draw)

    banner_top = draw_banner(draw, banner_text, color, H - FOOTER_H - 8)
    y = draw_slide_title(draw, titulo, HEADER_H + 12, color, fnt_size=34)

    area_top  = y
    area_h    = banner_top - y - 12
    n         = len(itens)
    card_gap  = 16
    cw        = W - 2 * PAD
    card_pad  = 16
    bullet_f  = font(False, 20)
    label_f   = font(True, 17)

    natural_h = [_measure_categorias_card(draw, item, cw, label_f, bullet_f, card_pad)
                 for item in itens]

    for i, item in enumerate(itens):
        card_h     = natural_h[i]
        cx         = PAD
        cy         = area_top + sum(natural_h[:i]) + card_gap * i
        item_color = item.get("cor", color)

        draw.rounded_rectangle((cx, cy, cx+cw, cy+card_h),
                                radius=12, fill=tint(DARK_BG, item_color, 0.14))
        draw.rounded_rectangle((cx, cy, cx+cw, cy+card_h),
                                radius=12, outline=item_color, width=1)
        draw.rounded_rectangle((cx, cy, cx+4, cy+card_h),
                                radius=2, fill=item_color)

        iy = cy + card_pad

        label = item.get("label", "")
        if label:
            # pill outlined (nao solida) dentro do card
            _, pill_h = draw_pill(draw, label, cx + 18, iy, item_color, label_f,
                                  filled=False)
            iy += pill_h + 12

        for bullet in item.get("bullets", []):
            br = 4
            draw.ellipse((cx+18, iy+9, cx+18+br*2, iy+9+br*2), fill=item_color)
            iy = draw_wrapped(draw, bullet, cx+34, iy, bullet_f, WHITE, cw-52, 4)
            iy += 7

    draw_progress(draw, num, total, color)
    return img


# ============================================================================
# LAYOUT "timeline"
# Linha vertical + circulos + pill + titulo + descricao
# (ex: fluxo de etapas, sequencia de comandos)
# ============================================================================
def slide_timeline(num, total, titulo, slide_pill, itens, banner_text, color):
    """
    itens: [{"pill": str, "cor": str, "titulo": str, "desc": str}, ...]
    """
    img  = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    draw_header(img, draw)

    banner_top = draw_banner(draw, banner_text, color, H - FOOTER_H - 8)
    y = draw_slide_title(draw, titulo, HEADER_H + 12, color,
                         fnt_size=34, pill_label=slide_pill, pill_color=color)

    # Cards preenchem a area (igual a numbered) com circulo + linha na borda esquerda
    area_h   = banner_top - y - 12
    n        = len(itens)
    card_gap = 12
    card_h   = max(80, (area_h - card_gap * max(n-1, 0)) // max(n, 1))
    cw       = W - 2 * PAD

    pill_f = font(True, 17)
    tit_f  = font(True, 22)
    desc_f = font(False, 19)

    CR     = 10
    LINE_X = PAD + 2   # centro da linha/circulo na borda esquerda do card

    # Linha vertical conectando os centros dos cards
    if n > 1:
        line_top    = y + card_h // 2
        line_bottom = y + (n-1) * (card_h + card_gap) + card_h // 2
        draw.line([(LINE_X, line_top), (LINE_X, line_bottom)], fill=DIM_GRAY, width=2)

    for i, item in enumerate(itens):
        cx         = PAD
        cy         = y + i * (card_h + card_gap)
        item_color = item.get("cor", color)

        draw.rounded_rectangle((cx, cy, cx+cw, cy+card_h), radius=12, fill=CARD_BG)
        draw.rounded_rectangle((cx, cy, cx+5, cy+card_h), radius=2, fill=item_color)

        # Circulo sobre a borda do card
        cc = cy + card_h // 2
        draw.ellipse((LINE_X-CR, cc-CR, LINE_X+CR, cc+CR), fill=item_color)

        plab = item.get("pill", "")
        tlab = item.get("titulo", "")
        dlab = item.get("desc", "")

        tx = cx + 30
        if plab:
            pill_cy = cy + (card_h - (th_val(draw, plab, pill_f) + 12)) // 2
            x_right, _ = draw_pill(draw, plab, tx, pill_cy, item_color, pill_f, filled=True)
            tx = x_right + 16

        max_txt_w = cw - (tx - cx) - 16
        t_h = th_val(draw, tlab or "A", tit_f) if tlab else 0
        d_h = measure_wrapped(draw, dlab, desc_f, max_txt_w, 4) if dlab else 0
        gap = 6 if (tlab and dlab) else 0
        ty  = cy + (card_h - (t_h + gap + d_h)) // 2

        if tlab:
            put(draw, tlab, tx, ty, tit_f, WHITE)
            ty += t_h + gap
        if dlab:
            draw_wrapped(draw, dlab, tx, ty, desc_f, GRAY, max_txt_w, 4)

    draw_progress(draw, num, total, color)
    return img


# ============================================================================
# LAYOUT "comparativo"
# Dois cards lado a lado (ex: EVITE vs FACA, Sem vs Com)
# ============================================================================
def slide_comparativo(num, total, titulo, slide_pill, esquerda, direita,
                      banner_text, color):
    """
    esquerda / direita:
      {"titulo": str, "cor": str, "itens": [str, ...], "prefixo": "x" | "+" | ""}
    """
    img  = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    draw_header(img, draw)

    banner_top = draw_banner(draw, banner_text, color, H - FOOTER_H - 8)
    y = draw_slide_title(draw, titulo, HEADER_H + 12, color,
                         fnt_size=34, pill_label=slide_pill, pill_color=color)

    area_h = banner_top - y - 12
    cw     = W - 2 * PAD
    tit_f  = font(True, 22)
    item_f = font(False, 19)
    pref_f = font(True, 22)
    card_gap = 16

    # Altura natural de cada card (content-fit)
    def _side_natural_h(side):
        lbl_f = font(True, 17)
        lh    = th_val(draw, side.get("titulo", ""), lbl_f) + 6*2 + 12
        ih    = sum(measure_wrapped(draw, t, item_f, cw - 56, 5) + 10
                    for t in side.get("itens", []))
        return 16 + lh + 4 + ih + 16

    n1 = _side_natural_h(esquerda)
    n2 = _side_natural_h(direita)
    # cada card ocupa metade do espaco disponivel, no minimo sua altura natural
    half_h  = (area_h - card_gap) // 2
    card_h1 = max(n1, half_h)
    card_h2 = max(n2, half_h)

    for idx, (side, card_h) in enumerate([(esquerda, card_h1), (direita, card_h2)]):
        cx         = PAD
        cy         = y + idx * (card_h1 + card_gap) if idx == 1 else y
        side_color = side.get("cor", color)

        draw.rounded_rectangle((cx, cy, cx+cw, cy+card_h),
                                radius=12, fill=tint(DARK_BG, side_color, 0.16))
        draw.rounded_rectangle((cx, cy, cx+cw, cy+card_h),
                                radius=12, outline=side_color, width=1)
        draw.rounded_rectangle((cx, cy, cx+4, cy+card_h),
                                radius=2, fill=side_color)

        # Label outlined (pill)
        lbl_f  = font(True, 17)
        iy     = cy + 16
        label  = side.get("titulo", "")
        if label:
            _, lh = draw_pill(draw, label, cx + 18, iy, side_color, lbl_f, filled=False)
            iy += lh + 10

        # Itens
        prefixo = side.get("prefixo", "")
        for item_txt in side.get("itens", []):
            row_h = measure_wrapped(draw, item_txt, item_f, cw - 56, 5)
            if prefixo:
                pref_color = "#ff6b6b" if prefixo == "x" else side_color
                put(draw, prefixo, cx + 18, iy, pref_f, pref_color)
            tx = cx + 44
            draw_wrapped(draw, item_txt, tx, iy, item_f, WHITE, cw - 60, 5)
            iy += row_h + 10

    draw_progress(draw, num, total, color)
    return img


# ============================================================================
# LAYOUT "grade"
# 4 itens em grade 2x2; item[0] com destaque
# itens: [{"titulo", "texto", "pill"(opt), "destaque"(bool opt)}, ...]
# ============================================================================
# LAYOUT "checklist"
# Itens com checkmark, sem card background — visual limpo de revisao/lista
# itens: [str, ...] ou [{"texto": str, "check": bool(opt, default True)}, ...]
# ============================================================================
def slide_checklist(num, total, titulo, slide_pill, itens, banner_text, color):
    img  = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    draw_header(img, draw)

    banner_top = draw_banner(draw, banner_text, color, H - FOOTER_H - 8)
    y = draw_slide_title(draw, titulo, HEADER_H + 12, color,
                         fnt_size=34, pill_label=slide_pill, pill_color=color)

    cw      = W - 2 * PAD
    item_f  = font(False, 22)
    row_gap = 20
    box_s   = 24   # tamanho do quadrado do checkmark

    def draw_checkmark(cx, cy, c):
        draw.rounded_rectangle((cx, cy, cx+box_s, cy+box_s), radius=4, fill=c)
        # V shape em branco dentro do quadrado
        mx, my = cx + box_s//2, cy + box_s - 6
        lx = cx + 5
        draw.line([(lx, my-4), (mx-2, my), (cx+box_s-5, cy+7)],
                  fill=BG, width=2)

    for item in itens:
        if isinstance(item, str):
            txt, checked = item, True
        else:
            txt, checked = item.get("texto", ""), item.get("check", True)

        check_color = color if checked else DIM_GRAY
        txt_color   = WHITE if checked else GRAY

        # Linha separadora acima
        draw.line([(PAD, y), (PAD + cw, y)], fill=tint(BG, color, 0.35), width=1)
        y += 16

        # Checkmark box
        draw_checkmark(PAD + 4, y + 2, check_color)

        # Texto alinhado com o centro do box
        tx    = PAD + box_s + 20
        row_h = measure_wrapped(draw, txt, item_f, cw - box_s - 24, 5)
        draw_wrapped(draw, txt, tx, y, item_f, txt_color, cw - box_s - 24, 5)
        y += max(row_h, box_s + 4) + row_gap

    draw_progress(draw, num, total, color)
    return img


# ============================================================================
def slide_grade(num, total, titulo, slide_pill, itens, banner_text, color):
    img  = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    draw_header(img, draw)

    banner_top = draw_banner(draw, banner_text, color, H - FOOTER_H - 8)
    y = draw_slide_title(draw, titulo, HEADER_H + 12, color,
                         fnt_size=34, pill_label=slide_pill, pill_color=color)

    area_h   = banner_top - y - 12
    gap      = 16
    card_w   = (W - 2*PAD - gap) // 2
    card_h   = (area_h - gap) // 2

    num_f  = font(True, 32)
    tit_f  = font(True, 20)
    desc_f = font(False, 17)
    pill_f = font(True, 14)

    for idx, item in enumerate(itens[:4]):
        row    = idx // 2
        col    = idx % 2
        cx     = PAD + col * (card_w + gap)
        cy     = y + row * (card_h + gap)

        destaque    = item.get("destaque", idx == 0)
        item_color  = item.get("cor", color)
        fill_alpha  = 0.22 if destaque else 0.10
        border_w    = 2 if destaque else 1

        draw.rounded_rectangle((cx, cy, cx+card_w, cy+card_h),
                                radius=12, fill=tint(DARK_BG, item_color, fill_alpha))
        draw.rounded_rectangle((cx, cy, cx+card_w, cy+card_h),
                                radius=12, outline=item_color, width=border_w)

        # Numero
        num_str = str(idx + 1)
        nw = tw(draw, num_str, num_f)
        put(draw, num_str, cx + 16, cy + 14, num_f, item_color)

        # Conteudo a direita do numero
        tx     = cx + 16 + nw + 12
        tw_max = card_w - (tx - cx) - 12
        iy     = cy + 14

        tit = item.get("titulo", "")
        if tit:
            put(draw, tit, tx, iy, tit_f, WHITE)
            iy += th_val(draw, tit, tit_f) + 6

        plab = item.get("pill", "")
        if plab:
            _, ph = draw_pill(draw, plab, tx, iy, item_color, pill_f, filled=True)
            iy += ph + 8

        desc = item.get("texto", "")
        if desc:
            draw_wrapped(draw, desc, tx, iy, desc_f, GRAY, tw_max, 4)

    draw_progress(draw, num, total, color)
    return img


# ============================================================================
# SLIDE 8: CTA
# ============================================================================
def slide_cta(num, total, pergunta, detalhe, color, cta_botao=None):
    img  = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    draw_header(img, draw)

    ct     = HEADER_H + 20
    cb     = H - FOOTER_H - 20
    avail  = cb - ct
    card_h = int(avail * 0.64)
    cx     = PAD
    cw     = W - 2 * PAD
    cy     = ct + (avail - card_h) // 2

    draw.rounded_rectangle((cx, cy, cx+cw, cy+card_h),
                            radius=14, fill=CARD_BG)
    draw.rounded_rectangle((cx, cy, cx+cw, cy+card_h),
                            radius=14, outline=color, width=1)

    sv_bold_f = font(True, 36)
    sv_sub_f  = font(False, 22)
    q_f       = font(True, 34)
    d_f       = font(False, 22)
    btn_f     = font(True, 22)
    sig_f     = font(False, 20)
    sig_b_f   = font(True, 20)

    sv_h   = th_val(draw, "Salva esse post", sv_bold_f)
    sub_h  = th_val(draw, "para consultar depois.", sv_sub_f)
    q_h    = measure_wrapped(draw, pergunta, q_f, cw-80, 10)
    d_h    = measure_wrapped(draw, detalhe, d_f, cw-80, 8) if detalhe else 0
    btn_h  = (th_val(draw, cta_botao or "x", btn_f) + 22) if cta_botao else 0
    sig_h  = th_val(draw, "Matheus Zacche", sig_b_f) + 6 + th_val(draw, "Analista de Dados", sig_f)
    gap    = 24

    total_h = (sv_h + 8 + sub_h + gap + 1 + gap +
               q_h + (gap//2 + d_h if detalhe else 0) +
               (gap + btn_h if cta_botao else 0) +
               gap + 1 + gap + sig_h)
    iy = cy + (card_h - total_h) // 2
    if iy < cy + 20:
        iy = cy + 20

    # "Salva esse post"
    put_center(draw, "Salva esse post", cx + cw//2, iy, sv_bold_f, WHITE)
    iy += sv_h + 8
    put_center(draw, "para consultar depois.", cx + cw//2, iy, sv_sub_f, GRAY)
    iy += sub_h + gap

    draw.line([(cx+60, iy), (cx+cw-60, iy)], fill=tint(BG, color, 0.50), width=1)
    iy += 1 + gap

    iy = draw_wrapped_center(draw, pergunta, cx+cw//2, iy, q_f, color, cw-80, 10)

    if detalhe:
        iy += gap // 2
        iy = draw_wrapped_center(draw, detalhe, cx+cw//2, iy, d_f, GRAY, cw-80, 8)

    # Botao outlined
    if cta_botao:
        iy += gap
        bw    = tw(draw, cta_botao, btn_f) + 80
        bh    = th_val(draw, cta_botao, btn_f) + 22
        bx    = cx + (cw - bw) // 2
        draw.rounded_rectangle((bx, iy, bx+bw, iy+bh), radius=bh//2,
                                outline=color, width=2)
        put_center(draw, cta_botao, bx + bw//2, iy + (bh - th_val(draw, cta_botao, btn_f))//2,
                   btn_f, WHITE)
        iy += bh

    iy += gap
    draw.line([(cx+60, iy), (cx+cw-60, iy)], fill=tint(BG, color, 0.40), width=1)
    iy += 1 + gap

    put_center(draw, "Matheus Zacche", cx + cw//2, iy, sig_b_f, color)
    iy += th_val(draw, "Matheus Zacche", sig_b_f) + 6
    put_center(draw, "Analista de Dados", cx + cw//2, iy, sig_f, GRAY)

    draw_progress(draw, num, total, color)
    return img


# ============================================================================
# FUNCAO PRINCIPAL
# ============================================================================
def gerar_carrossel(titulo_destaque, titulo_branco, subtitulo,
                    pills, slides_conteudo, cta_pergunta, cta_detalhe,
                    capa_preview=None, capa_abstract=None,
                    theme_color="#00d4aa", output_name="carrossel",
                    cta_botao=None):
    """
    Gera carrossel de 8 slides + PDF.

    slides_conteudo: lista de ate 6 dicts. Cada dict tem "layout" + campos proprios:

      "numbered" (default):
        {"titulo", "pill"(opt), "banner", "itens": [{"titulo", "texto"}, ...]}

      "categorias":
        {"titulo", "banner", "layout":"categorias",
         "itens": [{"label", "cor", "bullets":[str,...]}, ...]}

      "timeline":
        {"titulo", "pill"(opt), "banner", "layout":"timeline",
         "itens": [{"pill", "cor", "titulo", "desc"}, ...]}

      "comparativo":
        {"titulo", "pill"(opt), "banner", "layout":"comparativo",
         "esquerda": {"titulo", "cor", "itens":[str,...], "prefixo":"x"|"+"|""},
         "direita":  {"titulo", "cor", "itens":[str,...], "prefixo":"x"|"+"|""}}
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    total  = 8
    images = []

    images.append(slide_capa(
        1, total,
        titulo_destaque, titulo_branco, subtitulo,
        pills, capa_preview or [], theme_color,
        abstract=capa_abstract
    ))

    for i, s in enumerate(slides_conteudo[:6]):
        layout = s.get("layout", "numbered")
        n      = i + 2

        if layout == "categorias":
            images.append(slide_categorias(
                n, total, s["titulo"], s.get("itens", []),
                s.get("banner", ""), theme_color))

        elif layout == "timeline":
            images.append(slide_timeline(
                n, total, s["titulo"], s.get("pill", ""),
                s.get("itens", []), s.get("banner", ""), theme_color))

        elif layout == "comparativo":
            images.append(slide_comparativo(
                n, total, s["titulo"], s.get("pill", ""),
                s.get("esquerda", {}), s.get("direita", {}),
                s.get("banner", ""), theme_color))

        elif layout == "grade":
            images.append(slide_grade(
                n, total, s["titulo"], s.get("pill", ""),
                s.get("itens", []), s.get("banner", ""), theme_color))

        elif layout == "checklist":
            images.append(slide_checklist(
                n, total, s["titulo"], s.get("pill", ""),
                s.get("itens", []), s.get("banner", ""), theme_color))

        else:  # numbered
            images.append(slide_numbered(
                n, total, s["titulo"], s.get("pill", ""),
                s.get("itens", []), s.get("banner", ""), theme_color))

    while len(images) < 7:
        images.append(slide_numbered(
            len(images)+1, total, "...", "", [], "...", theme_color))

    images.append(slide_cta(8, total, cta_pergunta, cta_detalhe, theme_color, cta_botao=cta_botao))

    png_paths = []
    for i, img in enumerate(images):
        path = os.path.join(OUTPUT_DIR, f"{output_name}_slide_{i+1}.png")
        img.save(path, "PNG")
        png_paths.append(path)

    pdf_path = os.path.join(OUTPUT_DIR, f"{output_name}.pdf")
    rgb = [img.convert("RGB") for img in images]
    rgb[0].save(pdf_path, "PDF", save_all=True, append_images=rgb[1:])

    print(f"Carrossel gerado: {len(png_paths)} slides | {pdf_path}")
    return pdf_path, png_paths


# ============================================================================
# TESTE — carrossel Python + N8N com todos os layouts
# ============================================================================
if __name__ == "__main__":
    gerar_carrossel(
        titulo_destaque="Python + N8N",
        titulo_branco="Como integrar tratamento\nde dados com automacao",
        subtitulo="Quando usar cada um e como faze-los trabalhar juntos",
        pills=["PYTHON", "N8N", "AUTOMACAO"],
        capa_abstract="Cada ferramenta no que faz melhor. Dados no Python. Fluxo no N8N.",
        capa_preview=[
            {"icone": "{}", "titulo": "Python",
             "subs": ["Dados", "Transformacao"], "cor": "#4a9eff"},
            {"icone": "[>>]", "titulo": "N8N",
             "subs": ["Fluxo", "Automacao"], "cor": "#00d4aa"},
        ],
        slides_conteudo=[
            # Slide 2 — categorias
            {
                "layout": "categorias",
                "titulo": "O papel de cada um",
                "banner": "Python e o cerebro. N8N e o sistema nervoso.",
                "itens": [
                    {"label": "PYTHON", "cor": "#4a9eff", "bullets": [
                        "Limpeza e tratamento de dados",
                        "Calculos e transformacoes complexas",
                        "Leitura de arquivos (CSV, Excel, JSON)",
                        "Conexao com bancos de dados",
                        "Analise e modelagem",
                    ]},
                    {"label": "N8N", "cor": "#00d4aa", "bullets": [
                        "Conexao entre sistemas e APIs",
                        "Triggers automaticos (horario, webhook)",
                        "Envio de e-mails e notificacoes",
                        "Orquestracao sem codigo",
                    ]},
                ],
            },
            # Slide 3 — numbered
            {
                "titulo": "Quando usar Python",
                "pill": "PYTHON",
                "banner": "Use Python quando o problema esta nos dados.",
                "itens": [
                    {"titulo": "Tratar dados sujos",
                     "texto": "Normalizar colunas, remover duplicatas, converter tipos com Pandas"},
                    {"titulo": "Calculos complexos",
                     "texto": "Formulas, agregacoes, estatisticas alem do basico"},
                    {"titulo": "Processar arquivos",
                     "texto": "Ler e transformar CSV, Excel, JSON, conectar bancos SQL"},
                    {"titulo": "Logica customizada",
                     "texto": "Regras de negocio especificas que nao existem em nos prontos"},
                ],
            },
            # Slide 4 — checklist
            {
                "layout": "checklist",
                "titulo": "Antes de publicar, confira",
                "banner": "Dashboard bom e dashboard util sao coisas diferentes.",
                "itens": [
                    "KPI principal no canto superior esquerdo?",
                    "Informacoes de cima pra baixo (resumo > detalhe)?",
                    "Tamanho dos elementos reflete a importancia?",
                    "Cores usadas com proposito, nao decoracao?",
                    "Tem espaco em branco suficiente?",
                    "O usuario sabe pra onde olhar primeiro?",
                ],
            },
            # Slide 5 — timeline (fluxo real, antes era numbered)
            {
                "layout": "timeline",
                "titulo": "Exemplo de fluxo real",
                "banner": "Cada ferramenta no que faz melhor.",
                "itens": [
                    {"pill": "N8N",    "cor": "#00d4aa",
                     "titulo": "Agenda a execucao",
                     "desc":   "Todo dia as 8h ou via webhook externo"},
                    {"pill": "N8N",    "cor": "#00d4aa",
                     "titulo": "Busca os dados",
                     "desc":   "API, banco de dados ou arquivo CSV"},
                    {"pill": "PYTHON", "cor": "#4a9eff",
                     "titulo": "Processa e transforma",
                     "desc":   "Limpeza, calculos e agregacoes com Pandas"},
                    {"pill": "N8N",    "cor": "#00d4aa",
                     "titulo": "Distribui o resultado",
                     "desc":   "E-mail, Sheets, Slack ou dashboard"},
                ],
            },
            # Slide 6 — numbered (3 formas)
            {
                "titulo": "3 formas de integrar",
                "banner": "Dados no Python, acao automatizada no N8N.",
                "itens": [
                    {"titulo": "Code Node",
                     "pill": "Simples", "pill_cor": "#00d4aa",
                     "texto": "Escreve Python direto dentro do N8N. Para transformacoes simples."},
                    {"titulo": "Execute Command",
                     "pill": "Intermediario", "pill_cor": "#4a9eff",
                     "texto": "N8N chama um script .py externo pelo terminal."},
                    {"titulo": "API via FastAPI",
                     "pill": "Avancado", "pill_cor": "#a855f7",
                     "texto": "Python roda como API separada. N8N consome via HTTP Request."},
                ],
            },
            # Slide 7 — comparativo (regra de ouro)
            {
                "layout": "comparativo",
                "titulo": "A regra de ouro",
                "banner": "Python para dados. N8N para fluxo.",
                "esquerda": {
                    "titulo":  "EVITE",
                    "cor":     "#ff6b6b",
                    "prefixo": "x",
                    "itens": [
                        "Fazer tudo no N8N (fluxo fragil e gigante)",
                        "Fazer tudo no Python (perde orquestracao visual)",
                        "Misturar logica de dados com logica de fluxo",
                    ],
                },
                "direita": {
                    "titulo":  "FACA",
                    "cor":     "#00d4aa",
                    "prefixo": "+",
                    "itens": [
                        "Python cuida dos dados: tratar, calcular, transformar",
                        "N8N cuida do fluxo: agendar, conectar, distribuir",
                        "Cada ferramenta no que faz melhor",
                    ],
                },
            },
        ],
        cta_pergunta="Voce ja usa Python e N8N juntos?",
        cta_detalhe="Conta nos comentarios como voce faz a integracao",
        cta_botao="Comenta qual metodo voce usa!",
        theme_color="#00d4aa",
        output_name="carrossel_test"
    )
