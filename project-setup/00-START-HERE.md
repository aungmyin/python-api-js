# Shopping Cart Project — Start Here
### FastAPI + PostgreSQL + Vanilla JS + Docker, built with Claude Code in VS Code

A learning project to understand how Python powers a real REST API, how a
frontend talks to it, and how Docker ties it all together. The work is split
into phases so you can stop and resume on different days.

---

## The Files in This Guide

| File | What it covers | When to use it |
|---|---|---|
| **00-START-HERE.md** | Setup, prerequisites, workflow, how to resume | Read first, revisit when resuming |
| **01-phase-1-backend.md** | FastAPI + PostgreSQL API in Docker | Day(s) 1 |
| **02-phase-2-frontend.md** | Vanilla JS frontend with Vite in Docker | After Phase 1 is fully working |
| **03-phase-3-typescript.md** | Convert the frontend to TypeScript | After Phase 2 is fully working |
| **99-troubleshooting.md** | Quick-fix table for common errors | Keep open whenever something breaks |

---

## 1. Prerequisites (one-time setup)

Install these before starting:

| Tool | Purpose | Check it works |
|---|---|---|
| **VS Code** | Editor | `code --version` |
| **Docker Desktop** | Runs API + database + frontend in containers | `docker compose version` |
| **Node.js 18+** | Required by Claude Code (and Vite) | `node --version` |
| **Claude Code** | AI coding agent in your terminal | `claude --version` |
| **Git** (recommended) | Version control, checkpoint each step | `git --version` |

Install Claude Code:

```bash
npm install -g @anthropic-ai/claude-code
```

> **Important:** Keep Docker Desktop **running** whenever you work. Claude
> Code runs `docker compose` commands to verify each step and will stall if
> the Docker daemon is down.

### Recommended VS Code extensions

- **Python** (Microsoft) — syntax, linting, debugging
- **Docker** (Microsoft) — see running containers in the sidebar
- **REST Client** or **Thunder Client** — test API endpoints inside VS Code

---

## 2. Project Setup (one-time)

1. Create a project folder and open it in VS Code:

   ```bash
   mkdir shopping-project
   cd shopping-project
   code .
   ```

2. Open the integrated terminal: **Terminal → New Terminal**
   (or `` Ctrl+` `` / `` Cmd+` ``).

3. Initialize Git so you can checkpoint after every step:

   ```bash
   git init
   ```

4. Start Claude Code from the project root:

   ```bash
   claude
   ```

   The first run will ask you to log in.

---

## 3. The Working Rhythm (every phase, every step)

Each phase file contains one big prompt designed so Claude Code builds
**one step at a time** and waits for you. The loop is always:

1. Paste the phase prompt into Claude Code.
2. Claude Code builds one step, then stops and summarizes.
3. **Verify it yourself** using the checkpoint list in the phase file.
4. Commit a checkpoint:

   ```bash
   git add -A && git commit -m "Phase X Step N: <what was built>"
   ```

5. Tell Claude Code `continue` / `next step`.

If something breaks, paste the **full error message** into Claude Code —
don't summarize it. Check `99-troubleshooting.md` for the common ones.

---

## 4. How to Stop and Resume Another Day

**When stopping:**

1. Finish and verify the step you're on (don't stop mid-step).
2. Commit: `git add -A && git commit -m "Phase X: stopped after step N"`
3. Shut containers down cleanly: `docker compose down`
   (your database data survives — it lives in a named Docker volume).

**When resuming:**

1. Start Docker Desktop.
2. Open the project in VS Code, open the terminal.
3. Bring the stack back up: `docker compose up --build`
4. Start Claude Code fresh: `claude`
5. Paste the **resume prompt** below (edit the phase/step numbers):

```
I'm resuming a step-by-step learning project. This repo contains a shopping
cart app: FastAPI + PostgreSQL backend in api/, Docker Compose at the root
(and possibly a web/ frontend if I've started Phase 2).

I previously completed Phase <X> up to and including step <N> of my phase
guide. Before doing anything:
1. Read docker-compose.yml, the api/ code, and web/ if it exists.
2. Summarize the current state of the project in a few sentences so we
   confirm we're in sync.
3. Run `docker compose up --build` and confirm everything still works
   (API docs at http://localhost:8000/docs, frontend at
   http://localhost:5173 if it exists).

Then wait — I will paste the instructions for the next step. Keep the same
working style as before: one step at a time, explain in plain language
(I'm learning), stop after each step for my confirmation.
```

Then open the phase file you're on and paste the **specific step text** you
want to continue with (each phase file lists its steps individually for
exactly this purpose).

> **Tip:** A fresh Claude Code session doesn't remember your previous
> sessions — that's fine. The resume prompt makes it re-read your actual
> code, which is more reliable than memory anyway.

---

## 5. Phase Completion Gates

Don't start a phase until the previous one fully passes:

- **Start Phase 2 only when:** the entire backend flow works in Swagger UI —
  register → login → add to cart → checkout → order in history — and tests pass.
- **Start Phase 3 only when:** the entire shopping flow works in the browser
  end to end.

Next: open **01-phase-1-backend.md**.
