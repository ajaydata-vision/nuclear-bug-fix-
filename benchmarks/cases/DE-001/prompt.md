# DE-001: Fixed Code Never Runs Because Container Was Not Rebuilt

## User Prompt

I changed the bugged code, redeployed the app, and the behavior is still
identical. I even added a log line and never see it. What is actually wrong if
the code fix is clearly in the repo?

## Context Provided To The Skill

- stack: Docker Compose + Node.js service
- versions: local staging environment
- environment: containerized deploy
- logs:
  - new sentinel log string never appears
  - `docker compose up -d` was run after the code change
  - running container still shows old app version
- code excerpt:

```yaml
services:
  api:
    build: .
    image: myapp-api:local
```

- reproduction:
  1. Change code and add sentinel log
  2. Run `docker compose up -d`
  3. Exercise endpoint
  4. Observe old behavior and missing sentinel
