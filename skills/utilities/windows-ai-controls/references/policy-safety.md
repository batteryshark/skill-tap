# Windows policy safety

Feature names, registry values, edition support, and defaults change across Windows releases. Use the target build's official policy documentation as the authority. A registry value may be ignored, superseded, or controlled by organization management.

Always export previous values or emit a restore script before mutation. Prefer supported policy over package removal, ownership changes, TrustedInstaller workarounds, scheduled-task deletion, or component-store surgery.
