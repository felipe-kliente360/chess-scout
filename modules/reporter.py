import os
from datetime import date

try:
    import anthropic
    _HAS_ANTHROPIC = True
except ImportError:
    _HAS_ANTHROPIC = False

try:
    import markdown as _md_lib
    import weasyprint as _weasyprint
    _HAS_PDF = True
except ImportError:
    _HAS_PDF = False

_PDF_CSS = """
@page { margin: 2cm; }
body { font-family: Georgia, serif; font-size: 11pt; line-height: 1.65; color: #1a1a1a; }
h1 { font-size: 20pt; border-bottom: 2px solid #1a1a1a; padding-bottom: 6px; margin-bottom: 4px; }
h2 { font-size: 14pt; margin-top: 22px; border-bottom: 1px solid #ccc; padding-bottom: 4px; }
h3 { font-size: 11.5pt; color: #333; margin-top: 14px; }
p  { margin: 6px 0; }
ul, ol { margin: 6px 0 6px 20px; }
li { margin-bottom: 3px; }
table { border-collapse: collapse; width: 100%; margin: 12px 0; font-size: 10pt; }
th { background: #f0f0f0; padding: 6px 10px; text-align: left; border: 1px solid #bbb; font-weight: bold; }
td { padding: 5px 10px; border: 1px solid #ddd; }
tr:nth-child(even) td { background: #fafafa; }
em { color: #555; }
strong { color: #111; }
hr { border: none; border-top: 1px solid #ddd; margin: 18px 0; }
"""


def md_to_pdf(md_text: str) -> bytes | None:
    if not _HAS_PDF:
        return None
    try:
        html_body = _md_lib.markdown(md_text, extensions=["tables", "fenced_code"])
        html = (
            "<!DOCTYPE html><html><head>"
            "<meta charset='utf-8'>"
            f"<style>{_PDF_CSS}</style>"
            f"</head><body>{html_body}</body></html>"
        )
        return _weasyprint.HTML(string=html).write_pdf()
    except Exception:
        return None

_SYSTEM = """Você é um analista de xadrez de elite especializado em construir relatórios profundos e acionáveis sobre jogadores de xadrez online.

ESTILO:
- Prosa fluida e analítica, não apenas bullet points
- Observações específicas baseadas nos dados fornecidos
- Linguagem técnica de xadrez (desenvolvimento, estrutura de peões, iniciativa, conversão, zugzwang)
- Tom profissional mas acessível, como um coach de xadrez experiente
- Insights psicológicos baseados nos padrões de erros e estilo de jogo

QUALIDADE ESPERADA:
Os relatórios devem ter profundidade similar a análises profissionais de grandes mestres, como análises publicadas sobre jogadores de elite. Cada seção deve conter observações genuínas baseadas nos dados, não frases genéricas. Conecte os padrões de erro ao estilo geral de jogo e às aberturas escolhidas.

INTERPRETAÇÃO DE DADOS:
- ACPL < 20: qualidade excepcional (nível master/GM)
- ACPL 20-40: qualidade sólida (nível avançado)
- ACPL 40-60: qualidade intermediária com lapsos frequentes
- ACPL > 60: problemas sérios de precisão em cálculo
- Blunders/partida > 1.5: tendência de colapso tático sob pressão
- Taxa de vitória > 60%: jogador em excelente forma
- Diferença Brancas/Pretas > 10pp: desequilíbrio significativo a explorar

ESTRUTURA DOS RELATÓRIOS:
Escreva em português brasileiro. Cite números específicos. Conecte as aberturas ao estilo geral. Seja concreto."""


def _call_claude(prompt: str, max_tokens: int = 2000) -> str | None:
    if not _HAS_ANTHROPIC:
        return None
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return None
    try:
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model="claude-opus-4-7",
            max_tokens=max_tokens,
            system=[{"type": "text", "text": _SYSTEM, "cache_control": {"type": "ephemeral"}}],
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text
    except Exception:
        return None


def _pct(value: float) -> str:
    return f"{value:.1f}%"


def _opening_table(openings: list[dict]) -> str:
    if not openings:
        return "_Dados insuficientes_\n"
    header = "| Abertura | Partidas | % Vitória |\n|---|---|---|\n"
    rows = ""
    for o in openings:
        rows += f"| {o['opening']} | {o['games']} | {_pct(o['win_rate'])} |\n"
    return header + rows


