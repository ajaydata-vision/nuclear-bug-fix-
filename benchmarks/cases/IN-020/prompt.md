# IN-020: Microservice Returns Wrong Content-Type Causing JSON Parse Failure

## User Prompt

Our microservice integration keeps failing with a JSON parse error on a response that should be JSON. The upstream service returns 200. What is the bug?

## Context Provided To The Skill

- stack: Node.js 20.11, axios 1.6, Express 4.18.2
- environment: production microservice communication
- logs:
- SyntaxError: Unexpected token < in JSON at position 0
  - response body starts with '<html>'
  - Content-Type response header: text/html instead of application/json
  - axios parses as text and caller tries JSON.parse on HTML
- code excerpt:
```js
app.get('/health', (req, res) => {
  res.send({ status: 'ok' })  // missing res.json() or content-type
})
```
- reproduction:
1. Call /health from another service
2. Response is HTML (Express default error page or string)
3. Caller tries JSON.parse → SyntaxError
