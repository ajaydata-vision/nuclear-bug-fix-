# VE-003: Exact Library Version Has A Confirmed Upload Bug

## User Prompt

File uploads started failing in the browser right after we upgraded Axios. Small
JSON requests still work, but multipart uploads now return `400 invalid multipart boundary`.
Backend code did not change. What is the real cause?

## Context Provided To The Skill

- stack: React 18.2.0 + Axios 0.27.1 + Express upload API
- versions: Chrome 123
- environment: browser multipart form upload
- logs:
  - request header shows `Content-Type: multipart/form-data`
  - server rejects request with missing boundary
  - reverting Axios to previous version makes uploads pass again
- code excerpt:

```ts
const form = new FormData();
form.append('file', file);
await axios.post('/upload', form, {
  headers: { 'Content-Type': 'multipart/form-data' }
});
```

- reproduction:
  1. Upgrade to Axios 0.27.1
  2. Upload a file from the browser
  3. Observe `400 invalid multipart boundary`
