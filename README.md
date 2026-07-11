# Skills Tap

![Skills Tap — a retro comic-book mascot](assets/skills-tap.png)

Skills Tap is a public collection of portable, reusable skills for agents. It is a general-purpose catalog of repeatable workflows, organized by category as it grows. Each skill is self-contained, readable without a specific agent platform, and backed by small command-line tools where deterministic checks help.

## Skills

### Development

| Skill | Use it to |
|---|---|
| [`architecture-for-comprehension`](skills/development/architecture-for-comprehension/) | Review whether a system is coherent, navigable, and explainable as a whole. |
| [`code-quality-review`](skills/development/code-quality-review/) | Audit or improve local code quality with evidence and behavior-preserving refactoring. |
| [`codebase-archeology`](skills/development/codebase-archeology/) | Map inherited or archived projects and decide what to preserve, merge, or retire. |
| [`codebase-writeup`](skills/development/codebase-writeup/) | Produce an evidence-backed technical explanation of how a codebase works. |
| [`deliverable-hygiene`](skills/development/deliverable-hygiene/) | Keep a repository shaped like finished work and recover one that has accumulated process residue. |
| [`agent-create`](skills/development/skill-development/agent-create/) | Scaffold a portable Markdown role prompt with explicit inputs, constraints, and output contract. |
| [`excalidraw`](skills/development/excalidraw/) | Create and validate editable Excalidraw diagram JSON before rendering and delivery. |
| [`engineering-diagrams`](skills/development/engineering-diagrams/) | Create evidence-backed system, component, data-flow, sequence, state, and trust-boundary diagrams. |
| [`github-publish`](skills/development/github-publish/) | Preflight and publish a local project to GitHub without leaking or staging unrelated state. |
| [`publish-ready`](skills/development/publish-ready/) | Run a final, evidence-backed cleanup before sharing or releasing a repository. |
| [`mcp-elicitations`](skills/development/mcp/mcp-elicitations/) | Build and test protocol elicitations and FastMCP Apps interaction boundaries. |
| [`mcp-server-create`](skills/development/mcp/mcp-server-create/) | Scaffold a library-first FastMCP 3 server with portable configuration and tests. |
| [`mcp-server-design`](skills/development/mcp/mcp-server-design/) | Design providers, transforms, auth, tasks, outputs, discovery, and safety boundaries. |
| [`mcp-server-upgrade`](skills/development/mcp/mcp-server-upgrade/) | Upgrade an MCP server while preserving and verifying observable compatibility. |
| [`mcp-testing`](skills/development/mcp/mcp-testing/) | Test domain logic, MCP components, interactions, security, lifecycle, and transports. |
| [`skill-create`](skills/development/skill-development/skill-create/) | Scaffold a complete portable skill package that satisfies this tap's contract. |
| [`skill-node-portability`](skills/development/skill-development/skill-node-portability/) | Audit Node.js skill dependencies, lockfiles, launchers, and compiled artifacts. |
| [`skill-python-portability`](skills/development/skill-development/skill-python-portability/) | Audit Python skill imports, PEP 723 metadata, dependencies, and launchers. |
| [`skill-refine`](skills/development/skill-development/skill-refine/) | Audit and refine a skill package against the public portability contract. |
| [`work-product-audit`](skills/development/work-product-audit/) | Find public prose that leaks internal reasoning, defensive framing, or generated-sounding filler. |

### Productivity

| Skill | Use it to |
|---|---|
| [`decision-records`](skills/productivity/decision-records/) | Preserve consequential choices, constraints, alternatives, consequences, and reconsideration criteria. |
| [`project-retrospective`](skills/productivity/project-retrospective/) | Extract concrete lessons and improvements from completed or paused work. |
| [`project-tracker`](skills/productivity/project-tracker/) | Maintain compact durable project memory across sessions and handoffs. |
| [`claude-session-handoff`](skills/productivity/claude-session-handoff/) | Build a redacted, evidence-backed continuation brief from a Claude Code JSONL transcript. |
| [`apple-reminders`](skills/productivity/apple-reminders/) | Manage Apple Reminders through a native EventKit command with mutation safeguards. |
| [`reverse-brief`](skills/productivity/reverse-brief/) | Reconstruct an evidence-labeled implementation brief from existing artifacts. |

### Utilities

| Skill | Use it to |
|---|---|
| [`intellidiff`](skills/utilities/intellidiff/) | Compare files or folders, calculate SHA-256 hashes, and find exact duplicates. |
| [`docker-cleanup`](skills/utilities/docker-cleanup/) | Survey and selectively reclaim Docker disk usage without broad implicit deletion. |
| [`external-ip`](skills/utilities/external-ip/) | Cross-check public IPv4 or IPv6 observations through multiple HTTPS services. |
| [`nano-banana-image`](skills/utilities/nano-banana-image/) | Generate or edit images with Gemini using portable environment credentials. |
| [`system-recon`](skills/utilities/system-recon/) | Collect a bounded read-only system inventory without harvesting secrets. |
| [`windows-ai-controls`](skills/utilities/windows-ai-controls/) | Audit and plan reversible Windows AI policy changes for a specific build. |
| [`windows-elevation`](skills/utilities/windows-elevation/) | Plan the narrowest Windows elevation path with a guarded SYSTEM fallback. |

## Use a skill

Copy a complete skill directory into your agent's skill path, or point the agent directly at its `SKILL.md`. Keep the directory intact: scripts, references, and role prompts are part of the skill.

```sh
git clone https://github.com/batteryshark/skills-tap.git
cp -R skills-tap/skills/development/publish-ready /path/to/your/agent/skills/
```

Every Python tool can run with `uv` or the system Python. The executable in each skill's `bin/` directory prefers `uv` and falls back to `python3` when the tool has no third-party dependencies.

```sh
skills/development/publish-ready/bin/publish-ready .
```

## Add a skill

Put new skills under a broad category in `skills/`, optionally nest related skills in organizational groups, follow the [skill contract](SKILL-CONTRACT.md), and run:

```sh
python3 scripts/validate_skills.py
python3 -m unittest discover -s tests
```

## License

MIT. See [LICENSE](LICENSE).
