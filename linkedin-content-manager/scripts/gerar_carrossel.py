# -*- coding: utf-8 -*-
"""
Gerador de Carrossel LinkedIn - Matheus Zacche
===============================================
Sistema visual baseado nos criativos de referencia (03_estrutura_criativos.md).

Dois layouts de slide suportados:
  - "numbered" : cards compactos com numero 01/02/03 + titulo + descricao
  - "categorias": cards com pill de categoria + lista de bullet points

Uso:
    from scripts.gerar_carrossel import gerar_carrossel
    pdf, pngs = gerar_carrossel(...)
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
# DESIGN
# ============================================================================
W        = 1080
H        = 1350
PAD      = 56          # margem lateral
HEADER_H = 120         # altura do header + separador
FOOTER_H = 50          # barra de progresso
BANNER_H = 76          # banner de destaque (slides 2-7)

BG         = "#1a1a2e"
CARD_BG    = "#22223a"
WHITE      = "#ffffff"
GRAY       = "#a0a0b8"
DIM_GRAY   = "#4a4a6a"   # numero dos cards
SEP        = "#2a2a48"   # linha separadora header
DARK_BG    = "#141428"   # fundo mais escuro para contraste


def font(bold=False, size=24):
    path = FONT_BOLD if bold else FONT_REGULAR
    try:
        return ImageFont.truetype(path, size)
    except (OSError, IOError):
        try:
            return ImageFont.truetype("arialbd.ttf" if bold else "arial.ttf", size)
        except (OSError, IOError):
            return ImageFont.load_default()


def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def tint(base_hex, color_hex, alpha=0.18):
    """Mistura base_hex com color_hex no alpha dado."""
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
    """Retorna (x0,y0,x1,y1) do textbbox."""
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
    """Centraliza texto horizontalmente em torno de cx."""
    b = bb(draw, text, fnt)
    put(draw, text, cx - (b[2] - b[0]) // 2, y, fnt, fill)


def wrap_lines(draw, text, fnt, max_w):
    """Quebra texto em linhas que cabem em max_w."""
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
    """Desenha texto com wrap. Retorna Y final."""
    for line in wrap_lines(draw, text, fnt, max_w):
        put(draw, line, x, y, fnt, fill)
        y += th_val(draw, line, fnt) + line_gap
    return y


def draw_wrapped_center(draw, text, cx, y, fnt, fill, max_w, line_gap=8):
    """Desenha texto centralizado com wrap."""
    for line in wrap_lines(draw, text, fnt, max_w):
        put_center(draw, line, cx, y, fnt, fill)
        y += th_val(draw, line, fnt) + line_gap
    return y


def measure_wrapped(draw, text, fnt, max_w, line_gap=8):
    """Retorna altura total do texto apos wrap."""
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

    # Nome
    fn = font(True, 26)
    put(draw, "Matheus Zacche", nx, py + 4, fn, WHITE)
    name_end = nx + tw(draw, "Matheus Zacche", fn)

    # Badge verificado
    bcx = name_end + 16
    bcy = py + 4 + th_val(draw, "Matheus Zacche", fn) // 2
    br  = 10
    draw.ellipse((bcx-br, bcy-br, bcx+br, bcy+br), fill="#1a8cff")
    cf = font(True, 13)
    b = bb(draw, "v", cf)
    draw.text((bcx - (b[2]-b[0])//2 - b[0], bcy - (b[3]-b[1])//2 - b[1]),
              "v", font=cf, fill=WHITE)

    # Handle
    hf = font(False, 19)
    put(draw, "@matheus.zacche", nx, py + 38, hf, GRAY)

    # Tres pontos
    df = font(False, 20)
    dots = "• • •"
    put(draw, dots, W - PAD - tw(draw, dots, df), py + 16, df, GRAY)

    # Separador
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
# ============================================================================

def draw_banner(draw, text, color, y_bottom):
    """Desenha banner de destaque. Retorna y_top do banner."""
    bx = PAD
    bw = W - 2 * PAD
    by = y_bottom - BANNER_H

    draw.rounded_rectangle((bx, by, bx+bw, by+BANNER_H),
                            radius=10, fill=tint(DARK_BG, color, 0.30))
    draw.rounded_rectangle((bx, by, bx+bw, by+BANNER_H),
                            radius=10, outline=color, width=1)

    bf = font(True, 23)
    lines = wrap_lines(draw, text, bf, bw - 48)
    total_h = sum(th_val(draw, l, bf) + 6 for l in lines)
    ty = by + (BANNER_H - total_h) // 2
    for line in lines:
        put_center(draw, line, bx + bw // 2, ty, bf, WHITE)
        ty += th_val(draw, line, bf) + 6

    return by


# ============================================================================
# PILL
# ============================================================================

def draw_pill(draw, label, x, y, color, fnt=None):
    """Desenha uma pill outlined. Retorna (x_right, height)."""
    if fnt is None:
        fnt = font(True, 16)
    ph, pv = 10, 5
    lw = tw(draw, label, fnt)
    lh = th_val(draw, label, fnt)
    pw = lw + ph * 2
    pill_h = lh + pv * 2
    draw.rounded_rectangle((x, y, x+pw, y+pill_h),
                            radius=5, fill=tint(DARK_BG, color, 0.20),
                            outline=color, width=1)
    put(draw, label, x + ph, y + pv, fnt, color)
    return x + pw, pill_h


# ============================================================================
# CIRCULOS DECORATIVOS (capa)
# ============================================================================

def draw_deco_circles(img, color):
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    r, g, b = hex_rgb(color)

    d.ellipse((-160, H-280, 160, H+100), fill=(r, g, b, 28))
    d.ellipse((-80, H-180, 80, H+20),   fill=(r, g, b, 18))
    d.ellipse((W-160, H-280, W+160, H+100), fill=(r, g, b, 22))
    d.ellipse((W-60, -60, W+120, 120),   fill=(r, g, b, 15))

    blurred = overlay.filter(ImageFilter.GaussianBlur(radius=50))
    img.paste(blurred, (0, 0), blurred)


# ============================================================================
# SLIDE 1: CAPA
# ============================================================================

def slide_capa(num, total, titulo_destaque, titulo_branco,
               subtitulo, pills, preview_cards, color, abstract=None):
    img  = Image.new("RGB", (W, H), BG)
    draw_deco_circles(img, color)
    draw = ImageDraw.Draw(img)
    draw_header(img, draw)

    y = HEADER_H + 16

    # Pills
    if pills:
        pf = font(True, 16)
        x  = PAD
        ph_max = 0
        for label in pills:
            x_right, ph = draw_pill(draw, label, x, y, color, pf)
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

    # Underline
    draw.rounded_rectangle((PAD, y+6, PAD+64, y+10), radius=2, fill=color)
    y += 26

    # Subtitulo
    if subtitulo:
        sf = font(False, 26)
        y  = draw_wrapped(draw, subtitulo, PAD, y, sf, GRAY, W - 2*PAD, 7)

    y += 28  # breathing room

    # ---- Abstract highlight box ----
    # Fills the dead space between subtitle and preview cards / progress bar
    preview_h  = 200 if (preview_cards and len(preview_cards) >= 2) else 0
    footer_top = H - FOOTER_H - 14
    box_bottom  = footer_top - preview_h - (24 if preview_h else 0)
    raw_box_h   = box_bottom - y - 8
    MAX_BOX_H   = 340
    if raw_box_h > MAX_BOX_H:
        y      += (raw_box_h - MAX_BOX_H) // 2  # centraliza a caixa verticalmente
        box_h   = MAX_BOX_H
    else:
        box_h   = raw_box_h

    if abstract and box_h > 60:
        bx = PAD
        bw = W - 2 * PAD

        draw.rounded_rectangle((bx, y, bx+bw, y+box_h),
                                radius=14, fill=tint(DARK_BG, color, 0.14))
        draw.rounded_rectangle((bx, y, bx+bw, y+box_h),
                                radius=14, outline=color, width=1)
        # Accent bar on left
        draw.rounded_rectangle((bx, y, bx+5, y+box_h), radius=2, fill=color)

        # Linha decorativa superior + inferior (separa o abstract visualmente)
        deco_pad = 48
        draw.line([(bx + deco_pad, y + box_h//2 - 40),
                   (bx + bw - deco_pad, y + box_h//2 - 40)],
                  fill=tint(BG, color, 0.40), width=1)
        draw.line([(bx + deco_pad, y + box_h//2 + 40),
                   (bx + bw - deco_pad, y + box_h//2 + 40)],
                  fill=tint(BG, color, 0.40), width=1)

        af    = font(True, 36)
        lines = wrap_lines(draw, abstract, af, bw - 100)
        lh    = sum(th_val(draw, l, af) + 14 for l in lines)
        ay    = y + (box_h - lh) // 2
        for line in lines:
            put_center(draw, line, bx + bw//2, ay, af, WHITE)
            ay += th_val(draw, line, af) + 14

        y = box_bottom + 24

    elif preview_h:
        # No abstract: anchor preview cards to bottom
        y = box_bottom + 24

    # Preview cards (2 cards lado a lado)
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
        arrow_cy = card_y + card_h // 2 - 10
        put_center(draw, ">", arrow_x, arrow_cy, af, GRAY)

    draw_progress(draw, num, total, color)
    return img


# ============================================================================
# SLIDE CONTEUDO: LAYOUT "numbered"
# Cards compactos com numero 01/02/03 + titulo + descricao
# ============================================================================

def slide_numbered(num, total, titulo, slide_pill, itens, banner_text, color):
    img  = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    draw_header(img, draw)

    banner_top = draw_banner(draw, banner_text, color, H - FOOTER_H - 8)
    content_top = HEADER_H + 12

    y = content_top

    # Pill do slide (opcional)
    if slide_pill:
        _, ph = draw_pill(draw, slide_pill, PAD, y, color)
        y += ph + 14

    # Titulo
    title_f = font(True, 32)
    y = draw_wrapped(draw, titulo, PAD, y, title_f, WHITE, W - 2*PAD, 4)
    draw.rounded_rectangle((PAD, y+2, PAD+46, y+6), radius=2, fill=color)
    y += 18

    # Area dos cards
    area_h    = banner_top - y - 10
    n         = len(itens)
    card_gap  = 10
    MAX_CH    = 200
    card_h    = min(MAX_CH, max(90, (area_h - card_gap*(n-1)) // max(n, 1)))
    block_h   = n * card_h + (n-1) * card_gap
    start_y   = y + max(0, (area_h - block_h) // 2)

    num_f  = font(True, 34)
    tit_f  = font(True, 21)
    desc_f = font(False, 19)

    for i, item in enumerate(itens):
        cx = PAD
        cy = start_y + i * (card_h + card_gap)
        cw = W - 2*PAD

        draw.rounded_rectangle((cx, cy, cx+cw, cy+card_h),
                                radius=10, fill=CARD_BG)
        # Barra lateral 4px
        draw.rounded_rectangle((cx, cy, cx+4, cy+card_h),
                                radius=2, fill=color)

        # Numero (cinza escuro, nao accent)
        num_str = f"{i+1:02d}"
        nw2 = tw(draw, num_str, num_f)
        nh  = th_val(draw, num_str, num_f)
        num_x = cx + 20
        put(draw, num_str, num_x, cy + (card_h - nh) // 2, num_f, DIM_GRAY)

        # Texto
        tx        = num_x + nw2 + 18
        max_txt_w = cw - (tx - cx) - 16

        titulo_item = item.get("titulo", "")
        desc_item   = item.get("texto", "")

        t_h = th_val(draw, titulo_item or "A", tit_f) if titulo_item else 0
        d_h = measure_wrapped(draw, desc_item, desc_f, max_txt_w, 5) if desc_item else 0
        gap_td = 6 if (titulo_item and desc_item) else 0
        block  = t_h + gap_td + d_h
        ty     = cy + (card_h - block) // 2

        if titulo_item:
            put(draw, titulo_item, tx, ty, tit_f, WHITE)
            ty += t_h + gap_td
        if desc_item:
            draw_wrapped(draw, desc_item, tx, ty, desc_f, GRAY, max_txt_w, 5)

    draw_progress(draw, num, total, color)
    return img


# ============================================================================
# SLIDE CONTEUDO: LAYOUT "categorias"
# 2 cards grandes com pill de categoria + bullet list
# ============================================================================

def _measure_card_categorias(draw, item, item_color, cw, label_f, bullet_f,
                              card_pad=14):
    """Retorna a altura natural de um card categorias (sem desenhar)."""
    h = card_pad
    label = item.get("label", "")
    if label:
        lh = th_val(draw, label, label_f)
        pv = 5
        h += lh + pv * 2 + 10  # pill_h + gap
    for bullet in item.get("bullets", []):
        h += measure_wrapped(draw, bullet, bullet_f, cw - 50, 4) + 8
    h += card_pad
    return h


def slide_categorias(num, total, titulo, itens, banner_text, color):
    img  = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    draw_header(img, draw)

    banner_top  = draw_banner(draw, banner_text, color, H - FOOTER_H - 8)
    content_top = HEADER_H + 12

    y = content_top

    # Titulo
    title_f = font(True, 32)
    y = draw_wrapped(draw, titulo, PAD, y, title_f, WHITE, W - 2*PAD, 4)
    draw.rounded_rectangle((PAD, y+2, PAD+46, y+6), radius=2, fill=color)
    y += 18

    area_top = y
    area_h   = banner_top - y - 10
    n        = len(itens)
    card_gap = 16

    bullet_f  = font(False, 20)
    label_f   = font(True, 17)
    card_pad  = 14
    cw        = W - 2 * PAD

    # Mede altura natural de cada card
    natural_heights = [
        _measure_card_categorias(draw, item, item.get("cor", color),
                                 cw, label_f, bullet_f, card_pad)
        for item in itens
    ]
    total_natural = sum(natural_heights) + card_gap * max(n - 1, 0)

    if total_natural <= area_h:
        # Cards menores que area: ancora ao topo (espaco vazio fica embaixo, antes do banner)
        card_heights = natural_heights
        start_y = area_top
    else:
        # Cards maiores que area: distribui igualmente (escala)
        equal_h = (area_h - card_gap * max(n - 1, 0)) // max(n, 1)
        card_heights = [max(equal_h, 80)] * n
        start_y = area_top

    for i, item in enumerate(itens):
        card_h     = card_heights[i]
        cx         = PAD
        cy         = start_y + sum(card_heights[:i]) + card_gap * i
        item_color = item.get("cor", color)

        draw.rounded_rectangle((cx, cy, cx+cw, cy+card_h),
                                radius=10, fill=tint(DARK_BG, item_color, 0.12))
        draw.rounded_rectangle((cx, cy, cx+4, cy+card_h),
                                radius=2, fill=item_color)

        iy = cy + card_pad

        # Pill de categoria
        label = item.get("label", "")
        if label:
            _, pill_h = draw_pill(draw, label, cx + 18, iy, item_color, label_f)
            iy += pill_h + 10

        # Bullets — usa retorno de draw_wrapped para avançar corretamente
        for bullet in item.get("bullets", []):
            br = 4
            draw.ellipse((cx + 18, iy + 8, cx + 18 + br*2, iy + 8 + br*2),
                         fill=item_color)
            iy = draw_wrapped(draw, bullet, cx + 32, iy, bullet_f, WHITE,
                              cw - 50, 4)
            iy += 6  # gap entre bullets

    draw_progress(draw, num, total, color)
    return img


# ============================================================================
# SLIDE 8: CTA
# ============================================================================

def slide_cta(num, total, pergunta, detalhe, color):
    img  = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    draw_header(img, draw)

    ct    = HEADER_H + 20
    cb    = H - FOOTER_H - 20
    avail = cb - ct
    card_h = int(avail * 0.60)
    cx   = PAD
    cw   = W - 2*PAD
    cy   = ct + (avail - card_h) // 2

    draw.rounded_rectangle((cx, cy, cx+cw, cy+card_h),
                            radius=14, fill=CARD_BG)
    draw.rounded_rectangle((cx, cy, cx+cw, cy+card_h),
                            radius=14, outline=color, width=1)

    # Conteudo centralizado verticalmente no card
    q_f  = font(True, 34)
    d_f  = font(False, 24)
    s_f  = font(False, 20)
    sv_f = font(True, 20)

    save_text = "Salva esse post para consultar depois"

    q_h   = measure_wrapped(draw, pergunta, q_f, cw-80, 10)
    d_h   = measure_wrapped(draw, detalhe,  d_f, cw-80, 8) if detalhe else 0
    sv_h  = th_val(draw, save_text, s_f)
    sig_h = th_val(draw, "Matheus Zacche", sv_f)
    gap   = 28

    total_h = sv_h + 24 + 1 + 24 + q_h + (gap + d_h if detalhe else 0) + gap*2 + sig_h
    iy = cy + (card_h - total_h) // 2
    if iy < cy + 20:
        iy = cy + 20

    # "Salva esse post..."
    put_center(draw, save_text, cx + cw//2, iy, s_f, GRAY)
    iy += sv_h + 24

    # Separador
    draw.line([(cx+48, iy), (cx+cw-48, iy)], fill=SEP, width=1)
    iy += 1 + 24

    # Pergunta
    iy = draw_wrapped_center(draw, pergunta, cx+cw//2, iy, q_f, color, cw-80, 10)
    iy += 6

    # Detalhe
    if detalhe:
        iy += gap // 2
        iy = draw_wrapped_center(draw, detalhe, cx+cw//2, iy, d_f, GRAY, cw-80, 8)

    # Assinatura — no fluxo, logo abaixo do detalhe
    iy += gap * 2
    sig = "Matheus Zacche  •  Analista de Dados"
    put_center(draw, sig, cx + cw//2, iy, sv_f, color)

    draw_progress(draw, num, total, color)
    return img


# ============================================================================
# FUNCAO PRINCIPAL
# ============================================================================

def gerar_carrossel(titulo_destaque, titulo_branco, subtitulo,
                    pills, slides_conteudo, cta_pergunta, cta_detalhe,
                    capa_preview=None, capa_abstract=None,
                    theme_color="#00d4aa", output_name="carrossel"):
    """
    Gera carrossel completo de 8 slides + PDF.

    Args:
        titulo_destaque:  Parte do titulo em theme_color (capa)
        titulo_branco:    Parte do titulo em branco (capa). Suporta \\n.
        subtitulo:        Subtitulo cinza (capa)
        pills:            Lista de strings para pills da capa
        slides_conteudo:  Lista de 1-6 dicts. Cada dict:
            Layout "numbered" (default):
                { "titulo": str, "pill": str (opt), "banner": str,
                  "itens": [{"titulo": str, "texto": str}, ...] }
            Layout "categorias":
                { "titulo": str, "banner": str, "layout": "categorias",
                  "itens": [{"label": str, "cor": str, "bullets": [str,...]}, ...] }
        cta_pergunta:     Pergunta no slide 8
        cta_detalhe:      Texto complementar do CTA
        capa_abstract:    Frase de destaque que preenche o corpo da capa (opcional)
        capa_preview:     Lista de 2 dicts para preview cards da capa (opcional):
                          [{"icone": str, "titulo": str, "subs": [str,...], "cor": str}, ...]
        theme_color:      Cor hex do tema ("#00d4aa" ou "#f5a623")
        output_name:      Nome base dos arquivos

    Returns:
        (pdf_path, png_paths)
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    total  = 8
    images = []

    # Slide 1 — Capa
    images.append(slide_capa(
        1, total,
        titulo_destaque, titulo_branco, subtitulo,
        pills, capa_preview or [], theme_color,
        abstract=capa_abstract
    ))

    # Slides 2-7 — Conteudo
    for i, s in enumerate(slides_conteudo[:6]):
        layout = s.get("layout", "numbered")
        if layout == "categorias":
            images.append(slide_categorias(
                i+2, total,
                s.get("titulo", ""),
                s.get("itens", []),
                s.get("banner", ""),
                theme_color
            ))
        else:
            images.append(slide_numbered(
                i+2, total,
                s.get("titulo", ""),
                s.get("pill", ""),
                s.get("itens", []),
                s.get("banner", ""),
                theme_color
            ))

    # Preencher ate 7 se necessario
    while len(images) < 7:
        images.append(slide_numbered(
            len(images)+1, total, "...", "", [], "...", theme_color
        ))

    # Slide 8 — CTA
    images.append(slide_cta(8, total, cta_pergunta, cta_detalhe, theme_color))

    # Salvar
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
# TESTE
# ============================================================================
if __name__ == "__main__":
    gerar_carrossel(
        titulo_destaque="Python + N8N",
        titulo_branco="Como integrar tratamento\nde dados com automacao",
        subtitulo="Quando usar cada um e como faze-los trabalhar juntos",
        pills=["PYTHON", "N8N", "AUTOMACAO"],
        capa_abstract="Cada ferramenta no que faz melhor. Dados no Python. Fluxo no N8N.",
        capa_preview=[
            {"icone": "{}", "titulo": "Python", "subs": ["Dados", "Transformacao"], "cor": "#4a9eff"},
            {"icone": "[>>]", "titulo": "N8N", "subs": ["Fluxo", "Automacao"], "cor": "#00d4aa"},
        ],
        slides_conteudo=[
            {
                "titulo": "O papel de cada um",
                "banner": "Python e o cerebro. N8N e o sistema nervoso.",
                "layout": "categorias",
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
            {
                "titulo": "Quando usar Python",
                "pill": "PYTHON",
                "banner": "Use Python quando o problema esta nos dados.",
                "itens": [
                    {"titulo": "Tratar dados sujos", "texto": "Normalizar colunas, remover duplicatas, converter tipos com Pandas"},
                    {"titulo": "Calculos complexos", "texto": "Formulas, agregacoes, estatisticas alem do basico"},
                    {"titulo": "Processar arquivos", "texto": "Ler e transformar CSV, Excel, JSON, conectar bancos SQL"},
                    {"titulo": "Logica customizada", "texto": "Regras de negocio especificas que nao existem em nos prontos"},
                ],
            },
            {
                "titulo": "Quando usar N8N",
                "pill": "N8N",
                "banner": "Use N8N quando o problema esta no fluxo.",
                "itens": [
                    {"titulo": "Conectar sistemas", "texto": "APIs, bancos, planilhas, e-mails sem escrever codigo"},
                    {"titulo": "Agendar execucoes", "texto": "Cron jobs visuais, sem servidor dedicado"},
                    {"titulo": "Orquestrar acoes", "texto": "Sequencia de passos faceis de manter e alterar"},
                    {"titulo": "Manter sem codigo", "texto": "Fluxos que o time consegue entender e ajustar"},
                ],
            },
            {
                "titulo": "3 formas de integrar",
                "banner": "Dados no Python, acao automatizada no N8N.",
                "itens": [
                    {"titulo": "Code Node", "texto": "Escreve Python direto dentro do N8N. Ideal para transformacoes simples."},
                    {"titulo": "Execute Command", "texto": "N8N chama um script .py externo pelo terminal."},
                    {"titulo": "API via FastAPI", "texto": "Python roda como API separada. N8N consome via HTTP Request."},
                ],
            },
            {
                "titulo": "Exemplo de fluxo real",
                "banner": "Cada ferramenta no que faz melhor.",
                "itens": [
                    {"titulo": "N8N agenda", "texto": "Todo dia as 8h ou via webhook externo"},
                    {"titulo": "N8N busca dados", "texto": "API, banco de dados ou arquivo CSV"},
                    {"titulo": "Python processa", "texto": "Limpeza, calculos e transformacoes com Pandas"},
                    {"titulo": "N8N distribui", "texto": "E-mail, Sheets, Slack ou dashboard"},
                ],
            },
            {
                "titulo": "A regra de ouro",
                "banner": "Python para dados. N8N para fluxo.",
                "itens": [
                    {"titulo": "Python cuida dos dados", "texto": "Tratar, calcular, transformar"},
                    {"titulo": "N8N cuida do fluxo", "texto": "Agendar, conectar, distribuir"},
                    {"titulo": "Separar responsabilidades", "texto": "Sistema robusto e facil de manter"},
                ],
            },
        ],
        cta_pergunta="Voce ja usa Python e N8N juntos?",
        cta_detalhe="Conta nos comentarios como voce faz a integracao",
        theme_color="#00d4aa",
        output_name="carrossel_test"
    )
