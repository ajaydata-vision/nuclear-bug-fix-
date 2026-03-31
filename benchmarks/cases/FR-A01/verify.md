# Verify

## before_fix

- Source run launches the bridge
- Packaged build resolves a nonexistent bridge path
- Spawn fails with ENOENT

## after_fix

- Frozen build resolves the bundled bridge script correctly
- Bridge starts successfully from the packaged app
- Source mode still works

## regression_checks

- Onefile and onedir path resolution are both understood
- Bridge version still matches parent version
- App launches from arbitrary working directories
