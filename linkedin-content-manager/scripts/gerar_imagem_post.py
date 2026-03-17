# -*- coding: utf-8 -*-
"""
=============================================================================
Gerador de Imagens para Posts LinkedIn - Matheus Zacché
=============================================================================

Este script gera imagens profissionais para acompanhar posts do LinkedIn.
São 4 tipos de imagem disponíveis:

  1. DESTAQUE  → Título grande com subtítulo. Para opiniões, reflexões, tendências.
  2. COMPARATIVO → Antes vs Depois lado a lado. Para cases, transformações.
  3. LISTA → Itens numerados em cards. Para dicas, ferramentas, recomendações.
  4. DIAGRAMA → Fluxo com setas entre etapas. Para tutoriais, pipelines.

Todas seguem o mesmo design system:
  - Fundo escuro (#1a1a2e) com cards (#2a2a4a)
  - Cor de destaque cyan (#00d4aa)
  - Header com foto circular do Matheus + nome + badge
  - Auto-crop: remove espaço vazio na parte inferior

Como usar:
  - Direto: python gerar_imagem_post.py  (roda os testes)
  - Import: from gerar_imagem_post import gerar_imagem_post

Dependências:
  - Pillow (PIL) → pip install Pillow
  - Font Noto Sans em assets/ (com fallback para Arial)
"""

import os
from PIL import Image, ImageDraw, ImageFont


# =============================================================================
# CAMINHOS DOS ARQUIVOS
# =============================================================================
# Descobre automaticamente onde estão os assets e onde salvar output.
# SCRIPT_DIR = pasta onde este .py está (scripts/)
# SKILL_DIR  = pasta pai (linkedin-content-manager/)
# ASSETS_DIR = onde ficam fontes e foto (assets/)
# OUTPUT_DIR = onde as imagens geradas são salvas (output/)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(SCRIPT_DIR)
ASSETS_DIR = os.path.join(SKILL_DIR, "assets")
OUTPUT_DIR = os.path.join(SKILL_DIR, "output")

# Caminhos específicos dos assets
PHOTO_PATH = os.path.join(ASSETS_DIR, "foto_matheus.jpeg")   # Foto do perfil
FONT_REGULAR = os.path.join(ASSETS_DIR, "NotoSans-Regular.ttf")  # Fonte normal
FONT_BOLD = os.path.join(ASSETS_DIR, "NotoSans-Bold.ttf")        # Fonte negrito


# =============================================================================
# CONSTANTES DE DESIGN
# =============================================================================
# Todas as imagens do LinkedIn são 1080px de largura.
# Altura padrão 1350px (formato 4:5, ideal para feed).
# O header ocupa 140px no topo com foto + nome + badge.
# PADDING de 60px nas laterais para respiro visual.

W = 1080            # Largura da imagem em pixels
H = 1350            # Altura máxima (pode ser reduzida pelo auto_crop)
HEADER_H = 140      # Altura reservada para o header (foto + nome)
PADDING = 60        # Margem lateral em pixels
CARD_RADIUS = 20    # Raio de arredondamento dos cards
PHOTO_SIZE = 80     # Tamanho da foto circular em pixels
PHOTO_TOP = 30      # Distância do topo até a foto

# --- Paleta de cores ---
# Mesmo padrão visual do gerar_carrossel.py para manter consistência
BG_COLOR = "#1a1a2e"      # Fundo principal (azul muito escuro)
CARD_COLOR = "#2a2a4a"    # Fundo dos cards (azul escuro um pouco mais claro)
ACCENT = "#00d4aa"        # Cor de destaque (cyan/verde-água)
WHITE = "#ffffff"          # Texto principal
LIGHT_GRAY = "#b0b0c0"    # Texto secundário (descrições, subtítulos)
DARK_GRAY = "#3a3a5a"     # Elementos de fundo mais claros
RED_SOFT = "#ff6b6b"       # Vermelho suave → usado no "ANTES" do comparativo
GREEN_SOFT = "#51cf66"     # Verde suave → usado no "DEPOIS" do comparativo


# =============================================================================
# FUNÇÕES UTILITÁRIAS
# =============================================================================
# Estas funções são compartilhadas por todos os tipos de imagem.
# São praticamente iguais às do gerar_carrossel.py (mesmo design system).


