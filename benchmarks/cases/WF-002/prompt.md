# WF-002: WebFlux GET Returns 200 With Empty Body for Missing Resources

## User Prompt

Our Spring WebFlux API returns HTTP 200 with an empty body when a product ID does not exist. It should return 404. Clients are silently failing to parse the empty response. What is wrong?

## Context Provided To The Skill

- stack: Java 17, Spring Boot 3.2.1, Spring WebFlux, Spring Data R2DBC
- environment: local and production, fully reproducible
- logs: no errors — 200 responses logged normally
- code excerpt:
```java
@GetMapping("/products/{id}")
public Mono<ProductDto> getProduct(@PathVariable Long id) {
    return productRepo.findById(id)   // returns Mono.empty() when not found
                      .map(ProductMapper::toDto);
}
```
- reproduction:
  1. GET /products/99999 (non-existent)
  2. Expected: HTTP 404
  3. Actual: HTTP 200, Content-Length: 0, empty body
  4. Client JSON parser throws NullPointerException on empty response
