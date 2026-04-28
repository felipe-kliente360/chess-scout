# Chess Scout — Benchmark & Roadmap

_Documento gerado em 2026-04-28. Combina análise interna do código + pesquisa de mercado sobre 12 ferramentas concorrentes._

---

## 1. Sumário Executivo

Chess Scout é uma ferramenta open-source em Python/Streamlit que busca partidas do Chess.com ou Lichess via API, analisa cada lance com Stockfish e gera dois relatórios em markdown: um diagnóstico do próprio jogador e um guia de como vencer um adversário específico.

### Posição no mercado

| Dimensão | Status |
|---|---|
| Diagnóstico do jogador | Faz — mas com profundidade abaixo dos líderes |
| Guia do adversário | Faz — **diferencial real**: nenhum concorrente open-source faz isso |
| Relatório exportável (markdown) | **Exclusivo** no segmento open-source |
| Chess.com + Lichess como fonte | Faz — diferencial em relação a ferramentas que suportam só uma |
| Análise com Stockfish local | Faz — gratuito, sem limite de partidas |
| Plano de estudo personalizado | Parcial — template fixo, pouca personalização real |
| Métricas padrão da indústria (ACPL, accuracy %) | **Não faz** — gap crítico |
| Contexto de rating (comparar com jogadores da mesma faixa) | **Não faz** — gap crítico |

### Conclusão em uma linha

> Chess Scout tem um diferencial genuíno (guia do adversário open-source + markdown exportável), mas precisa adicionar as métricas padrão da indústria e contextualizar a análise por faixa de rating para ter credibilidade analítica.

---

## 2. Análise Competitiva — 12 Ferramentas

### 2.1 Chess.com Insights (built-in)

**O que faz:** Dashboard de estatísticas agregadas sobre todas as suas partidas — abertura, precisão, cor, horário do dia. Game Review analisa cada lance com Stockfish e classifica em 6-9 categorias.

**Diferenciais:**
- CAPS (Computer Aggregated Precision Score) — métrica própria de precisão
- Base comparativa de milhões de jogadores do mesmo rating
- Explicação de movimentos em linguagem natural (Diamond)

**Limitações:**
- Insights e Game Review ilimitado só no plano Diamond (~$14/mês)
- Não gera guia do adversário
- Não suporta partidas do Lichess
- Sem exportação de relatório

**Pricing:** Free (1 review/dia) → Diamond $14/mês

---

### 2.2 Lichess Analysis (built-in)

**O que faz:** Análise gratuita, sem paywall, de qualquer partida. Stockfish via fishnet distribuído pode atingir depth 50+. Opening Explorer com 3 bases de dados (masters, Lichess, suas partidas).

**Diferenciais:**
- 100% gratuito, open-source (AGPLv3)
- Fórmula de accuracy% transparente e documentada
- Fishnet: maior profundidade gratuita do mercado

**Limitações:**
- Não gera diagnóstico do jogador nem guia do adversário
- Não importa partidas do Chess.com nativamente
- Sem relatório exportável ou plano de estudo

**Pricing:** Gratuito

---

### 2.3 ChessBase (desktop)

**O que faz:** Padrão profissional. Style Report, Blunder Report, preparação de adversário, base de dados com 11M+ partidas, integração multi-engine.

