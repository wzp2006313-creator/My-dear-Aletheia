# Session Notes: Feishu Gateway Setup (2026-06-01)

## Credentials used

```
FEISHU_APP_ID=cli_aa97d44962badbd1
FEISHU_CONNECTION_MODE=websocket
FEISHU_GROUP_POLICY=open
FEISHU_DOMAIN=feishu
GATEWAY_ALLOW_ALL_USERS=true
```

## Config set

```bash
hermes config set gateway.feishu.app_id cli_aa97d44962badbd1
hermes config set gateway.feishu.group_policy open
hermes config set gateway.feishu.connection_mode websocket
hermes config set gateway.feishu.domain feishu
```

## Successful connection log

```
2026-06-01 19:16:38 INFO  gateway.run: Starting Hermes Gateway...
2026-06-01 19:16:38 INFO  gateway.run: Session storage: /Users/eason/.hermes/sessions
2026-06-01 19:16:38 INFO  gateway.run: Agent budget: max_iterations=150
2026-06-01 19:16:38 INFO  gateway.run: Secret redaction: ENABLED
2026-06-01 19:16:38 INFO  gateway.run: Recovered 1 background process(es) from previous run
2026-06-01 19:17:03 INFO  gateway.run: Connecting to feishu...
2026-06-01 19:17:03 INFO  gateway.platforms.feishu: [Feishu] Connected in websocket mode (feishu)
2026-06-01 19:17:03 INFO  gateway.run: ✓ feishu connected
2026-06-01 19:17:03 INFO  gateway.run: Gateway running with 1 platform(s)
2026-06-01 19:17:03 INFO  gateway.run: Channel directory built: 0 target(s)
```

## Key observation

`Channel directory built: 0 target(s)` is normal at startup when no messages have been received yet. The directory populates when users first interact with the bot. If the bot has been @'ed and no new log lines appear, the app-side configuration (permissions, publish, event subscription) is the culprit — NOT the gateway.

## Dedup command used

```bash
sed -i '' '486,490d' ~/.hermes/.env
```
Used to remove duplicate FEISHU_* and GATEWAY_ALLOW_ALL_USERS lines after a double-write.
