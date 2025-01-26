# Local Development Overview

This document outlines how to run the project locally using Docker Compose and environment files.

## Environment Files

### Development (.env)
- Used for local development
- Contains database configuration:
  ```
  DATABASE_URL=postgres://postgres:password@localhost:5432/app
  DB_NAME=app
  DB_USER=postgres
  DB_PASSWORD=password
  ```
- Contains authentication configuration:
  ```
  AUTH_SECRET=your_auth_secret
  AUTH_DISCORD_ID=your_discord_id
  AUTH_DISCORD_SECRET=your_discord_secret
  NEXTAUTH_URL=http://localhost:3000
  NEXTAUTH_SECRET=your_nextauth_secret
  ```

### Testing (.env.test)
- Used specifically for testing
- Contains separate database configuration:
  ```
  DATABASE_URL=postgres://postgres:password@localhost:5433/app_test
  TEST_DATABASE_URL=postgres://postgres:password@localhost:5433/app_test
  DB_NAME=app_test
  DB_USER=postgres
  DB_PASSWORD=password
  ```
- Used automatically when running tests via `npm run test`

## Docker Setup

Docker Compose manages two separate PostgreSQL instances:

### Development Database (dev-db)
- Port: 5432
- Uses environment variables from .env
- Optional persistent storage via Docker volumes
- Start with: `npm run docker:up`

### Test Database (test-db)
- Port: 5433
- Uses environment variables from .env.test
- Uses tmpfs for ephemeral storage
- Automatically managed by test suite
- Clean state for each test run

## Database Management

### Initial Setup
1. Start the containers:
   ```bash
   npm run docker:up
   ```
2. Apply migrations:
   ```bash
   npm run db:migrate
   ```
3. (Optional) Seed the development database:
   ```bash
   npm run db:seed
   ```

### Storage Options

#### Ephemeral Storage (Default)
- Data is cleared when container is removed
- Ideal for reproducible development environments
- Default configuration in docker-compose.yml

#### Persistent Storage
To enable, uncomment these lines in docker-compose.yml:
```yaml
volumes:
  - dev-db-data:/var/lib/postgresql/data
```

## Testing Workflow

1. Ensure .env.test is properly configured
2. Run the test suite:
   ```bash
   npm run test
   ```
   This will:
   - Start test-db container if not running
   - Run migrations on test database
   - Execute tests with proper isolation
   - Clean up test data after each test

For development mode:
```bash
npm run test:watch
```

## Available Scripts

### Development
- `npm run dev` - Start Next.js development server
- `npm run docker:up` - Start Docker containers
- `npm run docker:down` - Stop Docker containers
- `npm run docker:restart` - Restart Docker containers

### Database
- `npm run db:migrate` - Apply database migrations
- `npm run db:seed` - Seed development database
- `npm run db:studio` - Open Drizzle Studio

### Testing
- `npm run test` - Run test suite
- `npm run test:watch` - Run tests in watch mode

## Troubleshooting

### Database Connection Issues
1. Verify Docker containers are running:
   ```bash
   docker ps
   ```
2. Check correct ports:
   - Development: 5432
   - Test: 5433
3. Ensure environment variables match docker-compose.yml

### Test Database Issues
- Test database is ephemeral by design
- Each container restart provides a clean state
- No need to manually clear test data

### Seed Script Errors
1. Ensure TypeScript is properly configured
2. Check DATABASE_URL matches your environment
3. Verify Docker containers are healthy

For more detailed configuration, see:
- docker-compose.yml
- drizzle.config.ts
- src/env.js