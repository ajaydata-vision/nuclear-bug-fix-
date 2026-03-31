# PD-002: qasync App Freezes During Mail Sync

## User Prompt

Our PyQt6 mail client uses qasync, but clicking "Sync Inbox" freezes the whole
window for 6-8 seconds. The spinner stops and the title bar says "Not
Responding". As soon as sync finishes, the UI wakes back up. Where is the real
bug?

## Context Provided To The Skill

- stack: Python 3.11.8 + PyQt6 6.7.0 + qasync 0.27.1 + imaplib
- versions: Windows 11 desktop app
- environment: source run from venv
- logs:
  - `[ui] sync clicked on thread=MainThread`
  - `[sync] starting mailbox refresh`
  - `[sync] mailbox refresh finished 7.4s later`
- code excerpt:

```python
@asyncSlot()
async def sync_inbox(self):
    self.status.setText("Syncing...")
    mailbox = imaplib.IMAP4_SSL(self.host)
    mailbox.login(self.username, self.password)
    status, data = mailbox.search(None, "UNSEEN")
    self.model.replace_rows(data[0].split())
    self.status.setText("Done")
```

- reproduction:
  1. Launch desktop app
  2. Click Sync Inbox
  3. Move the window or interact with controls during sync
