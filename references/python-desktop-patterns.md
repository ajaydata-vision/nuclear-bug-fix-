# Python Desktop / qasync Patterns

Use this file for PyQt6, qasync, desktop websocket, scheduler, and local SQLite
bugs inside a GUI process.

Format for every verdict:
- Symptom
- Strongest signals
- Why
- Prove
- Accepted fix
- Wrong fixes to reject
- Sentinel logs
- Verify

---

### Pattern: qasync event loop ownership is wrong

**Symptom:** UI shows, but awaited slot logic never resumes, or tasks behave as if
they are scheduled on a loop that is not being pumped by Qt.

**Strongest signals:**
- `asyncio.create_task()` succeeds but task never completes
- Multiple loop IDs appear in logs
- Code uses `asyncio.run()` or a plain `new_event_loop()` around a Qt app

**Why:** `qasync` must own the running asyncio loop for the Qt application. If
the app starts one loop and schedules work onto another, coroutines are queued
on a loop that never advances.

**Prove:**
- Log `hex(id(asyncio.get_running_loop()))` in the startup path and in the
  failing slot.
- If the IDs differ, or the slot has no running loop, loop ownership is wrong.

**Accepted fix:** Create a single `qasync.QEventLoop(app)`, set it as the
current loop, and run the app through that loop. All UI coroutines must target
that loop only.

**Wrong fixes to reject:**
- Add sleeps or timers so the coroutine "has time" to run
- Create a second background asyncio loop for UI work
- Wrap the failing call in `asyncio.run()` inside a slot

**Sentinel logs:**
- Loop ID at startup
- Loop ID inside failing slot
- Task creation and completion on the same loop

**Verify:**
- Failing action resumes and updates UI once per click
- No orphan loop remains after exit
- Shutdown completes without pending-task warnings

---

### Pattern: Async Qt slot returns a coroutine that nobody awaits

**Symptom:** Button click appears to do nothing. Sometimes a warning like
`coroutine was never awaited` appears later.

**Strongest signals:**
- Signal connected directly to an `async def`
- No `@asyncSlot()` decorator or explicit task scheduling
- Warning appears only on shutdown or GC

**Why:** Qt signals are synchronous. If a raw coroutine function is connected,
Qt calls it like a normal callable and receives a coroutine object. No one
awaits it, so the body never runs.

**Prove:**
- Log at the top of the slot. If the log never appears but the click signal
  does, the coroutine is not executing.
- Inspect the signal connection: direct async function vs `@asyncSlot()`.

**Accepted fix:** Use `@asyncSlot()` for async Qt slots, or connect a sync slot
that schedules the coroutine on the running qasync loop.

**Wrong fixes to reject:**
- Add `await` inside code that is never entered
- Convert the whole UI to threads to avoid the warning
- Suppress the warning and keep the same connection pattern

**Sentinel logs:**
- Signal fired
- Async slot entered
- Async slot completed

**Verify:**
- Click always executes the coroutine body
- No `coroutine was never awaited` warning remains
- Repeated clicks do not leak pending tasks

---

### Pattern: Blocking work runs on the UI / qasync event loop

**Symptom:** Window freezes during email, IMAP, filesystem, SQLite, HTTP, or
CPU-heavy work. Spinner stops animating.

**Strongest signals:**
- Freeze lasts exactly as long as one synchronous call
- Stack trace or logs show `imaplib`, `smtplib`, file I/O, or CPU work inside
  the UI-triggered path
- User can reproduce by clicking one action

**Why:** qasync does not make blocking code non-blocking. Synchronous calls
still block the single event loop thread that drives Qt repaint, timers, and
async callbacks.

**Prove:**
- Log timestamps before and after the blocking call.
- Log current thread name; if it is the main/UI thread during the blocking
  operation, the cause is confirmed.

**Accepted fix:** Move blocking work off the UI loop with `asyncio.to_thread`,
`run_in_executor`, or a worker object/thread. Keep UI mutations on the main
thread.

**Wrong fixes to reject:**
- Add `await asyncio.sleep(0)` around synchronous code
- Increase timer intervals
- Blame PyQt repainting when the freeze matches blocking I/O duration

**Sentinel logs:**
- Main-thread entry into the action
- Start/end timestamp for the blocking call
- Main-thread UI update after the worker result returns

