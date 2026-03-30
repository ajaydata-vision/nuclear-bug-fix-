# IN-002: Webhook Signature Validation Fails Because Raw Body Is Lost

## User Prompt

Our payment provider says webhooks are being delivered, and we can see the
requests hitting our endpoint, but every event is rejected with "invalid
signature". The secret is definitely correct. What are we actually doing wrong?

## Context Provided To The Skill

- stack: Node.js 20.11.0 + Express 4.18.2
- versions: payment provider signs the raw request body
- environment: production webhook endpoint
- logs:
  - provider dashboard shows HTTP 400 responses
  - local logs show parsed JSON body but signature mismatch
- code excerpt:

```js
app.use(express.json());

app.post('/webhooks/provider', (req, res) => {
  const signature = req.header('x-provider-signature');
  verifySignature(JSON.stringify(req.body), signature, process.env.WEBHOOK_SECRET);
  handleEvent(req.body);
  res.sendStatus(200);
});
```

- reproduction:
  1. Replay a real provider webhook
  2. Confirm request reaches endpoint
  3. Confirm signature verification fails every time
