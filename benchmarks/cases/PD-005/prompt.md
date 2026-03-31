# PD-005: SQLite Locks Appear When UI And Background Writes Overlap

## User Prompt

Our PyQt6 app uses SQLite for local message state. Most of the time it works,
but during a sync burst the app starts logging `database is locked` and one of
the UI updates never appears. The same database file is used for the main
screen and the background sync task. What is the real bug?

## Context Provided To The Skill

- stack: Python 3.11.8 + PyQt6 6.7.0 + qasync 0.27.1 + aiosqlite 0.19.0
- versions: Windows 11 desktop app
- environment: source run from a virtual environment
- logs:
  - `[db] sync transaction started`
  - `[db] ui save started before previous commit finished`
  - `[db] sqlite3.OperationalError: database is locked`
- code excerpt:

```python
class Store:
    def __init__(self, conn):
        self.conn = conn

    async def save_sync_batch(self, rows):
        await self.conn.execute("BEGIN")
        for row in rows:
            await self.conn.execute("INSERT INTO messages VALUES (?, ?)", row)
        await self.conn.commit()

    async def save_ui_change(self, row):
        await self.conn.execute("INSERT OR REPLACE INTO messages VALUES (?, ?)", row)
        await self.conn.commit()

async def open_store(path):
    conn = await aiosqlite.connect(path)
    return Store(conn)
```

- reproduction:
  1. Start a sync
  2. Edit a message in the UI before the sync finishes
  3. Observe lock errors or lost UI updates
