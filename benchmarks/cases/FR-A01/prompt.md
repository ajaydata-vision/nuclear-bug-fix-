# FR-A01: Packaged Bridge Launch Fails Only In Onefile Build

## User Prompt

The app works perfectly from source, but the PyInstaller `.exe` fails to launch
our WhatsApp Node bridge. It says the script does not exist. We bundle the app
successfully and the main window opens, but the bridge is dead in packaged
mode. What is actually wrong?

## Context Provided To The Skill

- stack: Python 3.11.8 + PyInstaller 6.6.0 + Node 20.11.0 bridge
- versions: onefile build on Windows 11
- environment: packaged `.exe` only
- logs:
  - `[packaged] frozen=True`
  - `[packaged] resolved bridge path=C:\Users\Ajay\AppData\Local\Temp\_MEI31202\app\bridge\wa_bridge.js`
  - `[spawn] ENOENT: file not found`
  - attached `assets/extracted-tree.txt` shows the extracted onefile layout from the failing run
- code excerpt:

```python
BASE_DIR = Path(__file__).resolve().parent
BRIDGE_SCRIPT = BASE_DIR / "bridge" / "wa_bridge.js"

proc = await asyncio.create_subprocess_exec("node", str(BRIDGE_SCRIPT))
```

- reproduction:
  1. Build onefile exe
  2. Launch packaged app
  3. Open WhatsApp panel
  4. Bridge spawn fails
