# Verification

## Before Fix
50 concurrent requests → all reactor-http-nio threads blocked → hang

## After Fix
```java
return Mono.fromCallable(() -> jdbcRepo.findById(id).orElseThrow())
           .subscribeOn(Schedulers.boundedElastic())
           .map(ProductMapper::toDto);
```
50 concurrent requests → nio threads free → all respond

## Regression Checks
- BlockHound.install() in test: no BlockingOperationError on reactor threads
- 500 concurrent requests: bounded elastic scales, no hang
- Single request: still responds in <25ms
