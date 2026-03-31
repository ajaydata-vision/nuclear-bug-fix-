# Verification

## Before Fix
- Requests without session reach ProtectedServlet
- No AuthFilter log line appears
- Returns 200 instead of 401

## After Fix
1. Remove @WebFilter from AuthFilter
2. Add to web.xml before CorsFilter:
   <filter><filter-name>AuthFilter</filter-name>...</filter>
   <filter-mapping><filter-name>AuthFilter</filter-name><url-pattern>/*</url-pattern></filter-mapping>
3. Unauthenticated request → 401, AuthFilter log appears
4. Authenticated request → reaches ProtectedServlet

## Regression Checks
- OPTIONS preflight (CORS): should still pass through if CorsFilter handles it
- Authenticated user: full access to protected endpoints
- Public endpoints if any: verify they are excluded from filter mapping
