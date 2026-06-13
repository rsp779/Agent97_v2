# DAL Changes: Why, What, and How

This document explains the Data Access Layer changes added for `Agent97_v2`.

## Why this was added

The original code path read JSON data directly from the generator and validation code. That works for a small script, but it does not scale for:

- LangGraph agents that need a stable interface
- future storage swaps like PostgreSQL or DuckDB
- reusable business logic in repositories
- faster lookups on large datasets
- testability and dependency injection

The goal was to separate **storage access** from **business logic**.

## What changed

The DAL was split into small, focused modules under [`src/data/`](/Users/rsp/Desktop/autonomus_agent/src/data):

- [`data_access_layer.py`](/Users/rsp/Desktop/autonomus_agent/src/data/data_access_layer.py)
- [`cache.py`](/Users/rsp/Desktop/autonomus_agent/src/data/cache.py)
- [`indexes.py`](/Users/rsp/Desktop/autonomus_agent/src/data/indexes.py)
- [`query_engine.py`](/Users/rsp/Desktop/autonomus_agent/src/data/query_engine.py)
- [`relationships.py`](/Users/rsp/Desktop/autonomus_agent/src/data/relationships.py)

The repository layer then consumes the DAL instead of reading JSON files directly:

- [`src/repositories/base_repository.py`](/Users/rsp/Desktop/autonomus_agent/src/repositories/base_repository.py)
- [`src/repositories/customer_repository.py`](/Users/rsp/Desktop/autonomus_agent/src/repositories/customer_repository.py)
- [`src/repositories/banking_repository.py`](/Users/rsp/Desktop/autonomus_agent/src/repositories/banking_repository.py)
- [`src/repositories/transaction_repository.py`](/Users/rsp/Desktop/autonomus_agent/src/repositories/transaction_repository.py)
- [`src/repositories/fraud_repository.py`](/Users/rsp/Desktop/autonomus_agent/src/repositories/fraud_repository.py)
- [`src/repositories/factory.py`](/Users/rsp/Desktop/autonomus_agent/src/repositories/factory.py)

## How the DAL works

### 1. Storage backend abstraction

[`data_access_layer.py`](/Users/rsp/Desktop/autonomus_agent/src/data/data_access_layer.py) defines a `StorageBackend` protocol.

Why:
- This makes the DAL **storage agnostic**.
- JSON is the first backend, but the interface can later be implemented by PostgreSQL, DuckDB, or Snowflake without changing repository APIs.

How:
- `JsonDataBackend` implements the protocol for the current `output/<preset>/*.json` files.
- `DataAccessLayer.from_path()` creates a DAL using that backend.

### 2. Lazy loading

[`cache.py`](/Users/rsp/Desktop/autonomus_agent/src/data/cache.py) stores datasets in memory only after they are first requested.

Why:
- Avoids loading every JSON file at startup.
- Reduces startup cost.
- Makes it cheaper to access only the tables that an agent actually needs.

How:
- `DataAccessLayer.load_dataset(table)` calls `cache.get_or_load()`.
- If the table is not in cache, the backend reads the file once.
- Later requests reuse the cached list.

### 3. Caching

Caching is the in-memory reuse layer on top of lazy loading.

Why:
- JSON parsing is repeated work if the same table is read many times.
- Repositories often query the same datasets repeatedly during a single agent run.

How:
- The cache is a simple dictionary keyed by table name.
- `save_dataset()` refreshes the cache after writing.

### 4. Automatic indexing

[`indexes.py`](/Users/rsp/Desktop/autonomus_agent/src/data/indexes.py) defines primary keys for each dataset and builds lookup maps.

Why:
- Direct list scans are slow for repeated `get_by_id()` calls.
- Agents often need point lookups like `customer_id`, `account_id`, or `transaction_id`.

How:
- `PRIMARY_KEYS` maps each dataset to its ID field.
- `build_primary_index()` converts rows into `{id: row}`.
- `DataAccessLayer._ensure_index()` creates the index the first time a dataset is loaded.

