# BE-012: Uploaded File Inaccessible In Multi-Instance Deployment

## User Prompt

File uploads work but files become inaccessible intermittently in production. The issue seems to depend on which server handles the request. What is the real bug?

## Context Provided To The Skill

- stack: Node.js 20.11, Express 4.18.2, Multer 1.4, 3 app instances
- environment: production with 3 app instances behind load balancer
- logs:
- file upload returns 200
  - subsequent GET /files/:id sometimes returns 404
  - error correlates with requests hitting different instance than the upload
  - local /uploads directory on each instance has the file only on one
- code excerpt:
```js
storage: multer.diskStorage({
  destination: './uploads'
})
```
- reproduction:
1. Upload file (hits instance A)
2. GET /files/:id (hits instance B)
3. Observe 404 because file is only on instance A