def _build_stats_summary(stats: dict, username: str) -> str:
    error_stats = stats.get("error_stats", {})
    play_style = stats.get("play_style", {})
    color_stats = stats.get("color_stats", {})
    averages = error_stats.get("averages_per_game", {})
    bp = error_stats.get("blunders_by_phase", {})

    lines = [
        f"JOGADOR: {username}",
        f"Rating atual: {stats.get('current_rating', 'N/A')}",
        f"Modalidade principal: {stats.get('primary_time_class', 'N/A')}",
        f"Total de partidas: {stats.get('total_games', 0)}",
        f"Vitórias: {stats.get('wins', 0)} ({stats.get('win_rate', 0):.1f}%)",
        f"Derrotas: {stats.get('losses', 0)}",
        f"Empates: {stats.get('draws', 0)}",
        "",
        "QUALIDADE DAS JOGADAS:",
        f"ACPL (perda média por lance em centipeões): {error_stats.get('acpl', 'N/A')}",
        f"Blunders por partida: {averages.get('blunder', 0)}",
        f"Erros por partida: {averages.get('mistake', 0)}",
        f"Imprecisões por partida: {averages.get('inaccuracy', 0)}",
        f"Partidas com análise Stockfish: {error_stats.get('games_analyzed', 0)}",
        "",
        "BLUNDERS POR FASE:",
        f"Abertura (lances 1-15): {bp.get('opening', 0)}",
        f"Meio de Jogo (lances 16-35): {bp.get('middlegame', 0)}",
        f"Final de Jogo (lance 36+): {bp.get('endgame', 0)}",
        "",
        "ESTATÍSTICAS POR COR:",
        f"Brancas: {color_stats.get('white', {}).get('total', 0)} partidas, {color_stats.get('white', {}).get('win_rate', 0):.1f}% vitórias",
        f"Pretas: {color_stats.get('black', {}).get('total', 0)} partidas, {color_stats.get('black', {}).get('win_rate', 0):.1f}% vitórias",
        "",
        "ESTILO DE JOGO:",
        f"Classificação: {play_style.get('style', 'N/A')}",
        f"Comprimento médio de partida: {play_style.get('avg_game_length', 0)} lances",
        f"Tendência de conversão: {play_style.get('conversion_tendency', 'N/A')}",
        f"Comportamento em posições perdidas: {play_style.get('fighting_tendency', 'N/A')}",
    ]

    openings_white = stats.get("openings_white", [])
    if openings_white:
        lines += ["", "TOP ABERTURAS COM BRANCAS:"]
        for o in openings_white[:5]:
            lines.append(f"  {o['opening']}: {o['games']} partidas, {o['win_rate']:.1f}% vitórias")

    openings_black = stats.get("openings_black", [])
    if openings_black:
        lines += ["", "TOP ABERTURAS COM PRETAS:"]
        for o in openings_black[:5]:
            lines.append(f"  {o['opening']}: {o['games']} partidas, {o['win_rate']:.1f}% vitórias")

    best_white = stats.get("best_opening_white")
    worst_white = stats.get("worst_opening_white")
    best_black = stats.get("best_opening_black")
    worst_black = stats.get("worst_opening_black")

    lines += ["", "DESTAQUES DE ABERTURA:"]
    if best_white:
        lines.append(f"  Melhor abertura com Brancas: {best_white['opening']} ({best_white['win_rate']:.1f}% em {best_white['games']} partidas)")
    if worst_white:
        lines.append(f"  Pior abertura com Brancas: {worst_white['opening']} ({worst_white['win_rate']:.1f}% em {worst_white['games']} partidas)")
    if best_black:
        lines.append(f"  Melhor abertura com Pretas: {best_black['opening']} ({best_black['win_rate']:.1f}% em {best_black['games']} partidas)")
    if worst_black:
        lines.append(f"  Pior abertura com Pretas: {worst_black['opening']} ({worst_black['win_rate']:.1f}% em {worst_black['games']} partidas)")

    return "\n".join(lines)


