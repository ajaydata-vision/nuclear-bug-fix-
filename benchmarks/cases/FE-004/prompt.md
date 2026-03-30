# FE-004: CSS Purge Removes Dynamic Classes In Production Only

## User Prompt

Dynamically coloured text works perfectly in development but loses all styling in production. The class names appear in the HTML but have no styles. What is wrong?

## Context Provided To The Skill

- stack: React 18.2, Tailwind CSS 3.3, Vite 5.0
- environment: production build vs development
- logs:
- styles present in dev
  - production bundle missing CSS classes used dynamically
  - no console errors
- code excerpt:
```js
const color = isError ? 'red' : 'green'
return <div className={`text-${color}-500`}>Message</div>
```
- reproduction:
1. Run production build
2. Load page with error state
3. Observe text-red-500 class has no styles applied
