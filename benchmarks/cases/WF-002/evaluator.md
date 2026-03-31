# Evaluator

## Metadata

- id: WF-002
- domain: java-enterprise
- track: bohrbug-core
- difficulty: easy
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: false
- tags: webflux, reactive, mono-empty, switchIfEmpty, 404, not-found, response-status

## Ground Truth

- root_cause: R2DBC repository.findById() returns Mono.empty() when the entity does not exist. Without switchIfEmpty(), the pipeline completes successfully with no value emitted. Spring WebFlux serializes a completed empty Mono as HTTP 200 with an empty body.
- why_it_happens: In reactive programming, an empty stream (Mono.empty()) is a valid successful completion — it is not an error. Spring WebFlux maps a completed Mono to 200 OK. Returning a 404 requires explicitly signaling an error condition, which switchIfEmpty() enables by substituting an error Mono.
- accepted_fix: Add .switchIfEmpty(Mono.error(new ResponseStatusException(HttpStatus.NOT_FOUND))) after findById().
- rejected_fix_patterns:
  - return Optional<ProductDto> instead of Mono (mixes reactive and non-reactive models)
  - add null check after .map() (map is never called on empty Mono — null never arrives)

## Evidence Signals

- strongest_signal: findById() returns Mono.empty() for not-found (R2DBC contract); no switchIfEmpty() in pipeline; 200 with empty body observed
- strongest_alternative_explanation: ProductMapper.toDto() returning null for some products
- why_alternative_is_wrong: map() is never invoked on Mono.empty() — a null return from toDto() would cause a NullPointerException inside map(), not a silent 200 empty body

## Scoring Notes

- full_credit_conditions:
  - identifies Mono.empty() completing as 200 OK as root cause
  - proposes switchIfEmpty(Mono.error(new ResponseStatusException(NOT_FOUND)))
- partial_credit_conditions:
  - suggests returning Optional or wrapping in ResponseEntity without switchIfEmpty
- fail_conditions:
  - blames R2DBC returning null
  - suggests adding @ResponseStatus(NOT_FOUND) to the controller class
