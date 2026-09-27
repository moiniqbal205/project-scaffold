Here is the updated, comprehensive `README.md` reflecting your modern architecture (**Laravel 12, Vue 3, Inertia.js, PostgreSQL 17, and Vite with shadcn-vue readiness**):

````markdown
# Project Scaffold

A robust, automated CLI-based scaffolding tool that provisions a fully-containerized modern web development environment combining **Laravel 12 (PHP 8.4)**, **PostgreSQL 17**, and **Vue 3 with Inertia.js, Tailwind CSS, and shadcn-vue ecosystem readiness** using **Docker Compose**.

---

## 🛠️ Tech Stack

- **Backend & Architecture:** Laravel 12 monolith running on PHP 8.4 CLI with server-side routing via **Inertia.js** and Laravel Sanctum configured.
- **Database:** PostgreSQL 17 optimized with container health checks and automatic persistent volume mapping.
- **Frontend Ecosystem:** Vue 3, Vite, Tailwind CSS, and full compatibility with the **shadcn-vue** component library.
- **Orchestration:** Docker & Docker Compose with dynamic port allocation and unified PHP/Node container management.

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
````

3. Enter your desired project name when prompted (e.g., `my-prototype`).
4. The script will automatically:

- Scan for available localhost ports (defaulting around `8000` for the application).
- Generate the isolated project structure.
- Build the Docker images and install backend/frontend dependencies via Composer and npm.
- Configure environment variables and database connections securely.
- Run database migrations and compile initial build assets.

---

## 📂 Project Structure

Once scaffolded, your project directory will look like this:

```text
my-prototype/
├── backend/             # Laravel 12 + Vue 3 source code (Inertia pages, controllers)
├── docker/              # Custom Dockerfiles (PHP 8.4 + Node.js LTS)
└── compose.yaml         # Docker Compose multi-service definition

```

---

## 🕹️ Day-to-Day Usage

Navigate into your newly generated project folder:

```bash
cd my-prototype

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

- **Run hot-reloading frontend development assets (Vite):**
  _(Keep this running in a separate terminal window during development)_

```bash
docker compose exec app npm run dev

```

- **Run Artisan commands:**

```bash
docker compose exec app php artisan [command]

```

---

## 🧩 Getting Started with `shadcn-vue`

Because this stack is optimized for scalable SaaS apps, CRMs, and dashboards using `shadcn-vue`, you can initialize and pull components directly into your codebase:

1. **Initialize shadcn-vue:**

```bash
docker compose exec app npx shadcn-vue@latest init

```

2. **Add desired components (e.g., Button, Table, Dialog):**

```bash
docker compose exec app npx shadcn-vue@latest add button

```

---

## 🌍 Accessing Your App

- **Main Application URL:** [http://localhost:8000](http://localhost:8000?utm_source=gemini) _(Port automatically adjusts if 8000 is occupied)_

```

```
