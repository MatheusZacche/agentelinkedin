# -*- coding: utf-8 -*-
"""
Gerador de Carrossel LinkedIn - Matheus Zacche
Gera 8 slides PNG + 1 PDF combinado para upload no LinkedIn.

Uso:
    python gerar_carrossel.py
    Ou importar: from gerar_carrossel import gerar_carrossel
"""

import os
import textwrap
from PIL import Image, ImageDraw, ImageFont, ImageFilter

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
FOOTER_H = 60
PADDING = 60
CARD_RADIUS = 20

# Colors
BG_COLOR = "#1a1a2e"
CARD_COLOR = "#2a2a4a"
ACCENT = "#00d4aa"
WHITE = "#ffffff"
LIGHT_GRAY = "#b0b0c0"
DARK_GRAY = "#3a3a5a"

# Photo
PHOTO_SIZE = 80
PHOTO_TOP = 30


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
        # Crop from top center (face is at top of vertical photo)
        pw, ph = photo.size
        crop_size = min(pw, ph)
        left = (pw - crop_size) // 2
        top = 0
        photo = photo.crop((left, top, left + crop_size, top + crop_size))
        photo = photo.resize((size, size), Image.LANCZOS)

        # Create circular mask
        mask = Image.new("L", (size, size), 0)
        ImageDraw.Draw(mask).ellipse((0, 0, size, size), fill=255)
        photo.putalpha(mask)
        return photo
    except (FileNotFoundError, IOError):
        # Fallback: colored circle
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        ImageDraw.Draw(img).ellipse((0, 0, size, size), fill=ACCENT)
        return img


def draw_rounded_rect(draw, xy, radius, fill):
    """Draw a rounded rectangle."""
    x0, y0, x1, y1 = xy
    draw.rounded_rectangle(xy, radius=radius, fill=fill)


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


def draw_progress_bar(draw, current, total):
    """Draw progress bar at footer."""
    bar_y = H - FOOTER_H + 15
    bar_h = 6
    bar_x = PADDING
    bar_w = W - 2 * PADDING
    # Background
    draw.rounded_rectangle(
        (bar_x, bar_y, bar_x + bar_w, bar_y + bar_h),
        radius=3, fill=DARK_GRAY
    )
    # Progress
    progress_w = int(bar_w * current / total)
    if progress_w > 0:
        draw.rounded_rectangle(
            (bar_x, bar_y, bar_x + progress_w, bar_y + bar_h),
            radius=3, fill=ACCENT
        )
    # Page number
    page_font = load_font(bold=False, size=16)
    page_text = f"{current}/{total}"
    bbox = draw.textbbox((0, 0), page_text, font=page_font)
    tw = bbox[2] - bbox[0]
    draw.text((W - PADDING - tw, bar_y + bar_h + 4), page_text, fill=LIGHT_GRAY, font=page_font)


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
    """Draw text centered horizontally."""
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


