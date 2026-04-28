import os
import shutil
import chess
import chess.pgn
import io
from typing import Optional
from stockfish import Stockfish


MOVE_CLASSIFICATIONS = {
    "excellent": (0, 20),
    "good": (20, 50),
    "inaccuracy": (50, 100),
    "mistake": (100, 200),
    "blunder": (200, 10000),
}

DEPTH = 15


def _find_stockfish_path() -> str:
    candidates = [
        shutil.which("stockfish"),
        "/usr/bin/stockfish",
        "/usr/local/bin/stockfish",
        "/opt/homebrew/bin/stockfish",
        "/usr/games/stockfish",
    ]
    for path in candidates:
        if path and os.path.isfile(path):
            return path
    raise FileNotFoundError(
        "Stockfish não encontrado. Instale com:\n"
        "  Mac: brew install stockfish\n"
        "  Linux: sudo apt install stockfish"
    )


def _classify_move(centipawn_loss: int) -> str:
    for label, (lo, hi) in MOVE_CLASSIFICATIONS.items():
        if lo <= centipawn_loss < hi:
            return label
    return "blunder"


def _get_game_phase(move_number: int) -> str:
    if move_number <= 15:
        return "opening"
    if move_number <= 35:
        return "middlegame"
    return "endgame"


def _extract_cp(evaluation: dict, perspective_white: bool) -> Optional[int]:
    if not evaluation:
        return None
    etype = evaluation.get("type")
    value = evaluation.get("value", 0)
    if etype == "cp":
        return value if perspective_white else -value
    if etype == "mate":
        mate_val = 10000 if value > 0 else -10000
        return mate_val if perspective_white else -mate_val
    return None


def _analyze_game(pgn_str: str, username: str, sf: Stockfish) -> dict:
    game = chess.pgn.read_game(io.StringIO(pgn_str))
    if game is None:
        return {}

    board = game.board()
    moves_analysis = []

    for node in game.mainline():
        move = node.move
        move_number = board.fullmove_number
        is_white_turn = board.turn == chess.WHITE

        sf.set_fen_position(board.fen())
        eval_before = sf.get_evaluation()

        board.push(move)

        sf.set_fen_position(board.fen())
        eval_after = sf.get_evaluation()

        score_before = _extract_cp(eval_before, is_white_turn)
        score_after = _extract_cp(eval_after, is_white_turn)

        if score_before is not None and score_after is not None:
            loss = max(0, score_before - score_after)
            classification = _classify_move(loss)
        else:
            loss = 0
            classification = "good"

        moves_analysis.append({
            "move_number": move_number,
            "move": move.uci(),
            "is_white": is_white_turn,
            "classification": classification,
            "cp_loss": loss,
            "phase": _get_game_phase(move_number),
        })

    white_name = game.headers.get("White", "").lower()
    is_player_white = white_name == username.lower()

    player_moves = [m for m in moves_analysis if m["is_white"] == is_player_white]

    counts = {k: 0 for k in MOVE_CLASSIFICATIONS}
    for m in player_moves:
        counts[m["classification"]] += 1

    blunders_by_phase = {"opening": 0, "middlegame": 0, "endgame": 0}
    for m in player_moves:
        if m["classification"] == "blunder":
            blunders_by_phase[m["phase"]] += 1

    return {
        "move_counts": counts,
        "blunders_by_phase": blunders_by_phase,
        "total_moves": len(player_moves),
        "moves_detail": player_moves,
    }


def analyze_games(
    games: list[dict],
    username: str,
    progress_callback=None,
) -> list[dict]:
    stockfish_path = _find_stockfish_path()
    sf = Stockfish(path=stockfish_path, depth=DEPTH, parameters={"Threads": 1, "Hash": 64})

    results = []
    for i, game in enumerate(games):
        try:
            analysis = _analyze_game(game["pgn"], username, sf)
            results.append({**game, "analysis": analysis})
        except Exception:
            results.append({**game, "analysis": {}})

        if progress_callback:
            progress_callback(i + 1, len(games))

    return results