def load_font(bold=False, size=24):
    """
    Carrega a fonte Noto Sans do diretório assets/.

    Ordem de tentativa:
      1. NotoSans-Bold.ttf ou NotoSans-Regular.ttf em assets/
      2. Arial (arialbd.ttf / arial.ttf) como fallback do sistema
      3. Fonte padrão do Pillow (último recurso, sem controle de tamanho)

    Parâmetros:
        bold (bool): Se True, carrega a versão negrito
        size (int): Tamanho da fonte em pixels

    Retorna:
        ImageFont: Objeto de fonte pronto para uso no Pillow
    """
    path = FONT_BOLD if bold else FONT_REGULAR
    try:
        return ImageFont.truetype(path, size)
    except (OSError, IOError):
        # Fallback 1: Arial do Windows
        try:
            fallback = "arialbd.ttf" if bold else "arial.ttf"
            return ImageFont.truetype(fallback, size)
        except (OSError, IOError):
            # Fallback 2: fonte padrão do Pillow (bitmap, não escala bem)
            return ImageFont.load_default()


def make_circular_photo(size=PHOTO_SIZE):
    """
    Cria a foto circular do Matheus para o header.

    Processo:
      1. Abre foto_matheus.jpeg (720x1280, vertical)
      2. Recorta um quadrado central (720x720) → pega o rosto
      3. Redimensiona para o tamanho desejado (80x80 padrão)
      4. Aplica máscara circular (pixels fora do círculo ficam transparentes)

    Se a foto não existir, gera um círculo cyan como placeholder.

    Parâmetros:
        size (int): Diâmetro do círculo em pixels

    Retorna:
        Image: Imagem RGBA com a foto recortada em círculo
    """
    try:
        photo = Image.open(PHOTO_PATH).convert("RGBA")
        pw, ph = photo.size

        # Recorta quadrado central (foca no rosto)
        crop_size = min(pw, ph)
        left = (pw - crop_size) // 2
        photo = photo.crop((left, 0, left + crop_size, crop_size))

        # Redimensiona para o tamanho final
        photo = photo.resize((size, size), Image.LANCZOS)

        # Cria máscara circular: branco = visível, preto = transparente
        mask = Image.new("L", (size, size), 0)
        ImageDraw.Draw(mask).ellipse((0, 0, size, size), fill=255)
        photo.putalpha(mask)

        return photo
    except (FileNotFoundError, IOError):
        # Fallback: círculo cyan sólido (quando a foto não está disponível)
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        ImageDraw.Draw(img).ellipse((0, 0, size, size), fill=ACCENT)
        return img


def draw_header(img, draw):
    """
    Desenha o header padrão no topo da imagem.

    Layout do header:
      [Foto circular]  Matheus Zacche
                       [Analista de Dados]  ← badge com fundo cyan
                       @matheus-zacche      ← handle em cinza claro

    Este header aparece em TODOS os tipos de imagem para manter
    a identidade visual consistente.

    Parâmetros:
        img (Image): Imagem PIL onde o header será desenhado
        draw (ImageDraw): Objeto de desenho da imagem
    """
    # --- Foto circular ---
    photo = make_circular_photo()
    photo_x = PADDING
    photo_y = PHOTO_TOP
    # paste() com 3º arg = máscara de transparência (RGBA)
    img.paste(photo, (photo_x, photo_y), photo)

    # --- Nome "Matheus Zacche" ---
    name_x = photo_x + PHOTO_SIZE + 16  # 16px de espaço após a foto
    name_font = load_font(bold=True, size=28)
    draw.text((name_x, photo_y + 8), "Matheus Zacche", fill=WHITE, font=name_font)

    # --- Badge "Analista de Dados" com fundo cyan ---
    badge_font = load_font(bold=False, size=18)
    badge_text = "Analista de Dados"
    badge_y = photo_y + 42  # Logo abaixo do nome

    # Calcula tamanho do badge dinamicamente baseado no texto
    bbox = draw.textbbox((0, 0), badge_text, font=badge_font)
    bw = bbox[2] - bbox[0] + 20   # largura do texto + 20px de padding
    bh = bbox[3] - bbox[1] + 10   # altura do texto + 10px de padding

    # Retângulo arredondado de fundo
    draw.rounded_rectangle(
        (name_x, badge_y, name_x + bw, badge_y + bh),
        radius=10, fill=ACCENT
    )
    # Texto do badge (cor escura sobre fundo cyan)
    draw.text((name_x + 10, badge_y + 3), badge_text, fill=BG_COLOR, font=badge_font)

    # --- Handle "@matheus-zacche" ---
    handle_font = load_font(bold=False, size=16)
    draw.text((name_x, badge_y + bh + 6), "@matheus-zacche", fill=LIGHT_GRAY, font=handle_font)