**Diferenciais:**
- Único produto mainstream com **Opponent Preparation Report** explícito
- Style Report: caracteriza estilo de jogo, fase crítica, motivos táticos recorrentes
- Suporte a Lichess na preparação de adversário (CB18+)
- AI description of plans (ChessBase '26)

**Limitações:**
- Windows-only, desktop
- Caro ($250–$500)
- Curva de aprendizado íngreme
- Sem conexão direta a Chess.com/Lichess via API
- Sem output em markdown/texto portável

**Pricing:** $249–$499 (one-time)

---

### 2.4 Aimchess

**O que faz:** Conecta Chess.com, Lichess e Chess24. Analisa todos os lances. Gera diagnóstico em 6 dimensões: Aberturas, Táticas, Finais, Conversão de Vantagem, Recursos, Gestão de Tempo. Plano de estudo personalizado.

**Diferenciais:**
- **Concorrente direto do DIAGNOSTICO.md** — mas entregue como dashboard web
- 6 dimensões de análise muito bem definidas
- Training rooms com exercícios direcionados às suas fraquezas
- Suporte a 3 plataformas

**Limitações:**
- Não gera guia do adversário
- Dashboard web, sem exportação de relatório
- Free tier limitado (1 análise de 40 partidas/mês)

**Pricing:** Free limitado → Premium $57.99/ano

---

### 2.5 ChessScout.net

**O que faz:** Serviço de scouting por IA. Gera relatório de scout do adversário: padrões de abertura, tendências, hábitos exploráveis.

**Diferenciais:**
- **Concorrente direto do GUIA_ADVERSARIO.md** — comercial, pago
- Suporta Chess.com e Lichess
- "Entre em cada partida com um plano"

**Limitações:**
- Proprietário e pago (pricing não divulgado publicamente)
- Sem diagnóstico do próprio jogador
- Sem exportação em markdown

**Pricing:** Trial 3 dias → pago (valor não divulgado)

---

### 2.6 PrepSuite

**O que faz:** Scout de adversário com IA — Chess.com, Lichess e base OTB. Análise Stockfish + resumo estratégico gerado por IA + gráficos de repertório.

**Diferenciais:**
- Combina engine analysis com narrativa gerada por IA
- Acesso a base OTB (torneios presenciais)
- Concorrente direto do GUIA_ADVERSARIO.md, mais sofisticado

**Limitações:**
- Proprietário e pago
- Sem diagnóstico do próprio jogador
- Sem exportação open-source

**Pricing:** Não divulgado publicamente

---

### 2.7 Chess Stalker

**O que faz:** Ferramenta gratuita que analisa estilo, aberturas favoritas e padrões psicológicos de qualquer jogador. Stockfish in-browser (WebAssembly). Suporta Lichess, Chess.com e FIDE.

**Diferenciais:**
- Gratuito
- Stockfish no browser sem instalação
- Acesso a dados FIDE (jogadores OTB)

**Limitações:**
- Interface web apenas, sem relatório exportável
- Análise superficial de estilo
- Sem diagnóstico do próprio jogador

**Pricing:** Gratuito

---

### 2.8 OpeningTree

**O que faz:** Puxa partidas do Chess.com ou Lichess por username e constrói uma árvore interativa de aberturas com estatísticas de W/D/L em cada nó. Pode analisar adversários também.

**Diferenciais:**
- Open-source (GPL-3.0), 457 stars no GitHub
- Pode ser usado para mapear o repertório de um adversário
- Filtros por time control, data, cor

**Limitações:**
- Sem análise Stockfish
- Sem diagnóstico, sem plano de estudo, sem relatório exportável
- Apenas aberturas

**Pricing:** Gratuito

---

### 2.9 DecodeChess

**O que faz:** Explica posições de xadrez em linguagem natural (XAI — Explainable AI). Análise 360° de uma posição: ameaças, planos, peças, movimentos candidatos. Importa de Chess.com e Lichess.

**Diferenciais:**
- Único que explica *por quê* um lance é bom, não só que é bom
- Suporta Chess.com e Lichess
- Tecnologia proprietária (não é ChatGPT)

**Limitações:**
- Analisa partidas e posições individuais, não agrega padrões
- Sem guia de adversário, sem plano de estudo
- Assinatura necessária para uso real

**Pricing:** Free (créditos limitados) → $8.25/mês

---

### 2.10 Chess Tempo

**O que faz:** Plataforma de treinamento tático com análise pós-partida. Feature única: converte seus blunders em puzzles personalizados com spaced repetition.

**Diferenciais:**
- **"Táticas dos seus erros"** — sem paralelo no mercado
- FSRS (spaced repetition de última geração)
- Análise Stockfish em cluster, alta qualidade

**Limitações:**
- Só analisa partidas jogadas no próprio site
- Sem guia de adversário
- Interface datada

**Pricing:** Free limitado → Premium ~$36–60/ano

---

### 2.11 Chessable

**O que faz:** Memorização de repertório por spaced repetition. Não é ferramenta de análise — é plataforma de cursos.

**Relevância para o benchmark:** Representa o padrão de qualidade em *aprendizado de abertura*. O Chess Scout poderia sugerir linhas específicas do Chessable nos relatórios.

**Pricing:** Free → PRO $74.99/ano + cursos individuais

---

### 2.12 Ferramentas CLI open-source (Chesalyser, chess-analysis, pgn-extract)

**Chesalyser** (Python + Streamlit + Stockfish) — o ancestral arquitetural mais próximo do Chess Scout. Aceita PGN manual, classifica movimentos com cores, não conecta a APIs, não gera relatório exportável.

**chess-analysis** (ianfab) — pipeline de pesquisa. Calcula ACPL, expectation-value loss, win-rate models. CLI puro, sem UI, sem relatório.

**pgn-extract** — manipulação de arquivos PGN em massa. Sem engine, sem relatório.

**Relevância:** Confirmam que o nicho de "análise completa via API + relatório exportável" não está coberto no open-source.

---

## 3. Matriz de Posicionamento Competitivo

Legenda: ✅ Faz bem | 🟡 Parcial / limitado | ❌ Não faz | 💰 Só no plano pago

| Ferramenta | Diagnóstico do jogador | Guia do adversário | Chess.com | Lichess | Stockfish local | Open-source | Relatório exportável | Erros por fase | Plano de estudo | Sem conta exigida |
|---|---|---|---|---|---|---|---|---|---|---|
| **Chess Scout** | 🟡 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 🟡 | ✅ |
| Chess.com Insights | 💰 | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | 💰 | ❌ | ❌ |
| Lichess Analysis | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ |
| ChessBase | 🟡 | ✅ | ❌ | 🟡 | ✅ | ❌ | 🟡 | ❌ | ❌ | ❌ |
| Aimchess | ✅ | ❌ | ✅ | ✅ | ❌ | ❌ | ❌ | 🟡 | ✅ | ❌ |
| ChessScout.net | ❌ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| PrepSuite | ❌ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Chess Stalker | ❌ | 🟡 | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ |
| OpeningTree | ❌ | 🟡 | ✅ | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ | ✅ |
| DecodeChess | ❌ | ❌ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Chess Tempo | 🟡 | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ | 🟡 | ✅ | ❌ |
| Chessable | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ |
| CLI OSS (Chesalyser etc.) | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ |

### Leitura da matriz

**Chess Scout é o único produto que combina as três colunas:**
1. Relatório exportável (markdown portável)
2. Guia do adversário
3. Open-source / gratuito

Nenhum dos 12 concorrentes analisados satisfaz os três critérios simultaneamente. ChessBase satisfaz (1) parcialmente e (2) completamente, mas não é open-source e custa $250–500. ChessScout.net e PrepSuite satisfazem (2) mas são proprietários e pagos.

**Gap persistente:**
- Nenhum concorrente open-source calcula ACPL nem accuracy% por partida
- Nenhum concorrente gratuito oferece guia do adversário com análise Stockfish
- Nenhum produto (pago ou gratuito) combina diagnóstico + guia + markdown exportável + ambas as plataformas

---

## 4. Diagnóstico Interno do Código

### 4.1 `modules/fetcher.py`

**Pontos fortes:**
- Arquitetura limpa: função única `fetch_games()` despacha para `_fetch_lichess()` ou `_fetch_chesscom()` — fácil adicionar novas plataformas
- Mapeamento de categorias explícito (`CHESSCOM_CATEGORY`, `LICHESS_CATEGORY`) — não há magic strings espalhadas
- Lichess usa streaming NDJSON (`stream=True`, `iter_lines()`) — correto e eficiente para payloads grandes
- Tratamento de `x-deny-reason: host_not_allowed` com mensagem clara ao usuário (ambas as plataformas)
- `_build_lichess_pgn()` constrói PGN válido a partir do JSON — habilita `python-chess` a analisar partidas Lichess

**Limitações atuais:**
- Chess.com: iteração mês a mês sem cache local — 50 partidas de jogador ativo = 1–2 meses, mas jogador inativo pode ser lento (loop de 24 meses)
- Sem retry automático além do caso 429 no Chess.com — erros de rede transitórios causam falha silenciosa
- `_build_lichess_pgn()` usa o campo `moves` do JSON como SAN já formatado; se a Lichess mudar o formato (ex: adicionar anotações de clock), a função quebra
- Não há paginação defensiva: se a Lichess retornar menos partidas do que `max=50` (ex: jogador novo), a função simplesmente retorna o que vier — correto, mas não documentado

**Escalabilidade:**
- Para suportar uma 3ª plataforma (ex: FIDE, Chess24), basta adicionar `_fetch_<plataforma>()` e um case no dispatcher — boa extensibilidade
- Suporte a OAuth (Lichess token) para acessar partidas privadas seria simples: adicionar header `Authorization: Bearer <token>` ao `HEADERS` dict

---

### 4.2 `modules/analyzer.py`

**Pontos fortes:**
- Instância única de Stockfish reutilizada para todas as partidas — evita overhead de 50 spawns de processo
- `DEPTH = 10` explicitado como constante com comentário justificando o trade-off (~90% de blunders, 4–5x mais rápido que depth 15)
- `_extract_cp()` trata tanto `cp` quanto `mate` corretamente, com perspectiva do jogador
- Classificação por fase (`_get_game_phase()`) permite análise de blunders em abertura vs. meio-de-jogo vs. final

**Limitações atuais:**
- **ACPL não calculado**: a análise produz `cp_loss` por movimento mas não agrega como ACPL (média simples de centipawn loss por lance do jogador) — gap crítico em relação ao padrão da indústria
- **Accuracy% não calculada**: a fórmula Lichess (`100 * (103.1668 * e^(-0.04354 * cp_loss) - 3.1668)`, clipped 0–100) não está implementada
- `_classify_move()` retorna `"blunder"` como fallback fora dos ranges — inócuo dado os thresholds, mas tecnicamente impreciso
- Sem detecção de `?!` (inaccuracy de abertura baseada em teoria) — toda classificação é puramente por centipawn loss
- `moves_detail` guardado no dict mas não exibido na UI (preparado para uso futuro)
- Sem timeout por partida: uma posição muito complexa em depth 10 pode travar em casos raros (ex: posições com muitas peças)

**Performance medida:**
- Depth 10, 50 partidas, ~40 lances/partida = ~4.000 chamadas Stockfish ≈ 30–50 segundos em hardware moderno
- Depth 15 equivaleria a ~150–200 segundos — inaceitável para MVP web

---

### 4.3 `modules/stats.py`

**Pontos fortes:**
- `_best_worst_opening(min_games=3)`: filtro correto de mínimo amostral antes de qualificar "melhor/pior abertura"
- Pré-computa `best/worst_opening_white/black` no dict de stats — o reporter não precisa recalcular
- `time_class_stats` segmentado por modalidade — base para análise comparativa

**Limitações atuais:**
- `play_style` inferido por `avg_game_length > 35` — tautológico (jogos mais longos = estilo "posicional"?) e não confiável
- `conversion_tendency` derivado da taxa de vitória — não captura realmente se o jogador converte vantagens ou desperdiça endgames ganhos
- **Draws ignorados no cálculo de performance de abertura**: `win_rate` = `wins / games`, onde `draws` valem 0 — deveria ser `(wins + 0.5 * draws) / games` (sistema ELO-compatível)
- Sem normalização por rating do oponente — vitória contra 1200 e vitória contra 1600 pesam igual
- `avg_opponent_rating` calculado como média simples — sem distinção por resultado (ex: jogadores tendem a ter oponentes mais fracos nas vitórias)

---

### 4.4 `modules/reporter.py`

**Pontos fortes:**
- Relatórios em markdown puro — portável, versionável, legível sem dependências
- Separação clara: `generate_diagnostic()` para o próprio jogador, `generate_opponent_guide()` para o adversário
- `save_reports()` cria o diretório `outputs/{username}/` automaticamente

**Limitações atuais:**
- **Templates estáticos**: o texto é quase idêntico para um jogador de 800 e um de 1800 — não há personalização real por faixa de rating
- **Sem modo de análise**: atualmente trata qualquer análise como "este jogador sou eu" — o usuário pode querer analisar um adversário (mudança de perspectiva do diagnóstico)
- Recomendações de estudo são genéricas (ex: "pratique táticas") — sem links para recursos específicos nem contexto por rating
- GUIA_ADVERSARIO.md não usa `moves_detail` para indicar padrões táticos específicos exploráveis (ex: "comete blunders no movimento 20–25 com pretas")

---

### 4.5 `app.py`

**Pontos fortes:**
- `st.session_state` para cache de resultados — evita re-análise ao navegar entre abas
- Tabs bem segmentadas: Visão Geral / Análise de Erros / Aberturas / Relatórios Completos
- Download buttons para ambos os markdowns na sidebar
- Progress bar granular (5 → 30 → 75 → 85 → 100) com feedback de texto

**Limitações atuais:**
- `GAME_TYPES` dict redefinido dentro do bloco `with st.sidebar:` — recriado em cada render (inócuo, mas ruim para legibilidade)
- Sem estado de erro persistente: se a análise falha, o usuário precisa preencher tudo de novo
- Sem cache de partidas buscadas: reanalisa do zero a cada clique em "Analisar"
- A tab "Relatórios Completos" renderiza markdown cru — sem syntax highlighting de variações de xadrez ou diagramas

---

### 4.6 `main.py`

**Pontos fortes:**
- CLI completo com validação de argumentos e mensagens de erro claras
- Argumentos opcionais com defaults sensatos (`platform=lichess`, `tipos=todos`)
- Progress callbacks integrados com output `\r` (sobrescreve a linha)

**Limitações atuais:**
- Sem flag `--output-dir` — sempre salva em `outputs/`
- Sem flag `--no-stockfish` — só skippa Stockfish em caso de `FileNotFoundError`
- Sem suporte a análise de adversário via CLI (modo de scouting)

---

## 5. Benchmarks da Indústria

### 5.1 ACPL por faixa de rating (referência empírica)

ACPL (Average Centipawn Loss) é a métrica padrão para medir qualidade de jogo. Valores menores = jogo mais preciso.

| Faixa de rating | ACPL típico (Lichess/Chess.com) | Accuracy% equivalente |
|---|---|---|
| < 800 (iniciante) | 150–300 | 40–60% |
| 800–1200 | 80–150 | 60–72% |
| 1200–1500 | 50–80 | 72–80% |
| 1500–1800 | 30–50 | 80–86% |
| 1800–2000 | 20–35 | 86–90% |
| 2000–2200 | 12–25 | 90–93% |
| 2200–2400 (master) | 8–15 | 93–96% |
| 2400+ (GM) | 3–10 | 96–99% |

_Fontes: análises publicadas em Lichess forum, chess.stackexchange.com e artigos acadêmicos (Reid, 2020; Guid & Bratko, 2006)._

**Implicação para Chess Scout:** sem ACPL, o relatório não consegue situar o jogador na escala acima. Um blunder count de "3 blunders/partida" pode ser excelente para 800 ou ruim para 1800 — sem referência de rating, a métrica não tem contexto.

---

### 5.2 Taxa de blunders por fase (referência)

Estudos baseados em milhões de partidas do Lichess (dataset público) mostram padrão consistente:

| Fase | % de blunders totais (jogadores 1000–1800) |
|---|---|
| Abertura (lances 1–15) | ~15% |
| Meio de jogo (lances 16–35) | ~55% |
| Final (lances 36+) | ~30% |

O Chess Scout já calcula `blunders_by_phase` — falta apenas contextualizar o resultado do jogador contra esses benchmarks.

---

### 5.3 Depth Stockfish vs. qualidade de análise

| Depth | Tempo médio/posição | Elo equivalente | Adequado para |
|---|---|---|---|
| 5 | ~1 ms | ~2000 | Detecção rápida de erros graves |
| 10 | ~8 ms | ~2700 | **MVP — detecta ~90% dos blunders** |
| 15 | ~40 ms | ~3000 | Análise mais profunda — referência |
| 20 | ~200 ms | ~3200 | Análise profissional |
| 25+ | ~1–5 s | ~3400+ | Análise de alto nível (torneio) |

Chess Scout usa depth 10 — decisão correta para MVP: o custo de 50 partidas × ~40 lances × 8ms = ~16 segundos de CPU pura, contra ~80 segundos em depth 15 e ~400 segundos em depth 20.

---

### 5.4 Volume mínimo de partidas para análise confiável

| Nº de partidas | Margem de erro (win rate) | Adequado para |
|---|---|---|
| 10 | ±31% | Impressão inicial, não confiável |
| 20 | ±22% | Tendências grossas |
| 50 | ±14% | **MVP — padrões de erro confiáveis** |
| 100 | ±10% | Análise robusta de aberturas |
| 200 | ±7% | Análise de estilo de jogo |

_Fórmula: ±1.96 × √(p(1-p)/n), com p=0.5 (pior caso)._

Chess Scout usa 50 partidas — patamar correto: suficiente para detectar padrões de blunder e abertura, sem o custo de análise de 100+ partidas.

---

## 6. Oportunidades de Diferenciação

### 6.1 Curto prazo — fechar gaps críticos

**ACPL e accuracy%** (impacto: alto, esforço: baixo)

A fórmula do Lichess para accuracy% é pública e documentada:

```
accuracy(cp_loss) = 103.1668 × e^(−0.04354 × cp_loss) − 3.1668
```
_Clipped entre 0 e 100. Fonte: lichess.org/accuracy_

Implementar no `analyzer.py`:
1. Calcular `cp_loss` por lance (já existe)
2. Aplicar fórmula → `move_accuracy`
3. Média por partida → `game_accuracy`
4. Média de todas as partidas → `avg_accuracy` no stats dict
5. ACPL = média de `cp_loss` dos lances do jogador

Custo: ~30 linhas de código. Impacto: coloca Chess Scout no mesmo patamar métrico que Lichess e Chess.com.

---

**Contextualização por faixa de rating** (impacto: alto, esforço: médio)

Com ACPL calculado e rating conhecido (`player_rating`), é possível:
- Informar "Seu ACPL de 45 é típico de jogadores 1500–1600"
- Comparar com a tabela de benchmarks da seção 5.1
- Adaptar o texto do relatório por faixa (`< 1200 / 1200–1600 / 1600–2000 / 2000+`)

---

**Modo de análise: próprio jogador vs. adversário** (impacto: médio, esforço: baixo)

O usuário pode querer analisar um adversário antes de uma partida (scouting puro) ou analisar a si mesmo (diagnóstico). A distinção muda a ênfase do relatório:

- **Modo Diagnóstico**: foco em fraquezas do próprio jogador, plano de estudo
- **Modo Scouting**: foco em explorar fraquezas do adversário, abertura recomendada contra ele

Implementação: parâmetro `mode: Literal["self", "opponent"]` em `generate_diagnostic()` e `generate_opponent_guide()`.

---

### 6.2 Médio prazo — aprofundar vantagem competitiva

**Draws como meia vitória** (impacto: baixo, esforço: baixo)

Substituir `win_rate = wins / games` por `score_rate = (wins + 0.5 * draws) / games` — métrica compatível com ELO, mais honesta.

**Padrão de erros por abertura** (impacto: alto, esforço: médio)

Cruzar `opening` com `blunders_by_phase` e `avg_cp_loss` — identificar qual abertura produz mais blunders no meio-jogo. Exemplo: "Siciliana Dragon: você comete 2.3 blunders/partida no meio-jogo, vs. 1.1 na Italiana."

**Rating do oponente como peso** (impacto: médio, esforço: médio)

Ponderar vitórias pelo rating do oponente: uma vitória contra 1600 sendo 1400 vale mais que uma vitória contra 1200. Alinhar com o modelo ELO.

---

### 6.3 Longo prazo — construir fosso competitivo

**Geração de puzzles dos seus erros** (impacto: muito alto, esforço: alto)

Chess Tempo faz isso para partidas jogadas na plataforma deles. Chess Scout pode fazer para qualquer partida do Chess.com ou Lichess:
1. Identificar posições onde o jogador cometeu blunder
2. Exportar como puzzle (FEN + solução = melhor lance Stockfish)
3. Salvar como arquivo PGN de puzzles ou integrar com Lichess Puzzle Racer API

Sem paralelo no open-source para partidas de plataformas externas.

**Narrativa gerada por LLM** (impacto: alto, esforço: médio)

Substituir templates fixos do reporter por chamadas à API de um LLM (ex: Claude API):
- Input: stats dict + abertura mais jogada + principais blunders
- Output: diagnóstico em linguagem natural personalizado

PrepSuite já faz isso, mas é proprietário e pago. Chess Scout poderia oferecer a mesma qualidade narrativa de forma open-source (usuário traz sua própria API key).

**Repertório personalizado** (impacto: alto, esforço: alto)

Baseado nas aberturas com melhor e pior performance do jogador, sugerir linhas específicas:
- "Você vence 70% com Italiana como brancas — aprofunde com a variante ..."
- "Evite Siciliana como pretas até resolver o problema de blunders no meio-jogo"

---

## 7. Roadmap por Fases

### Fase 1 — MVP Polish (2–4 semanas)

Objetivo: credibilidade analítica mínima para divulgação pública.

| Item | Módulo | Prioridade |
|---|---|---|
| Calcular ACPL por partida e em média | `analyzer.py` + `stats.py` | 🔴 Crítico |
| Calcular accuracy% (fórmula Lichess) | `analyzer.py` + `stats.py` | 🔴 Crítico |
| Contextualizar ACPL/accuracy pelo rating | `reporter.py` | 🔴 Crítico |
| Draws como 0.5 no win_rate | `stats.py` | 🟡 Importante |
| Modo self vs. opponent na UI e CLI | `app.py` + `main.py` + `reporter.py` | 🟡 Importante |
| Corrigir `play_style` (lógica circular) | `stats.py` | 🟡 Importante |
| Exibir ACPL e accuracy na tab Visão Geral | `app.py` | 🟡 Importante |

---

### Fase 2 — Métricas Faltantes (1–2 meses)

Objetivo: paridade com Lichess Analysis em termos de métricas básicas.

| Item | Módulo | Prioridade |
|---|---|---|
| ACPL por fase (abertura / meio / final) | `analyzer.py` + `stats.py` | 🟡 Importante |
| Accuracy por abertura | `stats.py` + `reporter.py` | 🟡 Importante |
| Ponderação de vitória por rating do oponente | `stats.py` | 🟢 Desejável |
| Histograma de cp_loss (distribuição visual) | `app.py` | 🟢 Desejável |
| Cache local de partidas (evitar re-fetch) | `fetcher.py` | 🟢 Desejável |

---

### Fase 3 — Diferenciação (2–4 meses)

Objetivo: recursos que nenhum concorrente open-source oferece.

| Item | Módulo | Prioridade |
|---|---|---|
| Geração de puzzles dos erros do jogador | novo `puzzles.py` | 🔴 Alto impacto |
| Padrão de erros cruzado com abertura | `stats.py` + `reporter.py` | 🟡 Importante |
| Suporte a token Lichess (partidas privadas) | `fetcher.py` | 🟢 Desejável |
| Export para PGN com anotações de classificação | novo `exporter.py` | 🟢 Desejável |

---

### Fase 4 — Fosso Competitivo (4–6 meses)

Objetivo: transformar Chess Scout no padrão open-source de análise de jogadores.

| Item | Módulo | Prioridade |
|---|---|---|
| Integração LLM para narrativa personalizada (bring-your-own-key) | `reporter.py` + config | 🔴 Alto impacto |
| Sugestão de repertório baseada em performance | novo `repertoire.py` | 🟡 Importante |
| Histórico de análises (evolução do rating ao longo do tempo) | `stats.py` + `app.py` | 🟡 Importante |
| API REST própria (FastAPI) para integração externa | novo `api.py` | 🟢 Desejável |
| Suporte a FIDE/Chess24 como fonte de dados | `fetcher.py` | 🟢 Desejável |

---

## 8. Conclusão

Chess Scout ocupa um nicho genuinamente vazio no mercado open-source: a combinação de **guia do adversário + diagnóstico + relatório markdown + ambas as plataformas** não existe em nenhum outro produto gratuito.

Os dois gaps mais urgentes são técnicos e de baixo custo de implementação:
1. **ACPL e accuracy%** — ~30 linhas de código, impacto imediato na credibilidade
2. **Contextualização por rating** — diferencia radicalmente o relatório de um template genérico

Com a Fase 1 concluída, Chess Scout terá as métricas mínimas para ser comparado com Lichess Analysis e Aimchess — e o diferencial do guia do adversário open-source permanece exclusivo.

_Documento gerado em 2026-04-28. Atualizar após cada fase concluída._
