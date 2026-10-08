#!/usr/bin/env python3

import argparse
import json
import re
import socket
import shutil
import subprocess
import sys
import time
from pathlib import Path


LARAVEL_STARTER_KIT_VERSION = "1.0.2"

# Data Table and Date Picker are intentionally excluded. In shadcn-vue they are
# composition patterns rather than single registry primitives.
SHADCN_COMPONENTS = [
    "accordion",
    "alert",
    "alert-dialog",
    "attachment",
    "avatar",
    "badge",
    "breadcrumb",
    "bubble",
    "button",
    "button-group",
    "calendar",
    "card",
    "carousel",
    "chart",
    "checkbox",
    "collapsible",
    "combobox",
    "command",
    "context-menu",
    "dialog",
    "drawer",
    "dropdown-menu",
    "empty",
    "field",
    "hover-card",
    "input",
    "input-group",
    "input-otp",
    "item",
    "label",
    "menubar",
    "message",
    "message-scroller",
    "navigation-menu",
    "number-field",
    "pagination",
    "pin-input",
    "popover",
    "progress",
    "questionnaire",
    "radio-group",
    "range-calendar",
    "resizable",
    "scroll-area",
    "select",
    "separator",
    "sheet",
    "sidebar",
    "skeleton",
    "slider",
    "sonner",
    "spinner",
    "stepper",
    "switch",
    "table",
    "tabs",
    "tags-input",
    "textarea",
    "toggle",
    "toggle-group",
    "tooltip",
]

