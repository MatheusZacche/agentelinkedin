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
BANNER_H = 76

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
    # Checkmark desenhado com linhas (NotoSans nao tem o caractere ✓)
    # Ponto medio (p1), canto baixo (p2), canto alto direito (p3)
    p1 = (bcx - 5, bcy)
    p2 = (bcx - 1, bcy + 4)
    p3 = (bcx + 6, bcy - 5)
    draw.line([p1, p2, p3], fill=WHITE, width=2)

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
# FILL VERTICAL DE CARDS — preenchem toda a area disponivel
# ============================================================================
def _fill_cards(y_start, area_h, n, card_gap=12):
    """
    Divide area_h em n cards iguais com card_gap entre eles.
    Retorna (card_h, lista de posicoes y).
    Cards preenchem exatamente a area — sem espaco morto.
    """
    if n == 0:
        return 0, []
    card_h = (area_h - card_gap * (n - 1)) // n
    card_h = max(card_h, 60)
    positions = [y_start + i * (card_h + card_gap) for i in range(n)]
    return card_h, positions


def _fill_cards_proportional(y_start, area_h, content_h_list, card_gap=12):
    """
    Distribui area_h entre cards com altura proporcional ao conteudo.
    Util para categorias/comparativo onde os cards tem conteudos muito diferentes.
    """
    n = len(content_h_list)
    if n == 0:
        return [], []
    total_content = sum(content_h_list) or 1
    available = area_h - card_gap * (n - 1)
    card_heights = [max(int(available * h / total_content), 60) for h in content_h_list]
    # Ajustar ultimo card para fechar exatamente
    diff = available - sum(card_heights)
    card_heights[-1] += diff
    positions = []
    cy = y_start
    for h in card_heights:
        positions.append(cy)
        cy += h + card_gap
    return card_heights, positions


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

    bf    = font(True, 27)
    lines = wrap_lines(draw, text, bf, bw - 48)
    line_h  = th_val(draw, lines[0] if lines else "x", bf)
    total_h = line_h * len(lines) + 6 * max(0, len(lines) - 1)
    ty = by + (BANNER_H - total_h) // 2
    for line in lines:
        put_center(draw, line, bx + bw // 2, ty, bf, color)  # texto na cor de destaque
        ty += line_h + 6

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
    lw        = tw(draw, label, fnt)
    lh_ref    = th_val(draw, "PYTHON", fnt)  # altura de referencia sem acentos — forma consistente
    lh_actual = th_val(draw, label, fnt)     # altura real do texto do label
    pw        = lw + ph * 2
    pill_h    = lh_ref + pv * 2
    text_y    = y + (pill_h - lh_actual) // 2  # centraliza texto real dentro da forma fixa

    if filled:
        draw.rounded_rectangle((x, y, x+pw, y+pill_h), radius=6, fill=color)
        put(draw, label, x + ph, text_y, fnt, PILL_TXT)
    else:
        draw.rounded_rectangle((x, y, x+pw, y+pill_h),
                                radius=6, fill=tint(DARK_BG, color, 0.20),
                                outline=color, width=1)
        put(draw, label, x + ph, text_y, fnt, color)

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
        pf = font(True, 19)
        _, ph = draw_pill(draw, pill_label, PAD, y, pill_color or color, pf)
        y += ph + 28

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
               pills, preview_cards, color, abstract=None, watermark=None,
               capa_index=None):
    img  = Image.new("RGB", (W, H), BG)
    draw_deco_circles(img, color)

    # Watermark decorativo (ex: "5") — posicionado na metade inferior do slide
    if watermark:
        wm_draw = ImageDraw.Draw(img)
        wm_f    = font(True, 420)
        wm_col  = tint(BG, color, 0.08)
        wm_w    = tw(wm_draw, watermark, wm_f)
        put(wm_draw, watermark, W - wm_w + 70, int(H * 0.42), wm_f, wm_col)

    draw = ImageDraw.Draw(img)
    draw_header(img, draw)

    # --- Medir altura total do bloco de titulo para centralizar verticalmente ---
    _tf = font(True, 52)
    _sf = font(False, 26)
    _pf_m = font(True, 16)

    title_block_h = 0
    if pills:
        _ph_row = th_val(draw, pills[0], _pf_m) + 12 + 20
        title_block_h += _ph_row
    if titulo_destaque:
        for _line in titulo_destaque.split("\n"):
            title_block_h += measure_wrapped(draw, _line, _tf, W - 2*PAD, 4)
    if titulo_branco:
        for _line in titulo_branco.split("\n"):
            title_block_h += measure_wrapped(draw, _line, _tf, W - 2*PAD, 4)
    title_block_h += 26  # underline + gap
    if subtitulo:
        title_block_h += measure_wrapped(draw, subtitulo, _sf, W - 2*PAD, 7)
    title_block_h += 16  # trailing gap (reduced from 28)

    # Espaco disponivel antes do abstract/preview
    _preview_h_est = 460 if (preview_cards and len(preview_cards) >= 2) else 0
    _footer_top_est = H - FOOTER_H - 14
    if abstract:
        _af_m = font(True, 34)
        _bw_m = W - 2 * PAD
        _abs_lines = wrap_lines(draw, abstract, _af_m, _bw_m - 80)
        _abs_lh = sum(th_val(draw, _l, _af_m) + 12 for _l in _abs_lines)
        _box_h_est = _abs_lh + 36
        _box_bot_est = (_footer_top_est - _preview_h_est - 16) if _preview_h_est else (_footer_top_est - 8)
        _avail_bottom = _box_bot_est - _box_h_est - 16
    elif _preview_h_est:
        _avail_bottom = _footer_top_est - _preview_h_est - 8
    else:
        _avail_bottom = _footer_top_est - 8

    # Titulo ancorado ao topo (nao centralizado verticalmente)
    y = HEADER_H + 32

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

    # Abstract + preview cards: âncora no rodapé para evitar espaço no meio
    preview_h  = 460 if (preview_cards and len(preview_cards) >= 2) else 0
    footer_top = H - FOOTER_H - 14

    if abstract:
        bx = PAD
        bw = W - 2 * PAD
        af      = font(True, 34)
        lines   = wrap_lines(draw, abstract, af, bw - 80)
        line_h  = th_val(draw, lines[0] if lines else "x", af)
        gap_ln  = 12
        text_h  = line_h * len(lines) + gap_ln * max(0, len(lines) - 1)
        box_pad = 28
        box_h   = text_h + box_pad * 2

        # Box posicionado logo abaixo do titulo, sempre
        box_y = y + 28

        draw.rounded_rectangle((bx, box_y, bx+bw, box_y+box_h),
                                radius=14, fill=tint(DARK_BG, color, 0.14))
        draw.rounded_rectangle((bx, box_y, bx+bw, box_y+box_h),
                                radius=14, outline=color, width=1)
        draw.rounded_rectangle((bx, box_y, bx+5, box_y+box_h), radius=2, fill=color)

        ay = box_y + (box_h - text_h) // 2
        for line in lines:
            put_center(draw, line, bx + bw//2, ay, af, WHITE)
            ay += line_h + gap_ln

    if preview_h:
        if abstract:
            y = box_y + box_h + 24  # logo abaixo do abstract
        else:
            y = footer_top - preview_h - 8

    # Preview cards
    if preview_cards and len(preview_cards) >= 2:
        card_y = y
        card_w = (W - 2*PAD - 20) // 2
        card_h = 424
        gap    = 20
        arrow_x = PAD + card_w + gap // 2

        for i, pc in enumerate(preview_cards[:2]):
            cx       = PAD + i * (card_w + gap)
            pc_color = pc.get("cor", color)

            draw.rounded_rectangle((cx, card_y, cx+card_w, card_y+card_h),
                                   radius=12, fill=tint(DARK_BG, pc_color, 0.15))
            draw.rounded_rectangle((cx, card_y, cx+card_w, card_y+card_h),
                                   radius=12, outline=pc_color, width=1)

            # Centralizar conteudo verticalmente no card — fontes maiores
            if_fnt  = font(True, 72)
            tif     = font(True, 42)
            sif     = font(False, 30)
            icon    = pc.get("icone", "")
            icon_h  = th_val(draw, icon or "x", if_fnt)
            tit_h   = th_val(draw, pc.get("titulo", "x"), tif)
            subs    = pc.get("subs", [])
            subs_h  = len(subs) * (th_val(draw, subs[0] if subs else "x", sif) + 10)
            content_h = icon_h + 24 + tit_h + 18 + subs_h
            iy = card_y + (card_h - content_h) // 2

            if icon:
                put_center(draw, icon, cx + card_w//2, iy, if_fnt, pc_color)
            iy += icon_h + 24
            put_center(draw, pc.get("titulo", ""), cx + card_w//2, iy, tif, WHITE)
            iy += tit_h + 18
            for sub in subs:
                put_center(draw, sub, cx + card_w//2, iy, sif, GRAY)
                iy += th_val(draw, sub, sif) + 10

        af = font(False, 32)
        put_center(draw, ">", arrow_x, card_y + card_h // 2 - 12, af, GRAY)

    # Preview das automacoes — mini cards de apresentacao (nao sumario)
    if capa_index:
        ix_top   = (box_y + box_h + 24) if abstract else (y + 28)
        num_f    = font(True, 19)
        tit_f    = font(False, 20)
        cw       = W - 2 * PAD
        n_items  = len(capa_index)

        # Altura natural do card: linha de texto + padding interno
        card_pad_v = 14
        _row_txt_h = max(th_val(draw, "01", num_f), th_val(draw, "Texto", tit_f))
        card_h_idx = _row_txt_h + card_pad_v * 2

        # Distribuir espaco disponivel uniformemente
        avail   = (H - FOOTER_H - 14) - ix_top - 8
        total_c = card_h_idx * n_items
        gap_idx = max(6, (avail - total_c) // (n_items + 1))

        iy = ix_top + gap_idx
        for item in capa_index:
            item_color = item.get("cor", color)
            num_txt    = item.get("numero", "")
            tit_txt    = item.get("titulo", "")

            # Card sutil
            draw.rounded_rectangle((PAD, iy, PAD + cw, iy + card_h_idx),
                                    radius=10, fill=tint(DARK_BG, item_color, 0.07))
            draw.rounded_rectangle((PAD, iy, PAD + cw, iy + card_h_idx),
                                    radius=10, outline=tint(BG, item_color, 0.18), width=1)
            # Borda esquerda na cor do item
            draw.rounded_rectangle((PAD, iy, PAD + 4, iy + card_h_idx),
                                    radius=2, fill=item_color)

            # Numero e titulo centralizados verticalmente no card
            txt_y = iy + (card_h_idx - _row_txt_h) // 2
            nw    = tw(draw, num_txt, num_f)
            put(draw, num_txt, PAD + 18, txt_y, num_f, item_color)
            put(draw, tit_txt, PAD + 18 + nw + 14, txt_y + (_row_txt_h - th_val(draw, tit_txt, tit_f)) // 2,
                tit_f, WHITE)

            iy += card_h_idx + gap_idx

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

    num_f  = font(True, 46)
    tit_f  = font(True, 28)
    desc_f = font(False, 25)

    pill_f = font(True, 20)

    # Cards preenchem toda a area — sem espaco morto
    card_h, card_positions = _fill_cards(y, area_h, n, card_gap)

    for i, item in enumerate(itens):
        cx = PAD
        cy = card_positions[i]

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
    bullet_f  = font(False, 26)
    label_f   = font(True, 20)

    natural_h = [_measure_categorias_card(draw, item, cw, label_f, bullet_f, card_pad)
                 for item in itens]
    # Cards preenchem toda a area — sem espaco morto
    card_h, card_positions = _fill_cards(area_top, area_h, n, card_gap)

    for i, item in enumerate(itens):
        cx         = PAD
        cy         = card_positions[i]
        item_color = item.get("cor", color)

        draw.rounded_rectangle((cx, cy, cx+cw, cy+card_h),
                                radius=12, fill=tint(DARK_BG, item_color, 0.14))
        draw.rounded_rectangle((cx, cy, cx+cw, cy+card_h),
                                radius=12, outline=item_color, width=1)
        draw.rounded_rectangle((cx, cy, cx+4, cy+card_h),
                                radius=2, fill=item_color)

        # Centralizar conteudo verticalmente no card
        iy = cy + max(card_pad, (card_h - natural_h[i]) // 2)

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
    cw       = W - 2 * PAD
    pill_f_m = font(True, 20)
    tit_f_m  = font(True, 28)
    desc_f_m = font(False, 25)

    # Cards preenchem toda a area — sem espaco morto
    card_h, card_positions_tl = _fill_cards(y, area_h, n, card_gap)
    card_h_list = [card_h] * n

    pill_f = font(True, 20)
    tit_f  = font(True, 28)
    desc_f = font(False, 25)

    CR     = 10
    LINE_X = PAD + 2   # centro da linha/circulo na borda esquerda do card

    # Linha vertical conectando os centros dos cards
    if n > 1:
        line_top    = card_positions_tl[0] + card_h // 2
        line_bottom = card_positions_tl[-1] + card_h // 2
        draw.line([(LINE_X, line_top), (LINE_X, line_bottom)], fill=DIM_GRAY, width=2)

    for i, item in enumerate(itens):
        cx         = PAD
        cy         = card_positions_tl[i]
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

    area_h   = banner_top - y - 12
    cw       = W - 2 * PAD
    lbl_f    = font(True, 26)
    item_f   = font(False, 44)
    pref_f   = font(True, 44)
    card_gap = 16
    item_gap = 20

    # Preencher area completa com cards de altura igual
    card_h, card_positions = _fill_cards(y, area_h, 2, card_gap)

    for idx, side in enumerate([esquerda, direita]):
        cx         = PAD
        cy         = card_positions[idx]
        side_color = side.get("cor", color)

        draw.rounded_rectangle((cx, cy, cx+cw, cy+card_h),
                                radius=12, fill=tint(DARK_BG, side_color, 0.16))
        draw.rounded_rectangle((cx, cy, cx+cw, cy+card_h),
                                radius=12, outline=side_color, width=1)
        draw.rounded_rectangle((cx, cy, cx+4, cy+card_h),
                                radius=2, fill=side_color)

        label   = side.get("titulo", "")
        prefixo = side.get("prefixo", "")
        itens   = side.get("itens", [])

        item_hs  = [measure_wrapped(draw, t, item_f, cw - 76, 5) for t in itens]
        pill_h   = (th_val(draw, label, lbl_f) + 6*2) if label else 0
        gap_pill = 20

        block_h = (pill_h + gap_pill if label else 0) + sum(item_hs) + item_gap * (len(itens) - 1)
        iy = cy + (card_h - block_h) // 2

        if label:
            _, lh = draw_pill(draw, label, cx + 20, iy, side_color, lbl_f, filled=False)
            iy += lh + gap_pill

        for i, item_txt in enumerate(itens):
            row_h = item_hs[i]
            if prefixo:
                pref_color = "#ff6b6b" if prefixo == "x" else side_color
                pref_h = th_val(draw, prefixo, pref_f)
                pref_y = iy + (row_h - pref_h) // 2
                put(draw, prefixo, cx + 20, pref_y, pref_f, pref_color)
            tx = cx + 64
            draw_wrapped(draw, item_txt, tx, iy, item_f, WHITE, cw - 80, 5)
            iy += row_h + (item_gap if i < len(itens) - 1 else 0)

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
    n_items = len(itens)
    item_f  = font(False, 28)
    box_s   = 32   # tamanho do quadrado do checkmark

    # row_h preenche toda a area disponivel
    area_rows = banner_top - y - 12
    sep_h     = 1 + 14  # separator + gap acima
    row_h_fill = max(box_s + 4, (area_rows - sep_h * n_items) // max(n_items, 1))
    min_row_h  = row_h_fill

    def draw_checkmark(cx, cy, c):
        draw.rounded_rectangle((cx, cy, cx+box_s, cy+box_s), radius=5, fill=c)
        mx, my = cx + box_s//2, cy + box_s - 7
        lx = cx + 5
        draw.line([(lx, my-4), (mx-2, my), (cx+box_s-6, cy+7)],
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
        y += 14

        # Calcular altura da linha
        tx    = PAD + box_s + 22
        row_h = measure_wrapped(draw, txt, item_f, cw - box_s - 26, 5)
        row_h = max(row_h, min_row_h)

        # Checkmark box centrado verticalmente na linha
        box_y = y + (row_h - box_s) // 2
        draw_checkmark(PAD + 4, box_y, check_color)

        # Texto centrado verticalmente
        # Subtrair trailing line_gap para alinhar centro do texto com centro do checkbox
        txt_h_raw = measure_wrapped(draw, txt, item_f, cw - box_s - 26, 5)
        txt_y = y + (row_h - txt_h_raw + 5) // 2
        draw_wrapped(draw, txt, tx, txt_y, item_f, txt_color, cw - box_s - 26, 5)
        y += row_h + 8

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
# ============================================================================
# LAYOUT "automacao"
# Layout premium: watermark decorativo + cor unica por slide + steps limpos
# ============================================================================
def slide_automacao(num, total, titulo, pill_label, numero_str, itens,
                    banner_text, color):
    """
    itens: [{"titulo": str, "texto": str}, ...]
    numero_str: "01", "02", etc. — usado como watermark de fundo
    """
    img  = Image.new("RGB", (W, H), BG)
    draw_deco_circles(img, color)

    # Numero decorativo watermark (fundo, atras de tudo)
    wm_draw = ImageDraw.Draw(img)
    wm_f    = font(True, 360)
    wm_col  = tint(BG, color, 0.09)
    wm_w    = tw(wm_draw, numero_str, wm_f)
    put(wm_draw, numero_str, W - wm_w + 55, HEADER_H, wm_f, wm_col)

    draw = ImageDraw.Draw(img)
    draw_header(img, draw)

    banner_top = draw_banner(draw, banner_text, color, H - FOOTER_H - 8)
    y = draw_slide_title(draw, titulo, HEADER_H + 16, color,
                         fnt_size=44, pill_label=pill_label, pill_color=color)
    y += 10

    area_h = banner_top - y - 12
    n      = len(itens)
    cw     = W - 2 * PAD

    num_f  = font(True, 20)
    tit_f  = font(True, 28)
    desc_f = font(False, 23)

    # Altura natural de cada card: conteudo + padding interno generoso
    pad_v      = 34  # padding top+bottom dentro do card
    tit_hs     = [th_val(draw, item.get("titulo",""), tit_f) for item in itens]
    desc_hs    = [measure_wrapped(draw, item.get("texto",""), desc_f, cw - 62, 4) for item in itens]
    card_h     = max(tit_hs[i] + 8 + desc_hs[i] for i in range(n)) + pad_v * 2
    card_h     = max(card_h, 90)

    # Distribuir espaco entre os cards uniformemente
    # top_offset = gap (mesmo espaco no topo que entre cards) — evita gap excessivo em titulos curtos
    total_used = card_h * n
    gap        = max(16, (area_h - total_used) // (n + 1))
    top_offset = gap

    for i, item in enumerate(itens):
        sy = y + top_offset + i * (card_h + gap)

        # Card delicado: fundo sutil, borda levemente arredondada
        draw.rounded_rectangle((PAD, sy, PAD + cw, sy + card_h),
                                radius=16, fill=tint(DARK_BG, color, 0.10))
        draw.rounded_rectangle((PAD, sy, PAD + cw, sy + card_h),
                                radius=16, outline=tint(BG, color, 0.22), width=1)
        # Borda esquerda colorida
        draw.rounded_rectangle((PAD, sy, PAD + 5, sy + card_h),
                                radius=2, fill=color)

        # Numero do passo — centralizado verticalmente no card
        step_num = f"0{i+1}"
        num_h    = th_val(draw, step_num, num_f)
        num_y    = sy + (card_h - num_h) // 2
        put(draw, step_num, PAD + 16, num_y, num_f, tint(WHITE, BG, 0.40))

        # Conteudo centralizado verticalmente no card
        tit_txt  = item.get("titulo", "")
        desc_txt = item.get("texto", "")
        block_h  = tit_hs[i] + 8 + desc_hs[i]
        iy = sy + (card_h - block_h) // 2

        put(draw, tit_txt, PAD + 52, iy, tit_f, WHITE)
        draw_wrapped(draw, desc_txt, PAD + 52, iy + tit_hs[i] + 8,
                     desc_f, GRAY, cw - 62, 4)

    draw_progress(draw, num, total, color)
    return img


# SLIDE 8: CTA
# Layout aberto: sem card gigante — watermark "?" decorativo + conteudo
# distribuido verticalmente com respiro generoso
# ============================================================================
def slide_cta(num, total, pergunta, detalhe, color, cta_botao=None):
    img  = Image.new("RGB", (W, H), BG)
    draw_deco_circles(img, color)

    # Watermark "?" decorativo — mesmo principio do numero nos slides de automacao
    wm_draw = ImageDraw.Draw(img)
    wm_f    = font(True, 420)
    wm_col  = tint(BG, color, 0.08)
    wm_w    = tw(wm_draw, "?", wm_f)
    wm_h_px = 420  # aproximado
    put(wm_draw, "?", (W - wm_w) // 2 + 20, H // 2 - wm_h_px // 2, wm_f, wm_col)

    draw = ImageDraw.Draw(img)
    draw_header(img, draw)

    cw    = W - 2 * PAD
    cx    = PAD

    q_f   = font(True, 68)
    d_f   = font(False, 30)
    btn_f = font(True, 28)
    sig_b = font(True, 26)
    sig_f = font(False, 22)

    # Medir todos os blocos
    q_h   = measure_wrapped(draw, pergunta, q_f, cw, 8)
    d_h   = measure_wrapped(draw, detalhe, d_f, cw, 8) if detalhe else 0
    btn_h = (th_val(draw, cta_botao or "x", btn_f) + 36) if cta_botao else 0
    sig_h = th_val(draw, "Matheus Zacche", sig_b) + 10 + th_val(draw, "Analista de Dados", sig_f)

    gap_q_d   = 44
    gap_d_btn = 52
    gap_btn_sep = 56
    gap_sep_sig = 32

    # Altura total do bloco principal (pergunta + detalhe + botao)
    main_h = q_h
    if detalhe:  main_h += gap_q_d + d_h
    if cta_botao: main_h += gap_d_btn + btn_h

    # Assinatura ancorada no rodape
    sig_y   = H - FOOTER_H - 48 - sig_h
    sep_y   = sig_y - gap_sep_sig - 1
    sep_x1  = cx + cw // 4
    sep_x2  = cx + 3 * cw // 4

    # Bloco principal centrado na area acima do separador
    area_top = HEADER_H + 48
    area_bot = sep_y - gap_btn_sep
    iy = area_top + max(0, (area_bot - area_top - main_h) // 2)

    # Renderizar pergunta + detalhe + botao em sequencia
    iy = draw_wrapped_center(draw, pergunta, cx + cw//2, iy, q_f, color, cw, 8)

    if detalhe:
        iy += gap_q_d
        iy = draw_wrapped_center(draw, detalhe, cx + cw//2, iy, d_f, GRAY, cw, 8)

    if cta_botao:
        iy += gap_d_btn
        bw = tw(draw, cta_botao, btn_f) + 96
        bh = btn_h
        bx = cx + (cw - bw) // 2
        draw.rounded_rectangle((bx, iy, bx+bw, iy+bh), radius=bh//2,
                                fill=tint(BG, color, 0.14))
        draw.rounded_rectangle((bx, iy, bx+bw, iy+bh), radius=bh//2,
                                outline=color, width=2)
        put_center(draw, cta_botao, bx + bw//2,
                   iy + (bh - th_val(draw, cta_botao, btn_f))//2, btn_f, WHITE)

    draw.line([(sep_x1, sep_y), (sep_x2, sep_y)], fill=tint(BG, color, 0.45), width=1)
    put_center(draw, "Matheus Zacche", cx + cw//2, sig_y, sig_b, color)
    put_center(draw, "Analista de Dados", cx + cw//2,
               sig_y + th_val(draw, "Matheus Zacche", sig_b) + 10, sig_f, GRAY)

    draw_progress(draw, num, total, color)
    return img


# ============================================================================
# FUNCAO PRINCIPAL
# ============================================================================
def gerar_carrossel(titulo_destaque, titulo_branco, subtitulo,
                    pills, slides_conteudo, cta_pergunta, cta_detalhe,
                    capa_preview=None, capa_abstract=None, capa_watermark=None,
                    capa_index=None, theme_color="#00d4aa", output_name="carrossel",
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
    n_content = min(len(slides_conteudo), 6)
    total     = 2 + n_content  # capa + conteudo + cta
    images    = []

    images.append(slide_capa(
        1, total,
        titulo_destaque, titulo_branco, subtitulo,
        pills, capa_preview or [], theme_color,
        abstract=capa_abstract, watermark=capa_watermark,
        capa_index=capa_index
    ))

    for i, s in enumerate(slides_conteudo[:n_content]):
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

        elif layout == "automacao":
            images.append(slide_automacao(
                n, total, s["titulo"], s.get("pill", ""),
                s.get("numero", f"0{i+1}"), s.get("itens", []),
                s.get("banner", ""), s.get("cor", theme_color)))

        else:  # numbered
            images.append(slide_numbered(
                n, total, s["titulo"], s.get("pill", ""),
                s.get("itens", []), s.get("banner", ""), theme_color))

    images.append(slide_cta(len(images)+1, total, cta_pergunta, cta_detalhe, theme_color, cta_botao=cta_botao))

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
# TESTE — carrossel: 5 automações que todo analista deveria ter rodando
# ============================================================================
if __name__ == "__main__":
    gerar_carrossel(
        titulo_destaque="5 automações",
        titulo_branco="que analistas eficientes\njá têm rodando",
        subtitulo="Economize horas por semana com Python e N8N",
        pills=["PYTHON", "N8N", "AUTOMAÇÃO"],
        capa_abstract="Tarefas repetitivas são custo. Automação é investimento.",
        capa_preview=[],
        capa_index=[
            {"numero": "01", "titulo": "Relatório semanal automático",        "cor": "#4a9eff"},
            {"numero": "02", "titulo": "Alerta quando o dado foge do padrão", "cor": "#f59e0b"},
            {"numero": "03", "titulo": "Pipeline que roda toda madrugada",    "cor": "#a855f7"},
            {"numero": "04", "titulo": "Planilha atualizada? Banco atualizado","cor": "#00d4aa"},
            {"numero": "05", "titulo": "Monitor diário de saúde dos dados",   "cor": "#ff6b6b"},
        ],
        slides_conteudo=[
            # Slide 2 — Automação 01 — azul
            {
                "layout": "automacao",
                "titulo": "Relatório semanal automático",
                "pill": "AUTOMAÇÃO 01",
                "numero": "01",
                "cor": "#4a9eff",
                "banner": "Você não deveria montar relatório toda segunda.",
                "itens": [
                    {"titulo": "Coleta e calcula",
                     "texto": "Busca dados do banco e calcula os KPIs sem intervenção"},
                    {"titulo": "Gera o arquivo",
                     "texto": "Monta PDF ou Excel formatado com layout consistente"},
                    {"titulo": "Dispara o envio",
                     "texto": "E-mail enviado toda segunda-feira às 7h, sem clique"},
                    {"titulo": "Você só lê",
                     "texto": "Chega no trabalho com o relatório pronto na caixa de entrada"},
                ],
            },
            # Slide 3 — Automação 02 — âmbar
            {
                "layout": "automacao",
                "titulo": "Alerta quando o dado foge do padrão",
                "pill": "AUTOMAÇÃO 02",
                "numero": "02",
                "cor": "#f59e0b",
                "banner": "Saber antes que alguém reclame faz toda a diferença.",
                "itens": [
                    {"titulo": "Monitora",
                     "texto": "Métricas críticas verificadas todo dia pelo script Python"},
                    {"titulo": "Compara",
                     "texto": "Desvia mais de X% da média histórica? Algo mudou."},
                    {"titulo": "Alerta",
                     "texto": "Mensagem automática no WhatsApp ou Slack com detalhes"},
                    {"titulo": "Você age",
                     "texto": "Antes de virar problema — e antes de alguém reclamar"},
                ],
            },
            # Slide 4 — Automação 03 — roxo
            {
                "layout": "automacao",
                "titulo": "Pipeline que roda sozinho toda madrugada",
                "pill": "AUTOMAÇÃO 03",
                "numero": "03",
                "cor": "#a855f7",
                "banner": "Dados frescos sem você precisar acionar nada.",
                "itens": [
                    {"titulo": "Extrai",
                     "texto": "Conecta na fonte: API, banco de dados ou arquivo CSV"},
                    {"titulo": "Trata",
                     "texto": "Python limpa, valida e transforma os dados brutos"},
                    {"titulo": "Carrega",
                     "texto": "Dados prontos no banco de destino ou Google Sheets"},
                    {"titulo": "Agenda",
                     "texto": "N8N dispara o pipeline toda madrugada sem intervenção"},
                ],
            },
            # Slide 5 — Automação 04 — teal
            {
                "layout": "automacao",
                "titulo": "Planilha atualizada? Banco atualizado",
                "pill": "AUTOMAÇÃO 04",
                "numero": "04",
                "cor": "#00d4aa",
                "banner": "Copiar e colar é o maior ladrão de tempo do analista.",
                "itens": [
                    {"titulo": "Detecta",
                     "texto": "Google Sheets atualizado? Webhook dispara em segundos"},
                    {"titulo": "Valida",
                     "texto": "Python checa tipo, formato e regras antes de salvar"},
                    {"titulo": "Salva",
                     "texto": "Dado certo no banco, com registro de quem alterou e quando"},
                    {"titulo": "Elimina",
                     "texto": "Fim do ctrl+C ctrl+V entre planilha e sistema"},
                ],
            },
            # Slide 6 — Automação 05 — vermelho
            {
                "layout": "automacao",
                "titulo": "Monitor diário de saúde dos dados",
                "pill": "AUTOMAÇÃO 05",
                "numero": "05",
                "cor": "#ff6b6b",
                "banner": "Dado ruim gera decisão ruim. Monitore antes de trabalhar.",
                "itens": [
                    {"titulo": "Verifica",
                     "texto": "Nulos, duplicatas e outliers checados automaticamente"},
                    {"titulo": "Resume",
                     "texto": "Relatório de qualidade gerado toda manhã antes do expediente"},
                    {"titulo": "Alerta",
                     "texto": "Se alguma fonte parou de atualizar, você sabe na hora"},
                    {"titulo": "Você começa",
                     "texto": "Sabendo o estado real dos dados, não descobrindo no meio"},
                ],
            },
        ],
        cta_pergunta="Qual dessas você ainda faz na mão?",
        cta_detalhe="Conta nos comentários qual automação te salvaria mais tempo",
        cta_botao="Comenta aqui embaixo!",
        theme_color="#00d4aa",
        output_name="carrossel_automacoes"
    )
