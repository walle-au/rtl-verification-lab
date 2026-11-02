"""ALU testbench: compares the RTL against a Python reference model."""

import random

import cocotb
from cocotb.triggers import Timer

WIDTH = 8
MASK = (1 << WIDTH) - 1
OPS = ["ADD", "SUB", "AND", "OR", "XOR", "SLL", "SRL", "SLT"]


def to_signed(x: int) -> int:
    return x - (1 << WIDTH) if x & (1 << (WIDTH - 1)) else x


def alu_model(a: int, b: int, op: int) -> tuple[int, int]:
    """Returns (result, carry) exactly as the spec in rtl/alu.sv."""
    sh = b & (WIDTH - 1)
    if op == 0:
        full = a + b
        return full & MASK, full >> WIDTH
    if op == 1:
        return (a - b) & MASK, int(a < b)  # carry = borrow
    if op == 2:
        return a & b, 0
    if op == 3:
        return a | b, 0
    if op == 4:
        return a ^ b, 0
    if op == 5:
        return (a << sh) & MASK, 0
    if op == 6:
        return a >> sh, 0
    return int(to_signed(a) < to_signed(b)), 0


async def apply_and_check(dut, a: int, b: int, op: int) -> None:
    dut.a.value = a
    dut.b.value = b
    dut.op.value = op
    await Timer(1, unit="ns")

    exp_res, exp_carry = alu_model(a, b, op)
    got_res = int(dut.result.value)
    got_carry = int(dut.carry.value)
    got_zero = int(dut.zero.value)

    msg = f"{OPS[op]} a=0x{a:02x} b=0x{b:02x}"
    assert got_res == exp_res, f"{msg}: result 0x{got_res:02x} != 0x{exp_res:02x}"
    assert got_carry == exp_carry, f"{msg}: carry {got_carry} != {exp_carry}"
    assert got_zero == int(exp_res == 0), f"{msg}: zero flag wrong"


@cocotb.test()
async def test_corner_cases(dut):
    """Edge values for every operation: 0, 1, max, sign boundary."""
    corners = [0x00, 0x01, 0x7F, 0x80, 0xFE, 0xFF]
    for op in range(len(OPS)):
        for a in corners:
            for b in corners:
                await apply_and_check(dut, a, b, op)


@cocotb.test()
async def test_random(dut):
    """Random stimulus, with a count per operation so we know each was exercised."""
    random.seed(1234)
    hits = {name: 0 for name in OPS}
    for _ in range(4000):
        a, b, op = random.randint(0, MASK), random.randint(0, MASK), random.randint(0, 7)
        await apply_and_check(dut, a, b, op)
        hits[OPS[op]] += 1

    dut._log.info("Operations exercised: %s", hits)
    assert all(n > 0 for n in hits.values()), "some operation was never tested"
