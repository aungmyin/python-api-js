# Phase 3 — Convert the Frontend to TypeScript

**Goal:** convert your working vanilla JS frontend to TypeScript, and in the
process *see* exactly which categories of bugs the type system catches.
This is deliberately a conversion exercise, not a rewrite — the app should
behave identically at the end.

**Prerequisites:**
- Phase 2 completion gate fully passed
- Everything committed (`git status` clean) — you want a safe rollback point
- Fresh Claude Code session from the project root

---

## Why This Phase Is Worth Doing

Your backend already has types: Pydantic validates every request and
response. TypeScript brings the same discipline to the frontend — if the
API returns `price` as a number and your code treats it as a string, or you
misspell `prodcut.name`, the compiler catches it before the browser ever
runs it. Converting working JS is the best way to learn this, because every
compiler error maps to a real risk that existed silently in your JS version.

---

## The Full Phase Prompt

Paste this into Claude Code:

```
My project has a FastAPI + PostgreSQL backend in api/ and a working vanilla
JavaScript frontend in web/ (Vite, Fetch API, no framework), all running
via Docker Compose. I want to convert the frontend to TypeScript as a
learning exercise. The app's behavior must not change — this is a
conversion, not a rewrite.

WORK STEP BY STEP — after each step, stop, summarize, tell me how to
verify, and wait for my confirmation.

0. Inspect web/ and api/ first. List the frontend modules you'll convert
   and the API data shapes (from the Pydantic schemas / OpenAPI docs)
   you'll need types for. Confirm with me before changing anything.
1. Add TypeScript tooling: install typescript, add a tsconfig.json
   appropriate for a Vite vanilla-ts project (start with "strict": false —
   we'll tighten it at the end), and explain each tsconfig option you set.
   Verify the dev server still runs and the app still works unchanged.
2. Create a types file (e.g. web/src/types.ts) with interfaces mirroring
   my Pydantic schemas: Product, Category, User, CartItem, Cart, Order,
   OrderItem, plus auth request/response shapes (login, register, token).
   Explain how each interface maps to its Pydantic counterpart.
3. Convert the API/fetch layer first: rename it to .ts and type every
   function's parameters and return values (e.g.
   fetchProducts(): Promise<Product[]>). Explain how typing a fetch
   response works and why the `as` cast or a validation approach is needed
   at the network boundary.
4. Convert the remaining modules one file at a time (rename .js to .ts,
   fix the errors that surface). For each error TypeScript reports,
   briefly explain what real bug that error could have been in the JS
   version — this is the learning payoff.
5. Turn on "strict": true in tsconfig.json and fix everything it surfaces
   (nulls, implicit any, DOM element types like HTMLButtonElement).
   Explain the most instructive fixes.
6. Verify no behavior changed: run the full browser flow (browse → login →
   cart → checkout) and run `tsc --noEmit` clean. Update the README's
   frontend section for TypeScript.
7. OPTIONAL (ask me first): set up automatic type generation from the
   API's OpenAPI schema at http://localhost:8000/openapi.json using
   openapi-typescript, replace the hand-written interfaces with generated
   ones, and explain why this prevents frontend/backend type drift.

GROUND RULES
- One file at a time in step 4 — never a bulk rename
- Explain every compiler error we fix in plain language; I'm learning
  what TypeScript actually protects against
- No behavior changes, no refactors beyond what typing requires
- If web/ structure differs from what I described, tell me before editing
```

---

## Steps, Checkpoints, and Resume Snippets

Resuming on a new day: use the resume prompt from `00-START-HERE.md`, then
the snippet for your next step.

### Step 0 — Inspect and plan
- **Checkpoint:** The module list and data shapes match your actual code
  and `http://localhost:8000/docs`.
- **Resume snippet:** `Continue with Phase 3, step 1: add TypeScript
  tooling (typescript + tsconfig.json for a Vite vanilla-ts setup,
  strict: false for now) and verify the app still runs unchanged.`

### Step 1 — Tooling
- **Checkpoint:** App runs exactly as before; `tsconfig.json` exists and
  its options were explained to you.
- **Resume snippet:** `Continue with Phase 3, step 2: create
  web/src/types.ts with interfaces mirroring the Pydantic schemas.`

### Step 2 — Type definitions
- **Checkpoint:** Interfaces exist for every entity; you can point at each
  field and name its Pydantic twin.
- **Resume snippet:** `Continue with Phase 3, step 3: convert the API/fetch
  layer to .ts with typed parameters and return values.`

### Step 3 — Typed fetch layer
- **Checkpoint:** App still works; fetch functions have explicit
  `Promise<...>` return types; you understand why the network boundary
  needs a cast or validation.
- **Resume snippet:** `Continue with Phase 3, step 4: convert the remaining
  modules one file at a time, explaining what real bug each compiler error
  could have been.`

### Step 4 — Convert remaining modules
- **Checkpoint:** All files are `.ts`; app behavior unchanged; you can name
  at least 2–3 real bug classes the compiler flagged (this is the point of
  the whole phase — write them down).
- **Resume snippet:** `Continue with Phase 3, step 5: enable strict mode in
  tsconfig.json and fix what it surfaces.`

### Step 5 — Strict mode
- **Checkpoint:** `"strict": true` and the project compiles clean.
- **Resume snippet:** `Continue with Phase 3, step 6: final verification —
  full browser flow, tsc --noEmit clean, README updated.`

### Step 6 — Verify + README
- **Checkpoint:** Full browser flow works; `tsc --noEmit` reports zero
  errors; README updated.
- **Resume snippet (optional step):** `Continue with Phase 3, step 7:
  generate types from the OpenAPI schema with openapi-typescript and
  replace the hand-written interfaces.`

### Step 7 — (Optional) Generated types from OpenAPI
- **Checkpoint:** Types are generated from
  `http://localhost:8000/openapi.json`; changing a Pydantic schema and
  regenerating makes the frontend compiler flag the mismatch — try it once
  to see the drift protection in action, then revert.

---

## Phase 3 Done — Completion Gate

- [ ] Everything is `.ts`, strict mode on, `tsc --noEmit` clean
- [ ] App behaves identically to the end of Phase 2
- [ ] You wrote down the real bug classes TypeScript caught during step 4
- [ ] Final commit: `git add -A && git commit -m "Phase 3 complete: TypeScript"`

## Where to Go Next (ideas)

- Rebuild the frontend in **React + TypeScript** (you now know exactly what
  the framework is abstracting)
- Add **Redis** for caching or session data — one of the fastest-growing
  pieces of the modern stack
- Add a production build: multi-stage Dockerfile serving the built frontend
  with nginx instead of the Vite dev server
- Deploy the stack to a cloud host and add CI that runs your pytest suite
