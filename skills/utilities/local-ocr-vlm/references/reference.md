# local-ocr-vlm reference

## Options

| Flag | Default | Meaning |
| --- | --- | --- |
| `images...` | — | Positional image paths to OCR. |
| `--input-dir <dir>` | none | Directory of images; all image files in it are added (sorted, case-insensitive). |
| `--base-url <url>` | `http://127.0.0.1:1234/v1` | OpenAI-compatible base URL. |
| `--api-key <key>` | `lm-studio` | Sent as `Authorization: Bearer <key>`. LM Studio ignores it. |
| `--model <id>` | auto | Model ID. If omitted, auto-selection runs (below). |
| `--prompt <text>` | OCR prompt | Instruction sent alongside each image. |
| `--output-dir <dir>` | none | Write `<stem>.md` per image. If omitted, print to stdout. |
| `--max-workers <n>` | `4` | Concurrent requests. `1` is fully sequential. |
| `--enable-thinking` | off | Allow model reasoning. Off means the tool probes for a way to disable it. |
| `--preflight-timeout <s>` | `10` | Timeout (seconds) for `/models` and the thinking-disable probe. |
| `-h`, `--help` | — | Print usage. |

Duplicate image paths (positional and directory) are de-duplicated by resolved path.

## Endpoints called

- `GET  {base-url}/models` — preflight; lists available model IDs.
- `POST {base-url}/chat/completions` — the thinking-disable probe and each OCR request.

Requests use the standard chat-completions shape: a `user` message whose content is a text part (the prompt) plus an `image_url` part carrying the image as a `data:<mime>;base64,...` URL. `temperature` is `0`.

## Model auto-selection

When `--model` is omitted, the tool prefers, in order:

1. Qwen 3.5 9B
2. any Qwen 9B
3. Qwen 3.5 27B
4. any Qwen 27B
5. the first model returned by `/models`

## Thinking mode

By default the tool tries to suppress model reasoning so output is just the OCR text. It probes these request bodies in order and keeps the first the endpoint accepts:

1. `chat_template_kwargs.enable_thinking = false`
2. `enable_thinking = false`
3. `thinking.enabled = false`
4. `reasoning_effort = "low"`

Probe rejections that look like unsupported-parameter errors are skipped silently; any other probe failure stops probing and the run continues with endpoint defaults (a warning is printed). Pass `--enable-thinking` to skip all of this and allow reasoning.

## Output

- stdout mode prints `===== <path> =====` followed by the text.
- `--output-dir` mode writes `# OCR Output: <filename>` followed by the text to `<stem>.md`.

## Exit codes

- `0` — all images processed successfully.
- `1` — invalid arguments, no input images, unreachable endpoint, no model resolvable, or one or more per-image failures.

## Runtime

Node.js 18+ only — the script relies on the global `fetch`, `AbortController`, and `node:fs/promises`. No npm install, no external dependencies.
