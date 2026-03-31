# FR-002: Packaged App Exits Before UI On Some Windows PCs

## User Prompt

A customer can launch our packaged app on one machine, but on another Windows
PC it exits immediately before the UI appears.

We only have the packaged startup log and the exact error text. What is the
real bug?

## Context Provided To The Skill

- stack: Python 3.11.8 + PyQt6 6.7.0 + PyInstaller 6.6.0
- versions: packaged `.exe`, customer machine logs only
- environment: evidence-limited, no code excerpt
- logs:
  - attached `assets/startup-log.txt` is the only captured startup artifact
  - source run on developer machine works
- reproduction:
  1. Build packaged exe
  2. Launch on customer Windows machine
  3. App exits before UI appears
