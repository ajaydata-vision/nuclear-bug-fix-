# RC-003: Double Form Submission Creates Duplicate Records

## User Prompt

Users on slow connections sometimes submit forms twice creating duplicate entries. We need to prevent this both on the frontend and backend. What is the proper fix?

## Context Provided To The Skill

- stack: React 18.2, Node.js 20.11, Express 4.18.2, PostgreSQL 16.1
- environment: production
- logs:
- duplicate form submissions on slow connections
  - users double-click submit button
  - two identical POST requests arrive within milliseconds
  - two database records created with identical data
- code excerpt:
```jsx
<button onClick={handleSubmit}>Submit</button>
// No disabled state during submission
```
- reproduction:
1. Double-click the submit button on a slow connection
2. Observe two identical records in the database
