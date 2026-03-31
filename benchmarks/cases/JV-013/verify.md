# Verification

## Before Fix
ctx.lookup("jdbc/appDB") → NameNotFoundException

## After Fix
```java
return (DataSource) ctx.lookup("java:comp/env/jdbc/appDB");
```
Plus in web.xml:
```xml
<resource-ref>
    <res-ref-name>jdbc/appDB</res-ref-name>
    <res-type>javax.sql.DataSource</res-type>
    <res-auth>Container</res-auth>
</resource-ref>
```
First DB call succeeds, connection pool initializes from Tomcat-managed DataSource

## Regression Checks
- Multiple lookups: same DataSource instance returned (pool not re-created)
- Connection pool: maxTotal=20 respected
- App restart: JNDI re-initialized correctly
