# Evaluator

## Metadata

- id: JV-019
- domain: java-enterprise
- track: bohrbug-core
- difficulty: easy
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: jsp, servlet, post-redirect-get, prg, forward, redirect, double-submit, idempotency

## Ground Truth

- root_cause: The servlet uses `RequestDispatcher.forward()` after processing the POST. A forward is a server-side operation — the browser's URL bar remains at the POST endpoint (`/orders`). When the user presses F5, the browser sees a POST URL and offers to resubmit the form data. Clicking "Continue" replays the original POST, creating a second order. A redirect would have changed the browser URL to a GET endpoint, making F5 a safe re-request of the GET.
- why_it_happens: `forward()` hands off the request internally without a round trip to the browser. The browser is unaware a new resource was rendered — it still has the original POST in its history. `sendRedirect()` sends HTTP 302 to the browser, which then makes a new GET request to the redirect URL. F5 refreshes the GET, which is idempotent and safe. This is the POST-Redirect-GET (PRG) pattern.
- accepted_fix: After creating the order, store the order ID in the session (or pass it as a query parameter), issue `response.sendRedirect(request.getContextPath() + "/confirmation?orderId=" + order.getId())`, and serve the confirmation page from a GET handler or confirmation JSP. `req.setAttribute("order", order)` data is lost across the redirect — use session or query param instead.
- rejected_fix_patterns:
  - add JavaScript to disable the submit button (client-side only — does not prevent server-side resubmission)
  - use a database unique constraint as the only defence (correct as a backstop but does not fix the UX problem or remove the "Resend" prompt)
  - keep forward() and add a session-based token check (adds complexity; PRG is the standard solution)

## Evidence Signals

- strongest_signal: Browser URL remains at `/orders` (POST URL) after confirmation displays — the "Confirm Form Resubmission" dialog on F5 is the definitive proof of forward-not-redirect; `RequestDispatcher.forward()` visible in servlet code
- strongest_alternative_explanation: The order service itself is not idempotent and accepts duplicate submissions because no idempotency key is checked
- why_alternative_is_wrong: Non-idempotency of the order service is a contributing factor but not the root cause of the duplicate submission mechanism. The browser only replays the POST because the URL did not change — that is the forward's fault. Even with an idempotent service, the browser prompts and the user experience is broken. The PRG pattern prevents the replay; idempotency is a safety net for failures, not the primary fix.

## Scoring Notes

- full_credit_conditions:
  - identifies forward() as root cause — browser URL stays at POST endpoint, enabling F5 resubmission
  - names POST-Redirect-GET (PRG) pattern explicitly
  - prescribes sendRedirect() with data passed via session or query parameter
  - notes that req.setAttribute data is lost across a redirect and must be moved to session
- partial_credit_conditions:
  - correctly identifies the need for redirect but does not mention that req.setAttribute data is lost across the redirect
  - prescribes PRG correctly but also adds a synchroniser token as the primary fix (valid defence-in-depth but not the root cause fix)
- fail_conditions:
  - recommends client-side submit button disabling as the fix
  - blames the order service for not checking idempotency without addressing the browser resubmission mechanism
  - suggests using AJAX form submission without explaining why it helps
