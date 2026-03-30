# FE-006: Form Submit Handler Never Reached Due To Wrong Event Binding

## User Prompt

Clicking Submit causes a page reload and the handler never runs. I can see the button and the handler are connected. What is the real bug?

## Context Provided To The Skill

- stack: React 18.2, TypeScript 5.0
- environment: browser
- logs:
- no console logs from handleSubmit
  - page reloads on button click
  - no network requests visible
- code excerpt:
```jsx
function handleSubmit(data) {
  console.log('submitted', data)
  api.post('/submit', data)
}
return (
  <form>
    <button onClick={handleSubmit}>Submit</button>
  </form>
)
```
- reproduction:
1. Fill form and click Submit
2. Page reloads
3. No console log appears
