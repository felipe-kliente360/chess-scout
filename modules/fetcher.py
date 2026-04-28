import json
import requests
import time
from datetime import datetime, date
from typing import Optional


HEADERS = {"User-Agent": "chess-scout/1.0 (github.com/chess-scout)"}
CHESSCOM_BASE = "https://api.chess.com/pub/player"
LICHESS_BASE  = "https://lichess.org/api"

# category name → Chess.com time_class values
CHESSCOM_CATEGORY: dict[str, set[str]] = {
    "bullet":    {"bullet"},
    "blitz":     {"blitz"},
    "rapid":     {"rapid"},
    "classical": {"daily"},
}

# category name → Lichess perfType string (API accepts comma-separated)
LICHESS_CATEGORY: dict[str, str] = {
    "bullet":    "bullet,ultraBullet",
    "blitz":     "blitz",
    "rapid":     "rapid",
    "classical": "classical,correspondence",
}


# ── Chess.com ──────────────────────────────────────────────────────────────────

def _chesscom_profile(username: str) -> dict:
    url = f"{CHESSCOM_BASE}/{username.lower()}"
    resp = requests.get(url, headers=HEADERS, timeout=10)
    if resp.status_code == 404:
        raise ValueError(f"Jogador '{username}' não encontrado no Chess.com")
    if resp.status_code == 403:
        deny = resp.headers.get("x-deny-reason", "")
        if deny == "host_not_allowed":
            raise ValueError(
                "A API do Chess.com bloqueou esta requisição (IP de servidor/datacenter "
                "não permitido). Execute o Chess Scout localmente para obter os dados."
            )
        raise ValueError(f"Acesso negado pela API do Chess.com (403): {deny}")
    resp.raise_for_status()
    data = resp.json()
    data["platform"] = "chesscom"
    return data


def _chesscom_month(username: str, year: int, month: int) -> list[dict]:
    url = f"{CHESSCOM_BASE}/{username.lower()}/games/{year}/{month:02d}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        if resp.status_code == 404:
            return []
        if resp.status_code == 429:
            time.sleep(5)
            resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        return resp.json().get("games", [])
    except requests.RequestException:
        return []


def _parse_chesscom(game: dict, username: str) -> Optional[dict]:
    pgn = game.get("pgn", "")
    if not pgn:
        return None

    white = game.get("white", {})
    black = game.get("black", {})
    is_white = white.get("username", "").lower() == username.lower()
    player   = white if is_white else black
    opponent = black if is_white else white

    result_raw = player.get("result", "")
    if result_raw == "win":
        result = "win"
    elif result_raw in ("checkmated", "timeout", "resigned", "lose", "abandoned"):
        result = "loss"
    else:
        result = "draw"

    opening = eco = ""
    for line in pgn.split("\n"):
        if line.startswith("[ECOUrl"):
            opening = line.split('"')[1].rstrip('"]').split("/")[-1].replace("-", " ").title()
        elif line.startswith("[ECO "):
            eco = line.split('"')[1]

    end_time = game.get("end_time", 0)
    return {
        "pgn":               pgn,
        "result":            result,
        "time_class":        game.get("time_class", "unknown"),
        "time_control":      game.get("time_control", ""),
        "player_rating":     player.get("rating"),
        "opponent_rating":   opponent.get("rating"),
        "opponent_username": opponent.get("username", ""),
        "is_white":          is_white,
        "opening":           opening,
        "eco":               eco,
        "date":              date.fromtimestamp(end_time).isoformat() if end_time else "",
        "url":               game.get("url", ""),
    }


def _fetch_chesscom(
    username: str,
    target: int = 100,
    time_class_filter: Optional[list[str]] = None,
    progress_callback=None,
) -> tuple[dict, list[dict]]:
    profile = _chesscom_profile(username)
    now = datetime.utcnow()
    year, month = now.year, now.month
    games: list[dict] = []

    allowed: set[str] = set()
    if time_class_filter:
        for cat in time_class_filter:
            allowed.update(CHESSCOM_CATEGORY.get(cat, {cat}))

    for _ in range(24):
        if len(games) >= target:
            break
        for g in reversed(_chesscom_month(username, year, month)):
            if allowed and g.get("time_class") not in allowed:
                continue
            parsed = _parse_chesscom(g, username)
            if parsed:
                games.append(parsed)
                if len(games) >= target:
                    break
        if progress_callback:
            progress_callback(len(games), target)
        month -= 1
        if month == 0:
            month, year = 12, year - 1

    return profile, games[:target]


# ── Lichess ────────────────────────────────────────────────────────────────────

def _lichess_profile(username: str) -> dict:
    url = f"{LICHESS_BASE}/user/{username.lower()}"
    resp = requests.get(url, headers=HEADERS, timeout=10)
    if resp.status_code == 404:
        raise ValueError(f"Jogador '{username}' não encontrado no Lichess")
    if resp.status_code == 403:
        deny = resp.headers.get("x-deny-reason", "")
        if deny == "host_not_allowed":
            raise ValueError(
                "A API do Lichess bloqueou esta requisição (IP de servidor/datacenter não permitido). "
                "Execute o Chess Scout localmente na sua máquina para obter os dados."
            )
        raise ValueError(f"Acesso negado pela API do Lichess (403): {deny}")
    resp.raise_for_status()
    data = resp.json()
    return {
        "username": data.get("username", username),
        "avatar":   None,
        "country":  data.get("profile", {}).get("country", ""),
        "status":   "closed" if data.get("disabled") else "active",
        "platform": "lichess",
        "url":      f"https://lichess.org/@/{data.get('username', username)}",
    }


