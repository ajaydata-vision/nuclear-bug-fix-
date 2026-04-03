# FE-021: fetch() Returns 400 But Login Flow Continues — Error Never Caught

## User Prompt

Our login form submits credentials. When the password is wrong the server returns
400 with `{ "error": "Invalid credentials" }`. But instead of showing an error
message the app navigates the user to the dashboard as if login succeeded. There
is no error in the browser console. The network tab clearly shows 400. How is the
error being swallowed?

## Context Provided To The Skill

- stack: React 18.2.0, TypeScript 5.3, Vite 5.1
- versions: Node.js 20.11, Chrome 122
- environment: browser, development and production
- logs:
  - Network tab: POST /api/auth/login → Status 400, Response: `{"error":"Invalid credentials"}`
  - No console errors
  - No `[AUTH]` error log line appears
- code excerpt:
```typescript
// authService.ts
async function login(email: string, password: string): Promise<User> {
  try {
    const response = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
    const data = await response.json();
    return data.user; // undefined when server returns error body
  } catch (err) {
    log.error('[AUTH] login failed:', err);
    throw err;
  }
}

// LoginForm.tsx
const handleSubmit = async () => {
  const user = await login(email, password);
  setCurrentUser(user);      // sets user to undefined
  navigate('/dashboard');    // navigates regardless
};
```
- reproduction:
  1. Enter valid email, wrong password
  2. Server returns HTTP 400 with `{"error":"Invalid credentials"}`
  3. `catch` block never executes
  4. `data.user` is `undefined` (error body has no `user` field)
  5. App navigates to `/dashboard` with no user set
