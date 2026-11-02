# RTL Verification Lab

![CI](https://github.com/walle-au/rtl-verification-lab/actions/workflows/ci.yml/badge.svg)

SystemVerilog RTL modules verified with **cocotb** (Python) and **Icarus Verilog**. Every push runs the full regression in **GitHub Actions**.

Each design has:
- a short **spec** in the header of its `.sv` file
- a **Python reference model** or **scoreboard**
- **directed** tests for corner cases and **constrained-random** tests that log which scenarios were reached

| Design | Description | Verification approach |
|---|---|---|
| [`alu`](rtl/alu.sv) | 8-bit ALU: ADD, SUB, AND, OR, XOR, SLL, SRL, SLT, plus carry and zero flags | Reference model. All corner values × all ops, then 4,000 random vectors with a hit count per op. |
| [`sync_fifo`](rtl/sync_fifo.sv) | Parameterized synchronous FIFO with full, empty and count | Scoreboard with a Python `deque`. Fill and drain, overflow and underflow protection, 3,000 cycles of random read/write traffic that must reach full and empty. |
| [`uart_tx`](rtl/uart_tx.sv) | UART transmitter, 8N1, configurable baud divider | A serial-line monitor decodes frames mid-bit. Checks known patterns, random bytes, and that each frame lasts 10 bit-times. |

## Run it

Requirements: Python 3.10+, Icarus Verilog 12+ (`sudo apt install iverilog`)

```bash
make setup        # virtualenv + cocotb + pytest
make test         # full regression
make test-fifo    # a single design
make waves-uart   # dump waveforms (FST), open with GTKWave or Surfer
```

## Project layout

```
rtl/                 SystemVerilog sources (one module per file)
tb/test_<name>.py    cocotb testbenches
tb/test_runner.py    builds each design and runs its tests (pytest)
.github/workflows/   CI: simulates every push
```

## Roadmap

- [ ] SystemVerilog Assertions (SVA) for FIFO and UART protocol properties
- [ ] Functional coverage with `cocotb-coverage`
- [ ] `uart_rx` + loopback test (TX → RX)
- [ ] Verilator as a second simulator in CI
- [ ] Synthesis on a Nexys 4 (Artix-7): resource and timing report
- [ ] Use these specs and testbenches as a benchmark for an LLM agent that writes RTL

## AI usage

This project was developed with the help of Claude Code (Anthropic), working under hooks that block commits and destructive commands. I reviewed every design and test, and I made all the commits.