Result:
- `get_by_id("customers", "cus_00000001")` becomes a dictionary lookup instead of a full scan.

### 5. Query helpers

[`query_engine.py`](/Users/rsp/Desktop/autonomus_agent/src/data/query_engine.py) implements reusable list operations.

Why:
- Repositories should not duplicate filtering and join logic.
- Query behavior should live in one place.

How:
- `matches()` checks row criteria.
- `filter_rows()` returns all rows matching criteria.
- `inner_join()` combines rows from two datasets.
- `aggregate()` groups or reduces rows.

### 6. Relationship map

[`relationships.py`](/Users/rsp/Desktop/autonomus_agent/src/data/relationships.py) describes parent-child links between datasets.

Why:
- The DAL needs a central source of truth for foreign-key style connections.
- Repositories should not hardcode dataset relationships everywhere.

How:
- `RELATIONSHIPS` stores tuples of `(fk_field, parent_table, parent_key)`.
- `children()` uses this map to return all dependent rows for a parent record.
- `parent()` uses the reverse lookup path for a child record.

## What the public DAL API does

[`data_access_layer.py`](/Users/rsp/Desktop/autonomus_agent/src/data/data_access_layer.py) now exposes:

- `load_dataset(table)`
- `get(table, **criteria)`
- `get_by_id(table, record_id)`
- `find(table, **criteria)`
- `filter(table, predicate)`
- `exists(table, **criteria)`
- `count(table, **criteria)`
- `children(parent_table, parent_id)`
- `parent(child_table, child_id, fk_field, parent_table)`
- `join(left_table, right_table, left_key, right_key)`
- `aggregate(table, group_by, metric)`

Why this matters:
- It gives repositories one stable interface.
- Agents never need to read JSON directly.
- The backend can change later without rewriting business logic.

## Repository layer impact

Repositories now sit above the DAL and contain business rules.

Examples:
- [`CustomerRepository`](/Users/rsp/Desktop/autonomus_agent/src/repositories/customer_repository.py) returns customer views and networks.
- [`BankingRepository`](/Users/rsp/Desktop/autonomus_agent/src/repositories/banking_repository.py) calculates balances, credit limits, and exposure.
- [`TransactionRepository`](/Users/rsp/Desktop/autonomus_agent/src/repositories/transaction_repository.py) computes spend and velocity.
- [`FraudRepository`](/Users/rsp/Desktop/autonomus_agent/src/repositories/fraud_repository.py) builds the investigation package for LangGraph.

Why:
- This keeps business logic out of raw data access.
- It makes the system easier to test and easier to evolve.

## Dependency injection

[`factory.py`](/Users/rsp/Desktop/autonomus_agent/src/repositories/factory.py) creates a `RepositoryBundle`.

Why:
- No global state.
- Easier testing.
- Easier backend swapping.

How:
- `RepositoryFactory.create(data_path)` creates one DAL.
- That DAL is passed into every repository.
- All repositories share the same cache and indexes.

## Pydantic models

[`src/models/`](/Users/rsp/Desktop/autonomus_agent/src/models) adds typed models for the datasets.

Why:
- Validation catches bad data early.
- Typed models help future API compatibility.
- Repository outputs become safer and clearer.

How:
- Repositories call `Model.model_validate(row)`.
- Output can be serialized with `model_dump()`.

## Current limitations

This implementation is production-oriented, but still JSON-backed.

That means:
- file updates are local to the output directory
- concurrency and transactions are not yet database-grade
- backend swapping is designed, not yet implemented for Postgres/DuckDB

## Summary

The DAL now acts as the storage boundary:

JSON Storage -> DAL -> Repository Layer -> Agent/Tool Layer

That is the main architectural shift.
It gives the project lazy loading, caching, indexing, reusable query primitives, and a clean path to future storage backends.

