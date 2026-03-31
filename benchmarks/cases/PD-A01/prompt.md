# PD-A01: qasync Loop Ownership Split Across Two Event Loops

## User Prompt

Our PyQt6 desktop app opens and the login restore task starts, but the UI keeps
showing "Restoring session..." forever. No exception is shown. Manual login
works, but anything scheduled during startup never finishes. What is actually
wrong?

## Context Provided To The Skill

- stack: Python 3.11.8 + PyQt6 6.7.0 + qasync 0.27.1 + httpx 0.27.0
- versions: Windows 11, source run from venv
- environment: desktop app, startup path only
- logs:
  - `[startup] created bootstrap task on loop=0x2a4be6a2c40`
  - `[ui] MainWindow shown`
  - no later `restore_session completed` log ever appears
- code excerpt:

```python
app = QApplication(sys.argv)
qt_loop = qasync.QEventLoop(app)
asyncio.set_event_loop(asyncio.new_event_loop())

window = MainWindow()
window.show()

async def bootstrap():
    await window.restore_session()

asyncio.get_event_loop().create_task(bootstrap())

with qt_loop:
    qt_loop.run_forever()
```

- reproduction:
  1. Launch the app with a stored session
  2. Observe startup spinner
  3. Spinner never completes until app is closed
