#!/bin/sh
set -e

# Prints error message to stderr and exits with code 1
error() { printf 'ERROR: %s\n' "$1" >&2; exit 1; }

# Prints warning message to stderr
warn() { printf 'WARN: %s\n' "$1" >&2; }

# Prints info message to stdout
info() { printf 'INFO: %s\n' "$1"; }

# Check if running inside container
[ -f /.dockerenv ] || [ -n "$CONTAINER" ] || error "This script must be run inside the container"

# Load and export all environment variables from .env
if [ -f /workspace/.env ]; then
  set -a  # Enable auto-export of variables
  . /workspace/.env
  set +a  # Disable auto-export
else
  error "Missing .env file in /workspace"
fi

# ======================================================================
# Optional installation functions
# ======================================================================

install_claude() {
  info "Starting Claude Code installation..."
  command -v claude >/dev/null 2>&1 && { info "Claude Code already installed"; return 0; }
  command -v node >/dev/null 2>&1 || error "Node.js not found. Install Node.js first."

  info "Installing Claude Code via npm..."
  npm install -g @anthropic-ai/claude-code || error "Claude Code installation failed"
  command -v claude >/dev/null 2>&1 || error "Claude Code installation verification failed"

  # Copy Claude Code configuration
  if [ -d "/workspace/.toolchain/prototype/.claude" ]; then
    info "Installing Claude Code configuration..."

    # Preserve settings.local.json if exists
    if [ -f "/workspace/.claude/settings.local.json" ]; then
      cp /workspace/.claude/settings.local.json /tmp/claude-settings.local.json.bak
    fi

    rm -rf /workspace/.claude
    cp -r /workspace/.toolchain/prototype/.claude /workspace/.claude

    # Restore settings.local.json
    if [ -f "/tmp/claude-settings.local.json.bak" ]; then
      cp /tmp/claude-settings.local.json.bak /workspace/.claude/settings.local.json
      rm /tmp/claude-settings.local.json.bak
      info "Preserved existing settings.local.json"
    fi

    info "Claude Code configuration installed at /workspace/.claude"
  else
    warn "Claude Code configuration not found in /workspace/.toolchain/prototype/.claude"
  fi

  info "Claude Code installation completed"
  info "Run 'claude' to start using Claude Code CLI"
}

install_vscode() {
  info "Setting up VSCode configuration..."
  mkdir -p /workspace/.vscode

  # Copy VSCode configuration files from install
  if [ -d /workspace/.toolchain/prototype/vscode ]; then
    if [ -f /workspace/.toolchain/prototype/vscode/settings.json ]; then
      cp /workspace/.toolchain/prototype/vscode/settings.json /workspace/.vscode/settings.json
      info "  - settings.json: Editor and language settings"
    else
      warn "VSCode settings.json not found in prototype/vscode"
    fi

    if [ -f /workspace/.toolchain/prototype/vscode/launch.json ]; then
      cp /workspace/.toolchain/prototype/vscode/launch.json /workspace/.vscode/launch.json
      info "  - launch.json: Debug configurations (C++ microservices)"
    else
      warn "VSCode launch.json not found in prototype/vscode"
    fi

    if [ -f /workspace/.toolchain/prototype/vscode/tasks.json ]; then
      cp /workspace/.toolchain/prototype/vscode/tasks.json /workspace/.vscode/tasks.json
      info "  - tasks.json: Build tasks"
    else
      warn "VSCode tasks.json not found in prototype/vscode"
    fi

    info "VSCode configuration created at /workspace/.vscode/"
  else
    error "prototype/vscode directory not found"
  fi
}

show_help() {
  cat << EOF
Usage: setup.sh [OPTIONS]

Options:
  --help                    Show this help message
EOF
  exit 0
}

# ======================================================================
# Command-line argument parsing
# ======================================================================

while [ $# -gt 0 ]; do
  case $1 in
    --help) show_help ;;
    *) error "Unknown option: $1" ;;
  esac
done

# ======================================================================
# Main setup (full installation)
# ======================================================================

