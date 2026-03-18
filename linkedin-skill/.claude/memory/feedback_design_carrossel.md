---
name: feedback_design_carrossel
description: Principios de design para carrosseis LinkedIn — aprendidos em sessao de refinamento intenso
type: feedback
---

Cards tem tamanho do conteudo, nao do espaco disponivel. Distribuir o espaco restante como gap uniforme, nunca maximizar os cards para "preencher" o slide.

**Why:** O usuario apontou multiplas vezes que o trabalho estava "péssimo" quando os cards cresciam para preencher o espaco. O problema fundamental era que o codigo servia ao espaco, nao ao conteudo.

**How to apply:** Calcular altura natural (conteudo + pad_v generoso), depois `gap = (area_h - total_cards) // (n+1)`, `top_offset = gap`. Nunca usar `_fill_cards` para slides de automacao.

---

Centralizacao de texto dentro de formas SEMPRE pela formula real: `text_y = container_y + (container_h - text_h) // 2`. Nunca usar offsets fixos como `y + 18` ou `y + pv`.

**Why:** Causava pills com texto colado no topo, banners com texto desalinhado, abstract box com texto flutuando.

**How to apply:** Medir `text_h` real com `th_val`, calcular offset dinamico. Isso inclui pills, banners, abstract box, mini cards da capa.

---

Pills com altura de referencia consistente: usar `th_val(draw, "PYTHON", fnt)` como altura base, nao `th_val(draw, label, fnt)`. Textos acentuados (ex: AUTOMACAO) tem altura maior e desalinham as pills.

---

Watermark decorativo com corte proporcional fixo: `x = W - int(wm_w * 0.68)` — sempre mostra 68% do numero. Nunca pixel fixo porque numeros diferentes tem larguras diferentes.

---

Cada slide de conteudo deve ter cor de destaque propria. Cor propaga para: pill, watermark, borda do card, outline, banner. Slides identicos visualmente = trabalho ruim.

---

Capa: mini cards com borda colorida (nao lista com separador "—"). Titulo ancorado ao topo, abstract logo abaixo do titulo. Nao centralizar verticalmente no slide.

---

Slide CTA: calcular bloco completo (pergunta + detalhe + botao), centralizar no espaco acima do separador. Assinatura ancorada no rodape. Nunca separar pergunta (topo) de detalhe (rodape) — cria gap de 500px no meio.
