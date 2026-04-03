# Verification

## Before Fix
- JSP renders JSTL tags as visible literal text
- `<c:forEach items="${products}" var="p">` appears on screen verbatim
- No runtime exception, no compilation error

## After Fix
Update the taglib declaration in every affected JSP:
```jsp
<%-- OLD (javax — works on Spring Boot 2 / Tomcat 9 / Jakarta EE 8) --%>
<%@ taglib uri="http://java.sun.com/jsp/jstl/core" prefix="c" %>

<%-- NEW (jakarta — required for Spring Boot 3 / Tomcat 10 / Jakarta EE 9+) --%>
<%@ taglib uri="jakarta.tags.core" prefix="c" %>
```
Update all used tag libraries:
```jsp
<%@ taglib uri="jakarta.tags.format"    prefix="fmt" %>
<%@ taglib uri="jakarta.tags.functions" prefix="fn"  %>
<%@ taglib uri="jakarta.tags.sql"       prefix="sql" %>
```
1. Restart application
2. `/products` page: `<c:forEach>` iterates correctly, products display
3. EL expressions `${p.name}` resolve correctly alongside JSTL tags

## Regression Checks
- All JSP pages using JSTL: verify none still reference the old `http://java.sun.com/jsp/jstl/core` URI
- `fmt:formatDate`, `fn:length`, other tag functions: confirm they use jakarta URIs
- Spring Boot 2 if still maintained in parallel: old URIs still required there — do not backport the jakarta URI change
