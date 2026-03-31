# Verify

## before_fix

- First realtime event is lost on slower startups
- Later events arrive normally

## after_fix

- Listener is attached before the bridge emits ready traffic
- First event is delivered consistently
- Startup remains stable across slow and fast machines

## regression_checks

- Reconnect path uses the same listener ordering
- Buffering does not duplicate events
- Child emits are not lost when startup is delayed
