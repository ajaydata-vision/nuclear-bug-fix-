# FE-022: Batch Import Runs But No Records Saved — Loop Completes Instantly

## User Prompt

We have a batch import function that reads a CSV, maps each row to a user object,
and saves each one to the database via an async API call. The function completes
without errors. The progress log shows "Import complete: 0 saved" immediately —
but then individual save confirmations arrive 2-3 seconds later with no way to
track them. Database ends up with partial saves depending on race conditions.
What is wrong with the loop?

## Context Provided To The Skill

- stack: React 18.2.0, TypeScript 5.3, Node.js 20.11 (backend API)
- versions: Vite 5.1, browser environment
- environment: browser, triggered by file upload UI
- logs:
  - `[IMPORT] starting batch of 47 users`
  - `[IMPORT] Import complete: 0 saved`   ← appears immediately
  - `[IMPORT] saved user: alice@example.com`  ← appears 2s later
  - `[IMPORT] saved user: bob@example.com`    ← appears 2.1s later
  - ... (all 47 arrive eventually, out of order)
- code excerpt:
```typescript
async function importUsers(csvRows: CsvRow[]): Promise<void> {
  const users = csvRows.map(row => parseUser(row));
  let savedCount = 0;

  await users.forEach(async (user) => {
    await apiClient.saveUser(user);
    savedCount++;
    log.info('[IMPORT] saved user:', user.email);
  });

  log.info('[IMPORT] Import complete:', savedCount, 'saved');
}
```
- reproduction:
  1. Upload CSV with 47 users
  2. `importUsers()` called
  3. "Import complete: 0 saved" logs immediately
  4. Individual save confirmations arrive seconds later, out of order
  5. If browser tab is closed before all complete → partial import with no tracking
