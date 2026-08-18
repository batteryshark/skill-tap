# Optional integration: the Work system

Applies only when a Work workspace is present (`work agent context`
resolves) and the user wants results filed. Everything here is additive; the
core workflows never require it.

## Mapping

The standard's document maps 1:1 onto a Work task — sections keep their
names and order; Work adds `Progress Log` and `Completion Summary`, which
this skill leaves alone.

- A goal is a top-level task (`parentId: null`); an epic's children are
  tasks with `parentId` set to it. One level only.
- The checkbox economics are enforced: Work refuses `review` and `blocked`
  while any checkbox is neither ticked nor declined-with-a-reason.
- A goal enters execution only when a human ticks `delegated` and moves it
  `backlog → ready`. Never do either.

## Craft

- Recon adds: `work agent context` for the resolved project — keep it, never
  infer assignment from prose — and `work list` for collisions and
  `dependsOn` candidates.
- File on confirm with the `work` CLI. The installed catalog is the
  authority on mechanics — `work agent instructions tasks.create` — not this
  file. Status stays `backlog`. Anything this Work version's CLI cannot set,
  set with a follow-up from the same catalog rather than editing files.
- Hand back the new `W-####` id, then the two actions only the human can
  take: tick `delegated`, and move it `backlog → ready`.

## Grade

Load a `W-####` id with `work show <id>`; grade the markdown it prints.

## Split

- Create each child with the `work` CLI, same project as the parent, status
  `backlog`, sibling orderings as `dependsOn`.
- Set each child's `parentId` to the epic's id: `tasks.update` via the
  installed catalog, or `PATCH /api/tasks/<child-id>` with
  `{"parentId": "<epic-id>"}` if the API is up. Neither reachable from this
  Work version: edit the child file's frontmatter `parentId` — that one
  field only, camelCase key, quoted value.
- Verify with `work show` on one child, then list the new child ids under
  the epic id.
