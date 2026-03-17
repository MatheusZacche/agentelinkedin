# -*- coding: utf-8 -*-
"""
Gerador de Imagens para Posts LinkedIn - Matheus Zacche
Gera imagens em 4 tipos: destaque, comparativo, lista, diagrama.

Uso:
    python gerar_imagem_post.py
    Ou importar: from gerar_imagem_post import gerar_imagem_post
"""

import os
from PIL import Image, ImageDraw, ImageFont

# === PATHS ===
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(SCRIPT_DIR)
ASSETS_DIR = os.path.join(SKILL_DIR, "assets")
OUTPUT_DIR = os.path.join(SKILL_DIR, "output")

PHOTO_PATH = os.path.join(ASSETS_DIR, "foto_matheus.jpeg")
FONT_REGULAR = os.path.join(ASSETS_DIR, "NotoSans-Regular.ttf")
FONT_BOLD = os.path.join(ASSETS_DIR, "NotoSans-Bold.ttf")

# === DESIGN CONSTANTS ===
W = 1080
H = 1350
HEADER_H = 140
PADDING = 60
CARD_RADIUS = 20
PHOTO_SIZE = 80
PHOTO_TOP = 30

# Colors
BG_COLOR = "#1a1a2e"
CARD_COLOR = "#2a2a4a"
ACCENT = "#00d4aa"
WHITE = "#ffffff"
LIGHT_GRAY = "#b0b0c0"
DARK_GRAY = "#3a3a5a"
RED_SOFT = "#ff6b6b"
GREEN_SOFT = "#51cf66"


def load_font(bold=False, size=24):
    """Load Noto Sans font with Arial fallback."""
    path = FONT_BOLD if bold else FONT_REGULAR
    try:
        return ImageFont.truetype(path, size)
    except (OSError, IOError):
        try:
            fallback = "arialbd.ttf" if bold else "arial.ttf"
            return ImageFont.truetype(fallback, size)
        except (OSError, IOError):
            return ImageFont.load_default()


def make_circular_photo(size=PHOTO_SIZE):
    """Create circular photo from foto_matheus.jpeg."""
    try:
        photo = Image.open(PHOTO_PATH).convert("RGBA")
        pw, ph = photo.size
        crop_size = min(pw, ph)
        left = (pw - crop_size) // 2
        photo = photo.crop((left, 0, left + crop_size, crop_size))
        photo = photo.resize((size, size), Image.LANCZOS)
        mask = Image.new("L", (size, size), 0)
        ImageDraw.Draw(mask).ellipse((0, 0, size, size), fill=255)
        photo.putalpha(mask)
        return photo
    except (FileNotFoundError, IOError):
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        ImageDraw.Draw(img).ellipse((0, 0, size, size), fill=ACCENT)
        return img


def draw_header(img, draw):
    """Draw header with circular photo, name, and badge."""
    photo = make_circular_photo()
    photo_x = PADDING
    photo_y = PHOTO_TOP
    img.paste(photo, (photo_x, photo_y), photo)

    name_x = photo_x + PHOTO_SIZE + 16
    name_font = load_font(bold=True, size=28)
    draw.text((name_x, photo_y + 8), "Matheus Zacche", fill=WHITE, font=name_font)

    badge_font = load_font(bold=False, size=18)
    badge_text = "Analista de Dados"
    badge_y = photo_y + 42
    bbox = draw.textbbox((0, 0), badge_text, font=badge_font)
    bw = bbox[2] - bbox[0] + 20
    bh = bbox[3] - bbox[1] + 10
    draw.rounded_rectangle(
        (name_x, badge_y, name_x + bw, badge_y + bh),
        radius=10, fill=ACCENT
    )
    draw.text((name_x + 10, badge_y + 3), badge_text, fill=BG_COLOR, font=badge_font)

    handle_font = load_font(bold=False, size=16)
    draw.text((name_x, badge_y + bh + 6), "@matheus-zacche", fill=LIGHT_GRAY, font=handle_font)


def wrap_text(text, font, max_width, draw):
    """Wrap text to fit within max_width pixels."""
    words = text.split()
    lines = []
    current_line = ""
    for word in words:
        test = f"{current_line} {word}".strip()
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current_line = test
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    return lines


def text_center(draw, text, y, font, fill=WHITE, max_width=None):
    """Draw text centered horizontally. Returns next y position."""
    if max_width:
        lines = wrap_text(text, font, max_width, draw)
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            tw = bbox[2] - bbox[0]
            x = (W - tw) // 2
            draw.text((x, y), line, fill=fill, font=font)
            y += bbox[3] - bbox[1] + 8
        return y
    else:
        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        x = (W - tw) // 2
        draw.text((x, y), text, fill=fill, font=font)
        return y + bbox[3] - bbox[1] + 8


