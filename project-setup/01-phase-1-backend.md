# Phase 1 — Backend: FastAPI + PostgreSQL + Docker

**Goal:** a complete Shopping Cart REST API running in Docker, with products,
categories, users (JWT auth), carts, orders, migrations, and tests.

**Prerequisite:** setup from `00-START-HERE.md` is done, Docker Desktop is
running, and you've started `claude` from the project root.

---

## The Full Phase Prompt

Paste this into Claude Code to start (or restart) the phase:

```
I want to build a Shopping Cart REST API as a learning project using Python,
FastAPI, PostgreSQL, and Docker. Please work with me step by step — build and
explain one piece at a time, wait for my confirmation before moving to the
next step, and keep the code simple enough for someone learning API
development to follow.

TECH STACK
- Python 3.12
- FastAPI (async, with automatic OpenAPI/Swagger docs)
- PostgreSQL (via SQLAlchemy + Alembic for migrations)
- Pydantic for request/response validation
- Docker + Docker Compose (one container for the API, one for PostgreSQL)
- Pytest for tests

FEATURES (build in this order)
1. Project scaffolding: folder structure, requirements.txt/pyproject.toml,
   .env handling, basic FastAPI app with a health-check endpoint
2. Docker setup: Dockerfile for the API + docker-compose.yml with an "api"
   service and a "db" (Postgres) service, with a named volume for data
   persistence and environment variables for DB credentials
3. Database models: Product, Category, User, Cart, CartItem, Order, OrderItem
   using SQLAlchemy, with Alembic migrations
4. Product & Category endpoints: CRUD (list, get, create, update, delete)
   with pagination and filtering
5. User auth: registration, login, JWT access tokens, password hashing
   (passlib/bcrypt)
6. Cart endpoints: add item, update quantity, remove item, view cart
   (tied to the logged-in user)
7. Checkout/Order endpoints: convert cart to an order, view order history
8. Tests: pytest tests for at least the product and cart endpoints,
   run inside Docker
9. README: how to run everything with `docker compose up`, how to run
   migrations, and example curl requests for each endpoint

GROUND RULES
- Explain what each file does and why, in plain language, as you go —
  I'm learning
- After each numbered step, stop and give me a short summary of what
  was added and how to test it before continuing
- Use environment variables for all secrets/config, never hardcode them
- Keep it runnable with a single `docker compose up --build`

Start with step 1.
```

---

## Steps, Checkpoints, and Resume Snippets

Each step below has a **checkpoint** (verify before continuing) and a
**resume snippet** (paste after the resume prompt from `00-START-HERE.md`
if you're picking up on a new day).

### Step 1 — Project scaffolding
- **Checkpoint:** `api/` folder exists with a FastAPI app and a
  health-check endpoint; the folder structure has been explained to you.
- **Resume snippet:** `Continue with Phase 1, step 2: the Docker setup —
  Dockerfile for the API plus docker-compose.yml with "api" and "db"
  (Postgres) services, named volume for data, env vars for credentials.`

### Step 2 — Docker setup
- **Checkpoint:** `docker compose up --build` starts both containers;
  `http://localhost:8000/docs` shows Swagger UI with the health check.
- **Resume snippet:** `Continue with Phase 1, step 3: SQLAlchemy models
  (Product, Category, User, Cart, CartItem, Order, OrderItem) with Alembic
  migrations.`

### Step 3 — Database models + migrations
- **Checkpoint:** Alembic migration runs successfully; tables exist in
  Postgres (Claude Code can show you how to check with `psql` or a query).
- **Resume snippet:** `Continue with Phase 1, step 4: CRUD endpoints for
  Products and Categories with pagination and filtering.`

### Step 4 — Product & Category endpoints
- **Checkpoint:** From Swagger UI you can create a category, create a
  product, list products with pagination, update, and delete.
- **Resume snippet:** `Continue with Phase 1, step 5: user auth —
  registration, login, JWT access tokens, password hashing with
  passlib/bcrypt.`

### Step 5 — Auth (registration, login, JWT)
- **Checkpoint:** Register + login via Swagger returns a JWT; the
  "Authorize" button in Swagger works with that token.
- **Resume snippet:** `Continue with Phase 1, step 6: cart endpoints —
  add item, update quantity, remove item, view cart, tied to the
  logged-in user.`

### Step 6 — Cart endpoints
- **Checkpoint:** While authorized, you can add products to a cart, change
  quantities, remove items, and view the cart. Unauthorized requests get 401.
- **Resume snippet:** `Continue with Phase 1, step 7: checkout/order
  endpoints — convert cart to an order, view order history.`

### Step 7 — Checkout & orders
- **Checkpoint:** Full flow works in Swagger: login → add to cart →
  checkout → order appears in order history and the cart is emptied.
- **Resume snippet:** `Continue with Phase 1, step 8: pytest tests for at
  least the product and cart endpoints, runnable inside Docker.`

### Step 8 — Tests
- **Checkpoint:** Tests pass inside Docker (Claude Code shows the command;
  typically something like `docker compose run api pytest`).
- **Resume snippet:** `Continue with Phase 1, step 9: the README — how to
  run everything with docker compose up, how to run migrations, and example
  curl requests for each endpoint.`

### Step 9 — README
- **Checkpoint:** Following your own README from scratch
  (`docker compose down` then `up --build`) brings everything back working.

---

## Phase 1 Done — Completion Gate

Before moving on, verify the whole thing one more time:

- [ ] `docker compose up --build` starts clean with no errors
- [ ] Swagger UI at `http://localhost:8000/docs` lists all endpoints
- [ ] Register → login → add to cart → checkout → order history works
- [ ] Tests pass
- [ ] Final commit: `git add -A && git commit -m "Phase 1 complete"`

Next: **02-phase-2-frontend.md**. Use `/clear` in Claude Code before
starting it — Phase 2's step 0 re-reads your code anyway.
