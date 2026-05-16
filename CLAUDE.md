# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

KSeF CLI is a command-line tool and Python package for interacting with KSeF 2.0 (Krajowy System e-Faktur) — Poland's national e-invoicing system. It wraps the `ksef2.0-python` SDK with a CLI interface, session management, structured logging, and support for both token and certificate-based authentication.

## Commands

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run all tests
python -m unittest discover tests

# Run a single test file
python -m unittest tests.test1

# Run a single test case
python -m unittest tests.test1.TestKSEFCli.test_wyslij_fakture

# Lint
ruff check .

# Run the CLI
python -m ksef_cli <action> <nip> <output_file> [params...]
```

## Architecture

### CLI Entry Flow

```
python -m ksef_cli → __main__.py → main.py:run_main(sys.argv)
    → looks up action in ACTIONS dict
    → instantiates KSEFCLI.from_os_env(nip)
    → calls method(output_path, **kwargs)
```

Every action writes a JSON file to `output_file` with at minimum `{"OK": true}` or `{"OK": false, "errmess": "..."}` plus action-specific fields.

### `@ksef_action` Decorator (`ksef_cli.py`)

The decorator wrapping every public method in `KSEFCLI` handles the full operation lifecycle:
1. Reads config via `CONF` and tokens via `get_token()`
2. Opens a KSeF session (KSEFSDK) unless `enable_session=False`
3. Calls the wrapped method
4. Catches `requests.HTTPError` and generic exceptions, writing error JSON
5. Logs a `E` event record to CSV
6. Terminates the session

Adding a new action means: write a method decorated with `@ksef_action`, register it in `main.py`'s `ACTIONS` dict.

### Configuration (`ksef_conf.py`)

- `CONF` reads `KSEFCONF` (path to YAML file) and `KSEFDIR` (working directory) from env vars.
- `NIP` class parses `NIP$SUBDIR` syntax — e.g. `7497725064$ROK2025` splits into nip and subdirectory used under `KSEFDIR/`.
- Directory layout: `KSEFDIR/{NIP}/{KSEF_NUMBER}/` for invoices, `KSEFDIR-zakupowe/{NIP}/` for purchase invoice buffer.

### Authentication (`ksef_tokens.py`)

Reads the YAML config at `KSEFCONF`. Two supported schemes:

**Token-based:**
```yaml
tokens:
  NIP7497725064:
    token: "20251116-EC-..."
    env: test  # prod | demo | test
```

**Certificate-based:**
```yaml
tokens:
  NIP7497725064:
    p12: /path/to/cert.p12
    password: secret
    env: prod
```

Environments map to KSeF endpoints: `prod` → production, `demo` → PREKSEF, `test` → DEVKSEF.

### Logging (`ksef_log.py`)

- `LOGGER` base class sets up file logging to `KSEFDIR/ksef.log` and `KSEFDIR/{NIP}/ksef.log`.
- `E` records operation events to `KSEFDIR/events.csv` and per-NIP CSVs with timing, status, and error info.
- `KSEFCLI` inherits from both `LOGGER` and `KSEF_ZAKUPOWE_HELPER`.

### Purchase Invoice Buffer (`ksef_zakupowe.py`)

Implements incremental sync: tracks the last fetched KSeF sequence number in `KSEFDIR-zakupowe/{NIP}/lastread.json`, stores each invoice as `{KSEF_NUMBER}/faktura.xml` + `{KSEF_NUMBER}/metadata.json`. The `uaktualnij_zakupowe_bufor` action fetches only new invoices since the last run.

### Test Structure

Tests use `unittest` and require a live KSeF test environment. The abstract class `AbstractTestKSEFCLI` in `test1.py` defines 30+ test scenarios; `TestKSEFCli` and `TestKSEFCliCert` extend it for token and certificate auth respectively. `TestKSEFCliMain` tests the full CLI path via `run_main()`. Test configs live in `tests/conf/` and sample XML invoices in `tests/testdata/`.
