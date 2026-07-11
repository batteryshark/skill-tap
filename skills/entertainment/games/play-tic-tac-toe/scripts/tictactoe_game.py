# /// script\n# requires-python = ">=3.11"\n# dependencies = []\n# ///\n\nfrom __future__ import annotations

import argparse
import json
import os
import random
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

EMPTY = " "
PLAYER_TURN = "player"
AI_TURN = "ai"
FINISHED_TURN = "finished"
AGGRESSIVE = "aggressive"
DEFENSIVE = "defensive"
MARKERS = ("X", "O")
STRATEGIES = (AGGRESSIVE, DEFENSIVE)
FIRST_PLAYERS = (PLAYER_TURN, AI_TURN, "random")
MOVE_ORDER = (4, 0, 2, 6, 8, 1, 3, 5, 7)
WIN_CONDITIONS = (
    (0, 1, 2),
    (3, 4, 5),
    (6, 7, 8),
    (0, 3, 6),
    (1, 4, 7),
    (2, 5, 8),
    (0, 4, 8),
    (2, 4, 6),
)

SKILL_DIR = Path(__file__).resolve().parents[1]
DEFAULT_STATE_FILE = SKILL_DIR / ".state" / "current_game.json"
STATE_FILE_ENV_VAR = "TICTACTOE_STATE_FILE"


class GameError(ValueError):
    pass


