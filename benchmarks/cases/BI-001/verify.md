# Verify

## before_fix

- Parent marks connected at subprocess spawn
- First event can occur before listener attachment
- Earliest message after startup is missing

## after_fix

- Parent does not declare ready until listener attached and child ready confirmed
- First inbound message after startup is delivered
- Startup ordering is explicit in logs

## regression_checks

- Slow startup and fast startup both behave correctly
- Reconnect path uses the same readiness contract
- No duplicate buffering/replay occurs
