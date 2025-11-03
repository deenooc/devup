# DevUp — Local Dev Onboarding Bootstrapper

**Goal:** reduce time-to-first-success for new devs by automating local environment setup, basic mocks, health checks and a smoke test.  
Stack: Python 3, Docker Compose, MySQL, Flask (mock API).

## Prerequisites

Install these on your machine:

- Docker (Engine) — https://docs.docker.com/get-docker/
- Docker Compose CLI (v2 recommended) — often included with Docker Desktop or available as `docker compose` / `docker-compose`.
- Python 3.11+
- `pip` (Python package manager)
- (optional) Git


## Quick overview

Commands are provided by `devup.py` (Click CLI):
```
./devup.py init       # create .env from .env.example
./devup.py up         # start docker-compose (default detached)
./devup.py status     # check Docker Compose and health endpoints
./devup.py test       # run smoke tests (mock API + mysql ping)
./devup.py clean      # docker-compose down -v
./devup.py add-mock NAME  # scaffold small mock service
```


## ✨ Core Features
| Capability | Description |
|-------------|-------------|
| `.env` generator | `devup.py init` copies `.env.example` → `.env` |
| Environment bootstrap | One command: `devup.py up` |
| Mock API service | Simple Flask service with `/health` & `/echo` |
| Health checks | Verify MySQL + mock API are alive |
| Smoke tests | Send a test request and ping DB |
| Teardown | `devup.py clean` removes containers & volumes |
| Logs | Stream container logs easily |
| Extensible | Add new mock services, later integrate into CI/CD |

---


## Setup

1. Clone repo:
```bash
git clone https://github.com/deenooc/devup
cd devup
```

2. Create a virtualenv and install dev dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3.	Initialise the env file:
```bash
./devup.py init
```

This copies .env.example → .env. Edit .env if you need non-default ports/passwords.

4.	Start environment:
```bash
./devup.py up
```

5.	Check status (wait ~5-10 seconds for services to initialise):
```bash
./devup.py status
```

6.	Run smoke tests:
```bash
./devup.py test
```
🧪 Smoke Test Output:
```
[OK] mock_api echo test passed
mysqladmin: ping: connected
```
✅ If you see both lines, your environment works!

7.	Tear down when done:
```bash
./devup.py clean
```


## What each service does
- mysql — local MySQL server (data persisted in Docker volume mysql-data).
- mock_api — tiny Flask app that exposes /health and /echo endpoints to simulate downstream services.

Ports are forwarded to the host via env vars in .env (defaults: MySQL 3306, mock API 6000).

## How this helps onboarding
- Single command (./devup.py up) boots a reproducible environment matching core dependencies.
- .env.example documents required environment variables and sensible defaults.
- ./devup.py status provides a simple single place to check readiness.
- ./devup.py test runs a smoke test so newcomers can confirm their setup works.

## Extensibility / Next steps (suggested)
- Add a small “service template” to bootstrap new microservices (includes Dockerfile, CI job stub).
- Add GitHub Action to ./devup.py test periodically to ensure onboarding remains healthy.
- Replace mock_api with WireMock or Pact for contract testing in advanced flows.
- Add a simple web UI that shows current status of local services (optional).


## Troubleshooting
-	If ports conflict, change .env values and restart with ./devup.py clean then ./devup.py up.
-	If docker-compose is not found, try docker compose (note: modify DOCKER_COMPOSE env var if needed).
-	If MySQL doesn’t start first time, wait 10–20s and re-run ./devup.py status.   

## Measuring success
-	Time-to-first-success: manually time a new dev from clone → smoke test success.
-	Track issues reported in onboarding docs or via a short survey after running through the flow.

---

## 3) How to get running locally — commands (exact)

Assuming you put the files in `devup/`:

```bash
cd devup

# (optional) venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# init env file
./devup.py init

# start environment
./devup.py up

# wait ~5-10 seconds for services to initialize, then check status
./devup.py status

# run smoke tests
./devup.py test

# teardown when done
./devup.py clean  
```

If docker-compose is docker compose (no dash), set an env var before running:
```bash
export DOCKER_COMPOSE="docker compose"
./devup.py up
```

## 4) Design notes, tradeoffs & rationale (short)
- Why Docker Compose? Lightweight, fast, perfect for local dev.
- Why Python CLI? You’re comfortable with Python; Click provides a very small, readable CLI that demonstrates scripting and UX.
- Mocks vs real dependencies: Mocks are fast and reduce resource usage; they should be contract-friendly to add later.
- Simplicity: This prototype focuses on the core pain (onboarding & local reproducible environment) and intentionally leaves CI integration and multi-service orchestration for follow-up.

## 5) Test plan & acceptance criteria

A successful demo should show:
1.	Clone + pip install + ./devup.py init executes without errors.
2.	./devup.py up brings up MySQL and mock_api.
3.	./devup.py status reports mock_api health OK and runs mysql ping.
4.	./devup.py test runs mock API echo successfully.
5.	./devup.py clean removes containers and volumes.
