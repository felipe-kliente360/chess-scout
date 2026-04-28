# Chess Scout

## Fluxo de trabalho Git

**Sempre commitar e fazer push direto em `main`.** Este é um protótipo sem risco — não usar feature branches. Todo commit e deploy vai direto para main.

Ferramenta de análise de jogadores do Chess.com que gera dois relatórios: diagnóstico do jogador e guia de como vencê-lo.

## Como rodar

### Interface web (Streamlit)
```bash
streamlit run app.py
```

### CLI
```bash
python main.py {username}
# Exemplo:
python main.py magnuscarlsen
```

## Outputs

Os relatórios são salvos em:
```
outputs/{username}/DIAGNOSTICO.md
outputs/{username}/GUIA_ADVERSARIO.md
```

## Instalação

```bash
pip install -r requirements.txt
```

## Stockfish

O Stockfish deve ser instalado **separadamente** no sistema operacional:

- **Mac**: `brew install stockfish`
- **Linux**: `sudo apt install stockfish`
- **Windows**: Baixar em https://stockfishchess.org/download/

O módulo `analyzer.py` detecta automaticamente o path do Stockfish no sistema.

## Estrutura

```
chess-scout/
├── app.py              # Interface Streamlit (lógica de app + wizard + resultados)
├── main.py             # Entry point CLI
├── modules/
│   ├── ui.py           # Design system: DOSSIE, build_css, SVG/render helpers
│   ├── fetcher.py      # Busca partidas na API do Chess.com
│   ├── analyzer.py     # Analisa partidas com python-chess + Stockfish
│   ├── stats.py        # Calcula estatísticas e padrões (inclui ACPL)
│   └── reporter.py     # Gera os relatórios em markdown (Claude API + fallback)
├── exemplo-report/     # Referência de qualidade: análise profunda de Magnus Carlsen
└── outputs/            # Relatórios gerados
```

## Qualidade dos Relatórios

Os relatórios devem ter profundidade similar à análise profissional de grandes mestres disponível em `exemplo-report/`. Consulte esse documento como referência de estilo e profundidade ao modificar `modules/reporter.py`.

Características-chave do padrão de qualidade almejado:
- Prosa analítica fluida (não apenas tabelas e bullet points)
- Análise por fase do jogo (abertura / meio de jogo / final)
- Perfil psicológico baseado nos padrões de erros
- Planos acionáveis com prioridades claras
- ACPL (Average Centipawn Loss) como métrica central de qualidade
- Perspectiva dupla: diagnóstico do jogador + guia para vencê-lo

### Claude API (geração narrativa)

`reporter.py` usa o modelo `claude-opus-4-7` quando `ANTHROPIC_API_KEY` está definida. Sem a chave, cai automaticamente para templates estáticos com a mesma estrutura. O prompt do sistema usa `cache_control: ephemeral` para reduzir custo em chamadas repetidas.

Ver `REFERENCE.md` para a estrutura completa dos relatórios.
