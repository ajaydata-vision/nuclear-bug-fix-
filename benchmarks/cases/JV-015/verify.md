# Verification

## Before Fix
Second report contains first report's rows; identityHashCode identical

## After Fix (ObjectFactory)
```java
@Autowired private ObjectFactory<ReportGenerator> generatorFactory;

public Report buildReport(Long userId) {
    ReportGenerator gen = generatorFactory.getObject(); // new instance each call
    gen.addRow(fetchRows(userId));
    return gen.generate();
}
```
Second report logs different identityHashCode; contains only its own rows

## Regression Checks
- 100 concurrent reports: each gets isolated ReportGenerator instance
- Memory: prototype instances are not retained by Spring — GC'd after use
- Thread safety: each call gets its own instance, no shared state
