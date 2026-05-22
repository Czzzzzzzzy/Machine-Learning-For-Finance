.PHONY: reproduce reproduce-final ablation report-assets baseline experiments phase2 test

PYTHON ?= python3
PYTEST ?= $(PYTHON) -m pytest

reproduce:
	PYTHONPATH=src $(PYTHON) -m c2o_strategy.final_strategy --data-dir data --output-dir outputs --cutoff 2024-12-31 --development-cutoff 2024-12-31 --mode all

reproduce-final:
	PYTHONPATH=src $(PYTHON) -m c2o_strategy.final_strategy --data-dir data --output-dir outputs --cutoff 2024-12-31 --development-cutoff 2024-12-31 --mode final

ablation:
	PYTHONPATH=src $(PYTHON) -m c2o_strategy.final_strategy --data-dir data --output-dir outputs --cutoff 2024-12-31 --development-cutoff 2024-12-31 --mode ablation

report-assets:
	PYTHONPATH=src $(PYTHON) -m c2o_strategy.final_strategy --data-dir data --output-dir outputs --cutoff 2024-12-31 --development-cutoff 2024-12-31 --mode audits

baseline:
	PYTHONPATH=src $(PYTHON) -m c2o_strategy.run --data-dir data --output-dir outputs --cutoff 2024-12-31 --development-cutoff 2024-12-31

experiments:
	PYTHONPATH=src $(PYTHON) -m c2o_strategy.experiments --data-dir data --output-dir outputs --cutoff 2024-12-31 --development-cutoff 2024-12-31

phase2:
	PYTHONPATH=src $(PYTHON) -m c2o_strategy.phase2 --data-dir data --output-dir outputs --cutoff 2024-12-31 --development-cutoff 2024-12-31

test:
	$(PYTEST) -q
