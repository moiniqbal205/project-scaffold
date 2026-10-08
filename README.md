# Project Scaffold

A robust CLI-based scaffolding tool for rapidly provisioning a fully containerized modern Laravel/Vue development environment.

The scaffold combines **Laravel 12**, **PHP 8.4**, **PostgreSQL 17**, **Vue 3 + TypeScript**, **Inertia.js**, **Tailwind CSS 4**, and a feature-rich **shadcn-vue** component library using **Docker Compose**.

By default, the scaffold installs a curated collection of shadcn-vue components, form validation support, a local component catalogue, database migrations, frontend validation, production assets, and Laravel tests — giving new projects a highly capable starting point immediately.

---

## 🛠️ Tech Stack

- **Backend:** Laravel 12 running on PHP 8.4
- **Frontend:** Vue 3 + TypeScript
- **SPA Bridge:** Inertia.js
- **Styling:** Tailwind CSS 4
- **UI Components:** shadcn-vue using the `new-york` style
- **UI Primitives:** Reka UI
- **Icons:** Lucide Vue
- **Forms:** VeeValidate + Zod
- **Tables:** TanStack Vue Table
- **Database:** PostgreSQL 17
- **Frontend Tooling:** Vite
- **Runtime:** Node.js 22
- **Package Management:** Composer + npm
- **Orchestration:** Docker + Docker Compose

Application and Vite ports are dynamically allocated to avoid conflicts with existing local projects.

---

## 🚀 Getting Started

### Prerequisites

Only the following tools need to be installed on your host machine:

- **Docker Desktop**, installed and running
- **Python 3**, available in your system PATH

PHP, Composer, Node.js, npm, PostgreSQL, and the application runtime are handled inside Docker.

---

## Running the Scaffolder

### Option 1 — Interactive

Run:

```bash
python3 scaffold.py
```

You will be prompted for a project name:

```text
Enter project name (e.g., my-prototype): my-poc
```

The resulting project will be created in:

```text
./my-poc/
```

### Option 2 — Specify the Project Name Directly

Recommended for normal use:

```bash
python3 scaffold.py --project my-poc
```

This creates:

```text
./my-poc/
```

> **Important:** Do not use `>` to specify the project name.
>
> For example:
>
> ```bash
> python3 scaffold.py > my-poc
> ```
>
> redirects terminal output into a file named `my-poc`. It does not pass `my-poc` to the scaffolder.

---

## ⚙️ What the Scaffold Does

A normal run:

```bash
python3 scaffold.py --project my-poc
```

automatically performs the following workflow:

1. Validates and sanitizes the project name.
2. Verifies Docker and Docker Compose are available and running.
3. Finds available localhost ports for:
   - Laravel
   - Vite
4. Creates the project directory structure.
5. Generates:
   - `docker/php/Dockerfile`
   - `compose.yaml`
6. Builds the PHP 8.4 + Node.js 22 application container.
7. Installs the Laravel Vue Starter Kit pinned to:
   ```text
   laravel/vue-starter-kit v1.0.2
   ```
   providing the Laravel 12 baseline.
8. Configures:
   - `.env`
   - PostgreSQL connection
   - `APP_URL`
   - `VITE_PORT`
   - Laravel `APP_KEY`
9. Modernizes the frontend foundation to:
   - Tailwind CSS 4
   - current shadcn-vue conventions
   - Reka UI
   - lowercase component paths
10. Configures shadcn-vue using:
    ```text
    resources/js/components/ui/
    ```
11. Installs the curated shadcn-vue component collection.
12. Installs supporting component dependencies.
13. Installs VeeValidate + Zod form validation support.
14. Creates the local shadcn-vue component catalogue:
    ```text
    /shadcn-vue-components
    ```
15. Starts the Docker stack.
16. Runs Laravel database migrations.
17. Runs the Vue/TypeScript type-check.
18. Runs the production Vite build.
19. Runs the Laravel test suite.
20. Prints the generated application and component catalogue URLs.

---

## 📂 Generated Project Structure

A scaffolded project has the following top-level structure:

```text
my-poc/
├── app/
│   ├── app/
│   ├── bootstrap/
│   ├── config/
│   ├── database/
│   ├── public/
│   ├── resources/
│   │   ├── css/
│   │   │   └── app.css
│   │   └── js/
│   │       ├── components/
│   │       │   └── ui/
│   │       │       ├── accordion/
│   │       │       ├── alert/
│   │       │       ├── button/
│   │       │       ├── dialog/
│   │       │       ├── table/
│   │       │       └── ...
│   │       ├── layouts/
│   │       ├── pages/
│   │       │   ├── Welcome.vue
│   │       │   ├── Dashboard.vue
│   │       │   └── ShadcnVueComponents.vue
│   │       ├── types/
│   │       └── app.ts
│   ├── routes/
│   │   └── web.php
│   ├── components.json
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
├── docker/
│   └── php/
│       └── Dockerfile
└── compose.yaml
```

