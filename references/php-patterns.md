# PHP Bug Patterns

Covers: PHP execution model, type system, Laravel, PHP-FPM, OPcache, PDO, Eloquent, queues, version mismatches.
Each pattern: symptom → why → prove → fix.

---

## ⚠️ VISIBILITY PREREQUISITE — Run Before Any Prove

PHP production servers run with `display_errors=Off` by default. A broken PHP page shows a blank response with no visible error. Before running any Prove below, confirm you can see PHP errors.

```bash
# Where is PHP writing errors? (run on server)
php -r "echo ini_get('error_log');"          # e.g. /var/log/php8.2-fpm.log
php -r "echo ini_get('display_errors');"     # should be 0 in prod — expected
php -r "echo ini_get('log_errors');"         # must be 1 — if 0, errors are lost

# Watch the error log live
tail -f $(php -r "echo ini_get('error_log');")

# If error_log is empty or wrong, find FPM log directly
sudo tail -f /var/log/php8.2-fpm.log        # adjust version
sudo tail -f /var/log/nginx/error.log        # nginx may show PHP upstream errors too
```

**If you cannot see any PHP errors at all:** Add these three lines to the top of the entry point (`index.php` / `public/index.php`) for ONE request, observe, then remove immediately:
```php
ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);
```

Do not leave these in production code. Use them once to surface the error, then remove.

---

## CATEGORY 1 — PHP EXECUTION MODEL

PHP is **shared-nothing**: every request spawns a fresh process, executes top-to-bottom, and dies. No persistent memory between requests. This is the root cause of bugs that would never exist in Java or Node.js.

### Pattern: OPcache stale bytecode — new code deployed but old behaviour runs
**Symptom:** Code changed and deployed. Old behaviour persists. `var_dump` shows old values. Restarting PHP-FPM immediately fixes it. Other team members on different servers see the new code.
**Why:** OPcache caches compiled PHP bytecode in shared memory. When `opcache.validate_timestamps=0` (common production hardening), OPcache never re-checks disk — it serves cached bytecode indefinitely regardless of file changes on disk. New files are deployed; old bytecode runs.
**Prove:** ⚠️ **Must run inside a web request — not from CLI.** `opcache.enable_cli=0` by default means `opcache_get_status()` from `php -r` returns `false` or an empty scripts array. Add to a temporary web endpoint, hit it once in a browser, then remove the file.

Check whether the specific changed file's cached timestamp is older than its disk modification time:
```php
// Temporary file: /var/www/html/ops-opcache-check.php — DELETE AFTER USE
if ($_SERVER['REMOTE_ADDR'] !== '127.0.0.1') { http_response_code(403); exit; }

$file = realpath('/var/www/html/app/Services/PaymentService.php'); // ← your changed file
$status = opcache_get_status(false);

if ($status === false) {
    error_log('[OPCACHE-PROVE] OPcache not active in this FPM pool — not the cause');
    exit;
}

$cached = $status['scripts'][$file] ?? null;
if ($cached) {
    error_log(sprintf(
        '[OPCACHE-PROVE] file=%s cached_at=%s disk_mtime=%s stale=%s',
        basename($file),
        date('Y-m-d H:i:s', $cached['timestamp']),
        date('Y-m-d H:i:s', filemtime($file)),
        $cached['timestamp'] < filemtime($file) ? 'YES — OLD BYTECODE RUNNING' : 'no'
    ));
} else {
    error_log('[OPCACHE-PROVE] file not in OPcache — not the cause');
}
echo 'done — check error log';
```
If log shows `stale=YES — OLD BYTECODE RUNNING` → confirmed. The FPM worker is executing bytecode compiled from the pre-deploy file.
**Fix:** On each deploy, call `opcache_reset()` via a protected CLI script or deploy hook:
```bash
php -r "opcache_reset(); echo 'OPcache cleared';"
# Or via web with auth guard:
# curl -H "X-Deploy-Token: $SECRET" https://app.example.com/ops/opcache-reset
```
**Dead giveaway:** `opcache.validate_timestamps=0` in `php.ini` with no deploy step calling `opcache_reset()`.

### Pattern: State assumed to persist between requests — counter/singleton resets every request
**Symptom:** Counter never exceeds 1. "Singleton" object reinitialised on every page load. Cache logic has no effect. Global variable reset on each request. Works correctly in a long-running Node.js or Java process, fails in PHP.
**Why:** PHP static variables, global variables, and all class properties are destroyed at request end. PHP's shared-nothing model creates a fresh process per request. A developer expecting Java-style singleton behaviour gets a new object every time.
**Prove:** Add to a temporary endpoint:
```php
static $count = 0;
$count++;
error_log('[STATE-PROVE] count=' . $count . ' pid=' . getmypid());
```
Hit the endpoint three times. If log shows `count=1 pid=X`, `count=1 pid=Y`, `count=1 pid=Z` — fresh state each request confirmed.
**Fix:** For cross-request state: use Redis (`$redis->incr('counter')`), Memcached, APCu (single-machine cache), or the database. PHP static variables persist only within one request's execution.

### Pattern: Headers already sent — output before `header()` or `setcookie()`
**Symptom:** `Warning: Cannot modify header information — headers already sent by (output started at /var/www/app/config.php:12)`. Redirect fires but page does not redirect. Cookie not set. PHP names the exact file and line in the warning.
**Why:** PHP sends HTTP headers on the first byte of output. Any `echo`, `print`, whitespace before `<?php`, or a BOM character (`\xEF\xBB\xBF`) at the start of an included file causes headers to flush. `header()` and `setcookie()` called after this throw a warning and do nothing.
**Prove:** The warning message IS the Prove — it names the exact file and line causing the premature output. Read it:
```
headers already sent by (output started at /var/www/app/helpers/config.php:12)
                                            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                                            This file, this line — fix here first
```
If `display_errors=Off` and you cannot see the warning: temporarily enable (see Visibility Prerequisite) or check error log.
**Fix:** Three checks in order:
1. **BOM in file:** Open `config.php` (or named file) in a hex editor. If first 3 bytes are `EF BB BF` → BOM present. Save as UTF-8 without BOM.
2. **Whitespace before `<?php`:** Open the named file. Confirm `<?php` is on line 1, column 1, with zero characters before it.
3. **Output logic:** Any `echo`/`print`/`var_dump` before `header()` calls must be moved after.
**Dead giveaway:** Whitespace or blank lines AFTER the closing `?>` tag at the bottom of included files.

