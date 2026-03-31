# Verify

## before_fix

- First launch after install can fail
- Second launch often succeeds

## after_fix

- First launch succeeds reliably
- Child/helper launch waits for frozen runtime readiness
- Onefile startup is stable on a clean machine

## regression_checks

- Onedir build does not regress
- Packaged helper path still resolves correctly
- No arbitrary startup delay is introduced
