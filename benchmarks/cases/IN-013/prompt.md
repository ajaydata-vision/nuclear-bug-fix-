# IN-013: CI/CD Pipeline Deploys To Wrong Environment Due To Missing Branch Check

## User Prompt

A push to a feature branch accidentally deployed to production. The deploy pipeline should only run on main. What is the bug?

## Context Provided To The Skill

- stack: GitHub Actions, Node.js 20.11
- environment: GitHub Actions CI/CD
- logs:
- feature branch push triggers production deploy
  - no branch condition on the deploy job
  - production data modified by incomplete feature code
- code excerpt:
```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    # missing: if: github.ref == 'refs/heads/main'
    steps:
      - run: ./deploy-production.sh
```
- reproduction:
1. Push to a feature branch
2. CI runs the deploy job
3. Incomplete feature code deployed to production
