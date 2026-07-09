# Bridge / Adapter / Unofficial Client Patterns

Use this file for Python <-> Node subprocess bridges, framed stdout/stderr
protocols, Baileys-style adapters, websocket relays, and unofficial scrapers.

Before choosing a pattern, split the bug family:

- Local bridge / IPC / realtime lifecycle: spawn path, cwd/env, stdout framing,
  ready handshake, listener timing, reconnect leaks, packaged parent/child
  mismatch.
- Upstream provider / scraper drift: no local change, raw response shape/status
  changed, maintainer issues report breakage, provider anti-bot/auth markup
  shifted.

If there was no local code/deploy/version change and the upstream response body,
status, or DOM signature changed, jump to provider-drift handling and external
intelligence before modifying bridge or parser logic.

---

### Pattern: Stdout protocol is polluted by debug logs

**Symptom:** Bridge starts, but parent reports JSON parse errors, dropped events,
or random protocol corruption.

**Strongest signals:**
- Parent reads JSON or framed messages from child stdout
- Child also prints debug logs to stdout
- Failures correlate with new logging or verbose mode

**Why:** If stdout is the transport channel, every extra log line becomes
protocol garbage. The parent cannot distinguish a debug print from a message
frame.

**Prove:**
- Capture raw stdout bytes.
- If non-protocol lines appear in the stream before parse failure, the cause is
  confirmed.

**Accepted fix:** Reserve stdout for framed protocol only. Send diagnostics to
stderr or a file sink. Prefix/structure all protocol frames consistently.

**Wrong fixes to reject:**
- Add more tolerant JSON parsing while leaving mixed logs on stdout
- Log only "sometimes" on stdout
- Blame websocket transport when corruption is visible in raw stdout

**Sentinel logs:**
- Raw frame sequence number on stdout
- Diagnostic logs on stderr only
- Parent parse success/failure with frame index

**Verify:**
- Bridge handles verbose logging without protocol breakage
- Parent receives valid frames only
- Reconnect path preserves framing discipline

---

### Pattern: Child process started != bridge ready

**Symptom:** Parent says bridge is connected, but the first inbound events are
missing. Later events work.

**Strongest signals:**
- Parent marks ready when subprocess PID exists
- Child emits a later `ready/authenticated` event
- Missing messages happen only right after startup

**Why:** Process spawn is not the same as protocol readiness. If the parent
attaches consumers or releases buffered work before the child has completed its
own authentication/handshake, early events are lost.

**Prove:**
- Log timestamps for: parent spawn, child ready, parent listener attach, first
  inbound event.
- If events arrive before the listener or before explicit ready, the cause is
  proven.

**Accepted fix:** Add an explicit ready handshake and do not release traffic
until it is received. Buffer or replay inbound events until the parent confirms
listener attachment.

**Wrong fixes to reject:**
- Add arbitrary startup sleeps
- Treat child PID creation as equivalent to ready
- Retry the missed first event manually without fixing readiness

**Sentinel logs:**
- `spawned`
- `listener_attached`
- `bridge_ready`
- `first_event_seq`

**Verify:**
- First inbound event after startup is always delivered
- Cold starts and reconnects behave the same way
- No race remains at normal and slow startup times

---

### Pattern: Reconnect path registers listeners more than once

**Symptom:** Same WhatsApp/websocket event is delivered twice or more after one
or more reconnects.

**Strongest signals:**
- Duplicate delivery starts only after reconnect
- Listener registration lives inside reconnect logic
- Event count grows with each reconnect

**Why:** Every reconnect adds another live handler to the same event source or
replacement source. One inbound event fan-outs to N handlers.

**Prove:**
- Log listener registration count and reconnect counter.
- If the handler is attached again without teardown, the cause is confirmed.

**Accepted fix:** Register once per socket lifecycle and tear down old
listeners explicitly before reconnect. Or recreate the socket and handler graph
cleanly with old references disposed.

**Wrong fixes to reject:**
- Deduplicate only at the database layer while leaving duplicate listeners
- Restart the whole app as the primary fix
- Ignore duplicates because downstream is idempotent

**Sentinel logs:**
- Reconnect counter
- Listener attach/detach count
- Event ID delivered once at parent boundary

