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

## Practice Topics (to revisit)
- [ ] Docker hands-on: write a script, build a Dockerfile, run it locally, see output
- [ ] Celery hands-on: set up a simple task, run the worker, see async execution

---

## Concepts to Study

### Celery + Redis (async job processing)

**What it is:**
Celery is a background task runner. Redis is the message queue between Flask and Celery.

**The 3 pieces:**
```
Flask (waiter)  →  Redis (ticket board)  →  Celery worker (kitchen)
"here's a job"     "task #7 waiting"        "running the job"
```

**Why we use it in Educlouds:**
Docker jobs can take several minutes. Without Celery, the browser freezes waiting.
With Celery, Flask responds immediately and the worker runs the job in the background.

**How to run it locally (3 terminal windows):**
```bash
# Window 1 — Flask app
python app.py

# Window 2 — Celery worker
celery -A app worker

# Window 3 — Redis
redis-server
```

**The key line of code:**
```python
# WITHOUT Celery (blocks browser for minutes)
run_docker()

# WITH Celery (returns immediately, runs in background)
run_docker.delay()
```

`.delay()` is how you hand a task to Celery.

**Interview questions to prepare:**
- "How would you handle a long running task in a web app?"
- "What's the difference between sync and async processing?"
- "What happens if the Celery worker crashes mid-job?"
- "How does the user know when their job is done?"

**Your answers:**
- Why Celery? → "Docker jobs take minutes. Celery decouples job submission from execution so Flask stays responsive."
- Worker crashes? → "Celery has retry logic. Job stays in Redis queue and status is tracked in DB."
- How does borrower know? → "Dashboard polls DB for status. Celery updates status to done/error when finished."

**The one sentence that impresses interviewers:**
> "I used Celery to decouple job submission from job execution, so the platform stays responsive regardless of how long the compute job takes."

---

## Session Log

### Session 1
- Explored full codebase and identified all bugs and gaps
- Fixed Bug 1: `list.py` field references corrected
- Defined Phase 1–4 upgrade roadmap

### Session 2
- Fixed Bug 2: FK type mismatch + redesigned schema (5 tables → 3)
- Fixed Bug 3: SSH credentials moved to environment variables
- Fixed Bug 4: removed duplicate routes and templates
- Committed Phase 1, opened PR, merged into main
- Started Phase 2: rewrote matching.py and wired into requests.py
- Next: lender dashboard

### Reminder for Phase 3
- Build ML model that predicts job runtime based on workload, dependencies, python version, resource type
- Use predictions to make matching smarter (pick lender most likely to finish fastest)
- Show predicted runtime to borrower at submission time
