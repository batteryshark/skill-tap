# Commands and state

## Commands

```sh
bin/play-tic-tac-toe start --player X --strategy defensive --first player
bin/play-tic-tac-toe move 5
bin/play-tic-tac-toe show
bin/play-tic-tac-toe clear
```

- `--player`: `X`, `O`, or `random`.
- `--strategy`: `aggressive` prioritizes immediate wins; `defensive` prioritizes blocks and non-losing lines.
- `--first`: `player`, `ai`, or `random`.

## State

The default state file is `${XDG_STATE_HOME:-~/.local/state}/play-tic-tac-toe/current-game.json`. Override it with `TICTACTOE_STATE_FILE` for testing or separate concurrent games.

