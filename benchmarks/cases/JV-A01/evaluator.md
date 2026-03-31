# Evaluator

## Metadata

- id: JV-A01
- domain: java-enterprise
- track: intermittent-race
- difficulty: hard
- determinism: intermittent
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: servlet, singleton, instance-variable, thread-safety, tomcat, race-condition

## Ground Truth

- root_cause: HttpServlet is a singleton — Tomcat creates one CartServlet instance and routes all concurrent requests through it on different threads. The instance variables `cart` and `currentUser` are shared across all concurrent requests, causing cross-user data contamination.
- why_it_happens: The Servlet specification (Section 2.2) states that a servlet container may maintain only a single instance of a servlet per deployment. All concurrent requests share that instance and its fields. Thread A sets `currentUser` and `cart` for User 9182; Thread B sets them for User 7703; Thread A's `doGet` reads the values Thread B just wrote.
- accepted_fix: Remove `cart` and `currentUser` as instance variables. Store per-request state as local variables in each method or as HttpServletRequest attributes. Use HttpSession for per-user persistent state.
- rejected_fix_patterns:
  - add synchronized keyword to doGet/doPost (serializes all requests — fixes race but kills concurrency)
  - move cart to HttpSession (correct for cart persistence, but currentUser should still be local)
  - add ThreadLocal (over-engineered — local variables are the correct fix for per-request state)

## Evidence Signals

- strongest_signal: Bug appears only under concurrent load, never in single-user testing; both users have valid sessions (ruling out session bug); instance variables `cart` and `currentUser` declared at class level
- strongest_alternative_explanation: HttpSession shared between users due to session fixation or URL rewriting
- why_alternative_is_wrong: Logs confirm both users have distinct valid sessions (userId=9182 and userId=7703 logged separately); session attributes are correct — the contamination is at the servlet instance field level, not the session level

## Scoring Notes

- full_credit_conditions:
  - identifies servlet singleton model as root cause
  - identifies instance variables cart and currentUser as the shared mutable state
  - proposes moving state to local variables or request attributes
  - explains that Tomcat reuses the single servlet instance across threads
- partial_credit_conditions:
  - identifies thread-safety issue but proposes synchronized (works but wrong approach)
  - identifies session as the fix location without explaining the servlet singleton cause
- fail_conditions:
  - blames Tomcat session management
  - blames network load balancer or caching
  - suggests adding more Tomcat threads as the fix
