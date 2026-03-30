# DE-007: Deployment Targets Wrong Environment Due To Missing Env Flag

## User Prompt

After merging to main our deploy pipeline succeeds but production still has the old version. Staging was updated. What is wrong?

## Context Provided To The Skill

- stack: Node.js 20.11, GitHub Actions
- environment: CI/CD pipeline
- logs:
- deploy script runs successfully
  - production URL still shows old version
  - staging URL shows the new version
  - CI log shows deploy target: staging instead of production
  - deploy command missing --env production flag
- code excerpt:
```yaml
# .github/workflows/deploy.yml
- run: ./deploy.sh  # missing --env production
```
- reproduction:
1. Merge to main branch
2. CI deploy runs
3. Observe staging updated but production unchanged
