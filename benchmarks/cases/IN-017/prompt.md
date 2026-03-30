# IN-017: Deploy Succeeds But Kubernetes Still Runs Old Image

## User Prompt

Our CI pipeline says the deploy succeeded, but the production cluster is still
running the old broken code. We use `:latest` in the deployment, and the rollout
shows green. Why is the cluster not actually picking up the fix?

## Context Provided To The Skill

- stack: Docker + Kubernetes Deployment
- versions: image tag `myapp:latest`
- environment: production cluster with multiple pods
- logs:
  - CI built and pushed a new image successfully
  - `kubectl rollout status deployment/myapp` shows success
  - running pods still report old app version on `/version`
- config excerpt:

```yaml
containers:
  - name: myapp
    image: registry.example.com/myapp:latest
    imagePullPolicy: IfNotPresent
```

- reproduction:
  1. Push a new image with the same mutable tag
  2. Trigger rollout
  3. Query `/version` on running pods
  4. Observe old version remains
