# DE-004: Database Migration Not Run After Deploy Causes Schema Mismatch

## User Prompt

After deploying our app errors appear with 'Invalid column' errors in production. The column exists in the codebase. What is wrong?

## Context Provided To The Skill

- stack: Node.js 20.11, Prisma 5.9.1, PostgreSQL 16.1
- environment: production after deploy
- logs:
- PrismaClientKnownRequestError: Invalid column: 'last_login'
  - column added in recent migration
  - migration file exists in repo
  - production DB does not have the column
  - npx prisma migrate status shows 1 pending migration
- code excerpt:
```
# Deploy script (migration step missing)
git pull
npm install
pm2 restart app
```
- reproduction:
1. Deploy without running migration
2. App accesses new column
3. Observe database column error
