# Estrutura Completa dos Criativos do LinkedIn

Este documento detalha a construção de cada criativo produzido para o perfil do Matheus Zacché no LinkedIn. Ele cobre a lógica por trás de cada decisão visual e de conteúdo, servindo como referência para replicar o padrão em novos posts.

---

## Identidade Visual (padrão para todos os criativos)

Antes de entrar nos criativos individuais, é importante entender o sistema visual que se repete em todos eles.

### Especificações técnicas gerais

| Elemento | Especificação |
|----------|---------------|
| Dimensões | 1080x1350px (retrato, otimizado para mobile) |
| Fundo base | #1a1a2e (azul muito escuro, quase preto) |
| Fonte | Noto Sans (Regular e Bold) |
| Cor do texto principal | #FFFFFF (branco) |
| Cor do texto secundário | #b0b0b0 (cinza claro) |
| Cor de destaque primária | Varia por carrossel (ciano para Python+N8N, laranja para Power BI) |
| Ferramenta de geração | Python com Pillow (PIL) |

### Header (presente em todos os slides e posts)

O header aparece no topo de cada imagem e funciona como assinatura visual. Ele contém a foto circular do Matheus (recortada pelo topo da imagem original para capturar o rosto, já que a foto é vertical de corpo inteiro), o nome "Matheus Zacché" em branco bold, um selo verificado azul (círculo azul com check branco desenhado via código) e o handle @matheus.zacche em cinza claro. No canto superior direito, três pontos simulam o menu do LinkedIn. Abaixo do header, uma linha separadora sutil divide o header do conteúdo.

### Elementos visuais recorrentes

