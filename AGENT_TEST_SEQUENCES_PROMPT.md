# Agent Prompt: QA Test Sequences Feature

Copy this prompt when launching the `test-sequences` agent:

---

You're working on the **QA Test Sequences** feature for the Device Panel project.

## First Steps (Do these now):

1. **Check out your branch:**
   ```bash
   git checkout feature/test-sequences
   git pull origin feature/test-sequences
   ```

2. **Read these files in order:**
   - `AGENT_QUICK_START.md` - Quick start guide (read this first!)
   - `QA_Test_Sequences_Design.md` - **CRITICAL: Complete design document**
   - `BRANCH_TEST_SEQUENCES.md` - Your feature's plan and requirements
   - `DECISION_LOG.md` - Understand why decisions were made
   - `PROJECT_OVERVIEW.md` - See all branches and current status
   - `AGENT_SHARED_CONTEXT.md` - Check current coordination status

3. **Understand your feature:**
   - You're building a **QA test execution layer** for embedded MCUs
   - **Key Principle**: Pi orchestrates tests, MCU executes simple primitives
   - MCU-agnostic design (works with any MCU via UART)
   - MCU runs minimal QA Agent with 10 task slots (TASK 1-10)
   - Sleep control via UART, wake via GPIO
   - See `QA_Test_Sequences_Design.md` for complete design rationale

## Your Assignment:

- **Branch**: `feature/test-sequences`
- **Design Document**: `QA_Test_Sequences_Design.md` - **READ THIS FIRST**
- **RPi for Testing**: (Not assigned yet - will be assigned when hardware needed)

## Core Architecture:

### Separation of Responsibilities

**Raspberry Pi (Device Panel)**:
- Owns test orchestration
- Defines test sequences
- Controls timing, repetition, and pass/fail
- Provides UI, logs, and reporting

**MCU (DUT)**:
- Runs lightweight QA Agent
- Exposes stable UART command interface
- Executes simple actions when commanded (TASK 1-10)
- Enters sleep modes on request
- Does NOT interpret test scripts

> **Key Rule**: The MCU executes primitives. The Pi decides *what*, *when*, and *why*.

## Development Rules:

- ✅ Use feature flag: `ENABLE_TEST_SEQUENCES` in `config/feature_flags.py`
- ✅ Put code in `features/test_sequences/` directory
- ✅ Wrap all feature code in try/except blocks
- ✅ Don't modify protected files (see `PROTECTED_FILES.md`)
- ✅ Test on Ubuntu first, then deploy to RPi when hardware needed
- ✅ Update `AGENT_SHARED_CONTEXT.md` with your status
- ✅ **MCU-Agnostic**: Don't require MCU selection in UI
- ✅ **Task Numbers**: Use TASK 1-10, not named tasks (keeps protocol simple)

## Key Components to Build:

1. **DUT Profile Manager**
   - Configure UART port and baud rate
   - Configure GPIO for WAKE and RESET
   - Document what each task (TASK 1-10) does
   - Save/load DUT profiles

2. **UART Manager**
   - Communicate with MCU QA Agent
   - Send commands: `TASK N`, `SLEEP <mode>`, `WAKE`, `RESET`
   - Receive responses: `OK` or `ERR <reason>`
   - Handle timeouts and errors

3. **Sequence Builder**
   - Define sequences with steps:
     - Wake DUT (via GPIO)
     - Trigger Task N (via UART)
     - Enter sleep mode (via UART)
     - Wait (ms/seconds/minutes)
     - Loop/repeat
     - Pass/fail conditions
   - Save/load sequences (JSON/YAML)

4. **Sequence Executor**
   - Execute sequences one command at a time
   - Wait for OK/ERR responses
   - Log wake, sleep, and reset events
   - Handle failures (stop or flag)
   - Collect timing data

5. **Results & Reporting**
   - Pass/Fail outcomes
   - Failure reasons
   - Timing data
   - Execution logs
   - Exportable QA records

6. **UI Components**
   - DUT Profile Setup interface
   - Sequence Builder interface
   - Execution & Monitoring interface
   - Results display

## UART Protocol (MCU Side - You Don't Implement This)

The MCU QA Agent must support (users provide this):
- `TASK N` - Execute task N (1-10)
- `SLEEP <mode>` - Enter sleep mode (ACTIVE, LIGHT, DEEP, SHUTDOWN)
- `WAKE` - Wake from sleep (via GPIO, but acknowledge via UART)
- `RESET` - Reset MCU (via GPIO)
- Responses: `OK` or `ERR <reason>`

**You implement the Pi side that sends these commands and parses responses.**

## Testing Workflow:

1. **Ubuntu Testing** (this machine):
   - Unit tests with mock UART
   - UI tests
   - Sequence builder tests
   - Run: `pytest tests/`
   - Test app: `python device_panel.py`

2. **RPi Testing** (when hardware needed):
   - Test with real MCU running QA Agent
   - Test UART communication
   - Test GPIO wake/reset
   - Test full sequences

## Non-Goals (Explicitly Out of Scope):

This feature does **NOT**:
- Generate CubeMX `.ioc` files
- Flash firmware
- Inspect LCD pixels or SPI traffic
- Replace power instruments
- Parse scripts on MCU

## Success Criteria:

- DUT profiles can be configured
- Sequences can be defined and saved
- Sequences execute correctly via UART
- Task execution (TASK 1-10) works
- Sleep control works (all modes)
- Wake via GPIO works
- Timing is accurate
- Error handling works (OK/ERR responses)
- Results are logged correctly
- QA records are exportable
- All tests pass
- App works with feature disabled
- App works with feature enabled
- Works with any MCU (MCU-agnostic)

## Communication:

- Update `AGENT_SHARED_CONTEXT.md` when your status changes
- Reference other branches in commit messages if needed
- See `AGENT_COMMUNICATION.md` for coordination methods

## Start Here:

1. **Read `QA_Test_Sequences_Design.md` completely** - This is your design bible
2. Read `AGENT_QUICK_START.md` and `BRANCH_TEST_SEQUENCES.md`
3. Start implementing the QA Test Sequences feature
4. Focus on MCU-agnostic design and separation of concerns

Good luck! 🚀


