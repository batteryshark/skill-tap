---
name: external-ip
description: "Resolve and cross-check a machine's public IP address through bounded external services with clear disagreement and network-failure reporting."
---

# Resolve a Public IP Address

1. Explain that the request contacts external services and reveals the source network address to them.
2. Run `bin/external-ip` with a short timeout. It queries multiple HTTPS endpoints and validates returned values as IP addresses.
3. Report consensus separately for IPv4 and IPv6. If services disagree, return all observations and do not guess; VPNs, proxies, split egress, DNS, or endpoint family can explain differences.
4. Do not label an address as a permanent home or device identity. It represents observed public egress at that time.

Read [references/interpretation.md](references/interpretation.md) before using the result in firewall or allowlist decisions.
