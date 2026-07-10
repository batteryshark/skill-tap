# Diagram review checklist

## Question and scope

- Can a reader state the question this diagram answers?
- Does every node help answer it?
- Are system context and internal implementation kept at compatible levels?

## Evidence

- Is each important relationship supported by code, configuration, schema, test, log, reproduced behavior, or explicit documentation?
- Are inference and documented intent distinguishable from observed behavior?
- Are paths, symbols, or scenarios supplied outside the visual?

## Model quality

- Are direction, ownership, data movement, and state changes unambiguous?
- Are important errors, alternate branches, retries, guards, or terminal conditions missing?
- Does the visual hide shared state, side effects, privilege changes, or external dependencies?
- Are names based on responsibility rather than incidental directories or implementation classes?

## Readability and durability

- Can the diagram be understood without zooming through implementation noise?
- Does its legend explain nonstandard shapes or line styles?
- Does nearby documentation state scope, omissions, and uncertainty?
- Is there an owner or obvious update trigger when the represented system changes?
