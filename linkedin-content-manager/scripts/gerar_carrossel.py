# -*- coding: utf-8 -*-
"""
Gerador de Carrossel LinkedIn - Matheus Zacche
===============================================
Gera 8 slides PNG + 1 PDF combinado para upload no LinkedIn.

Estrutura dos 8 slides:
  1. Titulo (capa com titulo grande + subtitulo)
  2. Contexto (problema/cenario dentro de um card)
  3-6. Conteudo (4 itens numerados, 1 por slide)
  7. Resumo (bullet points com os pontos principais)
  8. CTA (call to action: salvar, comentar, seguir)

Design:
  - 1080x1350px (formato vertical ideal para LinkedIn)
  - Tema escuro: fundo #1a1a2e, cards #2a2a4a, accent #00d4aa
  - Header com foto circular do Matheus + badge "Analista de Dados"
  - Progress bar no footer mostrando slide atual/total

Uso:
    # Via terminal (roda o teste embutido):
    python gerar_carrossel.py

    # Via import em outro script ou chamada do agente:
    from gerar_carrossel import gerar_carrossel
    pdf, pngs = gerar_carrossel(titulo="...", subtitulo="...", ...)

    # Via python -c (como o agente Claude chama):
    python -c "from scripts.gerar_carrossel import gerar_carrossel; ..."
"""

import os
import textwrap
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# ============================================================================
# PATHS - Caminhos relativos ao script para funcionar em qualquer maquina
# ============================================================================
# __file__ aponta para este script. Subimos um nivel para chegar na skill root.
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(SCRIPT_DIR)  # pasta linkedin-content-manager/
ASSETS_DIR = os.path.join(SKILL_DIR, "assets")  # fontes e foto
OUTPUT_DIR = os.path.join(SKILL_DIR, "output")  # onde salva PNGs e PDFs

# Caminhos dos assets individuais
PHOTO_PATH = os.path.join(ASSETS_DIR, "foto_matheus.jpeg")
FONT_REGULAR = os.path.join(ASSETS_DIR, "NotoSans-Regular.ttf")
FONT_BOLD = os.path.join(ASSETS_DIR, "NotoSans-Bold.ttf")

# ============================================================================
# CONSTANTES DE DESIGN - Altere aqui para mudar o visual de TODOS os slides
# ============================================================================
W = 1080           # Largura do slide em pixels
H = 1350           # Altura do slide em pixels (formato 4:5 vertical)
HEADER_H = 140     # Altura reservada para o header (foto + nome)
FOOTER_H = 60      # Altura reservada para o footer (progress bar)
PADDING = 60       # Margem lateral em ambos os lados
CARD_RADIUS = 20   # Raio das bordas arredondadas dos cards

# Paleta de cores - tema escuro profissional
BG_COLOR = "#1a1a2e"    # Fundo principal (azul escuro)
CARD_COLOR = "#2a2a4a"  # Fundo dos cards (um tom mais claro)
ACCENT = "#00d4aa"      # Cor de destaque/accent (cyan/verde agua)
WHITE = "#ffffff"        # Texto principal
LIGHT_GRAY = "#b0b0c0"  # Texto secundario (subtitulos, descricoes)
DARK_GRAY = "#3a3a5a"   # Elementos sutis (barra de progresso fundo)

# Configuracoes da foto circular no header
PHOTO_SIZE = 80   # Diametro da foto em pixels
PHOTO_TOP = 30    # Distancia do topo ate a foto


# ============================================================================
# FUNCOES UTILITARIAS
# ============================================================================

