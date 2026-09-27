Here is a clean, comprehensive `README.md` summarizing your fully working scaffold script. You can drop this directly into your main project directory or template repository as your stable baseline.

---

# Project Scaffold

A robust, automated CLI-based scaffolding tool that provisions a fully-containerized local development environment combining **Laravel 12 (PHP 8.4)**, **PostgreSQL 17**, and **Vue 2.7 (with Vite 6)** using **Docker Compose**.

---

## 🛠️ Tech Stack

- **Backend API:** Laravel 12 running on PHP 8.4 CLI (Bookworm container) with Laravel Sanctum configured.
- **Database:** PostgreSQL 17 optimized with container health checks and automatic persistent volume mapping.
- **Frontend:** Vue 2.7 powered by Vite 6 and configured with API proxying.
- **Orchestration:** Docker & Docker Compose with dynamic port allocation and automated retry safeguards.

---

## 🚀 Getting Started

### Prerequisites

- **Docker Desktop** installed and running on your machine.
- **Python 3** installed in your system PATH.

### Running the Scaffolder

1. Place the `scaffold.py` script into your working workspace directory.
2. Run the script:

```bash
python3 scaffold.py

```

3. Enter your desired project name when prompted (e.g., `my-app`).
4. The script will automatically:

- Scan for available localhost ports (defaulting around `8000` for API and `5173` for frontend).
- Generate the isolated project structure.
- Build the Docker images and install dependencies via Composer and npm.
- Configure environment variables and database connections.
- Run database migrations safely.

---

## 📂 Project Structure

Once scaffolded, your project directory will look like this:

```text
my-app/
├── backend/             # Laravel 12 source code & API routes
├── frontend/            # Vue 2.7 + Vite source code
├── docker/              # Custom Dockerfiles (PHP 8.4)
└── compose.yaml         # Docker Compose multi-service definition

```

---

## 🕹️ Day-to-Day Usage

Navigate into your newly generated project folder:

```bash
cd my-app

```

- **Start the stack in the background:**

```bash
docker compose up -d

```

- **Stop the stack:**

```bash
docker compose down

```

- **View container logs:**

```bash
docker compose logs -f

```

- **Run Artisan commands:**

```bash
docker compose exec api php artisan [command]

```

- **Run npm commands for frontend:**

```bash
docker compose run --rm frontend npm [command]

```

---

## 🌍 Accessing Your App

- **Frontend Development Server:** [http://localhost:5173](http://localhost:5173?utm_source=gemini) _(Proxies `/api` requests straight to the backend)_
- **Backend API Health Check:** [http://localhost:8000/api/health](http://localhost:8000/api/health?utm_source=gemini)
