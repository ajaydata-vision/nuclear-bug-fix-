# WF-001: WebFlux API Hangs Completely Under Moderate Load

## User Prompt

Our Spring WebFlux REST API performs well for single users. When we reach 50 concurrent users it stops responding entirely. No errors logged. No timeouts thrown. Requests just hang indefinitely. The service is not hitting any DB or upstream timeout threshold. What is wrong?

## Context Provided To The Skill

- stack: Java 17, Spring Boot 3.2.1, Spring WebFlux, R2DBC is NOT used — using JDBC (JPA) inside reactive handlers
- environment: production, 50+ concurrent users
- logs: nothing — requests simply stop producing output
- code excerpt:
```java
@RestController
public class ProductController {
    @Autowired ProductRepository jdbcRepo;  // JPA repository, blocking

    @GetMapping("/products/{id}")
    public Mono<ProductDto> getProduct(@PathVariable Long id) {
        return Mono.just(jdbcRepo.findById(id).orElseThrow())  // blocking JDBC call
                   .map(ProductMapper::toDto);
    }
}
```
- reproduction:
  1. Single request: responds in 20ms
  2. 50 concurrent requests: all hang after ~10 requests complete
  3. Thread dump shows all reactor-http-nio-* threads in WAITING state on JDBC
  4. No exception thrown
