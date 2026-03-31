# Verification

## Before Fix
WAR deploy → ClassCastException at startup

## After Fix (Option A — use server-provided)
1. Add <scope>provided</scope> to log4j-core in pom.xml
2. Rebuild WAR — log4j-core absent from WEB-INF/lib
3. Deploy — single ClassLoader loads log4j-core, no conflict, starts cleanly

## After Fix (Option B — bundle in WAR only)
1. Remove log4j-core from $CATALINA_HOME/lib
2. Deploy — WebappClassLoader provides log4j-core, no conflict

## Regression Checks
- Verify: log4j-core present in exactly one location
- Logging works correctly after fix
- Other WARs on same Tomcat: if they also need log4j, each bundles its own (no sharing)
