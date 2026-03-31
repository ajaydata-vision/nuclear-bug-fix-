# Verify

## before_fix

- Clicking Send Reply does not update status
- Warning appears on shutdown

## after_fix

- Click immediately enters the async slot
- Status changes to Sending then Sent
- No coroutine warning appears at exit

## regression_checks

- Repeated clicks do not create duplicate tasks
- Errors inside the slot still surface cleanly
- App shutdown remains clean
