.PHONY: reproduce reproduce-final ablation report-assets report baseline experiments phase2 test

PYTHON ?= python3
PYTEST ?= $(PYTHON) -m pytest

reproduce:
	PYTHONPATH=src $(PYTHON) -m c2o_strategy.final_strategy --data-dir data --output-dir outputs --cutoff 2024-12-31 --development-cutoff 2024-12-31 --mode all
	PYTHONPATH=src $(PYTHON) tools/fill_brief_compliance_gaps.py
	PYTHONPATH=src $(PYTHON) tools/write_final_model_weights.py
	PYTHONPATH=src $(PYTHON) tools/lightgbm_diagnostic.py
	PYTHONPATH=src $(PYTHON) tools/model_family_robustness.py
	PYTHONPATH=src $(PYTHON) tools/build_corrected_report.py
	PYTHONPATH=src $(PYTHON) tools/render_report_with_machine_style.py

reproduce-final:
	PYTHONPATH=src $(PYTHON) -m c2o_strategy.final_strategy --data-dir data --output-dir outputs --cutoff 2024-12-31 --development-cutoff 2024-12-31 --mode final

ablation:
	PYTHONPATH=src $(PYTHON) -m c2o_strategy.final_strategy --data-dir data --output-dir outputs --cutoff 2024-12-31 --development-cutoff 2024-12-31 --mode ablation

report-assets:
	PYTHONPATH=src $(PYTHON) -m c2o_strategy.final_strategy --data-dir data --output-dir outputs --cutoff 2024-12-31 --development-cutoff 2024-12-31 --mode audits

report:
	PYTHONPATH=src $(PYTHON) tools/build_corrected_report.py
	PYTHONPATH=src $(PYTHON) tools/render_report_with_machine_style.py

baseline:
	PYTHONPATH=src $(PYTHON) -m c2o_strategy.run --data-dir data --output-dir outputs --cutoff 2024-12-31 --development-cutoff 2024-12-31

experiments:
	PYTHONPATH=src $(PYTHON) -m c2o_strategy.experiments --data-dir data --output-dir outputs --cutoff 2024-12-31 --development-cutoff 2024-12-31

phase2:
	PYTHONPATH=src $(PYTHON) -m c2o_strategy.phase2 --data-dir data --output-dir outputs --cutoff 2024-12-31 --development-cutoff 2024-12-31

test:
	@if [ ! -f outputs/performance_summary.csv ] || [ ! -f outputs/positions_250m.parquet ]; then \
		echo "Final outputs missing; running make reproduce before tests."; \
		$(MAKE) reproduce PYTHON=$(PYTHON); \
	fi
	$(PYTEST) -q
