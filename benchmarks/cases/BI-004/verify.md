# Verify

## before_fix

- Packaged parent and child report different versions/protocols
- Messages stop after startup handshake

## after_fix

- Parent refuses incompatible child versions
- Packaged parent and child report matching versions/protocols
- Messages continue after startup

## regression_checks

- Development and packaged modes both enforce the same version check
- Incompatible builds fail fast with a clear log
- Reconnect path still works when versions match
