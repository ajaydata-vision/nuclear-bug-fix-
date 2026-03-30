# RC-006: Deadlock Between Two Database Transactions Acquiring Locks In Opposite Order

## User Prompt

Our money transfer system occasionally fails with 'deadlock detected' errors under concurrent load. Transfers always roll back cleanly but the failure rate is unacceptable. What is causing this?

## Context Provided To The Skill

- stack: Node.js 20.11, pg 8.11, PostgreSQL 16.1
- environment: production under concurrent load
- logs:
- ERROR: deadlock detected
  - DETAIL: Process 14521 waits for ShareLock on transaction 87903
  - Process 14698 waits for ShareLock on transaction 87895
  - TransferA: locks account 1 then account 2
  - TransferB: locks account 2 then account 1
- code excerpt:
```js
// Transaction A: transfer from account 1 to account 2
await lock(accountId1)
await lock(accountId2)

// Transaction B (concurrent): transfer from account 2 to account 1
await lock(accountId2)
await lock(accountId1)  // deadlock: waits for lock held by A
```
- reproduction:
1. Concurrent transfers: A->B and B->A simultaneously
2. Both acquire first lock
3. Both wait for second lock held by the other
4. PostgreSQL detects deadlock and rolls back one transaction
