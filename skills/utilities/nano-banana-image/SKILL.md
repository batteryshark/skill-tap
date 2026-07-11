---
name: nano-banana-image
description: "Generate or edit images through Google's Gemini image API using environment-provided credentials, explicit output paths, and reproducible request metadata."
---

# Generate Images with Gemini

1. Confirm the requested content, aspect/size constraints, output directory, and whether source images may be sent to Google's API.
2. Read [references/request-safety.md](references/request-safety.md). Require the API key through `GEMINI_API_KEY`; never put it in arguments, source, logs, or generated metadata.
3. Run `bin/nano-banana-image --prompt ... --output ...` and pass source images only when editing is requested. The command validates MIME types, uses a user-selectable model, and writes returned image parts atomically.
4. Inspect every output image and record the prompt, model, source hashes, and response text without recording credentials.
5. If the API or model name has changed, verify the current official Google documentation before modifying the request.

Use [agents/image-request-reviewer.md](agents/image-request-reviewer.md) for sensitive source material or public-facing output.
