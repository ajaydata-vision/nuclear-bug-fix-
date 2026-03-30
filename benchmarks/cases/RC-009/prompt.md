# RC-009: Race Condition In Database Migration Causes Schema Corruption

## User Prompt

Our database schema gets corrupted during rolling deployments on Kubernetes. We think multiple pods are running migrations at the same time. How do we prevent this?

## Context Provided To The Skill

- stack: Node.js 20.11, Prisma 5.9.1, PostgreSQL 16.1, Kubernetes
- environment: production Kubernetes rolling deployment
- logs:
- schema corruption after rolling deployment
  - two pods ran migrations simultaneously
  - migration applied twice causing constraint conflicts
  - migration table shows migration run twice
- code excerpt:
```js
// Each pod runs migrations on startup
await prisma.$migrate.deploy()
// No distributed lock — two pods can run simultaneously
```
- reproduction:
1. Kubernetes rolling deploy starts with 2 pods
2. Both pods start and run migrations simultaneously
3. Migration applied twice → schema corruption
