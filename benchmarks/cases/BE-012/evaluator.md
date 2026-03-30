# Evaluator

## Metadata

- id: BE-012
- domain: backend
- track: deploy-env
- difficulty: medium
- determinism: intermittent
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: file-upload, multi-instance, local-disk, s3, load-balancer

## Ground Truth

- root_cause: Files are stored on the local disk of the instance that handled the upload. Other instances do not have the file and return 404.
- why_it_happens: Local disk storage is not shared between instances in a horizontally scaled deployment. Uploaded files must be stored in a shared storage system accessible to all instances.
- accepted_fix: Use shared object storage (AWS S3, Google Cloud Storage, or a shared NFS mount) instead of local disk. Return a URL pointing to the shared storage.
- rejected_fix_patterns:
  - pin users to the same instance via sticky sessions
  - sync files between instances via cron

## Evidence Signals

- strongest_signal: 404 correlates exactly with request hitting a different instance than the upload
- strongest_alternative_explanation: File permissions preventing access
- why_alternative_is_wrong: Files are accessible on the instance that uploaded them; permissions are not the issue

## Scoring Notes

- full_credit_conditions:
  - identifies local disk not shared between instances
  - proposes S3 or shared storage
  - explains horizontal scaling requirement
- partial_credit_conditions:
  - identifies multi-instance issue but proposes sticky sessions as solution
- fail_conditions:
  - suggests increasing disk space
  - blames load balancer