def _claude_diagnostic(stats: dict, username: str) -> str | None:
    today = date.today().isoformat()
    summary = _build_stats_summary(stats, username)
    openings_white = stats.get("openings_white", [])
    openings_black = stats.get("openings_black", [])

    prompt = f"""Com base nos dados abaixo, escreva um DIAGNÓSTICO completo e profundo do jogador {username}.

{summary}

Escreva o relatório COMPLETO em markdown no seguinte formato:

# Diagnóstico — {username}
_Gerado em {today}_

---

## Sumário Executivo
[2-3 parágrafos narrativos sobre o perfil do jogador, destacando o nível de jogo baseado no ACPL, taxa de vitória, estilo predominante e principais características]

---

## Análise por Fase do Jogo

### Abertura
[Análise específica das escolhas de abertura, consistência, transposições e vulnerabilidades nessa fase]

### Meio de Jogo
[Análise do estilo tático vs posicional, frequência de blunders nessa fase, tipo de posições que domina ou tem dificuldade]

### Final de Jogo
[Técnica de conversão, erros críticos no final, tendências identificadas]

---

## Aberturas com Brancas

{_opening_table(openings_white[:7])}

## Aberturas com Pretas

{_opening_table(openings_black[:7])}

---

## Perfil Psicológico
[1-2 parágrafos sobre comportamento sob pressão, como reage a posições perdidas, padrões de colapso, mentalidade identificada nos dados]

---

## Padrão de Erros

| Tipo | Total | Média/Partida |
|---|---|---|
| Blunders | {stats.get('error_stats', {}).get('totals', {}).get('blunder', 0)} | {stats.get('error_stats', {}).get('averages_per_game', {}).get('blunder', 0)} |
| Erros | {stats.get('error_stats', {}).get('totals', {}).get('mistake', 0)} | {stats.get('error_stats', {}).get('averages_per_game', {}).get('mistake', 0)} |
| Imprecisões | {stats.get('error_stats', {}).get('totals', {}).get('inaccuracy', 0)} | {stats.get('error_stats', {}).get('averages_per_game', {}).get('inaccuracy', 0)} |

**ACPL:** {stats.get('error_stats', {}).get('acpl', 'N/A')} centipeões por lance

**Blunders por fase:**
- Abertura: {stats.get('error_stats', {}).get('blunders_by_phase', {}).get('opening', 0)}
- Meio de Jogo: {stats.get('error_stats', {}).get('blunders_by_phase', {}).get('middlegame', 0)}
- Final de Jogo: {stats.get('error_stats', {}).get('blunders_by_phase', {}).get('endgame', 0)}

---

## Plano de Estudo

### Prioridade Alta — 30 dias
[3-4 itens específicos baseados nas maiores fraquezas identificadas]

### Prioridade Média — 90 dias
[3 itens para consolidação e expansão]

### Prioridade Baixa — refinamento contínuo
[2-3 itens de polimento de longo prazo]

---

REGRAS:
- Escreva APENAS o markdown do relatório, sem introdução ou comentários extras
- Cite números e percentuais específicos dos dados fornecidos
- Para as seções de tabelas já formatadas acima, copie-as exatamente como estão
- Nas seções narrativas, escreva prosa analítica, não apenas bullet points
"""
    return _call_claude(prompt, max_tokens=2500)