def _build_lichess_pgn(game: dict, white_name: str, black_name: str) -> str:
    winner = game.get("winner")
    if winner == "white":
        result = "1-0"
    elif winner == "black":
        result = "0-1"
    else:
        result = "1/2-1/2"

    opening = game.get("opening", {})
    created_at = game.get("createdAt", 0)
    date_str = date.fromtimestamp(created_at / 1000).strftime("%Y.%m.%d") if created_at else "????.??.??"

    hdr = "\n".join([
        f'[Event "Lichess {game.get("speed", "?").capitalize()}"]',
        f'[Site "https://lichess.org/{game.get("id", "")}"]',
        f'[Date "{date_str}"]',
        f'[White "{white_name}"]',
        f'[Black "{black_name}"]',
        f'[Result "{result}"]',
        f'[ECO "{opening.get("eco", "?")}"]',
        f'[Opening "{opening.get("name", "?")}"]',
    ])

    moves = game.get("moves", "").split()
    numbered = []
    for i, mv in enumerate(moves):
        if i % 2 == 0:
            numbered.append(f"{i // 2 + 1}. {mv}")
        else:
            numbered.append(mv)

    return hdr + "\n\n" + " ".join(numbered) + f" {result}"


def _parse_lichess(game: dict, username: str) -> Optional[dict]:
    players = game.get("players", {})
    white_p  = players.get("white", {})
    black_p  = players.get("black", {})
    white_user = white_p.get("user", {})
    black_user = black_p.get("user", {})
    white_name = white_user.get("name", white_user.get("id", "?"))
    black_name = black_user.get("name", black_user.get("id", "?"))

    is_white = white_name.lower() == username.lower()
    player   = white_p if is_white else black_p
    opponent = black_p if is_white else white_p
    opp_user = opponent.get("user", {})

    winner = game.get("winner")
    if winner is None:
        result = "draw"
    elif (winner == "white") == is_white:
        result = "win"
    else:
        result = "loss"

    opening = game.get("opening", {})
    clock   = game.get("clock", {})
    tc_str  = f"{clock.get('initial', 0) // 60}+{clock.get('increment', 0)}" if clock else ""
    created = game.get("createdAt", 0)

    return {
        "pgn":               _build_lichess_pgn(game, white_name, black_name),
        "result":            result,
        "time_class":        game.get("speed", "unknown"),
        "time_control":      tc_str,
        "player_rating":     player.get("rating"),
        "opponent_rating":   opponent.get("rating"),
        "opponent_username": opp_user.get("name", opp_user.get("id", "")),
        "is_white":          is_white,
        "opening":           opening.get("name", ""),
        "eco":               opening.get("eco", ""),
        "date":              date.fromtimestamp(created / 1000).isoformat() if created else "",
        "url":               f"https://lichess.org/{game.get('id', '')}",
    }


def _fetch_lichess(
    username: str,
    target: int = 100,
    time_class_filter: Optional[list[str]] = None,
    progress_callback=None,
) -> tuple[dict, list[dict]]:
    profile = _lichess_profile(username)

    params: dict = {"max": target, "opening": "true", "clocks": "true"}
    if time_class_filter:
        perf_parts: list[str] = []
        for cat in time_class_filter:
            perf_parts.append(LICHESS_CATEGORY.get(cat, cat))
        params["perfType"] = ",".join(perf_parts)

    req_headers = {**HEADERS, "Accept": "application/x-ndjson"}
    try:
        resp = requests.get(
            f"{LICHESS_BASE}/games/user/{username.lower()}",
            headers=req_headers,
            params=params,
            timeout=30,
            stream=True,
        )
        if resp.status_code == 404:
            raise ValueError(f"Jogador '{username}' não encontrado no Lichess")
        resp.raise_for_status()
    except requests.RequestException as e:
        raise ValueError(f"Erro ao buscar partidas do Lichess: {e}")

    games: list[dict] = []
    for raw_line in resp.iter_lines():
        if not raw_line:
            continue
        try:
            game_data = json.loads(raw_line)
        except (json.JSONDecodeError, ValueError):
            continue

        parsed = _parse_lichess(game_data, username)
        if parsed:
            games.append(parsed)

        if progress_callback:
            progress_callback(len(games), target)

        if len(games) >= target:
            break

    return profile, games


# ── Unified entry point ────────────────────────────────────────────────────────

def fetch_games(
    username: str,
    target: int = 100,
    time_class_filter: Optional[list[str]] = None,
    platform: str = "lichess",
    progress_callback=None,
) -> tuple[dict, list[dict]]:
    if platform == "lichess":
        return _fetch_lichess(username, target, time_class_filter, progress_callback)
    return _fetch_chesscom(username, target, time_class_filter, progress_callback)