### Pattern: `session_start()` missing — `$_SESSION` silently empty or undefined
**Symptom:** `$_SESSION['user']` is undefined (PHP 8) or produces Notice (PHP 7). Login appears to work but user is not remembered. No error if `display_errors=Off`.
**Why:** `$_SESSION` is a superglobal populated only after `session_start()` is called. Without it, `$_SESSION` is not initialised — reads return undefined, writes are silently discarded. The session cookie may be sent to the browser but never read back.
**Prove:**
```php
error_log('[SESSION-PROVE] status=' . session_status());
// PHP_SESSION_DISABLED = 0, PHP_SESSION_NONE = 1 (not started), PHP_SESSION_ACTIVE = 2
error_log('[SESSION-PROVE] _SESSION defined=' . (isset($_SESSION) ? 'yes' : 'NO'));
```
If `status=1` (PHP_SESSION_NONE) → `session_start()` never called on this request path.
**Fix:** `session_start()` must be called: before any `$_SESSION` access, before any output (headers must be unsent), and on every request that needs session data. Place it in a bootstrap file that always runs.

### Pattern: Shared-nothing assumption broken — global written in one request, read in another
**Symptom:** Config set via `$GLOBALS['config'] = ...` in one request. Next request reads empty. Admin sets a flag; users don't see it. Only reproducible by understanding PHP's request model.
**Why:** `$GLOBALS` is per-process, per-request. Setting a global in request A does not affect request B — each runs in an independent PHP process. This is the correct PHP behaviour, but developers from Java/Node.js backgrounds expect in-process shared state.
**Prove:** Log `getmypid()` in both the write request and the read request. Different PIDs confirm separate processes.
**Fix:** For shared state across requests: Redis, Memcached, database, or filesystem. For config specifically: load from a file or environment variable at bootstrap — not from a previous request's memory.

---

## CATEGORY 2 — TYPE SYSTEM & COMPARISON TRAPS

PHP's loose comparison (`==`) silently converts types before comparing. This causes auth bypasses, silent logic errors, and security vulnerabilities. PHP 8 tightened some rules but loose comparison still governs `==`, `switch`, and `in_array` by default.

### Pattern: `==` vs `===` — auth bypass or silent wrong result
**Symptom:** Token comparison passes with wrong token. Hash check succeeds unexpectedly. `if ($userInput == $storedValue)` returns `true` for inputs that should not match. Auth bypass under specific input conditions.
**Why:** PHP `==` converts types before comparing. `0 == "any_non_numeric_string"` is `true` in PHP 7 (string coerced to int 0). If a hash like `"0e12345"` compares to another `"0e67890"` with `==`, both become scientific-notation floats (`0 * 10^N = 0`) and match — the "magic hash" vulnerability.
**Prove:** At the exact comparison site in the code, log both sides:
```php
error_log(sprintf(
    '[COMPARE-PROVE] left type=%s value=%s | right type=%s value=%s | loose=%s | strict=%s',
    gettype($token), var_export($token, true),
    gettype($expected), var_export($expected, true),
    var_export($token == $expected, true),
    var_export($token === $expected, true)
));
```
If `loose=true` and `strict=false` → type juggling is causing the match. This is pathognomonic.
**Fix:** Replace all security-sensitive comparisons with `===`. For hashes use `hash_equals($expected, $actual)` which is both strict and timing-safe.

### Pattern: `empty()` treats valid values as missing — `"0"`, `0`, `false`, `[]` all empty
**Symptom:** Form field with value "0" (floor number, zero quantity, boolean false) treated as not filled in. `if (empty($_POST['quantity']))` fires for quantity=0. Silent data loss — valid input rejected.
**Why:** `empty()` returns `true` for `""`, `"0"`, `0`, `0.0`, `null`, `false`, `[]`, and undefined. The string "0" (a valid floor number or zero count) is explicitly empty under PHP's definition.
**Prove:**
```php
$val = $_POST['quantity']; // assume submitted as "0"
error_log(sprintf('[EMPTY-PROVE] value=%s empty=%s isset=%s not_empty_string=%s',
    var_export($val, true),
    var_export(empty($val), true),
    var_export(isset($val), true),
    var_export($val !== '', true)
));
```
Output showing `empty=true` for `value="0"` confirms the bug.
**Fix:** Replace `empty($val)` with an explicit check matching the actual constraint:
```php
// WRONG — treats "0" as missing
if (empty($_POST['quantity'])) { ... }

// CORRECT — checks for genuinely missing or blank
if (!isset($_POST['quantity']) || $_POST['quantity'] === '') { ... }
```

### Pattern: `in_array()` loose match — string found in integer array, role bypass
**Symptom:** `in_array("admin", [0, 1, 2])` returns `true`. `in_array("foo", [false, null, 0])` returns `true`. Role check passes for strings that should not match integer roles. Security bypass.
**Why:** Without the third `$strict = true` parameter, `in_array` uses loose comparison. `"admin" == 0` is `true` in PHP 7 (non-numeric string coerced to 0). An array of integer role IDs can be bypassed by passing the string "admin".
**Prove:**
```php
error_log('[INARRAY-PROVE] loose=' . var_export(in_array("admin", [0, 1, 2]), true)
    . ' strict=' . var_export(in_array("admin", [0, 1, 2], true), true));
```
Output `loose=true strict=false` confirms type juggling in the array search.
**Fix:** Always pass `true` as the third argument: `in_array($needle, $haystack, true)`. For role checks, also validate that the needle is the expected type before calling in_array.

### Pattern: `switch` type coercion — string matches wrong integer case
**Symptom:** `switch($_GET['action'])` executes wrong case. Input `"1abc"` matches `case 1`. Input `""` matches `case 0` or `case false`. Unexpected code path executes, including privileged operations.
**Why:** PHP `switch` uses loose comparison for each `case`. `"1abc" == 1` is `true` (string starting with digit coerced to that digit). Any user-controlled string switch against integer cases is a type juggling trap.
**Prove:**
```php
$action = $_GET['action']; // e.g. "1abc"
error_log('[SWITCH-PROVE] action=' . var_export($action, true)
    . ' equals_1=' . var_export($action == 1, true)
    . ' identical_1=' . var_export($action === 1, true));
```
**Fix:** Cast input before switch, or use `match` (PHP 8+) which uses strict comparison:
```php
// PHP 8+ — strict comparison, no type juggling
$result = match($_GET['action']) {
    'view' => showItem(),
    'delete' => deleteItem(),
    default => throw new \ValueError("Unknown action"),
};

// PHP 7 — cast first
$action = (string)$_GET['action']; // stay as string, use string cases
switch ($action) {
    case 'view': ...
}
```

### Pattern: Integer overflow — large 64-bit IDs lose precision via float
**Symptom:** Large IDs from API (Snowflake, Twitter-style 64-bit) are wrong after JSON decode. `9223372036854775808` becomes `9.2233720368548E+18`. Database lookup fails — ID doesn't match. Works on 32-bit PHP (different failure), breaks on 64-bit.
**Why:** PHP `json_decode` converts integers larger than PHP_INT_MAX to float. IEEE 754 double-precision floats have a 53-bit mantissa — integers above 2^53 (~9 quadrillion) lose the least significant digits. The ID is silently corrupted.
**Prove:**
```php
$json = '{"id":9223372036854775808}';
$obj = json_decode($json);
error_log('[BIGINT-PROVE] decoded=' . var_export($obj->id, true)
    . ' type=' . gettype($obj->id)
    . ' original_preserved=' . var_export($obj->id == 9223372036854775808, true));
```
If type is `double` instead of `integer` → precision lost.
**Fix:** `json_decode($json, flags: JSON_BIGINT_AS_STRING)` — keeps large integers as strings. Treat the ID as a string throughout the application.