**Cards**: retângulos com fundo semi-transparente (#2a2a4a ou variação temática), bordas arredondadas (radius 15px), borda sutil (#3a3a5a). Muitos cards possuem uma barra colorida lateral (4px de largura) à esquerda, que funciona como indicador visual de categoria ou hierarquia.

**Pills/Tags**: retângulos pequenos arredondados com fundo escuro e borda colorida. Usadas para categorizar o tema do slide (ex: PYTHON, N8N, POWER BI). O texto dentro da pill deve estar centralizado tanto vertical quanto horizontalmente, calculado via `textbbox` com anchor.

**Banner de destaque**: retângulo largo no rodapé do slide com fundo colorido (verde escuro, laranja escuro, vermelho escuro dependendo do tema) e texto bold centralizado. Funciona como frase-chave ou takeaway do slide. Presente nos slides 2-7 de cada carrossel.

**Barra de progresso**: no rodapé absoluto de cada slide, mostra a posição atual (ex: 3/8). Barra com fundo cinza e preenchimento na cor de destaque do carrossel.

**Elementos decorativos (apenas na capa)**: círculos grandes semi-transparentes nos cantos, na cor temática do carrossel. Adicionam profundidade visual sem competir com o conteúdo.

---

## Criativo 1: Carrossel Python + N8N

### Contexto e objetivo

Este foi o primeiro carrossel produzido no projeto. O tema é a integração entre Python (tratamento de dados) e N8N (automação de fluxos), que é uma das competências centrais do Matheus. O objetivo era mostrar quando usar cada ferramenta e como fazê-las trabalhar juntas, posicionando o Matheus como alguém que domina essa combinação.

A cor de destaque escolhida foi **ciano/verde (#00d4aa)** para elementos N8N e **azul (#4a9eff)** para elementos Python, criando uma distinção visual clara entre as duas ferramentas ao longo de todo o carrossel.

### Estrutura slide a slide

| Slide | Título | Função narrativa | Tipo de layout |
|-------|--------|-------------------|----------------|
| 1 | Python + N8N: Como integrar tratamento de dados com automação | Capa: atrair o clique | Título + 2 cards lado a lado |
| 2 | O papel de cada um | Contextualizar: o que cada ferramenta faz | 2 cards empilhados com listas |
| 3 | Quando usar Python | Aprofundar: cenários específicos do Python | 4 cards numerados |
| 4 | Quando usar N8N | Aprofundar: cenários específicos do N8N | 4 cards numerados |
| 5 | 3 formas de integrar | Conteúdo principal: métodos de integração | 3 cards com níveis |
| 6 | Exemplo de fluxo | Aplicação prática: fluxo real | Timeline vertical 4 etapas |
| 7 | A regra de ouro | Consolidação: o que evitar vs o que fazer | 2 cards (vermelho/verde) |
| 8 | CTA | Engajamento: salvar + comentar | Card centralizado |

### Slide 1 (Capa)

A capa possui três pills no topo (PYTHON, N8N, AUTOMAÇÃO) que categorizam o conteúdo para quem está scrollando rápido. O título é dividido em duas partes: "Python + N8N" em ciano bold (destaque) e "Como integrar tratamento de dados com automação" em branco bold (contexto). Abaixo, o subtítulo cinza "Quando usar cada um e como fazê-los trabalhar juntos" define a promessa do carrossel.

Na parte inferior, dois cards lado a lado representam visualmente a dualidade do tema. O card da esquerda mostra um ícone de chaves `{}` em azul com "Dados / Tratamento / Transformação". O card da direita mostra `[>>]` em ciano com "Fluxo / Orquestração / Automação". Entre eles, um sinal `>` conecta os dois conceitos. Círculos decorativos verde e azul nos cantos inferiores completam a composição.

### Slide 2 (O papel de cada um)

Dois cards empilhados verticalmente, cada um com barra lateral colorida (azul para Python, ciano para N8N) e 5 itens com bullet points. O card Python lista: limpeza e tratamento de dados, cálculos e transformações complexas, leitura de arquivos (CSV, Excel, JSON), conexão com bancos de dados, análise e modelagem. O card N8N lista: conexão entre sistemas e APIs, triggers automáticos (horário, webhook), envio de e-mails e notificações, fluxos visuais e fáceis de manter, orquestração sem código.

O banner de destaque verde traz a frase-chave: **"Python é o cérebro. N8N é o sistema nervoso."** Essa metáfora resume todo o slide em uma frase memorável.

### Slides 3 e 4 (Quando usar Python / Quando usar N8N)

Esses dois slides são espelhos um do outro em estrutura, mas com cores diferentes (azul para Python, verde para N8N). Cada um contém 4 cards numerados (01-04) com número grande colorido à esquerda, título bold e descrição cinza.

Para Python: tratar dados sujos, fazer cálculos complexos, processar arquivos, criar lógica customizada. Para N8N: conectar sistemas, agendar execuções, orquestrar ações, manter sem código.

Cada slide termina com um banner que reforça a regra de decisão: **"Use Python quando o problema está nos dados"** e **"Use N8N quando o problema está no fluxo."**

### Slide 5 (3 formas de integrar)

Este é o slide de maior valor técnico do carrossel. Apresenta 3 métodos de integração com níveis de complexidade crescente, cada um em um card com barra lateral colorida diferente (verde, ciano, roxo) e uma pill indicando o nível (Simples, Intermediário, Avançado).

O método 1 (Code Node) permite escrever Python direto dentro do N8N, ideal para transformações simples. O método 2 (Execute Command) chama um script .py externo pelo terminal, ideal para scripts complexos. O método 3 (API via FastAPI) roda Python como API separada que o N8N chama via HTTP Request, ideal para lógica pesada e reutilizável.

A progressão de complexidade (verde > ciano > roxo) guia visualmente o leitor do mais simples ao mais avançado.

### Slide 6 (Exemplo de fluxo)

Uma timeline vertical com 4 etapas conectadas por linhas verticais, mostrando um fluxo real de Python + N8N trabalhando juntos. Cada etapa é um card com pill indicando a ferramenta (N8N ou PYTHON) e barra lateral colorida correspondente.

A sequência é: N8N agenda a execução (todo dia às 8h ou via webhook) > N8N busca os dados (API, banco de dados ou arquivo) > Python processa (limpeza, cálculos, transformações) > N8N distribui (e-mail, Sheets, Slack, dashboard). O banner resume: **"Dados no Python > ação automatizada no N8N."**

### Slide 7 (A regra de ouro)

Dois cards com fundos contrastantes. O card "EVITE" tem fundo vermelho escuro/marrom com 3 itens marcados com X vermelho: fazer tudo no N8N (vira fluxo gigante e frágil), fazer tudo no Python (perde a orquestração visual), misturar lógica de dados com lógica de fluxo.

O card "FAÇA" tem fundo verde escuro com 3 itens marcados com + ciano: Python cuida dos dados (tratar, calcular, transformar), N8N cuida do fluxo (agendar, conectar, distribuir), cada ferramenta no que faz melhor.

O contraste vermelho/verde cria uma distinção visual imediata entre erros e boas práticas. O banner fecha: **"Python para dados. N8N para fluxo."**

### Slide 8 (CTA)

Card centralizado com fundo semi-transparente. "Salva esse post para consultar depois" em branco bold + cinza. Abaixo, a pergunta em ciano: "Você já usa Python e N8N juntos?" com "Conta nos comentários como você faz a integração" em cinza. Um botão pill com borda verde diz "Comenta qual método você usa!" e a assinatura "Matheus Zacche / Analista de Dados" fecha o carrossel.

A lição aprendida com esse CTA: a pergunta "Você já usa Python e N8N juntos?" é muito nichada. A maioria das pessoas responde "não" mentalmente e segue. Em carrosseis futuros, o CTA foi ajustado para perguntas mais inclusivas.

---

## Criativo 2: Carrossel Power BI (Hierarquia Visual)

### Contexto e objetivo

Segundo carrossel do projeto. O tema é hierarquia visual em dashboards Power BI, um assunto que atinge um público maior do que Python + N8N (qualquer pessoa que trabalha com BI ou dashboards se identifica). O objetivo era ensinar princípios de design de dashboard de forma prática, posicionando o Matheus como alguém que não só faz dashboards, mas pensa na experiência do usuário.

A cor de destaque escolhida foi **laranja/dourado (#f5a623)**, remetendo à paleta do Power BI e criando uma identidade visual distinta do primeiro carrossel.

### Estrutura slide a slide

| Slide | Título | Função narrativa | Tipo de layout |
|-------|--------|-------------------|----------------|
| 1 | Onde colocar cada informação no seu dashboard | Capa: atrair o clique | Título + mockup de dashboard |
| 2 | O erro mais comum | Problema: gerar identificação | 4 cards vermelhos numerados |
| 3 | Padrão Z de leitura | Conceito: como o olho lê | Grid 2x2 com padrão Z |
| 4 | Organize em 3 camadas | Framework: pirâmide invertida | 3 cards empilhados coloridos |
| 5 | Use o tamanho a seu favor | Regra prática: tamanho = importância | 4 cards numerados |
| 6 | Cor não é decoração | Regra prática: uso intencional de cor | 4 cards numerados |
| 7 | Antes de publicar, confira | Consolidação: checklist | Card com 6 checkboxes |
| 8 | CTA | Engajamento: salvar + comentar | Card centralizado |

### Slide 1 (Capa)

Três pills no topo (POWER BI, DASHBOARD, DESIGN) em laranja/dourado. O título "Onde colocar cada informação no seu dashboard" tem a palavra "dashboard" destacada em laranja. O subtítulo "Hierarquia visual: o que seu olho lê primeiro" define o ângulo.

O diferencial desta capa é o mockup de dashboard na parte inferior: um layout em grid mostrando KPI Principal (posição 1, destaque laranja), KPI 2 (posição 2), KPI 3 (posição 3), gráfico de Tendência com barras, área de Comparativo (posição 4) e Detalhamento (tabela). Esse mockup já antecipa visualmente o conteúdo do carrossel e funciona como "preview" do que a pessoa vai aprender.

### Slide 2 (O erro mais comum)

Quatro cards com fundo vermelho escuro/marrom, numerados 01-04 com número vermelho grande. Cada card descreve uma consequência de não usar hierarquia visual: tudo igual (jogar gráficos sem ordem), sem hierarquia (tratar tudo como igualmente importante), usuário perdido (não sabe pra onde olhar), ninguém usa (dashboard vira decoração).

A progressão narrativa é de causa para consequência: erro > resultado > impacto final. O banner vermelho fecha: **"Se tudo tem destaque, nada tem destaque."** Essa frase se tornou uma das mais comentadas do post.

### Slide 3 (Padrão Z de leitura)

Este slide introduz o conceito central do carrossel. Um grid 2x2 dentro de um card grande mostra as 4 zonas do padrão Z: KPI principal (canto superior esquerdo, fundo dourado, "MAIOR DESTAQUE"), KPIs secundários (canto superior direito), Tendências (canto inferior esquerdo), Detalhamento (canto inferior direito). Uma linha diagonal tracejada conecta a posição 2 à posição 3, formando visualmente o Z.

O banner laranja reforça: **"KPI mais importante = canto superior esquerdo."** Abaixo, uma dica em texto explica por que o padrão funciona (nosso cérebro lê da esquerda pra direita e de cima pra baixo).

### Slide 4 (Organize em 3 camadas)

Três cards empilhados com cores e tamanhos diferentes, representando a pirâmide invertida. O card do topo (fundo dourado/marrom, borda laranja) é o maior e mostra "KPIs e status" com a pergunta "A resposta rápida: estamos bem?". O card do meio (fundo azul escuro, borda azul) mostra "Tendências e comparações" com "O que explica o movimento". O card da base (fundo roxo escuro, borda roxa) mostra "Detalhamento e tabelas" com "Pra quem quer ir mais fundo".

A diferença de cor entre as camadas (dourado > azul > roxo) cria uma hierarquia visual dentro do próprio slide, reforçando o conceito que está sendo ensinado. O banner fecha: **"De cima pra baixo: do resumo ao detalhe."**

### Slides 5 e 6 (Tamanho e Cor)

Dois slides com estrutura idêntica (4 cards numerados com barras laterais coloridas), cada um abordando uma dimensão do design de dashboard.

O slide 5 ensina que tamanho comunica importância: KPI principal deve ser o maior elemento, gráficos de tendência em tamanho médio no centro, filtros e tabelas menores na lateral ou embaixo, e espaço em branco não é desperdício, é respiro. Banner: **"Maior = mais importante. Simples assim."**

O slide 6 ensina que cor deve ter propósito: destaque com sentido (vermelho = alerta, verde = ok, amarelo = cuidado), fundo neutro, máximo 3 cores, cinza para informação secundária. Banner: **"Se tudo é colorido, nada se destaca."**

### Slide 7 (Checklist)

Um card grande com 6 itens de checklist, cada um com checkbox verde marcado. Os itens são perguntas que o leitor deve fazer antes de publicar um dashboard: KPI principal no canto superior esquerdo? Informações de cima pra baixo? Tamanho reflete importância? Cores com propósito? Espaço em branco suficiente? Usuário sabe pra onde olhar?

Esse slide é o mais "salvável" do carrossel porque funciona como referência rápida. O banner fecha: **"Dashboard bom e dashboard útil são coisas diferentes."**

### Slide 8 (CTA)

Mesmo layout do CTA do carrossel anterior, mas com cor laranja. A pergunta é mais inclusiva: **"Qual a primeira coisa que você olha quando abre um dashboard?"** com "Conta nos comentários o que chama sua atenção primeiro." Essa pergunta funciona melhor porque qualquer pessoa que já abriu um dashboard consegue responder, diferente da pergunta nichada do primeiro carrossel.

---

## Criativo 3: Post API (imagem única)

### Contexto e objetivo

Primeiro post no formato texto + imagem do projeto. O tema "API: como sistemas conversam entre si" foi escolhido por ser um conceito fundamental que atinge tanto desenvolvedores quanto analistas de dados. O objetivo era explicar API de forma acessível e visual, sem ser um tutorial técnico pesado.

### Estrutura da imagem

A imagem usa o mesmo padrão visual dos carrosseis (fundo escuro, header com foto), mas em formato único. O layout é organizado em 3 seções verticais:

**Seção 1 (Diagrama de fluxo)**: dois boxes lado a lado representando Sistema A (seu app, script, site) com borda azul e Sistema B (banco, serviço, API) com borda laranja. Setas horizontais conectam os dois: "Request" em verde (da esquerda para direita) e "Response" em laranja (da direita para esquerda). Abaixo, um conector vertical aponta para uma pill verde "API (o intermediário)". Esse diagrama traduz visualmente o conceito abstrato de comunicação entre sistemas.

**Seção 2 (Na prática)**: quatro métodos HTTP apresentados como pills coloridas com descrição ao lado. GET (verde) para buscar dados, POST (laranja) para enviar dados, PUT (amarelo) para atualizar dados, DELETE (vermelho) para remover dados. As cores seguem a convenção semântica (verde = seguro, vermelho = destrutivo).

**Seção 3 (Exemplo)**: um card com borda verde mostra um exemplo concreto de chamada API: `GET api.clima.com/temperatura?cidade=SP` com resposta `{ "temp": 28, "unidade": "C" }`. Esse exemplo torna o conceito tangível para quem nunca usou uma API.

O banner de rodapé fecha com: **"API é a ponte. Sem ela, sistemas não se falam."**

### Texto de apoio (legenda)

O texto da legenda complementa a imagem sem repetir o que está nela. O hook abre com uma provocação sobre como sistemas se comunicam. O corpo explica o conceito em linguagem acessível, conectando com o dia a dia de quem trabalha com dados. O CTA pergunta: "Você já consumiu alguma API no trabalho? Conta aqui qual foi."

---

## Criativo 4: Post Git (imagem única)

### Contexto e objetivo

Segundo post no formato texto + imagem. O tema "Git não é só pra desenvolvedor" foi escolhido para atingir analistas de dados que ainda não usam versionamento, um público grande e engajável. O ângulo diferenciador é que Git não é exclusividade de devs, analistas também precisam.

### Estrutura da imagem

A imagem segue o mesmo padrão visual, com 3 seções:

**Seção 1 (Timeline de comandos)**: uma timeline vertical com 5 etapas conectadas por linha. Cada etapa é composta por uma bolinha na linha, uma pill laranja com o comando Git e duas linhas de texto (título bold + descrição cinza). Os comandos são: `git init` (inicia o repositório), `git add` (seleciona arquivos), `git commit` (salva uma versão), `git push` (envia pro remoto), `git branch` (cria uma ramificação). As descrições usam linguagem simples e analogias ("Foto do seu código naquele momento" para commit).

**Seção 2 (Comparativo Sem Git vs Com Git)**: dois cards lado a lado. O card "Sem Git" tem borda e título vermelhos, mostrando nomes de arquivo caóticos: `relatorio_v2_final`, `_FINAL_de_verdade.py`, `quem_mexeu_nisso.py`. O card "Com Git" tem borda e título cianos, mostrando comandos organizados: `git log` (histórico completo), `git diff` (o que mudou), `git blame` (quem mexeu). O humor dos nomes de arquivo no card vermelho gera identificação imediata com qualquer pessoa que já trabalhou sem versionamento.

**Seção 3 (Banner)**: frase de fechamento em banner dourado/marrom: **"Versionar código é tão importante quanto escrever."**

### Texto de apoio (legenda)

O hook conecta Git com a realidade de analistas de dados. O corpo explica por que versionamento importa mesmo para quem não é dev, citando cenários reais (scripts que quebram, versões perdidas). O CTA pergunta sobre a experiência da pessoa com versionamento.

---

## Padrões de Design Reutilizáveis

### Layouts que se repetem

| Layout | Onde foi usado | Quando usar |
|--------|---------------|-------------|
| 4 cards numerados (01-04) | Slides 3, 4, 5, 6 de ambos os carrosseis | Listas de itens com hierarquia ou sequência |
| 2 cards empilhados com barra lateral | Slide 2 do Python+N8N | Comparação entre 2 categorias |
| 3 cards empilhados com cores | Slide 4 do Power BI, Slide 5 do Python+N8N | Níveis de complexidade ou hierarquia |
| Timeline vertical | Slide 6 do Python+N8N, post Git | Sequência de etapas ou fluxo |
| Grid 2x2 | Slide 3 do Power BI | Mapeamento de 4 quadrantes |
| Comparativo lado a lado | Slide 7 do Python+N8N, post Git | Antes/depois, certo/errado |
| Checklist | Slide 7 do Power BI | Resumo acionável |
| Diagrama de fluxo | Post API | Relação entre sistemas ou conceitos |

### Paleta de cores por tema

| Tema | Cor primária | Cor secundária | Cor de alerta | Uso |
|------|-------------|----------------|---------------|-----|
| Automação (Python/N8N) | #00d4aa (ciano) | #4a9eff (azul) | #ff6b6b (vermelho) | Carrossel 1 |
| BI/Dashboard (Power BI) | #f5a623 (laranja) | #4a9eff (azul) | #ff6b6b (vermelho) | Carrossel 2 |
| Conceito técnico (API) | #00d4aa (ciano) | #f5a623 (laranja) | #ff6b6b (vermelho) | Post API |
| Ferramenta (Git) | #f5a623 (laranja) | #00d4aa (ciano) | #ff6b6b (vermelho) | Post Git |

### Fórmula do banner de destaque

Todo banner de destaque segue a mesma fórmula: uma frase curta (máximo 10 palavras), assertiva, que resume o takeaway do slide. Exemplos que funcionaram:

| Slide | Frase | Por que funciona |
|-------|-------|-----------------|
| Python+N8N slide 2 | "Python é o cérebro. N8N é o sistema nervoso." | Metáfora memorável |
| Python+N8N slide 3 | "Use Python quando o problema está nos dados." | Regra de decisão clara |
| Power BI slide 2 | "Se tudo tem destaque, nada tem destaque." | Paradoxo que gera reflexão |
| Power BI slide 5 | "Maior = mais importante. Simples assim." | Simplicidade direta |
| API | "API é a ponte. Sem ela, sistemas não se falam." | Analogia concreta |
| Git | "Versionar código é tão importante quanto escrever." | Equiparação que eleva o conceito |

---

## Lógica de Construção (como pensar um novo criativo)

### Para carrosseis

1. Definir o tema e a cor de destaque (diferente dos últimos carrosseis)
2. Escrever a narrativa em 8 etapas: capa > problema > conceito > framework > regras práticas (2 slides) > consolidação > CTA
3. Para cada slide, escolher o layout mais adequado da tabela de layouts reutilizáveis
4. Escrever o banner de destaque de cada slide (frase curta, assertiva, memorável)
5. Gerar as imagens em Python com Pillow, seguindo as especificações técnicas
6. Verificar centralização de todos os textos dentro de cards e pills
7. Verificar se a foto do header não está esticada
8. Verificar se não há espaço vazio no rodapé
9. Converter os 8 PNGs em um único PDF
10. Escrever o texto de apoio (legenda) com hook, corpo e CTA

### Para posts com imagem

1. Definir o conceito a ser explicado e a cor de destaque
2. Escolher o tipo de visualização (diagrama, timeline, comparativo, grid)
3. Organizar o conteúdo em 2-3 seções verticais dentro da imagem
4. Incluir um exemplo concreto quando possível (torna o conceito tangível)
5. Fechar com banner de destaque
6. Gerar a imagem em Python com Pillow
7. Verificar centralização e proporções
8. Cortar espaço vazio se necessário
9. Escrever o texto de apoio (legenda) que complementa a imagem sem repetir
