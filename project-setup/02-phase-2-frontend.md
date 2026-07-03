# Phase 2 — Frontend: Vanilla JavaScript + Vite + Docker

**Goal:** a working shopping UI in the browser (products, cart, login,
checkout) built with plain JavaScript and the Fetch API, served by Vite
inside Docker, talking to your Phase 1 API.

**Prerequisites:**
- Phase 1 completion gate fully passed (see `01-phase-1-backend.md`)
- Docker Desktop running, `docker compose up --build` works
- Fresh Claude Code session (`/clear` or restart `claude`) from the
  project root

---

## Why the Networking Rules Matter (read once)

This phase has one classic trap: **your fetch calls run in the browser,
outside Docker**. Inside Docker, containers reach each other by service name
(`http://api:8000`), but your browser can only reach published ports on
`localhost`. Mixing these up causes mysterious "Failed to fetch" errors.
The prompt below bakes the fixes in — including Vite's `--host 0.0.0.0`,
hot-reload polling, the `node_modules` volume trick, and CORS.

---

## The Full Phase Prompt

Paste this into Claude Code to start (or restart) the phase:

```
I have a Shopping Cart REST API built with FastAPI + PostgreSQL, running
with Docker Compose (services: "api" and "db"). Now I want to build a
frontend using plain vanilla JavaScript (no framework) to learn how a
frontend talks to a REST API. I'll convert it to TypeScript later, so
set it up so that conversion stays easy.

TECH STACK
- Vite with the "vanilla" JavaScript template (plain JS for now)
- Plain HTML5 + CSS3, no CSS framework
- Fetch API only for HTTP requests (no axios)
- No state management library — plain JS objects and DOM updates

IMPORTANT NETWORKING RULES (Docker + browser)
- My fetch calls run in the BROWSER, not inside Docker. So the frontend
  must call the API at http://localhost:8000 (the api service's published
  port), NOT http://api:8000. Put the API base URL in a single config
  constant (e.g. const API_URL) so it's easy to change later.
- The Vite dev server runs inside a container, so it must start with
  --host 0.0.0.0 and publish port 5173 in docker-compose.yml, or the
  browser can't reach it.
- Bind-mount ./web into the container for live editing, but add an
  anonymous volume for /app/node_modules so the mount doesn't overwrite
  installed dependencies.
- Enable file-watch polling in vite.config.js (server.watch.usePolling =
  true) so hot reload works inside Docker.
- Configure FastAPI's CORSMiddleware to allow origin
  http://localhost:5173 (and explain what CORS is when you do it).

WORK STEP BY STEP — after each step, stop, summarize what you did, tell
me how to verify it in the browser, and wait for my confirmation before
continuing.

0. First, inspect my existing project: read docker-compose.yml and the
   api/ code, list the actual endpoints (paths, methods, auth
   requirements) for products, cart, auth, and orders, and confirm them
   with me. Use the REAL endpoint names in all frontend code — don't
   assume.
1. Scaffold the frontend with Vite's vanilla JS template in a new web/
   folder next to api/. Explain the folder structure.
2. Add a "web" service to docker-compose.yml following the networking
   rules above. Verify: `docker compose up --build` should serve the
   Vite starter page at http://localhost:5173 and the API docs at
   http://localhost:8000/docs, and editing a file in web/ should hot
   reload the page.
3. Build the static page layout: header, product grid area, cart panel —
   plain HTML + CSS, no data yet.
4. Fetch products from the products endpoint and render them as cards.
   Handle loading and error states, and explain the fetch call line by
   line.
5. Add "Add to Cart" buttons calling the cart API, plus a cart panel
   showing items, quantities, and total, with update-quantity and
   remove actions.
6. Add registration and login forms calling the auth endpoints. Store
   the JWT (explain in-memory vs localStorage tradeoffs, then pick one)
   and attach it as an Authorization: Bearer header on protected
   requests. Handle 401 responses by prompting login.
7. Add checkout: call the order endpoint, clear the cart UI, show a
   confirmation with the order details.
8. Polish: responsive CSS, disable buttons while a request is in flight,
   readable error messages for failed requests.
9. Update the README: how to run everything with one
   `docker compose up --build`, plus a short troubleshooting section
   (CORS errors, port conflicts, hot reload not working).

GROUND RULES
- Explain every fetch call and every Docker networking decision in
  plain language — I'm learning
- No frameworks, no TypeScript yet
- Small readable functions over clever code
- If something I described conflicts with what you find in my actual
  code, tell me before writing anything
```

