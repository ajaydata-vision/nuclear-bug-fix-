# Verify

## before_fix

- Queries that used to work now return zero items
- Raw response marker changed
- Maintainer/community reports match the timing

## after_fix

- App surfaces scraper/provider drift explicitly instead of silent empties
- Applying the known scraper fix or version pin restores results, or the app uses a documented fallback
- Empty-result handling is no longer silent

## regression_checks

- Non-empty queries still parse correctly
- Genuine empty results remain distinguishable from scraper breakage
- Future upstream drift is visible in logs/alerts
