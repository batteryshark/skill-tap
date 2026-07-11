# Core gameplay baseline

## Field and generation

- `R-ENG-01`: visible field is 10 columns by 20 rows.
- `R-ENG-02`: engine represents a 20-row buffer above the visible field.
- `R-ENG-03`: generator uses shuffled seven-piece bags, each containing one of every piece and refilling only after exhaustion.
- `R-ENG-04`: pieces spawn in their north-facing orientation at consistent centered positions.
- `R-ENG-05`: ordered next queue, hold enabled by default, no repeated hold before a lock, and visible landing projection enabled by default.
- `R-ENG-06`: a newly generated piece attempts the baseline initial downward step when unobstructed.

## Controls and lock-down

- `R-CTL-01`: horizontal movement is cell-discrete and collision checked.
- `R-CTL-02`: held horizontal input has a repeat delay near 0.3 seconds and predictable traversal speed.
- `R-CTL-03`: rotation uses an explicit kick system that behaves consistently near walls and floors.
- `R-CTL-04`: landed pieces use a 0.5-second lock timer; extended placement is the default, with at most 15 move/rotation resets before a new lowest row resets the counter. If infinite or classic modes exist, test them separately.
- `R-CTL-05`: soft drop is approximately 20 times normal fall and hard drop locks immediately.

## Scoring and spins

- `R-SCR-01`: single, double, triple, and four-line clear awards scale by level at 100, 300, 500, and 800 times level.
- `R-SCR-02`: soft and hard drop award 1 and 2 points per descended row.
- `R-SCR-03`: full and mini T rotations are recognized separately and map to distinct score events.
- `R-SCR-04`: difficult clears form a back-to-back chain and receive a 50% action bonus; ordinary one-, two-, or three-line clears break it.
- `R-SCR-05`: no-clear rotations neither start nor break a back-to-back chain.

Historical spin awards, multiplied by level: mini/no-clear 100, mini single 200, full/no-clear 400, full single 800, full double 1200, and full triple 1600.

## Game over and solo modes

- `R-GOV-01`: blocked spawn is detected.
- `R-GOV-02`: a piece locking entirely above the visible skyline is detected.
- `R-GOV-03`: overflow beyond the represented buffer has an explicit outcome.
- `R-GOV-04`: implemented marathon, sprint, or timed modes have explicit and tested completion rules.

## Timing note

A commonly used level fall interval is `(0.8 - ((level - 1) * 0.007)) ** (level - 1)` seconds per row. Treat timing tolerances as platform-sensitive and verify them at runtime.