# The showcase is intentionally data-driven. It demonstrates what is available
# without importing every component into one enormous Vue file.
COMPONENT_CATALOGUE = [
    ("Accordion", "accordion", "Layout", "Show and hide vertically stacked content.", '<Accordion type="single" collapsible>...</Accordion>'),
    ("Alert", "alert", "Feedback", "Display a contextual message or status.", '<Alert><AlertTitle>Saved</AlertTitle></Alert>'),
    ("Alert Dialog", "alert-dialog", "Overlay", "Require confirmation before a consequential action.", '<AlertDialog><AlertDialogTrigger>Delete</AlertDialogTrigger>...</AlertDialog>'),
    ("Attachment", "attachment", "Messaging", "Present attached files and attachment actions.", '<Attachment>...</Attachment>'),
    ("Avatar", "avatar", "Display", "Show a user image with a fallback.", '<Avatar><AvatarImage src="..." /><AvatarFallback>MI</AvatarFallback></Avatar>'),
    ("Badge", "badge", "Display", "Label compact statuses, categories, or metadata.", '<Badge variant="secondary">Draft</Badge>'),
    ("Breadcrumb", "breadcrumb", "Navigation", "Show the current location in a hierarchy.", '<Breadcrumb>...</Breadcrumb>'),
    ("Bubble", "bubble", "Messaging", "Render conversational message bubbles.", '<Bubble>Message content</Bubble>'),
    ("Button", "button", "Actions", "Trigger an action or submit a form.", '<Button variant="outline">Continue</Button>'),
    ("Button Group", "button-group", "Actions", "Group related actions into one control cluster.", '<ButtonGroup><Button>One</Button><Button>Two</Button></ButtonGroup>'),
    ("Calendar", "calendar", "Date & Time", "Select a single calendar date.", '<Calendar v-model="date" />'),
    ("Card", "card", "Layout", "Group related content and actions.", '<Card><CardHeader>...</CardHeader><CardContent>...</CardContent></Card>'),
    ("Carousel", "carousel", "Display", "Cycle through a horizontal sequence of content.", '<Carousel><CarouselContent>...</CarouselContent></Carousel>'),
    ("Chart", "chart", "Data", "Build themed charts using the shadcn chart helpers.", '<ChartContainer :config="chartConfig">...</ChartContainer>'),
    ("Checkbox", "checkbox", "Forms", "Toggle an independent boolean choice.", '<Checkbox v-model="accepted" />'),
    ("Collapsible", "collapsible", "Layout", "Expand or collapse a single content region.", '<Collapsible><CollapsibleTrigger>Details</CollapsibleTrigger>...</Collapsible>'),
    ("Combobox", "combobox", "Forms", "Search and select an option from a larger list.", '<Combobox v-model="selected" :items="items" />'),
    ("Command", "command", "Navigation", "Build searchable command palettes and option lists.", '<Command><CommandInput /><CommandList>...</CommandList></Command>'),
    ("Context Menu", "context-menu", "Overlay", "Show contextual actions on right click or long press.", '<ContextMenu><ContextMenuTrigger>...</ContextMenuTrigger>...</ContextMenu>'),
    ("Data Table", "data-table", "Data", "Compose Table with TanStack Vue Table for sorting, filtering and pagination.", 'Table + @tanstack/vue-table // define columns and render rows'),
    ("Date Picker", "date-picker", "Date & Time", "Compose Popover and Calendar into a date-picker control.", '<Popover><PopoverTrigger>Pick a date</PopoverTrigger><PopoverContent><Calendar v-model="date" /></PopoverContent></Popover>'),
    ("Dialog", "dialog", "Overlay", "Open modal content above the current page.", '<Dialog><DialogTrigger>Open</DialogTrigger><DialogContent>...</DialogContent></Dialog>'),
    ("Drawer", "drawer", "Overlay", "Present content in a drawer, commonly from a screen edge.", '<Drawer><DrawerTrigger>Open</DrawerTrigger><DrawerContent>...</DrawerContent></Drawer>'),
    ("Dropdown Menu", "dropdown-menu", "Navigation", "Expose a menu of actions from a trigger.", '<DropdownMenu><DropdownMenuTrigger>Actions</DropdownMenuTrigger>...</DropdownMenu>'),
    ("Empty", "empty", "Feedback", "Explain an empty state and offer a next action.", '<Empty>...</Empty>'),
    ("Field", "field", "Forms", "Structure labels, controls, descriptions and validation errors.", '<Field><FieldLabel>Email</FieldLabel><Input /><FieldError /></Field>'),
    ("Hover Card", "hover-card", "Overlay", "Show supplementary content when a pointer hovers a trigger.", '<HoverCard><HoverCardTrigger>Profile</HoverCardTrigger>...</HoverCard>'),
    ("Input", "input", "Forms", "Capture a single-line text value.", '<Input v-model="name" placeholder="Name" />'),
    ("Input Group", "input-group", "Forms", "Combine an input with addons, icons, or actions.", '<InputGroup><InputGroupInput /><InputGroupAddon>...</InputGroupAddon></InputGroup>'),
    ("Input OTP", "input-otp", "Forms", "Capture one-time passcodes in segmented inputs.", '<InputOTP v-model="code" :maxlength="6" />'),
    ("Item", "item", "Display", "Create reusable list-item layouts with media and actions.", '<Item><ItemContent>...</ItemContent></Item>'),
    ("Label", "label", "Forms", "Provide an accessible label for a form control.", '<Label for="email">Email</Label>'),
    ("Menubar", "menubar", "Navigation", "Provide desktop-style application menus.", '<Menubar><MenubarMenu>...</MenubarMenu></Menubar>'),
    ("Message", "message", "Messaging", "Render structured chat or assistant messages.", '<Message>...</Message>'),
    ("Message Scroller", "message-scroller", "Messaging", "Keep conversational content scrollable and anchored appropriately.", '<MessageScroller>...</MessageScroller>'),
    ("Navigation Menu", "navigation-menu", "Navigation", "Build application or marketing navigation with rich submenus.", '<NavigationMenu>...</NavigationMenu>'),
    ("Number Field", "number-field", "Forms", "Capture numeric values with increment and decrement controls.", '<NumberField v-model="quantity" :min="0" />'),
    ("Pagination", "pagination", "Navigation", "Navigate through paginated result sets.", '<Pagination :total="100" :items-per-page="10">...</Pagination>'),
    ("Pin Input", "pin-input", "Forms", "Capture a fixed-length PIN or verification code.", '<PinInput v-model="pin">...</PinInput>'),
    ("Popover", "popover", "Overlay", "Display floating content anchored to a trigger.", '<Popover><PopoverTrigger>Open</PopoverTrigger><PopoverContent>...</PopoverContent></Popover>'),
    ("Progress", "progress", "Feedback", "Visualize completion or loading progress.", '<Progress :model-value="60" />'),
    ("Questionnaire", "questionnaire", "Forms", "Build structured question-and-answer experiences.", '<Questionnaire>...</Questionnaire>'),
    ("Radio Group", "radio-group", "Forms", "Choose exactly one value from a set.", '<RadioGroup v-model="plan"><RadioGroupItem value="pro" /></RadioGroup>'),
    ("Range Calendar", "range-calendar", "Date & Time", "Select a start and end date.", '<RangeCalendar v-model="range" />'),
    ("Resizable", "resizable", "Layout", "Create panels whose dimensions can be adjusted by the user.", '<ResizablePanelGroup direction="horizontal">...</ResizablePanelGroup>'),
    ("Scroll Area", "scroll-area", "Layout", "Create a styled scrollable region.", '<ScrollArea class="h-72">...</ScrollArea>'),
    ("Select", "select", "Forms", "Select one value from a compact option list.", '<Select v-model="status">...</Select>'),
    ("Separator", "separator", "Layout", "Visually separate related regions.", '<Separator />'),
    ("Sheet", "sheet", "Overlay", "Open supplemental content from an edge of the viewport.", '<Sheet><SheetTrigger>Filters</SheetTrigger><SheetContent>...</SheetContent></Sheet>'),
    ("Sidebar", "sidebar", "Navigation", "Build responsive application side navigation.", '<SidebarProvider><Sidebar>...</Sidebar><SidebarInset>...</SidebarInset></SidebarProvider>'),
    ("Skeleton", "skeleton", "Feedback", "Display placeholder shapes while content loads.", '<Skeleton class="h-4 w-40" />'),
    ("Slider", "slider", "Forms", "Choose a numeric value or range by dragging a thumb.", '<Slider v-model="value" :max="100" />'),
    ("Sonner", "sonner", "Feedback", "Display toast notifications.", '<Toaster /> // then call toast("Saved")'),
    ("Spinner", "spinner", "Feedback", "Indicate an indeterminate loading state.", '<Spinner />'),
    ("Stepper", "stepper", "Navigation", "Guide users through ordered multi-step workflows.", '<Stepper v-model="step">...</Stepper>'),
    ("Switch", "switch", "Forms", "Toggle a setting between on and off states.", '<Switch v-model="enabled" />'),
    ("Table", "table", "Data", "Display structured tabular data.", '<Table><TableHeader>...</TableHeader><TableBody>...</TableBody></Table>'),
    ("Tabs", "tabs", "Navigation", "Switch between related content views.", '<Tabs default-value="details"><TabsList>...</TabsList>...</Tabs>'),
    ("Tags Input", "tags-input", "Forms", "Capture a dynamic list of tag values.", '<TagsInput v-model="tags">...</TagsInput>'),
    ("Textarea", "textarea", "Forms", "Capture multi-line text.", '<Textarea v-model="notes" placeholder="Notes" />'),
    ("Toggle", "toggle", "Actions", "Represent a pressed or unpressed action state.", '<Toggle v-model:pressed="bold">Bold</Toggle>'),
    ("Toggle Group", "toggle-group", "Actions", "Group mutually related toggle controls.", '<ToggleGroup v-model="alignment" type="single">...</ToggleGroup>'),
    ("Tooltip", "tooltip", "Overlay", "Show a brief explanation for a control or element.", '<Tooltip><TooltipTrigger>...</TooltipTrigger><TooltipContent>Help text</TooltipContent></Tooltip>'),
]


