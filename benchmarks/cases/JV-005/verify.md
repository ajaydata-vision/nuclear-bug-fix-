# Verification

## Before Fix
Under 20+ connections, messages arrive with missing bytes; no exception

## After Fix
1. Replace buf.clear() with buf.compact()
2. Add write loop: while(buf.hasRemaining()) { to.write(buf); }
3. Send 10000 messages under load — zero byte loss
4. Log buf.remaining() before clear: always 0 (compact ensures unread bytes preserved)

## Regression Checks
- Zero-length reads: handled correctly (read returns 0, buf unchanged)
- Full writes: compact() behaves identically to clear() when buffer fully drained
- High concurrency (100 connections): no corruption
