# Chess Scout

Analise qualquer jogador do Chess.com e descubra seus pontos fortes, fracos e como vencê-lo.

## Funcionalidades

- Busca as últimas 100 partidas de qualquer jogador via API pública do Chess.com
- Analisa cada partida com python-chess + Stockfish (depth 15)
- Classifica movimentos em: excelente / boa / imprecisão / erro / blunder
- Gera dois relatórios completos:
  - **DIAGNÓSTICO**: análise detalhada do jogador com plano de estudo
  - **GUIA DO ADVERSÁRIO**: como se preparar e vencer esse jogador

## Instalação

```bash
# Instalar Stockfish (necessário para análise)
# Mac:
brew install stockfish
# Linux:
sudo apt install stockfish

# Instalar dependências Python
pip install -r requirements.txt
```

## Uso

### Interface web
```bash
streamlit run app.py
```

### Linha de comando
```bash
python main.py magnuscarlsen
```

## Tecnologias

- `python-chess` — parsing e análise de PGN
- `stockfish` — engine de análise
- `streamlit` — interface web
- `plotly` — gráficos interativos
- `pandas` — manipulação de dados
- `requests` — chamadas à API do Chess.com
