# Portable agent design

A role prompt should state:

- one bounded responsibility;
- the artifacts or context it receives;
- what counts as evidence;
- constraints and prohibited actions;
- the exact decision or artifact it returns;
- how to report uncertainty and missing context.

Keep orchestration outside the prompt. Terms such as “subagent” and “workspace” travel better than vendor model names, tool APIs, or thread primitives. Forward-test with fresh context and raw inputs.
