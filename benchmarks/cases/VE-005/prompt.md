# VE-005: Node.js Version Below Framework Minimum Causes Cryptic Runtime Error

## User Prompt

Next.js 14 fails to start with a syntax error on a fresh developer machine and in CI. It works on the lead developer's machine. What is the bug?

## Context Provided To The Skill

- stack: Node.js 16.20, Next.js 14.0 (requires Node.js 18.17+)
- environment: CI/CD and new developer machine
- logs:
- SyntaxError: Unexpected token '??' or similar modern syntax error
  - error occurs at Next.js startup
  - node --version shows 16.20
  - next --version shows 14.0
  - works on lead developer machine running Node 20
- code excerpt:
```
node --version: v16.20.2
next --version: 14.0.0
```
- reproduction:
1. npm install on Node 16
2. next dev
3. Observe cryptic syntax error at startup