def load_font(bold=False, size=24):
    """Carrega a fonte Noto Sans dos assets, com fallback para Arial.

    A Noto Sans foi escolhida por ter boa cobertura de caracteres
    (incluindo acentos em portugues) e ser visualmente limpa.

    Args:
        bold: Se True, carrega a versao Bold da fonte
        size: Tamanho da fonte em pixels

    Returns:
        Objeto ImageFont pronto para uso com Pillow
    """
    path = FONT_BOLD if bold else FONT_REGULAR
    try:
        return ImageFont.truetype(path, size)
    except (OSError, IOError):
        # Se Noto Sans nao estiver disponivel, tenta Arial (Windows)
        try:
            fallback = "arialbd.ttf" if bold else "arial.ttf"
            return ImageFont.truetype(fallback, size)
        except (OSError, IOError):
            # Ultimo recurso: fonte padrao do Pillow (sem anti-aliasing)
            return ImageFont.load_default()


def make_circular_photo(size=PHOTO_SIZE):
    """Cria foto circular recortada da foto_matheus.jpeg.

    A foto original e vertical (720x1280). O rosto esta na parte
    superior, entao cortamos do topo ao centro para capturar o rosto.
    Depois aplicamos uma mascara circular para o efeito de avatar.

    Args:
        size: Diametro do circulo em pixels

    Returns:
        Imagem RGBA com a foto circular (fundo transparente)
    """
    try:
        photo = Image.open(PHOTO_PATH).convert("RGBA")

        # Recortar quadrado do topo (onde esta o rosto)
        pw, ph = photo.size
        crop_size = min(pw, ph)  # Menor dimensao define o quadrado
        left = (pw - crop_size) // 2  # Centraliza horizontalmente
        top = 0  # Comeca do topo (rosto esta la)
        photo = photo.crop((left, top, left + crop_size, top + crop_size))

        # Redimensionar para o tamanho desejado
        photo = photo.resize((size, size), Image.LANCZOS)

        # Criar mascara circular: branco = visivel, preto = transparente
        mask = Image.new("L", (size, size), 0)
        ImageDraw.Draw(mask).ellipse((0, 0, size, size), fill=255)
        photo.putalpha(mask)  # Aplica a mascara como canal alpha
        return photo

    except (FileNotFoundError, IOError):
        # Se a foto nao existir, cria um circulo colorido como placeholder
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        ImageDraw.Draw(img).ellipse((0, 0, size, size), fill=ACCENT)
        return img


def draw_rounded_rect(draw, xy, radius, fill):
    """Desenha um retangulo com bordas arredondadas.

    Wrapper simples para draw.rounded_rectangle do Pillow.

    Args:
        draw: Objeto ImageDraw
        xy: Tupla (x0, y0, x1, y1) com coordenadas do retangulo
        radius: Raio das bordas arredondadas
        fill: Cor de preenchimento (hex string ou tupla RGB)
    """
    draw.rounded_rectangle(xy, radius=radius, fill=fill)


def draw_header(img, draw):
    """Desenha o header padrao em todos os slides.

    Componentes do header:
    - Foto circular do Matheus (canto superior esquerdo)
    - Nome "Matheus Zacche" em bold
    - Badge "Analista de Dados" com fundo accent
    - Handle "@matheus-zacche" em cinza claro

    Args:
        img: Imagem PIL onde colar a foto (precisa do paste com alpha)
        draw: Objeto ImageDraw para desenhar textos e shapes
    """
    # Foto circular
    photo = make_circular_photo()
    photo_x = PADDING
    photo_y = PHOTO_TOP
    img.paste(photo, (photo_x, photo_y), photo)  # 3o arg = mascara alpha

    # Nome em bold ao lado da foto
    name_x = photo_x + PHOTO_SIZE + 16  # 16px de gap apos a foto
    name_font = load_font(bold=True, size=28)
    draw.text((name_x, photo_y + 8), "Matheus Zacche", fill=WHITE, font=name_font)

    # Badge "Analista de Dados" com fundo accent
    badge_font = load_font(bold=False, size=18)
    badge_text = "Analista de Dados"
    badge_y = photo_y + 42  # Abaixo do nome
    # Calcular largura do badge dinamicamente baseado no texto
    bbox = draw.textbbox((0, 0), badge_text, font=badge_font)
    bw = bbox[2] - bbox[0] + 20  # +20 de padding horizontal
    bh = bbox[3] - bbox[1] + 10  # +10 de padding vertical
    draw.rounded_rectangle(
        (name_x, badge_y, name_x + bw, badge_y + bh),
        radius=10, fill=ACCENT
    )
    # Texto do badge em cor escura (contraste com fundo accent)
    draw.text((name_x + 10, badge_y + 3), badge_text, fill=BG_COLOR, font=badge_font)

    # Handle do LinkedIn abaixo do badge
    handle_font = load_font(bold=False, size=16)
    draw.text((name_x, badge_y + bh + 6), "@matheus-zacche", fill=LIGHT_GRAY, font=handle_font)


