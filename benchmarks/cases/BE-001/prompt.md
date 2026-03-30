# BE-001: Request Body Undefined Because Body Parser Mounted After Route

## User Prompt

req.body is undefined in our Express POST handler even though we're sending JSON with the correct Content-Type. Body parsing is configured. What is wrong?

## Context Provided To The Skill

- stack: Node.js 20.11, Express 4.18.2
- environment: development and production
- logs:
- req.body is undefined in POST handler
  - Content-Type: application/json is set
  - body is present in raw request
- code excerpt:
```js
app.post('/users', (req, res) => {
  console.log(req.body) // undefined
  res.json(req.body)
})
app.use(express.json())
```
- reproduction:
1. POST /users with JSON body
2. Observe req.body is undefined
