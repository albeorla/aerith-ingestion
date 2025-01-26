#!/usr/bin/env bash
# Use this script to start a docker container for a local development database

# TO RUN ON WINDOWS:
# 1. Install WSL (Windows Subsystem for Linux) - https://learn.microsoft.com/en-us/windows/wsl/install
# 2. Install Docker Desktop for Windows - https://docs.docker.com/docker-for-windows/install/
# 3. Open WSL - `wsl`
# 4. Run this script - `./dev.sh`

# On Linux and macOS you can run this script directly - `./dev.sh`

DB_CONTAINER_NAME="app-postgres"
CLEANUP_ON_EXIT=true

# Function to clean up database resources
cleanup_database() {
  if [ "$CLEANUP_ON_EXIT" = true ]; then
    echo "🧹 Cleaning up existing database resources..."
    
    # Check if container exists and is running
    if [ "$(docker ps -q -f name=$DB_CONTAINER_NAME)" ]; then
      echo "Stopping running container..."
      docker kill $DB_CONTAINER_NAME > /dev/null 2>&1
    fi

    # Check if container exists regardless of state
    if [ "$(docker ps -aq -f name=$DB_CONTAINER_NAME)" ]; then
      echo "Removing existing container..."
      docker rm -f $DB_CONTAINER_NAME > /dev/null 2>&1
    fi

    # Check if volume exists
    if [ "$(docker volume ls -q -f name=${DB_CONTAINER_NAME}-data)" ]; then
      echo "Removing existing volume..."
      docker volume rm -f ${DB_CONTAINER_NAME}-data > /dev/null 2>&1
    fi

    echo "✨ Cleanup complete!"
  fi
}

handle_error() {
  echo "❌ Error occurred during database setup"
  CLEANUP_ON_EXIT=true
  cleanup_database
  exit 1
}

# Set up error handling
trap handle_error ERR

# Check Docker installation and daemon
if ! [ -x "$(command -v docker)" ]; then
  echo -e "❌ Docker is not installed. Please install docker and try again.\nDocker install guide: https://docs.docker.com/engine/install/"
  exit 1
fi

if ! docker info > /dev/null 2>&1; then
  echo "❌ Docker daemon is not running. Please start Docker and try again."
  exit 1
fi

# Clean up existing resources
CLEANUP_ON_EXIT=true
cleanup_database
CLEANUP_ON_EXIT=false

# import env variables from .env
if [ ! -f ".env" ]; then
  echo "❌ .env file not found. Please create one from .env.example"
  exit 1
fi

set -a
source .env

DB_PASSWORD=$(echo "$DATABASE_URL" | awk -F':' '{print $3}' | awk -F'@' '{print $1}')
DB_PORT=$(echo "$DATABASE_URL" | awk -F':' '{print $4}' | awk -F'\/' '{print $1}')

if [ "$DB_PASSWORD" = "password" ]; then
  echo "⚠️  You are using the default database password"
  read -p "Should we generate a random password for you? [y/N]: " -r REPLY
  if ! [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Please change the default password in the .env file and try again"
    exit 1
  fi
  # Generate a random URL-safe password
  DB_PASSWORD=$(openssl rand -base64 12 | tr '+/' '-_')
  sed -i -e "s#:password@#:$DB_PASSWORD@#" .env
fi

echo "🚀 Starting database container..."
if ! docker run -d \
  --name $DB_CONTAINER_NAME \
  -e POSTGRES_USER="postgres" \
  -e POSTGRES_PASSWORD="$DB_PASSWORD" \
  -e POSTGRES_DB=app \
  -p "$DB_PORT":5432 \
  -v ${DB_CONTAINER_NAME}-data:/var/lib/postgresql/data \
  docker.io/postgres; then
  echo "❌ Failed to start database container"
  handle_error
fi

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
RETRIES=30
DELAY=1
count=0
until docker exec $DB_CONTAINER_NAME pg_isready > /dev/null 2>&1; do
  echo -n "."
  sleep $DELAY
  count=$((count + 1))
  if [ $count -eq $RETRIES ]; then
    echo "❌ Database failed to start after $((RETRIES * DELAY)) seconds"
    handle_error
  fi
done
echo -e "\n✅ Database is ready!"

# Generate schema if drizzle directory doesn't exist
if [ ! -d "drizzle" ]; then
  echo "📝 Generating database schema..."
  if ! npm run db:generate; then
    echo "❌ Failed to generate schema"
    handle_error
  fi
fi

# Run migrations
echo "🔄 Running database migrations..."
if ! npm run db:push; then
  echo "❌ Failed to run migrations"
  handle_error
fi

# Seed the database
echo "🌱 Seeding the database..."
if ! npm run db:seed; then
  echo "❌ Failed to seed database"
  handle_error
fi

echo "🎉 Database setup complete!"
CLEANUP_ON_EXIT=false
exit 0