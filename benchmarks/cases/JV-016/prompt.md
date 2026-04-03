# JV-016: JSTL Tags Render As Literal Text On Screen — Not Processed

## User Prompt

We migrated our Spring Boot application from 2.7 to 3.2. Our JSP pages now show
the JSTL tags literally on screen instead of processing them. For example the page
renders `<c:forEach items="${products}" var="p">` as visible text instead of
iterating. The JSP compiles without error. The `jstl` dependency is in the
`pom.xml`. What changed?

## Context Provided To The Skill

- stack: Java 17, Spring Boot 3.2.3, Tomcat 10.1.19 (embedded), Jakarta Servlet 6.0
- versions: previously Spring Boot 2.7.18 with Tomcat 9
- environment: development and production, same behavior after migration
- logs:
  - No compilation errors
  - No runtime exceptions
  - Page renders with literal JSTL tag text visible to the user
- code excerpt:
```jsp
<%-- products.jsp --%>
<%@ page language="java" contentType="text/html; charset=UTF-8" %>
<%@ taglib uri="http://java.sun.com/jsp/jstl/core" prefix="c" %>
<!DOCTYPE html>
<html>
<body>
  <c:forEach items="${products}" var="p">
    <div>${p.name} - ${p.price}</div>
  </c:forEach>
</body>
</html>
```
```xml
<!-- pom.xml excerpt -->
<dependency>
    <groupId>org.glassfish.web</groupId>
    <artifactId>jakarta.servlet.jsp.jstl</artifactId>
    <version>3.0.1</version>
</dependency>
```
- reproduction:
  1. Run application with Spring Boot 3.2
  2. Navigate to `/products`
  3. Page body shows: `<c:forEach items="${products}" var="p"> <div>${p.name} - ${p.price}</div> </c:forEach>`
  4. Same JSP worked correctly on Spring Boot 2.7