def _template_diagnostic(stats: dict, username: str) -> str:
    today = date.today().isoformat()
    tc = stats.get("primary_time_class", "desconhecida")
    rating = stats.get("current_rating", "N/A")
    total = stats.get("total_games", 0)
    win_rate = stats.get("win_rate", 0)
    error_stats = stats.get("error_stats", {})
    averages = error_stats.get("averages_per_game", {})
    bp = error_stats.get("blunders_by_phase", {})
    play_style = stats.get("play_style", {})
    color_stats = stats.get("color_stats", {})

    white_wr = color_stats.get("white", {}).get("win_rate", 0)
    black_wr = color_stats.get("black", {}).get("win_rate", 0)
    better_color = "Brancas" if white_wr >= black_wr else "Pretas"
    worse_color = "Pretas" if white_wr >= black_wr else "Brancas"

    openings_white = stats.get("openings_white", [])
    openings_black = stats.get("openings_black", [])
    best_white = stats.get("best_opening_white")
    worst_white = stats.get("worst_opening_white")
    best_black = stats.get("best_opening_black")
    worst_black = stats.get("worst_opening_black")

    blunders_avg = averages.get("blunder", 0)
    mistakes_avg = averages.get("mistake", 0)
    style = play_style.get("style", "desconhecido")
    acpl = error_stats.get("acpl", "N/A")

    top_blunder_phase = max(bp, key=lambda k: bp[k], default="middlegame") if bp else "middlegame"
    phase_pt = {"opening": "Abertura", "middlegame": "Meio de Jogo", "endgame": "Final de Jogo"}

    doc = f"""# Diagnóstico — {username}
_Gerado em {today}_

---

## Sumário

| Campo | Valor |
|---|---|
| Jogador | {username} |
| Rating atual | {rating} |
| Modalidade principal | {tc.capitalize()} |
| Partidas analisadas | {total} |
| Taxa de vitória geral | {_pct(win_rate)} |
| ACPL | {acpl} |
| Estilo de jogo | {style.capitalize()} |

---

## Pontos Fortes

- Performance com {better_color}: **{_pct(max(white_wr, black_wr))}** de aproveitamento
- {play_style.get("conversion_tendency", "").capitalize()}
- {play_style.get("fighting_tendency", "").capitalize()}
"""

    if best_white:
        doc += f"- Abertura forte com Brancas: **{best_white['opening']}** ({_pct(best_white['win_rate'])} de vitória)\n"
    if best_black:
        doc += f"- Abertura forte com Pretas: **{best_black['opening']}** ({_pct(best_black['win_rate'])} de vitória)\n"

    doc += f"""
---

## Pontos Fracos

- Performance com {worse_color}: **{_pct(min(white_wr, black_wr))}** de aproveitamento
- Média de **{blunders_avg} blunders** e **{mistakes_avg} erros** por partida
- Fase mais crítica: **{phase_pt.get(top_blunder_phase, top_blunder_phase)}** (mais blunders nessa fase)
"""

    if worst_white:
        doc += f"- Abertura problemática com Brancas: **{worst_white['opening']}** ({_pct(worst_white['win_rate'])} de vitória)\n"
    if worst_black:
        doc += f"- Abertura problemática com Pretas: **{worst_black['opening']}** ({_pct(worst_black['win_rate'])} de vitória)\n"

    doc += f"""
---

## Análise por Fase do Jogo

### Abertura
- Aberturas mais usadas com Brancas: {openings_white[0]["opening"] if openings_white else "N/A"}
- Aberturas mais usadas com Pretas: {openings_black[0]["opening"] if openings_black else "N/A"}
- Blunders na abertura: **{bp.get("opening", 0)}** no total

### Meio de Jogo
- Blunders no meio de jogo: **{bp.get("middlegame", 0)}** no total
- Estilo identificado: **{style}**

### Final de Jogo
- Blunders no final: **{bp.get("endgame", 0)}** no total
- Tendência: {play_style.get("conversion_tendency", "N/A")}

---

## Aberturas com Brancas

{_opening_table(openings_white[:7])}

## Aberturas com Pretas

{_opening_table(openings_black[:7])}

---

## Padrão de Erros

| Tipo | Total | Média/Partida |
|---|---|---|
| Blunders | {error_stats.get("totals", {}).get("blunder", 0)} | {averages.get("blunder", 0)} |
| Erros | {error_stats.get("totals", {}).get("mistake", 0)} | {averages.get("mistake", 0)} |
| Imprecisões | {error_stats.get("totals", {}).get("inaccuracy", 0)} | {averages.get("inaccuracy", 0)} |

**ACPL:** {acpl} centipeões por lance

**Blunders por fase:**
- Abertura: {bp.get("opening", 0)}
- Meio de Jogo: {bp.get("middlegame", 0)}
- Final de Jogo: {bp.get("endgame", 0)}

---

## Plano de Estudo

### Prioridade Alta — resolver em 30 dias
1. Reduzir blunders no **{phase_pt.get(top_blunder_phase, top_blunder_phase)}** (fase mais crítica)
2. Estudar táticas básicas: garfos, espetos, pinos e ataques duplos
3. Melhorar repertório de abertura com {worse_color}

### Prioridade Média — resolver em 90 dias
1. Melhorar conversão de vantagem em finais de jogo
2. Aprofundar estudo de aberturas: revisar **{worst_white["opening"] if worst_white else "abertura mais fraca"}** com Brancas
3. Treinar gestão de tempo para evitar erros em zeitnot

### Prioridade Baixa — refinamento contínuo
1. Aprimorar precisão em posições posicionais complexas
2. Expandir repertório de aberturas secundárias
3. Estudar partidas de mestres no estilo **{style}**
"""
    return doc


