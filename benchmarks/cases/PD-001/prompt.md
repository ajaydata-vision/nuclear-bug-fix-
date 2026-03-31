# PD-001: PyQt Send Action Does Nothing

## User Prompt

In our PyQt6 app, clicking "Send Reply" leaves the composer unchanged. No mail
is sent, and some shutdowns emit a generic `RuntimeWarning: coroutine was never
awaited`. The button click definitely fires. What is the real bug?

## Context Provided To The Skill

- stack: Python 3.11.8 + PyQt6 6.7.0 + qasync 0.27.1
- versions: Windows 11 desktop app
- environment: source run from venv
- logs:
  - button click signal fires
  - no status change after click
  - no log from inside the send path
  - shutdown warning references an un-awaited coroutine
- code excerpt:

```python
class Composer(QWidget):
    def bind_actions(self):
        self.send_button.clicked.connect(self.send_reply)

    async def send_reply(self):
        self.status.setText("Sending...")
        await self.mailer.send_current_draft()
        self.status.setText("Sent")
```

- reproduction:
  1. Open composer
  2. Click Send Reply
  3. Nothing happens
  4. Close app and inspect warning