def draw_progress_bar(draw, current, total):
    """Desenha a barra de progresso no footer do slide.

    Mostra visualmente em qual slide o leitor esta (ex: 3/8).
    A parte preenchida usa a cor accent, o fundo usa cinza escuro.

    Args:
        draw: Objeto ImageDraw
        current: Numero do slide atual (1-based)
        total: Total de slides no carrossel
    """
    bar_y = H - FOOTER_H + 15  # Posicao vertical da barra
    bar_h = 6                   # Altura da barra (fina)
    bar_x = PADDING             # Comeca na margem esquerda
    bar_w = W - 2 * PADDING     # Largura = slide menos margens

    # Fundo da barra (cinza escuro, comprimento total)
    draw.rounded_rectangle(
        (bar_x, bar_y, bar_x + bar_w, bar_y + bar_h),
        radius=3, fill=DARK_GRAY
    )

    # Parte preenchida (accent, proporcional ao progresso)
    progress_w = int(bar_w * current / total)
    if progress_w > 0:
        draw.rounded_rectangle(
            (bar_x, bar_y, bar_x + progress_w, bar_y + bar_h),
            radius=3, fill=ACCENT
        )

    # Numero da pagina (ex: "3/8") no canto direito
    page_font = load_font(bold=False, size=16)
    page_text = f"{current}/{total}"
    bbox = draw.textbbox((0, 0), page_text, font=page_font)
    tw = bbox[2] - bbox[0]
    draw.text((W - PADDING - tw, bar_y + bar_h + 4), page_text, fill=LIGHT_GRAY, font=page_font)


def wrap_text(text, font, max_width, draw):
    """Quebra texto em multiplas linhas para caber na largura maxima.

    Funciona palavra por palavra: vai adicionando palavras na linha
    atual ate ultrapassar max_width, entao comeca uma nova linha.

    Args:
        text: Texto para quebrar
        font: Fonte para calcular largura
        max_width: Largura maxima em pixels
        draw: Objeto ImageDraw (necessario para textbbox)

    Returns:
        Lista de strings, cada uma sendo uma linha que cabe em max_width
    """
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        # Testa se a palavra cabe na linha atual
        test = f"{current_line} {word}".strip()
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current_line = test  # Cabe! Adiciona a palavra
        else:
            # Nao cabe: salva a linha atual e comeca nova
            if current_line:
                lines.append(current_line)
            current_line = word

    # Nao esquecer a ultima linha
    if current_line:
        lines.append(current_line)

    return lines


def text_center(draw, text, y, font, fill=WHITE, max_width=None):
    """Desenha texto centralizado horizontalmente no slide.

    Se max_width for fornecido, faz word-wrap automatico.
    Retorna a posicao Y apos o ultimo texto (util para encadear).

    Args:
        draw: Objeto ImageDraw
        text: Texto para desenhar
        y: Posicao Y inicial (topo do texto)
        font: Fonte a usar
        fill: Cor do texto
        max_width: Se fornecido, faz wrap nessa largura

    Returns:
        Posicao Y logo apos o texto desenhado
    """
    if max_width:
        # Com wrap: desenha cada linha centralizada
        lines = wrap_text(text, font, max_width, draw)
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            tw = bbox[2] - bbox[0]
            x = (W - tw) // 2  # Centraliza no slide
            draw.text((x, y), line, fill=fill, font=font)
            y += bbox[3] - bbox[1] + 8  # Avanca Y + 8px de espacamento
        return y
    else:
        # Sem wrap: linha unica centralizada
        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        x = (W - tw) // 2
        draw.text((x, y), text, fill=fill, font=font)
        return y + bbox[3] - bbox[1] + 8


