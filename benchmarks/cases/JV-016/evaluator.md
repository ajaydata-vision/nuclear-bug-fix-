# Evaluator

## Metadata

- id: JV-016
- domain: java-enterprise
- track: regression-version
- difficulty: medium
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: false
- tags: jsp, jstl, taglib, jakarta-ee, spring-boot-3, migration, javax-to-jakarta

## Ground Truth

- root_cause: The `taglib` URI `http://java.sun.com/jsp/jstl/core` is the legacy javax namespace URI. Spring Boot 3 requires Jakarta EE 9+, which uses `jakarta.servlet.jsp.jstl` JAR. That JAR's TLD declares its URI as `jakarta.tags.core` — not `http://java.sun.com/jsp/jstl/core`. The JSP container cannot resolve the old URI to any installed TLD, so it silently treats `<c:forEach>` as an unknown custom tag and renders it as literal text.
- why_it_happens: Jakarta EE 9 renamed all `javax.*` packages and corresponding TLD URIs. The installed JAR (`jakarta.servlet.jsp.jstl 3.0.1`) registers the tag library under the new URI `jakarta.tags.core`. The JSP declares `uri="http://java.sun.com/jsp/jstl/core"` which matches no installed TLD. The container does not throw an error for an unresolvable taglib — it silently ignores the prefix, causing tags to render as unknown XML/HTML text.
- accepted_fix: Change the `taglib` URI in every affected JSP from `http://java.sun.com/jsp/jstl/core` to `jakarta.tags.core`. Similarly update any `fmt`, `sql`, `fn` taglibs from their legacy URIs to `jakarta.tags.format`, `jakarta.tags.sql`, `jakarta.tags.functions`.
- rejected_fix_patterns:
  - downgrade the jstl JAR to version 1.2 (incompatible with Jakarta EE 9 — uses javax namespace)
  - add the javax jstl dependency alongside the jakarta one (class/TLD conflict)
  - wrap JSTL tags in scriptlets as a workaround

## Evidence Signals

- strongest_signal: Tags render as literal text after Spring Boot 2→3 migration; JAR is `jakarta.servlet.jsp.jstl` 3.0.1 (Jakarta EE 9); taglib URI in JSP is still the legacy javax URI
- strongest_alternative_explanation: The `jakarta.servlet.jsp.jstl` JAR is not on the classpath at runtime, so no TLD is found
- why_alternative_is_wrong: If the JAR were absent, the same literal-text rendering would occur BUT the behavior would have been broken before the migration too (the old javax jstl JAR was also present in Spring Boot 2.7). The bug is specifically triggered by the migration: the new JAR uses a different TLD URI. The JAR presence can be verified with `mvn dependency:tree` — it IS present, just registered under a different URI.

## Scoring Notes

- full_credit_conditions:
  - identifies URI mismatch between legacy `http://java.sun.com/jsp/jstl/core` and Jakarta `jakarta.tags.core` as root cause
  - explains that the container silently ignores unresolvable taglib URIs (no error thrown)
  - prescribes updating URI in all affected JSPs
- partial_credit_conditions:
  - correctly identifies taglib URI issue but only fixes the core taglib without mentioning fmt/fn taglibs
  - identifies the migration as the trigger but prescribes downgrading the JAR
- fail_conditions:
  - recommends adding a web.xml taglib mapping
  - suggests the JAR is missing from classpath as the fix
  - recommends reverting to Spring Boot 2.7
