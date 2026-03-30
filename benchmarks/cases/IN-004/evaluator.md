# Evaluator

## Metadata

- id: IN-004
- domain: integration
- track: deploy-env
- difficulty: easy
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: kafka, rabbitmq, queue, topic, typo, consumer

## Ground Truth

- root_cause: The consumer subscribes to a different topic name than the producer publishes to due to a typo.
- why_it_happens: Kafka with auto-create enabled silently creates new topics if they do not exist. The typo creates a second empty topic instead of failing with an error.
- accepted_fix: Fix the topic name typo in the consumer subscription: 'orders.created'. Disable auto-create in production to prevent silent topic fragmentation.
- rejected_fix_patterns:
  - add a message router to forward between topics
  - consume from both topics

## Evidence Signals

- strongest_signal: Two similar topic names exist in Kafka with different message counts; one is empty
- strongest_alternative_explanation: Consumer group rebalancing issue
- why_alternative_is_wrong: Rebalancing would show partial consumption; zero messages received across restarts indicates subscription to wrong topic

## Scoring Notes

- full_credit_conditions:
  - identifies topic name typo
  - proposes fixing typo
  - recommends disabling auto-create in production
- partial_credit_conditions:
  - identifies wrong topic but does not address auto-create risk
- fail_conditions:
  - adds retry logic to consumer
  - blames Kafka cluster health