info "Setting up nginx+FastAPI API gateway..."

# Replace install.sh with symlink to .toolchain/install.sh
if [ -f /workspace/install.sh ] && [ ! -L /workspace/install.sh ] && [ -f /workspace/.toolchain/install.sh ]; then
  info "Replacing install.sh with symbolic link to .toolchain/install.sh..."
  rm -f /workspace/install.sh
  ln -sf .toolchain/install.sh /workspace/install.sh || warn "Failed to create install.sh symlink"
fi

# Remove system, vscode, docs from workspace if install is a symlink to .toolchain/install
if [ -L /workspace/install ] && [ -d /workspace/.toolchain/install ]; then
  info "Cleaning up workspace directories (using .toolchain/install as source)..."

  if [ -d /workspace/system ] && [ ! -L /workspace/system ]; then
    rm -rf /workspace/system
    info "Removed /workspace/system"
  fi

  if [ -d /workspace/vscode ] && [ ! -L /workspace/vscode ]; then
    rm -rf /workspace/vscode
    info "Removed /workspace/vscode"
  fi

  if [ -d /workspace/docs ] && [ ! -L /workspace/docs ]; then
    rm -rf /workspace/docs
    info "Removed /workspace/docs"
  fi
fi

# Copy gitignore.example to .gitignore (overwrite if exists)
if [ -f /workspace/.toolchain/prototype/gitignore.example ]; then
  info "Creating .gitignore from gitignore.example..."
  cp /workspace/.toolchain/prototype/gitignore.example /workspace/.gitignore
  info ".gitignore created"
else
  warn "gitignore.example not found in install directory"
fi

# Update package list
info "Updating package lists..."
apt-get update >/dev/null 2>&1 || error "Failed to update package lists"

# Install nginx, Redis and Python dependencies
info "Installing nginx, Redis and system packages..."
DEBIAN_FRONTEND=noninteractive apt-get install -y \
  nginx redis-server python3 python3-pip python3-dev curl git \
  sqlite3 libsqlite3-dev libmysqlclient-dev libpq-dev build-essential \
  cmake nlohmann-json3-dev libspdlog-dev pkg-config default-mysql-client postgresql-client \
  libhiredis-dev unixodbc unixodbc-dev odbc-postgresql odbc-mariadb libsqliteodbc \
  >/dev/null 2>&1 || error "Failed to install nginx and dependencies"

# Install Python packages
info "Installing Python packages (FastAPI, uvicorn, database drivers, Redis)..."
pip3 install --no-cache-dir --break-system-packages \
  fastapi "uvicorn[standard]" psycopg2-binary pymysql pyodbc \
  python-dotenv pyjwt "email-validator" redis gunicorn httpx \
  sqlalchemy websockets \
  >/dev/null 2>&1 || error "Failed to install Python packages"

# Download cpp-httplib (header-only library) for C++ microservices
info "Downloading cpp-httplib header-only library..."
mkdir -p /usr/local/include
if curl -fsSL "https://raw.githubusercontent.com/yhirose/cpp-httplib/master/httplib.h" \
  -o /usr/local/include/httplib.h; then
  info "cpp-httplib downloaded successfully to /usr/local/include"
else
  warn "Failed to download cpp-httplib"
fi

# Download and install uWebSockets (header-only) and uSockets (static library)
info "Installing uWebSockets and uSockets..."
UWEBSOCKETS_TMP="/tmp/uwebsockets_install_$$"
mkdir -p "$UWEBSOCKETS_TMP"
cd "$UWEBSOCKETS_TMP"

