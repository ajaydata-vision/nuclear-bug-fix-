# Verify

## before_fix

- Source build launches the helper
- Packaged build resolves the expected frozen helper path
- Packaged extracted `bridge/` directory is empty
- Spawn fails with `ENOENT`

## after_fix

- Packaged bundle actually contains the helper
- Bridge helper launches from the frozen layout
- Source build still works

## regression_checks

- Onefile and onedir bundling inputs are both accounted for
- Packaged path logs remain explicit
- Child helper version still matches the parent release
