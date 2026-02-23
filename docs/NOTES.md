# 📚 Personal Learning Notes — Dagster

> These are my own notes for understanding the Dagster concepts used in this project.
> Not intended for the project README.

---

## Key Files & What They Do

### `__init__.py`
- Used to define **Dagster Definitions** — the entry point that wires everything together.
- Instantiates **Dagster resources** like `PostgresResource` (the database connection).
- Registers all assets so Dagster knows about them.

### `resources.py`
- Used to define **reusable, configurable** objects that represent external systems and services.
- Things like `database connections`, `API clients`, and `cloud credentials` are defined centrally here instead of being hardcoded directly into assets.
- These resources are then **injected into assets at runtime** by Dagster (like dependency injection).

---

## Concepts

### What is a Resource?
A Resource is Dagster's way of managing connections to the outside world (databases, APIs, etc.).
You define it once in `resources.py`, register it in `__init__.py`, and then any asset can request it by name via a type hint:
```python
def my_asset(database: PostgresResource):
    ...
```
Dagster sees the type hint and injects the correct object — you don't import or instantiate it yourself.

### What is `@multi_asset`?
Use `@multi_asset` when one function produces **multiple distinct assets (tables/datasets)**.
Normal `@asset` can only return one thing. `@multi_asset` lets you `yield` multiple named outputs.

### Parallelism in Dagster
Two assets run in parallel automatically if:
1. They **do not depend on each other** (no shared input/output relationship).
2. The executor supports concurrency (`dagster dev` is single-threaded by default).

In this project, `process_valid_records` and `process_invalid_records` can run in parallel
because both only depend on `validated_uld_records`, not on each other.