**Verify:**
- UI stays responsive during the operation
- Progress indicator continues animating
- Repeated runs do not freeze or deadlock

---

### Pattern: Cross-thread QObject / widget mutation

**Symptom:** Random crashes, `QObject` thread-affinity errors, or widgets update
unreliably only under background activity.

**Strongest signals:**
- Error mentions parent/thread affinity
- Worker thread calls widget methods directly
- Problem appears only when background work completes

**Why:** Qt widgets and most `QObject` state must be accessed from the owning
thread, typically the main GUI thread. Direct cross-thread mutation violates
Qt's threading contract.

**Prove:**
- Log thread ID in the worker and inside the UI update.
- If the worker thread invokes widget methods directly, the cause is proven.

**Accepted fix:** Emit a signal to the main thread, use queued connections, or
marshal the update back to the GUI thread before touching widgets.

**Wrong fixes to reject:**
- Add locks around widget access
- Disable warnings and continue cross-thread calls
- Move the entire UI to the worker thread

**Sentinel logs:**
- Worker thread ID
- GUI thread ID
- UI update executed on GUI thread only

**Verify:**
- Background completion updates the UI without warnings
- Repeated operations do not crash or leak orphan QObjects
- Shutdown remains clean

---

### Pattern: Shutdown hangs because background tasks never cancel cleanly

**Symptom:** App window closes, but process stays alive. Or exit shows
`Task was destroyed but it is pending!`.

**Strongest signals:**
- Websocket client, APScheduler job, long-lived task, or reconnect loop exists
- Exit path does not await cancellation
- Process remains after UI closes

**Why:** Closing the window does not automatically stop asyncio tasks, websocket
reconnect loops, timers, or schedulers. The event loop waits on unfinished
tasks, or destroys them during interpreter shutdown.

**Prove:**
- Log all outstanding tasks during shutdown.
- Log scheduler/websocket stop hooks. If they never run, shutdown ordering is
  wrong.

**Accepted fix:** On close, stop schedulers, cancel long-lived tasks, await
their completion, and then stop the loop. Suppress only expected
`CancelledError`.

**Wrong fixes to reject:**
- Force `os._exit(0)` as the main fix
- Ignore pending-task warnings
- Kill the process without closing child resources

**Sentinel logs:**
- Close event entered
- Task cancellation count
- Websocket/scheduler stopped
- Loop stopped after cleanup

**Verify:**
- Process exits immediately after window close
- No pending-task warnings remain
- Reopen/close cycles do not leave orphan child processes

---

### Pattern: SQLite lock or stale state from sharing one connection across UI and background work

**Symptom:** Intermittent `database is locked`, missing updates, or UI shows stale
rows after background sync.

**Strongest signals:**
- One SQLite connection/session shared across UI callbacks and worker tasks
- Background job and UI both write during the same period
- Errors increase under burst activity

**Why:** SQLite is sensitive to connection/thread ownership and write
serialization. Sharing one connection across UI and worker contexts causes lock
contention or undefined state flow.

**Prove:**
- Log connection identity and thread ID for each query.
- If the same connection is used from multiple threads/tasks, or write overlap
  matches the lock window, the cause is proven.

**Accepted fix:** Use one async access layer with serialized writes, or separate
connections per thread/task boundary plus a single write queue. Keep UI reads
and background writes coordinated. Two concrete SQLite-level settings that
directly address the `database is locked` symptom, in addition to the
architectural fix above: `PRAGMA busy_timeout = 5000;` (makes a connection
wait up to 5s for a lock to clear instead of failing immediately — set this
on every connection at open time) and `PRAGMA journal_mode = WAL;` (Write-Ahead
Logging lets readers proceed concurrently with a writer instead of blocking,
which is the more common real-world trigger than a single shared connection
across threads — multiple *separate* connections writing concurrently without
WAL hit this just as often).

**Wrong fixes to reject:**
- Retry blindly in a loop forever
- Disable SQLite thread checks without redesigning access
- Add arbitrary sleeps between queries

**Sentinel logs:**
- Connection ID per operation
- Write queue start/finish
- Lock wait duration

**Verify:**
- Burst writes no longer produce lock errors
- UI sees fresh state after sync
- App close does not leave the DB busy
