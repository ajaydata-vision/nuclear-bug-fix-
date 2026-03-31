# Evaluator

## Metadata

- id: JV-015
- domain: java-enterprise
- track: bohrbug-core
- difficulty: medium
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: spring, prototype, scope, singleton, autowired, bean-scope

## Ground Truth

- root_cause: @Scope("prototype") on ReportGenerator does not cause a new instance to be injected every time it is used. Spring resolves @Autowired dependencies at bean creation time for singleton beans. ReportService is a singleton — created once at startup. At that moment, one ReportGenerator instance is created and injected. All subsequent calls to buildReport() use the same ReportGenerator instance, accumulating rows.
- why_it_happens: Spring's dependency injection resolves @Autowired at bean instantiation time, not at method call time. For singleton beans, this is a one-time resolution. @Scope("prototype") means "create a new instance each time the bean is requested from the container" — but @Autowired into a singleton requests it only once.
- accepted_fix: Use ObjectFactory or ApplicationContext to request a fresh prototype on each call:
  @Autowired ObjectFactory<ReportGenerator> generatorFactory;
  public Report buildReport() { generatorFactory.getObject().addRow(...); }
  Or use @Lookup method injection. Or refactor ReportGenerator to be stateless.
- rejected_fix_patterns:
  - add @Scope("prototype") to ReportService (makes service prototype too — breaks other injections)
  - reset rows list at start of generate() (treats symptom, not root cause — not thread-safe)

## Evidence Signals

- strongest_signal: identityHashCode identical across two report generations; @Autowired used in singleton ReportService for prototype ReportGenerator; rows accumulate across calls
- strongest_alternative_explanation: @Scope("prototype") annotation not being processed (Spring AOP proxy issue)
- why_alternative_is_wrong: If @Scope were not processed, the bean would still be a singleton by default — same observable behavior. The root cause is that even with @Scope("prototype") correctly processed, @Autowired into a singleton resolves only once.

## Scoring Notes

- full_credit_conditions:
  - identifies @Autowired resolving prototype only once at singleton creation
  - explains Spring DI timing for singleton beans
  - proposes ObjectFactory, ApplicationContext.getBean(), or @Lookup
- partial_credit_conditions:
  - identifies same instance as problem but proposes resetting state rather than getting new instance
- fail_conditions:
  - suggests @Scope("prototype") is broken in this Spring version
  - recommends making ReportService a prototype bean
