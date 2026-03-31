# Verification

## Before Fix
footer.jsp modified; main.jsp uses <%@ include file %>; old footer still served

## After Fix
1. Replace <%@ include file="/WEB-INF/includes/footer.jsp" %> with <jsp:include page="/WEB-INF/includes/footer.jsp"/>
2. Deploy; new footer with privacy link appears immediately
3. Subsequent changes to footer.jsp appear on next request without any main.jsp touch

## Regression Checks
- Footer renders correctly on all pages that include it
- Dynamic content in footer (if any) resolves correctly at runtime
- Performance: runtime include adds one internal dispatch per request (acceptable)
