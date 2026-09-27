#!/usr/bin/env python3
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

    # 2. Automatically detect and assign available ports for App and Database
    print("\n🔍 Checking port availability...")
    app_port = find_available_port(8000)

    if app_port != 8000:
        print(f"⚠️ Port 8000 is in use. Assigned App port: {app_port}")
    else:
        print(f"✔ App port 8000 is available.")

    print(f"\n📂 Creating project directories for '{project_name}'...")
    docker_php_dir = root_dir / "docker" / "php"
    backend_dir = root_dir / "backend"

    docker_php_dir.mkdir(parents=True, exist_ok=True)
    backend_dir.mkdir(parents=True, exist_ok=True)

    # 3. Write docker/php/Dockerfile (Node + PHP 8.4 setup for Inertia/Vite compiling inside container)
    print("Creating docker/php/Dockerfile...")
    dockerfile_content = """FROM php:8.4-cli-bookworm
RUN apt-get update \\
    && apt-get install -y --no-install-recommends \\
       git unzip libicu-dev libonig-dev libpq-dev libzip-dev curl \\
    && docker-php-ext-install \\
       bcmath intl mbstring pdo_pgsql zip \\
    && rm -rf /var/lib/apt/lists/*

# Install Node.js (LTS) for building Vite / shadcn-vue assets
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \\
    && apt-get install -y nodejs

COPY --from=composer:2 /usr/bin/composer /usr/bin/composer
WORKDIR /app
"""
    (docker_php_dir / "Dockerfile").write_text(dockerfile_content)

    # 4. Write compose.yaml for Laravel + PostgreSQL + Vite Hot Module Reload
    print("Creating compose.yaml...")
    compose_content = f"""services:
  app:
    build:
      context: ./docker/php
    working_dir: /app
    volumes:
      - ./backend:/app
    ports:
      - "{app_port}:8000"
      - "5173:5173"
    command: php artisan serve --host=0.0.0.0 --port=8000
    depends_on:
      db:
        condition: service_healthy

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
"""
    (root_dir / "compose.yaml").write_text(compose_content)

    # 5. Build Container & Scaffold Official Laravel Vue Starter Kit via Composer
    print("\n🚀 Building app container and scaffolding Laravel 12 + Vue 3 starter kit...")
    run_cmd(["docker", "compose", "build", "app"], cwd=root_dir)
    
    # Create fresh Laravel project skeleton
    run_cmd(["docker", "compose", "run", "--rm", "app", "composer", "create-project", "laravel/laravel:^12.0", "."], cwd=root_dir)
    
    # Install Laravel Vue Starter Kit (Inertia + Vue 3 + Tailwind + shadcn-vue baseline)
    print("\n📦 Installing Laravel Vue Starter Kit dependencies...")
    run_cmd(["docker", "compose", "run", "--rm", "app", "composer", "require", "laravel/breeze", "--dev"], cwd=root_dir)
    run_cmd(["docker", "compose", "run", "--rm", "app", "php", "artisan", "breeze:install", "vue", "--no-interaction"], cwd=root_dir)

    # 6. Configure backend/.env with robust database connection parameters
    print("Configuring backend/.env...")
    env_file = backend_dir / ".env"
    if env_file.exists():
        env_content = env_file.read_text()
        
        # Clear out default values and inject Docker config reliably
        lines = []
        for line in env_content.splitlines():
            if not line.startswith(("DB_CONNECTION", "DB_HOST", "DB_PORT", "DB_DATABASE", "DB_USERNAME", "DB_PASSWORD", "APP_URL")):
                lines.append(line)
        
        clean_env = "\n".join(lines) + f"""
APP_URL=http://localhost:{app_port}

DB_CONNECTION=pgsql
DB_HOST=db
DB_PORT=5432
DB_DATABASE={db_name}
DB_USERNAME={db_name}
DB_PASSWORD=local_dev_password
"""
        env_file.write_text(clean_env.strip() + "\n")

    # 7. Start Stack & Initialize Migrations and Node Build Assets
    print("\n🐳 Starting Docker containers and running database migrations...")
    run_cmd(["docker", "compose", "up", "-d"], cwd=root_dir)

    print("\nRunning database migrations with auto-retry...")
    run_cmd_with_retry(["docker", "compose", "exec", "app", "php", "artisan", "migrate", "--no-interaction"], cwd=root_dir)

    print("\nInstalling frontend packages and building assets via npm inside container...")
    run_cmd(["docker", "compose", "exec", "app", "npm", "install"], cwd=root_dir)
    run_cmd(["docker", "compose", "exec", "app", "npm", "run", "build"], cwd=root_dir)

    print(f"\n✨ Success! Your modern Vue 3 + Laravel project '{project_name}' has been successfully scaffolded.")
    print(f"👉 Cd into your project: cd {project_slug}")
    print(f"🌍 Application URL: http://localhost:{app_port}")
    print(f"💡 To run frontend hot-reloading development assets: docker compose exec app npm run dev")

if __name__ == "__main__":
    main()