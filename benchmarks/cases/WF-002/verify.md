# Verification

## Before Fix
GET /products/99999 → HTTP 200, empty body

## After Fix
```java
return productRepo.findById(id)
    .switchIfEmpty(Mono.error(new ResponseStatusException(NOT_FOUND, "id=" + id)))
    .map(ProductMapper::toDto);
```
GET /products/99999 → HTTP 404 with error body

## Regression Checks
- Existing product: 200 with full DTO
- Non-existent product: 404 with message "id=99999"
- Error body format matches GlobalExceptionHandler output
