#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

from __future__ import annotations

import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import tictactoe_game as game

BLANK = game.EMPTY


class TicTacToeGameTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.state_file = Path(self.temporary_directory.name) / "current_game.json"

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def run_cli(self, *args: str) -> tuple[int, str, str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        argv = ["--state-file", str(self.state_file), *args]
        with redirect_stdout(stdout), redirect_stderr(stderr):
            exit_code = game.main(argv)
        return exit_code, stdout.getvalue(), stderr.getvalue()

    def test_detects_win_and_draw(self) -> None:
        winning_board = ["X", "X", "X", "O", BLANK, "O", BLANK, BLANK, BLANK]
        draw_board = ["X", "O", "X", "X", "O", "O", "O", "X", "X"]

        self.assertEqual(game.find_winner(winning_board), "X")
        self.assertTrue(game.is_draw(draw_board))

    def test_start_show_move_and_clear_flow(self) -> None:
        exit_code, output, error = self.run_cli(
            "start",
            "--player",
            "X",
            "--strategy",
            "defensive",
            "--first",
            "player",
        )
        self.assertEqual(exit_code, 0, error)
        self.assertIn("Game started.", output)
        self.assertIn("Your move", output)

        exit_code, output, error = self.run_cli("move", "1")
        self.assertEqual(exit_code, 0, error)
        self.assertIn("You choose: 1", output)
        self.assertIn("AI chooses:", output)

        exit_code, output, error = self.run_cli("show")
        self.assertEqual(exit_code, 0, error)
        self.assertIn("Moves played: 2", output)

        exit_code, output, error = self.run_cli("clear")
        self.assertEqual(exit_code, 0, error)
        self.assertIn("Cleared saved", output)
        self.assertFalse(self.state_file.exists())

    def test_invalid_move_does_not_change_saved_state(self) -> None:
        self.run_cli("start", "--player", "X", "--strategy", "defensive", "--first", "player")
        before = self.state_file.read_text(encoding="utf-8")

        exit_code, _, error = self.run_cli("move", "10")

        after = self.state_file.read_text(encoding="utf-8")
        self.assertEqual(exit_code, 1)
        self.assertIn("Move must be a number from 1 to 9.", error)
        self.assertEqual(after, before)

    def test_aggressive_ai_takes_immediate_win(self) -> None:
        state = game.GameState(
            board=["O", "O", BLANK, "X", "X", BLANK, BLANK, BLANK, BLANK],
            player_marker="X",
            ai_marker="O",
            current_turn=game.AI_TURN,
            strategy=game.AGGRESSIVE,
        )

        self.assertEqual(game.choose_ai_move(state) + 1, 3)

    def test_defensive_ai_blocks_immediate_player_win(self) -> None:
        state = game.GameState(
            board=["X", "X", BLANK, "O", BLANK, BLANK, BLANK, BLANK, BLANK],
            player_marker="X",
            ai_marker="O",
            current_turn=game.AI_TURN,
            strategy=game.DEFENSIVE,
        )

        self.assertEqual(game.choose_ai_move(state) + 1, 3)

    def test_finished_game_rejects_moves_without_corrupting_state(self) -> None:
        state = game.GameState(
            board=["X", "X", "X", "O", "O", BLANK, BLANK, BLANK, BLANK],
            player_marker="X",
            ai_marker="O",
            current_turn=game.FINISHED_TURN,
            strategy=game.AGGRESSIVE,
            winner="X",
        )
        game.save_state(state, self.state_file)
        before = self.state_file.read_text(encoding="utf-8")

        exit_code, _, error = self.run_cli("move", "6")

        after = self.state_file.read_text(encoding="utf-8")
        self.assertEqual(exit_code, 1)
        self.assertIn("This game is finished.", error)
        self.assertEqual(after, before)

if __name__ == "__main__":
    unittest.main()