def generate_diagnostic(stats: dict, username: str) -> str:
    result = _claude_diagnostic(stats, username)
    if result:
        return result
    return _template_diagnostic(stats, username)


def _claude_opponent_guide(stats: dict, username: str) -> str | None:
    today = date.today().isoformat()
    summary = _build_stats_summary(stats, username)
    openings_white = stats.get("openings_white", [])
    openings_black = stats.get("openings_black", [])
    error_stats = stats.get("error_stats", {})
    bp = error_stats.get("blunders_by_phase", {})
    averages = error_stats.get("averages_per_game", {})

    prompt = f"""Com base nos dados abaixo, escreva um GUIA DO ADVERSÁRIO completo sobre como VENCER o jogador {username}.

{summary}

Escreva o relatório COMPLETO em markdown no seguinte formato:

# Guia do Adversário — {username}
_Gerado em {today}_

---

## Perfil Resumido

| Campo | Valor |
|---|---|
| Jogador | {username} |
| Rating | {stats.get("current_rating", "N/A")} |
| Modalidade principal | {stats.get("primary_time_class", "N/A")} |
| Partidas na amostra | {stats.get("total_games", 0)} |
| Taxa de vitória | {stats.get("win_rate", 0):.1f}% |
| ACPL | {error_stats.get("acpl", "N/A")} |

---

## Protocolo de Preparação de Abertura
[Análise específica de como explorar o repertório do adversário — quais aberturas forçar, quais evitar, variantes que desestabilizam o estilo dele]

### Aberturas dele com Brancas

{_opening_table(openings_white[:7])}

### Aberturas dele com Pretas

{_opening_table(openings_black[:7])}

---

## Estratégia de Meio de Jogo
[Como o estilo de jogo dele cria vulnerabilidades exploráveis — posições fechadas vs abertas, complexidade tática, pressão psicológica]

### Fase mais vulnerável
[Análise da fase onde ele mais erra com recomendações concretas de como chegar lá]

---

## Como Forçar Finais Favoráveis
[Baseado nas tendências de conversão e comportamento em posições perdidas — quando buscar final, quando evitar]

---

## Fraquezas Táticas Exploráveis

| Tipo de Erro | Total | Média/Partida |
|---|---|---|
| Blunders | {error_stats.get("totals", {}).get("blunder", 0)} | {averages.get("blunder", 0)} |
| Erros | {error_stats.get("totals", {}).get("mistake", 0)} | {averages.get("mistake", 0)} |
| Imprecisões | {error_stats.get("totals", {}).get("inaccuracy", 0)} | {averages.get("inaccuracy", 0)} |

**Blunders por fase:**
- Abertura: {bp.get("opening", 0)}
- Meio de Jogo: {bp.get("middlegame", 0)}
- Final de Jogo: {bp.get("endgame", 0)}

[Análise de como capitalizar sobre esses padrões de erro]

---

## Perfil Psicológico do Adversário
[Como ele reage à pressão, posições defensivas, zeitnot — como usar isso contra ele]

---

## Alertas — O Que Ele Faz Bem
[Pontos fortes genuínos que você deve respeitar e evitar alimentar]

---

## Checklist de Preparação Pré-Partida
[Lista de verificação específica e acionável para antes de jogar contra ele]

---

REGRAS:
- Escreva APENAS o markdown do relatório, sem introdução ou comentários extras
- Tom de coach preparando um atleta para um duelo específico
- Cite números e percentuais específicos dos dados
- Para as seções de tabelas já formatadas acima, copie-as exatamente como estão
- Nas seções narrativas, escreva prosa analítica e direta
"""
    return _call_claude(prompt, max_tokens=2500)


