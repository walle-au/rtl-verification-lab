"""Synchronous FIFO testbench with a scoreboard (Python deque as reference model)."""

import random
from collections import deque

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ReadOnly, RisingEdge, Timer

DEPTH = 16
WIDTH = 8


async def reset(dut) -> None:
    dut.rst_n.value = 0
    dut.wr_en.value = 0
    dut.rd_en.value = 0
    dut.din.value = 0
    await Timer(25, unit="ns")
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)


async def start(dut) -> None:
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset(dut)


@cocotb.test()
async def test_reset_state(dut):
    """After reset the FIFO is empty and not full."""
    await start(dut)
    await ReadOnly()
    assert int(dut.empty.value) == 1
    assert int(dut.full.value) == 0
    assert int(dut.count.value) == 0


@cocotb.test()
async def test_fill_and_drain(dut):
    """Fill to full, check 'full' and that extra writes are ignored, then drain in order."""
    await start(dut)
    data = [random.randint(0, 2**WIDTH - 1) for _ in range(DEPTH)]

    for value in data:
        dut.wr_en.value = 1
        dut.din.value = value
        await RisingEdge(dut.clk)
    # One extra write while full: must be dropped
    dut.din.value = 0xAA
    await RisingEdge(dut.clk)
    dut.wr_en.value = 0

    await ReadOnly()
    assert int(dut.full.value) == 1
    assert int(dut.count.value) == DEPTH

    await RisingEdge(dut.clk)
    # Back-to-back reads: dout shows data[k] right after the k-th read edge
    dut.rd_en.value = 1
    for expected in data:
        await RisingEdge(dut.clk)
        await ReadOnly()
        assert int(dut.dout.value) == expected, (
            f"read 0x{int(dut.dout.value):02x}, expected 0x{expected:02x}"
        )
    await Timer(1, unit="ns")  # leave the read-only phase before driving
    dut.rd_en.value = 0

    await ReadOnly()
    assert int(dut.empty.value) == 1


@cocotb.test()
async def test_random_traffic(dut):
    """Random simultaneous reads and writes, checked against a reference queue."""
    await start(dut)
    random.seed(42)
    model: deque[int] = deque()
    pending_read = None  # value expected on dout after the previous read
    stats = {"writes": 0, "reads": 0, "full_hits": 0, "empty_hits": 0}

    for _ in range(3000):
        wr = random.random() < 0.55
        rd = random.random() < 0.45
        value = random.randint(0, 2**WIDTH - 1)

        dut.wr_en.value = int(wr)
        dut.rd_en.value = int(rd)
        dut.din.value = value

        # Sample the flags that the DUT sees at this clock edge
        await ReadOnly()
        full, empty = int(dut.full.value), int(dut.empty.value)
        assert full == int(len(model) == DEPTH), "full flag mismatch"
        assert empty == int(len(model) == 0), "empty flag mismatch"
        assert int(dut.count.value) == len(model), "count mismatch"
        stats["full_hits"] += full
        stats["empty_hits"] += empty

        await RisingEdge(dut.clk)

        # Update the model with what the DUT accepted on this edge
        if rd and not empty:
            pending_read = model.popleft()
            stats["reads"] += 1
        else:
            pending_read = None
        if wr and not full:
            model.append(value)
            stats["writes"] += 1

        await ReadOnly()
        if pending_read is not None:
            got = int(dut.dout.value)
            assert got == pending_read, f"dout 0x{got:02x} != 0x{pending_read:02x}"
        await Timer(1, unit="ns")

    dut._log.info("Traffic stats: %s", stats)
    assert stats["full_hits"] > 0 and stats["empty_hits"] > 0, (
        "random test never reached full and empty; adjust probabilities"
    )
