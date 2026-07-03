# Troubleshooting Quick Reference

Keep this open whenever something breaks. When in doubt, paste the **full
error message** into Claude Code — never a summary.

---

## Docker & Networking

| Symptom | Likely cause | Fix |
|---|---|---|
| `Failed to fetch` in browser console | Frontend calling `http://api:8000` (Docker-internal hostname) from the browser | Browser code must use `http://localhost:8000`; only container-to-container traffic uses service names |
| CORS error in browser console | FastAPI not allowing the frontend origin | Add `http://localhost:5173` to CORSMiddleware `allow_origins` in the FastAPI app |
| `localhost:5173` unreachable | Vite not bound to `0.0.0.0`, or port not published | Vite must run with `--host 0.0.0.0`; compose needs `ports: ["5173:5173"]` |
| Edits to `web/` don't hot reload | File watching broken across bind mounts | `server.watch.usePolling: true` in `vite.config.js` |
| `Cannot find module` inside web container | Bind mount overwrote container's `node_modules` | Anonymous volume in compose: `- /app/node_modules` |
| Port already in use | Old container or another app on 8000 / 5173 / 5432 | `docker compose down`, then `docker ps` to find stragglers; a local Postgres install often squats on 5432 |
| DB connection refused when API starts | API started before Postgres was ready | Healthcheck on `db` + `depends_on: { db: { condition: service_healthy } }` on `api` |
| Claude Code stalls on docker commands | Docker Desktop not running | Start Docker Desktop, retry |
| Changes to Dockerfile/requirements not taking effect | Stale image | Rebuild: `docker compose up --build` (add `--no-cache` if still stale) |
| Database data disappeared | Ran `docker compose down -v` (the `-v` deletes volumes) | Plain `docker compose down` keeps the named volume; avoid `-v` unless you want a wipe |

---

## Backend (FastAPI / Postgres)

| Symptom | Likely cause | Fix |
|---|---|---|
| `relation "..." does not exist` | Migrations not applied | Run the Alembic upgrade command from the README inside the api container |
| 401 on cart/order endpoints in Swagger | Not authorized in Swagger UI | Click "Authorize", paste the token from the login response |
| 422 Unprocessable Entity | Request body doesn't match the Pydantic schema | Compare your JSON to the schema shown in `/docs`; field names and types must match exactly |
| Password hashing / bcrypt errors on startup | passlib/bcrypt version mismatch | Ask Claude Code to pin compatible versions in requirements and rebuild |

---

## Frontend (Vanilla JS / Vite)

| Symptom | Likely cause | Fix |
|---|---|---|
| Products page empty, no errors | Database has no products | Add a couple via Swagger UI (`POST /products`) first |
| Token works, then stops after refresh | JWT stored in memory only | Expected with in-memory storage; switch to localStorage if you chose that tradeoff, or log in again |
| 401 after some time even with token | JWT expired | Log in again; token lifetime is set in the backend auth config |
| Stale UI after cart actions | UI not re-rendered after fetch | Make sure the render function is called after each successful API call |

---

## TypeScript Phase

| Symptom | Likely cause | Fix |
|---|---|---|
| Hundreds of errors after bulk rename | Converted everything at once | Revert (`git checkout .`), convert one file at a time as the Phase 3 prompt instructs |
| `Property 'value' does not exist on type 'HTMLElement'` | DOM query typed too broadly | Cast or narrow: `document.querySelector<HTMLInputElement>('#email')` |
| `Object is possibly 'null'` everywhere in strict mode | Strict null checks doing their job | Handle the null case (guard clause) — don't blanket-suppress with `!` while learning |
| Fetch response typed as `any` | `response.json()` returns `Promise<any>` | Type the boundary: `const data = (await res.json()) as Product[];` (or use generated/validated types in step 7) |

---

## Recovering From a Bad Step

1. See what changed: `git status` and `git diff`
2. Throw away uncommitted changes: `git checkout .` (careful — irreversible)
3. Roll back to the last good checkpoint: `git log --oneline` then
   `git reset --hard <commit>`
4. Tell Claude Code: `The last step broke X (error pasted below). I've
   rolled back to the previous commit. Let's redo that step differently.`

This is exactly why the guides say to commit after every verified step.
