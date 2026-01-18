#!/bin/sh
set -e

PROJECT_NAME=$(basename "$(pwd)")
INSTALL_MARIADB=false
INSTALL_PGSQL=false
RUN_ENV_SETUP=false

# Prints error message to stderr and exits with code 1
error() { printf 'ERROR: %s\n' "$1" >&2; exit 1; }

# Prints info message to stdout
info() { printf 'INFO: %s\n' "$1"; }

# Prints warning message to stderr
warn() { printf 'WARNING: %s\n' "$1" >&2; }

# Portable sed -i (works on both Linux and macOS)
# Usage: sed_inplace 's/pattern/replacement/' file
sed_inplace() {
  if [ "$(uname)" = "Darwin" ]; then
    # macOS (BSD sed) requires empty string for backup extension
    sed -i '' "$@"
  else
    # Linux (GNU sed)
    sed -i "$@"
  fi
}

# Shows usage and available options
show_help() {
  cat << EOF
Usage: ./install.sh [OPTIONS]

Options:
  --mariadb    Install MariaDB container
  --postgres   Install PostgreSQL container
  --env        Run setup.sh inside the container
  --help       Show this help message
EOF
  exit 0
}

# Creates .env configuration file
# - Skips if .env already exists
# - Sets project name, ports, database configs
# - Default DB: SQLite3 at /workspace/data/${PROJECT_NAME}.db
# - Optional DBs: PostgreSQL (port 2340), MariaDB (port 2330)
create_env_file() {
  if [ -f .env ]; then
    info ".env already exists"
    return 0
  fi
  # Generate JWT secret
  JWT_SECRET=$(openssl rand -hex 32 2>/dev/null || echo "change-this-secret-key-in-production-$(date +%s)")

  # Copy template and substitute placeholders
  if [ ! -f prototype/env.example ]; then
    error "prototype/env.example not found"
  fi

  cp prototype/env.example .env
  sed_inplace "s|{{PROJECT_NAME}}|$PROJECT_NAME|g" .env
  sed_inplace "s|{{JWT_SECRET}}|$JWT_SECRET|g" .env
  set -a  # Enable auto-export
  . ./.env
  set +a  # Disable auto-export
  info "Created .env file"
}

# Builds custom Docker image with s6-overlay
# - Image name: ${PROJECT_NAME}-dev:latest
# - Base: Ubuntu 24.04
# - Adds: s6-overlay v3.2.0.0
# - Skips if image already exists
build_docker_image() {
  info "Building custom Docker image with s6-overlay..."

  # Check if image already exists
  if docker images --format "{{.Repository}}:{{.Tag}}" | grep -q "^${UBUNTU_IMAGE}$"; then
    info "Docker image already exists: $UBUNTU_IMAGE"
    return 0
  fi

  # Check if Dockerfile exists
  [ ! -f "Dockerfile" ] && error "Dockerfile not found in current directory"

  # Build the image
  docker build -t "$UBUNTU_IMAGE" . >/dev/null 2>&1 || error "Failed to build Docker image"
  info "Docker image built successfully: $UBUNTU_IMAGE"
}

# Creates development container
# - Network: ${NETWORK} (<project>-net)
# - Container: ${PROJECT_NAME} (project name)
# - Image: ${PROJECT_NAME}-dev:latest (with s6-overlay)
# - Volume: $(pwd) -> /workspace
# - Ports: ${PORT}:2310 (HTTP), ${TLS_PORT}:2443 (HTTPS), ${VITE_PORT}:5173 (Vite)
# - Starts existing container if present
create_dev_container() {
  # Create network
  docker network ls --format "{{.Name}}" | grep -q "^${NETWORK}$" || \
    docker network create "$NETWORK" >/dev/null 2>&1 || error "Failed to create network"

  if docker ps -a --format "{{.Names}}" | grep -q "^${PROJECT_NAME}$"; then
    docker ps --format "{{.Names}}" | grep -q "^${PROJECT_NAME}$" && { info "Container already running"; return 0; }
    docker start "$PROJECT_NAME" >/dev/null 2>&1 || error "Failed to start container"
    info "Container started"
    return 0
  fi

  # Image must exist (built by build_docker_image)
  docker images --format "{{.Repository}}:{{.Tag}}" | grep -q "^${UBUNTU_IMAGE}$" || \
    error "Docker image not found: $UBUNTU_IMAGE. Run ./install.sh first."

  # Run container without command - s6-overlay ENTRYPOINT /init will start
  docker run -d --name "$PROJECT_NAME" --network "$NETWORK" \
    -v "$(pwd):/workspace" -w /workspace \
    -e TZ=Europe/Rome \
    -p "$API_PORT:2310" -p "$TLS_PORT:2443" -p "$VITE_PORT:5173" \
    "$UBUNTU_IMAGE" >/dev/null 2>&1 || error "Failed to create container"

  info "Container created"
}

