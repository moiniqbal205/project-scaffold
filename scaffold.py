#!/usr/init/env python3
import os
import subprocess
import sys
import socket
import time
from pathlib import Path

def find_available_port(start_port):
    """Scan sequentially starting from start_port until an available port is found."""
    port = start_port
    while port < 65535:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", port))
                return port
            except socket.error:
                port += 1
    raise RuntimeError("No available ports found on localhost.")

def run_cmd(cmd, cwd=None, check=True):
    """Helper to run shell commands with live output."""
    print(f"\n⚡ Running: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    result = subprocess.run(cmd, cwd=cwd, shell=isinstance(cmd, str), check=check)
    return result

def run_cmd_with_retry(cmd, cwd=None, retries=5, delay=4):
    """Run a command with retries for transient database startup/auth errors."""
    for attempt in range(1, retries + 1):
        print(f"\n⚡ Running (Attempt {attempt}/{retries}): {' '.join(cmd) if isinstance(cmd, list) else cmd}")
        result = subprocess.run(cmd, cwd=cwd, shell=isinstance(cmd, str), check=False)
        if result.returncode == 0:
            return result
        if attempt == retries:
            print(f"\n❌ Command failed after {retries} attempts.")
            sys.exit(1)
        print(f"⚠️ Database or container still initializing. Retrying in {delay} seconds...")
        time.sleep(delay)

def check_docker():
    """Verify Docker is installed and the daemon is running."""
    print("Checking Docker status...")
    try:
        subprocess.run(["docker", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        subprocess.run(["docker", "compose", "version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        res = subprocess.run(["docker", "info"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if res.returncode != 0:
            print("\n❌ Error: Docker daemon is not running.")
            print("Please open Docker Desktop and wait for it to start, then re-run this script.")
            sys.exit(1)
        print("✔ Docker is running.")
    except (subprocess.SubprocessError, FileNotFoundError):
        print("\n❌ Error: Docker or Docker Compose is not installed or not in your PATH.")
        sys.exit(1)

def main():
    # 1. Prompt for Project Name
    project_name = input("Enter project name (e.g., my-prototype): ").strip()
    if not project_name:
        print("Project name cannot be empty.")
        sys.exit(1)

    project_slug = project_name.lower().replace(" ", "-")
    db_name = project_slug.replace("-", "_")
    root_dir = Path(project_slug)

    if root_dir.exists():
        print(f"\n❌ Error: Directory '{project_slug}' already exists.")
        sys.exit(1)

    check_docker()

    # 2. Automatically detect and assign available ports for API and Frontend
    print("\n🔍 Checking port availability...")
    api_port = find_available_port(8000)
    frontend_port = find_available_port(5173)

    if api_port != 8000:
        print(f"⚠️ Port 8000 is in use. Assigned API port: {api_port}")
    else:
        print(f"✔ API port 8000 is available.")

    if frontend_port != 5173:
        print(f"⚠️ Port 5173 is in use. Assigned Frontend port: {frontend_port}")
    else:
        print(f"✔ Frontend port 5173 is available.")

    print(f"\n📂 Creating project directories for '{project_name}'...")
    docker_php_dir = root_dir / "docker" / "php"
    backend_dir = root_dir / "backend"
    frontend_dir = root_dir / "frontend"
    frontend_src_dir = frontend_dir / "src"

    docker_php_dir.mkdir(parents=True, exist_ok=True)
    backend_dir.mkdir(parents=True, exist_ok=True)
    frontend_src_dir.mkdir(parents=True, exist_ok=True)

    # 3. Write docker/php/Dockerfile
    print("Creating docker/php/Dockerfile...")
    dockerfile_content = """FROM php:8.4-cli-bookworm
RUN apt-get update \\
    && apt-get install -y --no-install-recommends \\
       git unzip libicu-dev libonig-dev libpq-dev libzip-dev \\
    && docker-php-ext-install \\
       bcmath intl mbstring pdo_pgsql zip \\
    && rm -rf /var/lib/apt/lists/*

COPY --from=composer:2 /usr/bin/composer /usr/bin/composer
WORKDIR /app
"""
    (docker_php_dir / "Dockerfile").write_text(dockerfile_content)

    # 4. Write compose.yaml using the dynamically assigned ports and sanitized db name
    print("Creating compose.yaml...")
    compose_content = f"""services:
  api:
    build:
      context: ./docker/php
    working_dir: /app
    volumes:
      - ./backend:/app
    ports:
      - "{api_port}:8000"
    command: php artisan serve --host=0.0.0.0 --port=8000
    depends_on:
      db:
        condition: service_healthy

  frontend:
    image: node:22-alpine
    working_dir: /app
    volumes:
      - ./frontend:/app
      - frontend_node_modules:/app/node_modules
    ports:
      - "{frontend_port}:5173"
    command: npm run dev -- --host 0.0.0.0
    depends_on:
      - api

  db:
    image: postgres:17-alpine
    environment:
      POSTGRES_DB: {db_name}
      POSTGRES_USER: {db_name}
      POSTGRES_PASSWORD: local_dev_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U {db_name} -d {db_name}"]
      interval: 3s
      timeout: 3s
      retries: 15

volumes:
  postgres_data:
  frontend_node_modules:
"""
    (root_dir / "compose.yaml").write_text(compose_content)

    # 5. Build API container & Generate Laravel 12
    print("\n🚀 Building API container and generating Laravel 12 project...")
    run_cmd(["docker", "compose", "build", "api"], cwd=root_dir)
    run_cmd(["docker", "compose", "run", "--rm", "--no-deps", "api", "composer", "create-project", "laravel/laravel:^12.0", "."], cwd=root_dir)

    # 6. Configure backend/.env
    print("Configuring backend/.env...")
    env_file = backend_dir / ".env"
    if env_file.exists():
        env_content = env_file.read_text()
        
        # Strip out any existing DB_ configuration lines to prevent duplicates
        lines = []
        for line in env_content.splitlines():
            if not line.startswith(("DB_CONNECTION", "DB_HOST", "DB_PORT", "DB_DATABASE", "DB_USERNAME", "DB_PASSWORD", "APP_URL")):
                lines.append(line)
        
        # Append clean, correct Docker PostgreSQL configuration
        clean_env = "\n".join(lines) + f"""
APP_URL=http://localhost:{api_port}

DB_CONNECTION=pgsql
DB_HOST=db
DB_PORT=5432
DB_DATABASE={db_name}
DB_USERNAME={db_name}
DB_PASSWORD=local_dev_password
"""
        env_file.write_text(clean_env.strip() + "\n")

    # 7. Scaffold Vue 2 Frontend
    print("\n📦 Initializing and configuring Vue 2.7 frontend...")
    run_cmd(["docker", "compose", "run", "--rm", "--no-deps", "frontend", "npm", "init", "-y"], cwd=root_dir)
    run_cmd(["docker", "compose", "run", "--rm", "--no-deps", "frontend", "npm", "install", "vue@2.7.16"], cwd=root_dir)
    run_cmd(["docker", "compose", "run", "--rm", "--no-deps", "frontend", "npm", "install", "-D", "vite@6", "@vitejs/plugin-vue2@2.3.3"], cwd=root_dir)
    run_cmd(["docker", "compose", "run", "--rm", "--no-deps", "frontend", "npm", "pkg", "set", "type=module", "scripts.dev=vite", "scripts.build=vite build"], cwd=root_dir)

    # Write frontend/vite.config.js
    print("Creating frontend/vite.config.js...")
    vite_config = """import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue2'

export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: {
      '/api': 'http://api:8000',
    },
  },
})
"""
    (frontend_dir / "vite.config.js").write_text(vite_config)

    # Write frontend/index.html
    print("Creating frontend/index.html...")
    index_html = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{project_name}</title>
  </head>
  <body>
    <div id="app"></div>
    <script type="module" src="/src/main.js"></script>
  </body>
</html>
"""
    (frontend_dir / "index.html").write_text(index_html)

    # Write frontend/src/main.js
    print("Creating frontend/src/main.js...")
    main_js = """import Vue from 'vue'
import App from './App.vue'

new Vue({
  render: (h) => h(App),
}).$mount('#app')
"""
    (frontend_src_dir / "main.js").write_text(main_js)

    # Write frontend/src/App.vue
    print("Creating frontend/src/App.vue...")
    app_vue = """<template>
  <main>
    <h1>App Prototype</h1>
    <p>API status: {{ apiStatus }}</p>
  </main>
</template>

<script>
export default {
  data() {
    return { apiStatus: 'Checking…' }
  },

  async mounted() {
    try {
      const response = await fetch('/api/health')
      if (!response.ok) throw new Error(`HTTP ${response.status}`)

      const result = await response.json()
      this.apiStatus = result.status
    } catch (error) {
      this.apiStatus = `Unavailable: ${error.message}`
    }
  },
}
</script>
"""
    (frontend_src_dir / "App.vue").write_text(app_vue)

    # 8. Start Stack & Initialize API/Migrations
    print("\n🐳 Ensuring a clean stack and starting Docker containers...")
    run_cmd(["docker", "compose", "down", "-v", "--remove-orphans"], cwd=root_dir, check=False)
    run_cmd(["docker", "compose", "up", "-d"], cwd=root_dir)

    print("\nInstalling API configuration...")
    run_cmd(["docker", "compose", "exec", "api", "php", "artisan", "install:api", "--no-interaction"], cwd=root_dir, check=False)

    print("\nRunning database migrations with auto-retry...")
    run_cmd_with_retry(["docker", "compose", "exec", "api", "php", "artisan", "migrate", "--no-interaction"], cwd=root_dir)

    # 9. Add health route to backend/routes/api.php
    print("Adding health check route to backend/routes/api.php...")
    api_routes_path = backend_dir / "routes" / "api.php"
    if api_routes_path.exists():
        route_content = api_routes_path.read_text()
        health_route = "\nRoute::get('/health', fn () => response()->json(['status' => 'ok']));\n"
        if "health" not in route_content:
            api_routes_path.write_text(route_content + health_route)

    print(f"\n✨ Success! Your project '{project_name}' has been successfully scaffolded.")
    print(f"👉 Cd into your project: cd {project_slug}")
    print(f"🌍 Frontend URL: http://localhost:{frontend_port}")
    print(f"🔌 API URL: http://localhost:{api_port}")

if __name__ == "__main__":
    main()