def wrap_text(text, font, max_width, draw):
    """
    Quebra um texto longo em múltiplas linhas que cabem na largura máxima.

    Algoritmo:
      - Percorre palavra por palavra
      - Testa se adicionar a próxima palavra ultrapassa max_width
      - Se sim, inicia nova linha
      - Se não, continua na mesma linha

    Parâmetros:
        text (str): Texto a ser quebrado
        font (ImageFont): Fonte para calcular largura
        max_width (int): Largura máxima em pixels
        draw (ImageDraw): Necessário para textbbox()

    Retorna:
        list[str]: Lista de linhas que cabem na largura
    """
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        # Tenta adicionar a palavra na linha atual
        test = f"{current_line} {word}".strip()
        bbox = draw.textbbox((0, 0), test, font=font)
        text_width = bbox[2] - bbox[0]

        if text_width <= max_width:
            # Cabe! Continua na mesma linha
            current_line = test
        else:
            # Não cabe! Salva linha atual e começa nova
            if current_line:
                lines.append(current_line)
            current_line = word

    # Não esquecer a última linha
    if current_line:
        lines.append(current_line)

    return lines


def text_center(draw, text, y, font, fill=WHITE, max_width=None):
    """
    Desenha texto centralizado horizontalmente na imagem.

    Se max_width for fornecido, quebra o texto em múltiplas linhas
    antes de centralizar cada uma.

    Parâmetros:
        draw (ImageDraw): Objeto de desenho
        text (str): Texto a desenhar
        y (int): Posição vertical (topo do texto)
        font (ImageFont): Fonte a usar
        fill (str): Cor do texto (hex ou nome)
        max_width (int|None): Se definido, quebra texto nessa largura

    Retorna:
        int: Próxima posição Y disponível (abaixo do texto desenhado)
    """
    if max_width:
        # Modo multi-linha: quebra e centraliza cada linha
        lines = wrap_text(text, font, max_width, draw)
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            tw = bbox[2] - bbox[0]
            x = (W - tw) // 2  # Centraliza: (largura_imagem - largura_texto) / 2
            draw.text((x, y), line, fill=fill, font=font)
            y += bbox[3] - bbox[1] + 8  # Avança Y + 8px de espaçamento
        return y
    else:
        # Modo linha única
        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        x = (W - tw) // 2
        draw.text((x, y), text, fill=fill, font=font)
        return y + bbox[3] - bbox[1] + 8


def auto_crop_bottom(img, bg_hex=BG_COLOR):
    """
    Remove espaço vazio (fundo sólido) da parte inferior da imagem.

    Problema: As imagens são criadas com altura fixa de 1350px, mas nem
    sempre todo o conteúdo ocupa esse espaço. O resultado seria uma
    imagem com muito espaço vazio embaixo.

    Solução: Escaneia de baixo para cima, pixel a pixel, procurando
    a última linha que tem conteúdo (cor diferente do fundo).
    Depois recorta a imagem até ali + 80px de margem.

    Otimização: Analisa apenas 1 a cada 4 pixels por linha (step=4)
    para ser mais rápido sem perder precisão.

    Parâmetros:
        img (Image): Imagem a ser cortada
        bg_hex (str): Cor do fundo em hex (ex: "#1a1a2e")

    Retorna:
        Image: Imagem recortada (ou original se não houver espaço vazio)
    """
    # Converte a cor hex do fundo para RGB (tupla de inteiros)
    bg = bg_hex.lstrip("#")
    bg_rgb = tuple(int(bg[i:i+2], 16) for i in (0, 2, 4))
    tolerance = 10  # Tolerância para variações de cor (anti-aliasing etc)

    pixels = img.load()  # Acesso direto aos pixels (mais rápido que getpixel)
    w, h = img.size
    last_content_y = h - 1  # Começa assumindo que o conteúdo vai até embaixo

    # Escaneia de baixo para cima, linha por linha
    for y in range(h - 1, HEADER_H, -1):
        row_has_content = False
        # Verifica 1 a cada 4 pixels na linha (otimização)
        for x in range(0, w, 4):
            # Extrai RGB do pixel (pode ser tupla RGBA ou valor escalar)
            r, g, b = pixels[x, y][:3] if isinstance(pixels[x, y], tuple) else (pixels[x, y], pixels[x, y], pixels[x, y])

            # Se algum canal difere do fundo além da tolerância → tem conteúdo
            if (abs(r - bg_rgb[0]) > tolerance or
                abs(g - bg_rgb[1]) > tolerance or
                abs(b - bg_rgb[2]) > tolerance):
                row_has_content = True
                break

        if row_has_content:
            last_content_y = y
            break  # Encontrou! Não precisa continuar subindo

    # Adiciona 80px de margem abaixo do último conteúdo
    crop_y = min(last_content_y + 80, h)

    # Garante altura mínima: pelo menos quadrada (1080x1080)
    crop_y = max(crop_y, W)

    # Só recorta se realmente for menor que o original
    if crop_y < h:
        return img.crop((0, 0, w, crop_y))
    return img


