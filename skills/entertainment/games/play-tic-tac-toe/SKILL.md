---
name: play-tic-tac-toe
description: Play, resume, inspect, or clear a terminal tic-tac-toe game with persistent user-scoped state and deterministic aggressive or defensive AI. Use when a user asks to play tic-tac-toe, supplies a board position, makes a numbered move, or wants to resume a saved match.
---

# Play Tic Tac Toe

Use `bin/play-tic-tac-toe` for every game operation. Read [references/commands.md](references/commands.md) when translating natural-language settings or troubleshooting saved state.

## Workflow

1. Start a game with the requested marker, first player, and strategy.
2. Relay the board and available numbered cells.
3. For each user move, run `move <1-9>` and relay the updated board.
4. Use `show` to resume and `clear` only when the user asks to discard the saved match.

Never edit the state file manually during normal play. Set `TICTACTOE_STATE_FILE` only when an isolated state location is needed.