# Clone and build uSockets
if git clone --depth 1 https://github.com/uNetworking/uSockets.git >/dev/null 2>&1; then
  cd uSockets
  if make >/dev/null 2>&1; then
    cp uSockets.a /usr/local/lib/libuSockets.a
    cp src/*.h /usr/local/include/
    info "uSockets library and headers installed to /usr/local"
  else
    warn "Failed to build uSockets"
  fi
  cd "$UWEBSOCKETS_TMP"
else
  warn "Failed to clone uSockets"
fi

# Clone uWebSockets (header-only)
if git clone --depth 1 https://github.com/uNetworking/uWebSockets.git >/dev/null 2>&1; then
  mkdir -p /usr/local/include/uwebsockets
  cp uWebSockets/src/*.h /usr/local/include/uwebsockets/
  info "uWebSockets headers installed to /usr/local/include/uwebsockets"
else
  warn "Failed to clone uWebSockets"
fi

# Cleanup
cd /workspace
rm -rf "$UWEBSOCKETS_TMP"
info "uWebSockets installation completed"

# Download nanodbc (ODBC wrapper library)
info "Downloading nanodbc library..."
mkdir -p /usr/local/include/nanodbc
mkdir -p /usr/local/src/nanodbc
if curl -fsSL "https://raw.githubusercontent.com/nanodbc/nanodbc/master/nanodbc/nanodbc.h" \
  -o /usr/local/include/nanodbc/nanodbc.h && \
   curl -fsSL "https://raw.githubusercontent.com/nanodbc/nanodbc/master/nanodbc/nanodbc.cpp" \
  -o /usr/local/src/nanodbc/nanodbc.cpp; then
  info "nanodbc downloaded successfully"
else
  warn "Failed to download nanodbc"
fi

# Copy and compile microtools library (required by C++ modules)
if [ -d /workspace/.toolchain/prototype/lib/utils/cpp ]; then
  info "Copying microtools library sources to services/utils..."
  mkdir -p /workspace/services/utils
  rm -rf /workspace/services/utils/*
  cp -r /workspace/.toolchain/prototype/lib/utils/cpp/* /workspace/services/utils/
  info "Compiling microtools static library..."
  cd /workspace/services/utils
  mkdir -p build
  cd build
  if cmake .. >/dev/null 2>&1 && make >/dev/null 2>&1; then
    info "microtools library compiled successfully"
    # Install library and headers to system location
    if [ -f libmicrotools.a ]; then
      mkdir -p /usr/local/lib
      mkdir -p /usr/local/include/microtools
      cp libmicrotools.a /usr/local/lib/
      cp ../*.h /usr/local/include/microtools/
      info "microtools library installed to /usr/local/lib"
    fi
  else
    warn "Failed to compile microtools library"
  fi
  cd /workspace
else
  warn "microtools library sources not found in .toolchain/prototype/lib/utils/cpp"
fi

# Copy Python utils library (required by API modules)
if [ -d /workspace/.toolchain/prototype/lib/utils/python ]; then
  info "Copying Python utils library to api/utils..."
  mkdir -p /workspace/api/utils
  rm -rf /workspace/api/utils/*
  cp -r /workspace/.toolchain/prototype/lib/utils/python/* /workspace/api/utils/
  info "Python utils library installed to /workspace/api/utils"
else
  warn "Python utils library not found in .toolchain/prototype/lib/utils/python"
fi

# Copy bin directory with utilities (only if install is not a symlink to .toolchain/install)
if [ -d /workspace/.toolchain/prototype/bin ] && [ ! -L /workspace/install ]; then
  info "Copying utility scripts from prototype/bin..."
  cp -r /workspace/.toolchain/prototype/bin /workspace/
  chmod +x /workspace/bin/* 2>/dev/null || true
  info "Utility scripts copied to /workspace/bin"
elif [ ! -d /workspace/bin ] && [ -L /workspace/install ]; then
  # If bin doesn't exist and install is a symlink, create bin directory
  mkdir -p /workspace/bin
fi

# Install s6 service definitions for s6-overlay v3
info "Installing s6 service definitions (s6-overlay v3)..."

# Clean up old service definitions
rm -rf /etc/services.d/*
rm -rf /etc/services.d.available/*
rm -rf /etc/s6-rc/source/*

mkdir -p /etc/services.d
mkdir -p /etc/services.d.available
mkdir -p /etc/s6-rc/source

# Define which services should be enabled by default
# All other services will be available but disabled
DEFAULT_ENABLED_SERVICES="uvicorn nginx redis mod_status"

# Copy all service templates
if [ -d /workspace/.toolchain/prototype/s6 ]; then
  info "Installing all services to available directory..."

  for service_dir in /workspace/.toolchain/prototype/s6/*/; do
    if [ -d "$service_dir" ]; then
      service_name=$(basename "$service_dir")

      # Copy to services.d.available (all services)
      cp -r "$service_dir" "/etc/services.d.available/$service_name"
      # Copy to s6-rc source (all services)
      cp -r "$service_dir" "/etc/s6-rc/source/$service_name"

      # Make run scripts executable
      if [ -f "/etc/services.d.available/$service_name/run" ]; then
        chmod +x "/etc/services.d.available/$service_name/run"
      fi
      if [ -f "/etc/services.d.available/$service_name/finish" ]; then
        chmod +x "/etc/services.d.available/$service_name/finish"
      fi
      if [ -f "/etc/s6-rc/source/$service_name/run" ]; then
        chmod +x "/etc/s6-rc/source/$service_name/run"
      fi
      if [ -f "/etc/s6-rc/source/$service_name/finish" ]; then
        chmod +x "/etc/s6-rc/source/$service_name/finish"
      fi

      info "  Installed service: $service_name"
    fi
  done

  # Enable default services
  info "Enabling default services..."
  for service in $DEFAULT_ENABLED_SERVICES; do
    if [ -d "/etc/services.d.available/$service" ]; then
      cp -r "/etc/services.d.available/$service" "/etc/services.d/$service"
      info "  Enabled service: $service"
    else
      warn "  Service '$service' not found, skipping"
    fi
  done

  # Create user bundle definition for s6-overlay v3
  info "Creating s6-rc user bundle..."
  mkdir -p /etc/s6-rc/source/user
  echo "bundle" > /etc/s6-rc/source/user/type
  mkdir -p /etc/s6-rc/source/user/contents.d
  for service in $DEFAULT_ENABLED_SERVICES; do
    touch "/etc/s6-rc/source/user/contents.d/$service"
    info "  Added $service to user bundle"
  done

  # Compile s6-rc database
  info "Compiling s6-rc service database..."
  if /command/s6-rc-compile /etc/s6-rc/compiled /etc/s6-rc/source >/dev/null 2>&1; then
    info "s6-rc database compiled successfully"

    # Update s6-overlay to use new compiled database
    if [ -L /run/s6-rc/compiled ]; then
      rm -f /run/s6-rc/compiled
    fi
    ln -sf /etc/s6-rc/compiled /run/s6-rc/compiled
    info "s6-rc database linked to runtime"
  else
    warn "Failed to compile s6-rc database - services may not start automatically"
    warn "You can compile manually with: s6-rc-compile /etc/s6-rc/compiled /etc/s6-rc/source"
  fi

  info "s6 service definitions installed (s6-overlay v3 compatible)"
  info "Enabled services: $DEFAULT_ENABLED_SERVICES"
  info "Disabled services available in /etc/services.d.available/"
