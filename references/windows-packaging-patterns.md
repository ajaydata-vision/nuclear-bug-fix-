# Windows Packaging / PyInstaller Patterns

Use this file for bugs that appear only in frozen `.exe` builds, especially
PyInstaller onefile/onedir on Windows.

---

### Pattern: Source works, packaged build fails because resource path is wrong

**Symptom:** App works from source but packaged `.exe` cannot find templates,
bridge scripts, icons, prompts, or config files.

**Strongest signals:**
- Code relies on `cwd` or `__file__` relative paths
- Failure appears only in the frozen build
- Missing file exists in the repo but not at runtime path

**Why:** Frozen apps run from a different layout. In PyInstaller, resources may
live under `sys._MEIPASS` or a bundled data directory, not beside the original
source file.

**Prove:**
- Log `sys.executable`, `cwd`, `__file__`, `getattr(sys, "_MEIPASS", "")`, and
  the resolved resource path.
- If the resolved path points to a dev layout in a frozen runtime, the cause is
  confirmed.

**Accepted fix:** Centralize resource resolution with a helper that uses
`sys._MEIPASS` when frozen and source-relative paths otherwise.

**Wrong fixes to reject:**
- Change the working directory globally as the main fix
- Copy random files beside the `.exe` manually
- Hardcode an absolute developer path

**Sentinel logs:**
- Frozen flag
- `_MEIPASS`
- Resolved resource path

**Verify:**
- Same resource resolves correctly from source and packaged builds
- Packaged app starts from arbitrary working directories
- Child bridge assets resolve in the bundled layout

---

### Pattern: Hidden import missing from packaged build

**Symptom:** Packaged app crashes with `ModuleNotFoundError`, dynamic plugin
import failure, or feature-specific import errors not seen in development.

**Strongest signals:**
- Stack trace appears only inside `.exe`
- Missing module is imported dynamically, by plugin, or by optional backend
- Source run works in the same environment

**Why:** PyInstaller cannot always discover dynamic imports statically. The
module is present in development but absent from the bundled archive.

**Prove:**
- Compare import path in source vs packaged stack trace.
- Inspect spec file / build command for hidden imports or collection hooks.

**Accepted fix:** Add the missing hidden import or hook, rebuild, and verify the
bundle contains it.

**Wrong fixes to reject:**
- Install the package globally on the target machine and call it fixed
- Add retry logic around an import failure
- Blame Windows permissions when the traceback shows a missing module

**Sentinel logs:**
- Frozen import target
- Hidden import list used in build
- Runtime traceback in packaged form

**Verify:**
- Packaged feature imports cleanly on a machine without source tree access
- Rebuild does not regress other dynamic imports
- Startup path no longer depends on a dev environment

---

### Pattern: Qt platform plugin or resource plugin missing in frozen build

**Symptom:** Packaged app fails to start with Qt plugin errors like
`Could not load the Qt platform plugin "windows"`.

**Strongest signals:**
- Error appears only on target machines or only in packaged runs
- Stack trace references Qt platform/image/style plugins
- Dev run works with local Qt install

**Why:** Qt requires plugin directories and resources that must be collected into
the frozen app. If the plugin tree is incomplete or resolved incorrectly, Qt
cannot start.

**Prove:**
- Capture the exact packaged startup error.
- Inspect the bundled Qt plugin directories and runtime plugin path.

**Accepted fix:** Use the correct PyInstaller Qt hooks/collectors, ensure the
needed platform plugins are bundled, and verify plugin lookup paths in the
frozen app.

**Wrong fixes to reject:**
- Tell users to install a full Qt SDK as the main fix
- Ship random DLLs beside the app without verifying plugin lookup
- Treat this as a generic Python import issue

**Sentinel logs:**
- Frozen plugin lookup path
- Available bundled plugin directories
- Startup error line from packaged build

**Verify:**
- App starts on a clean Windows machine
- High-DPI/icons/resources still load
- Onefile and onedir behavior are both understood and documented

---

### Pattern: Packaged app writes to a non-writable install path

**Symptom:** Sessions, SQLite DB, logs, auth files, or cache fail only from the
installed `.exe`, often under `Program Files`.

