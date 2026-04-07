# Evaluator

## Metadata

- id: EL-007
- domain: elixir-phoenix
- pattern: LiveView PubSub duplicate messages
- track: bohrbug-core
- difficulty: easy
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: liveview, pubsub, subscribe, double-subscribe, connected, mount, handle_info

## Ground Truth

- root_cause: `Phoenix.PubSub.subscribe/2` is called in `mount/3` without a `connected?(socket)` guard. Since LiveView calls `mount/3` twice (HTTP + WebSocket), the same LiveView process subscribes to `"room:#{room_id}"` twice. Each broadcast is delivered once per subscription — twice to this process — triggering two `handle_info` callbacks on the same pid.
- why_it_happens: PubSub subscriptions are per-process-per-topic. Subscribing twice creates two independent subscriptions. The same process receives the broadcast twice — once for each subscription — resulting in duplicate handle_info callbacks and duplicate messages appended to the list.
- accepted_fix: Wrap `Phoenix.PubSub.subscribe` in `if connected?(socket) do` — subscribes only on the WebSocket mount, resulting in exactly one subscription per process.
- rejected_fix_patterns:
  - deduplicate messages by ID in handle_info (workaround, not fix)
  - use Phoenix.Channel instead (architectural change, not the fix)
  - call Phoenix.PubSub.unsubscribe before subscribing (race-prone workaround)

## Evidence Signals

- strongest_signal: Same pid receives handle_info twice for same message_id; subscribe called in mount without connected? guard
- pathognomonic_prove: Add counter in handle_info — two calls per broadcast for same pid confirms double subscription; fix with connected? guard results in exactly one call
- strongest_alternative_explanation: Broadcast called twice from the sender
- why_alternative_is_wrong: Logs show single "Broadcasting message_id=abc123" line; all connected users see duplicates simultaneously (rules out single-user issue)

## Scoring Notes

- full_credit_conditions:
  - identifies double subscribe due to missing connected? guard in mount
  - explains LiveView double mount causes double subscription
  - fix wraps subscribe in if connected?(socket)
  - mentions counter Prove (two handle_info per broadcast)
- partial_credit_conditions:
  - identifies duplicate messages but suggests deduplication instead of fixing subscribe
- fail_conditions:
  - blames broadcast code (confirmed called once)
  - suggests client-side deduplication as the fix
