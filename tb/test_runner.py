"""Builds each RTL module with Icarus Verilog and runs its cocotb tests.

Run everything:   pytest -v tb/test_runner.py
Run one module:   pytest -v tb/test_runner.py -k fifo
Waveforms (FST):  WAVES=1 pytest tb/test_runner.py -k uart
"""

import os
from pathlib import Path

import pytest
from cocotb_tools.runner import get_runner

ROOT = Path(__file__).resolve().parent.parent
RTL = ROOT / "rtl"
SIM = os.getenv("SIM", "icarus")
WAVES = os.getenv("WAVES", "0") == "1"

# toplevel, cocotb test module, parameters
DESIGNS = [
    ("alu", "test_alu", {"WIDTH": 8}),
    ("sync_fifo", "test_sync_fifo", {"WIDTH": 8, "DEPTH": 16}),
    ("uart_tx", "test_uart_tx", {"CLKS_PER_BIT": 16}),
]


@pytest.mark.parametrize("toplevel,test_module,params", DESIGNS, ids=[d[0] for d in DESIGNS])
def test_design(toplevel, test_module, params):
    runner = get_runner(SIM)
    build_dir = ROOT / "sim_build" / toplevel

    runner.build(
        sources=[RTL / f"{toplevel}.sv"],
        hdl_toplevel=toplevel,
        parameters=params,
        build_args=["-g2012"] if SIM == "icarus" else [],
        build_dir=build_dir,
        timescale=("1ns", "1ps"),
        waves=WAVES,
        always=True,
    )
    runner.test(
        hdl_toplevel=toplevel,
        test_module=test_module,
        test_dir=Path(__file__).parent,
        build_dir=build_dir,
        waves=WAVES,
    )
