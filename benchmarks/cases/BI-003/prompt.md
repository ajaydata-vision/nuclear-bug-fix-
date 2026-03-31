# BI-003: Searches Suddenly Return Empty Results

## User Prompt

Our social-monitoring desktop app uses `ntscraper` to read public tweets. Since
yesterday, normal keyword searches return an empty list, but the app does not
crash. We did not deploy a local parser or UI change. Is the bug in our app or
somewhere else?

## Context Provided To The Skill

- stack: Python 3.11.8 + ntscraper 0.3.13
- versions: Windows desktop app, source run
- environment: logs only, no code excerpt from the scraper internals
- logs:
  - `[scrape] query="openai" status=200 items=0`
  - `[scrape] response signature no longer matches the scraper's expected markers`
  - app code after scraper call only checks `len(results)`
  - attached `assets/raw-response-signature.txt` was captured from a failing query
- reproduction:
  1. Run keyword search that previously returned results
  2. Observe 200 response with zero parsed items
