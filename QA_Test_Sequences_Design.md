# QA Test Sequences – Design & Planning Notes

## Feature Name (Keep Consistent)
This feature is named **`test-sequences`**, matching the existing repository structure:

```
features/
└── test_sequences/
```

This document describes the **QA Test Sequences feature**, not the power profiler.  
Power measurement may integrate later, but **QA orchestration is independent**.

---

## Purpose of the QA Test Sequences Feature

The **QA Test Sequences** feature provides a **device-agnostic test execution layer** that allows users to:

- Run repeatable QA tests on embedded devices
- Simulate real device behavior over time (wake, act, sleep, repeat)
- Trigger DUT actions via UART and GPIO
- Validate correctness, timing, and reliability
- Produce deterministic PASS / FAIL outcomes

This feature is **not**:
- a firmware debugger
- a power measurement instrument
- a replacement for vendor IDEs (CubeMX, etc.)

It is a **QA test executive**.

---

## Core Architectural Principle

### Separation of Responsibilities

**Raspberry Pi (Device Panel)**
- Owns test orchestration
- Defines test sequences
- Controls timing, repetition, and pass/fail
- Provides UI, logs, and reporting

**MCU (DUT)**
- Runs a lightweight **QA Agent**
- Exposes a stable UART command interface
- Executes simple actions when commanded
- Enters sleep modes on request
- Does *not* interpret test scripts

> The MCU executes primitives.  
> The Pi decides *what*, *when*, and *why*.

---

## MCU-Agnostic by Design

The QA Test Sequences feature is **MCU-agnostic**.

- The user does **not** select an MCU in the Device Panel UI
- The Pi communicates only through a standardized UART protocol
- MCU-specific setup happens outside the app

### MCU-Specific Handling
- Users download a **QA Agent firmware template**
- Templates are provided per MCU family (e.g., STM32U5)
- Users integrate the template into their own project (CubeMX, etc.)
- Flashing is handled separately

This keeps the system extensible and future-proof.

---

## QA Agent (MCU Side)

### Sleep Control
The MCU can be commanded via UART to enter:

- **Active (RUN)**
- **Light Sleep**
- **Deep Sleep (STOP)**
- **Shutdown (STANDBY)**

- Sleep is always commanded via UART
- Wake is performed via GPIO (recommended)

---

### Task Execution Model

The MCU exposes **10 generic task slots**:

```
TASK 1
TASK 2
...
TASK 10
```

Each task:
- Is implemented by the user in firmware
- Performs a single deterministic action
- Returns OK or ERR

Example task uses:
- LCD on/off
- Display bitmap
- Pump pulse
- GPIO toggle
- Internal routines

#### Design Rule
Tasks are **numeric**, not semantic, at the protocol level.

The Pi UI may label tasks for clarity, but the MCU only executes `TASK N`.

---

## Should Tasks Have Names?

**No, not at the protocol level.**

Reasons:
- Named tasks tightly couple firmware and test scripts
- Harder to maintain compatibility
- Breaks MCU-agnostic design

Correct approach:
- Protocol uses `TASK 1..10`
- Meaning is documented per DUT in the UI
- MCU remains simple and stable

---

## UI Flow – QA Test Sequences

### 1. DUT Profile Setup
User configures:
- UART port
- Baud rate (fixed default in v1)
- GPIO for WAKE
- Optional GPIO for RESET
- Documentation for what each task does

No MCU model selection is required.

---

### 2. Sequence Builder
Users define sequences using high-level actions:

- Trigger Task N
- Send UART command
- Enter sleep mode
- Wait (ms / seconds / minutes)
- Loop / repeat
- Pass/fail conditions

Example conceptual flow:
```
Wake DUT
TASK 1   # LCD_INIT
Wait 200 ms
TASK 2   # LCD_ON
Wait 2 s
TASK 3   # LCD_BITMAP 1
Wait 5 s
TASK 4   # LCD_OFF
Sleep Deep for 10 minutes
Repeat 100 times
```

---

### 3. Execution & Monitoring
- One command at a time
- Each command requires OK / ERR
- Wake, sleep, and reset events logged
- Failures stop or flag the sequence

---

### 4. Results
Results include:
- Pass / Fail
- Failure reason
- Timing data
- Execution logs
- Exportable QA records

---

## Why This Design

- Keeps MCU firmware simple
- Avoids script parsing on MCU
- Allows rapid iteration on Pi
- Supports many DUTs with one framework
- Scales from lab QA to manufacturing

---

## Non-Goals

This feature does **not**:
- Generate CubeMX `.ioc` files
- Flash firmware
- Inspect LCD pixels or SPI traffic
- Replace power instruments

These are explicitly out of scope.

---

## Summary

The **QA Test Sequences** feature is a device-agnostic QA execution system where the Raspberry Pi orchestrates deterministic test flows via UART and GPIO, while the MCU runs a minimal QA Agent that executes numbered tasks and enters defined sleep modes. Intelligence lives on the Pi, firmware remains simple, and QA becomes repeatable, operator-friendly, and scalable.
