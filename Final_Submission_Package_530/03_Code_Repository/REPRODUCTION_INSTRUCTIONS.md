# Reproduction Instructions

Git URL:

```text
https://github.com/Czzzzzzzzy/Machine-Learning-For-Finance.git
```

Raw coursework data is not included in this package. Place the course-provided
files listed in `data/README.md` into `data/` before running the commands.

Single-command reproduction:

```bash
PYTHON=/opt/anaconda3/bin/python3 make reproduce
```

Test command:

```bash
PYTHON=/opt/anaconda3/bin/python3 make test
```

`make test` checks whether generated final outputs exist. In a clean checkout it
will run `make reproduce` first, so the course-provided data files must already
be present in `data/`.

Latest local test result after reproduction: `13 passed`.

Development cutoff: `2024-12-31`. The 2025-2026 marker window is not used in development.

Optional notebook walkthrough:

```text
notebooks/c2o_reproduction_walkthrough.ipynb
```

The notebook links the modules, reproduction command, output checks, report PDF,
and QuantStats HTML in one place. It is a guide; `make reproduce` remains the
official single-command reproduction target.
