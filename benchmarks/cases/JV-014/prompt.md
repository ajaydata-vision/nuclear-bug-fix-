# JV-014: Spring Security Custom JWT Filter Not Protecting Endpoints

## User Prompt

We added a custom JWT authentication filter to our Spring Boot API. The filter runs (we see log output), it validates the token correctly, and sets the Authentication in SecurityContextHolder. But the controller still receives a null principal. All endpoints behave as if unauthenticated. What is wrong?

## Context Provided To The Skill

- stack: Java 17, Spring Boot 3.2.1, Spring Security 6.2.1
- environment: local and production, fully reproducible
- logs:
  - [DEBUG] JwtFilter: Token valid for userId=441
  - [DEBUG] JwtFilter: Authentication set in SecurityContextHolder
  - [WARN]  AuthController: Principal is null — treating as anonymous
- code excerpt:
```java
// JwtFilter registered as @Component with @WebFilter("/*")
@Component
@WebFilter("/*")
public class JwtFilter extends OncePerRequestFilter {
    protected void doFilterInternal(HttpServletRequest req,
                                    HttpServletResponse res, FilterChain chain) {
        String token = extractToken(req);
        if (token != null && jwtService.isValid(token)) {
            Authentication auth = buildAuthentication(token);
            SecurityContextHolder.getContext().setAuthentication(auth);
            log.debug("Authentication set for userId={}", extractUserId(token));
        }
        chain.doFilter(req, res);
    }
}

// SecurityConfig
@Bean
public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
    http.authorizeHttpRequests(a -> a.anyRequest().authenticated());
    // JwtFilter NOT added via http.addFilterBefore(...)
    return http.build();
}
```
- reproduction:
  1. Send request with valid JWT
  2. JwtFilter log confirms token valid and authentication set
  3. Spring Security's own filters run AFTER and clear the SecurityContext
  4. Controller receives null principal
