# Chess Scout

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
├── app.py              # Interface Streamlit
├── main.py             # Entry point CLI
├── modules/
│   ├── fetcher.py      # Busca partidas na API do Chess.com
│   ├── analyzer.py     # Analisa partidas com python-chess + Stockfish
│   ├── stats.py        # Calcula estatísticas e padrões
│   └── reporter.py     # Gera os relatórios em markdown
└── outputs/            # Relatórios gerados
```
