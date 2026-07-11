---
name: local-ocr-vlm
description: Run OCR on local images through an OpenAI-compatible local vision endpoint (LM Studio, vLLM/vmlx). Use when you need offline, on-machine document OCR into markdown, including batch directory processing, without sending images to a hosted service.
---

# Local OCR VLM

Send image(s) to a locally hosted OpenAI-compatible vision endpoint and capture the text. Defaults to `http://127.0.0.1:1234/v1`. The tool is a single, zero-dependency Node script; no Python or SDK is required.

## When to use

- OCR screenshots, scans, or document images on-machine.
- Batch a folder of images into per-image markdown files.
- Keep OCR offline using LM Studio or a vLLM/vmlx-compatible API.

## Prerequisites

- Node.js 18+ (uses the built-in global `fetch`; no packages to install).
- A local OpenAI-compatible server exposing a `/v1` API with a vision-capable model loaded. Qwen 3.5 9B is preferred; Qwen 3.5 27B also works.

## Commands

Run the portable entry point:

```sh
bin/local-ocr-vlm invoice.png
bin/local-ocr-vlm --input-dir doc_input --output-dir doc_output --max-workers 4
bin/local-ocr-vlm --input-dir doc_input --model "qwen3.5-vl-9b"
```

Run `bin/local-ocr-vlm --help` for every flag. See [`references/reference.md`](references/reference.md) for the endpoints called, model auto-selection, thinking-mode handling, and exit codes.

## Workflow

1. Confirm a local endpoint is serving `/v1` with a vision model loaded.
2. Point the tool at one or more images and/or an `--input-dir`. With no `--output-dir`, results print to stdout; with one, each image becomes `<stem>.md`.
3. Let the tool auto-select a model, or pass `--model` when the endpoint hosts several.
4. Tune `--max-workers` for throughput; use `1` for strictly sequential processing.

## Rules

- Never point the tool at a remote/hosted endpoint when the intent is to keep images on-machine; the default base URL is loopback.
- The tool reads images and writes only markdown output; it does not modify input images.
- Treat an unreachable endpoint or a per-image request failure as an explicit error. A run exits non-zero if any image fails.

Use [`agents/ocr-operator.md`](agents/ocr-operator.md) when a subagent should choose flags and verify the endpoint before running a batch.