def _template_opponent_guide(stats: dict, username: str) -> str:
    today = date.today().isoformat()
    tc = stats.get("primary_time_class", "desconhecida")
    rating = stats.get("current_rating", "N/A")
    total = stats.get("total_games", 0)
    win_rate = stats.get("win_rate", 0)
    error_stats = stats.get("error_stats", {})
    averages = error_stats.get("averages_per_game", {})
    bp = error_stats.get("blunders_by_phase", {})
    play_style = stats.get("play_style", {})
    color_stats = stats.get("color_stats", {})
    openings_white = stats.get("openings_white", [])
    openings_black = stats.get("openings_black", [])

    white_wr = color_stats.get("white", {}).get("win_rate", 0)
    black_wr = color_stats.get("black", {}).get("win_rate", 0)
    weak_color = "Pretas" if white_wr >= black_wr else "Brancas"
    weak_color_key = "black" if white_wr >= black_wr else "white"

    style = play_style.get("style", "desconhecido")
    blunders_avg = averages.get("blunder", 0)
    acpl = error_stats.get("acpl", "N/A")
    top_blunder_phase = max(bp, key=lambda k: bp[k], default="middlegame") if bp else "middlegame"
    phase_pt = {"opening": "Abertura", "middlegame": "Meio de Jogo", "endgame": "Final de Jogo"}

    best_white = stats.get("best_opening_white")
    worst_white = stats.get("worst_opening_white")
    best_black = stats.get("best_opening_black")
    worst_black = stats.get("worst_opening_black")

    doc = f"""# Guia do Adversário — {username}
_Gerado em {today}_

---

## Perfil Resumido

| Campo | Valor |
|---|---|
| Jogador | {username} |
| Rating | {rating} |
| Modalidade principal | {tc.capitalize()} |
| Partidas na amostra | {total} |
| Taxa de vitória | {_pct(win_rate)} |
| ACPL | {acpl} |
| Estilo de jogo | {style.capitalize()} |
| Ponto fraco principal | Com {weak_color} ({_pct(color_stats.get(weak_color_key, {}).get("win_rate", 0))} de vitória) |

---

## Preparação de Abertura

### Aberturas dele com Brancas

{_opening_table(openings_white[:7])}

### Aberturas dele com Pretas

{_opening_table(openings_black[:7])}

### O que jogar CONTRA ele
"""

    if weak_color == "Pretas":
        doc += "- Quando você tiver as **Brancas**: force variantes que levem para as aberturas onde ele vai de Pretas\n"
        if worst_black:
            doc += f"- Tente transpor para **{worst_black['opening']}** — ele tem apenas {_pct(worst_black['win_rate'])} de vitória aqui\n"
    else:
        doc += "- Quando você tiver as **Pretas**: force variantes onde ele vai de Brancas com pior resultado\n"
        if worst_white:
            doc += f"- Tente provocar **{worst_white['opening']}** — ele tem apenas {_pct(worst_white['win_rate'])} de vitória aqui\n"

    doc += "\n### O que EVITAR\n\n"
    if best_white:
        doc += f"- Evite cair na **{best_white['opening']}** quando ele jogar de Brancas ({_pct(best_white['win_rate'])} de vitória)\n"
    if best_black:
        doc += f"- Evite cair na **{best_black['opening']}** quando ele jogar de Pretas ({_pct(best_black['win_rate'])} de vitória)\n"

    doc += f"""
---

## Estratégia de Meio de Jogo

"""
    if style == "agressivo":
        doc += """- Ele prefere jogo **tático e agressivo** — busque posições **fechadas e posicionais**
- Troque peças quando possível para reduzir o potencial tático dele
- Evite abrir o jogo ou criar tensão tática prematura
"""
    else:
        doc += """- Ele prefere jogo **posicional e estratégico** — busque posições **abertas e táticas**
- Crie complicações táticas: ele pode ter dificuldade em calcular variantes agudas
- Evite simplificações que levem a finais técnicos sem chances táticas
"""

    doc += f"""
### Fase mais vulnerável
- **{phase_pt.get(top_blunder_phase, top_blunder_phase)}** é onde ele comete mais blunders
- Aumente a pressão justamente nessa fase para forçar erros

---

## Como Forçar Finais Favoráveis

- Tendência de conversão: **{play_style.get("conversion_tendency", "N/A")}**
- Comportamento em posições perdidas: **{play_style.get("fighting_tendency", "N/A")}**
"""

    if "dificuldade" in play_style.get("conversion_tendency", ""):
        doc += "- **Recomendação**: lute para chegar em finais mesmo com desvantagem pequena — ele pode não converter\n"
    else:
        doc += "- **Atenção**: ele converte bem vantagens — evite finais onde ele esteja com material superior\n"

    doc += f"""
---

## Fraquezas Táticas Exploráveis

- ACPL de **{acpl}** — indicador de frequência de erros
- Média de **{blunders_avg} blunders por partida** — aguarde pacientemente o erro
- Fase crítica: **{phase_pt.get(top_blunder_phase, top_blunder_phase)}**
- Com **{weak_color}**, o desempenho cai significativamente

| Tipo de Erro | Total | Média/Partida |
|---|---|---|
| Blunders | {error_stats.get("totals", {}).get("blunder", 0)} | {averages.get("blunder", 0)} |
| Erros | {error_stats.get("totals", {}).get("mistake", 0)} | {averages.get("mistake", 0)} |
| Imprecisões | {error_stats.get("totals", {}).get("inaccuracy", 0)} | {averages.get("inaccuracy", 0)} |

**Blunders por fase:**
- Abertura: {bp.get("opening", 0)}
- Meio de Jogo: {bp.get("middlegame", 0)}
- Final de Jogo: {bp.get("endgame", 0)}

---

## Perfil Psicológico do Adversário

"""
    if style == "agressivo":
        doc += """- Jogador **agressivo**: pode se frustrar quando a posição é fechada e sem ação
- Tende a assumir riscos — capitalize quando ele se expõe demais
- Em posições defensivas prolongadas, pode perder a paciência e jogar imprecisamente
"""
    else:
        doc += """- Jogador **posicional**: prefere acumular vantagens pequenas ao longo do tempo
- Pode ter dificuldade quando forçado a calcular táticas complexas
- Pressão no relógio pode afetar a qualidade das suas decisões
"""

    doc += "\n---\n\n## Alertas — O Que Ele Faz Bem\n\n"
    if best_white:
        doc += f"- **{best_white['opening']}** com Brancas: {_pct(best_white['win_rate'])} de aproveitamento\n"
    if best_black:
        doc += f"- **{best_black['opening']}** com Pretas: {_pct(best_black['win_rate'])} de aproveitamento\n"

    stronger_color = "Brancas" if white_wr >= black_wr else "Pretas"
    doc += f"- Com **{stronger_color}** joga em {_pct(max(white_wr, black_wr))} de aproveitamento — não subestime\n"

    doc += f"""
---

## Checklist de Preparação Pré-Partida

- [ ] Revisar as aberturas favoritas dele com a cor que ele vai jogar
- [ ] Preparar linha específica para **{worst_black["opening"] if worst_black else "abertura mais fraca"}** (ponto mais fraco)
- [ ] Estudar 2-3 partidas recentes para identificar padrões de jogo
- [ ] Planejar buscar posições {"fechadas" if style == "agressivo" else "abertas e táticas"} no meio de jogo
- [ ] Estar preparado para durar até o **{phase_pt.get(top_blunder_phase, top_blunder_phase)}** — fase onde ele mais erra
"""
    return doc


