"""UART TX testbench: a monitor decodes the serial line and checks each byte."""

import random

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge, RisingEdge, Timer
from cocotb.utils import get_sim_time

CLKS_PER_BIT = 16  # small value keeps simulation fast; set by the runner
CLK_NS = 10


async def reset(dut) -> None:
    dut.rst_n.value = 0
    dut.tx_start.value = 0
    dut.tx_data.value = 0
    await Timer(25, unit="ns")
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)


async def wait_clocks(dut, n: int) -> None:
    for _ in range(n):
        await RisingEdge(dut.clk)


async def uart_monitor(dut) -> int:
    """Waits for a start bit and returns the decoded byte (samples mid-bit)."""
    await FallingEdge(dut.tx)
    await wait_clocks(dut, CLKS_PER_BIT // 2)
    assert int(dut.tx.value) == 0, "start bit not low at its center"

    byte = 0
    for i in range(8):
        await wait_clocks(dut, CLKS_PER_BIT)
        byte |= int(dut.tx.value) << i

    await wait_clocks(dut, CLKS_PER_BIT)
    assert int(dut.tx.value) == 1, "stop bit not high"
    return byte


async def send_byte(dut, value: int) -> None:
    while int(dut.busy.value):
        await RisingEdge(dut.clk)
    dut.tx_data.value = value
    dut.tx_start.value = 1
    await RisingEdge(dut.clk)
    dut.tx_start.value = 0


@cocotb.test()
async def test_idle_line(dut):
    """After reset the line is high and the transmitter is not busy."""
    cocotb.start_soon(Clock(dut.clk, CLK_NS, unit="ns").start())
    await reset(dut)
    await wait_clocks(dut, 5)
    assert int(dut.tx.value) == 1
    assert int(dut.busy.value) == 0


@cocotb.test()
async def test_known_bytes(dut):
    """Bytes that exercise all-zeros, all-ones and alternating patterns."""
    cocotb.start_soon(Clock(dut.clk, CLK_NS, unit="ns").start())
    await reset(dut)
    for value in [0x00, 0xFF, 0x55, 0xAA, 0x01, 0x80]:
        monitor = cocotb.start_soon(uart_monitor(dut))
        await send_byte(dut, value)
        got = await monitor
        assert got == value, f"sent 0x{value:02x}, line carried 0x{got:02x}"


@cocotb.test()
async def test_random_bytes_and_timing(dut):
    """Random bytes back to back; also checks the frame lasts 10 bit-times."""
    cocotb.start_soon(Clock(dut.clk, CLK_NS, unit="ns").start())
    await reset(dut)
    random.seed(7)
    for _ in range(20):
        value = random.randint(0, 255)
        monitor = cocotb.start_soon(uart_monitor(dut))
        await send_byte(dut, value)
        start_ns = get_sim_time(unit="ns")
        got = await monitor
        assert got == value, f"sent 0x{value:02x}, line carried 0x{got:02x}"

        while int(dut.busy.value):
            await RisingEdge(dut.clk)
        frame_clks = (get_sim_time(unit="ns") - start_ns) / CLK_NS
        expected = 10 * CLKS_PER_BIT
        assert abs(frame_clks - expected) <= 2, (
            f"frame took {frame_clks:.0f} clocks, expected ~{expected}"
        )
