# FE-007: Frontend Validation Passes But Serialized Payload Fails Backend

## User Prompt

Our form passes all frontend validation but the API always returns 422. The backend team says the date format is wrong. We're using a date picker. What is the actual bug?

## Context Provided To The Skill

- stack: React 18.2, TypeScript 5.0, date-fns 3.0
- environment: browser to REST API
- logs:
- frontend validation passes
  - POST request returns 422 Unprocessable Entity
  - backend error: 'expected ISO 8601 date, got number'
  - network tab shows date field as Unix timestamp
- code excerpt:
```ts
const payload = {
  name: form.name,
  dueDate: selectedDate.getTime()  // returns milliseconds
}
await api.post('/tasks', payload)
```
- reproduction:
1. Fill form with any future date
2. Submit
3. Observe 422 from API
