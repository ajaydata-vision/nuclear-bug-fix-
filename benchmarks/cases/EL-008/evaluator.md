# Evaluator

## Metadata

- id: EL-008
- domain: elixir-phoenix
- pattern: LiveView assign_async stale closure
- track: bohrbug-core
- difficulty: hard
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: liveview, assign_async, closure, stale, handle_params, navigation

## Ground Truth

- root_cause: The `assign_async` closure captures `product_id` from the outer scope of `handle_params`. But `product_id` is a local variable bound BEFORE `socket = assign(socket, :product_id, product_id)`. The closure closes over this local variable correctly. However, the issue is that when navigating quickly between products, `handle_params` may be called again with a new `id` before the async task from the previous call completes. The async task from the Product A navigation is still running and will overwrite `socket.assigns.product` with Product A's data after Product B's data was already assigned. The closure captures the `product_id` at the time `handle_params` was called — which is correct for that call — but the async result arrives out of order.

  Simpler explanation for the logged case: the log shows `assign_async started for product_id=102` but `fetched product: id=99` — this means the closure is capturing `product_id` from a previous handle_params call (99, not 102). The variable `product_id` in the closure is from the wrong handle_params invocation because handle_params was called twice in quick succession and the closure from call 1 (product 99) completed after call 2 (product 102) started.

- why_it_happens: Each `handle_params` call creates a new async task. If navigation happens faster than the async fetch, multiple async tasks run concurrently. They complete in unpredictable order. The last-completing task wins, which may be the older one.
- accepted_fix: Cancel the previous async task before starting a new one, or use a version/sequence counter to discard stale results. Simpler: use `assign_async` with `reset: true` to cancel the previous task.
- rejected_fix_patterns:
  - add a delay before fetching (reduces frequency, doesn't fix)
  - disable navigation between products (removes the feature)

## Evidence Signals

- strongest_signal: Log shows wrong product_id fetched; navigation between products triggers the bug; assign_async in handle_params
- pathognomonic_prove: Add IO.inspect(product_id, label: "[ASYNC-CLOSURE-PROVE] captured id") before the closure AND inside the closure — if they differ during rapid navigation, async result is from wrong handle_params call
- strongest_alternative_explanation: MyApp.Catalog.get_product caches the wrong product
- why_alternative_is_wrong: Direct IEx call to get_product returns correct data; issue only occurs after rapid navigation

## Scoring Notes

- full_credit_conditions:
  - identifies stale async result from concurrent handle_params calls
  - explains closure captures product_id from the correct call but results arrive out of order
  - fix uses assign_async reset: true or cancels previous task
- partial_credit_conditions:
  - identifies the stale data but blames closure capture incorrectly
- fail_conditions:
  - blames Catalog.get_product returning wrong data
  - suggests adding a loading spinner (already present)
