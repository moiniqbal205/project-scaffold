# Project Scaffold

A robust, automated CLI-based scaffolding tool that provisions a fully-containerized modern web development environment combining **Laravel 12 (PHP 8.4)**, **PostgreSQL 17**, and **Vue 3 with Inertia.js, Tailwind CSS, and shadcn-vue** using **Docker Compose**.

---

## 🛠️ Tech Stack

- **Backend & Architecture:** Laravel 12 monolith running on PHP 8.4 CLI with server-side routing via **Inertia.js**.
- **Database:** PostgreSQL 17 optimized with container health checks and automatic persistent volume mapping.
- **Frontend Ecosystem:** Vue 3, Vite, Tailwind CSS, pre-configured with the **shadcn-vue** component library setup.
- **Orchestration:** Docker & Docker Compose with dynamic application and Vite port allocation.

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

3. Enter your desired project name when prompted (e.g., `my-prototype`). It will be sanitized to alphanumeric characters.
4. The script will automatically:
* Scan for available localhost ports for the app and Vite.
* Generate the isolated project structure.
* Build the Docker images and clone the official Laravel Vue Starter Kit.
* Configure local development environment variables (including local database credentials).
* Run database migrations and compile initial build assets.



---

## 📂 Project Structure

Once scaffolded, your project directory will look like this:

```text
my-prototype/
├── backend/             # Laravel 12 + Vue 3 source code (Inertia pages, controllers, components)
├── docker/              # Custom Dockerfiles (PHP 8.4 + Node.js LTS)
└── compose.yaml         # Docker Compose multi-service definition

````

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

- **Run Artisan commands:**

```bash
docker compose exec app php artisan [command]

```

- **Run hot-reloading frontend development assets (Vite):**
  _(Keep this running in a separate terminal window during development)_

```bash
# Check your script terminal output or backend/.env for your assigned VITE_PORT
docker compose exec app npm run dev -- --host 0.0.0.0 --port [VITE_PORT]

```

---

## 🧩 Building with `shadcn-vue`

Because this stack utilizes Laravel's new official Vue Starter Kit, the `shadcn-vue` baseline is ready out-of-the-box.

1. **Add desired components (e.g., Button, Table, Dialog):**

```bash
docker compose exec app npx shadcn-vue@latest add button

```

2. **Use the components in your Inertia pages (`backend/resources/js/Pages`):**
   Components are scaffolded into `backend/resources/js/components/ui/` allowing you total ownership over their styling.

---

## 🌍 Accessing Your App

- **Main Application Server:** Open the application URL provided at the end of the scaffolding run (e.g., [http://localhost:8001](http://localhost:8001)). Always view your application here in the browser.
- **Note on Security:** The `compose.yaml` and `.env` files hardcode standard passwords (`local_dev_password`) for frictionless local development. Do not reuse these files as-is for production deployment.