# ============================================================================
# TIPOS DE SLIDE
# ============================================================================

def create_slide(slide_num, total, slide_type, **kwargs):
    """Cria um slide individual do carrossel.

    Factory function que gera o slide baseado no tipo.
    Todos os slides compartilham header + progress bar.

    Args:
        slide_num: Numero do slide (1-based, para progress bar)
        total: Total de slides no carrossel
        slide_type: Tipo do slide. Opcoes:
            - 'titulo': Capa com titulo grande e subtitulo
            - 'contexto': Card com titulo e texto explicativo
            - 'conteudo': Item numerado com titulo e descricao
            - 'resumo': Lista de bullet points
            - 'cta': Call to action (salvar, comentar, seguir)
        **kwargs: Parametros especificos de cada tipo (ver abaixo)

    Kwargs por tipo:
        titulo: titulo (str), subtitulo (str)
        contexto: titulo (str), texto (str)
        conteudo: numero (int), titulo (str), texto (str)
        resumo: titulo (str), itens (list[str])
        cta: titulo (str), acoes (list[str])

    Returns:
        Imagem PIL (RGB, 1080x1350)
    """
    # Canvas base com fundo escuro
    img = Image.new("RGB", (W, H), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # Elementos comuns a todos os slides
    draw_header(img, draw)
    draw_progress_bar(draw, slide_num, total)

    # Area util para conteudo (entre header e footer)
    content_top = HEADER_H + 30
    content_bottom = H - FOOTER_H - 20
    content_area = content_bottom - content_top
    usable_width = W - 2 * PADDING

    # --- SLIDE TIPO: TITULO (capa) ---
    if slide_type == "titulo":
        title = kwargs.get("titulo", "Titulo")
        subtitle = kwargs.get("subtitulo", "")

        title_font = load_font(bold=True, size=48)
        y = content_top + content_area // 4  # Posiciona a ~25% da area

        # Linha decorativa accent acima do titulo
        line_w = 80
        draw.rounded_rectangle(
            ((W - line_w) // 2, y - 30, (W + line_w) // 2, y - 24),
            radius=3, fill=ACCENT
        )

        # Titulo centralizado com wrap
        y = text_center(draw, title, y, title_font, fill=WHITE, max_width=usable_width - 40)

        # Subtitulo (se houver)
        if subtitle:
            y += 20
            sub_font = load_font(bold=False, size=28)
            text_center(draw, subtitle, y, sub_font, fill=LIGHT_GRAY, max_width=usable_width - 60)

    # --- SLIDE TIPO: CONTEXTO (problema/cenario) ---
    elif slide_type == "contexto":
        title = kwargs.get("titulo", "Contexto")
        texto = kwargs.get("texto", "")

        title_font = load_font(bold=True, size=36)
        text_font = load_font(bold=False, size=26)

        # Card grande ocupando quase toda a area
        card_top = content_top + 40
        card_bottom = content_bottom - 40
        draw_rounded_rect(draw, (PADDING, card_top, W - PADDING, card_bottom), CARD_RADIUS, CARD_COLOR)

        y = card_top + 40
        # Barra accent vertical ao lado do titulo
        draw.rounded_rectangle(
            (PADDING + 30, y, PADDING + 36, y + 36),
            radius=3, fill=ACCENT
        )
        draw.text((PADDING + 50, y), title, fill=WHITE, font=title_font)
        y += 60

        # Texto do contexto com wrap
        lines = wrap_text(texto, text_font, usable_width - 100, draw)
        for line in lines:
            draw.text((PADDING + 50, y), line, fill=LIGHT_GRAY, font=text_font)
            y += 40

    # --- SLIDE TIPO: CONTEUDO (item numerado) ---
    elif slide_type == "conteudo":
        numero = kwargs.get("numero", 1)
        titulo_item = kwargs.get("titulo", "Item")
        texto = kwargs.get("texto", "")

        # Circulo com o numero do item (estilo badge)
        num_size = 70
        num_x = PADDING + 20
        num_y = content_top + 30
        draw.ellipse(
            (num_x, num_y, num_x + num_size, num_y + num_size),
            fill=ACCENT
        )
        # Centralizar numero dentro do circulo
        num_font = load_font(bold=True, size=36)
        bbox = draw.textbbox((0, 0), str(numero), font=num_font)
        nw = bbox[2] - bbox[0]
        nh = bbox[3] - bbox[1]
        draw.text(
            (num_x + (num_size - nw) // 2, num_y + (num_size - nh) // 2 - 4),
            str(numero), fill=BG_COLOR, font=num_font
        )

        # Titulo do item ao lado do numero
        title_font = load_font(bold=True, size=34)
        title_x = num_x + num_size + 20
        draw.text((title_x, num_y + 15), titulo_item, fill=WHITE, font=title_font)

        # Card com a descricao/explicacao
        card_top = num_y + num_size + 30
        card_bottom = content_bottom - 40
        draw_rounded_rect(draw, (PADDING, card_top, W - PADDING, card_bottom), CARD_RADIUS, CARD_COLOR)

        # Texto da descricao com wrap dentro do card
        text_font = load_font(bold=False, size=26)
        y = card_top + 30
        lines = wrap_text(texto, text_font, usable_width - 80, draw)
        for line in lines:
            draw.text((PADDING + 40, y), line, fill=LIGHT_GRAY, font=text_font)
            y += 40

    # --- SLIDE TIPO: RESUMO (bullet points) ---
    elif slide_type == "resumo":
        titulo = kwargs.get("titulo", "Resumo")
        itens = kwargs.get("itens", [])

        # Titulo centralizado em accent
        title_font = load_font(bold=True, size=36)
        y = content_top + 30
        text_center(draw, titulo, y, title_font, fill=ACCENT)
        y += 60

        # Cada item em um mini-card com bullet point accent
        item_font = load_font(bold=False, size=26)
        for item in itens:
            card_h = 80
            draw_rounded_rect(
                draw, (PADDING, y, W - PADDING, y + card_h),
                CARD_RADIUS, CARD_COLOR
            )
            # Bolinha accent como bullet point
            draw.ellipse((PADDING + 20, y + 30, PADDING + 32, y + 42), fill=ACCENT)
            # Texto do item com wrap
            lines = wrap_text(item, item_font, usable_width - 80, draw)
            ly = y + 25
            for line in lines:
                draw.text((PADDING + 50, ly), line, fill=WHITE, font=item_font)
                ly += 32
            y += card_h + 15

    # --- SLIDE TIPO: CTA (call to action) ---
    elif slide_type == "cta":
        titulo = kwargs.get("titulo", "Gostou?")
        acoes = kwargs.get("acoes", [
            "Salve para consultar depois",
            "Comente sua experiencia",
            "Siga @matheus-zacche"
        ])

        # Titulo grande centralizado
        title_font = load_font(bold=True, size=42)
        y = content_top + content_area // 5
        text_center(draw, titulo, y, title_font, fill=WHITE)
        y += 80

        # Cards de acao com icones
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

        # Handle do LinkedIn no rodape do slide
        handle_font = load_font(bold=True, size=24)
        text_center(draw, "@matheus-zacche", content_bottom - 40, handle_font, fill=ACCENT)

    return img


# ============================================================================
# FUNCAO PRINCIPAL - Gera o carrossel completo
# ============================================================================

def gerar_carrossel(titulo, subtitulo, contexto_titulo, contexto_texto,
                     slides_conteudo, resumo_itens,
                     cta_titulo="Gostou do conteudo?",
                     output_name="carrossel"):
    """Gera um carrossel completo de 8 slides + PDF.

    Esta e a funcao principal que o agente Claude chama.
    Ela orquestra a criacao de todos os slides e salva os arquivos.

    Args:
        titulo: Titulo principal do carrossel (slide 1)
        subtitulo: Subtitulo abaixo do titulo (slide 1)
        contexto_titulo: Titulo da secao de contexto (slide 2, ex: "O problema")
        contexto_texto: Texto explicativo do contexto (slide 2)
        slides_conteudo: Lista de dicts com 'titulo' e 'texto' (slides 3-6).
                         Cada dict = 1 slide. Maximo 4 itens.
                         Ex: [{"titulo": "Erro 1", "texto": "Descricao..."}]
        resumo_itens: Lista de strings para o slide de resumo (slide 7)
        cta_titulo: Titulo do slide de CTA (slide 8, default: "Gostou do conteudo?")
        output_name: Nome base dos arquivos de saida (sem extensao)

    Returns:
        Tupla (pdf_path, png_paths):
          - pdf_path: Caminho do PDF combinado
          - png_paths: Lista de caminhos dos PNGs individuais
    """
    # Garantir que o diretorio de output existe
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    total = 8  # Numero fixo de slides no carrossel
    images = []

    # Slide 1: Titulo/capa
    img1 = create_slide(1, total, "titulo", titulo=titulo, subtitulo=subtitulo)
    images.append(img1)

    # Slide 2: Contexto/problema
    img2 = create_slide(2, total, "contexto", titulo=contexto_titulo, texto=contexto_texto)
    images.append(img2)

    # Slides 3-6: Conteudo principal (maximo 4 itens)
    for i, item in enumerate(slides_conteudo[:4]):
        img = create_slide(i + 3, total, "conteudo",
                          numero=i + 1,
                          titulo=item["titulo"],
                          texto=item["texto"])
        images.append(img)

    # Se menos de 4 itens de conteudo, preenche com placeholders
    while len(images) < 6:
        images.append(create_slide(len(images) + 1, total, "conteudo",
                                   numero=len(images) - 1,
                                   titulo="...", texto="..."))

    # Slide 7: Resumo com bullet points
    img7 = create_slide(7, total, "resumo", titulo="Resumindo", itens=resumo_itens)
    images.append(img7)

    # Slide 8: Call to Action
    img8 = create_slide(8, total, "cta", titulo=cta_titulo)
    images.append(img8)

    # Salvar cada slide como PNG individual
    png_paths = []
    for i, img in enumerate(images):
        path = os.path.join(OUTPUT_DIR, f"{output_name}_slide_{i+1}.png")
        img.save(path, "PNG")
        png_paths.append(path)

    # Combinar todos os slides em um unico PDF (pronto para upload no LinkedIn)
    # Pillow exige imagens RGB (nao RGBA) para salvar como PDF
    pdf_path = os.path.join(OUTPUT_DIR, f"{output_name}.pdf")
    rgb_images = [img.convert("RGB") for img in images]
    rgb_images[0].save(pdf_path, "PDF", save_all=True, append_images=rgb_images[1:])

    print(f"Carrossel gerado com sucesso!")
    print(f"  PNGs: {len(png_paths)} slides em {OUTPUT_DIR}")
    print(f"  PDF:  {pdf_path}")
    return pdf_path, png_paths


# ============================================================================
# TESTE - Roda quando executa o script diretamente
# ============================================================================
if __name__ == "__main__":
    # Exemplo: carrossel sobre erros comuns no Power BI
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