TAILWIND_V4_CSS = r'''@import 'tailwindcss';
@import 'tw-animate-css';

@source '../../vendor/laravel/framework/src/Illuminate/Pagination/resources/views/*.blade.php';
@source '../../storage/framework/views/*.php';
@source '../views/**/*.blade.php';
@source '../js/**/*.{vue,js,ts,jsx,tsx}';

@custom-variant dark (&:is(.dark *));

@theme inline {
    --font-sans: 'Instrument Sans', ui-sans-serif, system-ui, sans-serif;

    --radius-sm: calc(var(--radius) - 4px);
    --radius-md: calc(var(--radius) - 2px);
    --radius-lg: var(--radius);
    --radius-xl: calc(var(--radius) + 4px);

    --color-background: var(--background);
    --color-foreground: var(--foreground);
    --color-card: var(--card);
    --color-card-foreground: var(--card-foreground);
    --color-popover: var(--popover);
    --color-popover-foreground: var(--popover-foreground);
    --color-primary: var(--primary);
    --color-primary-foreground: var(--primary-foreground);
    --color-secondary: var(--secondary);
    --color-secondary-foreground: var(--secondary-foreground);
    --color-muted: var(--muted);
    --color-muted-foreground: var(--muted-foreground);
    --color-accent: var(--accent);
    --color-accent-foreground: var(--accent-foreground);
    --color-destructive: var(--destructive);
    --color-destructive-foreground: var(--destructive-foreground);
    --color-border: var(--border);
    --color-input: var(--input);
    --color-ring: var(--ring);
    --color-chart-1: var(--chart-1);
    --color-chart-2: var(--chart-2);
    --color-chart-3: var(--chart-3);
    --color-chart-4: var(--chart-4);
    --color-chart-5: var(--chart-5);
    --color-sidebar: var(--sidebar-background);
    --color-sidebar-foreground: var(--sidebar-foreground);
    --color-sidebar-primary: var(--sidebar-primary);
    --color-sidebar-primary-foreground: var(--sidebar-primary-foreground);
    --color-sidebar-accent: var(--sidebar-accent);
    --color-sidebar-accent-foreground: var(--sidebar-accent-foreground);
    --color-sidebar-border: var(--sidebar-border);
    --color-sidebar-ring: var(--sidebar-ring);
}

:root {
    --background: hsl(0 0% 100%);
    --foreground: hsl(240 10% 3.9%);
    --card: hsl(0 0% 100%);
    --card-foreground: hsl(240 10% 3.9%);
    --popover: hsl(0 0% 100%);
    --popover-foreground: hsl(240 10% 3.9%);
    --primary: hsl(240 5.9% 10%);
    --primary-foreground: hsl(0 0% 98%);
    --secondary: hsl(240 4.8% 95.9%);
    --secondary-foreground: hsl(240 5.9% 10%);
    --muted: hsl(240 4.8% 95.9%);
    --muted-foreground: hsl(240 3.8% 46.1%);
    --accent: hsl(240 4.8% 95.9%);
    --accent-foreground: hsl(240 5.9% 10%);
    --destructive: hsl(0 84.2% 60.2%);
    --destructive-foreground: hsl(0 0% 98%);
    --border: hsl(240 5.9% 90%);
    --input: hsl(240 5.9% 90%);
    --ring: hsl(240 5.9% 10%);
    --radius: 0.625rem;

    --chart-1: hsl(12 76% 61%);
    --chart-2: hsl(173 58% 39%);
    --chart-3: hsl(197 37% 24%);
    --chart-4: hsl(43 74% 66%);
    --chart-5: hsl(27 87% 67%);

    --sidebar-background: hsl(0 0% 98%);
    --sidebar-foreground: hsl(240 5.3% 26.1%);
    --sidebar-primary: hsl(240 5.9% 10%);
    --sidebar-primary-foreground: hsl(0 0% 98%);
    --sidebar-accent: hsl(240 4.8% 95.9%);
    --sidebar-accent-foreground: hsl(240 5.9% 10%);
    --sidebar-border: hsl(220 13% 91%);
    --sidebar-ring: hsl(217.2 91.2% 59.8%);
}

.dark {
    --background: hsl(240 10% 3.9%);
    --foreground: hsl(0 0% 98%);
    --card: hsl(240 10% 3.9%);
    --card-foreground: hsl(0 0% 98%);
    --popover: hsl(240 10% 3.9%);
    --popover-foreground: hsl(0 0% 98%);
    --primary: hsl(0 0% 98%);
    --primary-foreground: hsl(240 5.9% 10%);
    --secondary: hsl(240 3.7% 15.9%);
    --secondary-foreground: hsl(0 0% 98%);
    --muted: hsl(240 3.7% 15.9%);
    --muted-foreground: hsl(240 5% 64.9%);
    --accent: hsl(240 3.7% 15.9%);
    --accent-foreground: hsl(0 0% 98%);
    --destructive: hsl(0 62.8% 30.6%);
    --destructive-foreground: hsl(0 0% 98%);
    --border: hsl(240 3.7% 15.9%);
    --input: hsl(240 3.7% 15.9%);
    --ring: hsl(240 4.9% 83.9%);

    --chart-1: hsl(220 70% 50%);
    --chart-2: hsl(160 60% 45%);
    --chart-3: hsl(30 80% 55%);
    --chart-4: hsl(280 65% 60%);
    --chart-5: hsl(340 75% 55%);

    --sidebar-background: hsl(240 5.9% 10%);
    --sidebar-foreground: hsl(240 4.8% 95.9%);
    --sidebar-primary: hsl(224.3 76.3% 48%);
    --sidebar-primary-foreground: hsl(0 0% 100%);
    --sidebar-accent: hsl(240 3.7% 15.9%);
    --sidebar-accent-foreground: hsl(240 4.8% 95.9%);
    --sidebar-border: hsl(240 3.7% 15.9%);
    --sidebar-ring: hsl(217.2 91.2% 59.8%);
}

@layer base {
    * {
        @apply border-border outline-ring/50;
    }

    body {
        @apply bg-background text-foreground;
    }
}
'''


