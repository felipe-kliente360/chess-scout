import os
from datetime import date


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


def generate_diagnostic(stats: dict, username: str) -> str:
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

    best_white = max(openings_white, key=lambda x: x["win_rate"], default=None) if openings_white else None
    worst_white = min(openings_white, key=lambda x: x["win_rate"], default=None) if openings_white else None
    best_black = max(openings_black, key=lambda x: x["win_rate"], default=None) if openings_black else None
    worst_black = min(openings_black, key=lambda x: x["win_rate"], default=None) if openings_black else None

    blunders_avg = averages.get("blunder", 0)
    mistakes_avg = averages.get("mistake", 0)
    style = play_style.get("style", "desconhecido")

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

| Tipo | Média por Partida |
|---|---|
| Excelentes | {averages.get("excellent", 0)} |
| Bons | {averages.get("good", 0)} |
| Imprecisões | {averages.get("inaccuracy", 0)} |
| Erros | {averages.get("mistake", 0)} |
| Blunders | {averages.get("blunder", 0)} |

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
2. Aprofundar estudo de aberturas: abandonar **{worst_white["opening"] if worst_white else "N/A"}** com Brancas
3. Treinar gestão de tempo para evitar erros em zeitnot

### Prioridade Baixa — refinamento contínuo
1. Aprimorar precisão em posições posicionais complexas
2. Expandir repertório de aberturas secundárias
3. Estudar partidas de mestres no estilo **{style}**
"""
    return doc


def generate_opponent_guide(stats: dict, username: str) -> str:
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
    top_blunder_phase = max(bp, key=lambda k: bp[k], default="middlegame") if bp else "middlegame"
    phase_pt = {"opening": "Abertura", "middlegame": "Meio de Jogo", "endgame": "Final de Jogo"}

    worst_white = min(openings_white, key=lambda x: x["win_rate"], default=None) if openings_white else None
    worst_black = min(openings_black, key=lambda x: x["win_rate"], default=None) if openings_black else None
    best_white = max(openings_white, key=lambda x: x["win_rate"], default=None) if openings_white else None
    best_black = max(openings_black, key=lambda x: x["win_rate"], default=None) if openings_black else None

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
| Estilo de jogo | {style.capitalize()} |
| Ponto fraco principal | Com {weak_color} ({_pct(color_stats.get(weak_color_key, {}).get("win_rate", 0))} de vitória) |

---

## Preparação de Abertura

### O que jogar CONTRA ele
"""

    if weak_color == "Pretas":
        doc += f"- Quando você tiver as **Brancas**: force variantes que levem para as aberturas onde ele vai de Pretas\n"
        if worst_black:
            doc += f"- Tente transpor para **{worst_black['opening']}** — ele tem apenas {_pct(worst_black['win_rate'])} de vitória com Pretas aqui\n"
    else:
        doc += f"- Quando você tiver as **Pretas**: force variantes que levem para as aberturas onde ele vai de Brancas com pior resultado\n"
        if worst_white:
            doc += f"- Tente provocar **{worst_white['opening']}** — ele tem apenas {_pct(worst_white['win_rate'])} de vitória com Brancas aqui\n"

    doc += f"""
### O que EVITAR

"""

    if best_white:
        doc += f"- Evite cair na **{best_white['opening']}** quando ele jogar de Brancas ({_pct(best_white['win_rate'])} de vitória)\n"
    if best_black:
        doc += f"- Evite cair na **{best_black['opening']}** quando ele jogar de Pretas ({_pct(best_black['win_rate'])} de vitória)\n"

    doc += f"""
---

## Estratégia de Meio de Jogo

### Que tipo de posição buscar
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

- Ele tem uma tendência de: **{play_style.get("conversion_tendency", "N/A")}**
- Jogo no final: **{play_style.get("fighting_tendency", "N/A")}**
"""

    if "dificuldade" in play_style.get("conversion_tendency", ""):
        doc += "- **Recomendação**: lute para chegar em finais mesmo com desvantagem pequena — ele pode não converter\n"
    else:
        doc += "- **Atenção**: ele converte bem vantagens — evite finais onde ele esteja com material superior\n"

    doc += f"""
---

## Fraquezas Táticas Exploráveis

- Média de **{blunders_avg} blunders por partida** — aguarde pacientemente o erro
- Fase crítica: **{phase_pt.get(top_blunder_phase, top_blunder_phase)}** — priorize manter posições complexas nessa fase
- Com **{weak_color}**, o desempenho cai significativamente — force-o a jogar com essa cor quando possível

### Top erros mais frequentes
| Tipo de Erro | Média por Partida |
|---|---|
| Blunders | {averages.get("blunder", 0)} |
| Erros | {averages.get("mistake", 0)} |
| Imprecisões | {averages.get("inaccuracy", 0)} |

---

## Perfil Psicológico

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

    doc += f"""
---

## Alertas — O que ele faz bem e você deve evitar

"""

    if best_white:
        doc += f"- **Cuidado com {best_white['opening']}** com Brancas: {_pct(best_white['win_rate'])} de aproveitamento\n"
    if best_black:
        doc += f"- **Cuidado com {best_black['opening']}** com Pretas: {_pct(best_black['win_rate'])} de aproveitamento\n"

    stronger_color = "Brancas" if white_wr >= black_wr else "Pretas"
    stronger_wr = max(white_wr, black_wr)
    doc += f"- Com **{stronger_color}** ele joga em {_pct(stronger_wr)} de aproveitamento — não subestime\n"

    doc += f"""
---

## Checklist de Preparação Pré-Partida

- [ ] Revisar as aberturas favoritas dele com a cor que ele vai jogar
- [ ] Preparar uma linha específica para **{worst_black["opening"] if worst_black else "sua abertura mais fraca"}** (ponto mais fraco)
- [ ] Estudar pelo menos 2-3 de suas partidas recentes para identificar padrões de jogo
- [ ] Planejar buscar posições {"fechadas" if style == "agressivo" else "abertas e táticas"} no meio de jogo
- [ ] Estar preparado para durar até o **{phase_pt.get(top_blunder_phase, top_blunder_phase)}** — fase onde ele mais erra
"""

    return doc


def save_reports(username: str, diagnostic: str, opponent_guide: str, output_dir: str = "outputs") -> tuple[str, str]:
    folder = os.path.join(output_dir, username)
    os.makedirs(folder, exist_ok=True)

    diag_path = os.path.join(folder, "DIAGNOSTICO.md")
    guide_path = os.path.join(folder, "GUIA_ADVERSARIO.md")

    with open(diag_path, "w", encoding="utf-8") as f:
        f.write(diagnostic)
    with open(guide_path, "w", encoding="utf-8") as f:
        f.write(opponent_guide)

    return diag_path, guide_path