else
  warn "prototype/s6 directory not found, skipping s6 service installation"
fi

# Create symlinks to bin utilities in .toolchain/prototype/bin
if [ -d /workspace/.toolchain/prototype/bin ]; then
  info "Creating symbolic links to .toolchain/prototype/bin utilities..."

  # Remove existing files/symlinks and create new symlinks
  rm -f /workspace/bin/cmd
  ln -sf /workspace/.toolchain/prototype/bin/cmd /workspace/bin/cmd || warn "Failed to create cmd symlink"
fi

# Add /workspace/bin to system PATH
info "Configuring system PATH..."
if [ -f /workspace/.toolchain/prototype/system/workspace-bin.sh ]; then
  cp /workspace/.toolchain/prototype/system/workspace-bin.sh /etc/profile.d/workspace-bin.sh
  chmod +x /etc/profile.d/workspace-bin.sh
  export PATH="/workspace/bin:$PATH"
  info "System PATH configured from prototype/system/workspace-bin.sh"
else
  error "workspace-bin.sh not found in prototype/system"
fi

# Configure shell aliases and timezone
info "Configuring shell environment..."
echo "alias cls='clear'" >> /root/.bashrc
echo "export TZ=Europe/Rome" >> /root/.bashrc
echo "export PATH=\"/workspace/bin:\$PATH\"" >> /root/.bashrc

