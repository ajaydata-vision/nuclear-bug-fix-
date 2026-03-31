# Evaluator

## Metadata

- id: JV-003
- domain: java-enterprise
- track: bohrbug-core
- difficulty: easy
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: false
- tags: jsp, include, compile-time, runtime, tomcat, translation

## Ground Truth

- root_cause: <%@ include file="..." %> is a compile-time (static) include. The content of footer.jsp is copy-pasted into main.jsp at JSP translation time. Tomcat only retranslates main.jsp when main.jsp itself is modified. Changes to footer.jsp are invisible until main.jsp is retranslated.
- why_it_happens: JSP translation converts .jsp files to Java servlets. The <%@ include file %> directive literally includes the file content at translation time — it is equivalent to copy-pasting. The resulting Java class has no dependency on footer.jsp at runtime. Only touching/modifying main.jsp (or clearing the work/ directory) triggers retranslation.
- accepted_fix: Switch to runtime include: <jsp:include page="/WEB-INF/includes/footer.jsp"/>. This directive is processed on every request, always reading the current footer.jsp content. As a one-time fix for the current deploy: touch main.jsp or delete Tomcat's work/ directory to force retranslation.
- rejected_fix_patterns:
  - redeploy the WAR again without touching main.jsp (does not trigger retranslation)
  - clear browser cache (server is serving old content, not a browser cache issue)

## Evidence Signals

- strongest_signal: File confirmed updated on disk; server still serving old content; <%@ include file="..." %> directive used (compile-time include)
- strongest_alternative_explanation: Tomcat serving cached/old WAR from work/ directory despite new deployment
- why_alternative_is_wrong: A new WAR deployment does clear the work/ directory for that app — but the newly deployed main.jsp is also unchanged, so Tomcat re-translates it from the same source and re-includes the current footer.jsp content... wait, actually this is a valid alternative: if the work/ directory was NOT cleared on redeployment. The key signal is <%@ include file which makes footer.jsp content baked in regardless.

## Scoring Notes

- full_credit_conditions:
  - identifies <%@ include file as compile-time include
  - explains that Tomcat only retranslates main.jsp when main.jsp changes
  - proposes switching to <jsp:include page> for runtime inclusion
- partial_credit_conditions:
  - suggests clearing Tomcat work/ directory (correct one-time fix but not root cause fix)
  - identifies the include type issue but proposes restarting Tomcat instead of switching include type
- fail_conditions:
  - blames browser caching
  - suggests CDN cache invalidation
