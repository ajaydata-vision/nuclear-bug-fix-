# BE-007: ORM Returns Wrong Rows Because JOIN Uses Wrong Condition

## User Prompt

Our endpoint for user posts returns posts from all users instead of just the requested user. The JOIN looks correct when reading the code. What is the real bug?

## Context Provided To The Skill

- stack: Node.js 20.11, Prisma 5.9.1, PostgreSQL 16.1
- environment: development and production
- logs:
- API returns posts for wrong user
  - query returns posts from all users
  - adding WHERE clause in raw SQL returns correct rows
  - Prisma query log shows JOIN without WHERE on userId
- code excerpt:
```js
const posts = await prisma.post.findMany({
  include: { author: true }
  // missing where: { authorId: userId }
})
```
- reproduction:
1. GET /users/42/posts
2. Observe posts from all users returned
