# Windows elevation model

Use this order: current user, supported per-operation elevation, interactive administrator process, then narrowly scoped SYSTEM task only when required. Windows sudo modes and availability vary by build; verify configuration locally. Third-party elevation helpers add a supply-chain decision and should not be installed implicitly.

SYSTEM runs in session 0, lacks the interactive user's profile and mapped drives, and has broad machine authority. Never use it for GUI or interactive commands.
