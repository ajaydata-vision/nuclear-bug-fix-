# Evaluator

## Metadata

- id: JT-001
- domain: java-enterprise
- track: deploy-env
- difficulty: hard
- determinism: intermittent
- one_shot_eligible: false
- requires_external_intelligence: true
- requires_runtime_access: false
- requires_log_access: true
- tags: jvm-crash, hs_err, sigsegv, jni, native, crash-analysis

## Ground Truth

- root_cause: The JVM crashed due to a SIGSEGV (segmentation fault) in native code — specifically inside libimageprocessor.so at process_batch(). This is a native library bug (memory access violation in the JNI library), not a Java application bug. The JVM cannot catch or handle native code crashes — the process exits immediately.
- why_it_happens: SIGSEGV in native code means the native library accessed invalid memory (null pointer, buffer overread, use-after-free, stack overflow in native frame). JNI libraries that have bugs can crash the entire JVM process because native code runs outside the JVM's memory safety guarantees.
- accepted_fix: Check if libimageprocessor.so v2.1.4 has a known bug in process_batch(). Search vendor issue tracker and release notes. Update to the latest version of the library. As a workaround, process images in smaller batches to stay within whatever memory limit triggers the bug.
- rejected_fix_patterns:
  - increase JVM heap size (crash is in native memory, not JVM heap)
  - add try/catch around image processing calls (cannot catch SIGSEGV — JVM is dead)
  - enable -XX:+HeapDumpOnOutOfMemoryError (OOM handler never fires for SIGSEGV)

## Evidence Signals

- strongest_signal: hs_err "Problematic frame: C [libimageprocessor.so]" — crash in native (C) code, not Java; SIGSEGV = memory access violation in native code; occurs after processing many images (suggesting memory accumulation in native heap)
- strongest_alternative_explanation: JVM bug in OpenJDK 17.0.9 causing crash
- why_alternative_is_wrong: The crash frame is in libimageprocessor.so, not in the JVM itself. JVM bugs show "V [libjvm.so]" in the problematic frame. "C [libimageprocessor.so]" definitively places the crash in the third-party native library.

## Scoring Notes

- full_credit_conditions:
  - reads the hs_err "Problematic frame: C [libimageprocessor.so]" correctly
  - identifies native library bug (not JVM, not Java application)
  - proposes checking library release notes and updating libimageprocessor.so
- partial_credit_conditions:
  - identifies crash in native code but suggests JVM flag tuning
- fail_conditions:
  - blames Java heap overflow
  - recommends adding OutOfMemoryError handler