---

## CATEGORY 3 — LARAVEL FRAMEWORK PATTERNS

### Pattern: Eloquent N+1 — fast in dev, timeout in production
**Symptom:** Route loads in 50ms with 10 records. Times out with 500 records. DB server CPU spikes. No code change between working and broken — only data volume changed.
**Why:** `$posts = Post::all(); foreach ($posts as $p) { echo $p->author->name; }` — accessing `$p->author` on each iteration fires a new SELECT query. 500 posts = 501 queries. The ORM hides this from developers during low-volume testing.
**Prove:**
```php
DB::enableQueryLog();
// run the controller/service code
$queries = DB::getQueryLog();
error_log('[N1-PROVE] query_count=' . count($queries));
// Or with Laravel Debugbar: watch query count badge in browser
```
If count equals (number of records + 1) → N+1 confirmed.
**Fix:**
```php
// WRONG — N+1
$posts = Post::all();

// CORRECT — 2 queries total
$posts = Post::with('author')->get();

// Multiple relationships
$posts = Post::with(['author', 'tags', 'comments.user'])->get();
```

### Pattern: Queue job silently not executing — driver is `sync` or worker not running
**Symptom:** `dispatch(new ProcessPayment($id))` called successfully. No payment processed. No log entry. No record in `failed_jobs`. Queue dashboard empty.
**Why:** Four causes — check in this order: (a) `QUEUE_CONNECTION=sync` in production `.env` runs the job inline and swallows exceptions silently, (b) queue worker not running (`php artisan queue:work`), (c) job table not migrated (`jobs` table missing), (d) job throws and `$tries=0` sends to `failed_jobs` without notification.
**Prove:**
```bash
# Check queue driver
php artisan tinker --execute="dump(config('queue.default'));"

# Run one job manually with full output
php artisan queue:work --once -vvv

# Check failed jobs
php artisan queue:failed
```
If driver shows `sync` in production → that is the bug. If `queue:work --once -vvv` shows an exception → that is the failure reason.
**Fix:** Set `QUEUE_CONNECTION=database` (or `redis`) in `.env.production`. Run `php artisan queue:work` as a supervised daemon (Supervisor, systemd). Add `php artisan queue:failed` monitoring.

### Pattern: Service container binding not found — BindingResolutionException
**Symptom:** `Target [App\Contracts\PaymentGateway] is not instantiable`. Works locally. Fails after deploy or in artisan context.
**Why:** Interface not bound in `AppServiceProvider::register()`. Or: binding registered in a provider that is not loaded. Or: `php artisan config:cache` cached a stale provider list. Or: typo in the contract's fully-qualified class name.
**Prove:**
```bash
# Clear all caches first — stale cache is a common cause
php artisan config:clear && php artisan cache:clear

# Then try to resolve the binding directly
php artisan tinker --execute="app(\App\Contracts\PaymentGateway::class);"
```
The tinker command throws with the exact reason — not found, not instantiable, or wrong type. This is pathognomonic.
**Fix:** Add to `AppServiceProvider::register()`:
```php
$this->app->bind(\App\Contracts\PaymentGateway::class, \App\Services\StripeGateway::class);
```
Confirm with `php artisan tinker --execute="dump(app()->getBindings());"` — check the contract appears.

### Pattern: Middleware not applied to route — authenticated endpoint publicly accessible
**Symptom:** Protected route accessible without login. `auth` middleware defined. Adding `@auth` check in controller works. Removing it breaks. Middleware class exists and works in isolation.
**Why:** Middleware registered in `$middlewareAliases` but not applied to the route or group. Or: route defined outside the authenticated group. Or: API routes use `auth:sanctum` but web routes use `auth` — guard mismatch. Or: cached route file is stale.
**Prove:**
```bash
php artisan route:clear  # clear stale route cache first
php artisan route:list --path=admin  # or the protected path
```
Check the `Middleware` column. If empty for the protected route → not applied. If present → guard mismatch — check the guard name.
**Fix:** Apply middleware at route or group level:
```php
Route::middleware('auth')->group(function () {
    Route::get('/admin/dashboard', AdminController::class);
});
// or per-route:
Route::get('/admin', AdminController::class)->middleware('auth');
```

### Pattern: Config cached with old values — `.env` changes ignored after deploy
**Symptom:** Changed `DB_HOST` or `MAIL_HOST` in `.env`. No effect even after redeployment. DB still connects to the old host. Other developers on different servers see the new value.
**Why:** `php artisan config:cache` writes `bootstrap/cache/config.php`. This file is read instead of `.env`. Changes to `.env` are completely ignored until the cache is cleared. Common in production deploy pipelines that cache config for performance.
**Prove:**
```bash
# Does the cache file exist?
ls -la bootstrap/cache/config.php

# What does the application think the value is?
php artisan config:show database.connections.mysql.host

# Clear cache and check again
php artisan config:clear
php artisan config:show database.connections.mysql.host
```
If the value changes after `config:clear` → was using cached value.
**Dead giveaway:** `bootstrap/cache/config.php` exists and its modification time is older than the `.env` change.
**Fix:** Add `php artisan config:clear && php artisan config:cache` to the deploy pipeline. Never edit `.env` on production without clearing config cache.

### Pattern: Eloquent relationship returns wrong results — method name or foreign key mismatch
**Symptom:** `$user->posts` is empty. `User::with('posts')->get()` returns users with empty posts arrays. Posts exist in the database for those user IDs.
**Why:** Eloquent relationship method name in `with('posts')` must match the method name on the model exactly (case-sensitive on Linux). Or: Eloquent expects foreign key `user_id` but column is named `author_id`, `created_by`, or similar — convention not followed.
**Prove:**
```php
// Step 1: Does the relationship method work at all?
error_log('[REL-PROVE] direct_count=' . User::first()->posts()->count());

// Step 2: Does eager load match?
$user = User::withCount('posts')->first();
error_log('[REL-PROVE] withCount=' . $user->posts_count . ' direct=' . $user->posts()->count());
```
If direct count is correct but `withCount` returns 0 → method name mismatch in `withCount()` argument. If direct count is also 0 → check foreign key.
**Fix:** Confirm method name matches exactly. Specify foreign key if not following convention:
```php
public function posts(): HasMany
{
    return $this->hasMany(Post::class, 'author_id'); // explicit when not user_id
}
```

