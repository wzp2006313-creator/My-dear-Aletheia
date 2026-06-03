---
name: feishu-gateway
description: "Configure, troubleshoot, and operate the Feishu (飞书 / Lark) gateway for Hermes Agent — websocket connection, app credentials, event subscription, permissions."
version: 1.0.0
author: Hermes Agent
platforms: [macos, linux, windows]
metadata:
  hermes:
    tags: [feishu, lark, gateway, messaging, websocket, bot]
    related_skills: [hermes-agent]
---

# Feishu Gateway (飞书)

Hermes Agent connects to Feishu via the gateway platform adapter. Supports both websocket mode (recommended) and webhook callback mode.

## Quick Setup

### 1. Feishu App (Open Platform)

Create or configure an app at https://open.feishu.cn/app

### 2. Env Vars (.env)

```bash
FEISHU_APP_ID=cli_xxxxxxxxxxxxxxx
FEISHU_APP_SECRET=your_app_secret
FEISHU_CONNECTION_MODE=websocket
FEISHU_GROUP_POLICY=open
FEISHU_DOMAIN=feishu
GATEWAY_ALLOW_ALL_USERS=true
```

### 3. Config (config.yaml)

```yaml
gateway:
  feishu:
    app_id: cli_xxxxxxxxxxxxxxx
    group_policy: open
    connection_mode: websocket
    domain: feishu
```

Set via CLI:
```bash
hermes config set gateway.feishu.app_id cli_xxx
hermes config set gateway.feishu.group_policy open
hermes config set gateway.feishu.connection_mode websocket
hermes config set gateway.feishu.domain feishu
```

### 4. Start Gateway

```bash
# Foreground (testing)
hermes gateway run

# Background service
hermes gateway install
hermes gateway start
```

Verify connection in logs:
```
INFO gateway.run: Connecting to feishu...
INFO gateway.platforms.feishu: [Feishu] Connected in websocket mode (feishu)
INFO gateway.run: ✓ feishu connected
INFO gateway.run: Gateway running with 1 platform(s)
```

## Common Pitfalls

### macOS `uchg` immutable flag blocks config edits

On macOS, `hermes config set` may fail with `PermissionError: [Errno 1] Operation not permitted` because `config.yaml` has the user-immutable (`uchg`) flag. Fix:

```bash
ls -laO ~/.hermes/config.yaml   # check for "uchg" flag
chflags nouchg ~/.hermes/config.yaml
hermes config set gateway.feishu.group_policy open
```

See `references/macos-config-uchg-flag.md` for full details.

### Duplicate env vars in .env

When appending Feishu env vars to `.env`, earlier commented-out lines (e.g. `# GATEWAY_ALLOW_ALL_USERS=false`) persist alongside the new active lines. This is harmless but messy. Clean duplicates:

```bash
# Remove specific line ranges
sed -i '' '486,490d' ~/.hermes/.env
# Or grep to check first
grep -n "FEISHU\|GATEWAY_ALLOW" ~/.hermes/.env
```

### Gateway already running

If `hermes gateway run` errors with "Gateway already running (PID X)", use `--replace`:

```bash
hermes gateway run --replace
```

This sends SIGTERM to the old process and starts a new one.

## Troubleshooting: "Connected but bot not responding"

**Symptom:** Gateway logs show `✓ feishu connected` and `Channel directory built: 0 target(s)`, but @'ing the bot in Feishu does nothing. No incoming message events appear in logs.

**Root cause:** This is ALWAYS a Feishu app-side configuration problem — the websocket connection succeeded, but the app lacks permissions or event subscriptions to receive messages.

### Checklist

1. **Publish the app**
   - Go to Feishu Open Platform → your app → **「发布」** (Publish)
   - A dev-version app cannot receive messages in production groups

2. **Add message permissions**
   - Feishu Open Platform → 权限管理 (Permissions)
   - Required scopes:
     - `im:message` — Send and receive messages
     - `im:message.group_at_msg` — Receive group @ messages
     - `im:message.p2p_msg` — Receive direct messages
   - Click **「批量开通」** and submit for approval

3. **Configure event subscription (websocket mode)**
   - Feishu Open Platform → 事件订阅 (Event Subscription)
   - Add event: `im.message.receive_v1` — Message received
   - No webhook URL needed in websocket mode; just add the event

4. **Add bot to a group or DM**
   - Group: add the bot as a group member, then @ it
   - DM: find the bot and send it a private message directly

5. **Verify event delivery**
   - After fixing the above, @ the bot again
   - Gateway log should show incoming event lines like `[Feishu] Received message from ...`
   - If still no events, check: is the app in "debug mode"? Is the permission approval still pending?

### Known error: "Access denied — im:message:send required"

**Log entry:**
```
[Feishu] Send failed: [99991672] Access denied. One of the following scopes
is required: [im:message:send, im:message, im:message:send_as_bot].
应用尚未开通所需的应用身份权限：[im:message:send, im:message, im:message:send_as_bot]
```

**This happens when:**
- Gateway connects fine via websocket ✓
- Bot receives messages from users ✓
- But bot cannot reply ✗

**Fix:** The error includes a clickable link to add permissions:
```
https://open.feishu.cn/app/<APP_ID>/auth?q=im:message:send,im:message,im:message:send_as_bot
```

Replace `<APP_ID>` with your app's ID. Add the scopes, then **Publish** the app. No gateway restart needed if already running — just re-@ the bot after publishing.

**Root cause:** The websocket connection succeeds regardless of permissions. Permission enforcement only surfaces when the bot tries to send a reply. This is the #1 most common first-time setup issue.

### Debug commands

```bash
# Watch live logs
tail -f ~/.hermes/logs/gateway.log

# Check process health
process action=poll session_id=<proc_id>

# Restart gateway
hermes gateway restart
```