VITE_CONFIG_TEMPLATE = r'''import tailwindcss from '@tailwindcss/vite';
import vue from '@vitejs/plugin-vue';
import laravel from 'laravel-vite-plugin';
import path from 'node:path';
import { defineConfig } from 'vite';

export default defineConfig({
    plugins: [
        laravel({
            input: ['resources/js/app.ts'],
            refresh: true,
        }),
        tailwindcss(),
        vue({
            template: {
                transformAssetUrls: {
                    base: null,
                    includeAbsolute: false,
                },
            },
        }),
    ],
    resolve: {
        alias: {
            '@': path.resolve(__dirname, './resources/js'),
        },
    },
    server: {
        host: '0.0.0.0',
        strictPort: true,
        hmr: {
            host: 'localhost',
        },
    },
});
'''


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Scaffold a Laravel 12 + Vue 3 + Inertia + PostgreSQL project with "
            "a modern Tailwind 4 / shadcn-vue frontend."
        )
    )
    parser.add_argument(
        "--project",
        help="Project name. If omitted, the script prompts interactively.",
    )
    parser.add_argument(
        "--minimal",
        action="store_true",
        help="Skip the extended shadcn component catalogue and form stack.",
    )
    parser.add_argument(
        "--no-showcase",
        action="store_true",
        help="Do not create the local-only /shadcn-vue-components catalogue page.",
    )
    parser.add_argument(
        "--no-forms",
        action="store_true",
        help="Do not install VeeValidate + Zod form dependencies.",
    )
    parser.add_argument(
        "--no-overwrite-shadcn",
        action="store_true",
        help=(
            "Preserve existing starter-kit UI component files instead of refreshing them "
            "from the current shadcn-vue registry. Not recommended with the full component set."
        ),
    )
    return parser.parse_args()


def find_available_port(start_port, reserved=None):
    """Scan sequentially from start_port until an available, unreserved port is found."""
    reserved = reserved or set()
    port = start_port

    while port < 65535:
        if port in reserved:
            port += 1
            continue

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.bind(("127.0.0.1", port))
                return port
            except OSError:
                port += 1

    raise RuntimeError("No available ports found on localhost.")


def command_text(cmd):
    return " ".join(cmd) if isinstance(cmd, list) else cmd


def run_cmd(cmd, cwd=None, check=True):
    """Run a command with live output."""
    print(f"\n⚡ Running: {command_text(cmd)}")
    return subprocess.run(
        cmd,
        cwd=cwd,
        shell=isinstance(cmd, str),
        check=check,
    )


def run_cmd_with_retry(cmd, cwd=None, retries=5, delay=4, label="command"):
    """Run a command with retries, useful for database startup or transient registry access."""
    for attempt in range(1, retries + 1):
        print(
            f"\n⚡ Running {label} (attempt {attempt}/{retries}): "
            f"{command_text(cmd)}"
        )
        result = subprocess.run(
            cmd,
            cwd=cwd,
            shell=isinstance(cmd, str),
            check=False,
        )

        if result.returncode == 0:
            return result

        if attempt == retries:
            print(f"\n❌ {label.capitalize()} failed after {retries} attempts.")
            sys.exit(result.returncode or 1)

        print(f"⚠️ {label.capitalize()} not ready/successful yet. Retrying in {delay} seconds...")
        time.sleep(delay)

    raise RuntimeError("Retry loop exited unexpectedly.")


