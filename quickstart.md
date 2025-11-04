# DevUp - Quick Start Guide

Here are the instructions for building, running, and demonstrating the DevUp project.

---

## Prerequisites

* Docker & Docker Compose installed
* Python 3.11+
* pip

---

## Setup

1. **Clone the repository**:

```bash
# If from Git repository
git clone https://github.com/deenooc/devup.git
cd devup

# OR if from zip file
unzip devup.zip
cd devup
```

2. **Create a Python virtual environment** (optional but recommended):

```bash
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

3. **Configure environment variables**:

```bash
./devup.py init
```

`.env` contains:

```dotenv
# MySQL
DB_USER=root
DB_PASSWORD=admin123
DB_NAME=devup
MYSQL_PORT=3306

# Mock API
MOCK_API_PORT=6000
```

---

## Start the Environment

Build and start Docker containers:

```bash
./devup.py up
```

* MySQL will be available at `localhost:3306`
* Mock API will be available at `http://localhost:6000`

---

## Check Status

Run:

```bash
./devup.py status
```

This will:

* Show `docker-compose ps`
* Check `mock_api` health immediately via HTTP
* Ping MySQL via Docker

Sample output:

```
NAME               IMAGE            SERVICE    STATUS
devup-mock_api-1   devup-mock_api   mock_api   Up 30s (healthy)
devup-mysql-1      mysql:8.0        mysql      Up 2m (healthy)

✅ mock_api at http://localhost:6000/health is responding
Attempting mysql ping via docker-compose exec
mysqld is alive
```

---

## Run Smoke Tests

Verify services are wired correctly:

```bash
./devup.py test
```

* Tests `mock_api` echo endpoint
* Pings MySQL

---

## Tear Down

Stop and remove containers:

```bash
./devup.py clean
```

---

## Developer Notes

* `mock_api` runs Flask on port 5000 inside the container; mapped to host via `MOCK_API_PORT`.
* MySQL uses `mysql_native_password` for simplicity; caching_sha2_password recommended for production.
* Healthchecks ensure services are ready before `devup.py` reports them healthy.
* Add new mock services easily by extending `docker-compose.yml` and updating `devup.py` health/test commands.