**Strongest signals:**
- App writes beside the `.exe` or current working directory
- Failure happens on user machines, not on dev workstations
- Error mentions permissions, missing file, or silent state loss

**Why:** Install directories may be read-only. Frozen apps must store mutable
state under a user-writable path such as `%APPDATA%` or `%LOCALAPPDATA%`.

**Prove:**
- Log target write path and whether it is writable.
- If path resolves under install dir or cwd and write fails, the cause is
  confirmed.

**Accepted fix:** Move mutable state to a per-user writable directory and
create it explicitly at startup.

**Wrong fixes to reject:**
- Run the app as administrator as the primary fix
- Keep writing beside the executable
- Silence the write error and continue

**Sentinel logs:**
- Resolved writable state dir
- File creation success/failure
- Migration of old state path if applicable

**Verify:**
- Fresh install persists state without admin rights
- Upgrade path preserves prior user data
- Multi-user machines keep data isolated per user

---

### Pattern: Bundled subprocess or helper script is missing

**Symptom:** Packaged parent app starts, but child Node/Python helper never
launches or exits immediately because the script/binary is absent.

**Strongest signals:**
- Parent spawn path works from source only
- Packaged runtime cannot find bridge/helper script
- Error mentions missing file, ENOENT, or spawn failure

**Why:** Freezing the parent does not automatically bundle helper scripts,
executables, or their runtime files. The parent points at a path that does not
exist inside the packaged layout.

**Prove:**
- Log the exact spawn command and resolved helper path from the packaged app.
- If the file is absent in the bundle, the cause is proven.

**Accepted fix:** Bundle the helper explicitly as data/binary, resolve it from
the frozen runtime layout, and verify the packaged spawn command points there.

**Wrong fixes to reject:**
- Retry spawns forever
- Use a source-tree relative path in packaged mode
- Assume PyInstaller bundled the helper because it bundled the parent

**Sentinel logs:**
- Resolved helper path
- Spawn command
- Child exit code and stderr

**Verify:**
- Parent launches helper successfully from packaged build
- Helper version matches parent version
- Failure mode is explicit if helper is missing

**See also:** this pattern is "the file is genuinely absent from the bundle"
(ENOENT). If the spawn instead resolves to a path that exists but is wrong —
different failure signature, no ENOENT — see
`references/bridge-adapter-patterns.md` → "Parent and child use different
runtime/build assumptions."

---

### Pattern: Onefile startup issues — NOT an extraction race, but AV scanning or a second `_MEIPASS`

**Symptom:** Onefile build behaves differently from onedir: slow or failing
first launch, resource-not-found errors, or a spawned child process that
can't find a bundled file the parent could see fine.

**Strongest signals:**
- Bug happens only in onefile mode, and mainly on the FIRST launch after
  install/update (points to AV scanning) — OR only when the app spawns a
  child process/subprocess of itself (points to the second `_MEIPASS`)
- Temporary extraction path appears in logs
- `multiprocessing` is used, or the app re-execs `sys.executable`

**Why — two distinct, unrelated mechanisms, not a startup race:** PyInstaller's
onefile bootloader extraction to `_MEIPASS` is synchronous and completes
in full BEFORE your entry-point script's first line ever executes — there
is no genuine race for resource access within a single process. The two
real mechanisms that produce this symptom are:
1. **AV/SmartScreen scanning the freshly-extracted temp exe/files** adds
   latency on first run, or can quarantine a file mid-extraction, producing
   a first-run-only failure that looks like a race but is a scanner delay.
2. **A spawned child process gets its own, separate `_MEIPASS` extraction
   directory.** If the app uses `multiprocessing` or re-execs
   `sys.executable` (common in some GUI/worker architectures), each child
   process re-runs the PyInstaller bootloader and extracts to a NEW temp
   directory — a path resolved from the PARENT's `_MEIPASS` and handed to
   the child (e.g. via an argument or env var) is invalid in the child's
   own extraction directory.

**Prove:**
- Log frozen mode and `_MEIPASS` in BOTH the parent and any child process —
  if they differ, mechanism 2 is confirmed.