# Reorganizes project structure
# - Creates '.toolchain/' directory
# - Moves .git/, setup.sh, install.sh, prototype/ into .toolchain/
# - Creates symlinks for prototype/ and setup.sh in current directory
set_project_structure() {
  info "Setting project structure..."

  # Skip if already reorganized
  if [ -d ".toolchain" ] && [ -L "install" ] && [ -L "setup.sh" ]; then
    info "Project already reorganized"
    return 0
  fi

  # Create .toolchain directory
  mkdir -p .toolchain

  # Move .git if exists
  if [ -d ".git" ]; then
    info "Moving .git to .toolchain/"
    mv .git .toolchain/ || warn "Failed to move .git"
  fi

  # Copy install.sh
  if [ -f "install.sh" ]; then
    info "Copying install.sh to .toolchain/"
    cp install.sh .toolchain/
  fi

  # Move setup.sh
  if [ -f "setup.sh" ]; then
    info "Moving setup.sh to .toolchain/"
    cp setup.sh .toolchain/
    rm -f setup.sh
  fi

  # Move prototype directory
  if [ -d "prototype" ]; then
    info "Moving prototype/ to .toolchain/"
    cp -r prototype .toolchain/
    rm -rf prototype
  fi

  # Move release directory
  if [ -d "release" ]; then
    info "Moving release/ to .toolchain/"
    cp -r release .toolchain/
    rm -rf release
  fi

  # Move Dockerfile
  if [ -f "Dockerfile" ]; then
    info "Moving Dockerfile to .toolchain/"
    mv Dockerfile .toolchain/
  fi

  # Move PROJECT.md
  if [ -f "PROJECT.md" ]; then
    info "Moving PROJECT.md to .toolchain/"
    mv PROJECT.md .toolchain/
  fi

  # Move TODO.md
  if [ -f "TODO.md" ]; then
    info "Moving TODO.md to .toolchain/"
    mv TODO.md .toolchain/
  fi

  # Create symlinks
  info "Creating symbolic links..."
  ln -sf .toolchain/setup.sh setup.sh || error "Failed to create setup.sh symlink"

  info "Done."
}

# Creates MariaDB container
# - Network: ${NETWORK} (<project>-net)
# - Container: ${MARIADB_CONTAINER} (<project>-mariadb)
# - Volume: ${MARIADB_VOLUME} (<project>-mariadb-data)
# - Port: ${MARIADB_PORT}:3306 (default 2330:3306)
# - Credentials: user=${MARIADB_USER}, password=secret, root password=root
# - Starts existing container if present
create_mariadb_container() {
  docker network ls --format "{{.Name}}" | grep -q "^${NETWORK}$" || \
    docker network create "$NETWORK" >/dev/null 2>&1 || { warn "Failed to create network"; return 1; }

  if docker ps -a --format "{{.Names}}" | grep -q "^${MARIADB_CONTAINER}$"; then
    docker ps --format "{{.Names}}" | grep -q "^${MARIADB_CONTAINER}$" && { info "MariaDB already running"; return 0; }
    docker start "$MARIADB_CONTAINER" >/dev/null 2>&1 || { warn "Failed to start MariaDB"; return 1; }
    info "MariaDB started"
    return 0
  fi

  docker images --format "{{.Repository}}:{{.Tag}}" | grep -q "^${MARIADB_IMAGE}$" || \
    docker pull "$MARIADB_IMAGE" >/dev/null 2>&1

  docker run -d --name "$MARIADB_CONTAINER" --network "$NETWORK" \
    -e MYSQL_ROOT_PASSWORD="$MARIADB_ROOT_PASSWORD" \
    -e MYSQL_DATABASE="$MARIADB_NAME" \
    -e MYSQL_USER="$MARIADB_USER" \
    -e MYSQL_PASSWORD="$MARIADB_PASSWORD" \
    -p "$MARIADB_PORT:3306" \
    -v "$MARIADB_VOLUME:/var/lib/mysql" \
    "$MARIADB_IMAGE" >/dev/null 2>&1 || { warn "Failed to create MariaDB"; return 1; }

  info "MariaDB created"
}

