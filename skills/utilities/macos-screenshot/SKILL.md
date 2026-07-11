---
name: macos-screenshot
description: Check macOS screen-recording readiness and capture a full display, selected region, window ID, or interactive selection to a caller-chosen image path using the native screencapture command. Use for local visual evidence, UI debugging, or screenshot capture outside browser-specific tooling.
---

# macOS Screenshot

Use `bin/macos-screenshot`. Captures can expose private screen content, so confirm the requested scope and output path before capture.

## Workflow

1. Run `check` when permissions or platform support are uncertain.
2. Choose the narrowest capture: region or window before full display.
3. Run `capture` with an explicit output path.
4. Verify that the output exists; inspect it only when the task requires visual analysis.

Read [references/usage.md](references/usage.md) for modes and macOS permission behavior.

