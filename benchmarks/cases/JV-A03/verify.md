# Verification

## Before Fix

1. Run server, connect client, request report.pdf
2. Client receives 0 bytes
3. Log: "Write returned: 0 bytes written"

## After Fix

1. Add buffer.flip() before client.write(buffer)
2. Run same scenario
3. Client receives 48291 bytes (full file)
4. Log: "Write returned: 48291 bytes written"

## Regression Checks

- Small file (< 1KB): received correctly
- Large file (> 64KB): requires while(buffer.hasRemaining()) loop — note as follow-up
- Empty file (0 bytes): write returns 0, connection closes cleanly
- Add log: buffer.position()={} limit={} remaining={} before write — confirm remaining=48291
