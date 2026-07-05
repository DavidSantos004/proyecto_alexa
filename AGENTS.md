    # JARVIS OS — Personal Intelligence Operating System

    ## Core Philosophy
    LLMs **never** execute actions directly — they only **propose**. The `OrchestratorService` is the sole component that decides whether an approved action runs.

    ## Architecture
    - **Modular Monolith**: single FastAPI service, 8 internal modules under `app/`.
    - Each module: `domain/` (Pydantic models), `ports/` (Protocol interfaces only — no implementations yet), `service.py` (business logic).
    - Modules are decoupled via interfaces; no direct imports between modules.

    ## Stack
    Python 3.12+, FastAPI, Pydantic v2, SQLAlchemy 2.0, Alembic, PostgreSQL 16, Docker Compose.

    ## Commands
    ```bash
    # install (from .venv or docker)
    pip install -e ".[dev]"

    # run dev server
    uvicorn app.main:app --reload

    # test (single package)
    python -m pytest tests/test_orchestrator/ -v

    # lint
    ruff check .

    # docker
    docker compose up --build
    ```

    ## Testing
    - `pytest` with class-based tests using `setup_method` (not fixtures yet).
    - Test paths mirror `app/` structure: `tests/test_orchestrator/`, etc.

    ## Conventions
    - StrEnum for all enum types (`ActionSource`, `DecisionVerdict`, etc.).
    - `action_id` generated via `uuid4().hex` on `ProposedAction` creation.
    - `ports/__init__.py` carries an explicit docstring: interfaces only; implementations deferred.
    - `decide()` currently auto-approves all actions (Sprint 1 temporary behavior, documented in code).
    - Ruff: line-length 88, rules `E,F,I,N,W`.

    ## Current State (Sprint 1)
    - Only `orchestrator/` has code: `ProposedAction`, `OrchestratorDecision` models + `OrchestratorService.decide()`.
    - No DB, no adapters, no auth, no real decisions.
    - `.gitignore` missing.
    - Repo has 0 commits; `origin` points to `git@github.com:DavidSantos004/proyecto_alexa.git`.
