# FR-003: Packaged App Saves Session Data Beside The EXE

## User Prompt

Our packaged app works when developers run it from their desktop, but users who
install it under `Program Files` have to re-scan the WhatsApp QR code every
launch. The logs show auth state write failures. Where is the real bug?

## Context Provided To The Skill

- stack: Python 3.11.8 + PyInstaller 6.6.0 + Node 20.11.0 helper
- versions: Windows 11 packaged app
- environment: installed under `C:\Program Files\AcmeAgent`
- logs:
  - `[auth] target path=C:\Program Files\AcmeAgent\data\wa_auth`
  - `[auth] PermissionError: [Errno 13] Permission denied`
  - app continues running but never persists the session
- code excerpt:

```python
session_dir = Path(sys.executable).resolve().parent / "data" / "wa_auth"
session_dir.mkdir(parents=True, exist_ok=True)
bridge_env["WA_AUTH_DIR"] = str(session_dir)
```

- reproduction:
  1. Install packaged app under Program Files
  2. Pair WhatsApp successfully
  3. Close and reopen app
  4. QR pairing is required again
