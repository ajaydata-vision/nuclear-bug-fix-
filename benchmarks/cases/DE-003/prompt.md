# DE-003: Environment Variable Set In .env But Undefined At Runtime

## User Prompt

An environment variable defined in our .env file is undefined at runtime even though dotenv is installed and the file exists. What is the bug?

## Context Provided To The Skill

- stack: Node.js 20.11, Express 4.18.2, dotenv 16.0
- environment: development and CI
- logs:
- process.env.DATABASE_URL is undefined
  - DATABASE_URL is set in .env file
  - no error from dotenv
  - other env vars set via OS environment work correctly
- code excerpt:
```js
// index.js
const db = new Database(process.env.DATABASE_URL) // undefined
require('dotenv').config() // dotenv loaded AFTER use
```
- reproduction:
1. Run node index.js
2. Observe DATABASE_URL is undefined
3. .env file contains DATABASE_URL
