# OCR operator

Run local OCR over the supplied image(s) or directory using `bin/local-ocr-vlm`, without sending images to any hosted service.

## Inputs

- One or more image paths and/or a directory of images.
- Optional: target endpoint base URL, model ID, prompt, output directory, concurrency.

## Steps

1. Read `SKILL.md` and `references/reference.md`.
2. Confirm the endpoint is reachable and serving a vision model. If a run fails at preflight, report that the local server is not running or has no model loaded rather than retrying blindly.
3. Choose the narrowest invocation: a single image to stdout for a spot check, or `--input-dir` with `--output-dir` for a batch. Only pass `--model` when the endpoint hosts several and auto-selection would pick the wrong one.
4. Run the command. Preserve the tool's per-image error reporting; do not suppress failures.

## Evidence standard

Report which endpoint and model were used, the mode (stdout vs. markdown files), and any images that failed with their error. Distinguish "endpoint unreachable" from "individual image failed" — the exit code is `1` in both cases, but the causes and fixes differ.

## Constraints

- Keep the base URL on-machine unless the user explicitly asks for a remote endpoint.
- Do not modify input images. The tool only writes markdown output.
- Do not claim a batch succeeded unless the exit code is `0`.

## Output

A short summary: endpoint, model, count processed, output location, and any per-image failures with their messages.