### Pattern: Event listener not firing — observer not registered or mass operation bypasses events
**Symptom:** `event(new OrderPlaced($order))` dispatched. Listener method never called. No log. No error. Works in `php artisan tinker`.
**Why:** Two distinct causes: (a) listener not registered in `EventServiceProvider::$listen` or via `Event::listen()` in a provider, (b) mass operations like `Post::where('active', false)->delete()` execute a single SQL DELETE and bypass all model events — they do not instantiate models.
**Prove:**
```bash
# Check registered event→listener map
php artisan event:list

# Clear event cache if using event:cache
php artisan event:clear

# Test listener directly
php artisan tinker --execute="event(new \App\Events\OrderPlaced(\App\Models\Order::first()));"
```
If `event:list` shows no listener for the event → not registered. If `event:list` shows it but tinker test also fails → class resolution error in listener constructor.
**Fix:** Register in `EventServiceProvider`:
```php
protected $listen = [
    \App\Events\OrderPlaced::class => [
        \App\Listeners\SendOrderConfirmation::class,
    ],
];
```
For mass operations that must trigger events: use `foreach` + individual model `delete()` calls, or explicitly fire events after the mass operation.

### Pattern: Blade template cached — view change not reflected after deploy
**Symptom:** Changed Blade template. Old output still served. `git pull` confirms new content on disk. Other developers on different servers see the new template. Restarting nginx has no effect.
**Why:** Blade compiles templates to PHP files in `storage/framework/views/`. Compiled files are reused if the source file's mtime has not changed. After `git checkout` or `rsync` deploy, file modification times may be reset to the commit time — older than the cached compiled file — causing Blade to use stale compiled output.
**Prove:**
```bash
php artisan view:clear
```
If the template output immediately updates → compiled cache was stale. Done.
**Fix:** Add `php artisan view:clear` to the deploy pipeline. For zero-downtime deploys: run `view:clear` before switching the symlink.

---

## CATEGORY 4 — PHP-FPM & SERVER

### Pattern: PHP-FPM worker exhaustion — 502 Bad Gateway under load
**Symptom:** App works normally. Under traffic spike: 502 Bad Gateway from nginx. Nginx error log shows connection refused or upstream unavailable. After load drops, app recovers. Restarting PHP-FPM fixes immediately.
**Why:** `pm.max_children` limits concurrent PHP-FPM workers. A slow DB query or external API call holds a worker for seconds. Under burst load, all workers are occupied. New requests find no available worker — nginx returns 502.
**Prove:**
```bash
# Check FPM worker count vs max_children (no prior config required)
ps aux | grep php-fpm | grep -v "master\|grep" | wc -l

# Check max_children setting
grep "max_children" /etc/php/8.2/fpm/pool.d/www.conf  # adjust version

# Confirm workers are all busy (not idle)
ps aux | grep php-fpm | grep -v "master\|grep" | awk '{print $8}'
# If all show 'S' (sleeping) = idle; if 'R' (running) = busy handling requests

# Nginx error log shows the reason
sudo tail -100 /var/log/nginx/error.log | grep "connect() failed\|no live upstreams\|resource temporarily unavailable"
```
If active worker count equals `max_children` AND nginx log shows `connect() failed` → worker exhaustion confirmed.
**Fix:** Increase `pm.max_children` (budget: each worker ~20–50MB RAM). More importantly: identify and fix the slow operation holding workers. A single slow query holding workers causes this pattern even at moderate traffic.

### Pattern: `max_execution_time` kills long operation — silent partial completion
**Symptom:** Long import or export process stops partway. No error in logs (timeout kills the process before it can log). Client receives 504 from nginx. Database shows partial records. Restarting PHP-FPM does not help — next attempt also fails at the same row count.
**Why:** `max_execution_time` (default 30s, often 60s in production) sends a hard kill to the PHP process when exceeded. The script terminates mid-loop with no exception, no cleanup, no finally block execution, and no log entry. Nginx 504 is the only visible symptom.
**Prove:**
```php
// Add at the start of the long operation
error_log('[TIMEOUT-PROVE] max_execution_time=' . ini_get('max_execution_time')
    . ' memory_limit=' . ini_get('memory_limit'));

// Add inside the loop
if ($rowCount % 100 === 0) {
    error_log('[TIMEOUT-PROVE] processed=' . $rowCount . ' elapsed=' . (microtime(true) - $start) . 's');
}
```
Compare the last logged row count to the total rows. If execution stops at roughly `max_execution_time` seconds worth of rows → timeout confirmed.
**Fix:** For background processing: use `php artisan make:command` — CLI PHP has no `max_execution_time`. For web requests that must be long-running: `set_time_limit(0)` at the top of the function, and ensure nginx `fastcgi_read_timeout` is also extended. Better: move heavy work to a queued job.

### Pattern: `memory_limit` exhausted — truncated response with no visible error
**Symptom:** Response is truncated mid-HTML. White screen partway through. PHP error log shows `Allowed memory size of X bytes exhausted (tried to allocate Y bytes)`. Users see partial pages. Only happens above a certain data size threshold.
**Why:** PHP allocates memory per request. Large arrays, image manipulation, or loading entire CSV files into memory can hit `memory_limit` (default 128M). PHP terminates the script; the response is abandoned mid-send. If `log_errors=On`, the error appears in `error_log`; if not, it is silent.
**Prove:**
```php
// Add at end of successful runs to establish baseline
register_shutdown_function(function () {
    error_log('[MEMORY-PROVE] peak=' . memory_get_peak_usage(true)
        . ' limit=' . ini_get('memory_limit'));
});
```
If peak is within 20% of limit → will fail for slightly larger inputs. Confirm by checking error log for `Allowed memory size exhausted`.
**Fix:** `ini_set('memory_limit', '512M')` for the specific operation. Or: restructure to stream/chunk data rather than loading the full dataset into memory. For CSV imports: use `fgetcsv()` in a loop, processing one row at a time.

### Pattern: PHP-FPM running as wrong user — file permission denied silently
**Symptom:** `file_put_contents()` returns `false`. `fopen()` fails. `is_writable()` returns `false` for a path that appears to have correct permissions. Uploads fail silently. Only in production, not dev.
**Why:** PHP-FPM pool runs as user `www-data` (or `nginx`) while the application directory is owned by a deploy user (`deployer`, `ubuntu`). Or: files written by PHP are not readable by the nginx/web server user. `open_basedir` restriction can also cause this.
**Prove:**
```bash
# Who is FPM running as?
ps aux | grep php-fpm | grep -v "master\|grep" | head -3

# Who owns the target directory?
ls -la /var/www/html/storage/

# Can FPM user write there?
sudo -u www-data touch /var/www/html/storage/framework/test_write && echo OK || echo FAILED
sudo -u www-data rm -f /var/www/html/storage/framework/test_write

# Check open_basedir restriction
php -r "var_dump(ini_get('open_basedir'));"
```
If `sudo -u www-data touch ...` fails → permission mismatch confirmed.
**Fix:** Set correct ownership: `chown -R www-data:www-data /var/www/html/storage`. Or configure the FPM pool to run as the deploy user. For `open_basedir`: add the path to the restriction list in `php.ini` or FPM pool config.