# Configure Redis (started by s6-overlay)
info "Configuring Redis..."

mkdir -p /var/log/redis
mkdir -p /var/lib/redis

# Configure Redis to bind to localhost and enable persistence
if [ -f /workspace/.toolchain/prototype/redis/redis.conf ]; then
  cp /workspace/.toolchain/prototype/redis/redis.conf /etc/redis/redis.conf
  info "Redis configuration copied from prototype/redis/redis.conf"
  info "Redis will be started automatically by s6-overlay"
else
  error "redis.conf not found in prototype/redis"
fi

# Ensure nginx directories exist
mkdir -p /etc/nginx/conf.d
mkdir -p /etc/nginx/sites-available
mkdir -p /etc/nginx/sites-enabled
mkdir -p /etc/nginx/modules-enabled
mkdir -p /var/log/nginx

# Create directories
mkdir -p /workspace/api
mkdir -p /workspace/services
mkdir -p /var/log/nginx
mkdir -p /workspace/logs

# Copy database schemas from install
if [ -d /workspace/.toolchain/prototype/database ]; then
  info "Copying database schemas from prototype/database..."
  cp -r /workspace/.toolchain/prototype/database /workspace/
  info "Database schemas copied to /workspace/database"
else
  warn "prototype/database directory not found, skipping database schemas copy"
fi

# Create Python FastAPI application structure
info "Creating FastAPI application structure..."
rm -rf /workspace/api/app 2>/dev/null || true

# Copy nginx configuration from install
info "Copying nginx configuration..."
if [ -f /workspace/.toolchain/prototype/nginx/gateway ]; then
  cp /workspace/.toolchain/prototype/nginx/gateway /etc/nginx/sites-available/gateway
  info "Nginx site configuration copied"
else
  error "nginx/gateway configuration file not found in install directory"
fi

# Enable site and disable default
info "Configuring nginx sites..."
ln -sf /etc/nginx/sites-available/gateway /etc/nginx/sites-enabled/gateway
rm -f /etc/nginx/sites-enabled/default

# Create conf directory with symlinks to service configurations for easy customization
info "Creating configuration symlinks..."
mkdir -p /workspace/conf
ln -sf /etc/nginx/sites-available/gateway /workspace/conf/nginx.conf
ln -sf /etc/redis/redis.conf /workspace/conf/redis.conf
info "Nginx configuration accessible at /workspace/conf/nginx.conf"
info "Redis configuration accessible at /workspace/conf/redis.conf"

# Copy api files and modules from install if available
if [ -d /workspace/.toolchain/prototype/api ]; then
  info "Copying api files and modules from prototype/api..."

  # Cleanup: remove existing modules and cache
  rm -rf /workspace/api/mod_*
  rm -rf /workspace/api/__pycache__
  find /workspace/api -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

  # Copy all files (main.py, requirements.txt, scripts, etc.)
  for file in /workspace/.toolchain/prototype/api/*; do
    if [ -f "$file" ]; then
      filename=$(basename "$file")
      info "Installing file: $filename"
      cp "$file" /workspace/api/
      # Make shell scripts executable
      case "$filename" in
        *.sh)
          chmod +x "/workspace/api/$filename"
          ;;
      esac
    fi
  done

  # Copy all module directories
  for module_dir in /workspace/.toolchain/prototype/api/*/; do
    if [ -d "$module_dir" ]; then
      module_name=$(basename "$module_dir")
      info "Installing module: $module_name"
      cp -r "$module_dir" /workspace/api/
    fi
  done
else
  info "No prototype/api directory found, skipping api installation"
