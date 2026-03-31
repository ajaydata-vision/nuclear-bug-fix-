# JT-001: JVM Exits Suddenly — SIGSEGV in Native Library

## User Prompt

Our Java 17 application exits unexpectedly with no Java exception and no log output. It leaves a file named hs_err_pid12345.log in the working directory. The exit is instant — no graceful shutdown. What happened and how do we diagnose it?

## Context Provided To The Skill

- stack: Java 17.0.9, Linux x86_64, application uses a native image processing library via JNI (libimageprocessor.so v2.1.4)
- environment: production, occurs after processing large image batches
- logs: none — process exits before any Java logging
- hs_err excerpt (provided):
```
# A fatal error has been detected by the Java Runtime Environment:
#  SIGSEGV (0xb) at pc=0x00007f8a1c234892, pid=12345, tid=0x00007f8a1c000700
#
# JRE version: OpenJDK Runtime Environment (17.0.9+9) (build 17.0.9+9)
# Java VM: OpenJDK 64-Bit Server VM (17.0.9+9, mixed mode, sharing, tiered, compressed oops)
#
# Problematic frame:
# C  [libimageprocessor.so+0x34892]  process_batch+0x92
#
# Core dump will be written.
```
- reproduction:
  1. Process batch of 500+ images
  2. JVM exits with SIGSEGV after ~200 images
  3. hs_err file appears in working directory
