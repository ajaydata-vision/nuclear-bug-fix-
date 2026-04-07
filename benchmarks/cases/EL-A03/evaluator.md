# Evaluator

## Metadata

- id: EL-A03
- domain: elixir-phoenix
- pattern: Oban struct-in-args (partial — one plain scalar correct, two structs empty)
- track: adversarial
- difficulty: hard
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: oban, struct, args, json, partial-serialization, misleading-args

## Ground Truth

- root_cause: Same as EL-013 but partial — the `order_id` is a plain integer and serializes correctly to JSON. The `carrier` and `tracking` fields are Elixir structs (`%MyApp.Carrier{}` and `%MyApp.TrackingInfo{}`) and serialize to `{}` (empty maps). The developer was misled by seeing the correct `order_id` in the DB and concluded "args look fine." The `{}` values for carrier and tracking are the bug.
- why_partial_is_harder: When all args are `{}`, the developer immediately sees the problem. When one field is correct and others are `{}`, the developer may dismiss the `{}` values as "empty but expected" or miss them while focusing on the correct field. This is the adversarial variant — partial correctness causes false confidence.
- accepted_fix: Replace struct values with plain scalar IDs and primitive fields:
  ```elixir
  %{
    order_id: order.id,
    carrier_code: carrier.code,         # string
    carrier_name: carrier.name,         # string  
    tracking_number: tracking_info.number,  # string
    tracking_url: tracking_info.url     # string
  }
  ```
- why_perform_completes: `perform/1` matches on `%{"order_id" => order_id}` only — it does not pattern-match carrier or tracking from args. The pattern match succeeds (order_id is present). `process_shipment(order, ???)` — the actual call either crashes (if it tries to use carrier/tracking from args) or is a placeholder that doesn't exist yet. If it crashes, it would be retried and discarded. If state = completed, then process_shipment somehow succeeds with empty carrier/tracking data or returns :ok without actually sending anything.

## Scoring Notes

- full_credit_conditions:
  - identifies carrier: {} and tracking: {} as serialized structs (not empty-by-design)
  - explains why partial correctness (order_id correct) is misleading
  - explains that plain integers serialize correctly but structs serialize to {}
  - fix extracts plain scalar fields from structs before inserting
  - recognizes this is the same struct-in-args pattern as complete serialization failure, just partial
- partial_credit_conditions:
  - identifies the {} values as the problem but attributes it to wrong cause (missing data)
  - suggests the structs should have a Jason.Encoder protocol implementation (workaround)
- fail_conditions:
  - concludes args are fine because order_id is correct
  - blames the process_shipment function without examining the args
  - suggests the carrier and tracking were never provided at insertion time
