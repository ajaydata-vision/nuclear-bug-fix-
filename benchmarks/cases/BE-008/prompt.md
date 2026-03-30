# BE-008: Migration Ran On Wrong Database Because Connection String Points To Staging

## User Prompt

We ran a database migration and it reported success, but production is still erroring with missing column. The migration definitely ran. What happened?

## Context Provided To The Skill

- stack: Node.js 20.11, Prisma 5.9.1, PostgreSQL 16.1
- environment: production deploy with .env misconfiguration
- logs:
- npx prisma migrate deploy ran successfully
  - production database schema unchanged
  - staging database has new schema applied
  - DATABASE_URL in .env points to staging connection string
  - production DATABASE_URL is set only in the CI/CD secret vault
- code excerpt:
```
# .env (committed by mistake — points to staging)
DATABASE_URL=postgresql://user:pass@staging-db.internal:5432/app

# CI/CD secrets (correct production URL — not loaded locally)
DATABASE_URL=postgresql://user:pass@prod-db.internal:5432/app
```
- reproduction:
1. Engineer runs migration locally with production intention
2. Migration runs against staging DB (from .env)
3. Production schema unchanged, application errors on deploy