def create_slide(slide_num, total, slide_type, **kwargs):
    """Create a single slide image.

    slide_type: 'titulo', 'contexto', 'conteudo', 'resumo', 'cta'
    """
    img = Image.new("RGB", (W, H), BG_COLOR)
    draw = ImageDraw.Draw(img)

    draw_header(img, draw)
    draw_progress_bar(draw, slide_num, total)

    content_top = HEADER_H + 30
    content_bottom = H - FOOTER_H - 20
    content_area = content_bottom - content_top
    usable_width = W - 2 * PADDING

    if slide_type == "titulo":
        # Big title centered
        title = kwargs.get("titulo", "Titulo")
        subtitle = kwargs.get("subtitulo", "")

        title_font = load_font(bold=True, size=48)
        y = content_top + content_area // 4

        # Accent line
        line_w = 80
        draw.rounded_rectangle(
            ((W - line_w) // 2, y - 30, (W + line_w) // 2, y - 24),
            radius=3, fill=ACCENT
        )

        y = text_center(draw, title, y, title_font, fill=WHITE, max_width=usable_width - 40)

        if subtitle:
            y += 20
            sub_font = load_font(bold=False, size=28)
            text_center(draw, subtitle, y, sub_font, fill=LIGHT_GRAY, max_width=usable_width - 60)

    elif slide_type == "contexto":
        # Problem/context card
        title = kwargs.get("titulo", "Contexto")
        texto = kwargs.get("texto", "")

        title_font = load_font(bold=True, size=36)
        text_font = load_font(bold=False, size=26)

        card_top = content_top + 40
        card_bottom = content_bottom - 40
        draw_rounded_rect(draw, (PADDING, card_top, W - PADDING, card_bottom), CARD_RADIUS, CARD_COLOR)

        y = card_top + 40
        # Title with accent
        draw.rounded_rectangle(
            (PADDING + 30, y, PADDING + 36, y + 36),
            radius=3, fill=ACCENT
        )
        draw.text((PADDING + 50, y), title, fill=WHITE, font=title_font)
        y += 60

        # Text
        lines = wrap_text(texto, text_font, usable_width - 100, draw)
        for line in lines:
            draw.text((PADDING + 50, y), line, fill=LIGHT_GRAY, font=text_font)
            y += 40

    elif slide_type == "conteudo":
        # Numbered content item
        numero = kwargs.get("numero", 1)
        titulo_item = kwargs.get("titulo", "Item")
        texto = kwargs.get("texto", "")

        # Number circle
        num_size = 70
        num_x = PADDING + 20
        num_y = content_top + 30
        draw.ellipse(
            (num_x, num_y, num_x + num_size, num_y + num_size),
            fill=ACCENT
        )
        num_font = load_font(bold=True, size=36)
        bbox = draw.textbbox((0, 0), str(numero), font=num_font)
        nw = bbox[2] - bbox[0]
        nh = bbox[3] - bbox[1]
        draw.text(
            (num_x + (num_size - nw) // 2, num_y + (num_size - nh) // 2 - 4),
            str(numero), fill=BG_COLOR, font=num_font
        )

        # Title
        title_font = load_font(bold=True, size=34)
        title_x = num_x + num_size + 20
        draw.text((title_x, num_y + 15), titulo_item, fill=WHITE, font=title_font)

        # Content card
        card_top = num_y + num_size + 30
        card_bottom = content_bottom - 40
        draw_rounded_rect(draw, (PADDING, card_top, W - PADDING, card_bottom), CARD_RADIUS, CARD_COLOR)

        text_font = load_font(bold=False, size=26)
        y = card_top + 30
        lines = wrap_text(texto, text_font, usable_width - 80, draw)
        for line in lines:
            draw.text((PADDING + 40, y), line, fill=LIGHT_GRAY, font=text_font)
            y += 40

    elif slide_type == "resumo":
        # Summary with bullet points
        titulo = kwargs.get("titulo", "Resumo")
        itens = kwargs.get("itens", [])

        title_font = load_font(bold=True, size=36)
        y = content_top + 30
        text_center(draw, titulo, y, title_font, fill=ACCENT)
        y += 60

        item_font = load_font(bold=False, size=26)
        for item in itens:
            card_h = 80
            draw_rounded_rect(
                draw, (PADDING, y, W - PADDING, y + card_h),
                CARD_RADIUS, CARD_COLOR
            )
            # Accent dot
            draw.ellipse((PADDING + 20, y + 30, PADDING + 32, y + 42), fill=ACCENT)
            lines = wrap_text(item, item_font, usable_width - 80, draw)
            ly = y + 25
            for line in lines:
                draw.text((PADDING + 50, ly), line, fill=WHITE, font=item_font)
                ly += 32
            y += card_h + 15

    elif slide_type == "cta":
        # Call to action
        titulo = kwargs.get("titulo", "Gostou?")
        acoes = kwargs.get("acoes", ["Salve para consultar depois", "Comente sua experiencia", "Siga @matheus-zacche"])

        title_font = load_font(bold=True, size=42)
        y = content_top + content_area // 5
        text_center(draw, titulo, y, title_font, fill=WHITE)
        y += 80

        action_font = load_font(bold=False, size=28)
        icons = ["💾", "💬", "➕"]
        for i, acao in enumerate(acoes):
            icon = icons[i] if i < len(icons) else ">"
            card_y = y + i * 100
            draw_rounded_rect(
                draw, (PADDING + 40, card_y, W - PADDING - 40, card_y + 80),
                CARD_RADIUS, CARD_COLOR
            )
            draw.text((PADDING + 70, card_y + 22), f"{icon}  {acao}", fill=WHITE, font=action_font)

        # Handle at bottom
        handle_font = load_font(bold=True, size=24)
        text_center(draw, "@matheus-zacche", content_bottom - 40, handle_font, fill=ACCENT)

    return img


def gerar_carrossel(titulo, subtitulo, contexto_titulo, contexto_texto,
                     slides_conteudo, resumo_itens,
                     cta_titulo="Gostou do conteudo?",
                     output_name="carrossel"):
    """Generate complete carousel.

    Args:
        titulo: Main title (slide 1)
        subtitulo: Subtitle (slide 1)
        contexto_titulo: Context section title (slide 2)
        contexto_texto: Context text (slide 2)
        slides_conteudo: List of dicts with keys 'titulo' and 'texto' (slides 3-6)
        resumo_itens: List of strings for summary (slide 7)
        cta_titulo: CTA title (slide 8)
        output_name: Base filename for output
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    total = 8
    images = []

    # Slide 1: Titulo
    img1 = create_slide(1, total, "titulo", titulo=titulo, subtitulo=subtitulo)
    images.append(img1)

    # Slide 2: Contexto
    img2 = create_slide(2, total, "contexto", titulo=contexto_titulo, texto=contexto_texto)
    images.append(img2)

    # Slides 3-6: Conteudo
    for i, item in enumerate(slides_conteudo[:4]):
        img = create_slide(i + 3, total, "conteudo",
                          numero=i + 1,
                          titulo=item["titulo"],
                          texto=item["texto"])
        images.append(img)

    # Fill remaining content slides if less than 4
    while len(images) < 6:
        images.append(create_slide(len(images) + 1, total, "conteudo",
                                   numero=len(images) - 1,
                                   titulo="...", texto="..."))

    # Slide 7: Resumo
    img7 = create_slide(7, total, "resumo", titulo="Resumindo", itens=resumo_itens)
    images.append(img7)

    # Slide 8: CTA
    img8 = create_slide(8, total, "cta", titulo=cta_titulo)
    images.append(img8)

    # Save individual PNGs
    png_paths = []
    for i, img in enumerate(images):
        path = os.path.join(OUTPUT_DIR, f"{output_name}_slide_{i+1}.png")
        img.save(path, "PNG")
        png_paths.append(path)

    # Combine into PDF
    pdf_path = os.path.join(OUTPUT_DIR, f"{output_name}.pdf")
    rgb_images = [img.convert("RGB") for img in images]
    rgb_images[0].save(pdf_path, "PDF", save_all=True, append_images=rgb_images[1:])

    print(f"Carrossel gerado com sucesso!")
    print(f"  PNGs: {len(png_paths)} slides em {OUTPUT_DIR}")
    print(f"  PDF:  {pdf_path}")
    return pdf_path, png_paths


# === TEST ===
if __name__ == "__main__":
    pdf, pngs = gerar_carrossel(
        titulo="5 Erros Comuns\nno Power BI",
        subtitulo="E como evitar cada um deles",
        contexto_titulo="O problema",
        contexto_texto="Muitos analistas cometem os mesmos erros ao criar dashboards no Power BI. O resultado: relatorios lentos, dados errados e decisoes ruins. Vou mostrar os 5 erros que eu mesmo cometia e como corrigi.",
        slides_conteudo=[
            {"titulo": "Nao modelar os dados",
             "texto": "Jogar tudo numa tabela unica parece rapido, mas trava o dashboard. Crie um modelo estrela com fatos e dimensoes. Seu Power BI vai agradecer."},
            {"titulo": "Medidas implicitas",
             "texto": "Arrastar campos direto no visual cria medidas implicitas que voce nao controla. Sempre crie medidas DAX explicitas. Voce ganha controle total."},
            {"titulo": "Visuais demais",
             "texto": "Dashboard com 15 graficos nao informa, confunde. Regra: maximo 6 visuais por pagina. Foque no que o gestor precisa decidir."},
            {"titulo": "Ignorar o refresh",
             "texto": "Dados desatualizados destroem confianca. Configure refresh automatico ou alerte o usuario sobre a data de atualizacao."},
        ],
        resumo_itens=[
            "Modele seus dados (estrela)",
            "Use medidas DAX explicitas",
            "Maximo 6 visuais por pagina",
            "Configure refresh automatico",
        ],
        cta_titulo="Gostou do conteudo?",
        output_name="carrossel_powerbi_test"
    )
