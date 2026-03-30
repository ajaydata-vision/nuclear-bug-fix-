# FE-001: SSR Hydration Mismatch From `Date.now()`

## User Prompt

Our Next.js dashboard renders fine on the server, but the browser console shows
`Hydration failed because the initial UI does not match what was rendered on the server`.
The timestamp chip keeps changing on refresh. This started after we added a
"last seen" badge. What is actually wrong?

## Context Provided To The Skill

- stack: Next.js 14.2.3 + React 18.3.1
- versions: Node.js 20.11.1
- environment: SSR page in both dev and production build
- logs:
  - `Warning: Text content did not match. Server: "1712321000000" Client: "1712321000412"`
- code excerpt:

```tsx
export default function LastSeenBadge() {
  return <span className="chip">{Date.now()}</span>;
}
```

- reproduction:
  1. `npm run build && npm start`
  2. Open `/dashboard`
  3. Refresh twice
  4. Observe hydration mismatch in console
