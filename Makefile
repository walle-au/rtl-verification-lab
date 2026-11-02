VENV := .venv
PY   := $(VENV)/bin/python

.PHONY: setup test test-% waves-% clean

setup:            ## Create the virtualenv and install cocotb + pytest
	python3 -m venv $(VENV)
	$(PY) -m pip install -r requirements.txt

test:             ## Run every testbench
	$(PY) -m pytest -v tb/test_runner.py

test-%:           ## Run one design, e.g. make test-fifo
	$(PY) -m pytest -v tb/test_runner.py -k $*

waves-%:          ## Run one design and dump waveforms (open with GTKWave/Surfer)
	WAVES=1 $(PY) -m pytest -v tb/test_runner.py -k $*

clean:
	rm -rf sim_build results.xml .pytest_cache tb/__pycache__
