# Project Scope

## Project Summary
What is Educlouds? Who is it for? What problem does it solve?
Educlouds is a platform that connects personal computer owners who can provide computing resources with university students  who need additional computational power for academic work. The goal is to make high-performance computing more accessible for education, experimentation, and research. 
The platform is designed primarily for students and researchers who need temporary access to compute resources, and for resource providers who can lend spare computing capacity. Educlouds addresses the problem that many students do not have reliable access to high computational resources, even though those resources are increasingly necessary for modern education and skill development. 
## Users

### Student / Borrower
A student or researcher who needs temporary computational resources to run code, experiments or academic projects. 

### Resource Provider / Lender 
A user who contributes available compute capacity that can be used by students through the platform. 

### Admin 
A platform operator who manages users, monitors requests and ensures the system remains reliable and safe.


## Core Workflow
1. A student signs up and submits a computational request.
2. The request includes the code to run, the environment requirements, and the expected workload. 
3. The platform identifies an available compute resource that can handle the request.
4. The submitted job is executed in an isolated environment.
5. The student can monitor job status and retrieve the output after execution. 

## In Scope for Portfolio v1
List the features you will actually build.
- User Registeration and login 
- Role-based access for borrowers and lenders 
- Resource registration and listing
- Job submission with Python script upload
- Basic job execution lifecycle: queued, running, succeeded, failed 
- Result retrieval for completed jobs
- Local reproducible setup for demo purpose 
- Basic automated tests for critical flows
## Out of Scope
List features you are explicitly not building now.
- Full production-grade distributed scheduling
- Real payment processing
- Multi-tenant infrastructure at scale
- Complex marketplace pricing logic
- Full remote-host orchestration across many machines
- Enterprise-grade monitoring and security hardening

## Future Enhancements

- Direct messaging between borrowers and resource providers
- Negotiation or coordination around job requirements
- Real-time notifications for job state changes
- More advanced matching and pricing logic

## Technical Direction

For the portfolio version, Educlouds will focus on a reproducible local-first architecture. Job execution should run in a controlled local Docker-based environment before considering remote infrastructure. The platform will prioritize correctness, clarity, and demoability over large-scale cloud deployment.

## Product Principles

- On-demand access to compute resources
- Scalable design direction
- Remote accessibility
- Cost-conscious usage model for students
- Educational use as the primary purpose


## Open Questions

- Should resource matching be automatic or manual in v1?
- Should execution be synchronous at first, or moved to a background worker immediately?
- How should resource capacity be modeled in the first version?
- Should pricing remain part of the portfolio version, or be deferred as future work?


Step 1: Define first deployment scope
Decide what the first hosted release actually includes.

Recommended scope:

web app only
login/register
resource and request flows that work without remote infra
no complex remote host orchestration yet