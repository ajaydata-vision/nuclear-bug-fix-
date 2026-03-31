# WF-003: Authentication Is Null Inside WebFlux Service Method

## User Prompt

Our Spring Boot WebFlux application loses the authenticated user inside a reactive service call. SecurityContextHolder.getContext().getAuthentication() returns null inside the service, even though Spring Security has correctly authenticated the request. The same pattern works in our Spring MVC services.

## Context Provided To The Skill

- stack: Java 17, Spring Boot 3.2.1, Spring WebFlux, Spring Security 6.2
- environment: local and production, fully reproducible
- logs:
  - [DEBUG] Security: Authentication set for user=alice
  - [WARN]  OrderService: authentication is null — cannot get userId
- code excerpt:
```java
@Service
public class OrderService {
    public Mono<Order> createOrder(OrderDto dto) {
        // MVC pattern — fails in WebFlux
        Authentication auth = SecurityContextHolder.getContext().getAuthentication();
        if (auth == null) {
            log.warn("authentication is null — cannot get userId");
            return Mono.error(new AccessDeniedException("not authenticated"));
        }
        return orderRepo.save(new Order(auth.getName(), dto));
    }
}
```
- reproduction:
  1. Authenticated request hits WebFlux endpoint
  2. Controller calls orderService.createOrder()
  3. SecurityContextHolder.getContext() returns empty context
  4. auth is null despite valid JWT processed by Spring Security
