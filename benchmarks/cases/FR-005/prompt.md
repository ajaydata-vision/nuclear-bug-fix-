# FR-005: Onefile Startup Races With Extraction And Child Launch

## User Prompt

Our onefile PyInstaller build sometimes fails on the very first launch after a
fresh install. The main window appears, but the bridge or background helper
dies before it can finish starting. Re-launching often works. What is the real
bug?

## Context Provided To The Skill

- stack: Python 3.11.8 + PyInstaller 6.6.0 + PyQt6 6.7.0
- versions: Windows 11 onefile build
- environment: packaged `.exe` only, fresh install
- logs:
  - `[packaged] frozen=True`
  - `[packaged] _MEIPASS=C:\\Users\\Ajay\\AppData\\Local\\Temp\\_MEI44781`
  - `[packaged] child launch attempted immediately after startup`
  - `[packaged] child missing on first run, present on second run`
- code excerpt:

```python
def start_child(self):
    child = self._resolve_child_path()
    asyncio.create_task(asyncio.create_subprocess_exec(child))

def _resolve_child_path(self):
    return Path(__file__).resolve().parent / "bridge" / "helper.exe"
```

- reproduction:
  1. Install the onefile build on a clean machine
  2. Launch it once immediately after install
  3. First launch fails, second launch often succeeds
