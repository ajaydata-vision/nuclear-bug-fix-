# Verify

## before_fix

- Parent reads stdout as JSON lines
- Bridge writes both JSON frames and debug logs to stdout
- Parse failures occur after debug lines

## after_fix

- Stdout contains protocol frames only
- Diagnostics move to stderr or file logging
- Parent parses all inbound frames successfully

## regression_checks

- Verbose logging mode no longer breaks the bridge
- Reconnect path preserves the same stdout discipline
- Parent surfaces malformed frames explicitly if they occur again
