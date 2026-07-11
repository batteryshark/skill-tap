# Public IP interpretation

Different services may observe different addresses because of IPv4/IPv6 selection, VPNs, proxies, carrier-grade NAT, or multiple egress paths. Record the service and timestamp. For firewall allowlisting, prefer a documented static egress range or dynamic-DNS/control-plane mechanism over a one-time observation.
