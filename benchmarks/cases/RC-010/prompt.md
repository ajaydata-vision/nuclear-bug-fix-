# RC-010: Concurrent Writes To Same Log File Causing Interleaved Corrupt Entries

## User Prompt

Our event log file contains corrupted JSON entries that are half from one write and half from another. This only happens with multiple workers. What is the bug?

## Context Provided To The Skill

- stack: Python 3.11, multiprocessing, concurrent file writes
- environment: production with multiple worker processes
- logs:
- log file contains interleaved JSON lines
  - some JSON entries are corrupt (half from one write, half from another)
  - only occurs with more than one worker process
  - single process writes are correct
- code excerpt:
```python
def log_event(event):
    with open('events.log', 'a') as f:
        f.write(json.dumps(event) + '\n')  # not atomic under multiprocessing
```
- reproduction:
1. Run with 4 worker processes
2. Workers write events concurrently
3. Inspect log file: JSON entries are interleaved and corrupt
