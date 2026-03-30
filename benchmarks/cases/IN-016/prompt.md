# IN-016: gRPC Streaming Call Drops After Load Balancer Idle Timeout

## User Prompt

Our gRPC streaming connections drop after exactly 60 seconds of inactivity. Clients with frequent messages are not affected. What is causing the disconnection?

## Context Provided To The Skill

- stack: Node.js 20.11, grpc-js 1.9, AWS ALB
- environment: production behind AWS Application Load Balancer
- logs:
- long-running gRPC streams disconnect after 60 seconds of no messages
  - AWS ALB idle connection timeout is 60s
  - gRPC client receives UNAVAILABLE status
  - streams with frequent messages do not disconnect
- code excerpt:
```js
const call = client.streamData({})
call.on('data', (chunk) => processChunk(chunk))
// No keepalive configured
```
- reproduction:
1. Start gRPC stream
2. Wait 60 seconds with no messages
3. Stream disconnects with UNAVAILABLE
