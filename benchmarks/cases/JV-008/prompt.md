# JV-008: User B Gets User A's Authentication Token in Logs

## User Prompt

Our Spring Boot API has a serious security issue. Under concurrent load, we see User A's userId appearing in log lines for User B's requests. Our MDC logging context is leaking between requests. All security checks pass correctly — only the logging context is wrong. But we are worried the issue is deeper.

## Context Provided To The Skill

- stack: Java 17, Spring Boot 3.2.1, SLF4J 2.0, Logback 1.4, Tomcat 10.1
- environment: production, concurrent load (50+ req/sec)
- logs:
  - 2025-01-15 10:00:01 [http-nio-8080-exec-3] userId=441 GET /orders  ← User 441
  - 2025-01-15 10:00:01 [http-nio-8080-exec-3] userId=441 GET /profile ← Different request, WRONG userId
  - 2025-01-15 10:00:01 [http-nio-8080-exec-4] userId=882 GET /orders  ← User 882, correct
- code excerpt:
```java
@Component
public class MdcFilter implements Filter {
    public void doFilter(ServletRequest req, ServletResponse res, FilterChain chain)
            throws IOException, ServletException {
        HttpServletRequest http = (HttpServletRequest) req;
        String userId = extractUserId(http);
        MDC.put("userId", userId);
        chain.doFilter(req, res);
        // MDC.clear() is missing here
    }
}
```
- reproduction:
  1. Send concurrent requests from multiple users
  2. Observe: exec-3 handles User 441, sets MDC
  3. exec-3 returned to pool, MDC not cleared
  4. exec-3 picks up User 882's request
  5. Log shows userId=441 for User 882's request
