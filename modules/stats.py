from collections import defaultdict
from typing import Optional
import pandas as pd


def _win_rate(wins: int, total: int) -> float:
    return round(wins / total * 100, 1) if total > 0 else 0.0


def compute_stats(games: list[dict], username: str) -> dict:
    if not games:
        return {}

    total = len(games)
    wins = sum(1 for g in games if g["result"] == "win")
    losses = sum(1 for g in games if g["result"] == "loss")
    draws = total - wins - losses

    by_time_class: dict[str, dict] = defaultdict(lambda: {"win": 0, "loss": 0, "draw": 0, "total": 0})
    for g in games:
        tc = g.get("time_class", "unknown")
        by_time_class[tc][g["result"]] += 1
        by_time_class[tc]["total"] += 1

    time_class_stats = {}
    for tc, counts in by_time_class.items():
        t = counts["total"]
        time_class_stats[tc] = {
            "wins": counts["win"],
            "losses": counts["loss"],
            "draws": counts["draw"],
            "total": t,
            "win_rate": _win_rate(counts["win"], t),
        }

    opponent_ratings = [g["opponent_rating"] for g in games if g.get("opponent_rating")]
    avg_opponent_rating = round(sum(opponent_ratings) / len(opponent_ratings)) if opponent_ratings else None

    white_games = [g for g in games if g.get("is_white")]
    black_games = [g for g in games if not g.get("is_white")]

    color_stats = {
        "white": {
            "total": len(white_games),
            "wins": sum(1 for g in white_games if g["result"] == "win"),
            "win_rate": _win_rate(sum(1 for g in white_games if g["result"] == "win"), len(white_games)),
        },
        "black": {
            "total": len(black_games),
            "wins": sum(1 for g in black_games if g["result"] == "win"),
            "win_rate": _win_rate(sum(1 for g in black_games if g["result"] == "win"), len(black_games)),
        },
    }

    opening_data: dict[str, dict] = defaultdict(lambda: {"white_wins": 0, "white_total": 0, "black_wins": 0, "black_total": 0})
    for g in games:
        opening = g.get("opening") or "Desconhecida"
        if g.get("is_white"):
            opening_data[opening]["white_total"] += 1
            if g["result"] == "win":
                opening_data[opening]["white_wins"] += 1
        else:
            opening_data[opening]["black_total"] += 1
            if g["result"] == "win":
                opening_data[opening]["black_wins"] += 1

    openings_white = []
    openings_black = []
    for name, d in opening_data.items():
        if d["white_total"] > 0:
            openings_white.append({
                "opening": name,
                "games": d["white_total"],
                "wins": d["white_wins"],
                "win_rate": _win_rate(d["white_wins"], d["white_total"]),
            })
        if d["black_total"] > 0:
            openings_black.append({
                "opening": name,
                "games": d["black_total"],
                "wins": d["black_wins"],
                "win_rate": _win_rate(d["black_wins"], d["black_total"]),
            })

    openings_white.sort(key=lambda x: x["games"], reverse=True)
    openings_black.sort(key=lambda x: x["games"], reverse=True)

    analyzed = [g for g in games if g.get("analysis")]
    error_stats = _compute_error_stats(analyzed)
    play_style = _compute_play_style(analyzed, games)

    player_ratings = [g["player_rating"] for g in games if g.get("player_rating")]
    current_rating = player_ratings[0] if player_ratings else None
    primary_time_class = max(by_time_class, key=lambda k: by_time_class[k]["total"]) if by_time_class else "unknown"

    return {
        "username": username,
        "total_games": total,
        "wins": wins,
        "losses": losses,
        "draws": draws,
        "win_rate": _win_rate(wins, total),
        "current_rating": current_rating,
        "avg_opponent_rating": avg_opponent_rating,
        "primary_time_class": primary_time_class,
        "time_class_stats": time_class_stats,
        "color_stats": color_stats,
        "openings_white": openings_white[:10],
        "openings_black": openings_black[:10],
        "error_stats": error_stats,
        "play_style": play_style,
    }


def _compute_error_stats(analyzed_games: list[dict]) -> dict:
    if not analyzed_games:
        return {}

    totals = defaultdict(int)
    phase_blunders = defaultdict(int)
    total_analyzed = len(analyzed_games)

    for g in analyzed_games:
        analysis = g.get("analysis", {})
        counts = analysis.get("move_counts", {})
        for k, v in counts.items():
            totals[k] += v
        bp = analysis.get("blunders_by_phase", {})
        for phase, count in bp.items():
            phase_blunders[phase] += count

    averages = {k: round(v / total_analyzed, 2) for k, v in totals.items()}

    total_blunders = totals.get("blunder", 0)
    top_errors = []
    if total_blunders:
        top_errors.append({"type": "Blunder", "count": total_blunders, "avg_per_game": averages.get("blunder", 0)})
    mistakes = totals.get("mistake", 0)
    if mistakes:
        top_errors.append({"type": "Erro", "count": mistakes, "avg_per_game": averages.get("mistake", 0)})
    inaccuracies = totals.get("inaccuracy", 0)
    if inaccuracies:
        top_errors.append({"type": "Imprecisão", "count": inaccuracies, "avg_per_game": averages.get("inaccuracy", 0)})

    top_errors.sort(key=lambda x: x["count"], reverse=True)

    return {
        "averages_per_game": averages,
        "totals": dict(totals),
        "blunders_by_phase": dict(phase_blunders),
        "top_errors": top_errors[:5],
        "games_analyzed": total_analyzed,
    }


def _compute_play_style(analyzed_games: list[dict], all_games: list[dict]) -> dict:
    total = len(all_games)
    wins = sum(1 for g in all_games if g["result"] == "win")
    losses = sum(1 for g in all_games if g["result"] == "loss")

    conversion_tendency = "consistente"
    if wins > 0:
        if wins / max(total, 1) > 0.6:
            conversion_tendency = "converte bem posições ganhas"
        elif wins / max(total, 1) < 0.35:
            conversion_tendency = "dificuldade em converter vantagem"

    fighting_tendency = "equilibrado"
    if losses > 0:
        loss_rate = losses / total
        if loss_rate > 0.5:
            fighting_tendency = "tende a desistir rapidamente"
        elif loss_rate < 0.25:
            fighting_tendency = "luta até o fim"

    avg_game_length = 0
    if analyzed_games:
        lengths = [g.get("analysis", {}).get("total_moves", 0) for g in analyzed_games]
        avg_game_length = round(sum(lengths) / len(lengths), 1) if lengths else 0

    style = "posicional" if avg_game_length > 35 else "agressivo"

    return {
        "style": style,
        "avg_game_length": avg_game_length,
        "conversion_tendency": conversion_tendency,
        "fighting_tendency": fighting_tendency,
    }