# Creates PostgreSQL container
# - Network: ${NETWORK} (<project>-net)
# - Container: ${PGSQL_CONTAINER} (<project>-postgres)
# - Volume: ${PGSQL_VOLUME} (<project>-postgres-data)
# - Port: ${PGSQL_PORT}:5432 (default 2340:5432)
# - Credentials: user=postgres, password=postgres
# - Starts existing container if present
create_pgsql_container() {
  docker network ls --format "{{.Name}}" | grep -q "^${NETWORK}$" || \
    docker network create "$NETWORK" >/dev/null 2>&1 || { warn "Failed to create network"; return 1; }

  if docker ps -a --format "{{.Names}}" | grep -q "^${PGSQL_CONTAINER}$"; then
    docker ps --format "{{.Names}}" | grep -q "^${PGSQL_CONTAINER}$" && { info "PostgreSQL already running"; return 0; }
    docker start "$PGSQL_CONTAINER" >/dev/null 2>&1 || { warn "Failed to start PostgreSQL"; return 1; }
    info "PostgreSQL started"
    return 0
  fi

  docker images --format "{{.Repository}}:{{.Tag}}" | grep -q "^${PGSQL_IMAGE}$" || \
    docker pull "$PGSQL_IMAGE" >/dev/null 2>&1

  docker run -d --name "$PGSQL_CONTAINER" --network "$NETWORK" \
    -e POSTGRES_USER="$PGSQL_ROOT_USER" \
    -e POSTGRES_PASSWORD="$PGSQL_ROOT_PASSWORD" \
    -p "$PGSQL_PORT:5432" \
    -v "$PGSQL_VOLUME:/var/lib/postgresql" \
    "$PGSQL_IMAGE" >/dev/null 2>&1 || { warn "Failed to create PostgreSQL"; return 1; }

  info "PostgreSQL created"
}

# Runs setup.sh inside the container
# - Loads .env to get container name
# - Checks if container is running
# - Executes /workspace/setup.sh via docker exec
run_env_setup() {
  [ ! -f .env ] && error ".env file not found. Run ./install.sh first to create the environment"

  # Load environment variables to get container name
  set -a  # Enable auto-export
  . ./.env
  set +a  # Disable auto-export

  # Check if container exists
  if ! docker ps -a --format "{{.Names}}" | grep -q "^${PROJECT_NAME}$"; then
    error "Container '$PROJECT_NAME' not found. Run ./install.sh first to create the container"
  fi

  # Check if container is running
  if ! docker ps --format "{{.Names}}" | grep -q "^${PROJECT_NAME}$"; then
    info "Container '$PROJECT_NAME' is not running. Starting it..."
    docker start "$PROJECT_NAME" >/dev/null 2>&1 || error "Failed to start container"
    sleep 2
  fi

  info "Running setup.sh inside container '$PROJECT_NAME'..."
  docker exec "$PROJECT_NAME" /workspace/setup.sh || error "Failed to run setup.sh inside container"
  info "Setup completed successfully"

  # Restart container to apply all changes and start enabled services
  info "Restarting container '$PROJECT_NAME' to apply changes..."
  docker restart "$PROJECT_NAME" >/dev/null 2>&1 || warn "Failed to restart container"
  info "Container restarted. Services should now be running."
}

[ -f /.dockerenv ] || [ -n "$CONTAINER" ] && error "Cannot run inside container"
command -v docker >/dev/null 2>&1 || error "Docker not found"
docker version >/dev/null 2>&1 || error "Docker daemon not running"

while [ $# -gt 0 ]; do
  case $1 in
    --help|-h) show_help ;;
    --mariadb) INSTALL_MARIADB=true; shift ;;
    --postgres) INSTALL_PGSQL=true; shift ;;
    --env) RUN_ENV_SETUP=true; shift ;;
    *) error "Unknown option: $1" ;;
  esac
done

# Count how many options are enabled
OPTIONS_COUNT=0
[ "$INSTALL_MARIADB" = "true" ] && OPTIONS_COUNT=$((OPTIONS_COUNT + 1))
[ "$INSTALL_PGSQL" = "true" ] && OPTIONS_COUNT=$((OPTIONS_COUNT + 1))
[ "$RUN_ENV_SETUP" = "true" ] && OPTIONS_COUNT=$((OPTIONS_COUNT + 1))

[ $OPTIONS_COUNT -gt 1 ] && error "Cannot specify multiple options. Use --help for usage"

[ "$INSTALL_MARIADB" = "true" ] && {
  create_env_file;
  create_mariadb_container;
  exit 0;
}

[ "$INSTALL_PGSQL" = "true" ] && {
  create_env_file;
  create_pgsql_container;
  exit 0;
}

[ "$RUN_ENV_SETUP" = "true" ] && {
  run_env_setup;
  exit 0;
}

info "Installing $PROJECT_NAME..."
create_env_file
build_docker_image
create_dev_container
set_project_structure
info "Done."
