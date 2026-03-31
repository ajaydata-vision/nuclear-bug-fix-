# Windows Packaging / PyInstaller Patterns

Use this file for bugs that appear only in frozen `.exe` builds, especially
PyInstaller onefile/onedir on Windows.

---

## Pattern: Source works, packaged build fails because resource path is wrong

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

## Pattern: Hidden import missing from packaged build

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

## Pattern: Qt platform plugin or resource plugin missing in frozen build

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

## Pattern: Packaged app writes to a non-writable install path

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

## Pattern: Bundled subprocess or helper script is missing

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

---

## Pattern: Onefile extraction/runtime assumptions break startup ordering

**Symptom:** Onefile build behaves differently from onedir: startup race,
temporary path issues, or first-run-only failures.

**Strongest signals:**
- Bug happens only in onefile mode
- Temporary extraction path appears in logs
- Relative paths or early child spawns happen before extraction-ready state

**Why:** Onefile apps extract to a temp directory at runtime. Code that assumes a
stable install directory or immediate helper availability can race extraction or
target the wrong path.

**Prove:**
- Log frozen mode, extraction path, and the exact moment child/resource access
  occurs.
- If helper/resource access happens before the extracted file exists, the cause
  is confirmed.

**Accepted fix:** Resolve resources from the final extracted path, delay helper
start until extraction-ready, and test onefile separately from onedir.

**Wrong fixes to reject:**
- Treat onefile and onedir as interchangeable
- Add arbitrary sleeps without verifying readiness
- Blame Windows Defender without path/timing evidence

**Sentinel logs:**
- Frozen mode
- Extraction path
- First access timestamp to bundled resource/helper

**Verify:**
- Onefile startup works on cold and warm launches
- Helper/resources resolve after extraction
- Onedir and onefile differences are covered by tests
