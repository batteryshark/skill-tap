# Node portability rules

- Prefer `node:` built-ins and relative local modules.
- Use `.mjs` for committed runnable JavaScript.
- Commit a compiled `.mjs` sibling for every runnable `.ts` file.
- Create `package.json` only when it provides scripts, engines, or real dependencies.
- Commit `package-lock.json` and use `npm ci` for deterministic installation.
- Invoke local scripts with `npm --prefix <skill>/scripts run <name>` or a matching skill launcher.
- Do not depend on globally installed npm packages.
- Resolve assets relative to `import.meta.url`, not the caller’s working directory.
