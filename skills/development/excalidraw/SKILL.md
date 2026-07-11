---
name: excalidraw
description: "Create, patch, validate, and render Excalidraw diagrams through deterministic JSON and layout checks before delivery."
---

# Build an Excalidraw Diagram

1. Establish the audience, message, diagram type, required facts, output path, and readability target.
2. Read [references/excalidraw-format.md](references/excalidraw-format.md), then compose or patch `.excalidraw` JSON with stable IDs and bound text.
3. Run `bin/excalidraw FILE` to validate document shape, element bounds, overlaps, dangling bindings, and canvas extent.
4. Render with an available Excalidraw-compatible renderer, inspect the image, and revise spacing, hierarchy, color contrast, labels, and edge routing.
5. Preserve editable JSON and deliver a rendered artifact. Never claim visual quality from schema validation alone.

Use [agents/diagram-reviewer.md](agents/diagram-reviewer.md) for an independent visual and semantic review.
