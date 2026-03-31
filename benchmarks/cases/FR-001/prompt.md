# FR-001: Packaged Build Misses A Dynamic Import

## User Prompt

Our app runs fine from source, but the packaged `.exe` crashes only when users
open the Google account settings page. The traceback says
`ModuleNotFoundError: No module named 'google.auth.transport.requests'`. Why
does this happen only in the packaged build?

## Context Provided To The Skill

- stack: Python 3.11.8 + PyInstaller 6.6.0 + google-auth 2.30.0
- versions: Windows 11, onefile build
- environment: packaged `.exe` only
- logs:
  - source run succeeds
  - packaged traceback occurs only when OAuth settings view is opened
- code excerpt:

```python
def build_google_session():
    from google.oauth2.credentials import Credentials
    creds = Credentials.from_authorized_user_file("google.json")
    return AuthorizedSession(creds)
```

- reproduction:
  1. Launch packaged exe
  2. Open Google account settings
  3. Import error appears
