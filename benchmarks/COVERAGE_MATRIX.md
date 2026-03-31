# Coverage Matrix

This matrix is the fastest way to grow a high-value benchmark suite without
adding random cases.

## Domain Coverage

| Domain | Benchmark Families | Target Cases |
|---|---|---:|
| Frontend | rendering, hydration, state, routing, forms, async data, websocket, build, browser compatibility, performance | 30 |
| Backend | request handling, auth, database, ORM, jobs, uploads, session, rate limit, observability, external API | 30 |
| Integration | webhooks, queues, microservices, ETL, CI/CD, gateway, service mesh, data consistency | 30 |
| Mobile | React Native bridge, iOS/Android differences, permissions, push, offline sync, ANR, memory, deep linking | 20 |
| General | async, race, env/config, timezone, encoding, caching, memory, algorithmic edge cases | 25 |
| Version / External Intelligence | dependency regression, browser support, RFC mismatch, CVE, compatibility matrix, runtime minimum version | 20 |

## Track Coverage

| Track | What It Tests | Target Cases |
|---|---|---:|
| Bohrbug core | deterministic, reproducible, one primary cause | 40 |
| Regression / version | behavior changed after update or documented framework change | 20 |
| Deploy / environment | wrong build, wrong env vars, stale assets, partial rollout, wrong instance | 20 |
| Intermittent / race | timing, load, startup, shared state, flaky tests | 20 |
| Distributed / multi-factor | duplicate processing, replica lag, gateway stripping, service drift, saga failures | 20 |
| Evidence-limited | only logs, stack trace, or symptom text available | 20 |

## Cross-Cutting Axes

Every mature suite should deliberately mix these axes:

| Axis | Values |
|---|---|
| Determinism | deterministic, intermittent |
| Evidence level | full code + logs, partial code, logs only, symptom only |
| Access level | local runtime access, no runtime access, no code access |
| Root cause class | code defect, version issue, config drift, deploy issue, protocol violation, architecture issue |
| Fix scope | one-line fix, local block fix, config fix, dependency pin/upgrade, infrastructure fix |
| Verification type | unit test, integration test, load run, replay, log assertion, manual repro |
| Risk of false confidence | low, medium, high |

## Supported Stack Families To Prioritize

- React
- Next.js
- Vue
- Angular
- Vite
- Express
- NestJS
- Django
- FastAPI
- Spring Boot
- PostgreSQL
- Redis
- RabbitMQ
- Kafka
- Docker
- Kubernetes
- Nginx
- React Native

## Case Distribution Rule

Do not let one stack dominate the suite. Keep at least:

- `40%` generic patterns
- `40%` stack-specific patterns
- `20%` version, deploy, or distributed environment cases


## Java Enterprise Domain (Added v1.4)

| Domain | Benchmark Families | Target Cases |
|---|---|---|
| Java Enterprise | servlet lifecycle/threading, JSP scope/include/EL, NIO ByteBuffer/Channel/Selector, Java threading (ThreadLocal/Interrupt/Executor/wait-notify), JVM ClassLoader/OOM, JDBC/HikariCP/JNDI, Spring Boot (@Transactional/Hibernate/bean-scope/Security) | 20 |

### Java Stack Families Added to Priority List

- Java Servlets (Tomcat 9/10, JBoss/WildFly)
- JSP / Jakarta Server Pages
- java.nio.channels (NIO — non-blocking I/O)
- Java Threading (synchronized, volatile, Executor, ThreadLocal)
- Spring Boot 3.x
- Spring Security 6.x
- Hibernate / JPA 3.x
- HikariCP connection pooling
- JNDI (Java Naming and Directory Interface)

## Python Desktop / Bridge / Packaging Domains (Added post-1.4.1)

| Domain | Benchmark Families | Target Cases |
|---|---|---|
| Python Desktop / UI | PyQt6 widgets, qasync loop ownership, async slots, UI freezes, thread affinity, desktop scheduler/websocket interaction | 12 |
| Bridge / Adapter / Unofficial Client | Python-to-Node subprocesses, stdout protocol framing, Baileys lifecycle, websocket relay ordering, scraper/provider drift | 12 |
| Frozen / Packaged Runtime | PyInstaller onefile/onedir, _MEIPASS, hidden imports, Qt plugins, writable paths, bundled helpers | 12 |

### Additional Stack Families To Prioritize

- PyQt6
- qasync
- PyInstaller
- Baileys / WhatsApp bridge adapters
- Python desktop local-agent runtimes
