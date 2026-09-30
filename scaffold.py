#!/usr/bin/env python3
import os
import subprocess
import sys
import socket
import time
import re
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
            sys.exit(1)
        print("✔ Docker is running.")
    except (subprocess.SubprocessError, FileNotFoundError):
        print("\n❌ Error: Docker or Docker Compose is not installed or not in your PATH.")
        sys.exit(1)

def configure_vite_hmr(vite_config_path):
    """Inject Docker HMR server settings into app/vite.config.ts if missing."""
    if not vite_config_path.exists():
        print(f"⚠️ Warning: {vite_config_path} not found. Skipping Vite HMR configuration.")
        return

    content = vite_config_path.read_text()
    if "strictPort:" in content:
        return

    server_block = """    server: {
        host: '0.0.0.0',
        strictPort: true,
        hmr: {
            host: 'localhost',
        },
    },"""

    # Inject server block into defineConfig({ ... })
    if "defineConfig({" in content:
        updated_content = content.replace("defineConfig({", f"defineConfig({{\n{server_block}")
        vite_config_path.write_text(updated_content)
        print("✔ Updated app/vite.config.ts with Docker HMR configuration.")

def main():
    # 1. Prompt and strictly validate Project Name
    project_name = input("Enter project name (e.g., my-prototype): ").strip()
    if not project_name:
        print("Project name cannot be empty.")
        sys.exit(1)

    project_slug = re.sub(r'[^a-z0-9]+', '-', project_name.lower()).strip('-')
    if not project_slug:
        print("❌ Error: Invalid project name. Please use alphanumeric characters.")
        sys.exit(1)

    db_name = project_slug.replace("-", "_")
    root_dir = Path(project_slug)

    if root_dir.exists():
        print(f"\n❌ Error: Directory '{project_slug}' already exists.")
        sys.exit(1)

    check_docker()

    # 2. Automatically detect and assign available ports for App and Vite
    print("\n🔍 Checking port availability...")
    app_port = find_available_port(8000)
    vite_port = find_available_port(5173)

    print(f"✔ App port assigned: {app_port}")
    print(f"✔ Vite port assigned: {vite_port}")

    print(f"\n📂 Creating project directories for '{project_slug}'...")
    docker_php_dir = root_dir / "docker" / "php"
    app_dir = root_dir / "app"

    docker_php_dir.mkdir(parents=True, exist_ok=True)
    app_dir.mkdir(parents=True, exist_ok=True)

    # 3. Write docker/php/Dockerfile
    print("Creating docker/php/Dockerfile...")
    dockerfile_content = """FROM php:8.4-cli-bookworm
RUN apt-get update \\
    && apt-get install -y --no-install-recommends \\
       git unzip libicu-dev libonig-dev libpq-dev libzip-dev curl \\
    && docker-php-ext-install \\
       bcmath intl mbstring pdo_pgsql zip \\
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \\
    && apt-get install -y nodejs

COPY --from=composer:2 /usr/bin/composer /usr/bin/composer
WORKDIR /app
"""
    (docker_php_dir / "Dockerfile").write_text(dockerfile_content)

    # 4. Write compose.yaml
    print("Creating compose.yaml...")
    compose_content = f"""services:
  app:
    build:
      context: ./docker/php
    working_dir: /app
    volumes:
      - ./app:/app
    ports:
      - "{app_port}:8000"
      - "{vite_port}:{vite_port}"
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

    # 5. Build Container & Install Pinned Laravel Vue Starter Kit
    print("\n🚀 Building app container and installing Laravel Vue Starter Kit (v1.0.2)...")
    run_cmd(["docker", "compose", "build", "app"], cwd=root_dir)
    
    # Run with --no-deps to avoid spinning up PostgreSQL unnecessarily during file generation
    run_cmd([
        "docker", "compose", "run", "--rm", "--no-deps", "app",
        "composer", "create-project", "laravel/vue-starter-kit", ".", "1.0.2"
    ], cwd=root_dir)

    # 6. Configure app/.env and APP_KEY verification
    print("Configuring app/.env...")
    env_file = app_dir / ".env"
    env_example = app_dir / ".env.example"

    if not env_file.exists() and env_example.exists():
        env_file.write_text(env_example.read_text())

    if not env_file.exists():
        print("❌ Error: Neither .env nor .env.example exists in app directory.")
        sys.exit(1)

    env_content = env_file.read_text()
    
    clean_lines = [
        line for line in env_content.splitlines()
        if not re.match(r'^\s*#?\s*(DB_|APP_URL=|VITE_PORT=)', line)
    ]
    
    docker_env_block = f"""
APP_URL=http://localhost:{app_port}
VITE_PORT={vite_port}

DB_CONNECTION=pgsql
DB_HOST=db
DB_PORT=5432
DB_DATABASE={db_name}
DB_USERNAME={db_name}
DB_PASSWORD=local_dev_password
"""
    final_env = "\n".join(clean_lines).strip() + "\n" + docker_env_block
    env_file.write_text(final_env)

    # Ensure APP_KEY exists
    env_lines = env_file.read_text().splitlines()
    has_app_key = any(
        line.startswith("APP_KEY=") and line.partition("=")[2].strip().strip('"').strip("'")
        for line in env_lines
    )
    if not has_app_key:
        print("🔑 Generating application encryption key...")
        run_cmd([
            "docker", "compose", "run", "--rm", "--no-deps", "app",
            "php", "artisan", "key:generate", "--no-interaction"
        ], cwd=root_dir)

    # Configure Vite HMR in app/vite.config.ts
    configure_vite_hmr(app_dir / "vite.config.ts")

    # 7. Start Stack & Initialize Migrations and Node Build Assets
    print("\n🐳 Starting Docker containers and running database migrations...")
    run_cmd(["docker", "compose", "up", "-d"], cwd=root_dir)

    print("\nRunning database migrations with auto-retry...")
    run_cmd_with_retry(["docker", "compose", "exec", "app", "php", "artisan", "migrate", "--no-interaction"], cwd=root_dir)

    print("\nInstalling frontend packages and building assets via npm inside container...")
    run_cmd(["docker", "compose", "exec", "app", "npm", "install"], cwd=root_dir)
    run_cmd(["docker", "compose", "exec", "app", "npm", "run", "build"], cwd=root_dir)

    print(f"\n✨ Success! Your modern Vue 3 + Laravel project '{project_slug}' has been successfully scaffolded.")
    print(f"👉 Cd into your project: cd {project_slug}")
    print(f"🌍 Application URL: http://localhost:{app_port}")
    print(f"💡 To run hot-reloading frontend assets: docker compose exec app npm run dev -- --host 0.0.0.0 --port {vite_port}")

if __name__ == "__main__":
    main()