The scaffold uses a single lowercase convention:

```text
resources/js/components/
```

and:

```text
@/components/...
```

This avoids filesystem and TypeScript conflicts between `Components` and `components`.

---

## 🧩 shadcn-vue Component Library

The default scaffold installs **61 curated shadcn-vue registry components**.

These include commonly needed components across forms, navigation, overlays, feedback, tables, messaging, layout, and application interfaces.

Examples include:

```text
Accordion
Alert
Alert Dialog
Attachment
Avatar
Badge
Breadcrumb
Bubble
Button
Button Group
Calendar
Card
Carousel
Chart
Checkbox
Collapsible
Combobox
Command
Context Menu
Dialog
Drawer
Dropdown Menu
Empty
Field
Hover Card
Input
Input Group
Input OTP
Item
Label
Menubar
Message
Message Scroller
Navigation Menu
Number Field
Pagination
Pin Input
Popover
Progress
Questionnaire
Radio Group
Range Calendar
Resizable
Scroll Area
Select
Separator
Sheet
Sidebar
Skeleton
Slider
Sonner
Spinner
Stepper
Switch
Table
Tabs
Tags Input
Textarea
Toggle
Toggle Group
Tooltip
```

### Data Table and Date Picker

`Data Table` and `Date Picker` are deliberately treated as **compositions rather than individual registry primitives**.

The scaffold includes the underlying components and dependencies required to build them.

For example, Data Tables can be composed using:

```text
Table + @tanstack/vue-table
```

while Date Pickers can be composed using:

```text
Popover + Calendar
```

or:

```text
Popover + Range Calendar
```

---

## 🎨 Component Catalogue

A normal scaffold creates a development component catalogue at:

```text
/shadcn-vue-components
```

For example:

```text
http://localhost:8000/shadcn-vue-components
```

The exact port is printed at the end of the scaffold run.

The corresponding Inertia page is:

```text
resources/js/pages/ShadcnVueComponents.vue
```

The catalogue provides a searchable overview of the available UI components along with:

- component names
- categories
- short usage descriptions
- example syntax
- links to official shadcn-vue documentation

The route is intentionally available only in the Laravel **local environment**, so it acts as a developer reference rather than part of the production application.

---

## 📝 Form Validation

The full scaffold includes:

```text
vee-validate
@vee-validate/zod
zod
```

This provides a ready-to-use validation stack for forms built with shadcn-vue components.

The scaffold currently uses the VeeValidate v4 + Zod v3 integration to maintain compatibility with the shadcn-vue form patterns used by the generated project.

Form support can be disabled with:

```bash
python3 scaffold.py --project my-poc --no-forms
```

---

## ➕ Adding More shadcn-vue Components

The default scaffold already contains the curated component library.

If another shadcn-vue component is required later, run the following from the generated project's root:

```bash
docker compose exec app npx shadcn-vue@latest add [component]
```

For example:

```bash
docker compose exec app npx shadcn-vue@latest add aspect-ratio
```

Generated components are placed under:

```text
app/resources/js/components/ui/
```

and can be imported using the lowercase alias convention:

```ts
import { Button } from "@/components/ui/button";
```

Because shadcn-vue places the component source directly in the application, components can be freely inspected and customized.

---

## 🎛️ Scaffold Options

View all supported arguments with:

```bash
python3 scaffold.py --help
```

### `--project`

Creates the project without prompting for its name.

```bash
python3 scaffold.py --project my-poc
```

This is the recommended normal command.

---

### `--minimal`

Creates a smaller project without the extended shadcn component collection, component catalogue, or form stack.

```bash
python3 scaffold.py --project my-poc --minimal
```

Useful for lightweight projects where the complete UI system is unnecessary.

---

### `--no-showcase`

Installs the full component library but does not generate:

```text
/shadcn-vue-components
```

or:

```text
ShadcnVueComponents.vue
```

Example:

```bash
python3 scaffold.py --project my-poc --no-showcase
```

Useful when all UI components are wanted but the developer catalogue is not.

---

### `--no-forms`

Installs the full UI component collection but skips VeeValidate + Zod.

```bash
python3 scaffold.py --project my-poc --no-forms
```

Useful when another validation library will be used.

---

### `--no-overwrite-shadcn`

