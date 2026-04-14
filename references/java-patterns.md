# Java Enterprise Bug Patterns

Covers: Servlet, JSP, NIO, Threading, JVM/ClassLoader, JDBC, Spring Boot.
Each pattern: symptom → why → prove → fix.

---

## CATEGORY 1 — SERVLET LIFECYCLE & THREADING

### Pattern: Mutable instance variable — cross-user data contamination
**Symptom:** Under concurrent load, User A sees User B's data. Never reproduces in testing (single user or low concurrency). Gets worse as traffic increases.
**Why:** `HttpServlet` is a singleton. The container creates one instance per deployment descriptor entry and routes all concurrent requests through it on different threads. Any field declared at the class level is shared across all concurrent requests simultaneously.
**Prove:** Add `log.debug("[SERVLET] threadId={} fieldValue={}", Thread.currentThread().getId(), instanceVar)` at the top of `doGet()`/`doPost()`. Under load, two different thread IDs will log conflicting values for the same field at the same time.
**Fix:** Remove all per-request state from instance fields. Move to:
- Local variables inside the method (disappear when method returns)
- `HttpServletRequest` attributes (`req.setAttribute("key", value)`)
- `HttpSession` attributes for user-scoped persistent state
**Safe instance fields:** `private final` constants, read-only injected services initialized in `init()`.
**Dead giveaway:** Any non-final field in a servlet class that is written in `doGet()`/`doPost()`.

### Pattern: Filter chain ordering — security check silently skipped
**Symptom:** Auth check not applied to certain routes. Works in unit tests where filter is applied manually. Bypassed in production.
**Why:** `web.xml` applies filters in declaration order. `@WebFilter` annotations have no guaranteed ordering across classes in the Servlet 3.x specification — Tomcat's ordering of `@WebFilter` annotated filters is unspecified. A filter calling `chain.doFilter()` without conditional logic always passes through regardless of order.
**Prove:** Put `log.debug("[AUTH-FILTER] reached for path={}", req.getRequestURI())` as the absolute first line of the auth filter. If a protected endpoint is reached without this log line → auth filter not in the chain.
**Fix:** Declare all filters explicitly in `web.xml` in correct order. Do NOT rely on `@WebFilter` for ordering — use `web.xml` `<filter>` and `<filter-mapping>` declarations. For Spring Security applications: configure `SecurityFilterChain` in Java config (see Category 7 — Spring Boot Patterns).

### Pattern: Response already committed — forward or redirect silently fails
**Symptom:** `IllegalStateException: Cannot call sendRedirect() after the response has been committed`. Or: redirect appears to do nothing. Or: `getWriter() has already been called for this response`.
**Why:** Once any byte is written to `HttpServletResponse` and the buffer flushes, headers are sent. `sendRedirect()` and `forward()` both set response headers, which is impossible after headers are already sent.
**Prove:** Add `log.debug("[RESPONSE] committed={}", response.isCommitted())` before the redirect/forward. If `true` → headers already sent upstream.
**Fix:** Restructure request handling:
1. Validate and make all routing decisions FIRST
2. Issue redirect/forward if needed
3. Only then write response body
Never write any output before the routing decision is made. If partial output must be written before a potential redirect: use `include()` not `forward()`.

### Pattern: AsyncContext never completed — request hangs forever
**Symptom:** Requests hang indefinitely. No error in logs. Client eventually times out. Only on certain code paths (usually error paths).
**Why:** `request.startAsync()` returns an `AsyncContext`. The container waits for `asyncContext.complete()` to be called. If an exception is thrown before `complete()`, the async context leaks — the container never closes the response.
**Prove:** Log at every `startAsync()` call and every `complete()` call with a matching ID. Count them. Any ID that appears in start but not in complete = leaked context.
**Fix:**
```java
AsyncContext async = request.startAsync();
async.setTimeout(30_000);
async.addListener(new AsyncListener() {
    public void onTimeout(AsyncEvent e) { async.complete(); }
    public void onError(AsyncEvent e) { async.complete(); }
    public void onStartAsync(AsyncEvent e) {}
    public void onComplete(AsyncEvent e) {}
});
executor.submit(() -> {
    try { doWork(async); }
    finally { async.complete(); }  // always in finally
});
```

---

## CATEGORY 2 — JSP LIFECYCLE & SCOPE

