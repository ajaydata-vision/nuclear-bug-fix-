# JV-015: Prototype Report Generator Always Reuses Same State

## User Prompt

Our Spring Boot service has a report generator that is supposed to be stateful and fresh for each report. We marked it @Scope("prototype"). But every report gets the same accumulated state — data from previous reports bleeds into new ones. What is wrong?

## Context Provided To The Skill

- stack: Java 17, Spring Boot 3.2.1
- environment: local and production, fully reproducible
- logs:
  - [INFO] ReportService: Generating report for user=441
  - [INFO] ReportGenerator: identityHashCode=24521612
  - [INFO] ReportService: Generating report for user=882
  - [INFO] ReportGenerator: identityHashCode=24521612  ← same instance!
- code excerpt:
```java
@Component
@Scope("prototype")
public class ReportGenerator {
    private List<Row> rows = new ArrayList<>();

    public void addRow(Row row) { rows.add(row); }

    public Report generate() {
        log.info("identityHashCode={}", System.identityHashCode(this));
        return new Report(rows);
    }
}

@Service
public class ReportService {
    @Autowired
    private ReportGenerator generator;  // injected once at service creation

    public Report buildReport(Long userId) {
        generator.addRow(fetchRows(userId));
        return generator.generate();
    }
}
```
- reproduction:
  1. Generate report for user 441
  2. Generate report for user 882
  3. User 882's report contains user 441's rows plus user 882's rows
  4. Both reports log identical identityHashCode
