# IN-010: API Gateway Strips Required Authorization Header

## User Prompt

All authenticated requests fail in production with 401 but work when calling the backend directly. The Authorization header is sent from the client. What is the bug?

## Context Provided To The Skill

- stack: Node.js 20.11, AWS API Gateway, Lambda
- environment: production behind API Gateway
- logs:
- 401 Unauthorized on all authenticated requests in production
  - works directly against Lambda function URL
  - API Gateway access logs show Authorization header absent
  - Authorization header present in client request
- code excerpt:
```yaml
# API Gateway integration — missing header mapping
Integration:
  RequestParameters:
    # Authorization header not mapped
```
- reproduction:
1. Send request with Authorization header through API Gateway
2. Lambda receives no Authorization header
3. Lambda returns 401
