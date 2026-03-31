# JV-012: ClassCastException in Tomcat but Works Fine in IDE

## User Prompt

Our web application works perfectly in IntelliJ IDEA with an embedded Tomcat. When deployed as a WAR to standalone Tomcat 10, we get ClassCastException at startup trying to cast a Logger object. Same code, same JDK. What is wrong?

## Context Provided To The Skill

- stack: Java 17, Tomcat 10.1.18, WAR deployment, SLF4J 2.0.9, Log4j2 2.22.0
- environment: standalone Tomcat 10, WAR deployment
- logs:
  - SEVERE: Exception starting filter LoggingFilter
  - java.lang.ClassCastException: class org.apache.logging.log4j.core.Logger
  -   cannot be cast to class org.apache.logging.log4j.core.Logger
  -   (org.apache.logging.log4j.core.Logger is in module org.apache.logging.log4j.core
  -    of loader 'app'; org.apache.logging.log4j.core.Logger is in module
  -    org.apache.logging.log4j.core of loader WebappClassLoader)
- code excerpt:
```xml
<!-- pom.xml dependencies -->
<dependency>
    <groupId>org.apache.logging.log4j</groupId>
    <artifactId>log4j-core</artifactId>
    <version>2.22.0</version>
    <!-- scope NOT set — defaults to 'compile', bundled in WAR -->
</dependency>
```
```
Tomcat lib/ directory also contains: log4j-core-2.22.0.jar (added by ops team)
```
- reproduction:
  1. Build WAR — log4j-core bundled in WEB-INF/lib
  2. Deploy to Tomcat with log4j-core also in $CATALINA_HOME/lib
  3. Two ClassLoaders each load log4j-core
  4. Cast between classes from different loaders fails