fi

# Gateway will be started automatically by s6-overlay
info "Gateway (uvicorn) will be started automatically by s6-overlay"

# Copy nginx main configuration if not exists
if [ ! -f /etc/nginx/nginx.conf ]; then
  info "Copying main nginx.conf..."
  if [ -f /workspace/.toolchain/prototype/nginx/nginx.conf ]; then
    cp /workspace/.toolchain/prototype/nginx/nginx.conf /etc/nginx/nginx.conf
    info "Main nginx.conf copied"
  else
    error "nginx/nginx.conf configuration file not found in install directory"
  fi
fi

# Test nginx configuration
info "Testing nginx configuration..."
nginx -t 2>&1 || error "Nginx configuration test failed"
info "Nginx will be started automatically by s6-overlay"

# Install Node.js if not present
if ! command -v node >/dev/null 2>&1; then
  info "Installing Node.js 20.x..."
  apt-get install -y curl >/dev/null 2>&1 || error "Failed to install curl"
  curl -fsSL https://deb.nodesource.com/setup_20.x | bash - >/dev/null 2>&1
  apt-get install -y nodejs >/dev/null 2>&1 || error "Failed to install Node.js"
  info "Node.js installed: $(node --version)"
fi

# Vite dev server (disabled by default, managed by s6 if enabled)

# Check if Svelte .toolchain needs to be created or just updated
PROJECT_EXISTS=false
if [ -f "/workspace/gui/package.json" ] && [ -d "/workspace/gui/node_modules" ]; then
  PROJECT_EXISTS=true
  info "Svelte .toolchain exists, updating dependencies..."
else
  info "Installing Svelte with Vite..."
fi

# Remove Svelte app structure (but keep package.json and node_modules if .toolchain exists)
if [ -d "/workspace/gui" ]; then
  cd /workspace/gui
  rm -rf src/ public/ .vscode/
  if [ "$PROJECT_EXISTS" = "false" ]; then
    rm -rf node_modules/
    rm -f package.json package-lock.json
  fi
  rm -f index.html .gitignore vite.config.js svelte.config.js jsconfig.json README.md
  cd /workspace
fi

# Create/recreate Svelte .toolchain only if needed
if [ "$PROJECT_EXISTS" = "false" ]; then
  cd /workspace
  mkdir -p gui
  cd gui
  yes | npm create vite@latest . -- --template svelte >/dev/null 2>&1 || error "Failed to create Svelte .toolchain"
  npm install >/dev/null 2>&1 || error "Failed to install Svelte dependencies"
  npm install -D terser >/dev/null 2>&1 || warn "Failed to install terser"
else
  cd /workspace/gui
  npm install >/dev/null 2>&1 || error "Failed to update Svelte dependencies"
  npm install -D terser >/dev/null 2>&1 || warn "Failed to install terser"
fi

# Clean default files
info "Cleaning default Svelte files..."
rm -rf src/* public
rm -f index.html

# Copy example files from /workspace/.toolchain/prototype/gui
if [ -d /workspace/.toolchain/prototype/gui ]; then
  info "Copying example files from prototype/gui..."

  # Copy all .svelte files to src/
  cp -r /workspace/.toolchain/prototype/gui/*.svelte src/ 2>/dev/null || true
  cp -r /workspace/.toolchain/prototype/gui/mod_status src/ 2>/dev/null || true

  # Copy index.html to src/
  cp /workspace/.toolchain/prototype/gui/index.html src/index.html 2>/dev/null || true

  # Copy store.js to gui root (not src/)
  cp /workspace/.toolchain/prototype/gui/store.js src/store.js 2>/dev/null || true

  # Copy vite.config.js
  cp /workspace/.toolchain/prototype/gui/vite.config.js vite.config.js 2>/dev/null || true

  info "Example files copied successfully"
else
  warn "prototype/gui directory not found, using default Vite template"
fi

# Copy static directory with service index.html
info "Copying static directory with service page..."
mkdir -p /workspace/gui/static
if [ -f /workspace/.toolchain/prototype/gui/static/index.html ]; then
  cp /workspace/.toolchain/prototype/gui/static/index.html /workspace/gui/static/index.html
  chmod 644 /workspace/gui/static/index.html
  chown www-data:www-data /workspace/gui/static/index.html
  info "Service page copied to /workspace/gui/static/index.html"
else
  warn "Service page not found in prototype/gui/static, skipping"
fi

# Copy all Svelte module components from prototype/gui to gui/src
if [ -d /workspace/.toolchain/prototype/gui ]; then
  info "Copying Svelte module components from prototype/gui..."

  # Copy all mod_* directories
  for module_dir in /workspace/.toolchain/prototype/gui/mod_*/; do
    if [ -d "$module_dir" ]; then
      module_name=$(basename "$module_dir")
      info "Installing Svelte module: $module_name"
      cp -r "$module_dir" /workspace/gui/src/
    fi
  done
