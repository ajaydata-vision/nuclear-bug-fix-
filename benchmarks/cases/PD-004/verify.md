# Verify

## before_fix

- Window closes but process remains running
- Logs show cleanup requested but tasks still alive

## after_fix

- Close event triggers orderly cleanup
- Websocket and scheduler stop before exit
- Process terminates immediately after window close

## regression_checks

- Reopen and close still exits cleanly
- No pending-task warnings remain
- Long-running websocket sessions still function before shutdown