@dataclass
class GameState:
    board: list[str]
    player_marker: str
    ai_marker: str
    current_turn: str
    strategy: str
    winner: str | None = None
    draw: bool = False
    move_history: list[dict[str, Any]] = field(default_factory=list)

    @classmethod
    def new(cls, player_choice: str, strategy: str, first: str) -> "GameState":
        player_marker = choose_marker(player_choice)
        current_turn = choose_first_turn(first)
        return cls(
            board=[EMPTY] * 9,
            player_marker=player_marker,
            ai_marker=opposite_marker(player_marker),
            current_turn=current_turn,
            strategy=strategy,
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "GameState":
        state = cls(
            board=list(data["board"]),
            player_marker=data["player_marker"],
            ai_marker=data["ai_marker"],
            current_turn=data["current_turn"],
            strategy=data["strategy"],
            winner=data.get("winner"),
            draw=bool(data.get("draw", False)),
            move_history=list(data.get("move_history", [])),
        )
        validate_state(state)
        return state

    def is_finished(self) -> bool:
        return self.winner is not None or self.draw


def choose_marker(player_choice: str) -> str:
    if player_choice == "random":
        return random.choice(MARKERS)
    return player_choice


def choose_first_turn(first: str) -> str:
    if first == "random":
        return random.choice((PLAYER_TURN, AI_TURN))
    return first


def opposite_marker(marker: str) -> str:
    return "O" if marker == "X" else "X"


def default_state_file() -> Path:
    configured_path = os.environ.get(STATE_FILE_ENV_VAR)
    if configured_path:
        return Path(configured_path)
    return DEFAULT_STATE_FILE


def validate_state(state: GameState) -> None:
    if len(state.board) != 9:
        raise GameError("Saved board must contain 9 cells.")
    if any(cell not in (EMPTY, "X", "O") for cell in state.board):
        raise GameError("Saved board contains an invalid marker.")
    if state.player_marker not in MARKERS or state.ai_marker not in MARKERS:
        raise GameError("Saved marker assignment is invalid.")
    if state.player_marker == state.ai_marker:
        raise GameError("Player and AI markers must differ.")
    if state.current_turn not in (PLAYER_TURN, AI_TURN, FINISHED_TURN):
        raise GameError("Saved turn is invalid.")
    if state.strategy not in STRATEGIES:
        raise GameError("Saved strategy is invalid.")


def load_state(state_file: Path) -> GameState:
    if not state_file.exists():
        raise GameError("No saved game. Start one with: start")
    try:
        with state_file.open("r", encoding="utf-8") as saved_game:
            data = json.load(saved_game)
        return GameState.from_dict(data)
    except (json.JSONDecodeError, KeyError, TypeError) as error:
        raise GameError(f"Saved game is unreadable: {error}") from error


def save_state(state: GameState, state_file: Path) -> None:
    validate_state(state)
    state_file.parent.mkdir(parents=True, exist_ok=True)
    temporary_file = state_file.with_suffix(f"{state_file.suffix}.tmp")
    with temporary_file.open("w", encoding="utf-8") as saved_game:
        json.dump(asdict(state), saved_game, indent=2)
        saved_game.write("\n")
    temporary_file.replace(state_file)


def available_moves(board: list[str]) -> list[int]:
    open_cells = set(index for index, cell in enumerate(board) if cell == EMPTY)
    return [index for index in MOVE_ORDER if index in open_cells]


def open_positions(board: list[str]) -> list[int]:
    return [index for index, cell in enumerate(board) if cell == EMPTY]


def find_winner(board: list[str]) -> str | None:
    for first, second, third in WIN_CONDITIONS:
        marker = board[first]
        if marker != EMPTY and marker == board[second] == board[third]:
            return marker
    return None


def is_draw(board: list[str]) -> bool:
    return find_winner(board) is None and all(cell != EMPTY for cell in board)


def refresh_result(state: GameState) -> None:
    state.winner = find_winner(state.board)
    state.draw = state.winner is None and is_draw(state.board)
    if state.is_finished():
        state.current_turn = FINISHED_TURN


def find_immediate_win(board: list[str], marker: str) -> int | None:
    for move in available_moves(board):
        candidate = board.copy()
        candidate[move] = marker
        if find_winner(candidate) == marker:
            return move
    return None


def choose_ai_move(state: GameState) -> int:
    player_threat = find_immediate_win(state.board, state.player_marker)
    ai_win = find_immediate_win(state.board, state.ai_marker)

    if state.strategy == DEFENSIVE:
        if player_threat is not None:
            return player_threat
        if ai_win is not None:
            return ai_win
        return choose_defensive_move(state)

    if ai_win is not None:
        return ai_win
    if player_threat is not None:
        return player_threat
    return choose_aggressive_move(state)


def choose_aggressive_move(state: GameState) -> int:
    scored_moves = score_moves(state)
    best_score = max(score for _, score in scored_moves)
    return next(move for move, score in scored_moves if score == best_score)


def choose_defensive_move(state: GameState) -> int:
    scored_moves = score_moves(state)
    drawing_moves = [move for move, score in scored_moves if score == 0]
    if drawing_moves:
        return drawing_moves[0]

    winning_moves = [move for move, score in scored_moves if score > 0]
    if winning_moves:
        return winning_moves[0]

    best_score = max(score for _, score in scored_moves)
    return next(move for move, score in scored_moves if score == best_score)


def score_moves(state: GameState) -> list[tuple[int, int]]:
    scored_moves: list[tuple[int, int]] = []
    for move in available_moves(state.board):
        candidate = state.board.copy()
        candidate[move] = state.ai_marker
        score = minimax(candidate, state.ai_marker, state.player_marker, False, 1)
        scored_moves.append((move, score))
    return scored_moves


def minimax(
    board: list[str],
    ai_marker: str,
    player_marker: str,
    is_ai_turn: bool,
    depth: int,
) -> int:
    winner = find_winner(board)
    if winner == ai_marker:
        return 10 - depth
    if winner == player_marker:
        return depth - 10
    if all(cell != EMPTY for cell in board):
        return 0

    marker = ai_marker if is_ai_turn else player_marker
    scores = []
    for move in available_moves(board):
        candidate = board.copy()
        candidate[move] = marker
        scores.append(minimax(candidate, ai_marker, player_marker, not is_ai_turn, depth + 1))
    return max(scores) if is_ai_turn else min(scores)


def place_move(state: GameState, actor: str, position: int) -> None:
    marker = marker_for_actor(state, actor)
    state.board[position] = marker
    state.move_history.append(
        {
            "actor": actor,
            "marker": marker,
            "position": position + 1,
        }
    )
    refresh_result(state)


def marker_for_actor(state: GameState, actor: str) -> str:
    if actor == PLAYER_TURN:
        return state.player_marker
    if actor == AI_TURN:
        return state.ai_marker
    raise GameError(f"Unknown actor: {actor}")


def play_ai_turn(state: GameState, messages: list[str]) -> None:
    if state.current_turn != AI_TURN or state.is_finished():
        return
    position = choose_ai_move(state)
    place_move(state, AI_TURN, position)
    messages.append(f"AI chooses: {position + 1}")
    if not state.is_finished():
        state.current_turn = PLAYER_TURN


def validate_player_move(state: GameState, position: int) -> int:
    if state.is_finished():
        raise GameError("This game is finished. Run clear or start to play again.")
    if state.current_turn != PLAYER_TURN:
        raise GameError("It is not the player's turn.")
    if position < 1 or position > 9:
        raise GameError("Move must be a number from 1 to 9.")

    index = position - 1
    if state.board[index] != EMPTY:
        raise GameError(f"Space {position} is already filled.")
    return index


def render_board(board: list[str]) -> str:
    rows = []
    for start in range(0, 9, 3):
        row = [
            board[index] if board[index] != EMPTY else str(index + 1)
            for index in range(start, start + 3)
        ]
        rows.append(" | ".join(row))
    return "\n---------\n".join(rows)


def owner_for_marker(state: GameState, marker: str) -> str:
    if marker == state.player_marker:
        return "you"
    return "AI"


def status_line(state: GameState) -> str:
    if state.winner is not None:
        return f"Game over: {state.winner} wins ({owner_for_marker(state, state.winner)})."
    if state.draw:
        return "Game over: draw."
    if state.current_turn == PLAYER_TURN:
        choices = ", ".join(str(move + 1) for move in open_positions(state.board))
        return f"Your move: choose one of {choices}."
    return "AI turn is pending."


def render_state(state: GameState, messages: list[str] | None = None) -> str:
    output = list(messages or [])
    output.extend(
        [
            f"You are {state.player_marker}. AI is {state.ai_marker}. Strategy: {state.strategy}.",
            f"Moves played: {len(state.move_history)}",
            "",
            render_board(state.board),
            "",
            status_line(state),
        ]
    )
    return "\n".join(output)


def start_game(args: argparse.Namespace) -> int:
    state = GameState.new(args.player, args.strategy, args.first)
    messages = ["Game started."]
    play_ai_turn(state, messages)
    save_state(state, args.state_file)
    print(render_state(state, messages))
    return 0


def show_game(args: argparse.Namespace) -> int:
    if not args.state_file.exists():
        print("No saved game. Start one with: start")
        return 0
    state = load_state(args.state_file)
    print(render_state(state))
    return 0


def clear_game(args: argparse.Namespace) -> int:
    if args.state_file.exists():
        args.state_file.unlink()
        print("Cleared saved tic-tac-toe game.")
    else:
        print("No saved game to clear.")
    return 0


def make_player_move(args: argparse.Namespace) -> int:
    state = load_state(args.state_file)
    position = validate_player_move(state, args.position)
    messages = [f"You choose: {args.position}"]
    place_move(state, PLAYER_TURN, position)

    if not state.is_finished():
        state.current_turn = AI_TURN
        play_ai_turn(state, messages)

    save_state(state, args.state_file)
    print(render_state(state, messages))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Play a resumable terminal tic-tac-toe game.")
    parser.add_argument(
        "--state-file",
        type=Path,
        default=default_state_file(),
        help=argparse.SUPPRESS,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    start_parser = subparsers.add_parser("start", help="Start a new game.")
    start_parser.add_argument("--player", choices=("X", "O", "random"), default="random")
    start_parser.add_argument("--strategy", choices=STRATEGIES, default=DEFENSIVE)
    start_parser.add_argument("--first", choices=FIRST_PLAYERS, default="random")
    start_parser.set_defaults(handler=start_game)

    move_parser = subparsers.add_parser("move", help="Make a player move from 1 to 9.")
    move_parser.add_argument("position", type=int)
    move_parser.set_defaults(handler=make_player_move)

    show_parser = subparsers.add_parser("show", help="Show the saved game.")
    show_parser.set_defaults(handler=show_game)

    clear_parser = subparsers.add_parser("clear", help="Clear the saved game.")
    clear_parser.set_defaults(handler=clear_game)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.handler(args)
    except GameError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

