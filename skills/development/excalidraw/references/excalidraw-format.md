# Excalidraw format notes

A document is JSON with `type: "excalidraw"`, a numeric `version`, `source`, `elements`, `appState`, and `files`. Elements need unique IDs, geometry, style, versioning fields, and type-specific data. Text bound to a container should use matching `containerId`/`boundElements`; arrows should have valid start/end bindings when attached.

Schema checks cannot establish readability. Render and inspect the final canvas. Keep the editable source free of renderer-specific generated artifacts.
