import requests
import time
from datetime import datetime, date
from typing import Optional


HEADERS = {"User-Agent": "chess-scout/1.0 (github.com/chess-scout)"}
BASE_URL = "https://api.chess.com/pub/player"


def get_player_profile(username: str) -> dict:
    url = f"{BASE_URL}/{username.lower()}"
    resp = requests.get(url, headers=HEADERS, timeout=10)
    if resp.status_code == 404:
        raise ValueError(f"Jogador '{username}' não encontrado no Chess.com")
    if resp.status_code == 403:
        deny = resp.headers.get("x-deny-reason", "")
        if deny == "host_not_allowed":
            raise ValueError(
                "A API do Chess.com bloqueou esta requisição (IP de servidor/datacenter não permitido). "
                "Execute o Chess Scout localmente na sua máquina para obter os dados."
            )
        raise ValueError(f"Acesso negado pela API do Chess.com (403): {deny}")
    resp.raise_for_status()
    return resp.json()


def get_player_stats(username: str) -> dict:
    url = f"{BASE_URL}/{username.lower()}/stats"
    resp = requests.get(url, headers=HEADERS, timeout=10)
    resp.raise_for_status()
    return resp.json()


def _fetch_month_games(username: str, year: int, month: int) -> list[dict]:
    url = f"{BASE_URL}/{username.lower()}/games/{year}/{month:02d}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        if resp.status_code == 404:
            return []
        if resp.status_code == 429:
            time.sleep(5)
            resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        return data.get("games", [])
    except requests.RequestException:
        return []


def _parse_game(game: dict, username: str) -> Optional[dict]:
    pgn = game.get("pgn", "")
    if not pgn:
        return None

    time_class = game.get("time_class", "unknown")
    time_control = game.get("time_control", "")
    end_time = game.get("end_time", 0)
    url = game.get("url", "")

    white = game.get("white", {})
    black = game.get("black", {})

    white_username = white.get("username", "").lower()
    is_white = white_username == username.lower()

    player = white if is_white else black
    opponent = black if is_white else white

    result_raw = player.get("result", "")
    if result_raw == "win":
        result = "win"
    elif result_raw in ("checkmated", "timeout", "resigned", "lose", "abandoned"):
        result = "loss"
    else:
        result = "draw"

    opening = ""
    eco = ""
    for line in pgn.split("\n"):
        if line.startswith("[ECOUrl"):
            eco_url = line.split('"')[1]
            opening = eco_url.rstrip('"]').split("/")[-1].replace("-", " ").title()
        elif line.startswith("[ECO "):
            eco = line.split('"')[1]

    game_date = date.fromtimestamp(end_time).isoformat() if end_time else ""

    return {
        "pgn": pgn,
        "result": result,
        "time_class": time_class,
        "time_control": time_control,
        "player_rating": player.get("rating"),
        "opponent_rating": opponent.get("rating"),
        "opponent_username": opponent.get("username", ""),
        "is_white": is_white,
        "opening": opening,
        "eco": eco,
        "date": game_date,
        "url": url,
    }


def fetch_games(
    username: str,
    target: int = 100,
    time_class_filter: Optional[str] = None,
    progress_callback=None,
) -> tuple[dict, list[dict]]:
    profile = get_player_profile(username)

    now = datetime.utcnow()
    year, month = now.year, now.month

    games = []
    months_checked = 0
    max_months = 24

    while len(games) < target and months_checked < max_months:
        raw_games = _fetch_month_games(username, year, month)

        for g in reversed(raw_games):
            if time_class_filter and g.get("time_class") != time_class_filter:
                continue
            parsed = _parse_game(g, username)
            if parsed:
                games.append(parsed)
                if len(games) >= target:
                    break

        if progress_callback:
            progress_callback(len(games), target)

        month -= 1
        if month == 0:
            month = 12
            year -= 1
        months_checked += 1

    return profile, games[:target]
