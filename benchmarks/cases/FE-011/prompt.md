# FE-011: Production Bundle Breaks Because Env Var Lacks VITE_ Prefix

## User Prompt

Our environment variable API_URL is set in .env.production but is undefined in the production bundle. It works fine in development. What is wrong?

## Context Provided To The Skill

- stack: React 18.2, Vite 5.0
- environment: production build
- logs:
- import.meta.env.API_URL is undefined in production
  - API_URL is set in .env.production
  - works in development with Vite dev server
- code excerpt:
```
# .env.production
API_URL=https://api.example.com
```
- reproduction:
1. Build production bundle
2. Load app
3. Observe API_URL is undefined, all API calls fail