fi

info "Svelte with Vite installed"
cd /workspace

# Setup enabled databases
info "Setting up enabled databases..."
mkdir -p /workspace/data

# Install SQLite3 schemas if enabled
if [ "$SQLITE3_ENABLED" = "y" ]; then
  info "SQLite3 database enabled - installing schemas..."
  DB_FILE="/workspace/data/${PROJECT_NAME}.db"

  # Cleanup: remove existing database to ensure clean state
  if [ -f "$DB_FILE" ]; then
    info "  Removing existing database for clean installation..."
    rm -f "$DB_FILE"
  fi

  touch "$DB_FILE"


  # Apply mod_status schema
  if [ -f /workspace/database/mod_status/sqlite3_install.sql ]; then
    info "  Applying mod_status schema (SQLite3)..."
    cd /workspace/database/mod_status
    /workspace/bin/cmd db -f sqlite3_install.sql || warn "Failed to apply mod_status schema"
    cd /workspace
  fi

  info "SQLite3 database created: $DB_FILE"
fi

# Install MariaDB schemas if enabled
if [ "$MARIADB_ENABLED" = "y" ]; then
  info "MariaDB database enabled - installing schemas..."

  # Check if MariaDB is reachable by testing connection
  if ! mysqladmin ping -h"$MARIADB_CONTAINER" -u"$MARIADB_ROOT_USER" -p"$MARIADB_ROOT_PASSWORD" >/dev/null 2>&1; then
    error "MariaDB is enabled (MARIADB_ENABLED=y) but container '$MARIADB_CONTAINER' is not reachable. Install it with: ./install.sh --mariadb"
  fi

  # Cleanup: drop and recreate database for clean state
  info "  Recreating MySQL database for clean installation..."
  mysql -h"$MARIADB_CONTAINER" -u"$MARIADB_ROOT_USER" -p"$MARIADB_ROOT_PASSWORD" \
    -e "DROP DATABASE IF EXISTS \`$MARIADB_NAME\`; CREATE DATABASE \`$MARIADB_NAME\`;" 2>/dev/null || \
    warn "Failed to recreate MySQL database"


  # Apply mod_status schema
  if [ -f /workspace/database/mod_status/mariadb_install.sql ]; then
    info "  Applying mod_status schema (MySQL)..."
    cd /workspace/database/mod_status
    /workspace/bin/cmd db -f mariadb_install.sql || warn "Failed to apply mod_status schema"
    cd /workspace
  fi

  info "MySQL schemas applied"
fi

