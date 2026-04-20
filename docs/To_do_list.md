Project Goal

Retrofit educlouds from a class project into a professional, demoable software engineering portfolio project.

Target Outcome

By the end, I should be able to say:

the app solves a clear problem
the architecture is intentional
the project runs locally in a reproducible way
the core flows work end-to-end
tests cover critical behavior
the repo looks professional
you can explain design decisions in interviews


## Milestone 0: Project Definition (Done)

Goal: decide what this project is now.

Tasks:

Write a one-paragraph product summary
Define the main user roles
Define the core workflow from request submission to result retrieval
Decide what the v1 portfolio version includes
Decide what is out of scope
Deliverables:

docs/project-scope.md
one short “in scope / out of scope” section in README
Suggested questions:

Is this a job execution platform, a resource marketplace, or both?
Will execution happen locally with Docker or on remote machines?
Is matching automatic or manual in v1?

## Milestone 1: Repo Hygiene (Done)
Goal: make the repo look like engineering work, not a class submission.

Tasks:

remove tracked junk like venv/, .DS_Store, dump.rdb
verify .gitignore is correct
add .env.example
clean dependency list if needed
make directory structure understandable
Deliverables:

clean .gitignore
.env.example
short setup section in README
Definition of done:

a new developer can clone the repo without polluted artifacts
no secrets or local machine files are committed

## Milestone 2: Configuration and Environment (Done)
Goal: separate config from code.

Tasks:

move SECRET_KEY, DB URI, upload paths, remote/worker settings to env vars
create DevelopmentConfig, TestingConfig, ProductionConfig
document required environment variables
ensure app factory loads config cleanly
Deliverables:

updated config.py
.env.example
README environment section
Definition of done:

no hard-coded secrets
app can start in dev/test/prod config modes


       Done:
       ## Milestone 2 Completed

       ### What I changed
       - Refactored `config.py` to use environment variables for secrets and infrastructure settings
       - Added `DevelopmentConfig`, `TestingConfig`, and `ProductionConfig`
       - Centralized upload and request size settings in config
       - Refactored the Flask app factory to load config first and use helper functions for setup
       - Separated startup concerns into smaller functions for readability and maintainability

       ### Why it matters
       This makes the application safer, easier to configure, and more portable across environments. It also improves startup clarity and aligns the project more closely   with common Flask engineering practices.

       ### Known limitation
       Database initialization still assumes a local SQLite workflow and should later be replaced with proper migrations.


## Milestone 3: Domain Model Redesign
Goal: fix the data model so the app is coherent.

Tasks:

list the real entities
define relationships between them
fix type mismatches like UUID/string vs integer foreign keys
decide whether borrower/lender stay as separate tables or become profiles/resources/jobs
remove dead or duplicate concepts
Recommended entities:

User
ComputeResource
JobRequest
JobRun or Execution
optional UserRole if needed
Deliverables:

ERD or simple schema diagram
revised SQLAlchemy models
migration plan
Definition of done:

every model has a clear purpose
relationships match actual product behavior
no duplicate concepts competing with each other

## Milestone 4: Database Migrations
Goal: manage schema changes professionally.

Tasks:

set up Flask-Migrate/Alembic correctly
generate initial or replacement migrations
test migration from empty DB
seed minimal reference data if needed
Deliverables:

migration files
seed script or seed command
setup instructions
Definition of done:

schema is created via migrations, not db.create_all() in app startup

## Milestone 5: Core Auth Flow
Goal: make login/register reliable and explainable.

Tasks:

review register/login/logout flows
validate inputs cleanly
improve unauthorized handling
make role assignment explicit
add tests for auth behavior
Deliverables:

stable auth routes
auth tests
documented user roles
Definition of done:

a new user can register, log in, and reach the right views without route errors

## Milestone 6: Resource Management
Goal: make the lender/provider side real.

Tasks:

define what a compute resource contains
implement create/list/update availability flow
validate fields
remove broken serializer code
decide whether public listing exists
Deliverables:

working resource CRUD for core fields
tests for creation/listing
cleaned API responses or templates
Definition of done:

a provider can add a resource and see it later
data returned matches actual model fields

## Milestone 7: Job Submission Flow
Goal: make borrower job submission correct and reproducible.

Tasks:

define allowed inputs
validate uploaded scripts
store files in a predictable structure
save dependency list cleanly
connect job submission to job records, not borrower profile records
Deliverables:

working job submission route
file storage convention
tests for happy path and invalid upload cases
Definition of done:

a borrower can submit a job and see it recorded with correct metadata

