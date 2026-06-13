# Synthetic Banking Ecosystem Generator

Generates deterministic, linked JSON datasets for a synthetic banking domain. The project covers customers, accounts, cards, loans, merchants, transactions, devices, sessions, behavioral signals, fraud records, investigations, approvals, task history, agent feedback, and knowledge content.

## What This Project Does

- Produces realistic banking data with consistent relationships.
- Writes the generated records to `output/<preset>/`.
- Exposes a repository layer for higher-level queries and agent workflows.
- Uses a DAL to keep storage concerns separate from business logic.

## Project Layout

- `banking_generator/` - synthetic data generation and CLI entrypoint.
- `src/data/` - DAL, cache, indexing, relationship mapping, and query helpers.
- `src/repositories/` - business-facing repository layer.
- `src/models/` - typed data models.
- `src/tests/` - unit tests for DAL, relationships, indexing, repositories, and investigation packages.
- `output/` - generated JSON datasets.

## Requirements

- Python 3.11+
- `pydantic`
- `pytest` for tests

## Install

```bash
python -m venv .venv
.venv/bin/pip install -e .
```

For test dependencies:

```bash
.venv/bin/pip install -e ".[dev]"
```

## Run The Generator

Default preset is `small`:

```bash
.venv/bin/python -m banking_generator
```

Other presets:

```bash
.venv/bin/python -m banking_generator --medium
.venv/bin/python -m banking_generator --large
```

Optional flags:

- `--seed <int>` - controls deterministic output, default `42`.
- `--output-dir <path>` - writes under that directory, default `output`.
- `--validate` - runs validation after generation.

You can also use the console script:

```bash
.venv/bin/banking-gen --small --validate
```

## Output

Each run writes a preset-specific directory:

```text
output/
  small/
  medium/
  large/
```

Each directory contains JSON files for the generated entities.

## Data Model

Core entities are documented in [data_model.md](data_model.md) and [schema.md](schema.md).

Main tables include:

- customers
- accounts
- credit_cards
- loans
- merchants
- devices
- sessions
- behavioral_signals
- account_openings
- kyc_documents
- transactions
- fraud_alerts
- fraud_cases
- mule_networks
- investigations
- approvals
- task_history
- agent_feedback
- knowledge_base

Primary keys live in [src/data/indexes.py](src/data/indexes.py). Relationships live in [src/data/relationships.py](src/data/relationships.py).

## Architecture

The system is split into clear layers:

`JSON Storage -> DAL -> Repository Layer -> Agent/Tool Layer`

See [architecture.md](architecture.md) and [dal_changes.md](dal_changes.md) for the detailed rationale.

### DAL Responsibilities

The DAL owns storage access only:

- lazy loading
- caching
- indexing
- filtering and joins
- parent/child lookups

### Repository Responsibilities

Repositories own business logic and compose DAL calls into usable views:

- customer risk views
- banking exposure summaries
- transaction spend and velocity analysis
- digital session and device context
- fraud investigation packages
- knowledge search

Repository overview:

- `customer_repository` - customer views and network context
- `banking_repository` - balances, credit, and exposure
- `transaction_repository` - spend and velocity
- `digital_repository` - devices, sessions, and signals
- `fraud_repository` - investigation package for LangGraph
- `investigation_repository` - approvals and case lookups
- `memory_repository` - task history and feedback
- `knowledge_repository` - operational knowledge search

Factory entrypoint:

- `RepositoryFactory.create(data_path)` builds the repository bundle with one shared DAL instance.

## Validation

Run the standalone validator:

```bash
.venv/bin/python validate.py output/small
```

Or validate during generation:

```bash
.venv/bin/python -m banking_generator --small --validate
```

## Tests

```bash
.venv/bin/pytest
```

## Current Scope

- Storage is JSON-backed today.
- The DAL is designed for future backend swaps without changing repository APIs.
- Concurrency and transactional guarantees are not database-grade yet.

## References

- [architecture.md](architecture.md)
- [dal_changes.md](dal_changes.md)
- [TOOLS.md](TOOLS.md)
- [repository_guide.md](repository_guide.md)
- [data_model.md](data_model.md)
- [schema.md](schema.md)
