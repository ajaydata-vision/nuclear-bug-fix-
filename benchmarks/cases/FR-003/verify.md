# Verify

## before_fix

- Auth state path resolves under the install directory
- Write fails with `PermissionError`
- Relaunch requires QR pairing again

## after_fix

- Auth state path resolves under a user-writable directory
- Session persists across relaunches without admin rights
- Existing users migrate or recreate state predictably

## regression_checks

- Multi-user machines keep auth state isolated per user
- Uninstall/reinstall does not corrupt user data unexpectedly
- Bridge still receives the resolved auth dir correctly
