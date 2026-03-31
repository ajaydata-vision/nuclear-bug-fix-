# Verification

## Before Fix
Processing 500 images → SIGSEGV in libimageprocessor.so → JVM crash

## After Fix
1. Check libimageprocessor.so changelog for v2.1.4 vs latest
2. Update to latest version (e.g. v2.2.1 if it fixes process_batch memory issue)
3. Process 1000 images — no crash
4. Alternatively: process in batches of 100 to stay under native memory threshold

## Regression Checks
- Run valgrind --leak-check=full on the native library test harness to confirm memory issue is fixed
- Process 2000 images in production — hs_err file no longer generated
- If library vendor has no fix: implement process isolation (subprocess per batch) to contain crashes
