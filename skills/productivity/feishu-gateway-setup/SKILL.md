---
name: feishu-gateway-setup
description: "Configure Feishu/Lark as a Hermes Agent messaging gateway platform — env vars, config.yaml, permission pitfalls, and troubleshooting."
version: 1.0.0
author: Hermes Agent
tags: [feishu, lark, gateway, messaging, permissions, websocket]
---

# Feishu Gateway Setup

Configure Feishu (飞书) / Lark as a Hermes gateway platform.

## Prerequisites

- A Feishu app created at [open.feishu.cn](https://open.feishu.cn) (or open.larksuite.com for international)
- App credentials: `App ID` and `App Secret` from the app's **Credentials & Basic Info** page

## Step 1: Environment Variables

Add to `~/.hermes/.env`:

```bash
FEISHU_APP_ID=cli_xxxxxxxxxxxxx
FEISHU_APP_SECRET=your_app_secret
FEISHU_CONNECTION_MODE=websocket
GATEWAY_ALLOW_ALL_USERS=true
FEISHU_GROUP_POLICY=open
FEISHU_DOMAIN=feishu    # use "lark" for international (larksuite.com)
```

`FEISHU_GROUP_POLICY` controls who can interact:
- `open` — anyone can talk to the bot
- `allowlist` (default) — only users in `FEISHU_ALLOWED_USERS` can interact

`FEISHU_DOMAIN`:
- `feishu` — for Chinese mainland (feishu.cn)
- `lark` — for international (larksuite.com)

## Step 2: Config.yaml

```bash
hermes config set gateway.feishu.app_id cli_xxxxxxxxxxxxx
hermes config set gateway.feishu.connection_mode websocket
hermes config set gateway.feishu.domain feishu
hermes config set gateway.feishu.group_policy open
```

Note: `group_policy` in config.yaml is read from `FEISHU_GROUP_POLICY` env var (not from config.yaml directly for this field).

## Step 3: Feishu Open Platform Permissions (⚠️ Critical)

This is the most common pitfall. The websocket connection will succeed even without these permissions, giving a false sense that everything works.

**Required scopes** (Permissions → Add Permissions):

| Scope | Purpose |
|-------|---------|
| `im:message` | Receive messages |
| `im:message:send_as_bot` | Send messages as bot |
| `im:message:send` | Send messages |
| `im:message.group_at_msg` | Receive group @-mentions |
| `im:message.p2p_msg` | Receive DMs |
| `contact:contact:readonly` | Read user info (optional, for user display names) |

Quick link to add permissions:
```
https://open.feishu.cn/app/<YOUR_APP_ID>/auth
```

**After adding permissions, you MUST click "Publish" (发布)** — the app uses the published version.

## Step 4: Events (WebSocket mode)

No manual event subscription needed in websocket mode — `lark-oapi` handles event routing automatically. The adapter registers these handlers:

- `im.message.receive_v1` — incoming messages
- `im.message.reaction.created_v1` / `deleted_v1` — reactions
- `p2p_chat_created` — first DM from user
- `im.chat.member.bot.added_v1` / `deleted_v1` — group add/remove
- `drive.notice.comment_add_v1` — document comments

## Start the Gateway

```bash
hermes gateway run                # foreground
hermes gateway run --replace      # force-replace existing instance
hermes gateway install && start   # background service
```

## Troubleshooting

### Symptom: Gateway connects but bot doesn't respond

**Logs show:** Channel directory built: 0 target(s)

**Check:** Feishu open platform → app → Permissions → verify `im:message:send`, `im:message:send_as_bot`, `im:message` are all added AND the app has been **Published**.

### Symptom: "Access denied. One of the following scopes is required: [im:message:send, ...]"

The error includes a direct link:
```
https://open.feishu.cn/app/<APP_ID>/auth?q=im:message:send,im:message,im:message:send_as_bot
```

Open it, add the scopes, then Publish.

### Symptom: "Gateway already running"

Use `--replace` flag:
```bash
hermes gateway run --replace
```

### Symptom: "Another local Hermes gateway is already using this Feishu app_id"

Two gateway processes are fighting over the same app_id. Stop the other one first:
```bash
hermes gateway stop
hermes gateway run
```
