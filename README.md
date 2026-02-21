# AI Risk Engine

FastAPI-based service for AI risk, compliance, and governance. This repository contains the application code, configuration, and documentation.

## Quick start

1. **Create and activate a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**  
   Create a `.env` file in the project root with at least:
   - `JWT_SECRET` (min 32 characters)
   - `DATABASE_URL`
   - `REDIS_URL`
   - `RABBITMQ_URL`

4. **Run the application**
   ```bash
   uvicorn app.main:app --reload
   ```

5. **Check health**
   ```bash
   curl http://127.0.0.1:8000/health
   ```

For detailed steps (including optional Docker Compose for Postgres/Redis/RabbitMQ), see **[docs/TESTING_AND_LOCAL_SETUP.md](docs/TESTING_AND_LOCAL_SETUP.md)**.

## Project layout

- **`app/`** — Application code: FastAPI app, API routers (health; events module present), config, domain, and infrastructure.
- **`docs/`** — Documentation (structure, testing, architecture).
- **`tests/`** — Unit, integration, load, and workflow tests (structure in place).
- **`docker-compose.yml`** — Local Postgres, RabbitMQ, and Redis. **`schema.sql`** — PostgreSQL schema dump (reference).

| Doc | Description |
|-----|-------------|
| [docs/TESTING_AND_LOCAL_SETUP.md](docs/TESTING_AND_LOCAL_SETUP.md) | Full local setup and testing (venv → health check) |
| [docs/FOLDER_AND_FILE_STRUCTURE.md](docs/FOLDER_AND_FILE_STRUCTURE.md) | Folder and file tree reference |
| [docs/PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md) | Project structure guide and conventions |

## API

- **Health:** `GET /health` — Returns status, environment, and version.
- **Interactive docs:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) when the server is running.

## License

See repository or project documentation for license information.