def generate_opponent_guide(stats: dict, username: str) -> str:
    result = _claude_opponent_guide(stats, username)
    if result:
        return result
    return _template_opponent_guide(stats, username)


def save_reports(username: str, diagnostic: str, opponent_guide: str, output_dir: str = "outputs") -> tuple[str, str]:
    folder = os.path.join(output_dir, username)
    os.makedirs(folder, exist_ok=True)

    diag_pdf = md_to_pdf(diagnostic)
    guide_pdf = md_to_pdf(opponent_guide)

    if diag_pdf:
        diag_path = os.path.join(folder, "DIAGNOSTICO.pdf")
        with open(diag_path, "wb") as f:
            f.write(diag_pdf)
    else:
        diag_path = os.path.join(folder, "DIAGNOSTICO.md")
        with open(diag_path, "w", encoding="utf-8") as f:
            f.write(diagnostic)

    if guide_pdf:
        guide_path = os.path.join(folder, "GUIA_ADVERSARIO.pdf")
        with open(guide_path, "wb") as f:
            f.write(guide_pdf)
    else:
        guide_path = os.path.join(folder, "GUIA_ADVERSARIO.md")
        with open(guide_path, "w", encoding="utf-8") as f:
            f.write(opponent_guide)

    return diag_path, guide_path
