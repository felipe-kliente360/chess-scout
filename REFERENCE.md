# Referência de Estrutura dos Relatórios

Este documento define a estrutura-alvo dos relatórios gerados pelo chess-scout, inspirada na análise profissional disponível em `exemplo-report/`.

---

## DIAGNOSTICO.md — Perspectiva do Próprio Jogador

### 1. Sumário Executivo
Prosa narrativa (2-3 parágrafos) cobrindo:
- Nível geral baseado no ACPL e taxa de vitória
- Estilo predominante (posicional / agressivo / misto)
- Principais padrões identificados

### 2. Análise por Fase do Jogo

#### Abertura
- Repertório com Brancas e Pretas
- Consistência e profundidade de preparo
- Vulnerabilidades na transição para o meio-jogo

#### Meio de Jogo
- Estilo tático vs posicional
- Frequência de erros nessa fase
- Tipos de posições onde domina vs onde se perde

#### Final de Jogo
- Técnica de conversão
- Taxa de aproveitamento de vantagens
- Erros críticos no final

### 3. Tabelas de Aberturas
- Top 7 aberturas com Brancas (partidas + % vitória)
- Top 7 aberturas com Pretas (partidas + % vitória)

### 4. Perfil Psicológico
- Comportamento sob pressão
- Reação a posições defensivas
- Padrões de colapso identificados

### 5. Padrão de Erros
Tabela com totais e médias por partida:
- Blunders / Erros / Imprecisões
- ACPL (Average Centipawn Loss)
- Blunders por fase (abertura / meio-jogo / final)

### 6. Plano de Estudo
Dividido em três horizontes:
- **30 dias**: resolver as maiores fraquezas agudas
- **90 dias**: consolidação e repertório
- **Contínuo**: refinamento de longo prazo

---

## GUIA_ADVERSARIO.md — Perspectiva do Desafiante

### 1. Perfil Resumido
Tabela com dados-chave do adversário incluindo ACPL.

### 2. Protocolo de Preparação de Abertura
- Que aberturas forçar (explora fraquezas)
- Que aberturas evitar (onde ele é forte)
- Variantes de desestabilização

#### Tabelas de Aberturas
- Aberturas dele com Brancas (para você se preparar como Pretas)
- Aberturas dele com Pretas (para você se preparar como Brancas)

### 3. Estratégia de Meio de Jogo
- Que tipo de posição buscar baseado no estilo dele
- Como forçar a fase onde ele mais erra
- Gestão de complexidade tática

### 4. Como Forçar Finais Favoráveis
- Quando buscar simplificações
- Quando manter tensão
- Baseado no comportamento dele em posições perdidas

### 5. Fraquezas Táticas Exploráveis
- Tabela de erros com totais e médias
- Blunders por fase
- Como capitalizar sobre os padrões

### 6. Perfil Psicológico do Adversário
- Pontos de pressão que geram erros
- Reação ao zeitnot
- Como induzir frustração ou pressa

### 7. Alertas — O Que Ele Faz Bem
- Forças genuínas a respeitar
- Posições onde ele é perigoso

### 8. Checklist de Preparação Pré-Partida
Lista de verificação específica antes de jogar contra ele.

---

## Métricas Centrais

| Métrica | Fonte | Interpretação |
|---|---|---|
| ACPL | `stats.error_stats.acpl` | < 20 = master; 20-40 = avançado; 40-60 = intermediário; > 60 = problemas |
| Taxa de vitória | `stats.win_rate` | > 60% = excelente forma; < 40% = fase difícil |
| Blunders/partida | `stats.error_stats.averages_per_game.blunder` | > 1.5 = colapso tático frequente |
| Diff Brancas/Pretas | diferença entre `color_stats` | > 10pp = desequilíbrio significativo |
| Comprimento médio | `stats.play_style.avg_game_length` | > 35 lances = posicional; < 35 = agressivo/tático |

---

## Referência de Qualidade

Ver `exemplo-report/Análise Profunda do Jogo de Carlsen.pdf` para o padrão de profundidade narrativa almejado. Aspectos-chave:
- Cada afirmação técnica é fundamentada em dados ou padrões observáveis
- O perfil psicológico conecta-se diretamente aos padrões estatísticos
- Os planos de ação são específicos e graduados por prioridade
- A perspectiva do adversário é um protocolo de batalha, não apenas uma lista de fraquezas