def check_docker():
    """Verify Docker and Docker Compose are installed and the daemon is running."""
    print("Checking Docker status...")
    try:
        subprocess.run(
            ["docker", "--version"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        subprocess.run(
            ["docker", "compose", "version"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        result = subprocess.run(
            ["docker", "info"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if result.returncode != 0:
            print("\n❌ Error: Docker daemon is not running.")
            sys.exit(1)
        print("✔ Docker is running.")
    except (subprocess.SubprocessError, FileNotFoundError):
        print("\n❌ Error: Docker or Docker Compose is not installed or not in PATH.")
        sys.exit(1)


def patch_package_json(package_json_path, include_forms):
    """Upgrade frontend dependencies while retaining old starter-kit dependencies for compatibility."""
    package = json.loads(package_json_path.read_text())

    scripts = package.setdefault("scripts", {})
    scripts["types:check"] = "vue-tsc --noEmit"

    dependencies = package.setdefault("dependencies", {})
    dependencies.update(
        {
            "@lucide/vue": "^1.17.0",
            "@tanstack/vue-table": "^9.2.4",
            "@vueuse/core": dependencies.get("@vueuse/core", "^12.8.2"),
            "class-variance-authority": dependencies.get(
                "class-variance-authority", "^0.7.1"
            ),
            "clsx": dependencies.get("clsx", "^2.1.1"),
            "reka-ui": "^2.9.8",
            "tailwind-merge": "^3.2.0",
            "tailwindcss": "^4.1.1",
            "tw-animate-css": "^1.2.5",
            "vue-input-otp": "^0.3.2",
            "vue-sonner": "^2.0.0",
        }
    )

    if include_forms:
        # Pin the documented shadcn-vue/VeeValidate v4 integration deliberately.
        # @vee-validate/zod 4.x expects Zod 3.x.
        dependencies.update(
            {
                "vee-validate": "4.15.1",
                "@vee-validate/zod": "4.15.1",
                "zod": "^3.25.0",
            }
        )

    dev_dependencies = package.setdefault("devDependencies", {})
    dev_dependencies.update(
        {
            "@tailwindcss/vite": "^4.1.11",
            "prettier-plugin-tailwindcss": "^0.6.11",
        }
    )

    package_json_path.write_text(json.dumps(package, indent=4) + "\n")
    print("✔ Updated package.json for Tailwind 4, shadcn-vue and supporting packages.")


def patch_tsconfig(tsconfig_path):
    """Normalize the Laravel 12 starter-kit TypeScript globals for the current Vue toolchain."""
    if not tsconfig_path.exists():
        raise FileNotFoundError(f"Missing {tsconfig_path}")

    content = tsconfig_path.read_text()
    updated, count = re.subn(
        r'"types"\s*:\s*\[[^\]]*\]',
        '"types": [\n            "vite/client"\n        ]',
        content,
        count=1,
        flags=re.DOTALL,
    )

    if count != 1:
        raise RuntimeError(
            "Could not normalize compilerOptions.types in tsconfig.json; "
            "the pinned starter-kit layout may have changed."
        )

    tsconfig_path.write_text(updated)
    print("✔ Updated tsconfig.json for the current Vue/TypeScript toolchain.")



def patch_legacy_starter_typescript(app_dir):
    """Patch known Laravel Vue starter-kit v1.0.2 typing assumptions for modern packages."""
    print("\nTypeScript: normalizing Laravel 12 starter-kit source typings...")

    js_dir = app_dir / "resources" / "js"

    # The old starter augments 'vite/client' directly from app.ts. With newer Vite
    # declarations this can be interpreted as augmenting a non-module. Keep Vite's
    # globals in a conventional declaration file instead.
    app_ts = js_dir / "app.ts"
    if app_ts.exists():
        content = app_ts.read_text()
        updated, count = re.subn(
            r"\n// Extend ImportMeta interface for Vite.*?\n}\n\n(?=const appName)",
            "\n",
            content,
            count=1,
            flags=re.DOTALL,
        )
        if count:
            app_ts.write_text(updated)
            print("- Removed legacy vite/client module augmentation from app.ts.")

    vite_env = js_dir / "vite-env.d.ts"
    vite_env.write_text('/// <reference types="vite/client" />\n')

    # Inertia PageProps is record-like in newer typings. Make the starter's shared
    # page props explicitly compatible with that generic constraint.
    types_index = js_dir / "types" / "index.ts"
    if types_index.exists():
        content = types_index.read_text()
        content = content.replace(
            "export interface SharedData {",
            "export interface SharedData extends Record<string, unknown> {",
            1,
        )
        types_index.write_text(content)

    # AppHeader: give usePage the starter's SharedData type so page.props.auth is
    # not inferred as unknown by newer @inertiajs/vue3 typings.
    app_header = js_dir / "components" / "AppHeader.vue"
    if app_header.exists():
        content = app_header.read_text()
        content = content.replace(
            "import type { BreadcrumbItem, NavItem } from '@/types';",
            "import type { BreadcrumbItem, NavItem, SharedData } from '@/types';",
            1,
        )
        content = content.replace("const page = usePage();", "const page = usePage<SharedData>();", 1)
        app_header.write_text(content)

    # AppSidebarHeader: optional breadcrumbs are used as an array in the template.
    sidebar_header = js_dir / "components" / "AppSidebarHeader.vue"
    if sidebar_header.exists():
        content = sidebar_header.read_text()
        content = re.sub(
            r"defineProps<\{\s*breadcrumbs\?: BreadcrumbItemType\[\];\s*\}>\(\);",
            "withDefaults(defineProps<{ breadcrumbs?: BreadcrumbItemType[] }>(), {\n"
            "    breadcrumbs: () => [],\n"
            "});",
            content,
            count=1,
        )
        sidebar_header.write_text(content)

    # NavMain in v1.0.2 declared a second, incompatible NavItem shape using `url`.
    nav_main = js_dir / "components" / "NavMain.vue"
    if nav_main.exists():
        content = nav_main.read_text()
        content = content.replace(
            "import { type SharedData } from '@/types';",
            "import { type NavItem, type SharedData } from '@/types';",
            1,
        )
        content = re.sub(
            r"\ninterface NavItem \{.*?\n\}\n",
            "\n",
            content,
            count=1,
            flags=re.DOTALL,
        )
        content = content.replace("item.url", "item.href")
        nav_main.write_text(content)

    # Inertia Link expects a finite Method union rather than an arbitrary string.
    text_link = js_dir / "components" / "TextLink.vue"
    if text_link.exists():
        content = text_link.read_text().replace(
            "method?: string;",
            "method?: 'get' | 'post' | 'put' | 'patch' | 'delete';",
            1,
        )
        text_link.write_text(content)

    # The avatar is optional in the starter User type; narrow it for the image prop.
    user_info = js_dir / "components" / "UserInfo.vue"
    if user_info.exists():
        content = user_info.read_text().replace(
            ':src="user.avatar"',
            ':src="user.avatar ?? \'\'"',
        )
        user_info.write_text(content)

    # AuthSplitLayout also reads custom shared page props without a generic.
    auth_split = js_dir / "layouts" / "auth" / "AuthSplitLayout.vue"
    if auth_split.exists():
        content = auth_split.read_text()
        if "import type { SharedData } from '@/types';" not in content:
            content = content.replace(
                "<script setup lang=\"ts\">\n",
                "<script setup lang=\"ts\">\nimport type { SharedData } from '@/types';\n",
                1,
            )
        content = content.replace("const page = usePage();", "const page = usePage<SharedData>();", 1)
        auth_split.write_text(content)

    # Welcome relied on the globally injected $page type. Make it explicit for vue-tsc.
    welcome = js_dir / "pages" / "Welcome.vue"
    if welcome.exists():
        content = welcome.read_text()
        if "usePage" not in content.split("</script>", 1)[0]:
            content = content.replace(
                "import { Head, Link } from '@inertiajs/vue3';",
                "import type { SharedData } from '@/types';\n"
                "import { Head, Link, usePage } from '@inertiajs/vue3';\n\n"
                "const page = usePage<SharedData>();",
                1,
            )
        content = content.replace("$page.props", "page.props")
        content = content.replace(
            ':style="{ mixBlendMode: \'plus-darker\' }"',
            'style="mix-blend-mode: plus-darker"',
        )
        welcome.write_text(content)

    # Newer component typings expect numeric tabindex values as numbers.
    for vue_file in js_dir.rglob("*.vue"):
        content = vue_file.read_text()
        updated = re.sub(r'(?<!:)tabindex="([0-9]+)"', r':tabindex="\1"', content)
        if updated != content:
            vue_file.write_text(updated)

    print("- Applied Laravel 12 starter-kit compatibility typing patches.")


def normalize_component_casing(app_dir):
    """Use one canonical lowercase resources/js/components tree and import alias."""
    js_dir = app_dir / "resources" / "js"
    lower = js_dir / "components"
    upper = js_dir / "Components"

    lower.mkdir(parents=True, exist_ok=True)

    # On case-sensitive filesystems both directories can coexist. Merge any legacy
    # uppercase tree into the lowercase tree, then remove the duplicate.
    if upper.exists():
        same_location = False
        try:
            same_location = upper.samefile(lower)
        except (FileNotFoundError, OSError):
            same_location = False

        if not same_location:
            for source in sorted(upper.rglob("*")):
                relative = source.relative_to(upper)
                target = lower / relative
                if source.is_dir():
                    target.mkdir(parents=True, exist_ok=True)
                else:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source, target)
            shutil.rmtree(upper)
            print("- Merged legacy resources/js/Components into resources/js/components.")

    # Normalize aliases/imports even on case-insensitive macOS filesystems.
    extensions = {".ts", ".tsx", ".js", ".jsx", ".vue", ".d.ts"}
    for source in js_dir.rglob("*"):
        if not source.is_file():
            continue
        if source.suffix not in extensions and not source.name.endswith(".d.ts"):
            continue
        content = source.read_text()
        updated = content.replace("@/Components", "@/components")
        if updated != content:
            source.write_text(updated)

    print("- Normalized shadcn/component paths to lowercase resources/js/components.")


def install_registry_dependencies(root_dir):
    """Install dependencies written to package.json by shadcn registry components."""
    print("\nInstalling dependencies added by the shadcn-vue registry...")
    run_cmd(
        [
            "docker",
            "compose",
            "run",
            "--rm",
            "--no-deps",
            "app",
            "npm",
            "install",
        ],
        cwd=root_dir,
    )

def write_components_json(path):
    """Write a current shadcn-vue registry configuration using lowercase component paths."""
    config = {
        "$schema": "https://shadcn-vue.com/schema.json",
        "style": "new-york",
        "typescript": True,
        "tailwind": {
            "config": "",
            "css": "resources/css/app.css",
            "baseColor": "neutral",
            "cssVariables": True,
            "prefix": "",
        },
        "iconLibrary": "lucide",
        "pointer": False,
        "rtl": False,
        "aliases": {
            "components": "@/components",
            "composables": "@/composables",
            "utils": "@/lib/utils",
            "ui": "@/components/ui",
            "lib": "@/lib",
        },
    }
    path.write_text(json.dumps(config, indent=4) + "\n")
    print("✔ Wrote current shadcn-vue components.json configuration.")


def modernize_frontend(app_dir, include_forms):
    """Convert the pinned Laravel 12 starter frontend to Tailwind 4/current shadcn conventions."""
    print("\n🎨 Modernizing Tailwind and shadcn-vue frontend foundation...")

    package_json = app_dir / "package.json"
    if not package_json.exists():
        raise FileNotFoundError(f"Missing {package_json}")

    patch_package_json(package_json, include_forms)
    patch_tsconfig(app_dir / "tsconfig.json")
    normalize_component_casing(app_dir)
    patch_legacy_starter_typescript(app_dir)
    write_components_json(app_dir / "components.json")

    css_path = app_dir / "resources" / "css" / "app.css"
    css_path.write_text(TAILWIND_V4_CSS)
    print("✔ Replaced resources/css/app.css with a Tailwind 4 theme foundation.")

    vite_path = app_dir / "vite.config.ts"
    vite_path.write_text(VITE_CONFIG_TEMPLATE)
    print("✔ Replaced vite.config.ts with Tailwind 4 + Docker HMR configuration.")

    legacy_tailwind_config = app_dir / "tailwind.config.js"
    if legacy_tailwind_config.exists():
        legacy_tailwind_config.unlink()
        print("✔ Removed legacy Tailwind 3 tailwind.config.js.")


def install_shadcn_components(root_dir, overwrite=False):
    """Install the explicit component allow-list from the current shadcn-vue registry."""
    print("\n🧩 Validating shadcn-vue configuration...")
    run_cmd_with_retry(
        [
            "docker",
            "compose",
            "run",
            "--rm",
            "--no-deps",
            "app",
            "npx",
            "--yes",
            "shadcn-vue@latest",
            "info",
            "--json",
        ],
        cwd=root_dir,
        retries=3,
        delay=3,
        label="shadcn-vue registry preflight",
    )

    print(f"\n🧩 Installing {len(SHADCN_COMPONENTS)} curated shadcn-vue components...")
    command = [
        "docker",
        "compose",
        "run",
        "--rm",
        "--no-deps",
        "app",
        "npx",
        "--yes",
        "shadcn-vue@latest",
        "add",
        *SHADCN_COMPONENTS,
        "--yes",
    ]
    if overwrite:
        command.append("--overwrite")

    run_cmd_with_retry(
        command,
        cwd=root_dir,
        retries=3,
        delay=4,
        label="shadcn-vue component installation",
    )


def add_components_route(routes_path):
    """Add a local-only /shadcn-vue-components Inertia catalogue route."""
    content = routes_path.read_text()
    if "name('shadcn-vue-components')" in content or 'name("shadcn-vue-components")' in content:
        print("- /shadcn-vue-components route already exists.")
        return

    marker = "require __DIR__.'/settings.php';"
    if marker not in content:
        raise RuntimeError(
            "Could not find the settings.php include in routes/web.php; route injection aborted."
        )

    route = """if (app()->environment('local')) {
    Route::get('/shadcn-vue-components', function () {
        return Inertia::render('ShadcnVueComponents');
    })->name('shadcn-vue-components');
}

"""
    routes_path.write_text(content.replace(marker, route + marker, 1))
    print("- Added local-only /shadcn-vue-components route.")

def catalogue_records(include_forms):
    records = [
        {
            "name": name,
            "slug": slug,
            "category": category,
            "description": description,
            "example": example,
            "docs": f"https://www.shadcn-vue.com/docs/components/{slug}",
            "kind": "composition" if slug in {"data-table", "date-picker"} else "component",
        }
        for name, slug, category, description, example in COMPONENT_CATALOGUE
    ]

    if include_forms:
        records.append(
            {
                "name": "VeeValidate + Zod",
                "slug": "vee-validate",
                "category": "Forms",
                "description": (
                    "Validate typed Vue forms using VeeValidate, Zod and shadcn Field primitives."
                ),
                "example": (
                    "const formSchema = toTypedSchema(z.object({ email: z.string().email() }))"
                ),
                "docs": "https://www.shadcn-vue.com/docs/forms/vee-validate",
                "kind": "integration",
            }
        )

    return records


def write_showcase_page(page_path, include_forms):
    page_path.parent.mkdir(parents=True, exist_ok=True)
    component_json = json.dumps(catalogue_records(include_forms), indent=4)

    page = f'''<script setup lang="ts">
import {{ Head }} from '@inertiajs/vue3';
import {{ computed, ref }} from 'vue';

type CatalogueItem = {{
    name: string;
    slug: string;
    category: string;
    description: string;
    example: string;
    docs: string;
    kind: 'component' | 'composition' | 'integration';
}};

const query = ref('');
const selectedCategory = ref('All');

const items: CatalogueItem[] = {component_json};

const categories = computed(() => [
    'All',
    ...Array.from(new Set(items.map((item) => item.category))).sort(),
]);

const filteredItems = computed(() => {{
    const term = query.value.trim().toLowerCase();

    return items.filter((item) => {{
        const categoryMatches =
            selectedCategory.value === 'All' || item.category === selectedCategory.value;
        const searchMatches =
            !term ||
            item.name.toLowerCase().includes(term) ||
            item.category.toLowerCase().includes(term) ||
            item.description.toLowerCase().includes(term);

        return categoryMatches && searchMatches;
    }});
}});
</script>

<template>
    <Head title="shadcn-vue components" />

    <main class="min-h-screen bg-background text-foreground">
        <div class="mx-auto max-w-7xl space-y-8 px-6 py-10 lg:px-8">
            <section class="space-y-3">
                <div class="flex flex-wrap items-center gap-3">
                    <h1 class="text-3xl font-semibold tracking-tight">shadcn-vue component catalogue</h1>
                    <span class="rounded-full border px-2.5 py-1 text-xs text-muted-foreground">
                        Local development only
                    </span>
                </div>
                <p class="max-w-3xl text-sm leading-6 text-muted-foreground">
                    The scaffold installs the reusable shadcn-vue primitives under
                    <code class="rounded bg-muted px-1.5 py-0.5">resources/js/components/ui</code>.
                    Data Table and Date Picker are composition patterns rather than standalone
                    primitives, so this catalogue calls that out explicitly.
                </p>
            </section>

            <section class="grid gap-4 md:grid-cols-[minmax(0,1fr)_auto] md:items-center">
                <input
                    v-model="query"
                    type="search"
                    placeholder="Search components, categories, or use cases..."
                    class="h-10 w-full rounded-md border border-input bg-background px-3 text-sm shadow-sm outline-none placeholder:text-muted-foreground focus:ring-2 focus:ring-ring/40"
                />

                <div class="flex flex-wrap gap-2">
                    <button
                        v-for="category in categories"
                        :key="category"
                        type="button"
                        class="rounded-md border px-3 py-2 text-xs font-medium transition"
                        :class="
                            selectedCategory === category
                                ? 'bg-primary text-primary-foreground'
                                : 'bg-background hover:bg-accent hover:text-accent-foreground'
                        "
                        @click="selectedCategory = category"
                    >
                        {{{{ category }}}}
                    </button>
                </div>
            </section>

            <section class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
                <article
                    v-for="item in filteredItems"
                    :key="item.slug"
                    class="flex min-h-64 flex-col rounded-xl border bg-card p-5 text-card-foreground shadow-sm"
                >
                    <div class="mb-4 flex items-start justify-between gap-3">
                        <div>
                            <p class="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                                {{{{ item.category }}}}
                            </p>
                            <h2 class="mt-1 text-lg font-semibold">{{{{ item.name }}}}</h2>
                        </div>
                        <span
                            class="rounded-full border px-2 py-1 text-[11px] capitalize text-muted-foreground"
                        >
                            {{{{ item.kind }}}}
                        </span>
                    </div>

                    <p class="text-sm leading-6 text-muted-foreground">{{{{ item.description }}}}</p>

                    <div class="mt-4 rounded-lg border bg-muted/50 p-3">
                        <p class="mb-2 text-xs font-medium text-muted-foreground">Example</p>
                        <pre class="overflow-x-auto whitespace-pre-wrap break-words text-xs leading-5"><code>{{{{ item.example }}}}</code></pre>
                    </div>

                    <div class="mt-auto pt-5">
                        <a
                            :href="item.docs"
                            target="_blank"
                            rel="noreferrer"
                            class="text-sm font-medium underline underline-offset-4 hover:text-muted-foreground"
                        >
                            Official docs ↗
                        </a>
                    </div>
                </article>
            </section>

            <p v-if="filteredItems.length === 0" class="rounded-lg border p-6 text-sm text-muted-foreground">
                No components match that search.
            </p>
        </div>
    </main>
</template>
'''

    page_path.write_text(page)
    print(f"✔ Created {page_path.relative_to(page_path.parents[3])} component catalogue.")


def verify_component_directories(app_dir):
    """Warn about unexpected missing component directories after CLI installation."""
    ui_dir = app_dir / "resources" / "js" / "components" / "ui"
    missing = [slug for slug in SHADCN_COMPONENTS if not (ui_dir / slug).exists()]

    if missing:
        print(
            "⚠️ The shadcn CLI completed, but these expected component directories were not "
            f"found: {', '.join(missing)}"
        )
        print("   Review registry output before using the affected components.")
    else:
        print(f"✔ Verified all {len(SHADCN_COMPONENTS)} curated component directories.")


def configure_environment(app_dir, app_port, vite_port, db_name, root_dir):
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
        line
        for line in env_content.splitlines()
        if not re.match(r"^\s*#?\s*(DB_|APP_URL=|VITE_PORT=)", line)
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
    env_file.write_text("\n".join(clean_lines).strip() + "\n" + docker_env_block)

    env_lines = env_file.read_text().splitlines()
    has_app_key = any(
        line.startswith("APP_KEY=")
        and line.partition("=")[2].strip().strip('"').strip("'")
        for line in env_lines
    )

    if not has_app_key:
        print("🔑 Generating application encryption key...")
        run_cmd(
            [
                "docker",
                "compose",
                "run",
                "--rm",
                "--no-deps",
                "app",
                "php",
                "artisan",
                "key:generate",
                "--no-interaction",
            ],
            cwd=root_dir,
        )


def write_docker_files(root_dir, docker_php_dir, app_port, vite_port, db_name):
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


def validate_project_name(project_name):
    project_slug = re.sub(r"[^a-z0-9]+", "-", project_name.lower()).strip("-")
    if not project_slug:
        print("❌ Error: Invalid project name. Please use alphanumeric characters.")
        sys.exit(1)
    return project_slug


def main():
    args = parse_args()

    project_name = (args.project or input("Enter project name (e.g., my-prototype): ")).strip()
    if not project_name:
        print("Project name cannot be empty.")
        sys.exit(1)

    project_slug = validate_project_name(project_name)
    db_name = project_slug.replace("-", "_")
    root_dir = Path(project_slug)

    if root_dir.exists():
        print(f"\n❌ Error: Directory '{project_slug}' already exists.")
        sys.exit(1)

    install_full_ui = not args.minimal
    include_forms = install_full_ui and not args.no_forms
    include_showcase = install_full_ui and not args.no_showcase

    check_docker()

    print("\n🔍 Checking port availability...")
    app_port = find_available_port(8000)
    vite_port = find_available_port(5173, reserved={app_port})
    print(f"✔ App port assigned: {app_port}")
    print(f"✔ Vite port assigned: {vite_port}")

    print(f"\n📂 Creating project directories for '{project_slug}'...")
    docker_php_dir = root_dir / "docker" / "php"
    app_dir = root_dir / "app"
    docker_php_dir.mkdir(parents=True, exist_ok=True)
    app_dir.mkdir(parents=True, exist_ok=True)

    write_docker_files(root_dir, docker_php_dir, app_port, vite_port, db_name)

    print(
        f"\n🚀 Building app container and installing Laravel Vue Starter Kit "
        f"v{LARAVEL_STARTER_KIT_VERSION} (Laravel 12 baseline)..."
    )
    run_cmd(["docker", "compose", "build", "app"], cwd=root_dir)
    run_cmd(
        [
            "docker",
            "compose",
            "run",
            "--rm",
            "--no-deps",
            "app",
            "composer",
            "create-project",
            "laravel/vue-starter-kit",
            ".",
            LARAVEL_STARTER_KIT_VERSION,
        ],
        cwd=root_dir,
    )

    configure_environment(app_dir, app_port, vite_port, db_name, root_dir)
    modernize_frontend(app_dir, include_forms=include_forms)

    print("\n📦 Installing frontend packages via npm inside a temporary app container...")
    run_cmd(
        [
            "docker",
            "compose",
            "run",
            "--rm",
            "--no-deps",
            "app",
            "npm",
            "install",
        ],
        cwd=root_dir,
    )

    if install_full_ui:
        install_shadcn_components(root_dir, overwrite=not args.no_overwrite_shadcn)
        normalize_component_casing(app_dir)
        install_registry_dependencies(root_dir)
        verify_component_directories(app_dir)

    if include_showcase:
        add_components_route(app_dir / "routes" / "web.php")
        write_showcase_page(
            app_dir / "resources" / "js" / "pages" / "ShadcnVueComponents.vue",
            include_forms=include_forms,
        )

    print("\n🐳 Starting Docker containers...")
    run_cmd(["docker", "compose", "up", "-d"], cwd=root_dir)

    print("\n🗄️ Running database migrations with auto-retry...")
    run_cmd_with_retry(
        [
            "docker",
            "compose",
            "exec",
            "-T",
            "app",
            "php",
            "artisan",
            "migrate",
            "--no-interaction",
        ],
        cwd=root_dir,
        retries=5,
        delay=4,
        label="database migration",
    )

    print("\n🔎 Running frontend type-check...")
    typecheck = run_cmd(
        ["docker", "compose", "exec", "-T", "app", "npm", "run", "types:check"],
        cwd=root_dir,
        check=False,
    )
    if typecheck.returncode == 0:
        print("✔ Frontend type-check passed.")
    else:
        print(
            "⚠️ Frontend type-check reported one or more issues. "
            "Continuing to the production build so registry-only typing quirks do not "
            "abort an otherwise buildable scaffold. Review the diagnostics above."
        )

    print("\n🏗️ Running production frontend build...")
    run_cmd(
        ["docker", "compose", "exec", "-T", "app", "npm", "run", "build"],
        cwd=root_dir,
    )

    print("\n🧪 Running Laravel test suite...")
    run_cmd(
        ["docker", "compose", "exec", "-T", "app", "php", "artisan", "test"],
        cwd=root_dir,
    )

    print(f"\n✨ Success! '{project_slug}' has been scaffolded.")
    print(f"👉 Project directory: cd {project_slug}")
    print(f"🌍 Application URL: http://localhost:{app_port}")
    if include_showcase:
        print(f"🧩 Component catalogue: http://localhost:{app_port}/shadcn-vue-components")
    print(
        "💡 Run Vite HMR with: "
        f"docker compose exec app npm run dev -- --host 0.0.0.0 --port {vite_port}"
    )

    if args.no_overwrite_shadcn:
        print(
            "⚠️ --no-overwrite-shadcn was enabled. Some modern components may expect newer "
            "shared primitives; use the default overwrite behavior if type-check/build fails."
        )


if __name__ == "__main__":
    main()
