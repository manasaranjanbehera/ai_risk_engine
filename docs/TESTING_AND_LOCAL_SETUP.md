# Testing and Local Setup

This guide walks you through setting up a local environment and testing the AI Risk Engine application, from creating a virtual environment to verifying the health router.

**Last updated:** February 19, 2025

---

## Prerequisites

- **Python 3.11+** (3.12 or 3.14 recommended)
- **pip**
- (Optional) **Docker & Docker Compose** — for running Postgres, Redis, and RabbitMQ locally

---

## 1. Clone and enter the project

```bash
cd /path/to/ai_risk_engine
```

---

## 2. Create a virtual environment

Create a venv in the project root (e.g. `venv` or `.venv`). The project `.gitignore` ignores both `venv/` and `.venv/`.

**Linux / macOS:**

```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows (Command Prompt):**

```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**Windows (PowerShell):**

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

You should see `(venv)` (or similar) in your shell prompt when the environment is active.

---

## 3. Install dependencies

From the project root with the venv activated:

```bash
pip install -r requirements.txt
```

This installs FastAPI, uvicorn, pydantic-settings, and the rest of the dependencies listed in `requirements.txt`.

---

## 4. Environment variables

The app loads configuration from environment variables and from a `.env` file in the project root. **Do not commit `.env`**; it is listed in `.gitignore`. You can copy `.env.example` to `.env` and fill in the values.

Required variables (see `app/config/settings.py`):

| Variable | Description | Example (local) |
|----------|-------------|-----------------|
| `JWT_SECRET` | Secret for JWT; must be at least 32 characters | `your-super-secret-key-at-least-32-chars-long` |
| `DATABASE_URL` | PostgreSQL connection URL | `postgresql+asyncpg://compliance_user:compliance_pass@localhost:5432/compliance_db` |
| `REDIS_URL` | Redis connection URL | `redis://localhost:6379/0` |

Optional (defaults in parentheses):

- `ENVIRONMENT` — `dev` \| `test` \| `prod` (default: `dev`)
- `DEBUG` — `true` \| `false` (default: `false`)
- `LOG_LEVEL` — `DEBUG` \| `INFO` \| `WARNING` \| `ERROR` (default: `INFO`)

Create a `.env` file in the project root, for example:

```env
JWT_SECRET=your-super-secret-key-at-least-32-chars-long
DATABASE_URL=postgresql+asyncpg://compliance_user:compliance_pass@localhost:5432/compliance_db
REDIS_URL=redis://localhost:6379/0
ENVIRONMENT=dev
LOG_LEVEL=INFO
```

To use the default Postgres and Redis from `docker-compose.yml`, start the stack first (see step 5). The health endpoint does **not** connect to the database or Redis; it only reads settings. So the app will start and serve `/health` even if Postgres/Redis are not running, as long as the URLs are set (they are only used when code actually connects).

---

## 5. (Optional) Start local services with Docker Compose

If you want a full local stack (Postgres, RabbitMQ, Redis) as defined in `docker-compose.yml`:

```bash
docker-compose up -d
```

Then use the same credentials in `.env` as in the compose file (e.g. `compliance_user` / `compliance_pass` / `compliance_db` for Postgres, and `redis://localhost:6379/0` for Redis). If you only need to hit the health router, you can skip this step and use the `.env` above; the app will start and `/health` will respond.

---

## 6. Run the application

From the project root with the venv activated:

```bash
uvicorn app.main:app --reload
```

- `--reload` restarts the server when you change code (useful during development).
- Default host is `127.0.0.1` and port is `8000`.

You should see log output indicating the server is running, e.g.:

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process ...
```

---

## 7. Check the health router locally

The health router is mounted at **`GET /health`** and returns application status, environment, and version.

**Using curl:**

```bash
curl http://127.0.0.1:8000/health
```

Expected response (example):

```json
{
  "status": "ok",
  "environment": "dev",
  "version": "0.1.0"
}
```

**Using a browser:** open [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health).

**Optional headers:** the app supports `X-Correlation-ID` and `X-Tenant-ID`; they are logged and echoed back in the response. Example:

```bash
curl -H "X-Correlation-ID: my-test-123" -H "X-Tenant-ID: tenant-a" http://127.0.0.1:8000/health
```

---

## 8. Interactive API docs

With the server running:

- **Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

You can call `/health` (and other routes) from the Swagger UI.

---

## 9. Run tests (when added)

The project has test directories under `tests/` (`unit/`, `integration/`, `load/`, `workflow/`). When tests are added, you can run them with pytest from the project root:

```bash
# Install dev dependencies if you have a dev requirements file
# pip install -r requirements-dev.txt

pytest
# Or only unit tests:
pytest tests/unit/
```

---

## Quick reference

| Step | Command / action |
|------|-------------------|
| Create venv | `python3 -m venv venv` |
| Activate venv (Unix) | `source venv/bin/activate` |
| Install deps | `pip install -r requirements.txt` |
| Configure | Create `.env` with `JWT_SECRET`, `DATABASE_URL`, `REDIS_URL` |
| Optional services | `docker-compose up -d` |
| Run app | `uvicorn app.main:app --reload` |
| Health check | `curl http://127.0.0.1:8000/health` |
| API docs | http://127.0.0.1:8000/docs |

---

## Related documentation

- [FOLDER_AND_FILE_STRUCTURE.md](./FOLDER_AND_FILE_STRUCTURE.md) — Full project tree and file roles
- [PROJECT_STRUCTURE.md](./PROJECT_STRUCTURE.md) — Project layout and conventions
