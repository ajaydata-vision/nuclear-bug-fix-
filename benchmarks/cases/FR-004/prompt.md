# FR-004: Packaged Helper Launch Fails Even With Frozen-Aware Path

## User Prompt

Our PyInstaller build works from source, but in the packaged app the WhatsApp
bridge fails immediately because the helper script cannot be found. The parent
process opens the main window, then the bridge spawn dies with `ENOENT`. What
is the real bug?

## Context Provided To The Skill

- stack: Python 3.11.8 + PyInstaller 6.6.0 + Node 20.11.0 helper
- versions: Windows 11 packaged `.exe`
- environment: packaged build only
- logs:
  - `[packaged] frozen=True`
  - `[packaged] helper path=C:\Users\Ajay\AppData\Local\Temp\_MEI12345\bridge\wa_bridge.js`
  - `[spawn] ENOENT: no such file or directory`
  - attached `assets/extracted-tree.txt` shows the packaged file tree from the failing run
- code excerpt:

```python
def resource_path(*parts):
    if getattr(sys, "frozen", False):
        base = Path(sys._MEIPASS)
    else:
        base = Path(__file__).resolve().parent
    return base.joinpath(*parts)

BRIDGE_SCRIPT = resource_path("bridge", "wa_bridge.js")
await asyncio.create_subprocess_exec("node", str(BRIDGE_SCRIPT))
```

- reproduction:
  1. Build the onefile exe
  2. Launch the packaged app
  3. Open the bridge-dependent panel
  4. Spawn fails immediately