## Milestone 8: Execution Engine
Goal: make the “interesting” feature credible.

Choose one:

local Docker execution first
background queue later
Recommended order:

start with local synchronous or queued Docker execution
avoid hard-coded remote SSH in the portfolio version unless you can fully explain and reproduce it
Tasks:

design execution lifecycle: queued, running, succeeded, failed
generate runtime environment from job metadata
capture stdout/stderr
persist outputs and status changes
handle failures safely
Deliverables:

execution service/module
status update logic
output retrieval flow
Definition of done:

a submitted job can be executed in a controlled way and results can be viewed

## Milestone 9: Background Jobs
Goal: add async processing only if needed.

Tasks:

decide whether to use Celery or RQ
move execution off request/response path
configure Redis if using queue
create worker startup instructions
test the queued execution path
Deliverables:

worker process setup
queue configuration
docs for running worker locally
Definition of done:

web request submits work quickly
worker handles execution asynchronously

## Milestone 10: Testing Strategy
Goal: prove the project works.

Tasks:

set up pytest with fixtures
separate unit tests from route/integration tests
replace broken legacy tests
add tests for:
auth
resource creation
job submission
status/result retrieval
mock Docker/SSH/queue boundaries where appropriate
Deliverables:

tests/ structure
passing test suite
test instructions in README
Definition of done:

tests run locally without hanging
critical paths are covered

## Milestone 11: Error Handling and Observability
Goal: make failure paths professional.

Tasks:

replace print() with structured logging
improve error responses and flash messages
add custom error pages or handlers
log important state changes
ensure failed jobs show useful output
Deliverables:

logging configuration
cleaner error handling
documented failure cases
Definition of done:

when something fails, you can understand why without guesswork

## Milestone 12: API and Route Cleanup
Goal: make naming and contracts consistent.

Tasks:

standardize blueprint names and route naming
fix broken url_for() references
choose either HTML-first app, API-first app, or hybrid clearly
remove duplicate flows if two routes do the same thing
normalize status and response structures
Deliverables:

cleaned route map
reduced duplication
updated templates/API docs
Definition of done:

route names are predictable
no dead endpoints
no conflicting versions of the same feature

## Milestone 13: UI Refresh
Goal: make the demo usable and presentable.

Tasks:

improve navigation and information hierarchy
make status/result pages readable
make forms clearer
ensure responsive layout
keep design simple and professional
Deliverables:

improved templates
better homepage copy
screenshots or demo GIF
Definition of done:

someone can understand the app in 30 seconds from the UI

## Milestone 14: Documentation
Goal: make the repo easy to evaluate.

Tasks:

rewrite README professionally
add architecture overview
add local setup instructions
add test instructions
add demo section
add tradeoffs and future improvements
Recommended README sections:

Overview
Problem
Features
Architecture
Tech stack
Local setup
Running tests
Design decisions
Future work
Deliverables:

final README
optional docs/architecture.md
Definition of done:

recruiter/interviewer can understand the project without asking you first

## Milestone 15: Interview Preparation
Goal: turn the project into a strong talking point.

Tasks:

write 5-7 bullet points about what you changed
prepare one architecture explanation
prepare one “challenge + tradeoff” story
prepare one “what I would do next” answer
prepare one demo walkthrough
Deliverables:

docs/interview-notes.md
short project pitch
Definition of done:

you can explain the project confidently in 2 minutes and 10 minutes
Suggested Working Order

Do them in this order:

Milestone 0: Project Definition
Milestone 1: Repo Hygiene
Milestone 2: Configuration and Environment
Milestone 3: Domain Model Redesign
Milestone 4: Database Migrations
Milestone 5: Core Auth Flow
Milestone 6: Resource Management
Milestone 7: Job Submission Flow
Milestone 8: Execution Engine
Milestone 10: Testing Strategy
Milestone 12: API and Route Cleanup
Milestone 11: Error Handling and Observability
Milestone 13: UI Refresh
Milestone 14: Documentation
Milestone 15: Interview Preparation


## How To Work Each Milestone

For each milestone, follow this mini-template:

Objective
Why it matters
Current problems
Planned changes
Risks/tradeoffs
Definition of done
Notes after completion
Weekly Rhythm Suggestion

Use this if you want structure:

Day 1: inspect and plan
Day 2: implement part 1
Day 3: implement part 2
Day 4: test and clean up
Day 5: document what changed and what you learned
Important Rule

Do not work on everything at once.
Finish one milestone until it is explainable, tested, and documented enough to talk about.

If you want, next I can turn this into a clean Markdown file you can paste directly into your project docs, with checkboxes and sections.


