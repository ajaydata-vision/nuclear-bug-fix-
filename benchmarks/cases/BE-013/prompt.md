# BE-013: Large File Upload Fails Because Reverse Proxy Has Lower Body Size Limit

## User Prompt

File uploads fail with 413 for anything over 1MB. Our Express app is configured to accept 50MB. Small files work. What is blocking the upload?

## Context Provided To The Skill

- stack: Node.js 20.11, Express 4.18.2, Multer 1.4, Nginx 1.24
- environment: production behind Nginx reverse proxy
- logs:
- 413 Request Entity Too Large for files above 1MB
  - Express body limit set to 50MB
  - Nginx error.log: client intended to send too large body: 3145728 bytes
  - small files upload correctly
  - curl directly to Node.js port (bypassing Nginx) succeeds for large files
- code excerpt:
```js
// Express — limit set correctly
app.use(express.json({ limit: '50mb' }))
app.use(multer({ limits: { fileSize: 50 * 1024 * 1024 } }).single('file'))
```
- reproduction:
1. Upload a 3MB file through the UI (via Nginx)
2. Observe 413 error
3. Upload same file directly to Node port 3000 (bypassing Nginx) — succeeds