### Pattern: Persistent PDO connection leaks DB session state across requests
**Symptom:** With `PDO::ATTR_PERSISTENT => true`, queries occasionally return stale data. Transactions appear to not commit. SET session variables from one request bleed into the next. Only under concurrent load, never in single-user testing.
**Why:** Persistent connections are reused across PHP-FPM requests within the same worker process. If a previous request started a transaction and the PHP process died (OOM, timeout, SIGKILL), the next request inherits an open transaction. SET variables, temporary tables, and user-defined variables also persist across the reused connection.
**Prove:**
```php
// Log autocommit state at the start of each request
$stmt = $pdo->query("SELECT @@session.autocommit, @@session.transaction_read_only");
$row = $stmt->fetch();
error_log('[PDO-PERSIST-PROVE] autocommit=' . $row['@@session.autocommit']
    . ' in_transaction=' . ($pdo->inTransaction() ? 'YES' : 'no'));
```
If `autocommit=0` or `in_transaction=YES` at the start of a fresh request → leaked state from previous request's connection.
**Fix:** Do not use `PDO::ATTR_PERSISTENT` in PHP-FPM environments. Use connection pooling at the database proxy level (PgBouncer for PostgreSQL, ProxySQL for MySQL) instead — these handle connection reuse safely.

---

## CATEGORY 5 — OPCACHE & AUTOLOADING

### Pattern: Composer autoload not regenerated — new class not found after adding file
**Symptom:** `Class 'App\Services\PaymentService' not found`. Class file exists in the correct namespace directory. Namespace matches PSR-4 config in `composer.json`. Works immediately after running one command.
**Why:** Composer generates a class map in `vendor/composer/autoload_classmap.php` and namespace map in `vendor/composer/autoload_psr4.php`. New files are not automatically discovered — the autoloader must be regenerated. In classmap-mode projects (common in legacy codebases), every new file requires a regeneration.
**Prove:**
```bash
composer dump-autoload
```
If the class becomes available immediately → autoload map was stale. Done — this is both the Prove and the fix.
**Fix:** Add `composer dump-autoload --optimize` to the deploy pipeline. For PSR-4 projects (modern Laravel): new files in the correct namespace/directory are found after regeneration. Verify PSR-4 mapping in `composer.json`:
```json
"autoload": {
    "psr-4": {
        "App\\": "app/"
    }
}
```

