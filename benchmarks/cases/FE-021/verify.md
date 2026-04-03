# Verification

## Before Fix
- Wrong password → network shows 400 → app navigates to /dashboard
- catch block never executes for HTTP errors
- setCurrentUser(undefined) sets no user

## After Fix
```typescript
async function login(email: string, password: string): Promise<User> {
  const response = await fetch('/api/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });

  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}));
    throw new Error(errorBody.error ?? `HTTP ${response.status}`);
  }

  const data = await response.json();
  return data.user;
}

// LoginForm.tsx — no change needed: the throw now propagates to the caller's catch
const handleSubmit = async () => {
  try {
    const user = await login(email, password);
    setCurrentUser(user);
    navigate('/dashboard');
  } catch (err) {
    setErrorMessage(err instanceof Error ? err.message : 'Login failed');
  }
};
```
1. Wrong password → 400 → `!response.ok` → throws `"Invalid credentials"` → catch shows error
2. Correct password → 200 → `data.user` → navigate to dashboard

## Regression Checks
- Network failure (offline): catch block receives TypeError (network error) — handled separately
- 500 server error: throws `"HTTP 500"`, catch shows error message
- 401 unauthorized: throws with error body content
- Successful login: no regression, navigate works as before
