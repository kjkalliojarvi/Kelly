# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

Kelly is a CLI tool for information-theoretic bet-size optimization (Kelly criterion) on
Finnish horse-race betting (Veikkaus toto pools). It fetches live odds/pool data from the
Veikkaus API, combines them with the user's own win-probability estimates, and computes
where positive-expectation bets exist and how large they should be. The domain vocabulary
and most identifiers are in Finnish.

## Commands

Dependencies are managed with **uv** (`pyproject.toml` + `uv.lock`). `uv run` and `uv sync`
create/refresh the `.venv` automatically — there is no manual venv/pip step.

```bash
uv sync                        # create/update .venv from pyproject.toml + uv.lock
make run-tests                 # uv run pytest tests
uv run pytest tests            # run tests directly
uv run pytest tests/test_kelly.py::TestMethods::test_get_prosentit   # single test
make lint                      # uv run flake8 Kelly
make coverage                  # coverage report + HTML
make dist                      # uv build → sdist + wheel
uv run kelly -h                # run the CLI
```

The CLI entry point is `kelly` (`[project.scripts]` in `pyproject.toml` → `Kelly.__main__:kelly`).

The project targets **Python 3.14+** (`requires-python = ">=3.14"`, `.python-version` = 3.14).

Dependencies use `>=` lower bounds in `pyproject.toml` (floors set to the versions last
validated together); `uv.lock` is committed and holds the exact resolved set for reproducible
installs. Refresh with `uv lock --upgrade` (or `uv lock --upgrade-package <name>`) and re-run
the suite. The stack runs on numpy 2.x / pandas 3.x.

The `p_2`/`p_3` unit test compares floats with `pytest.approx` (their pure-Python `sum()`
arithmetic differs by ~1 ULP across platforms/Python versions), so it is not tied to any
single interpreter.

## Runtime configuration (required to actually run)

`Kelly/__init__.py` calls `load_dotenv(find_dotenv(usecwd=True))` once at package import, so
`.env` (found by walking up from the current working directory) is loaded before any submodule
runs. Modules then read `os.environ['PELIT_FOLDER']` / `os.environ['PROSENTIT_FOLDER']` at
import time, so both must be set (via `.env` or the real environment) or imports fail with
`KeyError`. Real environment variables take precedence over `.env` (dotenv's default
`override=False`). The two folder paths:

- `PROSENTIT_FOLDER` — holds `prosentit.xlsx` (the user's probability estimates) and the
  per-track `<ratakoodi>_<YYMMDD>.json` probability files generated from it.
- `PELIT_FOLDER` — holds the game-config JSON files (`duo.json`, `troikka.json`, `t4.json`,
  `t5.json`, `t6.json`, `t7.json`, `t8.json`, `simulation.json`) and receives the generated
  `.peli` output files. These config files live **outside the repo** and define the betting
  system (which horses per leg, stake sizes, Kelly thresholds, ABCD split limits).

## Architecture

The `kelly` command dispatches argparse subcommands to functions (`Kelly/__main__.py`):

- **`tanaan`** → `veikkaus.tanaan` — lists today's races from the Veikkaus API.
- **`prosentit`** → `get_data.excel_prosentit` — reads `prosentit.xlsx` and writes the
  per-track probability JSON that every other command consumes.
- **`peli`** → `bet_calc.peli` — the core: compute Kelly bet sizes for one pool type.
- **`analyysi`** → `analyysi.analysoi` — reads back a generated `.peli` file and prints a
  cross-tab of how often each horse/leg appears.
- **`simu`** → `simulation.simulation` — Monte Carlo (numpy/pandas) over pool percentages to
  estimate hajotus (bet-spread) distributions.

Data flow for a bet calculation (`peli`):
1. `get_data.get_prosentit` loads the user's probability JSON (validated by
   `validoi.tarkista_prosentit`, which also cross-checks scratched horses against the live
   race card).
2. `veikkaus.hae_kertoimet` / `veikkaus.Tprosentit` fetch odds/pool XML from the Veikkaus API
   (`BASEURL` in `veikkaus.py`), parsed with BeautifulSoup (`xml` features → needs `lxml`).
   Multi-leg (T-pelit) responses are zipped.
3. The `Peli` dataclass hierarchy in `get_data.py` is the probability model. `Peli` defines
   `oma_kerroin` (the fair odds from own probabilities), `kelly` (Kelly fraction via
   `kelly_calc`), and `bet_size`. Subclasses override `oma_kerroin` for each pool type:
   `Voittaja` (win), `Sija` (place), `Kaksari` (exacta), `Troikka` (trifecta), `TPeli`
   (multi-leg). `p_1/p_2/p_3` derive place/show probabilities from raw win percentages using
   hard-coded empirical lookup tables.
4. `hajota.py` expands a betting system's ABCD categorisation into concrete combination rows
   (`hajotus_rivit`, `split_abcd`); `validoi.py` filters valid combinations.
5. `util.write_to_file` writes the `.peli` output and prints a summary (total stake, own
   probability, payout min/avg/max).

## Conventions

- Domain terms are Finnish: `ratakoodi` (track code), `lahto` (race/leg), `pelimuoto` (pool
  type), `kerroin` (odds), `prosentit` (percentages/probabilities), `vaihto` (turnover),
  `jako` (pool payout), `hajotus` (bet spread), `panos` (stake), `poissa` (scratched).
- Pool-type codes: `voi` win, `sij` place, `kak` exacta, `duo`, `tro`/`troikka` trifecta,
  and T-pool codes `t4 t5 t64 t65 t75 t86` (the number encodes legs, e.g. `t65` = 6 legs win
  / 5 legs consolation).
- `Kelly/__init__.py` `__version__` (`0.6.0`) matches `pyproject.toml`; `bumpversion` config
  in `setup.cfg` targets `pyproject.toml`.
- `setup.cfg` remains only for `flake8` config (plain flake8 does not read `pyproject.toml`)
  and `bumpversion`. The old cookiecutter scaffolding (`tox.ini`, `MANIFEST.in`, the `docs/`
  Sphinx tree, and the `README.rst`/`HISTORY.rst`/`CONTRIBUTING.rst` stubs) has been removed —
  `README.md` is the project readme and the workflow is `uv run` + the `Makefile` targets.
