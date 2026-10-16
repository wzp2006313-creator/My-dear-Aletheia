---
name: macos-proxy-diagnostics
description: "Diagnose macOS proxy/VPN traffic hijack via fake-ip/TUN."
version: 1.0.0
metadata:
  hermes:
    tags: [macos, network, proxy, vpn, shadowrocket, clash, surge, fake-ip, tun, feishu, gateway, troubleshooting]
---

# macOS Proxy/VPN Interference Diagnostics

When a service fails with ProxyError / 503 / connection timeout, or the user's
VPN/proxy software is suspected of hijacking traffic to a specific domain, run
this ordered diagnosis BEFORE changing anything.

## Detection (ordered)

1. System proxy: `scutil --proxy` — shows HTTP/HTTPS/SOCKS proxy (usually
   127.0.0.1:<port>) and the ExceptionsList.
2. TUN mode: `ifconfig | grep -E '^utun'` — several utun interfaces mean a
   VPN/TUN app is routing ALL traffic at the network layer. In TUN mode the
   system-proxy ExceptionsList (bypass list) is INEFFECTIVE — do not try to fix
   the problem by editing it.
3. Fake-ip DNS hijack: `dig +short <domain>` (or `nslookup`). An address in
   198.18.0.0/15 (the reserved fake-ip range) is the signature: the proxy app is
   running fake-ip mode with its own DNS at 198.18.0.2:53 and intercepting every
   DNS answer.
4. Identify the app + port: `lsof -nP -iTCP:<port> -sTCP:LISTEN` and
   `ps aux | grep -iE 'clash|surge|shadowrocket|v2ray|xray|trojan|sing-box|mihomo'`.
   Shadowrocket's tunnel runs as the `MacPacketTunnel` appex (process `MacPacket`).

## Isolate root cause (verify direct works)

Resolve the REAL ip via a public DNS that bypasses the fake-ip, then curl direct:

```bash
REAL_IP=$(dig +short <domain> @223.5.5.5 | grep -E '^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$' | head -1)
curl -s -o /dev/null -w 'HTTP %{http_code} time %{time_total}s\n' \
  --noproxy '*' --resolve "<domain>:443:$REAL_IP" --max-time 10 "https://<domain>/path"
```

- direct = 200/404 (TLS handshake works) while via-proxy = 503/000 → the proxy is
  the culprit; the fix is to route that domain DIRECT.
- Pitfall: a bare `nc -vz <domain> 443` "succeeds" even when HTTPS is broken,
  because TCP connects to the fake-ip handled by the TUN device while the proxy
  node still cannot reach the real server. Always verify with `curl --resolve` to
  the REAL ip, never just a TCP probe.

## Fix path

Shadowrocket macOS stores rules as COMPILED BINARY, not text:
- `~/Library/Group Containers/group.com.liguangming.Shadowrocket/default.db.rule`
  (compiled domain trie) plus `rule.db` (SQLite with private-format blobs).
- These files are macOS TCC-protected — terminal access returns
  "authorization denied" / "you don't have permission". There is no .conf text file.
- Do NOT attempt CLI editing: the format is private and hard-editing corrupts the
  entire VPN config. The only safe, persistent fix is the Shadowrocket GUI — add
  local rules, which outrank subscription rules and survive subscription updates.

Feishu (Lark) gateway needs these DIRECT rules (DOMAIN-SUFFIX covers all
subdomains, including open.feishu.cn used by the websocket):
```
DOMAIN-SUFFIX,feishu.cn,DIRECT
DOMAIN-SUFFIX,feishucdn.com,DIRECT
DOMAIN-SUFFIX,larksuite.com,DIRECT
```

## Hermes Feishu gateway cross-check

When the victim is the Hermes Feishu gateway, confirm from the log that the Lark
websocket is the failing connection:
```bash
grep -iE '\[Lark\].*connect failed|ProxyError' ~/.hermes/logs/gateway.log | tail -20
```
A repeating `[Lark] connect failed ... ProxyError ... 503` every ~2min means the
websocket long-connection is being killed by the proxy. After the user adds the
DIRECT rule (or disconnects the proxy), watch the same log for the websocket to
reconnect instead of erroring.
