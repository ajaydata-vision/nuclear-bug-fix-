# Verification

## Before Fix

1. Push a new image to the same mutable tag.
2. Run the deployment rollout.
3. Confirm pods can still report the old version.

## After Fix

1. Deploy using an immutable tag or digest.
2. Confirm all pods report the new version.
3. Confirm a new rollout really corresponds to a new image digest.

## Regression Checks

- Test node replacement or scale-out events.
- Confirm rollback still works with immutable versions.
- Confirm deployment automation updates the tag or digest every release.

