# PD-003: Background Worker Mutates Widgets From The Wrong Thread

## User Prompt

Our desktop app fetches search results in a background thread. Sometimes it
crashes with a Qt thread-affinity error, and other times the label updates are
just flaky. It only happens after the worker finishes. What is actually wrong?

## Context Provided To The Skill

- stack: Python 3.11.8 + PyQt6 6.7.0
- versions: Windows 11 desktop app
- environment: source run from venv
- logs:
  - `QObject::setParent: Cannot set parent, new parent is in a different thread`
  - worker completion log appears right before the error
- code excerpt:

```python
class SearchPanel(QWidget):
    def run_search(self, term: str) -> None:
        worker = threading.Thread(target=self._fetch_results, args=(term,), daemon=True)
        worker.start()

    def _fetch_results(self, term: str) -> None:
        rows = self.backend.search(term)
        self.status_label.setText(f"{len(rows)} results")
        self.results_table.setRowCount(len(rows))
```

- reproduction:
  1. Open search
  2. Run several searches quickly
  3. Observe intermittent crash or label corruption when worker finishes
