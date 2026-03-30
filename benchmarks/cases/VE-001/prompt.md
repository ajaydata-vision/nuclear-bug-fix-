# VE-001: npm Package Peer Dependency Version Mismatch Causes Silent Failure

## User Prompt

After upgrading to React 18 our react-query hooks stopped working silently. No errors appear but data is never fetched. What is causing this?

## Context Provided To The Skill

- stack: React 18.2, react-query 3.39 (requires React 16-17)
- environment: development and production
- logs:
- useQuery hook returns undefined and never fetches
  - no errors in console
  - npm install shows WARN incorrect peer dependency react@^16.8.0 || ^17.0.0
  - worked before React 18 upgrade
- code excerpt:
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-query": "^3.39.0"
  }
}
```
- reproduction:
1. Install dependencies with npm install
2. Use useQuery in a component
3. Observe it never fetches and returns undefined