def auto_crop_bottom(img, bg_hex=BG_COLOR):
    """Remove empty background from bottom of image."""
    # Parse bg color
    bg = bg_hex.lstrip("#")
    bg_rgb = tuple(int(bg[i:i+2], 16) for i in (0, 2, 4))
    tolerance = 10

    pixels = img.load()
    w, h = img.size
    last_content_y = h - 1

    for y in range(h - 1, HEADER_H, -1):
        row_has_content = False
        for x in range(0, w, 4):  # Sample every 4th pixel for speed
            r, g, b = pixels[x, y][:3] if isinstance(pixels[x, y], tuple) else (pixels[x, y], pixels[x, y], pixels[x, y])
            if (abs(r - bg_rgb[0]) > tolerance or
                abs(g - bg_rgb[1]) > tolerance or
                abs(b - bg_rgb[2]) > tolerance):
                row_has_content = True
                break
        if row_has_content:
            last_content_y = y
            break

    # Add some padding below content
    crop_y = min(last_content_y + 80, h)
    # Minimum height
    crop_y = max(crop_y, W)  # At least square

    if crop_y < h:
        return img.crop((0, 0, w, crop_y))
    return img


# === IMAGE TYPES ===

def gerar_destaque(titulo, subtitulo="", output_name="destaque"):
    """Big title with optional subtitle. For opinions, trends."""
    img = Image.new("RGB", (W, H), BG_COLOR)
    draw = ImageDraw.Draw(img)
    draw_header(img, draw)

    usable_width = W - 2 * PADDING
    content_top = HEADER_H + 60

    # Accent line
    line_w = 100
    y = content_top + 80
    draw.rounded_rectangle(
        ((W - line_w) // 2, y, (W + line_w) // 2, y + 6),
        radius=3, fill=ACCENT
    )
    y += 40

    # Title
    title_font = load_font(bold=True, size=52)
    y = text_center(draw, titulo, y, title_font, fill=WHITE, max_width=usable_width - 40)

    # Subtitle
    if subtitulo:
        y += 30
        sub_font = load_font(bold=False, size=30)
        text_center(draw, subtitulo, y, sub_font, fill=LIGHT_GRAY, max_width=usable_width - 80)

    img = auto_crop_bottom(img)
    path = os.path.join(OUTPUT_DIR, f"{output_name}.png")
    img.save(path, "PNG")
    print(f"Imagem destaque salva: {path}")
    return path


def gerar_comparativo(titulo, antes_titulo, antes_itens, depois_titulo, depois_itens, output_name="comparativo"):
    """Before vs After comparison. For cases, transformations."""
    img = Image.new("RGB", (W, H), BG_COLOR)
    draw = ImageDraw.Draw(img)
    draw_header(img, draw)

    usable_width = W - 2 * PADDING
    content_top = HEADER_H + 30

    # Title
    title_font = load_font(bold=True, size=36)
    y = text_center(draw, titulo, content_top, title_font, fill=WHITE, max_width=usable_width)
    y += 30

    card_width = (usable_width - 30) // 2
    card_x_left = PADDING
    card_x_right = PADDING + card_width + 30

    # Calculate card height
    item_font = load_font(bold=False, size=22)
    max_items = max(len(antes_itens), len(depois_itens))
    card_h = 80 + max_items * 50 + 20

    # ANTES card (red tint)
    draw.rounded_rectangle(
        (card_x_left, y, card_x_left + card_width, y + card_h),
        radius=CARD_RADIUS, fill=CARD_COLOR
    )
    # Red accent bar at top
    draw.rounded_rectangle(
        (card_x_left, y, card_x_left + card_width, y + 6),
        radius=3, fill=RED_SOFT
    )
    antes_font = load_font(bold=True, size=26)
    draw.text((card_x_left + 20, y + 20), antes_titulo, fill=RED_SOFT, font=antes_font)
    iy = y + 65
    for item in antes_itens:
        draw.text((card_x_left + 20, iy), f"x  {item}", fill=LIGHT_GRAY, font=item_font)
        iy += 45

    # DEPOIS card (green tint)
    draw.rounded_rectangle(
        (card_x_right, y, card_x_right + card_width, y + card_h),
        radius=CARD_RADIUS, fill=CARD_COLOR
    )
    draw.rounded_rectangle(
        (card_x_right, y, card_x_right + card_width, y + 6),
        radius=3, fill=GREEN_SOFT
    )
    depois_font = load_font(bold=True, size=26)
    draw.text((card_x_right + 20, y + 20), depois_titulo, fill=GREEN_SOFT, font=depois_font)
    iy = y + 65
    for item in depois_itens:
        draw.text((card_x_right + 20, iy), f"✓  {item}", fill=WHITE, font=item_font)
        iy += 45

    # Arrow between cards
    arrow_y = y + card_h // 2
    arrow_x = PADDING + card_width + 5
    arrow_font = load_font(bold=True, size=28)
    draw.text((arrow_x, arrow_y - 14), ">", fill=ACCENT, font=arrow_font)

    img = auto_crop_bottom(img)
    path = os.path.join(OUTPUT_DIR, f"{output_name}.png")
    img.save(path, "PNG")
    print(f"Imagem comparativo salva: {path}")
    return path


def gerar_lista(titulo, itens, output_name="lista"):
    """Numbered list in cards. For tips, tools, recommendations."""
    img = Image.new("RGB", (W, H), BG_COLOR)
    draw = ImageDraw.Draw(img)
    draw_header(img, draw)

    usable_width = W - 2 * PADDING
    content_top = HEADER_H + 30

    # Title
    title_font = load_font(bold=True, size=36)
    y = text_center(draw, titulo, content_top, title_font, fill=WHITE, max_width=usable_width)
    y += 30

    item_title_font = load_font(bold=True, size=26)
    item_desc_font = load_font(bold=False, size=22)

    for i, item in enumerate(itens):
        if isinstance(item, dict):
            item_titulo = item.get("titulo", "")
            item_desc = item.get("descricao", "")
        else:
            item_titulo = str(item)
            item_desc = ""

        # Calculate card height
        lines_titulo = wrap_text(item_titulo, item_title_font, usable_width - 130, draw)
        lines_desc = wrap_text(item_desc, item_desc_font, usable_width - 130, draw) if item_desc else []
        card_h = 30 + len(lines_titulo) * 36 + len(lines_desc) * 32 + 20

        # Card
        draw.rounded_rectangle(
            (PADDING, y, W - PADDING, y + card_h),
            radius=CARD_RADIUS, fill=CARD_COLOR
        )

        # Number circle
        num_size = 44
        num_x = PADDING + 20
        num_y_center = y + card_h // 2 - num_size // 2
        draw.ellipse(
            (num_x, num_y_center, num_x + num_size, num_y_center + num_size),
            fill=ACCENT
        )
        num_font = load_font(bold=True, size=22)
        bbox = draw.textbbox((0, 0), str(i + 1), font=num_font)
        nw = bbox[2] - bbox[0]
        nh = bbox[3] - bbox[1]
        draw.text(
            (num_x + (num_size - nw) // 2, num_y_center + (num_size - nh) // 2 - 2),
            str(i + 1), fill=BG_COLOR, font=num_font
        )

        # Text
        text_x = num_x + num_size + 20
        ty = y + 15
        for line in lines_titulo:
            draw.text((text_x, ty), line, fill=WHITE, font=item_title_font)
            ty += 36
        for line in lines_desc:
            draw.text((text_x, ty), line, fill=LIGHT_GRAY, font=item_desc_font)
            ty += 32

        y += card_h + 15

    img = auto_crop_bottom(img)
    path = os.path.join(OUTPUT_DIR, f"{output_name}.png")
    img.save(path, "PNG")
    print(f"Imagem lista salva: {path}")
    return path


def gerar_diagrama(titulo, etapas, output_name="diagrama"):
    """Flow/process diagram with arrows. For tutorials, pipelines."""
    img = Image.new("RGB", (W, H), BG_COLOR)
    draw = ImageDraw.Draw(img)
    draw_header(img, draw)

    usable_width = W - 2 * PADDING
    content_top = HEADER_H + 30

    # Title
    title_font = load_font(bold=True, size=36)
    y = text_center(draw, titulo, content_top, title_font, fill=WHITE, max_width=usable_width)
    y += 40

    step_font = load_font(bold=True, size=24)
    desc_font = load_font(bold=False, size=20)
    arrow_font = load_font(bold=True, size=28)

    for i, etapa in enumerate(etapas):
        if isinstance(etapa, dict):
            etapa_titulo = etapa.get("titulo", "")
            etapa_desc = etapa.get("descricao", "")
        else:
            etapa_titulo = str(etapa)
            etapa_desc = ""

        # Step box
        box_h = 80 if not etapa_desc else 110
        draw.rounded_rectangle(
            (PADDING + 40, y, W - PADDING - 40, y + box_h),
            radius=CARD_RADIUS, fill=CARD_COLOR
        )

        # Step number badge
        badge_w = 36
        draw.rounded_rectangle(
            (PADDING + 55, y + 15, PADDING + 55 + badge_w, y + 15 + badge_w),
            radius=8, fill=ACCENT
        )
        num_font_small = load_font(bold=True, size=20)
        bbox = draw.textbbox((0, 0), str(i + 1), font=num_font_small)
        nw = bbox[2] - bbox[0]
        draw.text(
            (PADDING + 55 + (badge_w - nw) // 2, y + 20),
            str(i + 1), fill=BG_COLOR, font=num_font_small
        )

        # Step text
        draw.text((PADDING + 105, y + 18), etapa_titulo, fill=WHITE, font=step_font)
        if etapa_desc:
            lines = wrap_text(etapa_desc, desc_font, usable_width - 160, draw)
            dy = y + 55
            for line in lines:
                draw.text((PADDING + 105, dy), line, fill=LIGHT_GRAY, font=desc_font)
                dy += 28

        y += box_h + 10

        # Arrow between steps
        if i < len(etapas) - 1:
            arrow_x = W // 2
            draw.text((arrow_x - 8, y - 5), "|", fill=ACCENT, font=arrow_font)
            draw.text((arrow_x - 8, y + 10), "v", fill=ACCENT, font=arrow_font)
            y += 35

    img = auto_crop_bottom(img)
    path = os.path.join(OUTPUT_DIR, f"{output_name}.png")
    img.save(path, "PNG")
    print(f"Imagem diagrama salva: {path}")
    return path


def gerar_imagem_post(tipo, output_name="post_image", **kwargs):
    """Main dispatcher. Generates image based on type.

    Args:
        tipo: 'destaque', 'comparativo', 'lista', 'diagrama'
        output_name: Base filename
        **kwargs: Arguments specific to each type

    Returns:
        Path to generated PNG
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    if tipo == "destaque":
        return gerar_destaque(
            titulo=kwargs.get("titulo", "Titulo"),
            subtitulo=kwargs.get("subtitulo", ""),
            output_name=output_name
        )
    elif tipo == "comparativo":
        return gerar_comparativo(
            titulo=kwargs.get("titulo", "Comparativo"),
            antes_titulo=kwargs.get("antes_titulo", "Antes"),
            antes_itens=kwargs.get("antes_itens", []),
            depois_titulo=kwargs.get("depois_titulo", "Depois"),
            depois_itens=kwargs.get("depois_itens", []),
            output_name=output_name
        )
    elif tipo == "lista":
        return gerar_lista(
            titulo=kwargs.get("titulo", "Lista"),
            itens=kwargs.get("itens", []),
            output_name=output_name
        )
    elif tipo == "diagrama":
        return gerar_diagrama(
            titulo=kwargs.get("titulo", "Diagrama"),
            etapas=kwargs.get("etapas", []),
            output_name=output_name
        )
    else:
        raise ValueError(f"Tipo invalido: {tipo}. Use: destaque, comparativo, lista, diagrama")


# === TEST ===
if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Test destaque
    gerar_imagem_post("destaque", "test_destaque",
                      titulo="Parei de fazer dashboards bonitos",
                      subtitulo="E meus relatorios ficaram melhores")

    # Test comparativo
    gerar_imagem_post("comparativo", "test_comparativo",
                      titulo="Relatorio de Incentivos",
                      antes_titulo="ANTES",
                      antes_itens=["7 horas por semana", "Erros manuais", "3 planilhas", "Copiar e colar"],
                      depois_titulo="DEPOIS",
                      depois_itens=["20 minutos", "Zero erros", "Automatizado", "Python + N8N"])

    # Test lista
    gerar_imagem_post("lista", "test_lista",
                      titulo="5 Ferramentas que Uso Todo Dia",
                      itens=[
                          {"titulo": "Python", "descricao": "Automacao e ETL"},
                          {"titulo": "Power BI", "descricao": "Dashboards e KPIs"},
                          {"titulo": "SQL", "descricao": "Consultas e analises"},
                          {"titulo": "N8N", "descricao": "Orquestracao de fluxos"},
                          {"titulo": "Airflow", "descricao": "Pipelines de dados"},
                      ])

    # Test diagrama
    gerar_imagem_post("diagrama", "test_diagrama",
                      titulo="Pipeline de Dados: SAP ao Power BI",
                      etapas=[
                          {"titulo": "Extrair do SAP", "descricao": "Python conecta via RFC"},
                          {"titulo": "Transformar", "descricao": "Limpeza e padronizacao"},
                          {"titulo": "Carregar no DW", "descricao": "SQL Server como staging"},
                          {"titulo": "Visualizar", "descricao": "Power BI com refresh automatico"},
                      ])

    print("\nTodos os testes concluidos!")
