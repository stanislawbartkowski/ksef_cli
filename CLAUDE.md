# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

KSeF CLI is a command-line tool and Python package for interacting with KSeF 2.0 (Krajowy System e-Faktur) — Poland's national e-invoicing system. It wraps the `ksef2.0-python` SDK with a CLI interface, session management, structured logging, and support for both token and certificate-based authentication.

## Commands

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# Run a single test file
pytest tests/test1.py

# Run a single test case
pytest tests/test1.py::TestKSEFCombined::test_wyslij_fakture_sprzedazy

# Run a parametrized variant
pytest tests/test1.py::TestKSEFCombined::test_wyslij_fakture_sprzedazy[token]

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

The decorator wrapping most public methods in `KSEFCLI` handles the full operation lifecycle:
1. Reads config via `CONF` and credentials via `load_credentials()` (returns a `Credentials` object exposing `.get_token()` or `.get_cert()`)
2. Opens a KSeF session (KSEFSDK) unless `enable_session=False`
3. Calls the wrapped method
4. Catches `requests.HTTPError` and generic exceptions, writing error JSON
5. Logs a `E` event record to CSV
6. Terminates the session

Adding a new action means: write a method decorated with `@ksef_action`, register it in `main.py`'s `_actions` dict.

Some actions skip the decorator entirely and call `self.genE(...)` directly, writing their result via `E.zapisz_res(...)` / `EV.koniec(...)`. Two sub-categories:
- **No KSeF session at all** (`daj_konfiguracje`, `dodaj_token`, `dodaj_certyfikat`) — pure local-file operations.
- **Session with ad-hoc credentials** (`sprawdz_token`, `sprawdz_certyfikat`) — credentials come from CLI args rather than `load_credentials`, so the standard decorator flow doesn't apply. They construct the SDK manually via `KSEFSDK.initsdk(...)` / `initsdkcert(...)` and exercise auth with a lightweight call (`get_list_of_tokens`).

### Configuration (`ksef_conf.py`)

- `CONF` reads `KSEFCONF` (path to YAML file) and `KSEFDIR` (working directory) from env vars.
- `NIP` class parses `NIP$SUBDIR` syntax — e.g. `7497725064$ROK2025` splits into nip and subdirectory used under `KSEFDIR/`.
- Directory layout: `KSEFDIR/{NIP}/{KSEF_NUMBER}/` for invoices, `KSEFDIR-zakupowe/{NIP}/` for purchase invoice buffer.

### Authentication (`credentials.py` + `credentials_yaml.py`)

Pluggable provider system. `credentials.py` defines:
- `Credentials` (abstract) + `TokenCredentials` / `CertCredentials` concrete subclasses.
- `CredentialsProvider` (abstract) with `get_credentials(conf, nip)` and optional `add_token` / `add_cert` (default raise `NotImplementedError`).
- Module-level helpers: `load_credentials(...)`, `add_token_credentials(...)`, `add_cert_credentials(...)`.
- Provider registry: `register_provider`, `get_provider`, `set_default_provider`. Default is `yaml`. Override via `KSEF_CREDENTIALS_PROVIDER` env var or `importlib.metadata` entry points in the `ksef_cli.credentials_providers` group.

`credentials_yaml.py` implements the default `yaml` provider against the file at `KSEFCONF`. Two supported schemes:

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

Environments map to KSeF endpoints: `prod` → production, `demo` → PREKSEF, `test` → DEVKSEF, `unittest` → UNITTEST.

The `dodaj_token` and `dodaj_certyfikat` CLI actions upsert entries into the YAML config (silent overwrite if `NIP{nip}` already exists). `env_s` is validated via `resolve_env(...)` before write. The `sprawdz_token` / `sprawdz_certyfikat` actions are read-only validators — they verify that supplied credentials can actually authenticate against KSeF without touching the YAML, intended as a "dry run" before `dodaj_*`.

The `pobierz_tokeny` action wraps `KSEFSDK.get_list_of_tokens()` to return the list of session tokens KSeF has on file for the configured NIP — uses the standard `@ksef_action` flow (loaded credentials, real session).

### Logging (`ksef_log.py`)

- `LOGGER` base class sets up file logging to `KSEFDIR/ksef.log` and `KSEFDIR/{NIP}/ksef.log`.
- `E` records operation events to `KSEFDIR/events.csv` and per-NIP CSVs with timing, status, and error info.
- `KSEFCLI` inherits from both `LOGGER` and `KSEF_ZAKUPOWE_HELPER`.

### Purchase Invoice Buffer (`ksef_zakupowe.py`)

Implements incremental sync: tracks the last fetched KSeF sequence number in `KSEFDIR-zakupowe/{NIP}/lastread.json`, stores each invoice as `{KSEF_NUMBER}/faktura.xml` + `{KSEF_NUMBER}/metadata.json`. The `uaktualnij_zakupowe_bufor` action fetches only new invoices since the last run.

### Test Structure

Tests use **pytest** and require a live KSeF test environment. Test configs live in `tests/conf/` and sample XML invoices in `tests/testdata/`.

**Shared infrastructure (`ksef_test_base.py`)** — not collected by pytest:
- `AKsefCli` — abstract adapter interface with static methods for each CLI operation.
- Concrete adapters: `TestKsefCli` (direct SDK), `TestKsefCliMain` (via `run_main()`), `TestWsadowoKsefCli` / `TestWsadowoMainKsefCli` (batch submission).
- `AbstractTestKSEFCLI` — mixin with `_test_*` helper methods that implement the actual assertion logic; subclasses call these with a chosen adapter.

**`test0.py`** — standalone error/auth tests (no live session required for the first two).

**`test1.py`** — `TestKSEFCombined`: single class parametrized over three adapters (`token`, `cert`, `main`). Tests that only apply to a subset use `pytest.skip()` guarded by flags on the `_KSEFConf` dataclass (`is_token`, `is_main`, `has_zbiorowy`).

**`test2.py`** — remaining test classes:
- `TestKSEFCliCertNIPDIR` — cert auth with `NIP$SUBDIR` path patterns.
- `TestKSEFWsadowe` / `TestKSEFWsadowoMain` — batch submission via SDK and CLI.
- `TestKSEFWsadowoDuzoFaktur` — bulk invoice submission (up to 10 invoices).

**`test3.py`** — credential write-path tests for `add_token_credentials` / `add_cert_credentials` and the `dodaj_token` / `dodaj_certyfikat` CLI actions. Uses `tmp_path` + `monkeypatch` fixtures — no live KSeF session, no shared state with `tests/conf/`.
