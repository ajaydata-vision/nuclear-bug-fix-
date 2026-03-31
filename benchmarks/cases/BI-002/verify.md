# Verify

## before_fix

- Fresh launch delivers one event once
- Reconnect cycles increase duplicate delivery count

## after_fix

- One reconnect still yields one handler invocation per inbound message
- Listener attach/detach counts remain stable across reconnects
- Duplicate deliveries disappear

## regression_checks

- Reconnect storms do not grow memory/listener count
- Intentional protocol retries are still handled correctly
- Parent-side idempotency is still preserved