- Log the first-launch wall-clock time from process start to first resource
  access; a large one-time delay only on a clean machine's first launch
  (absent on subsequent launches) points to mechanism 1 (AV scan), not code.

**Accepted fix:** For mechanism 2 — never pass a parent-resolved `_MEIPASS`
path to a child; each process must resolve its own `getattr(sys, "_MEIPASS", ...)`
independently, and if the child needs `multiprocessing`, call
`multiprocessing.freeze_support()` as the first line in `if __name__ == "__main__":`
(without it, a frozen onefile app on Windows using `multiprocessing.Process`
can spawn infinitely — each "child" re-runs the whole app from the top,
which itself spawns another child). For mechanism 1 — code signing the
executable measurably reduces AV/SmartScreen scan time and quarantine risk;
don't add sleeps to "wait out" the scan, since scan duration is not
controllable from inside the process.

**Wrong fixes to reject:**
- Treat onefile and onedir as interchangeable
- Add arbitrary sleeps assuming there's an extraction race to wait out — there isn't
- Blame Windows Defender without path/timing evidence, when the actual cause is
  an unresolved second `_MEIPASS` in a child process

**Sentinel logs:**
- Frozen mode
- `_MEIPASS` value, logged separately in parent AND any child process
- First-launch timing from process start to first resource access

**Verify:**
- Onefile startup works on cold (post-AV-scan) and warm launches
- If the app spawns children: child correctly resolves its OWN `_MEIPASS`,
  not one inherited from the parent
- Onedir and onefile differences are covered by tests

### Pattern: `multiprocessing.Process` in a frozen onefile app spawns infinitely
**Symptom:** Onefile Windows build using `multiprocessing` explodes into dozens/hundreds of new processes on launch, or the app appears to hang while spawning windows/processes rapidly. Works fine running from source (`python app.py`).
**Why:** On Windows, `multiprocessing` re-executes the frozen executable itself to create a new process (there's no `fork()`). Without `multiprocessing.freeze_support()` guarding the entry point, each "child" re-runs the entire script from the top — including the `multiprocessing.Process(...).start()` call that spawned it — so every child spawns another child, recursively.
**Prove:** Task Manager / Process Explorer during launch shows the process count climbing rapidly with no stabilization. Check whether `if __name__ == "__main__":` wraps both `freeze_support()` and the `Process(...).start()` call — if `freeze_support()` is absent or the multiprocessing entry code sits outside the `__main__` guard, this is confirmed.
**Fix:**
```python
import multiprocessing

def main():
    p = multiprocessing.Process(target=worker)
    p.start()
    p.join()

if __name__ == "__main__":
    multiprocessing.freeze_support()  # must be the first call inside the guard
    main()
```
**Do NOT:** move the `Process(...)` call itself into a `try/except` to "catch" the runaway spawning — that treats the symptom; the guard is the actual fix.

### Pattern: Windows SmartScreen blocks distribution of an unsigned PyInstaller exe
**Symptom:** End users see "Windows protected your PC" / "Microsoft Defender SmartScreen prevented an unrecognized app from starting" when launching the distributed `.exe`, even though it runs fine on the developer's machine. This is a distribution/first-run blocker for END USERS, distinct from the AV-scan-latency issue above (which affects launch speed, not an outright block).
**Why:** SmartScreen's reputation system flags executables with no code-signing certificate and low download/install-count reputation. A freshly built, unsigned PyInstaller exe has neither, regardless of how safe the code actually is.
**Prove:** Reproduce on a clean Windows machine (or VM) that has never run the exe before — SmartScreen's block is reputation-based and won't reliably trigger on a machine that's already run/allowed it once.
**Fix:** Code-sign the executable with an Authenticode certificate (EV certificates get SmartScreen reputation immediately; standard OV certificates build reputation over time/downloads). Until signed, document the "More info → Run anyway" click-through for users, but do not rely on that as a permanent solution for a public-facing release.
**Do NOT:** tell users to disable SmartScreen or Windows Defender system-wide — that's a security regression for the user, not a fix for the distribution problem.
