# JV-013: JNDI DataSource Not Found in Tomcat — Works in Spring Boot Tests

## User Prompt

Our servlet application looks up a DataSource via JNDI at runtime. The lookup throws NameNotFoundException in Tomcat. The same code works fine in our Spring Boot integration tests. What is wrong with the JNDI configuration?

## Context Provided To The Skill

- stack: Java 17, Tomcat 10.1.18, JNDI, PostgreSQL JDBC driver
- environment: Tomcat WAR deployment
- logs:
  - javax.naming.NameNotFoundException: Name [jdbc/appDB] is not bound in this Context
  -   at org.apache.naming.NamingContext.lookup(NamingContext.java:861)
  -   at com.example.DatabaseUtil.getDataSource(DatabaseUtil.java:22)
- code excerpt:
```java
// DatabaseUtil.java
public static DataSource getDataSource() throws NamingException {
    InitialContext ctx = new InitialContext();
    return (DataSource) ctx.lookup("jdbc/appDB");  // ← fails in Tomcat
}
```
```xml
<!-- context.xml (in META-INF/) -->
<Context>
    <Resource name="jdbc/appDB"
              type="javax.sql.DataSource"
              driverClassName="org.postgresql.Driver"
              url="jdbc:postgresql://localhost/appdb"
              username="app" password="secret"
              maxTotal="20"/>
</Context>
```
```xml
<!-- web.xml missing <resource-ref> -->
```
- reproduction:
  1. Deploy WAR to Tomcat
  2. First database call → NameNotFoundException: Name [jdbc/appDB] not bound
  3. Same code in Spring Boot test (which doesn't use JNDI) passes