# =============================================================================
# TIPO 1: DESTAQUE
# =============================================================================
# Imagem com título grande e centralizado + subtítulo opcional.
# Ideal para: opiniões, reflexões, tendências, frases de impacto.
# Visual: linha decorativa cyan + título grande + subtítulo menor em cinza.

def gerar_destaque(titulo, subtitulo="", output_name="destaque"):
    """
    Gera imagem tipo DESTAQUE: título grande centralizado com subtítulo.

    Layout:
      ┌──────────────────────────┐
      │  [foto] Matheus Zacche   │  ← header padrão
      │         Analista de Dados│
      │                          │
      │       ══════════         │  ← linha decorativa cyan
      │                          │
      │    TÍTULO GRANDE AQUI    │  ← fonte 52px bold, branco
      │                          │
      │    Subtítulo menor aqui  │  ← fonte 30px regular, cinza
      │                          │
      └──────────────────────────┘

    Parâmetros:
        titulo (str): Texto principal (grande, centralizado)
        subtitulo (str): Texto secundário opcional (menor, cinza)
        output_name (str): Nome do arquivo de saída (sem extensão)

    Retorna:
        str: Caminho completo do PNG gerado
    """
    # Cria imagem base com fundo escuro
    img = Image.new("RGB", (W, H), BG_COLOR)
    draw = ImageDraw.Draw(img)
    draw_header(img, draw)

    usable_width = W - 2 * PADDING  # Largura útil (descontando margens)
    content_top = HEADER_H + 60     # Começa 60px abaixo do header

    # --- Linha decorativa cyan (100px de largura, 6px de altura) ---
    line_w = 100
    y = content_top + 80
    draw.rounded_rectangle(
        ((W - line_w) // 2, y, (W + line_w) // 2, y + 6),
        radius=3, fill=ACCENT
    )
    y += 40

    # --- Título principal ---
    title_font = load_font(bold=True, size=52)
    y = text_center(draw, titulo, y, title_font, fill=WHITE, max_width=usable_width - 40)

    # --- Subtítulo (opcional) ---
    if subtitulo:
        y += 30  # Espaço entre título e subtítulo
        sub_font = load_font(bold=False, size=30)
        text_center(draw, subtitulo, y, sub_font, fill=LIGHT_GRAY, max_width=usable_width - 80)

    # Recorta espaço vazio e salva
    img = auto_crop_bottom(img)
    path = os.path.join(OUTPUT_DIR, f"{output_name}.png")
    img.save(path, "PNG")
    print(f"Imagem destaque salva: {path}")
    return path


# =============================================================================
# TIPO 2: COMPARATIVO
# =============================================================================
# Dois cards lado a lado: ANTES (vermelho) e DEPOIS (verde).
# Ideal para: cases de automação, antes/depois de dashboards, transformações.
# Visual: card esquerdo com barra vermelha + card direito com barra verde.

def gerar_comparativo(titulo, antes_titulo, antes_itens, depois_titulo, depois_itens, output_name="comparativo"):
    """
    Gera imagem tipo COMPARATIVO: dois cards lado a lado (antes vs depois).

    Layout:
      ┌────────────────────────────────┐
      │  [foto] Matheus Zacche         │
      │                                │
      │      Título do Comparativo     │
      │                                │
      │  ┌─ ANTES ──┐  ┌─ DEPOIS ──┐  │
      │  │ vermelho  │  │  verde    │  │
      │  │ x item 1  │>│ ✓ item 1  │  │
      │  │ x item 2  │ │ ✓ item 2  │  │
      │  │ x item 3  │ │ ✓ item 3  │  │
      │  └───────────┘  └───────────┘  │
      └────────────────────────────────┘

    Parâmetros:
        titulo (str): Título geral do comparativo
        antes_titulo (str): Rótulo do card esquerdo (ex: "ANTES")
        antes_itens (list[str]): Lista de itens negativos
        depois_titulo (str): Rótulo do card direito (ex: "DEPOIS")
        depois_itens (list[str]): Lista de itens positivos
        output_name (str): Nome do arquivo de saída

    Retorna:
        str: Caminho completo do PNG gerado
    """
    img = Image.new("RGB", (W, H), BG_COLOR)
    draw = ImageDraw.Draw(img)
    draw_header(img, draw)

    usable_width = W - 2 * PADDING
    content_top = HEADER_H + 30

    # --- Título centralizado ---
    title_font = load_font(bold=True, size=36)
    y = text_center(draw, titulo, content_top, title_font, fill=WHITE, max_width=usable_width)
    y += 30

    # --- Calcula dimensões dos cards ---
    # Dois cards lado a lado com 30px de espaço entre eles
    card_width = (usable_width - 30) // 2
    card_x_left = PADDING                      # Posição X do card esquerdo
    card_x_right = PADDING + card_width + 30   # Posição X do card direito

    # Altura dos cards: baseada no número de itens (o maior dos dois)
    item_font = load_font(bold=False, size=22)
    max_items = max(len(antes_itens), len(depois_itens))
    card_h = 80 + max_items * 50 + 20  # 80 header + 50 por item + 20 padding

    # === CARD ESQUERDO: ANTES (vermelho) ===
    # Fundo do card
    draw.rounded_rectangle(
        (card_x_left, y, card_x_left + card_width, y + card_h),
        radius=CARD_RADIUS, fill=CARD_COLOR
    )
    # Barra vermelha no topo do card (6px de altura)
    draw.rounded_rectangle(
        (card_x_left, y, card_x_left + card_width, y + 6),
        radius=3, fill=RED_SOFT
    )
    # Título "ANTES" em vermelho
    antes_font = load_font(bold=True, size=26)
    draw.text((card_x_left + 20, y + 20), antes_titulo, fill=RED_SOFT, font=antes_font)
    # Itens com "x" (indica negativo/problema)
    iy = y + 65
    for item in antes_itens:
        draw.text((card_x_left + 20, iy), f"x  {item}", fill=LIGHT_GRAY, font=item_font)
        iy += 45

    # === CARD DIREITO: DEPOIS (verde) ===
    # Fundo do card
    draw.rounded_rectangle(
        (card_x_right, y, card_x_right + card_width, y + card_h),
        radius=CARD_RADIUS, fill=CARD_COLOR
    )
    # Barra verde no topo do card
    draw.rounded_rectangle(
        (card_x_right, y, card_x_right + card_width, y + 6),
        radius=3, fill=GREEN_SOFT
    )
    # Título "DEPOIS" em verde
    depois_font = load_font(bold=True, size=26)
    draw.text((card_x_right + 20, y + 20), depois_titulo, fill=GREEN_SOFT, font=depois_font)
    # Itens com "✓" (indica positivo/solução)
    iy = y + 65
    for item in depois_itens:
        draw.text((card_x_right + 20, iy), f"✓  {item}", fill=WHITE, font=item_font)
        iy += 45

    # --- Seta ">" entre os dois cards ---
    arrow_y = y + card_h // 2
    arrow_x = PADDING + card_width + 5
    arrow_font = load_font(bold=True, size=28)
    draw.text((arrow_x, arrow_y - 14), ">", fill=ACCENT, font=arrow_font)

    # Recorta e salva
    img = auto_crop_bottom(img)
    path = os.path.join(OUTPUT_DIR, f"{output_name}.png")
    img.save(path, "PNG")
    print(f"Imagem comparativo salva: {path}")
    return path


# =============================================================================
# TIPO 3: LISTA
# =============================================================================
# Itens numerados em cards individuais com número em círculo cyan.
# Ideal para: "5 ferramentas que uso", "7 dicas de...", rankings.
# Cada item pode ter título + descrição opcional.

def gerar_lista(titulo, itens, output_name="lista"):
    """
    Gera imagem tipo LISTA: itens numerados em cards.

    Layout:
      ┌──────────────────────────────┐
      │  [foto] Matheus Zacche       │
      │                              │
      │    5 Ferramentas que Uso     │
      │                              │
      │  ┌─────────────────────────┐ │
      │  │ (1) Python              │ │
      │  │     Automação e ETL     │ │
      │  └─────────────────────────┘ │
      │  ┌─────────────────────────┐ │
      │  │ (2) Power BI            │ │
      │  │     Dashboards e KPIs   │ │
      │  └─────────────────────────┘ │
      │  ...                         │
      └──────────────────────────────┘

    Os itens podem ser:
      - Strings simples: ["Python", "Power BI"]
      - Dicts com título+descrição: [{"titulo": "Python", "descricao": "ETL"}]

    Parâmetros:
        titulo (str): Título geral da lista
        itens (list): Lista de strings ou dicts com titulo/descricao
        output_name (str): Nome do arquivo de saída

    Retorna:
        str: Caminho completo do PNG gerado
    """
    img = Image.new("RGB", (W, H), BG_COLOR)
    draw = ImageDraw.Draw(img)
    draw_header(img, draw)

    usable_width = W - 2 * PADDING
    content_top = HEADER_H + 30

    # --- Título centralizado ---
    title_font = load_font(bold=True, size=36)
    y = text_center(draw, titulo, content_top, title_font, fill=WHITE, max_width=usable_width)
    y += 30

    # Fontes para os itens
    item_title_font = load_font(bold=True, size=26)    # Título do item
    item_desc_font = load_font(bold=False, size=22)     # Descrição do item

    for i, item in enumerate(itens):
        # Suporta tanto strings simples quanto dicts
        if isinstance(item, dict):
            item_titulo = item.get("titulo", "")
            item_desc = item.get("descricao", "")
        else:
            item_titulo = str(item)
            item_desc = ""

        # Calcula altura do card baseado no conteúdo
        # Quebra texto para saber quantas linhas serão necessárias
        lines_titulo = wrap_text(item_titulo, item_title_font, usable_width - 130, draw)
        lines_desc = wrap_text(item_desc, item_desc_font, usable_width - 130, draw) if item_desc else []
        card_h = 30 + len(lines_titulo) * 36 + len(lines_desc) * 32 + 20

        # --- Card de fundo ---
        draw.rounded_rectangle(
            (PADDING, y, W - PADDING, y + card_h),
            radius=CARD_RADIUS, fill=CARD_COLOR
        )

        # --- Número em círculo cyan ---
        num_size = 44  # Diâmetro do círculo
        num_x = PADDING + 20
        num_y_center = y + card_h // 2 - num_size // 2  # Centraliza verticalmente

        # Desenha o círculo de fundo
        draw.ellipse(
            (num_x, num_y_center, num_x + num_size, num_y_center + num_size),
            fill=ACCENT
        )

        # Centraliza o número dentro do círculo
        num_font = load_font(bold=True, size=22)
        bbox = draw.textbbox((0, 0), str(i + 1), font=num_font)
        nw = bbox[2] - bbox[0]  # Largura do número
        nh = bbox[3] - bbox[1]  # Altura do número
        draw.text(
            (num_x + (num_size - nw) // 2, num_y_center + (num_size - nh) // 2 - 2),
            str(i + 1), fill=BG_COLOR, font=num_font
        )

        # --- Texto do item (à direita do número) ---
        text_x = num_x + num_size + 20  # 20px após o círculo
        ty = y + 15

        # Título do item (branco, bold)
        for line in lines_titulo:
            draw.text((text_x, ty), line, fill=WHITE, font=item_title_font)
            ty += 36

        # Descrição do item (cinza, regular)
        for line in lines_desc:
            draw.text((text_x, ty), line, fill=LIGHT_GRAY, font=item_desc_font)
            ty += 32

        y += card_h + 15  # 15px de espaço entre cards

    # Recorta e salva
    img = auto_crop_bottom(img)
    path = os.path.join(OUTPUT_DIR, f"{output_name}.png")
    img.save(path, "PNG")
    print(f"Imagem lista salva: {path}")
    return path


# =============================================================================
# TIPO 4: DIAGRAMA
# =============================================================================
# Fluxo/processo com caixas conectadas por setas verticais.
# Ideal para: pipelines de dados, tutoriais passo a passo, processos.
# Cada etapa tem badge numérico + título + descrição opcional.

def gerar_diagrama(titulo, etapas, output_name="diagrama"):
    """
    Gera imagem tipo DIAGRAMA: fluxo com setas entre etapas.

    Layout:
      ┌──────────────────────────────────┐
      │  [foto] Matheus Zacche           │
      │                                  │
      │  Pipeline de Dados: SAP → Power  │
      │                                  │
      │    ┌──────────────────────────┐  │
      │    │ [1] Extrair do SAP      │  │
      │    │     Python conecta RFC  │  │
      │    └──────────────────────────┘  │
      │              |                   │
      │              v                   │
      │    ┌──────────────────────────┐  │
      │    │ [2] Transformar         │  │
      │    │     Limpeza e padrão    │  │
      │    └──────────────────────────┘  │
      │              |                   │
      │              v                   │
      │    ...                           │
      └──────────────────────────────────┘

    As etapas podem ser:
      - Strings: ["Extrair", "Transformar", "Carregar"]
      - Dicts: [{"titulo": "Extrair", "descricao": "Python RFC"}]

    Parâmetros:
        titulo (str): Título geral do diagrama
        etapas (list): Lista de strings ou dicts com titulo/descricao
        output_name (str): Nome do arquivo de saída

    Retorna:
        str: Caminho completo do PNG gerado
    """
    img = Image.new("RGB", (W, H), BG_COLOR)
    draw = ImageDraw.Draw(img)
    draw_header(img, draw)

    usable_width = W - 2 * PADDING
    content_top = HEADER_H + 30

    # --- Título centralizado ---
    title_font = load_font(bold=True, size=36)
    y = text_center(draw, titulo, content_top, title_font, fill=WHITE, max_width=usable_width)
    y += 40

    # Fontes para as etapas
    step_font = load_font(bold=True, size=24)    # Título da etapa
    desc_font = load_font(bold=False, size=20)    # Descrição da etapa
    arrow_font = load_font(bold=True, size=28)    # Setas "|" e "v"

    for i, etapa in enumerate(etapas):
        # Suporta strings simples ou dicts
        if isinstance(etapa, dict):
            etapa_titulo = etapa.get("titulo", "")
            etapa_desc = etapa.get("descricao", "")
        else:
            etapa_titulo = str(etapa)
            etapa_desc = ""

        # --- Caixa da etapa ---
        # Altura: 80px sem descrição, 110px com descrição
        box_h = 80 if not etapa_desc else 110
        draw.rounded_rectangle(
            (PADDING + 40, y, W - PADDING - 40, y + box_h),
            radius=CARD_RADIUS, fill=CARD_COLOR
        )

        # --- Badge numérico (quadrado arredondado com número) ---
        badge_w = 36
        draw.rounded_rectangle(
            (PADDING + 55, y + 15, PADDING + 55 + badge_w, y + 15 + badge_w),
            radius=8, fill=ACCENT
        )
        # Centraliza o número dentro do badge
        num_font_small = load_font(bold=True, size=20)
        bbox = draw.textbbox((0, 0), str(i + 1), font=num_font_small)
        nw = bbox[2] - bbox[0]
        draw.text(
            (PADDING + 55 + (badge_w - nw) // 2, y + 20),
            str(i + 1), fill=BG_COLOR, font=num_font_small
        )

        # --- Texto da etapa ---
        # Título (branco, bold) à direita do badge
        draw.text((PADDING + 105, y + 18), etapa_titulo, fill=WHITE, font=step_font)

        # Descrição (cinza) abaixo do título
        if etapa_desc:
            lines = wrap_text(etapa_desc, desc_font, usable_width - 160, draw)
            dy = y + 55
            for line in lines:
                draw.text((PADDING + 105, dy), line, fill=LIGHT_GRAY, font=desc_font)
                dy += 28

        y += box_h + 10

        # --- Seta entre etapas ("|" e "v" em cyan) ---
        # Não desenha seta após a última etapa
        if i < len(etapas) - 1:
            arrow_x = W // 2  # Centralizado
            draw.text((arrow_x - 8, y - 5), "|", fill=ACCENT, font=arrow_font)
            draw.text((arrow_x - 8, y + 10), "v", fill=ACCENT, font=arrow_font)
            y += 35

    # Recorta e salva
    img = auto_crop_bottom(img)
    path = os.path.join(OUTPUT_DIR, f"{output_name}.png")
    img.save(path, "PNG")
    print(f"Imagem diagrama salva: {path}")
    return path


# =============================================================================
# FUNÇÃO PRINCIPAL (DISPATCHER)
# =============================================================================
# Esta é a função que o agente chama. Ela recebe o tipo desejado e
# redireciona para a função específica com os parâmetros corretos.

def gerar_imagem_post(tipo, output_name="post_image", **kwargs):
    """
    Função principal para gerar imagem de post. Direciona para o tipo correto.

    Tipos disponíveis e seus parâmetros (passados via **kwargs):

      "destaque":
        - titulo (str): Texto principal
        - subtitulo (str, opcional): Texto secundário

      "comparativo":
        - titulo (str): Título geral
        - antes_titulo (str): Rótulo do ANTES
        - antes_itens (list[str]): Itens negativos
        - depois_titulo (str): Rótulo do DEPOIS
        - depois_itens (list[str]): Itens positivos

      "lista":
        - titulo (str): Título da lista
        - itens (list): Strings ou dicts com titulo/descricao

      "diagrama":
        - titulo (str): Título do fluxo
        - etapas (list): Strings ou dicts com titulo/descricao

    Parâmetros:
        tipo (str): Tipo de imagem a gerar
        output_name (str): Nome do arquivo (sem extensão .png)
        **kwargs: Argumentos específicos de cada tipo

    Retorna:
        str: Caminho completo do PNG gerado

    Levanta:
        ValueError: Se o tipo não for válido
    """
    # Garante que a pasta de saída existe
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


# =============================================================================
# TESTES
# =============================================================================
# Quando executado diretamente (python gerar_imagem_post.py), gera 4 imagens
# de teste, uma de cada tipo, na pasta output/.

if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Teste 1: Destaque (opinião/reflexão)
    gerar_imagem_post("destaque", "test_destaque",
                      titulo="Parei de fazer dashboards bonitos",
                      subtitulo="E meus relatorios ficaram melhores")

    # Teste 2: Comparativo (antes vs depois de automação)
    gerar_imagem_post("comparativo", "test_comparativo",
                      titulo="Relatorio de Incentivos",
                      antes_titulo="ANTES",
                      antes_itens=["7 horas por semana", "Erros manuais", "3 planilhas", "Copiar e colar"],
                      depois_titulo="DEPOIS",
                      depois_itens=["20 minutos", "Zero erros", "Automatizado", "Python + N8N"])

    # Teste 3: Lista (ferramentas do dia a dia)
    gerar_imagem_post("lista", "test_lista",
                      titulo="5 Ferramentas que Uso Todo Dia",
                      itens=[
                          {"titulo": "Python", "descricao": "Automacao e ETL"},
                          {"titulo": "Power BI", "descricao": "Dashboards e KPIs"},
                          {"titulo": "SQL", "descricao": "Consultas e analises"},
                          {"titulo": "N8N", "descricao": "Orquestracao de fluxos"},
                          {"titulo": "Airflow", "descricao": "Pipelines de dados"},
                      ])

    # Teste 4: Diagrama (pipeline de dados)
    gerar_imagem_post("diagrama", "test_diagrama",
                      titulo="Pipeline de Dados: SAP ao Power BI",
                      etapas=[
                          {"titulo": "Extrair do SAP", "descricao": "Python conecta via RFC"},
                          {"titulo": "Transformar", "descricao": "Limpeza e padronizacao"},
                          {"titulo": "Carregar no DW", "descricao": "SQL Server como staging"},
                          {"titulo": "Visualizar", "descricao": "Power BI com refresh automatico"},
                      ])

    print("\nTodos os testes concluidos!")
