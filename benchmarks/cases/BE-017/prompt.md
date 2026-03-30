# BE-017: Logs Show No Errors But Exceptions Thrown At DEBUG Level Only

## User Prompt

Our production application sometimes returns 500 errors but the logs show nothing wrong. How are errors happening without appearing in logs?

## Context Provided To The Skill

- stack: Node.js 20.11, Express 4.18.2, Winston 3.11
- environment: production (log level: INFO)
- logs:
- production logs show no errors
  - requests return 500 intermittently
  - setting log level to DEBUG reveals exception stack traces
  - exceptions logged with logger.debug() instead of logger.error()
- code excerpt:
```js
try {
  await riskyOperation()
} catch (err) {
  logger.debug('operation failed', err)  // should be logger.error
  res.status(500).send('Error')
}
```
- reproduction:
1. Set log level to INFO (production default)
2. Trigger failing operation
3. Observe 500 response but no error in logs