### Pattern: Wrong scope — session scope for per-request data bleeds across requests
**Symptom:** Data from one request (search results, form values, computed state) appears in a later request from the same user. Or across users if `applicationScope` was used.
**Why:** JSP has four scopes: `page` (current JSP only), `request` (current request only), `session` (user's entire session lifetime), `application` (all users, JVM lifetime). Storing per-request computation in `session` or `application` causes it to persist and contaminate later requests.
**Prove:** Add `${sessionScope}` dump to JSP output temporarily. Watch it accumulate values across requests that should be gone.
**Fix:**
```java
// Servlet — request scope for per-request data
request.setAttribute("results", results);    // gone after response
// JSP
${requestScope.results}

// Session scope ONLY for: userId, locale, shopping cart, login state
session.setAttribute("userId", user.getId());
```
Rule: If the data only makes sense for one HTTP request-response cycle, use `requestScope`.

### Pattern: Compile-time include — file changes invisible without restart
**Symptom:** An included JSP file was changed. Change has no effect. Previous content still appears. Restarting the server fixes it.
**Why:** Two entirely different include mechanisms:
- `<%@ include file="x.jsp" %>` — **compile-time**: content is copy-pasted into parent JSP at translation time. Parent retranslates only when it itself changes.
- `<jsp:include page="x.jsp"/>` — **runtime**: content is freshly included on every request.
**Prove:** Touch/save the PARENT JSP file (not the include). If content updates without restart → compile-time include confirmed (parent retranslated, picked up current include).
**Fix:** Switch to `<jsp:include page="x.jsp"/>` for any included file that changes independently. Reserve `<%@ include file %>` for truly static fragments that never change independently of the parent.

### Pattern: EL expression sees null — scriptlet variable not in attribute scope
**Symptom:** `${user.name}` renders as empty string. `<%= user.getName() %>` on the same page works. `user` is not null in the servlet.
**Why:** EL `${}` resolves names against request/session/application attributes — NOT against local Java scriptlet variables. A variable `User user = ...` inside a scriptlet is a local Java variable invisible to EL.
**Prove:** In a scriptlet, call `request.getAttribute("user")` and log the result. If null → servlet never set the attribute.
**Fix:**
```java
// In servlet — set attribute so EL can find it
request.setAttribute("user", userObject);
dispatcher.forward(request, response);
// In JSP — EL resolves from request attributes
${user.name}   // works
<%= ((User) request.getAttribute("user")).getName() %>  // also works
```

### Pattern: JSP compilation error vs runtime error — wrong diagnostic path
**Symptom:** HTTP 500 with cryptic stack trace referencing auto-generated class names. No line numbers matching actual JSP source.
**Why:** JSP errors occur at three stages with different diagnostics:
- Translation error (invalid JSP syntax) → shown at first request, stack references `org.apache.jasper`
- Java compilation error (generated Java is invalid) → similar to translation error
- Runtime error (valid code, throws at runtime) → references generated class; look in Tomcat `work/` directory
**Prove:** Match the stack trace:
- Contains `org.apache.jasper.JasperException` → translation/compilation error, fix JSP syntax
- Contains your generated servlet class (e.g., `index_jsp`) → runtime error, find generated source
**Fix for runtime errors:** Find generated source at `$CATALINA_HOME/work/Catalina/localhost/<app>/`. Map failing line in generated class back to JSP line. Fix the JSP logic.
**Fix for translation errors:** Fix JSP syntax. Check JSTL tag library declarations (`<%@ taglib ... %>`).

### Pattern: JSTL tag renders as literal text — taglib declaration missing or wrong URI
**Symptom:** `<c:forEach>`, `<c:if>`, `<c:out>` render on screen as plain text, not as processed output. Or: `javax.servlet.jsp.JspException: The absolute uri: http://java.sun.com/jsp/jstl/core cannot be resolved`.
**Why:** JSTL requires two things: (1) `<%@ taglib uri="..." prefix="c" %>` declaration at the top of the JSP, and (2) the JSTL JAR present in `WEB-INF/lib`. If either is missing, the container either ignores the tags (renders as text) or throws on resolution. Wrong URI is the most common cause — the exact URI string must match the TLD.
**Prove:** Three-step check — stop at the first step that identifies the problem:
1. **Declaration present?** Search every JSP file that shows the broken tags for `<%@ taglib`. If absent → missing declaration, add it.
2. **URI correct for your stack?** If declaration exists, check the `uri` value against your Jakarta EE version:
   - Spring Boot 2 / Jakarta EE 8: `uri="http://java.sun.com/jsp/jstl/core"` ← must match exactly
   - Spring Boot 3 / Jakarta EE 9+: `uri="jakarta.tags.core"` ← old URI will silently fail here
   Mismatch between URI in declaration and the JAR version in `WEB-INF/lib` = tags silently ignored.
3. **JAR present?** Check `WEB-INF/lib` for `jstl-*.jar` + `standard-*.jar` (JSTL 1.x) or `jakarta.servlet.jsp.jstl-*.jar` (Jakarta EE 9+). If absent → dependency missing.
**Fix:**
```jsp
<%-- Top of every JSP that uses JSTL core tags --%>
<%@ taglib uri="http://java.sun.com/jsp/jstl/core" prefix="c" %>
<%-- For Jakarta EE 9+ (Spring Boot 3): --%>
<%@ taglib uri="jakarta.tags.core" prefix="c" %>
```
Dependency (Maven):
```xml
<!-- JSTL 1.x (Jakarta EE 8 / Spring Boot 2) -->
<dependency><groupId>javax.servlet</groupId><artifactId>jstl</artifactId><version>1.2</version></dependency>
<!-- Jakarta EE 9+ (Spring Boot 3) -->
<dependency><groupId>org.glassfish.web</groupId><artifactId>jakarta.servlet.jsp.jstl</artifactId><version>3.0.1</version></dependency>
```

### Pattern: JSP forward vs redirect — wrong choice causes data loss or double-submit
**Symptom:** After form submission, refreshing the page resubmits the form (double-submit). Or: servlet processes the request, forwards to JSP, but URL in browser still shows the old servlet URL. Or: `request.getAttribute()` returns null in the JSP after a redirect.
**Why:** Two fundamentally different mechanisms:
- `RequestDispatcher.forward(req, resp)` — server-side hand-off. Same request object, same URL in browser, attributes preserved. No new HTTP round trip.
- `response.sendRedirect(url)` — tells browser to make a new GET request. New request object, URL changes in browser, request attributes lost.
**Prove:** Two checks, one for each symptom:
- **Double-submit test:** After submitting the form, immediately press **F5** (refresh) without navigating away. If the browser shows a "Confirm Form Resubmission" / "Resend POST data?" dialog → the server used `forward()` instead of `redirect()`. A correct PRG implementation never shows this prompt because the final response is a GET.
- **URL check:** After submission, look at the browser URL bar. If it still shows the servlet's POST URL (e.g., `/submitOrder`) → forward. If it changed to a new URL (e.g., `/order/success`) → redirect. For data loss: add `log.debug("[FORWARD] attr=", request.getAttribute("results"))` at the top of the JSP — if null after a redirect, the attribute was lost.
**Fix:**
```java
// POST form handler — use redirect to prevent double-submit (PRG pattern)
response.sendRedirect(request.getContextPath() + "/success");

// Internal render (passing data from servlet to JSP) — use forward
request.setAttribute("results", results);
RequestDispatcher rd = request.getRequestDispatcher("/WEB-INF/views/results.jsp");
rd.forward(request, response);
// Note: data passed via request.setAttribute is LOST after sendRedirect
// Use session.setAttribute for data that must survive a redirect
```

### Pattern: JSP EL output unescaped — user input breaks HTML or creates XSS
**Symptom:** Page displays raw HTML tags from user input. Or: input with `<script>` tags executes JavaScript. Or: apostrophes in names break page layout.
**Why:** EL expressions `${expr}` do NOT HTML-encode output. If `expr` contains `<`, `>`, `&`, `"`, or `'`, these render as raw HTML, breaking layout or enabling XSS. This is the most common JSP security vulnerability.
**Prove:** Enter `<b>bold</b>` into any user-controlled text field. If the output page renders bold text instead of showing the literal characters → EL is not escaping.
**Fix:**
```jsp
<%-- WRONG — XSS vulnerable --%>
${user.name}

<%-- CORRECT — HTML-encodes output --%>
<c:out value="${user.name}"/>

<%-- CORRECT for inline use — escapeXml is true by default --%>
<c:out value="${user.comment}" escapeXml="true"/>

<%-- Spring MVC equivalent — always use fn:escapeXml or c:out --%>
${fn:escapeXml(user.name)}
```
Rule: NEVER use `${expr}` for any value that originates from user input. Always use `<c:out value="${expr}"/>`. Reserve bare `${expr}` for values you fully control (enum constants, hard-coded strings, numeric IDs).

---

## CATEGORY 3 — NIO: ByteBuffer, Channels, Selectors

### Pattern: ByteBuffer.flip() not called — channel.write() sends nothing
**Symptom:** NIO server logs write completing without error. Client receives 0 bytes or garbage data.
**Why:** After `buffer.put(data)`, position is at end of data, limit is at capacity. `channel.write(buffer)` reads from position to limit — an empty range. `flip()` sets `limit = position`, `position = 0`, making data available for reading.
```
After allocate(1024):     position=0,    limit=1024
After put(100 bytes):     position=100,  limit=1024
Without flip():           reads [100..1024] = 0 bytes / garbage
After flip():             position=0,    limit=100  ← correct
```
**Prove:** Log `buffer.position()`, `buffer.limit()`, `buffer.remaining()` before `channel.write()`. If `remaining() == 0` → flip was not called.
**Fix:** Call `buffer.flip()` immediately before every `channel.write()` call. Protocol: write into buffer → `flip()` → send via channel → `clear()` or `compact()`.

### Pattern: ByteBuffer.clear() instead of compact() — unread bytes silently dropped
**Symptom:** NIO proxy or relay drops bytes intermittently under load. Messages arrive truncated at variable lengths. No exception.
**Why:** `clear()` sets `position=0`, `limit=capacity` — discards any unread bytes. `compact()` copies unread bytes to buffer start, sets position after them — preserving unread data.
- `clear()` correct when: buffer is fully drained (`!buffer.hasRemaining()`)
- `compact()` correct when: buffer may have partial data remaining
**Prove:** Log `buffer.remaining()` before calling `clear()`. If non-zero → data loss imminent.
**Fix:** In read-process-send loops, replace `buffer.clear()` with `buffer.compact()` after partial sends. Only use `clear()` after confirming `!buffer.hasRemaining()`.

### Pattern: Partial channel write — message truncation under load
**Symptom:** Under low concurrency: all messages arrive complete. Under load: messages randomly truncated at varying lengths. No exception thrown.
**Why:** `SocketChannel.write(buffer)` does NOT guarantee all bytes are written. Returns bytes actually written, which may be less than `buffer.remaining()` when the socket send buffer is full (common under load).
**Prove:** Log `channel.write(buffer)` return value AND `buffer.remaining()` after each write. Under load: return value < initial remaining = partial write.
**Fix:**
```java
while (buffer.hasRemaining()) {
    int written = channel.write(buffer);
    if (written == 0 && buffer.hasRemaining()) {
        // Socket buffer full — register OP_WRITE; selector notifies when writable
        key.interestOps(key.interestOps() | SelectionKey.OP_WRITE);
        pendingWrites.put(channel, buffer);
        break;
    }
}
```

### Pattern: SelectionKey not removed from selectedKeys — CancelledKeyException or duplicate processing
**Symptom:** NIO server throws `CancelledKeyException` inside the event loop. Or processes the same event twice per selector cycle. Happens on second iteration.
**Why:** `selector.selectedKeys()` returns a Set that the JDK adds keys to but NEVER removes from automatically. After processing, the key remains in the set. On next `select()`, if the key is cancelled, iterating it throws `CancelledKeyException`. If not cancelled, it is processed again as a stale entry.
**Prove:** Log `selectedKeys().size()` before and after your processing loop. If it never shrinks → keys not being removed.
**Fix:**
```java
Iterator<SelectionKey> iter = selector.selectedKeys().iterator();
while (iter.hasNext()) {
    SelectionKey key = iter.next();
    iter.remove();           // MANDATORY — JDK does not auto-remove
    if (!key.isValid()) continue;
    if (key.isReadable())  handleRead(key);
    if (key.isWritable())  handleWrite(key);
}
```

### Pattern: OP_WRITE left registered — selector loop spins at 100% CPU
**Symptom:** NIO server CPU at 100% with no load. Selector fires `OP_WRITE` events continuously. Throughput collapses.
**Why:** `OP_WRITE` fires continuously while the socket send buffer has space (almost always). It must only be registered when there is pending data to write, and removed immediately after the buffer drains.
**Prove:** Log how many times per second `key.isWritable()` fires. Thousands per second with no data to write → OP_WRITE left registered.
**Fix:**
```java
// Register OP_WRITE only when you have data waiting
key.interestOps(key.interestOps() | SelectionKey.OP_WRITE);

// After write drains the buffer completely:
key.interestOps(key.interestOps() & ~SelectionKey.OP_WRITE);
```

---

## CATEGORY 4 — JAVA THREADING PATTERNS

### Pattern: ThreadLocal not removed — request context leaks between users
**Symptom:** User A's security context, tenant ID, or MDC logging values appear in User B's request. Only under concurrent load. Never in unit tests. Critical security implication.
**Why:** Servlet containers and thread pools reuse threads. `ThreadLocal` values survive the end of a task unless explicitly removed with `ThreadLocal.remove()`. Thread T handles User A's request, sets `SecurityContextHolder` (a ThreadLocal). T returns to pool. T picks up User B's request. `SecurityContextHolder.getContext()` still returns User A's context.
Spring Security's `SecurityContextHolder`, SLF4J's MDC, and all tenant-routing middleware that use ThreadLocal are vulnerable.
**Prove:** In a filter, log `threadLocal.get()` at the START of each request BEFORE setting it. If it returns a non-null value → previous request's value leaked.
**Fix:**
```java
public void doFilter(ServletRequest req, ServletResponse res, FilterChain chain)
        throws IOException, ServletException {
    try {
        MyContext.set(resolve(req));
        chain.doFilter(req, res);
    } finally {
        MyContext.remove();   // ALWAYS in finally, never in try body
    }
}
// MDC: MDC.clear() in finally, not after business logic
// Spring Security handles this in SecurityContextPersistenceFilter automatically
```

### Pattern: InterruptedException swallowed — thread pool never shuts down
**Symptom:** Application hangs during shutdown. Container stop command times out. `jstack` shows worker threads in `TIMED_WAITING` inside your code.
**Why:** Thread pool shutdown interrupts worker threads. Worker catches `InterruptedException`, ignores it — the interrupted flag is cleared. The thread continues running. Pool cannot terminate.
**Prove:** `jstack <pid>`. Find threads named for your executor. If in `TIMED_WAITING` inside code with `catch(InterruptedException e) { log.warn(...); continue; }` → interrupt is swallowed.
**Fix:**
```java
try {
    doWork();
} catch (InterruptedException e) {
    Thread.currentThread().interrupt();  // RESTORE the interrupted flag
    return;  // or throw new RuntimeException(e) depending on context
}
```
Rule: `InterruptedException` may only be swallowed at the top of a thread's run loop. All other code MUST restore the flag.

### Pattern: Thread pool task silently rejected — work disappears under burst load
**Symptom:** Tasks submitted to `ExecutorService` disappear under burst load. No error logged. No exception at call site. Work simply does not happen.
**Why:** `ThreadPoolExecutor` with bounded queue and default `AbortPolicy` throws `RejectedExecutionException` when pool and queue are both full. If the caller does not catch it, the exception propagates and the task is dropped. `Executors.newFixedThreadPool()` uses an unbounded queue — tasks never reject but accumulate unboundedly, eventually causing `OutOfMemoryError`.
**Prove:** Wrap every `executor.submit()` in try/catch. Log `RejectedExecutionException`. Add a counter. Under load: if counter grows → tasks being silently rejected.
**Fix:**
```java
ThreadPoolExecutor pool = new ThreadPoolExecutor(
    coreSize, maxSize, keepAlive, TimeUnit.SECONDS,
    new ArrayBlockingQueue<>(queueSize),
    new ThreadPoolExecutor.CallerRunsPolicy()  // submitting thread runs task = backpressure
    // or custom: (task, executor) -> log.error("Task rejected: {}", task)
);
```
Always define a `RejectedExecutionHandler` that at minimum logs the rejection.

### Pattern: wait()/notify() with if-guard — spurious wakeup processes empty state
**Symptom:** Producer-consumer with manual synchronization works in testing. Under load, consumer processes null or operates on empty state. No exception at `wait()` itself.
**Why:** The JVM specification explicitly permits spurious wakeups — `wait()` can return without `notify()` being called. An `if` guard is checked once; a spurious wakeup bypasses the check and proceeds to consume from an empty collection.
**Dead giveaway:**
```java
synchronized (lock) {
    if (queue.isEmpty()) lock.wait();  // BUG: if, not while
    process(queue.poll());             // null after spurious wakeup
}
```
**Prove:** Add `assert !queue.isEmpty() : "spurious wakeup hit";` after `wait()`. Under load, assert fires.
**Fix:**
```java
synchronized (lock) {
    while (queue.isEmpty()) lock.wait();  // ALWAYS while, never if
    process(queue.poll());
}
```
This applies to `Object.wait()`. `BlockingQueue.take()` handles spurious wakeups internally — do NOT use manual `wait()` with a `BlockingQueue`.

---

## CATEGORY 5 — JVM, CLASSLOADER & MEMORY

### Pattern: ClassLoader conflict in WAR deployment — ClassCastException or NoSuchMethodError
**Symptom:** Works in IDE and unit tests. `ClassCastException`, `NoSuchMethodError`, or `LinkageError` when deployed to Tomcat or JBoss/WildFly. Stack trace shows the correct class name but cast fails.
**Why:** Servlet containers use hierarchical ClassLoaders. If the same library exists in both `WEB-INF/lib` AND the server's `lib/`, two separate `Class` objects exist with the same name — one loaded per ClassLoader. An object of class `Foo` from ClassLoader A cannot be cast to `Foo` from ClassLoader B.
**Prove:**
```java
log.debug("object class loader: {}", object.getClass().getClassLoader());
log.debug("target class loader: {}", TargetType.class.getClassLoader());
// If different → ClassLoader conflict confirmed
```
**Fix:** Remove library from one location. For server-managed libraries: mark `<scope>provided</scope>` in Maven. Do not bundle the servlet API, JDBC drivers registered at server scope, or logging frameworks if the server already provides them.

### Pattern: OutOfMemoryError — identify which memory pool to find the right fix
**Symptom:** JVM crashes with `OutOfMemoryError`. Must identify which pool to find the correct fix.
**Prove:** The OOM error message text IS the diagnostic — read it literally:
```
java.lang.OutOfMemoryError: Java heap space          → objects not GC'd (heap leak)
java.lang.OutOfMemoryError: Metaspace                → class metadata overflow (dynamic class gen)
java.lang.OutOfMemoryError: Direct buffer memory     → NIO ByteBuffer.allocateDirect() not released
java.lang.OutOfMemoryError: GC overhead limit exceeded → variant of heap space, GC spending >98% time
```
Enable heap dump for heap space errors: add `-XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath=/var/log/app/` to JVM args. On next OOM, open `.hprof` in Eclipse MAT or VisualVM — dominator tree shows what is holding memory.
**Diagnosis by error message:**
- `Java heap space` → objects not GC'd. Enable heap dump, analyze with Eclipse MAT or VisualVM. Look for unbounded caches, event listeners never removed, static collections.
- `Metaspace` → class metadata overflow. Dynamic class generation (JSP compilation, CGLib proxies, Groovy) without corresponding ClassLoader cleanup. Find the ClassLoader that is not being collected.
- `Direct buffer memory` → NIO `ByteBuffer.allocateDirect()` not collected (outside heap). Add `-XX:MaxDirectMemorySize=512m`. Find and fix the direct buffer lifecycle.
- `GC overhead limit exceeded` → GC spending >98% of time; variant of heap space.
**Enable heap dump on crash:**
```
-XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath=/var/log/app/
```

### Pattern: Reading a thread dump — deadlock and hung thread diagnosis
**Prove:** Capture and read the thread dump:
```bash
jcmd <pid> Thread.print        # JDK 17+, preferred
jstack -l <pid>                # classic, includes lock ownership
kill -3 <pid>                  # SIGQUIT — dumps to stdout (non-destructive)
```
**Find PID:** `jps -l | grep YourApp`
**Smoking gun per state:**
- `BLOCKED (on object monitor)` with "waiting to lock" + "locked by" on same address → deadlock or contention. Owner thread is named.
- `TIMED_WAITING` in executor threads → idle workers (normal) OR `InterruptedException` swallowed (check catch block).
- `RUNNABLE` flood in same method → CPU bottleneck at that method.
- Deadlock: `jstack -l` prints `Found one Java-level deadlock:` automatically.
**Capture:**
```bash
jcmd <pid> Thread.print        # JDK 17+, preferred
jstack -l <pid>                # classic, includes lock ownership
kill -3 <pid>                  # SIGQUIT, dumps to stdout (non-destructive)
```
**Find PID:** `jps -l | grep YourApp`
**Thread states:**
- `RUNNABLE` — executing. High RUNNABLE count = CPU bottleneck.
- `BLOCKED (on object monitor)` — waiting for `synchronized` lock. Look for "waiting to lock" + "locked by" to find the holder.
- `WAITING (on object monitor)` — called `wait()`. Expected for idle workers.
- `TIMED_WAITING` — `Thread.sleep()` or `wait(timeout)`. Expected for scheduled tasks.
**Deadlock:** JVM reports automatically with `jstack -l`:
```
Found one Java-level deadlock:
Thread-1: waiting to lock <0x000...> (held by Thread-2)
Thread-2: waiting to lock <0x000...> (held by Thread-1)
```
**ThreadLocal leak signal:** Thread pool threads (names like `http-nio-8080-exec-`) in `RUNNABLE` state serving wrong user data → check MDC/ThreadLocal cleanup.

---

## CATEGORY 6 — JDBC & CONNECTION POOL PATTERNS

### Pattern: Connection not closed in exception path — pool exhausts over time
**Symptom:** App starts fine. Under moderate load, after 30–120 minutes, all requests time out with `HikariPool-1 - Connection is not available, request timed out after 30000ms`. Restarting fixes immediately. DB shows app's connections as idle.
**Why:** Connection acquired in try block. Exception thrown. Catch block rethrows without closing connection. Each such occurrence permanently reduces pool size by 1. Pool exhausts after N occurrences (N = pool size).
**Prove:**
```properties
spring.datasource.hikari.leak-detection-threshold=2000
```
HikariCP logs `WARN HikariPool-1 - Connection leak detection triggered` with acquisition stack trace.
**Fix:**
```java
// WRONG — connection leaked when validate() throws
Connection conn = dataSource.getConnection();
try {
    if (!validate(conn)) throw new ValidationException();
    return query(conn);
} catch (ValidationException e) {
    throw e;  // conn.close() never reached
}

// CORRECT — auto-closed on any exit path
try (Connection conn = dataSource.getConnection();
     PreparedStatement ps = conn.prepareStatement(sql)) {
    // conn and ps closed automatically
    return ps.executeQuery();
}
```

### Pattern: JNDI DataSource lookup fails in servlet container — NamingException
**Symptom:** App starts. First DB call throws `javax.naming.NameNotFoundException: Name [jdbc/myDS] is not bound in this Context`. Works standalone, fails in Tomcat/JBoss.
**Why:** JNDI in servlet containers requires the `java:comp/env/` prefix for the Enterprise Naming Context. `context.lookup("jdbc/myDS")` searches the global namespace — not found. Also: `<resource-ref>` must exist in `web.xml` to bind the ENC entry.
**Prove:** Log the exact JNDI name being looked up. Compare character-for-character to the `name` attribute in `context.xml` `<Resource name="jdbc/myDS"/>`.
**Fix:**
```java
// Code
DataSource ds = (DataSource) ctx.lookup("java:comp/env/jdbc/myDS");

// web.xml (required)
<resource-ref>
    <res-ref-name>jdbc/myDS</res-ref-name>
    <res-type>javax.sql.DataSource</res-type>
    <res-auth>Container</res-auth>
</resource-ref>
```

### Pattern: PreparedStatement or ResultSet not closed — cursor exhaustion on DB
**Symptom:** Memory grows steadily. DB eventually reports too many open cursors (`ORA-01000` on Oracle or `FATAL: sorry, too many clients` on PostgreSQL with leaked cursors). Works initially, fails over hours.
**Why:** Every `PreparedStatement` and `ResultSet` holds server-side cursor resources. Not closing them leaves cursors open on the DB server even after the Java objects are no longer referenced (GC may not close them promptly).
**Prove:** Query DB cursor count periodically: `SELECT count(*) FROM v$open_cursor` (Oracle) or `SELECT count(*) FROM pg_stat_activity` (PostgreSQL). Watch it grow monotonically.
**Fix:** Always use try-with-resources. Close in reverse order: `ResultSet` → `PreparedStatement` → `Connection`. Try-with-resources handles this automatically (closed in reverse declaration order).

---

## CATEGORY 7 — SPRING BOOT PATTERNS

### Pattern: @Transactional self-invocation — transaction silently not applied
**Symptom:** `@Transactional` method called. Expected transaction behavior (rollback, isolation, propagation) does not happen. No exception. No transaction log. Adding more `@Transactional` annotations has no effect.
**Why:** Spring `@Transactional` works via AOP proxy. External calls go through the proxy → transaction management applied. Internal calls `this.method()` go directly to the target object, bypassing the proxy entirely. `@Transactional` on the called method is silently ignored.
```
External → Proxy → @Transactional → yourBean.processOrder()
                                     ↓ this.applyPayment()
                                     Direct Java call — NO PROXY
                                     @Transactional on applyPayment IGNORED
```
**Prove:** Add `log.debug("TX active: {}", TransactionSynchronizationManager.isActualTransactionActive())` at the start of the inner method. If `false` when called from within the same bean → self-invocation confirmed.
**Fix:**
```java
// Option 1: extract to separate bean (cleanest)
@Service class PaymentService {
    @Transactional public void applyPayment(...) { }
}
@Service class OrderService {
    @Autowired PaymentService paymentService;
    public void processOrder() {
        paymentService.applyPayment(...); // crosses proxy boundary
    }
}

// Option 2: self-inject
@Autowired private OrderService self;
self.applyPayment();  // goes through proxy

// Option 3: keep as single transaction in outer method (simplest)
// Remove @Transactional from inner method; let outer transaction cover everything
```

### Pattern: LazyInitializationException — collection accessed after session closes
**Symptom:** `org.hibernate.LazyInitializationException: could not initialize proxy — no Session`. Happens during JSON serialization (Jackson in REST controller) or after service method returns.
**Why:** `@Transactional` opens a Hibernate session. When the method returns, session closes. The entity returned is now detached. Accessing any uninitialized lazy collection on a detached entity fails because there is no session to load from.
**Prove:** `log.debug("TX active: {}", TransactionSynchronizationManager.isActualTransactionActive())` at the point where the collection is accessed. If `false` → outside transaction boundary.
**Fix:**
```java
// Option 1: DTO — map inside @Transactional while session is open
@Transactional(readOnly = true)
public OrderDto getOrder(Long id) {
    Order order = repo.findById(id).orElseThrow();
    return new OrderDto(order);  // accesses items while session open
}

// Option 2: JOIN FETCH
@Query("SELECT o FROM Order o JOIN FETCH o.items WHERE o.id = :id")
Order findWithItems(@Param("id") Long id);

// Option 3: @EntityGraph
@EntityGraph(attributePaths = {"items"})
Optional<Order> findById(Long id);
```
**Do NOT use:** `FetchType.EAGER` globally (causes N+1 on every query regardless of need) or `spring.jpa.open-in-view=true` (keeps session open until view renders — performance antipattern).

### Pattern: Prototype bean injected into singleton — always same instance
**Symptom:** `@Scope("prototype")` bean expected to give a fresh instance per use. All invocations use the same instance — state accumulates incorrectly across requests.
**Why:** Spring resolves `@Autowired` dependencies when creating the singleton. The prototype dependency is resolved ONCE at that time. All subsequent calls on the singleton use the same prototype instance — there is no re-injection mechanism.
**Prove:** Log `System.identityHashCode(prototypeDep)` on each invocation. If hash never changes → same instance.
**Fix:**
```java
// Option 1: ObjectFactory
@Autowired private ObjectFactory<PrototypeBean> factory;
void doWork() { factory.getObject().execute(); }  // new instance each call

// Option 2: ApplicationContext
@Autowired private ApplicationContext ctx;
void doWork() { ctx.getBean(PrototypeBean.class).execute(); }

// Option 3: @Lookup method injection
@Lookup
protected abstract PrototypeBean getPrototypeBean();
void doWork() { getPrototypeBean().execute(); }
```

### Pattern: Spring Security custom filter runs but SecurityContext is empty
**Symptom:** Custom JWT filter runs (confirmed by logs). `SecurityContextHolder.getContext().getAuthentication()` is null in the controller. Or: filter sets authentication but it's overwritten by the next filter.
**Why:** Spring Security has a precisely ordered internal filter chain. Custom filters registered via `@WebFilter`, `FilterRegistrationBean`, or servlet `web.xml` run OUTSIDE Spring Security's chain and cannot interact with `SecurityContextHolder` in the expected way. Filters must be added via `HttpSecurity.addFilterBefore/After/At()` to participate in the Security filter chain.
**Prove:** Enable `logging.level.org.springframework.security=DEBUG`. Output lists every filter in the chain and execution order per request. Confirm your filter appears in the chain and at the right position.
**Fix:**
```java
@Bean
public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
    http
        .addFilterBefore(jwtAuthFilter, UsernamePasswordAuthenticationFilter.class)
        .authorizeHttpRequests(auth -> auth.anyRequest().authenticated());
    return http.build();
}
// JwtAuthFilter must extend OncePerRequestFilter
// Set authentication: SecurityContextHolder.getContext().setAuthentication(auth)
```
Never use `@WebFilter` or `FilterRegistrationBean` for filters that need to set or read `SecurityContext`.

---

## CATEGORY 8 — ORM / JPA PATTERNS (Hibernate)

### Pattern: N+1 query — fast in dev, times out in production
**Symptom:** List endpoint fast in development (10–50 rows). Times out in production with thousands of rows. DB CPU spikes. Response time grows linearly with data volume. No error thrown.
**Why:** `@OneToMany` with `FetchType.LAZY` (default). Loading N parent entities triggers N individual `SELECT` queries for children — 1 + N total. With SQL logging disabled (default in prod), the problem is invisible in code review.
**Prove:** Enable `spring.jpa.show-sql=true`. Make one API call. Count SQL statements — should be O(1) not O(N). Look for `SELECT * FROM order_items WHERE order_id = ?` repeated N times.
**Fix:**
```java
// Option 1: JOIN FETCH in JPQL (single query, all data)
@Query("SELECT o FROM Order o JOIN FETCH o.items WHERE o.status = :status")
List<Order> findByStatusWithItems(@Param("status") Status status);

// Option 2: @EntityGraph
@EntityGraph(attributePaths = {"items"})
List<Order> findByStatus(Status status);

// Option 3: @BatchSize (issues batch IN queries, not N individual)
@OneToMany @BatchSize(size = 30)
private List<OrderItem> items;
```

### Pattern: Optimistic locking conflict — ObjectOptimisticLockingFailureException under load
**Symptom:** Concurrent updates to the same entity fail with `ObjectOptimisticLockingFailureException`. Works fine single-threaded. Failure rate increases with concurrency.
**Why:** `@Version` field enables optimistic locking. Two transactions read entity at version N. Both update and try to commit at version N+1. First commit succeeds (version → N+1). Second commit finds version already N+1, expected N — rejected.
**Prove:** Log the `@Version` field value on read and on write attempt for both concurrent requests. Both will show version=N on read, first write succeeds, second fails.
**Fix:**
```java
// Catch and retry at service layer
@Retryable(value = ObjectOptimisticLockingFailureException.class, maxAttempts = 3)
@Transactional
public Order updateOrder(Long id, OrderDto dto) { ... }

// Or: pessimistic lock for highly-contended entities
@Lock(LockModeType.PESSIMISTIC_WRITE)
@Query("SELECT o FROM Order o WHERE o.id = :id")
Order findByIdForUpdate(@Param("id") Long id);
```

### Pattern: Bidirectional @OneToMany — mappedBy side not set causes duplicate inserts
**Symptom:** Saving parent entity with children causes duplicate rows in child table, or a unique/FK constraint violation. SQL logs show unexpected extra INSERT or UPDATE.
**Why:** In bidirectional `@OneToMany` / `@ManyToOne`, the child's `@ManyToOne` side owns the relationship FK. The parent's `@OneToMany(mappedBy=...)` is the inverse side — it is informational only. If `child.setParent(parent)` is not called before saving, Hibernate cannot set the FK correctly and issues a redundant UPDATE or duplicate INSERT.
**Prove:** Enable SQL logging. Count INSERT and UPDATE statements for a single parent+children save. Extra statements beyond one INSERT per entity = mappedBy side not maintained.
**Fix:**
```java
// Always set BOTH sides of a bidirectional relationship
public void addItem(OrderItem item) {
    this.items.add(item);      // inverse side (informational)
    item.setOrder(this);       // owner side — controls the FK column
}
// Use this method everywhere, never manipulate items list directly
```

---

## CATEGORY 9 — SPRING WEBFLUX / REACTIVE

### Pattern: Blocking call inside Reactor pipeline — scheduler thread starvation
**Symptom:** WebFlux API responds fast under low load. Hangs completely under moderate concurrent load. No error thrown. Requests queue indefinitely.
**Why:** Reactor's `parallel` and `nio` schedulers have a small fixed thread count (2×CPU). Any blocking call inside `.map()` or `.flatMap()` holds a scheduler thread. Under load, all threads block and no reactive work progresses.
**Prove:** Install BlockHound in test environment: `BlockHound.install()` — throws `BlockingOperationError` with exact stack trace on any blocking call in non-blocking context. In production: log `Thread.currentThread().getName()` inside the pipeline — `reactor-http-nio-*` threads must not block.
**Fix:**
```java
// Wrong — blocks a Reactor nio thread
.flatMap(id -> Mono.just(jdbcRepository.findById(id)))

// Correct — offloads to boundedElastic (designed for blocking work)
.flatMap(id -> Mono.fromCallable(() -> jdbcRepository.findById(id))
                   .subscribeOn(Schedulers.boundedElastic()))
```

### Pattern: switchIfEmpty missing — Mono.empty() serializes as HTTP 200 not 404
**Symptom:** GET endpoint returns 200 with empty/null body when resource not found. Client receives null and fails silently. No exception.
**Why:** Reactive `repository.findById()` returns `Mono.empty()` for not-found. Without `switchIfEmpty()`, the pipeline completes successfully with no emission. Spring WebFlux returns 200 with empty body for a completed empty Mono.
**Prove:** Call endpoint with non-existent ID. Log `mono.doOnSuccess(v -> log.debug("value: {}", v))` — logs null for empty Mono.
**Fix:**
```java
return repo.findById(id)
    .switchIfEmpty(Mono.error(new ResponseStatusException(NOT_FOUND, "id=" + id)))
    .map(entity -> ResponseEntity.ok(toDto(entity)));
```

### Pattern: Spring Security context null in WebFlux — ThreadLocal not propagated
**Symptom:** `SecurityContextHolder.getContext().getAuthentication()` returns null inside reactive pipeline despite authenticated request.
**Why:** Spring Security for WebFlux stores the security context in Reactor's `Context` API, not `ThreadLocal`. `SecurityContextHolder` (MVC/ThreadLocal mechanism) has no value on Reactor's scheduler threads.
**Prove:** Use `ReactiveSecurityContextHolder.getContext()` in the same pipeline location. If it returns the authentication but `SecurityContextHolder` does not → ThreadLocal/Reactor mismatch confirmed.
**Fix:**
```java
// Wrong (MVC ThreadLocal pattern — fails in WebFlux)
String user = SecurityContextHolder.getContext().getAuthentication().getName();

// Correct (Reactor Context pattern)
return ReactiveSecurityContextHolder.getContext()
    .map(ctx -> ctx.getAuthentication().getName())
    .flatMap(username -> service.doWork(username));
```

---

## CATEGORY 10 — SPRING ASYNC, SCHEDULING & CACHING

### Pattern: @Async method executes synchronously — @EnableAsync missing
**Symptom:** Method annotated `@Async` blocks the calling thread. Returns `CompletableFuture` but caller waits for it to finish. No error, no exception — it just runs synchronously and callers see it as slow.
**Why:** `@Async` is AOP-based. Without `@EnableAsync` on a `@Configuration` class, the annotation is parsed but the proxy is never woven. The method executes on the caller's thread exactly as if the annotation were absent.
**Prove:** Two-step discrimination — these two causes produce identical runtime symptoms but have different structural signatures:

**Step 1 — structural check (no code changes needed):**
Search the entire codebase for `@EnableAsync`. If absent from every `@Configuration` class → confirmed: proxy never woven. Fix: add `@EnableAsync`. Stop here, no need for Step 2.

**Step 2 — if @EnableAsync IS present:** The cause is self-invocation. Confirm by finding the call site — is the `@Async` method being called from within the SAME class (`this.asyncMethod()`)? Self-invocation bypasses the AOP proxy regardless of `@EnableAsync`. Runtime confirmation: `log.debug("[ASYNC] thread={}", Thread.currentThread().getName())` inside the async method. If thread name matches the caller's thread (e.g., `http-nio-8080-exec-3` instead of `task-1`) AND `@EnableAsync` is present → self-invocation confirmed.
**Fix:**
```java
@Configuration
@EnableAsync  // ← this is required
public class AsyncConfig { }
```
Also applies to self-invocation: calling an `@Async` method from within the same bean bypasses the proxy. Extract to a separate bean.

### Pattern: @Async exception silently swallowed — AsyncUncaughtExceptionHandler not set
**Symptom:** `@Async` void method throws an exception. Nothing happens. No log, no alert, no retry. Business operation silently not performed.
**Why:** For `@Async` methods returning `void`, exceptions cannot propagate to the caller (there is no return channel). Spring discards them unless an `AsyncUncaughtExceptionHandler` is configured.
**Prove:** Inspect the configuration class — is `@EnableAsync` present on any `@Configuration` class? If absent, the hypothesis is confirmed structurally: Spring cannot discard what it never registered. For runtime confirmation: add `log.debug("[ASYNC] handler registered: {}", exceptionHandler != null)` in a `@Configuration implements AsyncConfigurer` — if the handler is null at startup, it was never configured.
**Fix:**
```java
@Configuration
@EnableAsync
public class AsyncConfig implements AsyncConfigurer {
    @Override
    public AsyncUncaughtExceptionHandler getAsyncUncaughtExceptionHandler() {
        return (ex, method, params) ->
            log.error("[ASYNC] Uncaught exception in {}: {}", method.getName(), ex.getMessage(), ex);
    }
}
```

### Pattern: @Scheduled method not executing — @EnableScheduling missing
**Symptom:** Method annotated `@Scheduled(fixedRate=...)` or `@Scheduled(cron=...)` never runs. No error. Silence.
**Why:** Same root cause as `@Async`: without `@EnableScheduling`, the annotation is recognized but no scheduler is started. The task is registered nowhere.
**Prove:** Add `log.info("[SCHED] tick at {}", Instant.now())` as the absolute first line of the `@Scheduled` method. If this never appears in logs after the application is fully started → scheduler is not running. Cross-check: search the entire codebase for `@EnableScheduling` — if absent, confirmed. If present, check it is on a class that Spring actually loads (reachable via component scan or explicit `@Import`).
**Fix:** Add `@EnableScheduling` to any `@Configuration` class. For Spring Boot apps, adding it to the main `@SpringBootApplication` class is sufficient.

### Pattern: @Cacheable returns stale data — cache not invalidated after write
**Symptom:** Update operation succeeds (DB shows new value). Subsequent read returns old value. Restarting app returns correct value. Only one specific endpoint is stale. The eviction log line *does* fire — but `redis-cli KEYS users::*` shows the original key still present after the eviction "succeeded."
**Why:** `@Cacheable` stores the return value keyed by the SpEL-resolved method arguments. `@CacheEvict` on the write method must use the SAME cache name AND a SpEL expression that resolves to the SAME key object — including its **Java type**. Spring Cache uses `SimpleKeyGenerator` (or your serializer) to compute the cache key from the resolved object, and **`Long(42)` and `Integer(42)` are different objects**: `new Long(42).equals(new Integer(42)) == false`, and most Redis serializers (`GenericJackson2JsonRedisSerializer`, `JdkSerializationRedisSerializer`) embed the type in the serialized form. The eviction targets a key that was never stored, leaves the original entry intact, and reports success because evicting a non-existent key is a no-op, not an error.

**The Long/Integer trap (most common cause of "evict ran but cache is still stale"):**
```java
// Stored with a Long key — the controller passes Long userId
@Cacheable(value = "users", key = "#userId")
public User getUser(Long userId) { ... }   // key object: Long(42)

// Evicted with #user.id — but UserProfile.getId() returns Integer!
@CacheEvict(value = "users", key = "#user.id")
public void updateUser(UserProfile user) { ... }  // key object: Integer(42)
```
Both `toString()` to `"42"`, both look identical in logs, but the cache key bytes differ. The evict targets `Integer(42)`, which was never written. The original `Long(42)` entry survives. **This pattern survives code review because both call sites "look right."** The only way to spot it is to check the actual return type of every getter referenced in a `@CacheEvict` SpEL path against the parameter type used in the matching `@Cacheable`.

**Other key-mismatch variants to check at the same time:**
- Cache name mismatch: `value = "users"` vs `value = "user"`.
- SpEL path mismatch: `key = "#userId"` vs `key = "#user.id"` even when types agree (different objects → different `hashCode`/`equals` via `SimpleKeyGenerator`).
- Auto-key vs explicit key: `@Cacheable` with no `key` (auto-generated from all args) vs `@CacheEvict` with an explicit `key`.
- Composite vs scalar: `@Cacheable(key = "{#tenantId, #userId}")` vs `@CacheEvict(key = "#userId")`.

**Prove:**
```java
@Cacheable(value = "users", key = "#userId")
public User getUser(Long userId) {
    log.debug("[CACHE] MISS — loading user {} from DB (type={})",
        userId, userId.getClass().getSimpleName());
    return repo.findById(userId).orElseThrow();
}

@CacheEvict(value = "users", key = "#user.id")
public void updateUser(UserProfile user) {
    Object id = user.getId();
    log.debug("[CACHE] evicting user {} (type={})", id, id.getClass().getSimpleName());
    repo.save(user);
}
```
After one GET + one UPDATE, look at the two log lines side-by-side: `loading user 42 (type=Long)` then `evicting user 42 (type=Integer)`. Same number, different type ⇒ confirmed key-type mismatch. Then `redis-cli KEYS 'users::*'` will still show the original key — final proof.

**Fix:** Align the key expressions so both resolve to the **same SpEL path AND the same Java type**. Pick one:
- **Option A (preferred):** Change `UserProfile.getId()` to return `Long` to match the `Long userId` parameter in the read path. Also update any controller signature that passes `user.getId()` downstream so the type stays `Long` end-to-end.
- **Option B:** Add a dedicated `@CacheEvict(value = "users", key = "#userId") public void evictUser(Long userId)` and call it from `updateUser` with `evictUser(user.getId().longValue())`.
- **Option C:** Use `@CacheConfig(cacheNames = "users")` at class level and ensure every `key` SpEL expression on the class resolves to the exact same object type.

Do NOT use `allEntries = true` as the fix — it works but evicts every user on every update, defeating the cache. Do NOT switch to `@CachePut` without also fixing the underlying type mismatch — `@CachePut` only helps if its key matches `@Cacheable`'s key, which is exactly the bug.

### Pattern: @PreAuthorize expression fails silently — SpEL error returns 403 not 500
**Symptom:** Endpoint returns 403 Forbidden for a user who should have access. No exception logged. Security debug shows access denied but no reason.
**Why:** `@PreAuthorize("hasRole('ADMIN')")` uses Spring Expression Language. A SpEL error (wrong role name, method not found on principal) evaluates to `false` rather than throwing — access is denied silently. Also: role names differ by convention (`ROLE_ADMIN` vs `ADMIN`).
**Prove:** Enable `logging.level.org.springframework.security=TRACE`. Output shows the exact SpEL expression evaluated and the result. Also log `SecurityContextHolder.getContext().getAuthentication().getAuthorities()` inside the controller to see actual granted roles vs expected role string.
**Fix:** Match role string exactly. `hasRole('ADMIN')` prepends `ROLE_` automatically — so the authority must be `ROLE_ADMIN`. `hasAuthority('ROLE_ADMIN')` matches literally. Use one convention everywhere.

---

## CATEGORY 11 — SPRING BOOT 3 / JAKARTA EE MIGRATION

### Pattern: ClassNotFoundException on javax.* after Spring Boot 3 upgrade
**Symptom:** App compiled and ran on Spring Boot 2.x. After upgrading to Spring Boot 3.x, starts throwing `ClassNotFoundException: javax.servlet.http.HttpServletRequest` or similar `javax.*` class at runtime despite no code changes.
**Why:** Spring Boot 3 requires Jakarta EE 9+ which renamed all `javax.*` packages to `jakarta.*`. Any dependency still using `javax.*` is incompatible. Mixing is impossible — both cannot coexist.
**Prove:** Run `mvn dependency:tree | grep javax` (or Gradle equivalent). Any library still on the `javax.*` namespace is the culprit. Also: check the exception stack trace — the class loading the missing `javax.*` type is the incompatible library.
**Fix:** Upgrade all dependencies to Jakarta EE 9-compatible versions. Key upgrades: Hibernate 6+, Tomcat 10+, any persistence/validation library. For libraries with no Jakarta version: keep on Spring Boot 2.x or find a replacement. Use `jakarta.servlet.*`, `jakarta.persistence.*`, `jakarta.validation.*` in your own code.

### Pattern: Spring Boot 3 @HttpExchange / HTTP Interface client returns wrong type
**Symptom:** HTTP Interface client (new in Spring Boot 3, replaces Feign) compiles fine but returns null, wrong type, or throws `HttpClientErrorException` that was previously handled. Error handling behavior changed.
**Why:** Spring Boot 3's `@HttpExchange` wraps errors differently from OpenFeign. 4xx/5xx responses throw `WebClientResponseException` subclasses, not Feign's `FeignException`. Error decoder customization must use `WebClient`-level error handling, not Feign's `ErrorDecoder`.
**Prove:** Log the full response status and body in a `WebClient` `onStatus` handler. If 4xx arrives but exception type is different from what catch blocks expect → error type mismatch between Feign and HttpExchange confirmed.
**Fix:**
```java
WebClient client = WebClient.builder()
    .defaultStatusHandler(HttpStatusCode::isError,
        resp -> resp.bodyToMono(String.class)
            .map(body -> new MyApiException(resp.statusCode(), body)))
    .build();
```

---

## CATEGORY 12 — KAFKA / MESSAGING PATTERNS

### Pattern: Kafka consumer not receiving messages — wrong group.id or auto.offset.reset
**Symptom:** Producer sends messages (confirmed in producer logs). Consumer application starts with no error. No messages received. Consumer log shows `Assigned partitions: []` or shows partition assigned but no poll output.
**Why:** Two root causes with identical symptom: (1) `group.id` mismatch — consumer subscribes as a different group than the one that has an offset committed, so it starts at `latest` and misses all prior messages. (2) `auto.offset.reset=latest` with a new consumer group — no committed offset exists, consumer starts from the end, never sees messages produced before it started.
**Prove:**
```bash
# Check what offsets the consumer group actually has
kafka-consumer-groups.sh --bootstrap-server localhost:9092 \
  --group <your-group-id> --describe
# LAG column: if LAG=0 and no messages received → messages consumed before consumer started (offset.reset=latest)
# If group not listed → group.id in code doesn't match what you think
# Also log inside @KafkaListener: log.debug("[KAFKA] received topic={} partition={} offset={}", r.topic(), r.partition(), r.offset())
# If this never prints → listener not reached
```
**Fix:** Two steps — `auto.offset.reset=earliest` alone is NOT enough once the group already has committed offsets at log-end (the reset policy only applies when no offset exists). You must also rewind the existing offsets, and `kafka-consumer-groups.sh --reset-offsets` REFUSES to run while the group has live members.

```yaml
# 1. application.yml — change the default for any FUTURE new group
spring.kafka.consumer:
  auto-offset-reset: earliest
  group-id: order-processor-v1
```

```bash
# 2. STOP the consumer application FIRST (scale to 0, kill the pod, etc.)
#    Otherwise the next command fails with "Assignments can only be reset
#    if the group <id> is inactive".
kubectl scale deployment order-processor --replicas=0
# (or: docker stop, systemctl stop, etc.)

# 3. Rewind committed offsets to the beginning of the topic
kafka-consumer-groups.sh --bootstrap-server kafka:9092 \
  --group order-processor-v1 \
  --topic orders \
  --reset-offsets --to-earliest --execute

# 4. Restart the consumer — it will replay all historical messages
kubectl scale deployment order-processor --replicas=1
```

For production: never use `latest` on a new consumer group without explicit offset management. Set `group.id` explicitly in `application.yml` — never rely on default. For groups that must read historical data, configure `earliest` BEFORE the group's first connection so this rescue procedure is never needed.

### Pattern: Kafka consumer group rebalance storm — listener processing slower than max.poll.interval.ms
**Symptom:** Consumer processes some messages then stops. Logs show repeated `Revoked partitions` / `Assigned partitions` cycles. Messages processed multiple times (duplicate processing — *the same message key appears twice after a Revoked/Assigned cycle, with the duplicates already persisted to the database*). Lag grows despite consumer running.
**Why (read carefully — two timeouts, two different causes):**
- `session.timeout.ms` is heartbeat-based. Heartbeats run on a **separate background thread**, so they keep firing even while a `@KafkaListener` method is busy. A long-running listener does **NOT** trip session timeout on its own.
- `max.poll.interval.ms` is the limit between `poll()` calls *on the consumer thread itself*. Spring Kafka's listener container only calls `poll()` after the previous batch has finished processing. **If processing one batch takes longer than `max.poll.interval.ms`, the coordinator evicts the consumer**, triggers rebalance, and reassigns the partition. The unacknowledged messages are replayed by the new owner — duplicate processing.
- The diagnostic equation is: `processing_time_per_message × max-poll-records  >  max.poll.interval.ms` ⇒ guaranteed rebalance storm. Example: 47 s/msg × 1 batch = 47 s > 30 s `max.poll.interval.ms` ⇒ storm on every message.
**Prove:** Log the processing time of every message: `long start = System.currentTimeMillis(); process(record); log.debug("[KAFKA] processed in {}ms", System.currentTimeMillis()-start)`. Compare against `max.poll.interval.ms` from `application.yml` (NOT `session.timeout.ms`). The trigger is processing-time vs poll-interval, not heartbeat. Confirm in logs that the rebalance fires *after* the slow processing window completes — that timing correlation rules out the "network glitch" alternative.
**Fix:** Pick ONE knob to fix the rebalance, AND add idempotency to clean up duplicates already in the database. **Both are required** — fixing the rebalance only stops *future* duplicates; the existing dupes are already written.
```yaml
# application.yml — pick whichever matches your processing characteristics
spring.kafka.consumer:
  max-poll-records: 1               # process one slow message at a time (simplest)
  properties:
    max.poll.interval.ms: 600000    # OR: raise the ceiling above worst-case processing time
spring.kafka.listener:
  ack-mode: record                  # OR: commit after each record so a rebalance loses at most one
```
```java
// Idempotency — required regardless of which knob above you pick.
// Even with the rebalance fixed, retries on transient failures will redeliver.
@KafkaListener(topics = "payments")
public void handle(PaymentEvent event) {
    // Use a unique business key — eventId, idempotency-key header, or (orderId+amount+ts)
    if (processedRepo.existsByEventId(event.getEventId())) {
        log.info("[KAFKA] duplicate eventId={} skipped", event.getEventId());
        return;
    }
    paymentService.charge(event);              // your existing logic
    processedRepo.save(new Processed(event.getEventId())); // mark as done
}
```
For long processing: commit offset after each record, not after the batch (`AckMode.RECORD`). Do NOT add a try/catch around the listener method — that catches business exceptions, not the rebalance, and hides the real failure. Do NOT increase consumer thread count — it does not change the per-message processing time vs the poll-interval ceiling.

### Pattern: Kafka message silently not produced — transaction not committed
**Symptom:** Producer code executes with no exception. Messages appear in local log. Consumer never receives them. `kafka-console-consumer` also shows nothing.
**Why:** If the producer is configured with transactions (`transactional.id` set), messages are only visible to consumers with `isolation.level=read_committed` AFTER the transaction commits. If transaction is never committed (missing `@Transactional`, exception before commit, or `KafkaTemplate` not flushing), messages are buffered indefinitely.
**Prove:**
```java
// Log the send result explicitly — don't fire-and-forget
kafkaTemplate.send(topic, key, value)
    .whenComplete((result, ex) -> {
        if (ex != null) log.error("[KAFKA] send failed: {}", ex.getMessage());
        else log.debug("[KAFKA] sent offset={}", result.getRecordMetadata().offset());
    });
// If "sent offset" never appears → message never reached broker
// If offset appears but consumer doesn't see it → transaction not committed
```
Also: on a **non-production** diagnostic consumer only, temporarily set `isolation.level=read_uncommitted` to confirm uncommitted messages are present in the topic. Never change isolation on a production consumer — it exposes dirty reads from all producers on the broker.
**Fix:** Ensure `kafkaTemplate.send()` result is awaited or callback is checked. For transactional producers: annotate the method with `@Transactional` and ensure no exception exits before the method returns normally.

### Pattern: @KafkaListener deserialization error — poison pill stops entire partition
**Symptom:** Consumer processes messages normally then permanently stops on one partition. Error log shows `SerializationException` or `JsonParseException` and *the same offset and partition repeating identically* — e.g. `Seeking to current position for [notifications-1@offset 94821]` over and over. Other partitions on the same topic continue advancing. Adding a try/catch inside the `@KafkaListener` method does NOT help.
**Why:** A malformed message (wrong schema, wrong type, corrupted bytes) causes the value deserializer to throw on every poll attempt. The exception is raised in the converter layer **before** the `@KafkaListener` method is invoked, so an in-method try/catch can never see it. Kafka's at-least-once semantics retry the same offset until it succeeds or the offset is explicitly advanced. Result: that one offset blocks its entire partition forever — a "poison pill." Other partitions are unaffected, which is how you tell this apart from a deadlock or a downstream service outage.
**Prove:** Tail the consumer log and look for an offset that repeats *identically* across retries (`@offset 94821` printed every few seconds). Confirm partitions 0 and 2 are still advancing while partition 1 is stuck. Then enable `ErrorHandlingDeserializer` (see fix) which captures the raw bytes in a header so you can inspect what is malformed.
**Fix:** Two steps, **both required for one-shot recovery**. Step 1 unblocks the partition right now; Step 2 prevents it from happening again. Skipping Step 1 leaves production stuck even after the code fix is deployed.

**Step 1 — IMMEDIATE recovery: manually advance past the poison offset.**
```bash
# Stop the consumer first (reset-offsets refuses to run on an active group)
kubectl scale deployment notification-consumer --replicas=0

# Skip the single poisoned offset (94821 → 94822)
kafka-consumer-groups.sh --bootstrap-server kafka:9092 \
  --group notification-consumer-v1 \
  --topic notifications --partition 1 \
  --reset-offsets --to-offset 94822 --execute

# Restart the consumer — partition 1 unblocks
kubectl scale deployment notification-consumer --replicas=1
```

**Step 2 — PERMANENT fix: install `ErrorHandlingDeserializer` + DLQ routing** so the next poison pill is captured and routed instead of blocking the partition.
```yaml
# application.yml
spring.kafka.consumer:
  value-deserializer: org.springframework.kafka.support.serializer.ErrorHandlingDeserializer
  properties:
    spring.deserializer.value.delegate.class: org.springframework.kafka.support.serializer.JsonDeserializer
```
```java
// Listener — check for the deserialization error header and route to DLQ
import org.springframework.kafka.support.serializer.SerializationUtils;
import org.apache.kafka.common.header.Header;

@KafkaListener(topics = "notifications")
public void listen(ConsumerRecord<String, Object> record) {
    Header errorHeader = record.headers()
        .lastHeader(SerializationUtils.VALUE_DESERIALIZER_EXCEPTION_HEADER);
    if (errorHeader != null) {
        log.error("[KAFKA] poison pill at partition={} offset={} → DLQ",
            record.partition(), record.offset());
        dlqTemplate.send("notifications.DLQ", record.key(), record.value());
        return; // ack normally so the partition advances
    }
    process((NotificationEvent) record.value());
}
```
**Do NOT:** add try/catch *inside* the listener method as the primary fix (deserialization happens before the method is called — the catch never fires). Do NOT just restart the consumer — the same offset will be re-attempted and re-fail. Do NOT blame the producer without also fixing the consumer side; producers can always misbehave and the consumer must survive it.

---

## CATEGORY 13 — JAVA 21 VIRTUAL THREADS (PROJECT LOOM)

### Pattern: Virtual thread pinned to carrier thread — synchronized block kills scalability
**Symptom:** Application migrated to Java 21 virtual threads (`Executors.newVirtualThreadPerTaskExecutor()`). Under load, throughput is no better than platform threads — sometimes worse. Thread dump shows many virtual threads in WAITING state on a small number of carrier threads.
**Why:** Virtual threads are lightweight unless they hit a `synchronized` block or `synchronized` method — at that point they "pin" the carrier thread (an OS thread). The virtual thread cannot unmount from the carrier while holding a monitor lock. This converts a potentially-M:N concurrency model back to 1:1 for pinned threads, destroying the scalability benefit.
**Prove:**
```bash
# Enable JVM pinning diagnostics — add to JVM args
-Djdk.tracePinnedThreads=full

# Output when pinning occurs:
# Thread[#24,ForkJoinPool-1-worker-1,5,CarrierThreads]
#   java.base/java.lang.Object.wait(Object.java) @bci=0
#       com.example.MyService.doWork(MyService.java:42) <== synchronized method
# Count unique "synchronized" frames in output — high count = scalability bottleneck
```
**Fix:** Replace `synchronized` blocks with `ReentrantLock` (which supports virtual thread unmounting). Alternatively, use `Semaphore` for rate limiting. For third-party libraries that use `synchronized` internally: check for updated versions that use `java.util.concurrent` primitives.

### Pattern: Virtual thread + ThreadLocal — state leaks between unrelated requests
**Symptom:** After migrating to virtual threads, per-request data (MDC fields, user context, tenant ID) occasionally appears in unrelated requests. Symptom identical to the servlet singleton state pollution bug but the fix is different.
**Why:** Virtual threads are created per-task and should not share ThreadLocals with other tasks. However: if a thread pool is reused (e.g., a bounded virtual thread executor), or if `InheritableThreadLocal` is used, child virtual threads inherit parent's state. Web frameworks that create virtual threads from a thread pool that had prior request state cause cross-contamination.
**Prove:** Log `MDC.getCopyOfContextMap()` at the START of each request handler BEFORE setting any MDC values. If any prior request's MDC values appear at the start of a new request → ThreadLocal leak confirmed. Log `Thread.currentThread().isVirtual()` to confirm virtual threads are in use.
**Fix:** Use `ScopedValue` (preview in Java 21, finalized in **Java 22** — JEP 464) instead of `ThreadLocal` for request-scoped state. Clear ThreadLocals explicitly in a filter before and after each request. Prefer `ThreadLocal` over `InheritableThreadLocal` to prevent child thread inheritance.
```java
// Correct pattern for virtual thread request context
static final ScopedValue<RequestContext> REQUEST_CTX = ScopedValue.newInstance();

ScopedValue.where(REQUEST_CTX, new RequestContext(userId, tenantId))
    .run(() -> service.handleRequest()); // context automatically scoped to this call tree
```
