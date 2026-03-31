# Verify

## before_fix

- Packaged build reaches the settings page and crashes with `ModuleNotFoundError`
- Source build works

## after_fix

- Packaged build opens the settings page successfully
- Hidden import / hook is included in the build config
- No dev-environment dependency is required

## regression_checks

- Other dynamic imports still work after rebuild
- Clean machine test still passes
- Error reporting remains explicit if a future import is missing