---

## Steps, Checkpoints, and Resume Snippets

If resuming on a new day: paste the resume prompt from `00-START-HERE.md`
first, then the resume snippet for your next step. Because Phase 2 depends
on exact endpoint names, also add this line when resuming mid-phase:
`Before coding, re-check the api/ routes so you use the real endpoint paths.`

### Step 0 — Inspect the existing project
- **Checkpoint:** The endpoint list Claude Code prints matches
  `http://localhost:8000/docs` exactly. Correct it if not — everything
  downstream depends on this.
- **Resume snippet:** `Continue with Phase 2, step 1: scaffold the frontend
  with Vite's vanilla JS template in a new web/ folder next to api/.`

### Step 1 — Scaffold with Vite
- **Checkpoint:** `web/` exists with the Vite vanilla template; structure
  explained.
- **Resume snippet:** `Continue with Phase 2, step 2: add the "web" service
  to docker-compose.yml following the networking rules (host 0.0.0.0,
  port 5173 published, bind mount + anonymous node_modules volume, polling
  hot reload, CORS for http://localhost:5173).`

### Step 2 — Dockerize the frontend + CORS
- **Checkpoint:** `docker compose up --build` serves the Vite starter page
  at `http://localhost:5173` AND the API docs at `http://localhost:8000/docs`;
  editing a file in `web/` hot-reloads the browser.
- **Resume snippet:** `Continue with Phase 2, step 3: static page layout —
  header, product grid area, cart panel, plain HTML + CSS, no data yet.`

### Step 3 — Static layout
- **Checkpoint:** Layout renders; no console errors.
- **Resume snippet:** `Continue with Phase 2, step 4: fetch products from
  the products endpoint and render them as cards, with loading and error
  states, explaining the fetch call line by line.`

### Step 4 — Fetch and render products
- **Checkpoint:** Real products from your database appear as cards.
  (If the DB is empty, add a couple of products via Swagger UI first.)
- **Resume snippet:** `Continue with Phase 2, step 5: Add-to-Cart buttons
  calling the cart API, plus a cart panel with quantities, total,
  update-quantity and remove actions.`

### Step 5 — Cart interactions
- **Checkpoint:** Adding/updating/removing items updates the panel and the
  backend (verify via Swagger or a page refresh). Note: cart endpoints need
  auth, so Claude Code may stub the token or reorder slightly with step 6 —
  either is fine, just make sure both end up working.
- **Resume snippet:** `Continue with Phase 2, step 6: registration and
  login forms, JWT storage (explain in-memory vs localStorage, pick one),
  Authorization: Bearer header on protected requests, and 401 handling.`

### Step 6 — Auth in the browser
- **Checkpoint:** Register, log in, add to cart while logged in; requests
  without a token get 401 and the UI prompts login.
- **Resume snippet:** `Continue with Phase 2, step 7: checkout — call the
  order endpoint, clear the cart UI, show order confirmation details.`

### Step 7 — Checkout
- **Checkpoint:** Full shopping flow works end to end in the browser.
- **Resume snippet:** `Continue with Phase 2, step 8: polish — responsive
  CSS, disable buttons during in-flight requests, readable error messages.`

### Step 8 — Polish
- **Checkpoint:** Buttons disable during requests; failed requests show a
  human-readable message; layout is usable at phone width.
- **Resume snippet:** `Continue with Phase 2, step 9: update the README
  with one-command startup and a troubleshooting section.`

### Step 9 — README
- **Checkpoint:** `docker compose down` then `docker compose up --build`
  following only the README brings the whole app back.

---

## Phase 2 Done — Completion Gate

- [ ] One command (`docker compose up --build`) runs db + api + web
- [ ] Browser flow works: browse → register/login → add to cart →
      change quantities → checkout → see confirmation
- [ ] Hot reload works when you edit `web/` files
- [ ] Final commit: `git add -A && git commit -m "Phase 2 complete"`

Next: **03-phase-3-typescript.md** — where you'll see exactly what type
safety would have caught.
