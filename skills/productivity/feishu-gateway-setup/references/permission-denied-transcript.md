# Feishu Permission Denied: Reproduction Recipe

> From session 2026-06-01 (Feishu gateway first-time setup)

## Setup Context

- Hermes profile: default
- Feishu domain: feishu (Chinese mainland)
- Connection mode: websocket
- Group policy: open

## What Was Done

1. Set `FEISHU_APP_ID`, `FEISHU_APP_SECRET` in `.env`
2. Set `FEISHU_CONNECTION_MODE=websocket`, `FEISHU_DOMAIN=feishu`, `FEISHU_GROUP_POLICY=open`, `GATEWAY_ALLOW_ALL_USERS=true` in `.env`
3. Set `gateway.feishu.*` in `config.yaml` (app_id, connection_mode, domain, group_policy)

## What Happened

**Gateway startup log:**
```
✓ feishu connected (websocket mode)
Gateway running with 1 platform(s)
Channel directory built: 0 target(s)
```

**After user sent a DM ("你好"):**
```
[Feishu] Inbound dm message received: ... text='你好'
```

**Send failed:**
```
[99991672] Access denied. One of the following scopes is required:
[im:message:send, im:message, im:message:send_as_bot]
```

**Root cause:** App created on open.feishu.cn but never had message-send permissions added. The websocket connection succeeds regardless of permissions — the failure only surfaces when trying to send a reply.

## Fix

1. Opened https://open.feishu.cn/app/cli_aa97d44962badbd1/auth
2. Added scopes: `im:message`, `im:message:send_as_bot`, `im:message:send`
3. Published the app
4. Restarted gateway with `hermes gateway run --replace`

## Key Signals

- `Channel directory built: 0 target(s)` — strong indicator permissions are missing even if connection succeeds
- Error includes a clickable direct link to the permission page
- No need to configure event subscriptions in websocket mode (lark-oapi handles it)
