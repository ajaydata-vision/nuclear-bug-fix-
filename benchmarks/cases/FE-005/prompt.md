# FE-005: Modal Hidden By Stacking Context Despite High z-index

## User Prompt

Our modal has z-index 9999 but still renders behind the sidebar which only has z-index 1. Raising z-index further does not help. What is actually wrong?

## Context Provided To The Skill

- stack: React 18.2, CSS Modules
- environment: browser
- logs:
- modal has z-index: 9999
  - modal still renders behind a sidebar element
  - sidebar has z-index: 1
- code excerpt:
```css
.modal { z-index: 9999; position: fixed; }
.sidebar { z-index: 1; position: relative; transform: translateZ(0); }
```
- reproduction:
1. Open the modal
2. Observe it renders behind the sidebar
3. Inspect: modal z-index is 9999, sidebar z-index is 1
