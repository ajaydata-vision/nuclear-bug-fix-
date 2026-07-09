# .NET / ASP.NET Core Bug Patterns

Covers: ASP.NET Core (middleware, routing, model binding, filters), Dependency
Injection, async/await, HttpClient, Entity Framework Core, System.Text.Json,
Configuration / IOptions, Kestrel / IIS hosting, ThreadPool / concurrency,
.NET version migration (6 → 7 → 8 → 9).
Each pattern: symptom → why → prove → fix.

This file does NOT cover Blazor or SignalR. For those, collect deeper
intake and search upstream GitHub issues directly.

---

## CATEGORY 1 — ASP.NET CORE MIDDLEWARE PIPELINE

### Pattern: Authentication always fails with 401 even though token is valid — middleware order wrong
**Symptom:** Every request to a `[Authorize]` endpoint returns 401 Unauthorized. The JWT/cookie is in the request (confirmed in the Network tab). Token validates fine in jwt.io. `context.User.Identity.IsAuthenticated` is `false` inside the controller. Removing `[Authorize]` makes the endpoint work and `User` is an empty `ClaimsPrincipal`.
**Why:** ASP.NET Core middleware runs in the order you add it in `Program.cs`. `UseAuthentication()` MUST run before `UseAuthorization()`, and BOTH must run after `UseRouting()` and before `UseEndpoints()` / `MapControllers()`. If `UseAuthorization()` appears before `UseAuthentication()`, the authorization middleware sees an unauthenticated user on every request and rejects it — the token parsing never happens. In minimal hosting (.NET 6+) the order is still your responsibility; the `WebApplicationBuilder` does not auto-order them.
**Prove:** Add a one-line probe middleware just before `UseAuthorization()` and another just after `UseAuthentication()`:
```csharp
app.UseRouting();
app.Use(async (ctx, next) => {
    Console.WriteLine($"[BEFORE AUTHN] IsAuthenticated={ctx.User.Identity?.IsAuthenticated}");
    await next();
});
app.UseAuthentication();
app.Use(async (ctx, next) => {
    Console.WriteLine($"[AFTER AUTHN]  IsAuthenticated={ctx.User.Identity?.IsAuthenticated}");
    await next();
});
app.UseAuthorization();
app.MapControllers();
```
`BEFORE AUTHN` should show `False`, `AFTER AUTHN` should show `True`. If `AFTER AUTHN` still shows `False`, the JWT bearer scheme itself is failing — check `AddAuthentication().AddJwtBearer(...)` config. If `AFTER AUTHN` is `True` but the endpoint still returns 401, `UseAuthorization` is running *before* `UseAuthentication`.
**Fix:** The canonical order is fixed — memorize it and never deviate:
```csharp
var app = builder.Build();

app.UseExceptionHandler("/error");   // 1. outermost — catches everything
app.UseHttpsRedirection();           // 2. redirect before routing
app.UseStaticFiles();                // 3. static files skip the rest
app.UseRouting();                    // 4. routing decision
app.UseCors("MyPolicy");             // 5. CORS AFTER routing, BEFORE auth
app.UseAuthentication();             // 6. parse the token → populate User
app.UseAuthorization();              // 7. enforce [Authorize] on the route
app.MapControllers();                // 8. endpoint execution
app.Run();
```
**Do NOT:** add `UseRouting()` twice, call `UseAuthorization()` before `UseAuthentication()`, or put `UseCors()` after `UseAuthentication()` (preflight OPTIONS requests won't get CORS headers and the browser will reject authenticated cross-origin calls).

### Pattern: CORS preflight returns 204 but actual request has no Access-Control-Allow-Origin header
**Symptom:** Browser console shows `Access to fetch at '...' has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present`. OPTIONS request in Network tab returns 204 with CORS headers. The actual GET/POST that follows has NO CORS headers and is blocked by the browser. Works from Postman (which doesn't enforce CORS).
**Why:** `UseCors()` is registered after `UseAuthentication()` / `UseAuthorization()` / `MapControllers()`, or a short-circuiting middleware (auth, rate limiting, exception handler) writes the response before the CORS middleware runs on the return trip. CORS middleware adds headers on the *outbound* pass — if an earlier middleware already committed the response, the CORS headers are lost.
**Prove:** Check the order in `Program.cs`: `UseCors` must be between `UseRouting` and `UseAuthentication`. Test with a bare GET from the browser to a public endpoint — if that works but an authenticated endpoint doesn't, the auth pipeline is writing the response before CORS can add headers. Also check: is the endpoint throwing 401 via `[Authorize]`? If yes, the 401 response body is written by `UseAuthorization` without CORS headers.
**Fix:**
```csharp
// Program.cs
builder.Services.AddCors(options => options.AddPolicy("Spa", p => p
    .WithOrigins("https://app.example.com")  // NEVER use AllowAnyOrigin with credentials
    .AllowAnyMethod()
    .AllowAnyHeader()
    .AllowCredentials()));

// ORDER MATTERS — UseCors after UseRouting, before UseAuthentication
app.UseRouting();
app.UseCors("Spa");                  // <- here
app.UseAuthentication();
app.UseAuthorization();
app.MapControllers();
```
For the "401 has no CORS headers" case specifically: if `UseCors` is already in the right position (after `UseRouting`, before `UseAuthentication`), the CORS middleware runs on the outbound pass of the 401 response and DOES add the headers. If the 401 still has no CORS headers, it means `UseCors` is either missing, or registered AFTER `UseAuthentication`/`UseAuthorization` (so it never sees the 401 on the way out), or the 401 is being written by a custom exception handler earlier in the pipeline. Fix the ordering — don't try to patch it with `UseStatusCodePages`, which does not add CORS headers. Also: `AllowCredentials()` cannot be combined with `AllowAnyOrigin()` — the browser will reject the response even if the server sends both.

### Pattern: Custom middleware runs twice per request — you registered it twice
**Symptom:** A request ID is being generated twice per request, or logging middleware prints each log line twice, or a rate limit counter increments by 2 on every request. Only happens after a refactor.
**Why:** Middleware was registered more than once in the pipeline. The most common shapes are:
1. `app.UseMiddleware<MyMiddleware>()` called in `Program.cs` AND inside an extension method that was itself added to `Program.cs` (e.g. `app.UseMyModule()` that internally also calls `UseMiddleware<MyMiddleware>()`).
2. Registered once globally AND again inside a `UseWhen`/`Map` branch whose predicate matches every request.
3. Registered in both a base `Startup`-style class and in `Program.cs` during a minimal hosting migration.
The pipeline is a linear list — duplicate registrations produce duplicate invocations. Also note: calling `app.UseRouting()` more than once creates two separate routing middlewares in the pipeline and the second one can silently reset endpoint selection — keep `UseRouting` at exactly one call site.
**Prove:** Add a `Console.WriteLine` with a GUID at the start of the middleware's `InvokeAsync`. Hit one endpoint. Count how many GUIDs print per request. More than 1 = duplicate registration. Also dump the pipeline at startup by logging each middleware registration call site.
**Fix:** Search `Program.cs` AND every `Use*` extension method in the codebase for every occurrence of the middleware type name. Remove the duplicate — don't "gate" it with a flag, just remove the extra registration. If the middleware needs to run conditionally, use `UseWhen(ctx => ctx.Request.Path.StartsWithSegments("/api"), branch => branch.UseMiddleware<MyMiddleware>())` — but never register it both globally and inside a `UseWhen`.

---

## CATEGORY 2 — MODEL BINDING & VALIDATION

### Pattern: [FromBody] parameter is null even though the request has a valid JSON body
**Symptom:** POST/PUT endpoint receives the request, `Request.Body` contains valid JSON (confirmed by manually reading the stream), but the `[FromBody] MyDto dto` parameter is `null` inside the action. No model binding error surfaced to the client — just a null object. Only affects one endpoint; others bind fine.
**Why:** Several root causes produce identical symptoms — rule them out in order:
1. **Content-Type header is missing or wrong.** `[FromBody]` only binds when `Content-Type: application/json` (or `text/json`). `text/plain` or empty → null bind, no error.
2. **The DTO uses the `required` modifier on properties, and the project is on .NET 6.** System.Text.Json learned the `required` keyword in .NET 7 (STJ 7). On .NET 6, STJ silently fails to honor `required` members. Records with ordinary parameterized constructors DO work on STJ 5/6 — it's specifically the `required` keyword that's absent before STJ 7.
3. **A property the JSON uses has no public setter** — System.Text.Json silently skips it. If ALL properties are skipped, the resulting object may be null or default-constructed.
4. **The JSON root is an array but the parameter is a single object** (or vice versa) — silent null bind.
5. **`ApiBehaviorOptions.SuppressModelStateInvalidFilter = true`** was set somewhere — the automatic 400 response was disabled, so binding errors return null instead of a 400.
**Prove:** Add a diagnostic action filter that logs `ModelState.IsValid` and every `ModelState` error *before* the action runs:
```csharp
public class LogBindingFilter : IActionFilter {
    public void OnActionExecuting(ActionExecutingContext ctx) {
        foreach (var (key, entry) in ctx.ModelState) {
            foreach (var err in entry.Errors) {
                Console.WriteLine($"[BIND] {key}: {err.ErrorMessage} | {err.Exception?.Message}");
            }
        }
        Console.WriteLine($"[BIND] args: {string.Join(", ", ctx.ActionArguments.Select(a => $"{a.Key}={a.Value ?? "null"}"))}");
    }
    public void OnActionExecuted(ActionExecutedContext ctx) { }
}
// Register globally in Program.cs:
builder.Services.AddControllers(o => o.Filters.Add<LogBindingFilter>());
```
Also read `Request.ContentType` at the top of the action and log it — if it's not `application/json`, the client is wrong.
**Fix:** Depending on root cause:
- **Content-Type wrong:** fix the client. Never try to "be nice" and accept `text/plain` — it masks bugs forever.
- **Record / required properties on .NET 6:** upgrade to .NET 7+ (System.Text.Json 7 supports parameterized constructors and `required` members), OR add a public parameterless constructor AND public setters to the DTO.
- **Properties skipped:** ensure every JSON field maps to a property with a public setter (or `init`). For case mismatch: `builder.Services.ConfigureHttpJsonOptions(o => o.SerializerOptions.PropertyNameCaseInsensitive = true);` — but prefer consistent casing.
- **Never set `SuppressModelStateInvalidFilter = true`** unless you're explicitly handling validation yourself. The automatic 400 response is the feature that surfaces these bugs.

### Pattern: [ApiController] + model state error returns HTML error page instead of JSON 400
**Symptom:** A validation failure returns an HTML error page or `text/plain` response body, not a JSON ProblemDetails. Swagger clients can't parse it. Only some endpoints are affected.
**Why:** The controller is missing the `[ApiController]` attribute. Without it, ASP.NET Core does NOT automatically convert ModelState errors to a 400 JSON response — the request passes validation and reaches the action with `ModelState.IsValid == false`, and whatever the action returns (often a view, or a thrown exception caught by a different middleware) is what the client sees.
**Prove:** Check every controller class declaration. If a controller handling API routes is missing `[ApiController]`, that's it.
**Fix:**
```csharp
[ApiController]                          // <- this
[Route("api/[controller]")]
public class OrdersController : ControllerBase { ... }
```
To apply `[ApiController]` everywhere without repeating it, inherit every API controller from a base class that carries the attribute:
```csharp
[ApiController]
public abstract class ApiControllerBase : ControllerBase { }

public class OrdersController : ApiControllerBase { ... }  // inherits [ApiController]
```
Or apply it at the assembly level with `[assembly: ApiController]` in any `.cs` file — all controllers in the assembly then behave as if annotated. Never mix `Controller` (returns views) with `[ApiController]` — use `ControllerBase` as the base class for API endpoints.

### Pattern: DateTime query string parameter binds to wrong value or throws — culture / format mismatch
**Symptom:** `?date=2024-03-05` binds correctly in development but throws `FormatException` in production, or binds to a wrong date (month and day swapped). Happens after deploying to a server with a different OS locale.
**Why:** ASP.NET Core's default model binder for `DateTime` uses the server's current culture unless you override it. Windows servers set to `en-GB` parse `03/05/2024` as May 3; `en-US` parses it as March 5. Linux containers often default to `C.UTF-8` which accepts ISO-8601 but not all locale-specific formats. Any deployment across differently-localized machines produces inconsistent binding.
**Prove:** Log `CultureInfo.CurrentCulture.Name` at app startup. Compare between environments. If they differ → the binder is culture-dependent.
**Fix:** Force invariant culture globally and always use ISO-8601 in API contracts:
```csharp
// Program.cs — very early, before any other service registration
CultureInfo.DefaultThreadCurrentCulture = CultureInfo.InvariantCulture;
CultureInfo.DefaultThreadCurrentUICulture = CultureInfo.InvariantCulture;
```
And in API contracts use `DateTimeOffset` (not `DateTime`) — it preserves the offset through JSON and through query-string round-trips, and eliminates the `Kind == Unspecified` surprise entirely. For request body JSON this is mostly academic: System.Text.Json always uses ISO-8601 for `DateTime`/`DateTimeOffset`, so `[FromBody]` is safe. Only `[FromQuery]` / `[FromRoute]` / `[FromForm]` are at risk, because those go through the culture-sensitive type converter path. `DateTime.Kind == Unspecified` after deserialization is a frequent silent timezone bug — using `DateTimeOffset` avoids it.

---

## CATEGORY 3 — DEPENDENCY INJECTION LIFETIMES

### Pattern: Scoped DbContext captured by singleton — "A second operation was started on this context instance"
**Symptom:** Random `InvalidOperationException: A second operation was started on this context instance before a previous operation completed. This is usually caused by different threads concurrently using the same instance of DbContext.` Happens under concurrent load, disappears at low traffic, not reproducible in tests. No obvious threading code in the app.
**Why:** A singleton service (registered with `AddSingleton`) holds a reference to a scoped service (`AddScoped<AppDbContext>`). The singleton is constructed once, receives the DbContext from the first request's scope, and keeps using it for every subsequent request on every thread. The DbContext is not thread-safe and is also disposed at the end of the first request — so you get either the "second operation" exception or `ObjectDisposedException`, intermittently. ASP.NET Core's DI container detects this at startup via `ValidateScopes`, which `WebApplication.CreateBuilder` **enables by default in the Development environment** since .NET 6 — but in Staging and Production it is OFF by default. So the bug can pass through a Development-only CI run and explode only in Staging.
**Prove:** Enable scope validation in EVERY environment so Staging/Production catches it at startup instead of at first concurrent request:
```csharp
// Program.cs
builder.Host.UseDefaultServiceProvider(opts => {
    opts.ValidateScopes = true;        // throw if scoped captured in singleton
    opts.ValidateOnBuild = true;       // check every registered service at startup
});
```
Rerun the app. If the startup throws `InvalidOperationException: Cannot consume scoped service 'AppDbContext' from singleton 'MyBackgroundWorker'` → you have confirmation and the exact captured service is named. Note: this option must be set via `UseDefaultServiceProvider` before `builder.Build()` — setting it after has no effect.
**Fix:** Never inject a scoped service directly into a singleton. Inject `IServiceScopeFactory` instead and create a scope per unit of work:
```csharp
public class MyBackgroundWorker : BackgroundService {
    private readonly IServiceScopeFactory _scopeFactory;
    public MyBackgroundWorker(IServiceScopeFactory f) => _scopeFactory = f;

    protected override async Task ExecuteAsync(CancellationToken ct) {
        while (!ct.IsCancellationRequested) {
            using var scope = _scopeFactory.CreateScope();
            var db = scope.ServiceProvider.GetRequiredService<AppDbContext>();
            await DoWork(db, ct);
            // scope disposed here → DbContext disposed → safe
            await Task.Delay(TimeSpan.FromSeconds(5), ct);
        }
    }
}
```
**Do NOT:** change `AppDbContext` to a singleton — it is not thread-safe and will corrupt state. Do NOT use `IServiceProvider` as a service locator from everywhere — use scope factory only at the edges (background services, message consumers, timers).

### Pattern: Transient service that implements IDisposable leaks until request end
**Symptom:** Memory grows linearly with request throughput even though each request "finishes." Tracing shows `Dispose()` never called on a particular service type until the request completes — and if the request makes 100 uses of that transient, 100 instances pile up and all dispose together at end-of-request.
**Why:** When a transient `IDisposable` is resolved from the scoped `IServiceProvider` (the request's service provider), the container tracks it and disposes it when the scope ends — *not* when you're done with it. Across a long-running request that creates many transients (e.g. a bulk import), this pins all of them in memory simultaneously.
**Prove:** Take a dotnet-counters trace of `Microsoft.Extensions.DependencyInjection` scope stats during a high-volume request. Look for "tracked disposables per scope" growing. Or put a `~MyService()` finalizer with logging — finalizers run much later than `Dispose`, but tracked transients never reach the finalizer until scope disposes.
**Fix:** Three options:
1. **Most common:** refactor so the service does not implement `IDisposable` — many do so "just in case" without needing it.
2. Resolve from a **child scope** created explicitly for the batch: `using var scope = _scopeFactory.CreateScope();` inside the loop, dispose every iteration.
3. Register the service as `AddTransient` but resolve it from the **root** container (bypasses tracking) — dangerous; only use when you can guarantee manual disposal. Normally avoid.

### Pattern: Options injected into singleton never see updated config — you used IOptionsSnapshot
**Symptom:** `appsettings.json` is reloaded at runtime (`reloadOnChange: true`), but a background worker keeps using the old values. Restarting the app picks up the change. `IOptionsMonitor<T>.CurrentValue` shows the new value; `IOptionsSnapshot<T>.Value` shows the old.
**Why:** The three options interfaces have different lifetimes:
- `IOptions<T>` — singleton, read once at app start, never refreshed.
- `IOptionsSnapshot<T>` — **scoped**, refreshed per request. Cannot be injected into a singleton (captures-scoped-in-singleton bug). In a singleton that captured it, the first request's snapshot is held forever.
- `IOptionsMonitor<T>` — **singleton**, value refreshes on file change, exposes `OnChange` callback. This is the only one safe for singletons that need live config.
**Prove:** Check the injected type in the singleton's constructor. If it's `IOptionsSnapshot<T>` and the class is a singleton or hosted service → this is the bug. Scope validation (see first pattern in this category) will also flag it at startup.
**Fix:**
```csharp
public class EmailSender : IHostedService {
    private readonly IOptionsMonitor<EmailOptions> _opts;
    public EmailSender(IOptionsMonitor<EmailOptions> opts) {
        _opts = opts;
        _opts.OnChange(newOpts => Console.WriteLine($"[EMAIL] config reloaded: {newOpts.SmtpHost}"));
    }
    // Always read _opts.CurrentValue at point of use, never cache it:
    public Task SendAsync(string body) {
        var host = _opts.CurrentValue.SmtpHost;
        // ...
    }
}
```
Rule: `IOptionsMonitor` for singletons/background services, `IOptionsSnapshot` for per-request services (controllers, scoped services), `IOptions` only for config that genuinely never changes.

---

## CATEGORY 4 — ASYNC / AWAIT DEADLOCKS & SYNC-OVER-ASYNC

### Pattern: App hangs forever on `.Result` or `.Wait()` — classic sync-over-async deadlock (legacy ASP.NET / WinForms / WPF)
**Symptom:** Call to an async method via `.Result`, `.Wait()`, or `.GetAwaiter().GetResult()` hangs indefinitely. Only reproduces in the web/UI host — the same code works in a console app or in tests. Thread dump shows the calling thread blocked in `WaitOne`, and the awaited task blocked in a continuation queued to the same captured context.
**Why:** When `await` sees a non-null `SynchronizationContext` (legacy ASP.NET's `AspNetSynchronizationContext`, WPF/WinForms UI context), it captures it and tries to resume the continuation ON that same context. If the caller is blocking the only thread that context owns, the continuation cannot run → the task never completes → the block never returns → deadlock. **ASP.NET Core does NOT have a SynchronizationContext**, so this exact deadlock does not happen there — but it DOES still happen in library code shared with a legacy host, in WPF/WinForms apps, in unit tests using `[STAThread]`, and when your code is loaded into Office/VSTO/IIS-hosted WCF.
**Prove:** If the hanging call is `x.Result` on an async method, and you're in ASP.NET (System.Web), WPF, WinForms, Xamarin, VSTO, or classic WCF → this is it. Confirm by temporarily changing one call to `await` — if the hang disappears, deadlock confirmed.
**Fix:** Two correct approaches — pick one, never mix:
1. **Async all the way down (correct):** change the calling method to `async`, return `Task`/`Task<T>`, use `await`. Propagate up to the entry point (controller action, event handler, `Main` → `async Task Main`).
2. **ConfigureAwait(false) in library code (mitigation):** every `await` inside a library that may be called from a sync-over-async context must use `.ConfigureAwait(false)`:
   ```csharp
   public async Task<User> GetUserAsync(int id) {
       var row = await _db.Users.FindAsync(id).ConfigureAwait(false);
       var profile = await _http.GetAsync($"/profile/{id}").ConfigureAwait(false);
       return new User(row, profile);
   }
   ```
   This tells `await` not to capture the context, so the continuation runs on a thread-pool thread and the deadlock is broken. **`ConfigureAwait(false)` is required on EVERY `await` in the chain** — missing one anywhere re-introduces the capture. In ASP.NET Core application code it's unnecessary (no context); in library code that might be loaded by a legacy host, it's mandatory.
**Do NOT:** wrap the call in `Task.Run(() => x.Result).Result` ("hide the sync context") — that burns a thread-pool thread to block another thread-pool thread and can cause thread-pool starvation (see the next pattern in this category). The real fix is async propagation.

### Pattern: `async void` swallows exceptions and crashes the process
**Symptom:** An unhandled exception crashes the app instead of being caught by a try/catch. Exception source is an event handler, a `Timer` callback, or a fire-and-forget call. `try { MyAsyncVoidMethod(); } catch { ... }` does not catch anything.
**Why:** `async void` methods have no returned `Task`, so the runtime has nowhere to observe the exception. When one is thrown, the exception is rethrown on the `SynchronizationContext` that was active when the method started — in ASP.NET Core that's the thread pool, and it crashes the process. `async void` is ONLY safe for top-level event handlers (click handlers, `Timer.Elapsed`, etc.) where the framework explicitly supports it, and even there you must catch inside.
**Prove:** Grep the codebase for `async void`. Every hit that isn't a UI event handler is a latent bug. Also check: `Timer` callbacks, `IDisposable.Dispose` overrides, and `IHostedService` that use `async void` lambdas for `ExecuteAsync`-adjacent work.
**Fix:**
```csharp
// WRONG
public async void ProcessAsync() {
    await DoWorkAsync();
    throw new InvalidOperationException("boom"); // crashes the process
}

// RIGHT — return Task, let caller await and catch
public async Task ProcessAsync() {
    await DoWorkAsync();
}

// If you truly need fire-and-forget (rare), wrap in a try/catch:
public async void OnClick(object sender, EventArgs e) {
    try {
        await ProcessAsync();
    }
    catch (Exception ex) {
        _logger.LogError(ex, "unhandled in OnClick");
    }
}
```
For background work in ASP.NET Core, use `IHostedService` / `BackgroundService` — never `async void`.

### Pattern: ThreadPool starvation — "requests are slow" but CPU is idle
**Symptom:** Under moderate load, endpoint latency balloons from 50ms to 10+ seconds. CPU usage is low (< 40%). Database is fast (confirmed via query logs). Adding more replicas fixes it. Memory is fine. Happens only above a specific concurrency threshold.
**Why:** Sync-over-async code somewhere is blocking thread-pool threads. Each blocked thread removes one worker from the pool. When all workers are blocked, new requests queue waiting for a thread — the queue grows faster than the pool can grow (the pool grows by one thread per ~500ms, slowly). Every downstream async operation also queues its continuation behind the starved pool. CPU is idle because threads are blocked, not computing.
**Prove:** Capture `dotnet-counters monitor -n YourApp Microsoft.AspNetCore.Hosting System.Runtime` during the slow period. Look for:
- `System.Runtime threadpool-thread-count` — growing linearly (pool expanding to compensate)
- `System.Runtime threadpool-queue-length` — large and growing (requests waiting for a thread)
- `Microsoft.AspNetCore.Hosting requests-current` — high
- `threadpool-completed-items-per-sec` — low despite high thread count
Run `dotnet-stack report` on the hung process. If most threads show `Task.Wait` / `.Result` / `Thread.Sleep` / `Monitor.Wait` in their stack → confirmed starvation caller.
**Fix:** Find and eliminate every blocking call on a thread-pool thread:
- `.Result`, `.Wait()`, `.GetAwaiter().GetResult()` — replace with `await` (async all the way).
- `Task.Run(() => asyncFunc().Result)` — replace with `await asyncFunc()`.
- `Thread.Sleep` in a request path — replace with `await Task.Delay`.
- Synchronous file/stream I/O (`File.ReadAllText`) — replace with `File.ReadAllTextAsync`.
- Synchronous DB calls inside async action — use `ToListAsync`, `FirstOrDefaultAsync`, etc.
As a temporary relief (NOT a fix), raise `ThreadPool.SetMinThreads(200, 200)` at startup — this lets the pool skip the slow ramp-up. Use only while hunting the real blocker.

---

## CATEGORY 5 — HTTPCLIENT LIFECYCLE

### Pattern: SocketException / port exhaustion — `new HttpClient()` per request
**Symptom:** Under load, outbound HTTP calls start failing with `SocketException: Only one usage of each socket address (protocol/network address/port) is normally permitted`. `netstat -an | findstr TIME_WAIT` shows thousands of connections in `TIME_WAIT`. Restarting the app fixes it for a few minutes, then it returns. Local dev is fine; only production/high-traffic environments reproduce.
**Why:** Every `new HttpClient()` opens its own `HttpClientHandler`, which holds its own connection pool. When disposed, the underlying TCP sockets go into `TIME_WAIT` for the OS-configured interval (default 60–240 seconds on Windows, ~60s on Linux). Creating a new client per request burns a new socket per request. At high RPS you exceed the available ephemeral port range (~28k on Windows by default) and new connections fail.
**Prove:** `netstat -an | grep -c TIME_WAIT` during the failure window. If the count is in the tens of thousands → confirmed. Also check `dotnet-counters monitor System.Net.Http` — `current-connections` and `connections-established` will be climbing.
**Fix:** Never `new HttpClient()`. Always use `IHttpClientFactory`, which pools handlers and rotates them periodically (default every 2 minutes) to also pick up DNS changes:
```csharp
// Program.cs — register a named client
builder.Services.AddHttpClient("api", c => {
    c.BaseAddress = new Uri("https://api.example.com/");
    c.Timeout = TimeSpan.FromSeconds(10);
    c.DefaultRequestHeaders.Add("User-Agent", "MyApp/1.0");
});

// Or a typed client (preferred):
builder.Services.AddHttpClient<OrderApiClient>(c => {
    c.BaseAddress = new Uri("https://api.example.com/");
});

// In code — inject IHttpClientFactory and create per-call:
public class OrderService {
    private readonly IHttpClientFactory _factory;
    public OrderService(IHttpClientFactory f) => _factory = f;

    public async Task<Order> GetAsync(int id) {
        var http = _factory.CreateClient("api");
        return await http.GetFromJsonAsync<Order>($"orders/{id}")
            ?? throw new InvalidOperationException("null order");
    }
}
```
The `HttpClient` returned by `CreateClient` is a thin wrapper — creating it per call is free, the expensive handler is pooled underneath. Never store the returned `HttpClient` in a field.

### Pattern: DNS changes not picked up — HttpClient held as static forever
**Symptom:** App calls `https://api.example.com`. The upstream service changes its IP address (DNS update, failover, blue/green deploy). Your app continues calling the OLD IP for hours after the change, getting `SocketException` or connecting to the old server. Other apps on the same network see the new IP immediately.
**Why:** Before `IHttpClientFactory`, the recommended fix for the port-exhaustion bug was to store a single `static HttpClient` for the app's lifetime. But the underlying `HttpClientHandler` resolves DNS once per connection and caches the connection for the pool lifetime. A long-lived static client keeps the connection open forever, never re-resolving DNS — so DNS changes are invisible until the connection is forcibly closed.
**Prove:** `nslookup api.example.com` from the app's host — compare the IP to what your app is actually connecting to. Capture with `tcpdump host api.example.com` or Process Monitor. If your app is talking to a different IP than nslookup returns → stale connection pool.
**Fix:** Use `IHttpClientFactory` (it rotates handlers every `SetHandlerLifetime(TimeSpan.FromMinutes(2))` by default, picking up DNS). If you absolutely must use a static `HttpClient`, configure the handler to limit connection lifetime:
```csharp
var handler = new SocketsHttpHandler {
    PooledConnectionLifetime = TimeSpan.FromMinutes(2),  // rebuild connections periodically
    PooledConnectionIdleTimeout = TimeSpan.FromSeconds(60),
};
var client = new HttpClient(handler) {
    BaseAddress = new Uri("https://api.example.com/")
};
```
`PooledConnectionLifetime` is the key: it forces the connection (and its cached DNS) to be torn down and rebuilt at that interval. Without it, connections live as long as the handler does.

### Pattern: `HttpClient` timeout set but the request hangs for minutes
**Symptom:** `httpClient.Timeout = TimeSpan.FromSeconds(10)` is set, but a hung upstream causes the call to block for 90+ seconds (the OS's socket timeout) before throwing. Sometimes it hangs indefinitely.
**Why:** `HttpClient.Timeout` only covers the overall request, and only when the socket layer is making progress. DNS resolution, TCP connect, and TLS handshake are each governed by the OS's own timeouts, which can be minutes. A hung TCP `connect()` (e.g. firewall dropping SYN packets silently) is not interrupted by `HttpClient.Timeout` until the OS eventually gives up.
**Prove:** Pass a `CancellationToken` tied to a short `CancellationTokenSource(TimeSpan.FromSeconds(5))` to the request. If the request returns within 5 seconds with `OperationCanceledException` → the token is respected and the OS was the cause of the long hang. If it still hangs → a blocking call somewhere is ignoring the token.
**Fix:** Always pass an explicit `CancellationToken` with a tight deadline for every outbound call. Do NOT rely on `HttpClient.Timeout` alone:
```csharp
public async Task<Order> GetAsync(int id, CancellationToken callerCt) {
    using var cts = CancellationTokenSource.CreateLinkedTokenSource(callerCt);
    cts.CancelAfter(TimeSpan.FromSeconds(5));

    try {
        return await _http.GetFromJsonAsync<Order>($"orders/{id}", cts.Token)
            ?? throw new InvalidOperationException();
    }
    catch (OperationCanceledException) when (!callerCt.IsCancellationRequested) {
        throw new TimeoutException("upstream took too long");
    }
}
```
Also configure `SocketsHttpHandler.ConnectTimeout` to cap DNS+connect+TLS independently:
```csharp
new SocketsHttpHandler {
    ConnectTimeout = TimeSpan.FromSeconds(3),
    PooledConnectionLifetime = TimeSpan.FromMinutes(2),
}
```

---

## CATEGORY 6 — EF CORE CHANGE TRACKING & N+1

### Pattern: N+1 query from lazy loading or `Include` omission
**Symptom:** One list endpoint is 200x slower than expected. Database CPU spikes when that endpoint is hit. SQL log shows 1 outer query plus one query per row in the result, all hitting the same table. Happens only when the list is enumerated — the query itself is fast in isolation.
**Why:** EF Core issues a query per navigation property access unless you explicitly `Include` the relation or project into a DTO. On EF Core 2.1+ with `UseLazyLoadingProxies()` (requires the `Microsoft.EntityFrameworkCore.Proxies` package and virtual navigation properties), simply touching `order.Customer.Name` in a `foreach` loop issues one extra query per order. Without proxies, the property is `null` and you get a `NullReferenceException` instead — fixing that by adding a separate `FirstOrDefault` inside the loop produces the same N+1.
**Prove:** Enable sensitive data logging (development only) and capture the SQL:
```csharp
// Program.cs (Development)
builder.Services.AddDbContext<AppDbContext>(opts => opts
    .UseSqlServer(connectionString)
    .EnableSensitiveDataLogging()
    .LogTo(Console.WriteLine, LogLevel.Information));
```
Hit the endpoint once. Count SQL statements. If you see `SELECT ... FROM Customers WHERE Id = @__p_0` repeating once per row → confirmed N+1. In EF Core 5+, `.ToQueryString()` on an `IQueryable` shows the SQL without executing. Also: `QueryTrackingBehavior.NoTracking` alone does NOT fix N+1 — it only affects change tracking.
**Fix:** Use `Include` / `ThenInclude` for eager loading, OR project directly into a DTO (preferred — sends only the columns you need):
```csharp
// Option A — Include (loads full entity graph)
var orders = await _db.Orders
    .Include(o => o.Customer)
    .Include(o => o.Items).ThenInclude(i => i.Product)
    .Where(o => o.CreatedAt > cutoff)
    .AsNoTracking()                       // read-only → skip change tracking
    .ToListAsync();

// Option B — Projection (preferred for read endpoints)
var orders = await _db.Orders
    .Where(o => o.CreatedAt > cutoff)
    .Select(o => new OrderDto {
        Id = o.Id,
        CustomerName = o.Customer.Name,
        Items = o.Items.Select(i => new ItemDto { Name = i.Product.Name, Qty = i.Qty }).ToList(),
    })
    .ToListAsync();
```
**Bonus trap:** `Include` with multiple one-to-many relations causes a "cartesian explosion" — the SQL joins return `customers × orders × items` rows and EF Core deduplicates in memory. Use `.AsSplitQuery()` to issue one query per `Include`:
```csharp
_db.Orders.Include(o => o.Items).Include(o => o.Comments).AsSplitQuery()...
```
Or globally: `opts.UseSqlServer(cs, o => o.UseQuerySplittingBehavior(QuerySplittingBehavior.SplitQuery));`

### Pattern: `Update` or `SaveChanges` silently does nothing — `AsNoTracking` then `Update`
**Symptom:** Code reads an entity, modifies it, calls `SaveChangesAsync()`, sees no error — but the database is unchanged. Only happens for reads that used `.AsNoTracking()` or projected into a DTO and then manually rebuilt the entity.
**Why:** `AsNoTracking` tells EF Core not to track the returned entity. When you modify and call `SaveChanges`, there are no tracked changes, so EF produces zero UPDATE statements. No error, no warning. Also triggered by: constructing a new entity with the same Id and calling `SaveChanges` without attaching it.
**Prove:** `_db.ChangeTracker.Entries()` after the modification should show the entity with `State == Modified`. If it's not in there, or `State == Detached`, EF doesn't know about it.
**Fix:** Either track the original read, or explicitly update a detached entity:
```csharp
// Option A — don't use AsNoTracking if you intend to save
var order = await _db.Orders.FirstAsync(o => o.Id == id);  // tracked
order.Status = "Shipped";
await _db.SaveChangesAsync();   // UPDATE issued

// Option B — detached update (when you received the entity from outside)
_db.Orders.Update(order);       // marks ALL properties as modified
await _db.SaveChangesAsync();

// Option C — partial detached update (only changed columns)
_db.Entry(order).Property(o => o.Status).IsModified = true;
await _db.SaveChangesAsync();
```
Rule: `AsNoTracking` is only for read-only queries. The moment you mutate and intend to save, you need tracking OR an explicit `Update`/`Attach`.

### Pattern: `Contains` in a LINQ query translates to a massive `IN (...)` and errors on large lists
**Symptom:** Query works for small lists, fails or times out for large ones. SQL Server errors with `The query processor ran out of internal resources` or `The incoming tabular data stream (TDS) remote procedure call (RPC) protocol stream is incorrect`. PostgreSQL errors with a stack overflow in the parser.
**Why:** `where(o => ids.Contains(o.Id))` where `ids` is an `IEnumerable<int>` is translated to `WHERE o.Id IN (@p0, @p1, ... @pN)`. Each `int` becomes a separate parameter. SQL Server caps at 2100 parameters per RPC; PostgreSQL at 32767. Exceeding that cap throws. Even below the cap, plan cache pollution degrades performance as each different list length produces a distinct query plan.
**Prove:** Check the failing query's parameter count: `where(o => ids.Contains(o.Id))` with a 5000-element list → 5000 parameters. Log the SQL via `ToQueryString()` or `LogTo(Console.WriteLine)` — you'll see the enormous IN list.
**Fix:** Three options depending on the EF version and DB:
1. **EF Core 8+ with SQL Server:** `Contains` on a primitive collection is translated using an inlined `OPENJSON` → constant single parameter. No changes needed if you're on EF 8. On EF 7 and below, see below.
2. **Batch the list** and union the results in memory:
   ```csharp
   var results = new List<Order>();
   foreach (var chunk in ids.Chunk(1000)) {
       results.AddRange(await _db.Orders.Where(o => chunk.Contains(o.Id)).ToListAsync());
   }
   ```
3. **Bulk-load via a temp table / table-valued parameter.** Use `dapper` or raw SQL if the working set is large enough to matter.
4. **Use `Any` over a join** if the list actually comes from another table: `from o in _db.Orders where _db.Accounts.Any(a => a.Id == o.AccountId && a.IsActive) select o`.

---

## CATEGORY 7 — EF CORE TRANSACTIONS & CONCURRENCY

### Pattern: Multiple `SaveChangesAsync` calls in one operation — partial writes on exception
**Symptom:** A business operation writes to three tables via three separate `SaveChangesAsync` calls. An exception in the third write leaves tables 1 and 2 updated, table 3 unchanged. Subsequent retries fail uniqueness constraints because of the partial writes. Only reproduces under specific error paths.
**Why:** Each `SaveChangesAsync` opens its own implicit transaction. If the first two succeed and the third throws, the first two are already committed. There is no automatic rollback across `SaveChanges` calls. An ambient `TransactionScope` DOES auto-enlist when a new SQL connection is opened inside it, but only if the scope was created with `TransactionScopeAsyncFlowOption.Enabled` (without it, the ambient scope is lost across the first `await` and the second `SaveChangesAsync` runs outside the transaction — giving you exactly the same partial-write symptom). For clarity and predictability, prefer an explicit `BeginTransactionAsync` over relying on `TransactionScope`.
**Prove:** Grep the business method for multiple `SaveChanges*` calls. Any method with more than one is a candidate. Wrap the whole method in an explicit transaction as the fix test — if the partial-write symptom disappears, this was the cause.
**Fix:** One transaction for the whole operation, one `SaveChanges` at the end. If you need intermediate IDs (auto-increment keys), use an explicit transaction:
```csharp
// Option A — single SaveChanges (preferred when possible)
_db.Orders.Add(order);
_db.OrderItems.AddRange(items);
_db.AuditEntries.Add(audit);
await _db.SaveChangesAsync();  // one transaction, all-or-nothing

// Option B — explicit transaction when you need intermediate IDs
await using var tx = await _db.Database.BeginTransactionAsync();
try {
    _db.Orders.Add(order);
    await _db.SaveChangesAsync();          // order.Id now populated

    foreach (var i in items) { i.OrderId = order.Id; _db.OrderItems.Add(i); }
    await _db.SaveChangesAsync();

    _db.AuditEntries.Add(new AuditEntry { OrderId = order.Id, Action = "created" });
    await _db.SaveChangesAsync();

    await tx.CommitAsync();
}
catch {
    await tx.RollbackAsync();
    throw;
}
```
Do NOT use `TransactionScope` casually — it's ambient and interacts poorly with async without `TransactionScopeAsyncFlowOption.Enabled`, and on SQL Server it promotes to MSDTC if more than one connection enlists.

### Pattern: `DbUpdateConcurrencyException` after adding a `[Timestamp]` / `RowVersion` column
**Symptom:** Any update throws `DbUpdateConcurrencyException: The database operation was expected to affect 1 row(s), but actually affected 0 row(s).` Happens every time, not under concurrency. Started after a migration added a `RowVersion byte[]` property.
**Why:** When EF Core sees a `[Timestamp]` or `IsConcurrencyToken()` property, it adds a `WHERE RowVersion = @oldValue` clause to every UPDATE. If the entity was loaded and the RowVersion has since changed (or was never loaded, e.g. on an `Attach` of a detached entity built from a DTO), the WHERE matches zero rows and EF throws.
**Prove:** Log the generated SQL. You'll see `UPDATE Orders SET Status = @p0 WHERE Id = @p1 AND RowVersion = @p2`. Check whether `@p2` matches the current database value — if the entity came from a detached source (DTO from the wire), the RowVersion was never set.
**Fix:** Always round-trip the concurrency token:
```csharp
// DTO must expose RowVersion and send it back
public class OrderUpdateDto {
    public int Id { get; set; }
    public string Status { get; set; }
    public byte[] RowVersion { get; set; }   // client sends back what it received
}

// Server-side update
public async Task UpdateAsync(OrderUpdateDto dto) {
    var order = new Order { Id = dto.Id, Status = dto.Status, RowVersion = dto.RowVersion };
    _db.Orders.Attach(order);
    _db.Entry(order).Property(o => o.Status).IsModified = true;
    // RowVersion stays unmodified in the WHERE clause — concurrency check still applies

    try {
        await _db.SaveChangesAsync();
    }
    catch (DbUpdateConcurrencyException) {
        // Reload current DB state, merge, retry — or surface a 409 Conflict to client
        throw new ConflictException("Order was modified by another user; reload and retry.");
    }
}
```
If you truly want "last write wins" (no concurrency check), remove the `[Timestamp]` attribute — don't silently swallow the exception, it hides real conflicts.

### Pattern: Long-running DbContext accumulates tracked entities — memory grows, queries slow down
**Symptom:** A background worker using a single `DbContext` for hours sees memory grow, queries progressively slow, and `SaveChangesAsync` takes longer each time. Restarting the worker resets the symptom. Each work item individually is small.
**Why:** A `DbContext` is designed to be short-lived — one per unit of work, typically one per HTTP request. The `ChangeTracker` accumulates every entity ever loaded, and `SaveChanges` has to iterate all of them to detect changes. Hours of accumulation = a tracker with millions of entities = linear-time `DetectChanges` on every save.
**Prove:** Log `_db.ChangeTracker.Entries().Count()` periodically. If it grows monotonically, this is the bug. Also: `dotnet-counters monitor Microsoft.EntityFrameworkCore` — `query-duration` climbing.
**Fix:** One `DbContext` per unit of work. In a background worker loop, create a new scope per iteration:
```csharp
protected override async Task ExecuteAsync(CancellationToken ct) {
    while (!ct.IsCancellationRequested) {
        using var scope = _scopeFactory.CreateScope();
        var db = scope.ServiceProvider.GetRequiredService<AppDbContext>();
        await ProcessOneBatchAsync(db, ct);
        // db disposed here, fresh tracker next iteration
        await Task.Delay(TimeSpan.FromSeconds(5), ct);
    }
}
```
If you MUST reuse a DbContext (don't), call `_db.ChangeTracker.Clear()` after each batch. Combine with `AsNoTracking()` reads to minimize accumulation, but prefer the scope-per-iteration pattern.

---

## CATEGORY 8 — SERIALIZATION (System.Text.Json / Newtonsoft)

### Pattern: JSON property silently drops — case mismatch between camelCase payload and PascalCase DTO
**Symptom:** Client sends `{ "firstName": "Ada" }`. Server DTO has `public string FirstName { get; set; }`. The deserialized object has `FirstName == null`. No error, no warning. Switching to `"FirstName"` in the payload fixes it.
**Why:** `System.Text.Json` is case-sensitive by default. When ASP.NET Core configures MVC with `AddControllers().AddJsonOptions(...)`, it sets `PropertyNameCaseInsensitive = true` AND `PropertyNamingPolicy = CamelCase` — but those options apply only to the MVC pipeline. If you deserialize manually elsewhere (a message handler, a hosted service reading from a queue, a manual `JsonSerializer.Deserialize<T>(...)` call), you get the default case-sensitive behavior and properties silently drop.
**Prove:** Search for every `JsonSerializer.Deserialize` call in the codebase. If it's called without a `JsonSerializerOptions` argument, it's using the default (case-sensitive). Compare with MVC's behavior — MVC works because its pipeline passes pre-configured options.
**Fix:** Centralize the options and pass them to every manual deserialization:
```csharp
// Program.cs — register as a singleton so everywhere can inject it
builder.Services.AddSingleton(new JsonSerializerOptions(JsonSerializerDefaults.Web) {
    PropertyNameCaseInsensitive = true,           // default in Web defaults
    PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
    DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull,
});

// In any service that deserializes manually:
public class QueueHandler {
    private readonly JsonSerializerOptions _json;
    public QueueHandler(JsonSerializerOptions json) => _json = json;

    public Task HandleAsync(string payload) {
        var msg = JsonSerializer.Deserialize<MyMessage>(payload, _json);
        // ...
    }
}
```
`JsonSerializerDefaults.Web` is the shorthand for "match what ASP.NET Core Web APIs do" — it sets `PropertyNameCaseInsensitive = true` and `PropertyNamingPolicy = CamelCase`.

### Pattern: `StackOverflowException` or 413 Payload Too Large on serializing EF entity graph
**Symptom:** Returning an EF Core entity directly from a controller throws `StackOverflowException` or times out producing a massive JSON response. Or: serializer throws `JsonException: A possible object cycle was detected`. Only happens when the entity has a navigation property that navigates back to itself.
**Why:** EF entities commonly have bidirectional navigations (`Order.Customer` and `Customer.Orders`). System.Text.Json walks every property on serialization. Since .NET Core 3.0, STJ has always detected object cycles and thrown `JsonException("A possible object cycle was detected which is not supported...")` by default. .NET 6 added the friendlier `ReferenceHandler.IgnoreCycles` option, and `ReferenceHandler.Preserve` for `$id`/`$ref` emission. Even with cycle detection, non-cyclic-but-oversized graphs (`Order.Customer.Orders.Customer.Orders...` on a graph that isn't strictly self-referential) pull in enormous slices of the database when serialized naively, and the cost shows up as a huge response body and slow endpoint, not an exception.
**Prove:** Temporarily return `order.Id` only. If that works but returning `order` crashes → cyclic or oversized graph.
**Fix:** **Never return EF entities directly from a controller.** Project into a DTO:
```csharp
// WRONG — returns the tracked entity with all its navigations
[HttpGet("{id}")]
public async Task<Order> Get(int id) => await _db.Orders.FindAsync(id);

// RIGHT — return a DTO with exactly the fields the client needs
[HttpGet("{id}")]
public async Task<OrderDto> Get(int id) => await _db.Orders
    .Where(o => o.Id == id)
    .Select(o => new OrderDto {
        Id = o.Id,
        CustomerName = o.Customer.Name,
        Items = o.Items.Select(i => new ItemDto { Id = i.Id, Name = i.Product.Name }).ToList(),
    })
    .FirstOrDefaultAsync()
    ?? throw new NotFoundException();
```
If you absolutely cannot use DTOs (rapid prototype), configure the global JSON options with `ReferenceHandler.Preserve` (adds `$id`/`$ref` markers) or `ReferenceHandler.IgnoreCycles` (nulls out the back-reference). Both change the wire format and confuse non-.NET clients — DTO projection is the correct fix.

### Pattern: `JsonElement` / `JsonDocument` disposed after method returns — `ObjectDisposedException`
**Symptom:** Parsing a JSON payload with `JsonDocument.Parse(body)` works inside the method. Passing the parsed object up returns a `JsonElement` that throws `ObjectDisposedException` when accessed by the caller. Stack trace points at `JsonElement.GetProperty`.
**Why:** `JsonDocument` pools its internal buffer. When disposed, the buffer returns to the pool and any `JsonElement` previously handed out becomes invalid (it holds a reference into the buffer). A `using var doc = JsonDocument.Parse(...)` at the end of the method disposes the document on return, invalidating every `JsonElement` the caller still holds.
**Prove:** Check the lifetime: if `JsonDocument.Parse` is inside a `using` block and you return a `JsonElement` out of that block, this is it.
**Fix:** Either clone the `JsonElement` (it allocates a new independent tree), or deserialize into a POCO:
```csharp
// Option A — clone for caller ownership
public JsonElement ParseRoot(string body) {
    using var doc = JsonDocument.Parse(body);
    return doc.RootElement.Clone();   // standalone copy, safe after doc disposes
}

// Option B — deserialize into a strongly-typed DTO (preferred)
public MyDto Parse(string body) => JsonSerializer.Deserialize<MyDto>(body, _opts)
    ?? throw new InvalidOperationException("null");
```
Use `JsonDocument` only for very large payloads where you scan once without allocating POCOs.

---

## CATEGORY 9 — CONFIGURATION & IOptions

### Pattern: `appsettings.Production.json` never loads — environment variable not set
**Symptom:** App runs fine locally with `appsettings.Development.json` values. Deployed to production, it either uses `appsettings.json` defaults or crashes because a required section is missing. `appsettings.Production.json` IS in the deploy artifact and IS readable. Setting the values directly in `appsettings.json` works.
**Why:** ASP.NET Core picks which environment file to overlay based on `IHostEnvironment.EnvironmentName`, which is set from the `ASPNETCORE_ENVIRONMENT` environment variable (or `DOTNET_ENVIRONMENT` for generic host). If that variable is not set at runtime, `EnvironmentName` defaults to `Production` — BUT the file name must exactly match (case-sensitive on Linux). Common failures: variable misspelled (`ASPNET_ENVIRONMENT`), set in the wrong shell (set but not exported), value is `production` lowercase on a Linux host where the file is `appsettings.Production.json`, or set in a `systemd` unit without `Environment=`.
**Prove:** Add a startup log line:
```csharp
Console.WriteLine($"[ENV] Name={app.Environment.EnvironmentName}");
Console.WriteLine($"[ENV] File loaded? {File.Exists($"appsettings.{app.Environment.EnvironmentName}.json")}");
```
If the printed name doesn't match what you expect, the env var is wrong or unset. If the name is right but the file doesn't exist, the filename casing is wrong (Linux).
**Fix:**
- **Docker:** `ENV ASPNETCORE_ENVIRONMENT=Production` in the Dockerfile, or `-e ASPNETCORE_ENVIRONMENT=Production` on `docker run`.
- **systemd:** `Environment=ASPNETCORE_ENVIRONMENT=Production` in the `[Service]` section.
- **IIS:** set in `web.config` `<environmentVariables>` or via ` appcmd`.
- **Kubernetes:** put it in the pod spec `env:` list.
- **Linux casing:** rename the file to match exactly — `appsettings.Production.json` (uppercase P).
Always `Console.WriteLine` the environment name at startup so deployment mismatches are visible in the first log line.

### Pattern: Secret value from User Secrets / KeyVault reads empty in production — provider not registered
**Symptom:** `_config["ConnectionStrings:Default"]` returns a non-null string in development (pulled from User Secrets) but returns empty in production even though the secret IS in Azure Key Vault / AWS Secrets Manager. Other config values from `appsettings.json` load fine.
**Why:** The configuration builder loads providers in order; later providers overlay earlier ones. User Secrets is auto-registered by `WebApplication.CreateBuilder` when `EnvironmentName == Development`. Key Vault / Secrets Manager is NOT auto-registered — you must add it explicitly in `Program.cs`. Missing that `.AddAzureKeyVault(...)` / `.AddSecretsManager()` call leaves the secret unreachable at runtime, but with no error.
**Prove:** Iterate the configuration providers: `((IConfigurationRoot)_config).GetDebugView()` prints every key with its source. If the key is not listed, no provider is supplying it. If it IS listed but empty, the provider is registered but returning empty (permission issue, wrong key name).
**Fix:**
```csharp
// Program.cs — add the production secret provider before Build()
if (builder.Environment.IsProduction()) {
    builder.Configuration.AddAzureKeyVault(
        new Uri($"https://{builder.Configuration["KeyVault:Name"]}.vault.azure.net/"),
        new DefaultAzureCredential()
    );
}
```
For Kubernetes Secrets, mount them as files and use `AddKeyPerFile`:
```csharp
builder.Configuration.AddKeyPerFile("/etc/secrets", optional: true, reloadOnChange: true);
```
Also: Key Vault secret names replace `:` with `--` by convention. `ConnectionStrings:Default` in Key Vault is the secret named `ConnectionStrings--Default`.

### Pattern: Strongly typed options class has property that is always default — missing setter or wrong section name
**Symptom:** `services.Configure<SmtpOptions>(Configuration.GetSection("Smtp"))`. At runtime, `_opts.Value.Host` is empty even though `appsettings.json` clearly has `"Smtp": { "Host": "smtp.example.com" }`. Other properties in the same class bind correctly.
**Why:** Three candidates:
1. The section name doesn't match: `GetSection("SMTP")` when the JSON key is `"Smtp"`. Configuration keys are case-insensitive on Windows but case-sensitive on Linux for the underlying provider in older .NET versions — don't rely on it.
2. The property has no public setter, or is `init`-only and the binder version doesn't support `init` (pre-.NET 6 System.ComponentModel binder).
3. The property type doesn't match the JSON — e.g., class has `int Port` but JSON has `"Port": "2525"` as a string. The binder silently skips unmatched properties.
**Prove:** Temporarily validate the bound options at startup with `ValidateOnStart`:
```csharp
builder.Services.AddOptions<SmtpOptions>()
    .Bind(builder.Configuration.GetSection("Smtp"))
    .Validate(o => !string.IsNullOrWhiteSpace(o.Host), "SMTP Host required")
    .ValidateOnStart();
```
The app now fails at startup if Host is empty, instead of hours later when the first email send crashes. Also dump the raw section: `Console.WriteLine(builder.Configuration.GetSection("Smtp").GetDebugView());`.
**Fix:** Match the section name exactly, give every option property a public setter (or use a record with a primary constructor in .NET 8+ which the binder supports), and match types exactly. Combine with `ValidateDataAnnotations()` to catch `[Required]` attributes at startup:
```csharp
public class SmtpOptions {
    [Required] public string Host { get; set; } = "";
    [Range(1, 65535)] public int Port { get; set; }
    public string User { get; set; } = "";
    public string Password { get; set; } = "";
}

builder.Services.AddOptions<SmtpOptions>()
    .Bind(builder.Configuration.GetSection("Smtp"))
    .ValidateDataAnnotations()
    .ValidateOnStart();
```
Rule: every options class should validate at startup. Invalid config should prevent boot, not produce surprises at runtime.

---

## CATEGORY 10 — KESTREL / IIS / REVERSE PROXY HOSTING

### Pattern: Behind nginx/AWS ALB/CloudFront, `HttpContext.Connection.RemoteIpAddress` is the proxy, not the client
**Symptom:** Rate limiting, audit logging, and IP allowlists all see `10.0.0.x` (the load balancer's private IP) or `127.0.0.1`, never the real client IP. `X-Forwarded-For` header IS present in the request. `HttpContext.Request.Scheme` is `http` even though the public URL is HTTPS, causing generated URLs to be wrong and OAuth redirect URIs to break.
**Why:** ASP.NET Core does NOT trust proxy headers by default, for security (spoofing). You must explicitly register `UseForwardedHeaders` AND configure which proxies are allowed to set those headers. Without it, Kestrel sees the proxy's TCP connection and reports that as the client.
**Prove:** Log `HttpContext.Connection.RemoteIpAddress` and `HttpContext.Request.Headers["X-Forwarded-For"]` at the top of a probe endpoint. If the former is the LB IP while the latter contains the real client IP → ForwardedHeaders middleware is missing.
**Fix:** Add the middleware FIRST, before any other middleware that cares about scheme or IP (auth, logging, rate limiting):
```csharp
using Microsoft.AspNetCore.HttpOverrides;
// NOTE: on .NET 8+, also disambiguate — System.Net.IPNetwork was added in .NET 8
// and will collide with Microsoft.AspNetCore.HttpOverrides.IPNetwork if both namespaces
// are in scope. Use the fully qualified name if you hit CS0104:
// using AspIpNetwork = Microsoft.AspNetCore.HttpOverrides.IPNetwork;

// Program.cs
builder.Services.Configure<ForwardedHeadersOptions>(options => {
    options.ForwardedHeaders = ForwardedHeaders.XForwardedFor | ForwardedHeaders.XForwardedProto;
    // CRITICAL: restrict which proxies are allowed to set the headers
    options.KnownProxies.Clear();
    options.KnownNetworks.Clear();
    // Add your LB / nginx subnet — do NOT leave this empty in production
    options.KnownNetworks.Add(new Microsoft.AspNetCore.HttpOverrides.IPNetwork(
        IPAddress.Parse("10.0.0.0"), 16));
});

var app = builder.Build();

app.UseForwardedHeaders();   // <- FIRST, before UseRouting
app.UseRouting();
// ... rest of pipeline
```
**Security note:** leaving `KnownProxies` empty effectively trusts anyone who can reach your Kestrel port. If an attacker can hit Kestrel directly (bypassing the LB), they can spoof `X-Forwarded-For`. Always enumerate your actual proxy network.

### Pattern: Request body larger than 30MB gets `413 Payload Too Large` or `RequestBodyTooLargeException`
**Symptom:** File uploads or large JSON payloads fail at exactly 28–30MB. Below that threshold they work. Client gets a 413 or a closed connection with no response body.
**Why:** Two limits stack in ASP.NET Core:
1. **Kestrel**'s `MaxRequestBodySize` defaults to 30 MB (`30_000_000` bytes).
2. **Individual endpoint**'s form options or controller's `[RequestSizeLimit]`.
3. On IIS, `maxAllowedContentLength` in `web.config` defaults to 30MB and is applied BEFORE the request reaches Kestrel.
4. On nginx, `client_max_body_size` defaults to 1MB and aborts the upload upstream.
Any one of them being lower than your payload will fail the upload.
**Prove:** Start with the browser network tab — if the upload aborts before reaching Kestrel, it's nginx or IIS. If the request reaches Kestrel and then fails, it's Kestrel's limit. Log `BadHttpRequestException: Request body too large` in the Kestrel logs to confirm.
**Fix:** Raise all limits to the same explicit ceiling — and set it deliberately, don't remove the limit:
```csharp
// Program.cs — Kestrel global limit
builder.WebHost.ConfigureKestrel(o => {
    o.Limits.MaxRequestBodySize = 100 * 1024 * 1024;  // 100 MB
});

// For a specific upload endpoint, override per-action:
[HttpPost("upload")]
[RequestSizeLimit(100 * 1024 * 1024)]
[RequestFormLimits(MultipartBodyLengthLimit = 100 * 1024 * 1024)]
public async Task<IActionResult> Upload(IFormFile file) { ... }
```
For IIS: `<requestLimits maxAllowedContentLength="104857600" />` in `web.config`. For nginx: `client_max_body_size 100m;` in the server block. **Never set any of these to `0` / unlimited** — that turns into a DoS vector.

### Pattern: App runs in IIS but `HostingEnvironment` is wrong / `appsettings.*.json` wrong file loads
**Symptom:** Same binary works correctly from `dotnet run` with `ASPNETCORE_ENVIRONMENT=Staging`, but when hosted in IIS it loads `appsettings.Production.json`. Environment variables set at the OS level don't reach the app.
**Why:** IIS runs the .NET app either in-process inside `w3wp.exe` or out-of-process as a child `dotnet.exe`. Either way, the app pool worker process inherits system environment variables only AT its launch time — same rules as any Windows process. If a system-level env var is added or changed AFTER the pool started, `w3wp.exe` does not see the new value until the app pool recycles (and in some cases you also need to restart WAS/IIS to pick up a brand-new variable). Because app pools are long-lived, this makes "set env var at the OS level" unreliable in practice. The reliable, version-controlled approach is to declare env vars inside `web.config`'s `<aspNetCore><environmentVariables>` section, which applies at every pool recycle regardless of OS-level state.
**Prove:** Hit `/probe` and log `Environment.GetEnvironmentVariable("ASPNETCORE_ENVIRONMENT")`. If it's `Production` (the default when unset) but you expected `Staging`, IIS is not passing the var.
**Fix:** Declare in `web.config`:
```xml
<configuration>
  <system.webServer>
    <aspNetCore processPath="dotnet" arguments=".\MyApp.dll" hostingModel="inprocess">
      <environmentVariables>
        <environmentVariable name="ASPNETCORE_ENVIRONMENT" value="Staging" />
        <environmentVariable name="ConnectionStrings__Default" value="Server=..." />
      </environmentVariables>
    </aspNetCore>
  </system.webServer>
</configuration>
```
Note the `__` double underscore — that's the IIS/env-var-to-config-key syntax for nested sections (`ConnectionStrings:Default` becomes `ConnectionStrings__Default`).

---

## CATEGORY 11 — CONCURRENCY PRIMITIVES & THREAD SAFETY

### Pattern: `SemaphoreSlim` leaks a permit — `Release` skipped on exception
**Symptom:** A method that guards critical work with `await _semaphore.WaitAsync()` + `_semaphore.Release()` works for the first N requests. After some exceptions in production, it stops accepting ANY requests and every caller hangs on `WaitAsync` forever. Restarting the app fixes it for a while.
**Why:** `Release` was called after `try`/`finally` not inside `finally`, or it was called on a code path that isn't always hit. When the guarded work throws, `Release` is skipped, the semaphore count drops by one permanently, and eventually the count reaches zero and hangs everyone. `SemaphoreSlim` does not auto-release on exception (unlike `lock { }` which releases the monitor).
**Prove:** Log `_semaphore.CurrentCount` periodically. If it trends down monotonically and never recovers, some code path is taking without releasing. Review every `WaitAsync` call — the matching `Release` MUST be in a `finally` block.
**Fix:**
```csharp
// WRONG
await _semaphore.WaitAsync(ct);
await DoWorkAsync(ct);           // throws → Release never runs
_semaphore.Release();

// RIGHT
await _semaphore.WaitAsync(ct);
try {
    await DoWorkAsync(ct);
}
finally {
    _semaphore.Release();        // always runs
}
```
**Also watch:** `WaitAsync` with a timeout that returns `false` — you must NOT call `Release` in that case (you didn't acquire). Capture the result:
```csharp
if (!await _semaphore.WaitAsync(TimeSpan.FromSeconds(5), ct)) {
    throw new TimeoutException();  // didn't acquire — don't release
}
try { await DoWorkAsync(ct); }
finally { _semaphore.Release(); }
```

### Pattern: `ConcurrentDictionary.GetOrAdd` with an expensive factory runs the factory multiple times
**Symptom:** A cache built on `ConcurrentDictionary.GetOrAdd(key, factory)` has a race where the factory (an expensive API call, a DB hit, or a cryptographic compute) runs 2–5 times for the same missing key under concurrent load. The cache works, but the "load once" invariant is broken.
**Why:** `ConcurrentDictionary.GetOrAdd(key, valueFactory)` is NOT atomic: the factory can be called by multiple threads racing to add the same key, and only the first-completing thread's value wins. The others' factory calls are wasted. For an async factory (`GetOrAdd` doesn't support async directly — you pass `Task<T>`), you can get worse outcomes: multiple in-flight tasks, ambiguous ownership, multiple disposals.
**Prove:** Increment a counter in the factory and log it. Hit the cold cache with 10 concurrent requests for the same key. If the counter > 1, the factory raced.
**Fix:** Cache `Lazy<T>` or `Lazy<Task<T>>` — which DOES serialize first-time initialization:
```csharp
private readonly ConcurrentDictionary<string, Lazy<Task<User>>> _cache = new();

public Task<User> GetUserAsync(string id) =>
    _cache.GetOrAdd(id, k => new Lazy<Task<User>>(() => LoadUserFromDbAsync(k))).Value;
```
The `Lazy<T>` is cheap to construct — multiple threads may still create `Lazy` instances, but only the first-inserted one's `.Value` is ever accessed, and `Lazy<T>` internally uses a lock so the factory runs exactly once. The wasted `Lazy` instances are garbage-collected.

### Pattern: `Interlocked.Increment` works, but a read-then-decide-then-write pattern races
**Symptom:** A counter tracks something like "current active connections". `Interlocked.Increment(ref _count)` is used for add. `if (_count > limit) reject; else process();` appears thread-safe but under load too many requests pass the check.
**Why:** `_count > limit` reads the current count, then the code takes a decision. Between read and any subsequent action, other threads can increment. Classic check-then-act race. `Interlocked` primitives make individual operations atomic but do NOT make compound read-decide-write sequences atomic.
**Prove:** Log `_count` at decision time and at action time. Under load you'll see values different at the two points.
**Fix:** Two options:
1. **`Interlocked.CompareExchange` loop** — atomic check-and-update:
   ```csharp
   while (true) {
       int current = _count;
       if (current >= limit) throw new TooManyRequestsException();
       if (Interlocked.CompareExchange(ref _count, current + 1, current) == current)
           break;   // we won the race, proceed
       // someone else changed it; retry
   }
   try { await DoWorkAsync(); }
   finally { Interlocked.Decrement(ref _count); }
   ```
2. **`SemaphoreSlim(limit, limit)`** — simpler and more readable for "at most N concurrent":
   ```csharp
   private static readonly SemaphoreSlim _limiter = new(100, 100);

   if (!await _limiter.WaitAsync(TimeSpan.Zero, ct))
       throw new TooManyRequestsException();
   try { await DoWorkAsync(ct); }
   finally { _limiter.Release(); }
   ```
Rule: if your concurrency check uses two statements to inspect and act, it's racy. Either use an atomic CAS or a synchronization primitive designed for the count.

---

## CATEGORY 12 — .NET VERSION MIGRATION GOTCHAS

### Pattern: After Npgsql 5 → 6 upgrade, writing `DateTime` to PostgreSQL `timestamptz` throws
**Symptom:** Code that stored `DateTime.UtcNow` in a PostgreSQL `timestamp with time zone` column worked previously, now throws `Cannot write DateTime with Kind=Unspecified to PostgreSQL type 'timestamp with time zone', only UTC is supported.` at every INSERT/UPDATE. Started after an Npgsql version bump — which commonly coincides with a .NET version upgrade but is not caused by it (Npgsql 5 on .NET 8 is fine; Npgsql 6 on .NET 6 hits the bug).
**Why:** Npgsql 6.0 (released late 2021) introduced a strict mode where `timestamp with time zone` accepts ONLY `DateTime` values with `Kind == Utc`. `Kind == Unspecified` (the default for `DateTime.Parse("2024-01-01")`, deserialization from JSON strings without a `Z` or offset, `DateTime.Now`, or DB reads of `timestamp without time zone` columns) now throws. This change is in the Npgsql 6 release notes, not in any .NET release notes — which is why it's missed during upgrades. The fix is NOT to switch the DB column type — it's to ensure every `DateTime` written is explicitly UTC.
**Prove:** Check the package version of `Npgsql.EntityFrameworkCore.PostgreSQL` (or `Npgsql` directly) in the project — if it's `>= 6.0.0`, the new behavior is in effect. Log `myDate.Kind` at the point of write. If it's `Unspecified` → this is the bug. Deserialization is the most common culprit: `JsonSerializer.Deserialize<MyDto>(json)` where `json` contains `"2024-01-01T10:00:00"` (no timezone designator) produces `Kind == Unspecified`.
**Prove:** Log `myDate.Kind` at the point of write. If it's `Unspecified` → this is the bug. Deserialization is the most common culprit: `JsonSerializer.Deserialize<MyDto>(json)` produces `DateTime` values with `Kind == Unspecified` unless the string includes `Z` or a `+00:00` offset.
**Fix:** Three layers:
1. **Use `DateTimeOffset` in API contracts** — preserves offset through JSON, avoids the question entirely.
2. **Normalize at write time:** `DateTime.SpecifyKind(value, DateTimeKind.Utc)` — ONLY if you are certain the value is already in UTC. Never SpecifyKind on a local-time value; that silently lies.
3. **Opt out of the new Npgsql behavior (temporary)** — sets the global switch to restore .NET 6 semantics:
   ```csharp
   AppContext.SetSwitch("Npgsql.EnableLegacyTimestampBehavior", true);
   ```
   Use only as a bridge while migrating; commit to #1 or #2 before the next upgrade.

### Pattern: Nullable reference types flagged a property as non-null, EF Core migrations added NOT NULL, now inserts fail
**Symptom:** After enabling `<Nullable>enable</Nullable>` in `.csproj`, running `dotnet ef migrations add ...` generated a migration that added `NOT NULL` to existing columns that had rows with nulls. Migration apply fails with `null value in column violates not-null constraint`.
**Why:** EF Core treats a non-nullable reference type (`public string Name { get; set; }` with NRT enabled) as a required column. Enabling NRT flipped every non-`?` string property from `nullable` to `not null` in the model snapshot, producing an aggressive migration.
**Prove:** Open the generated migration file. If you see `AlterColumn<string>(... nullable: false, oldNullable: true)` for many columns, this is the pattern.
**Fix:** Decide per-column whether it should truly be `NOT NULL`:
- If yes, backfill the existing nulls first (separate data migration), THEN run the EF migration.
- If no, mark the property as nullable in the model:
  ```csharp
  public string? Name { get; set; }   // now migration will leave it nullable
  ```
Or, if you know the column SHOULD stay nullable but the NRT annotation must be non-null for application logic, explicitly configure:
```csharp
modelBuilder.Entity<User>()
    .Property(u => u.Name)
    .IsRequired(false);   // overrides NRT inference for the column
```
Review every "AlterColumn nullable: false" in a post-NRT migration. Blindly applying the migration is a data loss risk.

### Pattern: Minimal API endpoint returns 500 with `JsonException` after .NET 7 → 8 upgrade — source-generated serializer
**Symptom:** `app.MapGet("/orders", ...)` returned JSON fine on .NET 7. After upgrading to .NET 8, it returns 500 with `JsonException: Metadata for type 'Order' was not provided to the serializer`. Only affects Minimal API + AOT projects, or projects that opted into source-generated serialization.
**Why:** .NET 8 Minimal APIs can be compiled with AOT and use source-generated JSON metadata instead of runtime reflection. The source generator needs every type it serializes registered in a `JsonSerializerContext`. Missing types are not auto-detected — they fail at runtime inside the generator's fallback path.
**Prove:** Error message names the missing type. Also check `Program.cs` for `JsonSerializerContext` registration — if present, any type not in the generator's `[JsonSerializable]` list will fail.
**Fix:** Add every DTO to the context:
```csharp
[JsonSerializable(typeof(Order))]
[JsonSerializable(typeof(Order[]))]
[JsonSerializable(typeof(ProblemDetails))]
public partial class AppJsonContext : JsonSerializerContext { }

// Program.cs
builder.Services.ConfigureHttpJsonOptions(o => {
    o.SerializerOptions.TypeInfoResolverChain.Insert(0, AppJsonContext.Default);
});
```
If you don't need AOT: simply don't register a `JsonSerializerContext`, and .NET falls back to runtime reflection which serializes anything. AOT is opt-in; the runtime fallback is the default for non-AOT builds.

### Pattern: `IAsyncEnumerable<T>` returned from a controller — truncated array, `ObjectDisposedException`, or hang
**Symptom:** Endpoint returns `IAsyncEnumerable<Order>` (with `yield return`). Depending on the specific failure mode, the client sees one of:
(a) A truncated JSON array — e.g. 3 items followed by the connection closing, or the bytes `[{...},{...},` with no closing bracket.
(b) A 500 with `ObjectDisposedException: Cannot access a disposed context instance` in server logs, thrown mid-stream.
(c) A successful first item, then the endpoint hangs for minutes before the client times out.
(d) Empty `[]` with no server-side error logged.
Adjacent endpoints returning `List<Order>` work fine.
**Why — NOT buffering.** ASP.NET Core + System.Text.Json have streamed `IAsyncEnumerable<T>` responses end-to-end since .NET 6; items are serialized as they are produced. The failures above are from a different set of causes, all related to iterator lifetime and cancellation:
1. **DbContext disposed before enumeration completes.** The controller returns the `IAsyncEnumerable` immediately, and the framework begins iterating it while writing the response. If the iterator body touches a DbContext that was resolved from the request scope, the scope may end (response completes) before the iterator finishes — giving `ObjectDisposedException` mid-stream and a truncated array. Using `AsAsyncEnumerable()` over a DbContext query inside a controller method that returns the enumerator is exactly this trap.
2. **`[EnumeratorCancellation]` attribute missing on the `CancellationToken` parameter.** Without it, the framework cannot pass the request-abort token into the iterator, so the iterator never observes cancellation and keeps running after the client disconnects — at best wasting work, at worst hanging on a downstream call.
3. **Iterator blocking on an unfired signal.** Something inside the `await foreach` body (a `Channel.Reader.ReadAsync`, `SemaphoreSlim.WaitAsync`, or awaiting a `TaskCompletionSource` that never completes) blocks forever. The response is flushed up to the last `yield return` and then hangs.
4. **Error mid-stream.** Once the first item is written, the response status code is already 200 and the headers are flushed. An exception thrown on item N cannot surface as a JSON error body — the client just sees a truncated array and no clean 500.

**Prove:** Log entry, each `yield return`, and exit of the iterator. Also log `CancellationToken.IsCancellationRequested` on each iteration. Mappings:
- Entry logs but no yields → iterator is blocked before the first item (cause 3).
- Yields stop mid-stream with `ObjectDisposedException` in logs → cause 1 (DbContext lifetime).
- Yields stop mid-stream with a non-disposed exception → cause 4 (error mid-stream).
- Yields continue after client disconnected (check with `curl --max-time 1`) → cause 2 (missing `[EnumeratorCancellation]`).

**Fix:**
1. **Materialize inside the controller scope when the row count is bounded.** For any list endpoint under ~10k rows, return `List<T>` — not `IAsyncEnumerable<T>`. The DbContext stays alive for exactly one `ToListAsync()` and everything about the streaming failure mode goes away:
   ```csharp
   [HttpGet]
   public async Task<List<Order>> Get() =>
       await _db.Orders.AsNoTracking().ToListAsync();
   ```
2. **If you must stream**, always annotate the cancellation token and await each item so the DbContext stays alive for the whole enumeration. Do NOT return an `IAsyncEnumerable` that closes over a request-scoped DbContext without this:
   ```csharp
   [HttpGet]
   public async IAsyncEnumerable<Order> Stream(
       [EnumeratorCancellation] CancellationToken ct)    // <-- required
   {
       // Hold the context alive for the full enumeration by iterating inside the method
       await foreach (var o in _db.Orders.AsNoTracking().AsAsyncEnumerable().WithCancellation(ct)) {
           yield return o;
       }
       // When this method's async state machine completes, the request scope (and
       // therefore _db) is still alive — because the framework is iterating THIS method.
   }
   ```
3. **For truly large results, use NDJSON** (`application/x-ndjson`), not a JSON array. NDJSON is one complete JSON object per line, so a truncation leaves N complete objects and zero malformed ones — the client can detect EOF mid-stream and recover. Write it directly to `Response.Body`:
   ```csharp
   [HttpGet, Produces("application/x-ndjson")]
   public async Task Stream(CancellationToken ct) {
       Response.ContentType = "application/x-ndjson";
       await foreach (var o in _db.Orders.AsNoTracking().AsAsyncEnumerable().WithCancellation(ct)) {
           await JsonSerializer.SerializeAsync(Response.Body, o, cancellationToken: ct);
           await Response.Body.WriteAsync("\n"u8.ToArray(), ct);
           await Response.Body.FlushAsync(ct);
       }
   }
   ```
Rule: `IAsyncEnumerable` from a controller is correct only when the iterator body does not close over a request-scoped disposable, or when you explicitly manage the scope. For every other case, materialize to a `List<T>` — it's simpler, and none of the four failure modes above can happen.

---

## ROUTING HINTS (What Signal Maps to What Pattern)

| Intake signal | Most likely category |
|---|---|
| "401 on every request" or "`[Authorize]` broken" | 1 (middleware order) |
| "CORS blocked" / "no Access-Control-Allow-Origin" | 1 (middleware order / UseCors position) |
| "logging/request-id/custom middleware runs twice per request" | 1 (registered twice) |
| "`[FromBody]` parameter is null" | 2 (model binding) |
| "DateTime parsed wrong on server" | 2 (culture / format) |
| "validation error returns HTML page instead of JSON 400" | 2 ([ApiController] + ProblemDetails) |
| "`A second operation was started on this context instance`" | 3 (scoped in singleton) |
| "IOptionsMonitor vs IOptionsSnapshot" / "config not reloading" | 3 (options lifetime) |
| "memory grows with request throughput" / "Dispose() delayed" | 3 (transient IDisposable leaks to request end) |
| "app hangs on `.Result` / `.Wait()`" | 4 (sync-over-async deadlock) |
| "unhandled exception crashes the app" / "async void" | 4 |
| "requests slow under load, CPU low" | 4 (ThreadPool starvation) |
| "SocketException port exhaustion" / "`TIME_WAIT`" | 5 (HttpClient) |
| "DNS change not picked up" | 5 (static HttpClient) |
| "`HttpClient.Timeout` not respected" | 5 (CancellationToken + ConnectTimeout) |
| "N+1 query" / "endpoint slow" / "list endpoint" | 6 (Include / projection / split query) |
| "SaveChanges does nothing" / "AsNoTracking update" | 6 |
| "IN list too long" / "2100 parameters" | 6 |
| "partial writes on exception" / "no rollback" | 7 (transactions) |
| "DbUpdateConcurrencyException" | 7 (RowVersion round-trip) |
| "background worker memory grows" / "ChangeTracker bloat" | 7 (scope per iteration) |
| "JSON property is null" / "case mismatch" | 8 (JsonSerializerOptions) |
| "cycle detected" / "StackOverflow on serialize" / "EF entity returned" | 8 (DTO projection) |
| "ObjectDisposedException on JsonElement" | 8 (Clone or POCO) |
| "appsettings not loaded in prod" | 9 (ASPNETCORE_ENVIRONMENT) |
| "Key Vault secret empty" | 9 (provider not registered) |
| "IOptions property default" | 9 (ValidateOnStart) |
| "real client IP missing" / "scheme is http behind LB" | 10 (ForwardedHeaders) |
| "413 Payload Too Large" | 10 (limits stack) |
| "IIS loads wrong environment" | 10 (web.config env vars) |
| "SemaphoreSlim hangs forever" | 11 (Release in finally) |
| "ConcurrentDictionary factory runs twice" | 11 (Lazy<Task<T>>) |
| "check-then-act race" | 11 (CAS or SemaphoreSlim) |
| "DateTime.Kind after Npgsql 6 upgrade" | 12 (UTC required) |
| "EF migration added NOT NULL" | 12 (NRT + migrations) |
| "minimal API 500 after .NET 8 upgrade" | 12 (JsonSerializerContext) |
| "`IAsyncEnumerable` returns []" | 12 (buffering / NDJSON) |

---

## UNIVERSAL .NET DIAGNOSTIC TOOLKIT

Before running any pattern's Prove step, collect baseline telemetry. Missing this converts minutes into hours.

```bash
# 1. Runtime counters — ThreadPool, GC, exceptions, HTTP server stats
dotnet-counters monitor -n YourApp \
    System.Runtime \
    Microsoft.AspNetCore.Hosting \
    Microsoft.EntityFrameworkCore \
    System.Net.Http

# 2. Live stack dump — find the hung thread / blocking call
dotnet-stack report -n YourApp
# or for a core dump:
dotnet-dump analyze core.12345

# 3. GC + allocation trace
dotnet-trace collect -n YourApp --providers Microsoft-Windows-DotNETRuntime

# 4. SQL from EF Core
# In Development only:
# .EnableSensitiveDataLogging().LogTo(Console.WriteLine, LogLevel.Information)

# 5. Network connections
# Windows: netstat -an | findstr ESTABLISHED
# Linux:   ss -tn state established
```

If `dotnet-counters` shows `threadpool-queue-length > 0` and `requests-current > threadpool-thread-count` → sync-over-async blocking. If `System.Net.Http current-connections` keeps growing → HttpClient lifecycle bug. If `Microsoft.EntityFrameworkCore query-duration` is climbing over time → DbContext tracker bloat. Map the counter signal to the category before diving into code.