**Verify:**
- One event yields one handler invocation before and after reconnect
- Reconnect storms do not increase delivery count
- Memory usage does not grow with each reconnect

---

### Pattern: Parent and child use different runtime/build assumptions

**Symptom:** Bridge works in development and fails in packaged or deployed runs.
Child starts with wrong script, wrong cwd, wrong env, or wrong version.

**Strongest signals:**
- Parent spawns child via relative path
- Child version/build differs from parent release
- Failure appears only in packaged or production runtime

**Why:** Parent and child are separate runtimes. If the parent assumes dev paths
or ships one side without the other, the protocol layer fails even though each
piece works alone.

**Prove:**
- Log parent version, child version, spawn command, cwd, and resolved child
  executable/script path.
- If packaged path resolution differs from dev, the cause is proven.

**Accepted fix:** Resolve child binaries/scripts from the packaged runtime
layout, stamp both sides with the same release/version, and log the exact spawn
command.

**Wrong fixes to reject:**
- Retry spawns without checking resolved path
- Hardcode a developer workstation path
- Assume the child bundled correctly because the parent did

**Sentinel logs:**
- Parent release/version
- Child release/version
- Resolved command path

**Verify:**
- Same release works in dev and packaged form
- Parent refuses startup if child binary/script is missing or version-mismatched
- First handshake succeeds with the resolved packaged path

**See also:** this pattern is "the resolved path points to the wrong place." If
the resolved path is correct but the file is simply absent from the bundle
(different failure signature — `ENOENT`/"file not found" vs. a wrong-but-existent
path), see `references/windows-packaging-patterns.md` → "Bundled subprocess or
helper script is missing." SKILL.md's co-loading rule loads both files together
for exactly this ambiguity — check both before concluding which one applies.

---

### Pattern: Unofficial scraper breaks because upstream provider drifted

**Symptom:** Scraper suddenly returns empty results, malformed rows, or 403/429
patterns even though local parsing code was unchanged.

**Strongest signals:**
- Breakage starts without a local code change
- Raw HTML/content shape differs from previous captures
- Maintainer issues/changelog mention breakage or anti-bot changes

**Why:** Unofficial scrapers depend on unstable HTML, tokens, or undocumented
provider behavior. Upstream markup/auth changes invalidate selectors and flows.

**Prove:**
- Capture raw upstream response body or status.
- Compare with last known good sample.
- Check external intelligence: library issues, recent breakage reports, or
  provider-side changes.

**Accepted fix:** Treat this as provider drift first. Update selectors/parsing
only if raw response still contains the expected data. Otherwise pin a known
working version, apply the upstream workaround, or move to a supported API.

**Wrong fixes to reject:**
- Rewrite local business logic before checking raw upstream output
- Blame local caching when the raw response already lacks the data
- Assume "no exception" means the provider contract is unchanged

**Sentinel logs:**
- Upstream status code
- Raw response signature or first bytes
- Parser matched item count
- Scraper library version

**Verify:**
- Same query returns expected items after the provider-aware fix
- Empty-result handling is explicit
- Future upstream drift is surfaced by logs, not silent empties

---

### Pattern: WebSocket relay emits before downstream listener is attached

**Symptom:** Only the first event after connect disappears. Subsequent realtime
events arrive normally.

**Strongest signals:**
- Connect and first event happen back-to-back
- Listener registration happens after `connect()`
- Missing event is always the earliest event in the session

**Why:** The source emits before the consumer is ready. This is an ordering bug,
not a transport failure.

**Prove:**
- Log `listener_attached_at`, `socket_open_at`, and `first_event_at`.
- If the first event precedes listener attach, the cause is proven.

**Accepted fix:** Attach listeners before opening the socket, or buffer until
consumer registration completes.

**Wrong fixes to reject:**
- Add reconnects for an event that was never observed
- Add duplicate listeners "just in case"
- Increase websocket timeout values

**Sentinel logs:**
- Listener attached timestamp
- Socket open timestamp
- First event sequence number

**Verify:**
- First event after connect is always received
- Reconnect path preserves the same ordering
- No duplicate listeners are introduced