Prevents the current shadcn-vue registry from refreshing UI primitives already supplied by the Laravel starter kit.

```bash
python3 scaffold.py --project my-poc --no-overwrite-shadcn
```

This option is primarily intended as a compatibility/debugging escape hatch.

For normal scaffolding, **do not use this option**.

Modern shadcn-vue components may expect newer versions of shared components such as Button, Dialog, Sheet, Tooltip, or Separator.

---

## 🕹️ Day-to-Day Usage

Navigate into the generated project:

```bash
cd my-poc
```

### Start the Stack

```bash
docker compose up -d
```

### Stop the Stack

```bash
docker compose down
```

### View Logs

```bash
docker compose logs -f
```

### Run Artisan Commands

```bash
docker compose exec app php artisan [command]
```

For example:

```bash
docker compose exec app php artisan route:list
```

### Run Laravel Tests

```bash
docker compose exec app php artisan test
```

### Run the TypeScript Type-Check

```bash
docker compose exec app npm run types:check
```

### Run the Production Frontend Build

```bash
docker compose exec app npm run build
```

---

## ⚡ Vite Hot Module Reloading

During active frontend development, run Vite in a separate terminal:

```bash
docker compose exec app npm run dev -- --host 0.0.0.0 --port [VITE_PORT]
```

The assigned Vite port is printed when the project is scaffolded and is also stored in:

```text
app/.env
```

For example:

```env
VITE_PORT=5173
```

you would run:

```bash
docker compose exec app npm run dev -- --host 0.0.0.0 --port 5173
```

---

## 🌍 Accessing the Application

At the end of a successful scaffold run, the script prints URLs similar to:

```text
✨ Success! 'my-poc' has been scaffolded.

👉 Project directory: cd my-poc
🌍 Application URL: http://localhost:8000
🧩 Component catalogue: http://localhost:8000/shadcn-vue-components
💡 Run Vite HMR with: docker compose exec app npm run dev -- --host 0.0.0.0 --port 5173
```

Ports are dynamically assigned, so the actual values may differ.

Always use the **Laravel application URL** to access the application in the browser.

---

## ✅ Scaffold Validation

Before reporting a successful scaffold, the script performs several validation steps.

### Database Migrations

Laravel migrations run automatically with retry support while PostgreSQL finishes initializing.

### TypeScript Check

The scaffold runs:

```bash
npm run types:check
```

using:

```bash
vue-tsc --noEmit
```

Type-check diagnostics are reported but do not automatically terminate the entire scaffold. This prevents a registry-specific TypeScript quirk from blocking an otherwise functional application.

### Production Build

The scaffold then runs:

```bash
npm run build
```

The production Vite build is a **hard validation step**. If the application cannot compile for production, scaffolding fails.

### Laravel Tests

Finally:

```bash
php artisan test
```

is executed.

The scaffold reports success only after the production frontend build and Laravel test suite complete successfully.

---

## 🗄️ PostgreSQL

Each generated project receives its own PostgreSQL database and persistent Docker volume.

The database name and username are generated from the project slug.

For a project named:

```text
my-poc
```

the generated database will resemble:

```text
DB_DATABASE=my_poc
DB_USERNAME=my_poc
DB_PASSWORD=local_dev_password
```

PostgreSQL data is stored in a Docker volume and therefore survives normal container recreation.

To stop the project while preserving database data:

```bash
docker compose down
```

To completely remove the containers **and database volume**:

```bash
docker compose down -v
```

Use the latter with caution because it permanently deletes the local PostgreSQL data for that project.

---

## 🔐 Local Development Security

The generated environment is designed for **local development and rapid prototyping**.

For convenience, values such as:

```text
DB_PASSWORD=local_dev_password
```

are deliberately predictable.

Do not reuse the generated local Docker/database credentials unchanged in production.

Production deployments should use:

- secure secrets
- production database credentials
- environment-specific configuration
- production web servers
- appropriate TLS/HTTPS configuration
- production queue/cache/session configuration
- appropriate Laravel deployment hardening

The generated Docker Compose environment should therefore be treated as a **development environment**, not a production deployment template.

---

## 🎯 Typical Usage

For the normal feature-rich project:

```bash
python3 scaffold.py --project my-poc
```

For a lightweight project:

```bash
python3 scaffold.py --project my-poc --minimal
```

For the full UI system without the component catalogue:

```bash
python3 scaffold.py --project my-poc --no-showcase
```

For the full UI system without VeeValidate/Zod:

```bash
python3 scaffold.py --project my-poc --no-forms
```

For most Laravel/Vue prototypes and application projects, the recommended command remains simply:

```bash
python3 scaffold.py --project my-poc
```
