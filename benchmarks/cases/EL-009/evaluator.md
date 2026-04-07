# Evaluator

## Metadata

- id: EL-009
- domain: elixir-phoenix
- pattern: LiveView embedded schema hidden_input missing
- track: bohrbug-core
- difficulty: medium
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: false
- tags: liveview, embedded-schema, hidden_input, inputs_for, cast_embed, form

## Ground Truth

- root_cause: The `country` field is required by the backend but not shown in the form. Without a `<.input type="hidden" field={addr_form[:country]} />`, the `country` field is not included in the form submission params. `cast_embed/3` receives `%{"street" => "...", "city" => "..."}` with no `country` key. Depending on the validation rules, this either causes the embedded changeset to be invalid (silently failing if the case is not handled) or the entire embed is dropped.

  More commonly: the `_persistent_id` or `id` field of the embedded schema is also missing without a hidden input. Phoenix LiveView uses these internal fields to track which embedded record to update. Without them, `cast_embed` may not correctly associate the params with the existing embedded record and may drop the entire embed.

- why_it_happens: `inputs_for` generates the correct form structure and IDs for embedded schemas. But any field not rendered as an input (visible or hidden) will not be submitted in the form params. `cast_embed` only receives the fields that were in the params.
- accepted_fix: Add `<.input type="hidden" field={addr_form[:country]} />` inside the `inputs_for` block. For the `_persistent_id` field, `inputs_for` may add it automatically in newer versions — but any backend-managed field must have a hidden input.
- rejected_fix_patterns:
  - set country in handle_event after receiving params (works, but is a workaround)
  - use a separate changeset step outside the form (workaround)

## Evidence Signals

- strongest_signal: embeds_one used; field intentionally not in form template; address always nil/empty
- pathognomonic_prove: IO.inspect(params, label: "[HIDDEN-INPUT-PROVE]") in handle_event — shows params["order"]["shipping_address"] as %{"street" => "...", "city" => "..."} with no "country" key; or entire shipping_address key missing
- strongest_alternative_explanation: cast_embed not called in changeset
- why_alternative_is_wrong: Changeset code shows cast_embed(:shipping_address, required: true) — it is called; the issue is the params received, not the changeset code

## Scoring Notes

- full_credit_conditions:
  - identifies missing hidden_input for country field in embedded schema form
  - explains that fields not in the form are not submitted in params
  - fix adds <.input type="hidden" field={addr_form[:country]} />
  - mentions IO.inspect params Prove
- partial_credit_conditions:
  - identifies the missing field but suggests setting it in handle_event instead
- fail_conditions:
  - suggests the schema or changeset is wrong
  - recommends using a regular field instead of embedded schema
