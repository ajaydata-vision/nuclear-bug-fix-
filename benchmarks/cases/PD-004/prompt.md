# PD-004: Desktop App Hangs On Exit Because Cleanup Never Finishes

## User Prompt

Our PyQt6 desktop app opens fine, but when the user closes it the window
disappears and the process stays alive forever. The logs show the websocket
client and scheduler were still running during shutdown. Where is the real bug?

## Context Provided To The Skill

- stack: Python 3.11.8 + PyQt6 6.7.0 + qasync 0.27.1 + APScheduler 3.10.4
- versions: Windows 11 desktop app
- environment: source run from a virtual environment
- logs:
  - `[shutdown] close requested`
  - `[ws] websocket close requested`
  - `[scheduler] shutdown requested`
  - `[shutdown] pending tasks still alive after 10s`
- code excerpt:

```python
def closeEvent(self, event):
    self.status.setText("Shutting down...")
    self.websocket.close()
    self.scheduler.shutdown(wait=False)
    event.accept()
```

- reproduction:
  1. Open the app
  2. Let websocket reconnect and scheduler jobs start
  3. Close the window
  4. Process remains running
