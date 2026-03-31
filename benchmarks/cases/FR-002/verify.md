# Verify

## before_fix

- Packaged app exits before UI appears
- Startup log shows empty Qt plugin path
- Error explicitly references Qt platform plugin initialization

## after_fix

- Packaged app starts on a clean Windows machine
- Frozen plugin path is logged and non-empty
- Qt platform plugin `"windows"` resolves successfully

## regression_checks

- Icons/resources still load after packaging changes
- Both onefile and onedir packaging behavior are understood
- Clean-machine smoke test is part of release verification
