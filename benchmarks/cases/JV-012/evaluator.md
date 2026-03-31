# Evaluator

## Metadata

- id: JV-012
- domain: java-enterprise
- track: deploy-env
- difficulty: hard
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: classloader, war, tomcat, classcastexception, log4j, provided-scope

## Ground Truth

- root_cause: log4j-core is present in both WEB-INF/lib (bundled in WAR, loaded by Tomcat's WebappClassLoader) and $CATALINA_HOME/lib (loaded by Tomcat's common ClassLoader). Two separate Class objects for org.apache.logging.log4j.core.Logger exist, one per ClassLoader. A cast between them fails even though the class names are identical.
- why_it_happens: Java ClassLoader isolation means two classes with identical names loaded by different ClassLoaders are different types — instanceof returns false, casts throw ClassCastException. The JVM error message gives the exact diagnostic: same class name, two different loaders.
- accepted_fix: Remove log4j-core from one location. If Tomcat provides it as a server library, mark it <scope>provided</scope> in Maven so it is not bundled in WEB-INF/lib. Alternatively, remove it from $CATALINA_HOME/lib and let each WAR bundle its own.
- rejected_fix_patterns:
  - upgrade log4j-core to same version in both places (still two ClassLoaders, still ClassCastException)
  - add log4j-core to $CATALINA_HOME/endorsed/ (deprecated mechanism, not the right fix)

## Evidence Signals

- strongest_signal: JVM error message explicitly states "loader 'app'" and "loader WebappClassLoader" — two different ClassLoaders loading the same class; log4j-core in both WEB-INF/lib and Tomcat lib/
- strongest_alternative_explanation: Version mismatch between log4j-core in WAR and Tomcat lib
- why_alternative_is_wrong: Version mismatch would cause NoSuchMethodError or NoClassDefFoundError, not ClassCastException. The ClassCastException with identical class names but different loaders is the definitive ClassLoader conflict signature.

## Scoring Notes

- full_credit_conditions:
  - identifies ClassLoader conflict (same class loaded by two different ClassLoaders)
  - explains that same class name from different ClassLoaders = different types
  - proposes removing from one location (<scope>provided</scope> or removing from Tomcat lib)
- partial_credit_conditions:
  - identifies the two copies as the problem but suggests version alignment as fix
- fail_conditions:
  - suggests downgrading Java version
  - blames Tomcat version incompatibility
