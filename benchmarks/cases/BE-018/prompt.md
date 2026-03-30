# BE-018: External API Works In Dev But Fails In Production Due To Outbound Firewall

## User Prompt

A third-party API call works perfectly in development but times out in production. The code is identical. Network or infrastructure issue is suspected. What is the bug?

## Context Provided To The Skill

- stack: Node.js 20.11, Express 4.18.2
- environment: production VPC with outbound firewall rules
- logs:
- ECONNREFUSED or ETIMEDOUT connecting to api.thirdparty.com
  - works in dev with no VPN or firewall
  - internal API calls work fine
  - outbound port 443 to api.thirdparty.com blocked by security group
- code excerpt:
```js
const result = await axios.get('https://api.thirdparty.com/data')
```
- reproduction:
1. Deploy to production
2. Trigger third-party API call
3. Observe ETIMEDOUT; same code works locally
