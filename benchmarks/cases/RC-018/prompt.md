# RC-018: Readiness Probe Passes Before Dependencies Are Actually Ready

## User Prompt

Our service passes Kubernetes readiness almost immediately, then starts failing
requests for 20-30 seconds because Redis and PostgreSQL connections are still
warming up. After that it becomes healthy. Why are users hitting a "ready" pod
that is not truly ready?

## Context Provided To The Skill

- stack: Node.js 20 + Express + PostgreSQL + Redis
- versions: Kubernetes Deployment
- environment: startup and rolling deploy window
- logs:
  - readiness endpoint returns 200 as soon as HTTP server starts
  - first live requests fail with `ECONNREFUSED` to Redis or DB pool not ready
  - failures stop once dependencies finish connecting
- code excerpt:

```js
app.get('/ready', (_req, res) => {
  res.sendStatus(200);
});

app.listen(3000);
connectRedis();
connectPostgres();
```

- reproduction:
  1. Start a new pod
  2. Wait for readiness to pass
  3. Send traffic immediately
  4. Observe startup failures
