# Verification

## Before Fix
- "Import complete: 0 saved" appears immediately
- Individual saves arrive later out of order
- savedCount is always 0 at completion log

## After Fix (two options)

### Option A — Sequential (for...of, preserves order, safer for rate-limited APIs):
```typescript
async function importUsers(csvRows: CsvRow[]): Promise<void> {
  const users = csvRows.map(row => parseUser(row));
  let savedCount = 0;

  for (const user of users) {          // for...of awaits each iteration
    await apiClient.saveUser(user);
    savedCount++;
    log.info('[IMPORT] saved user:', user.email);
  }

  log.info('[IMPORT] Import complete:', savedCount, 'saved');
}
```

### Option B — Parallel (Promise.all, faster, use when API supports concurrent requests):
```typescript
async function importUsers(csvRows: CsvRow[]): Promise<void> {
  const users = csvRows.map(row => parseUser(row));

  const results = await Promise.all(
    users.map(async (user) => {
      await apiClient.saveUser(user);
      log.info('[IMPORT] saved user:', user.email);
      return user;
    })
  );

  log.info('[IMPORT] Import complete:', results.length, 'saved');
}
```

1. "Import complete: N saved" now appears AFTER all saves complete
2. savedCount accurately reflects the number of successful saves

## Regression Checks
- Empty CSV: `users` is empty array, loop completes immediately, "Import complete: 0 saved" correct
- Single user: saves once, completion log shows 1
- API error on one user: for...of stops at failure; Promise.all rejects with first failure — add error handling for partial failures