# Install PostgreSQL schemas if enabled
if [ "$PGSQL_ENABLED" = "y" ]; then
  info "PostgreSQL database enabled - installing schemas..."

  # Check if PostgreSQL is reachable by testing connection
  if ! pg_isready -h"$PGSQL_CONTAINER" -U"$PGSQL_ROOT_USER" >/dev/null 2>&1; then
    error "PostgreSQL is enabled (PGSQL_ENABLED=y) but container '$PGSQL_CONTAINER' is not reachable. Install it with: ./install.sh --postgres"
  fi

  # Cleanup: drop and recreate database for clean state
  info "  Recreating PostgreSQL database for clean installation..."
  PGPASSWORD="$PGSQL_ROOT_PASSWORD" psql -h"$PGSQL_CONTAINER" -U"$PGSQL_ROOT_USER" -d postgres \
    -c "DROP DATABASE IF EXISTS \"$PGSQL_NAME\";" 2>/dev/null || true
  PGPASSWORD="$PGSQL_ROOT_PASSWORD" psql -h"$PGSQL_CONTAINER" -U"$PGSQL_ROOT_USER" -d postgres \
    -c "CREATE DATABASE \"$PGSQL_NAME\";" 2>/dev/null || warn "Failed to create PostgreSQL database"

  # Create dedicated user (like MariaDB does)
  info "  Creating dedicated PostgreSQL user '$PGSQL_USER'..."
  PGPASSWORD="$PGSQL_ROOT_PASSWORD" psql -h"$PGSQL_CONTAINER" -U"$PGSQL_ROOT_USER" -d postgres \
    -c "DROP USER IF EXISTS \"$PGSQL_USER\";" 2>/dev/null || true
  PGPASSWORD="$PGSQL_ROOT_PASSWORD" psql -h"$PGSQL_CONTAINER" -U"$PGSQL_ROOT_USER" -d postgres \
    -c "CREATE USER \"$PGSQL_USER\" WITH PASSWORD '$PGSQL_PASSWORD';" 2>/dev/null || warn "Failed to create PostgreSQL user"
  PGPASSWORD="$PGSQL_ROOT_PASSWORD" psql -h"$PGSQL_CONTAINER" -U"$PGSQL_ROOT_USER" -d postgres \
    -c "GRANT ALL PRIVILEGES ON DATABASE \"$PGSQL_NAME\" TO \"$PGSQL_USER\";" 2>/dev/null || warn "Failed to grant privileges"
  PGPASSWORD="$PGSQL_ROOT_PASSWORD" psql -h"$PGSQL_CONTAINER" -U"$PGSQL_ROOT_USER" -d "$PGSQL_NAME" \
    -c "GRANT ALL ON SCHEMA public TO \"$PGSQL_USER\";" 2>/dev/null || warn "Failed to grant schema privileges"


  # Apply mod_status schema
  if [ -f /workspace/database/mod_status/postgres_install.sql ]; then
    info "  Applying mod_status schema (PostgreSQL)..."
    cd /workspace/database/mod_status
    /workspace/bin/cmd db -f postgres_install.sql || warn "Failed to apply mod_status schema"
    cd /workspace
  fi

  info "PostgreSQL schemas applied"
fi

# Copy and build mod_status microservice
if [ -d /workspace/.toolchain/prototype/services/mod_status ]; then
  info "Installing mod_status microservice..."

  # Remove existing installation
  rm -rf /workspace/services/mod_status

  # Install
  cp -r /workspace/.toolchain/prototype/services/mod_status /workspace/services/

  # Build the C++ microservice
  /workspace/bin/cmd service build -n mod_status || warn "Failed to build mod_status microservice"

  # Microservice will be started by s6 if enabled
  info "mod_status built successfully. Will be enabled later in setup."
else
  warn "prototype/services/mod_status not found, skipping microservice installation"
fi

# Setup VSCode configuration
install_vscode

# Install Claude Code CLI
install_claude

# Configure ODBC from .env settings
if [ -f /workspace/.toolchain/prototype/odbc/odbc.ini.template ]; then
  info "Configuring ODBC data sources..."
  /workspace/bin/cmd db conf || warn "Failed to configure ODBC"

  # Create symbolic link to odbc.ini in workspace config directory
  info "Creating symbolic link to ODBC configuration..."
  mkdir -p /workspace/conf
  ln -sf /etc/odbc.ini /workspace/conf/odbc.ini
  info "ODBC configuration accessible at /workspace/conf/odbc.ini"
else
  warn "ODBC template not found, skipping ODBC configuration"
fi

info "Setup complete!"
