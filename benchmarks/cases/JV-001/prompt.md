# JV-001: Auth Filter Not Executing — Unauthenticated Requests Reach Protected Endpoints

## User Prompt

Our Java web application has an authentication filter but unauthenticated requests are reaching protected servlets. The filter works in isolation (unit tested). In production Tomcat deployment it is being bypassed. What is wrong?

## Context Provided To The Skill

- stack: Java 17, Tomcat 10.1.18, Jakarta Servlet 6.0, no Spring
- environment: production Tomcat deployment
- logs:
  - [INFO] ProtectedServlet: Processing request from user=null
  - [INFO] ProtectedServlet: userId=null, proceeding without auth check
  - (no AuthFilter log entries for these requests)
- code excerpt:
```java
// AuthFilter.java
@WebFilter("/*")
public class AuthFilter implements Filter {
    public void doFilter(ServletRequest req, ServletResponse res, FilterChain chain) {
        log.info("[AUTH-FILTER] checking request");
        HttpServletRequest http = (HttpServletRequest) req;
        if (http.getSession().getAttribute("userId") == null) {
            ((HttpServletResponse) res).sendError(401);
            return;
        }
        chain.doFilter(req, res);
    }
}

// web.xml (excerpt)
<filter>
    <filter-name>CorsFilter</filter-name>
    <filter-class>com.example.CorsFilter</filter-class>
</filter>
<filter-mapping>
    <filter-name>CorsFilter</filter-name>
    <url-pattern>/*</url-pattern>
</filter-mapping>

<!-- AuthFilter declared via @WebFilter annotation, not in web.xml -->
```
- reproduction:
  1. Send request without session cookie
  2. Expected: 401 from AuthFilter
  3. Actual: request reaches ProtectedServlet, no AuthFilter log line
  4. CorsFilter log lines appear correctly for same requests
