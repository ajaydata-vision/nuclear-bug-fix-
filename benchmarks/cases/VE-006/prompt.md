# VE-006: OAuth Token Request Violates RFC Requirements

## User Prompt

Our OAuth integration gets `405 Method Not Allowed` from the token endpoint in
production. The auth code is valid, and the provider docs say the endpoint is
standard OAuth 2.0. What are we actually doing wrong?

## Context Provided To The Skill

- stack: Node.js 20 + custom OAuth client
- versions: OAuth 2.0 authorization code flow with PKCE
- environment: production auth callback exchange
- logs:
  - authorization redirect succeeds
  - token exchange request uses `GET /oauth/token?...`
  - provider responds `405 Method Not Allowed`
- code excerpt:

```js
const url = `${tokenUrl}?grant_type=authorization_code&code=${code}&redirect_uri=${redirectUri}`;
const tokenRes = await fetch(url, {
  method: 'GET',
  headers: { 'Accept': 'application/json' }
});
```

- reproduction:
  1. Complete login redirect
  2. Exchange code for token
  3. Observe `405` on the token endpoint
