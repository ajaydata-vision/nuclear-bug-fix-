# Evaluator

## Metadata

- id: JV-013
- domain: java-enterprise
- track: deploy-env
- difficulty: easy
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: jndi, datasource, tomcat, naming-exception, java-comp-env, web.xml, resource-ref

## Ground Truth

- root_cause: JNDI lookup in a servlet container requires the java:comp/env/ prefix to access the Enterprise Naming Context (ENC). ctx.lookup("jdbc/appDB") searches the global JNDI namespace where the resource is not bound. ctx.lookup("java:comp/env/jdbc/appDB") searches the component's ENC where Tomcat binds the context.xml Resource. Additionally, web.xml is missing the <resource-ref> declaration required to bridge the ENC.
- why_it_happens: Servlet containers bind resources into the component's ENC (java:comp/env/) not the global namespace. The java:comp/env/ prefix is mandatory for container-managed resources. Spring Boot tests don't use container JNDI at all (they use Spring's DataSource configuration directly), so the issue never surfaces in tests.
- accepted_fix: Change lookup to ctx.lookup("java:comp/env/jdbc/appDB"). Also add to web.xml: <resource-ref><res-ref-name>jdbc/appDB</res-ref-name><res-type>javax.sql.DataSource</res-type><res-auth>Container</res-auth></resource-ref>
- rejected_fix_patterns:
  - change context.xml Resource name to include java:comp/env/ prefix (Tomcat resource names don't use this prefix)
  - use Spring's JndiDataSourceLookup (correct tool, but doesn't explain why plain lookup fails)

## Evidence Signals

- strongest_signal: NameNotFoundException for "jdbc/appDB" (without prefix); context.xml correctly defines Resource; web.xml missing resource-ref; Spring Boot tests pass (use different DataSource mechanism)
- strongest_alternative_explanation: context.xml not being picked up by Tomcat (wrong location)
- why_alternative_is_wrong: If context.xml were not loaded, the error would be different. The resource exists — it is simply looked up at the wrong JNDI path (missing java:comp/env/ prefix).

## Scoring Notes

- full_credit_conditions:
  - identifies missing java:comp/env/ prefix as root cause
  - explains ENC vs global JNDI namespace
  - provides corrected lookup string and web.xml resource-ref
- partial_credit_conditions:
  - identifies JNDI path as wrong but does not explain ENC prefix requirement
- fail_conditions:
  - blames PostgreSQL JDBC driver not being in Tomcat lib
  - suggests restarting Tomcat
