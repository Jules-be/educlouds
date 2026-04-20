# Educlouds — Interview Upgrade Plan

## The Pitch (memorize this)
> "Educlouds is a peer-to-peer compute sharing platform — like Airbnb for CPU/GPU time.
> Students submit Python jobs that run in Docker containers on lenders' machines.
> I built the full stack: Flask backend, role-based auth, SSH/SFTP remote execution on GCP,
> and an intelligent matching algorithm that assigns jobs to the best available resource."

---

## Current Status

### What already works
- User registration and login with role-based access (Lender / Borrower)
- Lenders can register compute resources with availability status
- Borrowers can upload Python scripts with dependencies
- Jobs execute in Docker containers on a remote GCP VM via SSH/SFTP
- Job status tracking: initiated → running → done / error
- Result retrieval (output.txt / error.txt)

### Bugs found (Phase 1 — in progress)
- [x] Bug 1 — `list.py` referenced non-existent model fields → fixed to use real fields and `.name`
- [x] Bug 2 — `Request.owner_id` type mismatch → fixed + simplified schema from 5 tables to 3
- [x] Bug 3 — SSH credentials hardcoded in `requests.py` → moved to `.env` / `config.py`
- [ ] Bug 4 — Duplicate routes and templates (`/api/borrowers/submitRequest` vs `/request/new`, `borrower.html` vs `request.html`)

---

## Upgrade Roadmap

### Phase 1 — Fix what's broken (doing now)
Goal: make the codebase correct and clean before adding anything new.

- [x] Fix `list.py` field references
- [ ] Fix `Request.owner_id` type (Integer → String to match UUID)
- [ ] Move SSH host, user, key_path to environment variables
- [ ] Remove old duplicate routes from `views.py`
- [ ] Delete unused templates (`borrower.html`, `viewRequest.html`)

**Interview talking point:** "I audited an existing codebase, identified schema mismatches and hardcoded credentials, and refactored the code to be correct and secure."

---

### Phase 2 — Complete the core story
Goal: the matching algorithm actually runs when a job is submitted.

- [ ] Review and understand `backend/src/matching.py`
- [ ] Define matching logic: assign job to best available lender based on workload type
- [ ] Wire matching into the job submission flow (`requests.py`)
- [ ] Add a Lender dashboard: show incoming requests, accept / decline
- [ ] Move job execution to Celery background task (stop blocking the HTTP request)
- [ ] Add job status polling on the frontend (borrower sees live updates)

**Interview talking point:** "I designed a resource matching system that scores lenders by resource type and availability, and built an async job pipeline using Celery and Redis."

---

### Phase 3 — Add ML layer (your differentiator as a master's student)
Goal: use your ML background to make the platform smarter.

- [ ] Collect job execution data: lender, workload type, actual runtime
- [ ] Build a simple runtime prediction model (linear regression or gradient boosting)
  - Features: `estimated_workload`, `dependency_count`, `python_version`, `resource_type`
  - Target: job completion time in seconds
- [ ] Show predicted runtime to borrower at submission time
- [ ] Improve matching algorithm to factor in predicted runtime per lender

**Interview talking point:** "I used historical job data to train a runtime prediction model, and integrated it into the matching algorithm to select the lender most likely to complete the job fastest."

---

### Phase 4 — Polish for interviews
- [ ] Rewrite README with: overview, architecture diagram, setup instructions, design decisions
- [ ] Add `docs/architecture.md` with a system diagram
- [ ] Deploy to Render or Railway so you can demo it live
- [ ] Record a 2-minute demo GIF or video
- [ ] Write `docs/interview-notes.md` with stories for behavioral questions

---

## Key Technical Decisions to be able to explain

| Decision | What to say |
|----------|-------------|
| Why Flask? | Lightweight, easy to reason about, good for a focused backend without a heavy framework |
| Why Docker for job execution? | Isolation — each job runs in its own container so a student's script can't affect the host |
| Why Celery + Redis? | Decouples job submission from execution — HTTP request returns immediately, worker handles the job |
| Why SSH/SFTP? | Direct, low-overhead way to delegate execution to a remote machine without a full orchestration layer |
| Why UUID for User.id? | Avoids sequential ID enumeration — a basic security practice for user-facing IDs |

---

## Files to know

| File | Purpose |
|------|---------|
| `backend/models.py` | Database schema — all tables and relationships |
| `backend/api/requests.py` | Job submission and execution flow |
| `backend/src/docker_tasks.py` | SSH/SFTP + Docker execution pipeline |
| `backend/src/matching.py` | Resource matching algorithm (to be wired in) |
| `backend/api/list.py` | API endpoints returning lender/borrower/user data |
| `config.py` | Environment-based configuration (dev/test/prod) |

---

## Session Log

### Session 1
- Explored full codebase and identified all bugs and gaps
- Fixed Bug 1: `list.py` field references corrected
- Defined Phase 1–4 upgrade roadmap
- Next: fix Bug 2 (UUID/Integer FK mismatch in models.py)
