import sys
import os
from modules.fetcher import fetch_games
from modules.analyzer import analyze_games
from modules.stats import compute_stats
from modules.reporter import generate_diagnostic, generate_opponent_guide, save_reports


def print_step(step: str):
    print(f"\n{'='*50}")
    print(f"  {step}")
    print(f"{'='*50}")


def main():
    if len(sys.argv) < 2:
        print("Uso: python main.py <username>")
        print("Exemplo: python main.py magnuscarlsen")
        sys.exit(1)

    username = sys.argv[1]
    time_class = sys.argv[2] if len(sys.argv) > 2 else None

    print(f"\nChess Scout — Analisando: {username}")
    if time_class:
        print(f"Modalidade: {time_class}")

    print_step("1/4 Buscando partidas...")

    def fetch_progress(found, target):
        print(f"  Partidas encontradas: {found}/{target}", end="\r")

    try:
        profile, games = fetch_games(username, target=100, time_class_filter=time_class, progress_callback=fetch_progress)
    except ValueError as e:
        print(f"\nErro: {e}")
        sys.exit(1)

    print(f"\n  Total de partidas obtidas: {len(games)}")

    if not games:
        print("Nenhuma partida encontrada. Verifique o username e tente novamente.")
        sys.exit(1)

    print_step("2/4 Analisando com Stockfish...")

    try:
        def analysis_progress(done, total):
            print(f"  Analisando partida {done}/{total}...", end="\r")

        analyzed_games = analyze_games(games, username, progress_callback=analysis_progress)
        print(f"\n  {len(analyzed_games)} partidas analisadas com Stockfish")
    except FileNotFoundError as e:
        print(f"\nAviso: {e}")
        print("Prosseguindo sem análise Stockfish (apenas estatísticas básicas)...")
        analyzed_games = games

    print_step("3/4 Calculando estatísticas...")
    stats = compute_stats(analyzed_games, username)
    print(f"  Taxa de vitória: {stats.get('win_rate', 0):.1f}%")
    print(f"  Rating atual: {stats.get('current_rating', 'N/A')}")

    print_step("4/4 Gerando relatórios...")
    diagnostic = generate_diagnostic(stats, username)
    opponent_guide = generate_opponent_guide(stats, username)

    diag_path, guide_path = save_reports(username, diagnostic, opponent_guide)

    print(f"\n  Relatórios salvos em:")
    print(f"  DIAGNOSTICO:      {diag_path}")
    print(f"  GUIA ADVERSARIO:  {guide_path}")

    print("\n" + "="*50)
    print("  Análise concluída!")
    print("="*50 + "\n")


if __name__ == "__main__":
    main()