### Pattern: Class defined in two files — `Cannot redeclare class`
**Symptom:** `Fatal error: Cannot redeclare class PaymentService (previously declared in /app/Services/PaymentService.php:5)`. Intermittent — works on some requests, fails on others. Or: consistently fails after OPcache loads both versions.
**Why:** A file is included twice via different paths (symlink and real path bypass `require_once`'s dedup check). Or: copy-paste created a duplicate class definition in a different file. OPcache caches both compiled files independently — when both are loaded, the second declaration is fatal.
**Prove:**
```bash
grep -r "class PaymentService" app/ --include="*.php" -l
```
If two files returned → duplicate class. If one file: the file is being included twice — different path aliases:
```bash
php -r "
\$paths = spl_autoload_functions();
// Add include tracking temporarily
"
# Simpler: grep all include/require for the filename
grep -rn "PaymentService" app/ --include="*.php" | grep -i "require\|include"
```

### Pattern: Namespace or `use` statement missing — wrong class resolved
**Symptom:** `Call to undefined method`. `instanceof` check fails. Method exists but on the wrong class. `var_dump(get_class($obj))` shows a different class than expected.
**Why:** Without `use App\Models\User` at the top of the file, `new User()` resolves to the root namespace `\User` (if it exists as a global class) or throws `Class 'User' not found`. PHP resolves unqualified class names against the current namespace, then falls back to the global namespace.
**Prove:**
```php
error_log('[NS-PROVE] class=' . get_class($obj)
    . ' expected=App\\Models\\User'
    . ' match=' . ($obj instanceof \App\Models\User ? 'yes' : 'NO'));
```
If `match=NO` → wrong class was instantiated. Check `use` statements at the top of the calling file.
**Fix:** Add `use App\Models\User;` (or the correct FQCN) at the top of the file. Always use the fully-qualified class name or import it with `use`.

### Pattern: OPcache memory full — new files not cached, performance degrades after deploy
**Symptom:** After a deploy with many new files, application gradually slows under load. Response times increase. OPcache hit rate visible in monitoring drops from 99% to 80%.
**Why:** `opcache.memory_consumption` (default 128MB) sets OPcache's memory ceiling. When full, new scripts cannot be cached. Old scripts remain (not aggressively evicted). After a large deploy, many new files compete for a full cache.
**Prove:**
```php
// Add to a temporary ops endpoint
$s = opcache_get_status(false);
$mem = $s['memory_usage'];
error_log(sprintf('[OPCACHE-MEM] used=%dMB free=%dMB total=%dMB pct_used=%.1f%%',
    $mem['used_memory'] / 1024 / 1024,
    $mem['free_memory'] / 1024 / 1024,
    ($mem['used_memory'] + $mem['free_memory']) / 1024 / 1024,
    100 * $mem['used_memory'] / ($mem['used_memory'] + $mem['free_memory'])
));
```
If `pct_used > 85%` → OPcache memory pressure.
**Fix:** Increase `opcache.memory_consumption=256` in `php.ini`. Run `opcache_reset()` after deploy to clear old entries and let the new files populate cleanly.

---

## CATEGORY 6 — PDO & DATABASE

### Pattern: PDO error mode silent — SQL errors return `false`, not exception
**Symptom:** `$stmt->execute()` returns `false`. No exception. No log entry (if error log not checked). Code continues with wrong data — `$stmt->fetchAll()` returns empty array. Debugging is extremely difficult because nothing breaks visibly.
**Why:** PDO's default error mode is `PDO::ERRMODE_SILENT`. SQL errors set an internal error code and return `false` — but do not throw exceptions and do not trigger PHP errors. Developers not checking return values miss failures completely.
**Prove:**
```php
$attr = $pdo->getAttribute(PDO::ATTR_ERRMODE);
error_log('[PDO-MODE-PROVE] errmode=' . $attr
    . ' (' . ['SILENT', 'WARNING', 'EXCEPTION'][$attr] . ')');
// 0 = SILENT (bug), 1 = WARNING, 2 = EXCEPTION (correct)
```
If errmode=0 → PDO is silent. Then enable exceptions and re-run — does an exception appear?
**Fix:** Set at connection time — cannot be changed after construction in some cases:
```php
$pdo = new PDO($dsn, $user, $pass, [
    PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,  // throws on error
    PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
    PDO::ATTR_EMULATE_PREPARES => false,           // real prepared statements
]);
```

### Pattern: Transaction not committed — data lost on exception path
**Symptom:** Operation appears to succeed (no exception visible to user). DB shows no change. Only on certain code paths (error branches). Works in happy path testing.
**Why:** `$pdo->beginTransaction()` called. An exception is thrown and caught upstream. `$pdo->commit()` never reached. `$pdo->rollBack()` also not called — the connection is returned to a pool with an open transaction, which is rolled back on the next connection use or connection close.
**Prove:**
```php
try {
    $pdo->beginTransaction();
    performOperations();
    $pdo->commit();
} catch (\Exception $e) {
    error_log('[TX-PROVE] exception=' . $e->getMessage()
        . ' in_transaction=' . ($pdo->inTransaction() ? 'YES — UNCOMMITTED' : 'no'));
    $pdo->rollBack();  // add this too
    throw $e;
}
```
If log shows `in_transaction=YES` inside the catch block → transaction was open and uncommitted when exception fired.
**Fix:**
```php
// Always use try/catch/rollback pattern
$pdo->beginTransaction();
try {
    performOperations();
    $pdo->commit();
} catch (\Throwable $e) {
    if ($pdo->inTransaction()) {
        $pdo->rollBack();
    }
    throw $e;  // re-throw — don't swallow
}
```

### Pattern: PDO N+1 — query inside loop causes timeout at scale
**Symptom:** Page loads fine with 10 records. Times out with 500. DB slow log shows many near-identical SELECT queries with different ID values. Query pattern: `SELECT * FROM users WHERE id = ?` repeated hundreds of times.
**Why:** `foreach ($orders as $order) { $user = fetchUser($order['user_id']); }` where `fetchUser()` executes a query. N orders = N queries. Each query is fast; total time is N × per-query time.
**Prove:** Two approaches — use whichever fits the code structure:

**Option A — Inline counter (works for any query-in-loop pattern):**
```php
$queryCount = 0;
$recordCount = count($orders);

foreach ($orders as $order) {
    $queryCount++;
    // ... your existing query code unchanged
}

error_log("[N1-PROVE] queries=$queryCount records=$recordCount ratio=" . round($queryCount / max($recordCount, 1), 2));
```
If `ratio ≈ 1.0` (queries equals records) → N+1 confirmed. A fixed implementation has ratio near 0 — all IDs fetched before the loop in one query.

**Option B — Named function wrap (when queries are inside a helper function):**
```php
$queryCount = 0;
// Add at the very top of fetchUser() or equivalent:
function fetchUser($id) {
    global $queryCount;
    $queryCount++;
    error_log('[N1-PROVE] query #' . $queryCount . ' for id=' . $id);
    // ... actual query unchanged
}
// After the loop:
error_log('[N1-PROVE] total=' . $queryCount . ' records=' . count($orders));
```
If `total` equals record count → N+1 confirmed.
**Fix:** Collect all IDs first, then fetch in one query:
```php
$userIds = array_column($orders, 'user_id');
$placeholders = implode(',', array_fill(0, count($userIds), '?'));
$stmt = $pdo->prepare("SELECT * FROM users WHERE id IN ($placeholders)");
$stmt->execute($userIds);
$users = array_column($stmt->fetchAll(), null, 'id'); // keyed by ID
```

### Pattern: Charset mismatch — emoji and non-ASCII stored as `?` or `??????`
**Symptom:** User submits emoji or non-ASCII characters. Stored data shows `?` or `??????`. Works in development (UTF-8 terminal/editor). Breaks in production. The stored garbled data cannot be recovered.
**Why:** MySQL connection charset not set to `utf8mb4`. PDO default is latin1 unless explicitly specified. MySQL's `utf8` charset (confusingly named) only supports 3-byte UTF-8 — emoji are 4-byte and silently truncated or replaced with `?`.
**Prove:**
```sql
SHOW VARIABLES LIKE 'character_set%';
SHOW VARIABLES LIKE 'collation%';
```
If `character_set_client` or `character_set_connection` is not `utf8mb4` → charset mismatch is the cause.
**Fix:** Specify `charset=utf8mb4` in the DSN at connection time:
```php
$dsn = 'mysql:host=localhost;dbname=myapp;charset=utf8mb4';
$pdo = new PDO($dsn, $user, $pass);
// Also ensure DB table/column collation is utf8mb4_unicode_ci
```

### Pattern: PreparedStatement parameter count mismatch — silent wrong results or PDO exception
**Symptom:** Query returns wrong results or an `SQLSTATE[HY093]: Invalid parameter number` exception. Placeholders in SQL do not match the bound parameter count. Works in testing with simple queries, breaks when SQL is built dynamically.
**Why:** When building SQL dynamically (adding WHERE clauses conditionally), the number of `?` placeholders must exactly match the number of values bound in `execute()`. An extra or missing placeholder causes either an exception or silently wrong query execution.
**Prove:**
```php
$sql = "SELECT * FROM orders WHERE status = ? AND user_id = ?";
$params = [$status]; // forgot user_id!
$placeholder_count = substr_count($sql, '?');
error_log('[PARAM-PROVE] placeholders=' . $placeholder_count . ' params=' . count($params)
    . ' match=' . ($placeholder_count === count($params) ? 'yes' : 'NO'));
```
If `match=NO` → parameter count mismatch confirmed.
**Fix:** Count placeholders and params programmatically when building dynamic SQL:
```php
$conditions = [];
$params = [];
if ($status) { $conditions[] = 'status = ?'; $params[] = $status; }
if ($userId) { $conditions[] = 'user_id = ?'; $params[] = $userId; }
$sql = 'SELECT * FROM orders WHERE ' . implode(' AND ', $conditions);
// placeholder count always equals param count by construction
```

---

## CATEGORY 7 — ELOQUENT / ORM

### Pattern: Mass assignment silently ignores fields — `$fillable` not updated for new column
**Symptom:** `User::create($request->all())` called. New field not saved. No error. `$user->newField` is null after save. Other fields saved correctly.
**Why:** Eloquent `$fillable` controls which fields can be mass-assigned. Fields not in `$fillable` are silently ignored on `create()` and `fill()`. Adding a column to the DB without adding it to `$fillable` causes silent data loss.
**Prove:**
```php
$user = new User;
$user->fill($requestData);
error_log('[MASS-PROVE] dirty=' . json_encode($user->getDirty())
    . ' rejected_keys=' . json_encode(array_diff(array_keys($requestData), array_keys($user->getDirty()))));
```
`rejected_keys` shows every field that was silently dropped.
**Fix:** Add the new field to `$fillable`:
```php
protected $fillable = ['name', 'email', 'new_field'];  // add new_field
```

### Pattern: Soft delete — deleted records still appear in results
**Symptom:** `$post->delete()` called. `Post::all()` still returns the deleted post. `Post::find($id)` still finds it. No hard delete in DB — `deleted_at` is populated.
**Why:** `SoftDeletes` trait sets `deleted_at` instead of deleting the row. `Post::all()` applies a global scope excluding soft-deleted records — BUT only when querying through the Eloquent model. Raw queries via `DB::table('posts')` bypass all model scopes including soft-delete.
**Prove:**
```php
// Does the model scope work?
error_log('[SOFT-PROVE] model_count=' . Post::count());
error_log('[SOFT-PROVE] with_trashed=' . Post::withTrashed()->count());
error_log('[SOFT-PROVE] raw_count=' . DB::table('posts')->count());
```
If `raw_count > model_count` → soft-deleted records exist. If `model_count` still includes deleted record → not using `SoftDeletes` trait OR the query bypasses model scopes.
**Fix:** Ensure `use SoftDeletes;` is in the model. Replace any `DB::table('posts')` queries that should respect soft deletes with Eloquent model queries.

### Pattern: Eloquent model event not firing — observer not registered or mass operation
**Symptom:** `creating`, `updated`, `deleting` model event logic never executes. Observer class exists. Adding `dd()` inside the observer shows it's never reached.
**Why:** Two causes: (a) observer not registered in `AppServiceProvider::boot()`. (b) Mass operations (`Post::where(...)->delete()`, `Post::whereIn('id', $ids)->update([...])`) execute one SQL statement per call — they do not instantiate model objects and therefore cannot fire model events.
**Prove:**
```bash
# Check if observer fires on single model operation
php artisan tinker --execute="
\$post = \App\Models\Post::first();
\$post->touch(); // triggers 'updated'
"
```
If observer fires in tinker but not in the application → mass operation is bypassing it. If observer does not fire in tinker → not registered.
**Fix:** Register observer in `AppServiceProvider::boot()`:
```php
Post::observe(PostObserver::class);
```
For mass operations that must trigger events, use a loop:
```php
Post::where('active', false)->get()->each->delete(); // fires deleting/deleted for each
```

### Pattern: `withCount` / `withSum` returns 0 — relationship name mismatch
**Symptom:** `User::withCount('posts')->get()` — all users have `posts_count = 0`. Posts exist in DB. Direct `$user->posts()->count()` returns correct value.
**Why:** `withCount('posts')` must match the relationship method name on the model exactly. Typo, wrong plural/singular, or wrong string case causes Eloquent to generate an incorrect subquery that returns 0 rows (not an error).
**Prove:**
```php
$user = User::first();
error_log('[WITHCOUNT-PROVE] direct=' . $user->posts()->count());
$u2 = User::withCount('posts')->find($user->id);
error_log('[WITHCOUNT-PROVE] withCount=' . $u2->posts_count);
// Compare — if direct > 0 and withCount = 0 → name mismatch
```
**Fix:** Ensure string in `withCount()` exactly matches the method name:
```php
public function posts(): HasMany { ... }    // method name: "posts"
User::withCount('posts')->get();            // ← must match exactly
```

### Pattern: Eager load returns empty — wrong relationship or constraint filters all results
**Symptom:** `Order::with('activeItems')->get()` — `$order->activeItems` is empty on all orders. Items exist. `$order->items` (without scope) returns them correctly.
**Why:** A relationship with a constraint (`whereNull('deleted_at')` or `where('status', 'active')`) applied either in the relationship method or via `with()` closure may filter out all results if data does not match the constraint.
**Prove:**
```php
// Compare scoped vs unscoped
$order = Order::first();
error_log('[EAGER-PROVE] all_items=' . $order->items()->count());
error_log('[EAGER-PROVE] active_items=' . $order->activeItems()->count());
error_log('[EAGER-PROVE] active_status_values=' . json_encode(
    $order->items()->pluck('status')->unique()->toArray()
));
```
If `all_items > 0` but `active_items = 0` → the constraint filters out everything. Check whether `status` values in the data match what the relationship expects.

---

## CATEGORY 8 — QUEUES, CACHE & SCHEDULED COMMANDS

### Pattern: Cache returns stale data — wrong driver, wrong key, or missing invalidation
**Symptom:** `Cache::put('user_42', $user, 3600)` called after update. `Cache::get('user_42')` returns old data. Even after user updates their profile. Behaviour is consistent — not intermittent.
**Why:** Four causes — check in order: (a) cache driver is `array` (in-process, per-request — nothing persists), (b) putting to one store, getting from another (e.g., `Cache::store('redis')` vs default `file`), (c) `Cache::put()` key does not match `Cache::get()` key exactly (typo, dynamic key construction differs), (d) TTL not long enough — value expired between set and get.
**Prove:**
```bash
php artisan tinker --execute="
echo config('cache.default'); // confirm driver
\Cache::put('debug_probe', 'works', 300);
echo \Cache::get('debug_probe'); // if blank → driver issue
echo \Cache::has('user_42') ? 'key_exists' : 'key_missing'; // confirm key
"
```
**Fix:** Match the issue to the cause: set `CACHE_DRIVER=redis` in `.env`, use consistent key construction, ensure same cache store for put and get.

### Pattern: Scheduled command not running — missing cron entry or wrong working directory
**Symptom:** `php artisan app:send-reminders` works perfectly when run manually. Defined in `Kernel.php`. Never runs automatically. No log entry from the command at the expected time.
**Why:** Laravel scheduler requires exactly one cron entry on the server that calls `schedule:run` every minute. Without this entry, the scheduler is never invoked. Additionally: the cron entry must use the full path to the PHP binary and the full path to `artisan`, and the working directory must be the project root (where `.env` lives).
**Prove:**
```bash
# Does the command appear in the scheduler?
php artisan schedule:list

# Does the cron entry exist?
crontab -l | grep artisan

# Run the scheduler manually — does it execute the command?
php artisan schedule:run --verbose
```
If `schedule:list` shows the command and `schedule:run --verbose` runs it → cron entry is missing. If `schedule:run --verbose` shows the command is "due" but fails → check the command itself.
**Fix:** Add to crontab:
```
* * * * * cd /var/www/html && /usr/bin/php8.2 artisan schedule:run >> /dev/null 2>&1
```
Use full paths. Confirm: `which php` and `pwd` in the project directory.

### Pattern: Queue job silently swallows exception — try/catch inside job marks it as succeeded
**Symptom:** Job dispatched. No output or effect. No record in `failed_jobs`. `jobs` table shows job removed (consumed). Logic that the job should execute never happens.
**Why:** A `try/catch` inside the job's `handle()` method catches the exception and does not rethrow it. Laravel marks a job as succeeded when `handle()` returns without throwing. The exception is swallowed; the job succeeds with incorrect results.
**Prove:**
```bash
# Run the job manually with verbose output
php artisan queue:work --once -vvv 2>&1

# Or: temporarily add logging inside the catch
```
In `queue:work -vvv`, even caught exceptions may appear in verbose mode. Or temporarily add `logger()->error('JOB CAUGHT: ' . $e->getMessage())` inside the catch.
**Fix:** Rethrow exceptions that represent real failures:
```php
public function handle(): void
{
    try {
        $this->processPayment();
    } catch (NetworkException $e) {
        // transient — let Laravel retry
        throw $e;
    } catch (InvalidPaymentException $e) {
        // permanent failure — log and mark as failed
        logger()->error('[JOB] payment invalid: ' . $e->getMessage());
        $this->fail($e);  // marks as permanently failed
    }
}
```

### Pattern: Redis connection exhausted — cache and queue degrade under load
**Symptom:** Intermittent cache misses under load. Queue jobs delayed. `Predis\Connection\ConnectionException` or `Connection refused`. Redis commands time out. Normal at low traffic, degrades at peak.
**Why:** PHP-FPM workers each open their own Redis connection. With `pm.max_children=50`, up to 50 simultaneous Redis connections. If Redis `maxclients` is lower (default 10,000 — usually not the issue) or if each worker holds a long-lived connection, pool can exhaust. More commonly: Redis `maxmemory-policy allkeys-lru` is evicting cache keys silently.
**Prove:**
```bash
redis-cli INFO clients | grep connected_clients
redis-cli CONFIG GET maxclients
redis-cli CONFIG GET maxmemory-policy
redis-cli INFO memory | grep "used_memory_human\|maxmemory_human"
```
If `connected_clients` approaches `maxclients` → connection exhaustion. If `maxmemory-policy=allkeys-lru` and memory is near `maxmemory` → Redis is evicting cache keys.
**Fix:** For connection exhaustion: reduce connection hold time or use connection pooling (phpredis with persistent connections). For key eviction: change policy to `volatile-lru` (only evict keys with TTL) or increase `maxmemory`.

---

## CATEGORY 9 — SECURITY (FUNCTIONAL BUGS ONLY)

*Only patterns where a security mechanism causes a functional breakage the developer is actively debugging.*

### Pattern: CSRF token missing — form POST returns HTTP 419 or is rejected
**Symptom:** Form submission returns `419 Page Expired` (Laravel) or POST is rejected without explanation. GET requests to the same URL work. AJAX POST fails. Works in Postman (which skips CSRF).
**Why:** Laravel's `VerifyCsrfToken` middleware requires a `_token` field in every POST/PUT/DELETE form request matching the session token. Without it, 419. For AJAX: the `X-CSRF-TOKEN` header must be set. Routes in `routes/api.php` are excluded from CSRF by default — web routes are not.
**Prove:**
```bash
# Check if the form has the CSRF token field
curl -s https://app.example.com/your-form | grep "_token"

# Check if the route has CSRF middleware
php artisan route:list --path=your-route | grep Middleware
```
In browser DevTools: check the POST request body. If no `_token` field → Blade `@csrf` missing. If `_token` present but 419 → token expired (session expired, likely).
**Fix:** Add `@csrf` inside every Blade form:
```html
<form method="POST" action="/orders">
    @csrf
    ...
</form>
```
For AJAX:
```javascript
headers: { 'X-CSRF-TOKEN': document.querySelector('meta[name="csrf-token"]').content }
```
For long sessions: increase `SESSION_LIFETIME` in `.env`.

---

## CATEGORY 10 — PHP VERSION & ENVIRONMENT MISMATCH

### Pattern: CLI PHP and FPM serve different PHP versions — fix applied to wrong runtime
**Symptom:** `php --version` shows PHP 8.2. Added PHP 8 feature (`str_contains`, `match`, named arguments, union types). Error persists in the browser. `php artisan` works. Clearing caches, restarting nginx has no effect.
**Why:** Servers with multiple PHP versions installed have separate CLI (`/usr/bin/php8.2`) and FPM (`php8.2-fpm`) binaries. Nginx/Apache is configured to forward to a specific FPM socket — which may be a different version than the CLI default. Developers run `php --version` on CLI; the browser runs through FPM.
**Prove:**
```bash
# CLI version
php --version

# FPM version — check which socket nginx points to
grep fastcgi_pass /etc/nginx/sites-enabled/your-site
# e.g. fastcgi_pass unix:/run/php/php7.4-fpm.sock  ← version mismatch!

# Confirm via phpinfo
curl -s http://localhost/phpinfo.php | grep "PHP Version" | head -1
# Or add temporarily: <?php phpinfo(); die;
```
If CLI shows `8.2` and nginx config shows `php7.4-fpm.sock` → version mismatch confirmed. This is the pathognomonic finding.
**Fix:** Update nginx fastcgi_pass to point to the correct FPM socket:
```nginx
fastcgi_pass unix:/run/php/php8.2-fpm.sock;
```
Confirm: `sudo systemctl restart nginx && curl http://localhost/phpinfo.php | grep 'PHP Version'`.

### Pattern: Laravel `.env` not loaded in CLI / cron context — config values null in artisan
**Symptom:** `php artisan` command fails with connection refused or DB error. The same operation works in the browser. `config('database.connections.mysql.host')` is null in artisan. Cron jobs fail silently — no DB write, no queue message, no log.
**Why:** Laravel loads `.env` from the current working directory. When a cron job runs `artisan` with a different working directory (e.g., `cd /` or running from the home directory), `.env` is not found and all environment config values are empty. The application continues with null values — DB connection fails, queue connection fails.
**Prove:**
```bash
# From the project directory — works
php artisan tinker --execute="dump(config('database.connections.mysql.host'));"

# Simulate cron working directory — fails
cd / && php /var/www/html/artisan tinker --execute="dump(config('database.connections.mysql.host'));"
```
If second command returns `null` for the host → working directory is the cause.
**Fix:** Always `cd` to the project root in cron entries:
```
* * * * * cd /var/www/html && /usr/bin/php8.2 artisan schedule:run >> /dev/null 2>&1
```
Or use the `--env` flag and absolute `.env` path: `php artisan --env=/var/www/html/.env schedule:run`.

### Pattern: Composer runtime version conflict — package installed but wrong version at runtime
**Symptom:** `composer require vendor/package` succeeds with no errors. `Class 'Aws\S3\S3Client' not found` at runtime. Or: method exists in the class but throws "Call to undefined method" — wrong version resolved. Running `composer install` on a fresh checkout produces different behaviour.
**Why:** Composer resolves a dependency graph that satisfies all constraints simultaneously. If Package A requires `aws/aws-sdk-php:^3.0` and Package B requires `aws/aws-sdk-php:^2.0`, Composer picks one version — one of the packages silently gets the wrong version at runtime. No error during `composer require`. Error only appears when the code path using the wrong version is exercised.
**Prove:**
```bash
# Check what version is actually installed
composer show aws/aws-sdk-php

# Check which packages conflict on the version
composer why-not aws/aws-sdk-php 3.x

# Check overall dependency health
composer diagnose

# Show full dependency tree for the package
composer depends aws/aws-sdk-php
```
`composer why-not aws/aws-sdk-php 3.x` names exactly which installed package prevents the required version.
**Fix:** Update the conflicting package: `composer require conflicting/package:^new-version`. Or: use `composer update --with-all-dependencies` to let Composer resolve a compatible graph. If conflict cannot be resolved: consider replacing one of the packages.

