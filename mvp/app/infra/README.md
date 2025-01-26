# Infrastructure Implementation Guide

## Table of Contents
1. Introduction & Overview  
2. Local Development Environment  
3. Testing Environment & CI Integration  
4. Production Environment with Terraform & RDS  
5. Environment Variables & Secrets Management  
6. Optional Advanced Topics  
7. Roadmap  

---

## 1. Introduction & Overview

• You want a consistent setup so that local development, CI tests, and production deployments all reflect a similar environment.  
• For local dev and CI: use Docker Compose to spin up Postgres containers (and optionally your application container).  
• For production: provision a managed AWS RDS instance using Terraform, ensuring security, scalability, and best practices for production data.  

### Benefits at a Glance
• Minimal environment drift: the same Docker containers (local) and config (CI) reduce "it works on my machine" issues.  
• Reliability & scaling in production: Terraform handles the AWS RDS database, with robust failover and AWS-managed backups.  
• Clear separation: local/CI environment is fully containerized, production environment is fully managed.

---

## 2. Local Development Environment

1. Create (or extend) a docker-compose.yml with:  
   • A Postgres container (e.g., "dev-db").  
   • (Optionally) an application container (e.g., "web") if you prefer your dev environment fully containerized.

2. Configure environment variables (DB_NAME, DB_USER, DB_PASSWORD, etc.) as needed. For local dev, store them in a .env file (excluded from version control). For tests, use a separate .env.test.

3. Decide on volume persistence:  
   • Ephemeral approach: No volumes → Each time you run docker-compose up, you get a fresh DB. Great for quick resets and minimal manual cleanup, but data is lost on container removal.  
   • Persistent approach: Named volume → Your DB data persists between sessions. Great for iterative dev, but you'll need to drop/migrate data if your schema changes frequently.

4. Spin up the development database container and start your dev server:  
   • docker-compose up -d dev-db  
   • npm install (or yarn, pnpm, etc.)  
   • npm run dev  

   Make sure your "DATABASE_URL" (or equivalent) points to the container (e.g. "postgres://postgres:password@localhost:5432/app").

   > **Note**: The old dev.sh script is no longer needed—Docker Compose manages your local database.

5. Use Drizzle for migrations:
   - npm run db:generate → Generate migrations
   - npm run db:migrate → Apply migrations
   - npm run db:seed → (Optional) seed dev database

Example snippet (focusing on the DB):

```yaml:docker-compose.yml
version: "3.9"

services:
  dev-db:
    image: postgres:15
    container_name: dev-db
    environment:
      POSTGRES_DB: ${DB_NAME:-app}
      POSTGRES_USER: ${DB_USER:-postgres}
      POSTGRES_PASSWORD: ${DB_PASSWORD:-password}
    ports:
      - "5432:5432"
    # volumes:
    #   - dev-db-data:/var/lib/postgresql/data
```

---

## 3. Testing Environment & CI Integration

### 3.1 Local Testing

• You can add a second Postgres service called "test-db" in the same docker-compose.yml (or a separate file).  
• By default, you might map container port 5432 to host port 5433 for the test DB.  
• Use a .env.test file to set TEST_DB_NAME, TEST_DB_USER, etc.

Example snippet:

```yaml:docker-compose.yml
test-db:
  image: postgres:15
  container_name: test-db
  environment:
    POSTGRES_DB: ${TEST_DB_NAME:-app_test}
    POSTGRES_USER: ${TEST_DB_USER:-postgres}
    POSTGRES_PASSWORD: ${TEST_DB_PASSWORD:-password}
  ports:
    - "5433:5432"
```

Local test steps:
1. docker-compose up -d test-db  
2. Set NODE_ENV=test and DATABASE_URL pointing to localhost:5433/app_test.  
3. Run npm test (or your test command).  
4. docker-compose down if you want to tear it down afterwards.

Alternatively, you can separate dev and test Docker Compose configurations:
- docker-compose.yml → for dev  
- docker-compose.test.yml → for test  
This avoids confusion about which service is currently running if you only need one at a time.

### 3.2 CI with Docker Compose

In your CI workflow (GitHub Actions example):

```yaml:.github/workflows/ci.yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Check out repo
        uses: actions/checkout@v3

      - name: Install Docker Compose
        run: sudo apt-get update && sudo apt-get install -y docker-compose

      - name: Spin up test-db
        run: docker-compose up -d test-db

      - name: Wait for DB readiness
        run: npx wait-on tcp:localhost:5433

      - name: Install dependencies & test
        run: |
          npm install
          npm run db:migrate:test # optional step for migrations
          npm run test

      - name: Tear down containers
        if: always()
        run: docker-compose down --volumes
```

Notes:
• "wait-on" ensures the container is fully ready before tests begin.  
• If you need integration tests that also require your web container, do docker-compose up -d test-db web.  
• If you separate your Compose files (docker-compose.test.yml), run docker-compose -f docker-compose.test.yml up -d test-db.

---

## 4. Production Environment with Terraform & RDS

1. **Terraform State**  
   • Store your Terraform state in a remote backend (e.g., S3 with a DynamoDB lock table). This ensures your team can collaborate without overwriting each other's changes.  
   • Example backend block:

     ```hcl
     terraform {
       backend "s3" {
         bucket         = "my-terraform-state"
         key            = "rds/terraform.tfstate"
         region         = "us-east-1"
         dynamodb_table = "terraform-locks"
       }
     }
     ```

2. **AWS RDS Resource**  
   • Use Terraform to define a Postgres RDS instance:

     ```hcl:infrastructure/db/main.tf
     resource "aws_db_instance" "this" {
       identifier             = "my-prod-db"
       allocated_storage      = 20
       engine                 = "postgres"
       engine_version         = "15.2"
       instance_class         = "db.t3.medium"
       vpc_security_group_ids = [aws_security_group.db_access.id]
       db_subnet_group_name   = data.aws_db_subnet_group.default.name
       name                   = var.db_name
       username               = var.db_user
       password               = var.db_password
       skip_final_snapshot    = false
     }

     output "rds_endpoint" {
       value = aws_db_instance.this.endpoint
     }
     ```

   • The "skip_final_snapshot" can be set to false (default) to ensure AWS automatically creates a final snapshot before deleting the instance—important for production data.  
   • Provide `db_user`, `db_password`, and other variables securely (e.g., stored in GitHub Actions secrets, a Terraform Cloud workspace, or an environment variable pipeline).

3. **Production Deployment Steps**  
   • Run terraform init/plan/apply in your infrastructure repository or pipeline.  
   • Once RDS is provisioned, Terraform outputs the DB endpoint (something like my-prod-db.xxxxxxxx.us-east-1.rds.amazonaws.com).  
   • In your production environment (e.g., ECS, Kubernetes, or other hosting environment), set DATABASE_URL to reference that RDS endpoint. For example:  
     postgres://<db_user>:<db_password>@my-prod-db.xxxxxxxx.us-east-1.rds.amazonaws.com:5432/<db_name>

4. **Security Considerations**  
   • Ensure your security groups allow inbound traffic only from the application's ECS tasks or Kubernetes pods, not the open internet.  
   • Use AWS Secrets Manager or Terraform variables for credentials, never commit them to version control.

---

## 5. Environment Variables & Secrets Management

• Keep local dev secrets in .env, test secrets in .env.test, and exclude them from version control.  
• For CI, use encrypted secrets in your pipeline.  
• For production, rely on Terraform-managed secrets or AWS Secrets Manager, referencing them at runtime.  
• Rotate DB passwords regularly for security; Terraform or AWS Secrets Manager can automate or at least simplify the process.

---

## 6. Optional Advanced Topics

### 6.1 Migrations & Schema Management
• If you use a migration tool (e.g., Prisma Migrate, Flyway, Sequelize, Drizzle, etc.), add a step in both local dev and CI to apply new migrations.  
• In production, your deployment pipeline might run migrations after spinning up the new service but before switching traffic over, ensuring zero-downtime upgrades.

### 6.2 Monitoring & Logging
• Use CloudWatch or another monitoring tool to keep an eye on query volumes, CPU usage, and disk space in RDS.  
• For container logs: locally, docker-compose logs -f dev-db (and/or web) to troubleshoot issues. In CI, logs will persist only while the job is running unless you explicitly upload them as artifacts.

### 6.3 Terraform State & Security
• Always use a remote backend for team-based Terraform usage.  
• Lock state files to prevent simultaneous updates.  
• Make sure your Terraform files don't commit plaintext secrets. Use variables from AWS SSM / Secrets Manager or environment variables.

### 6.4 Named Networks & Docker Profiles
• If you plan to run multiple Compose stacks or advanced networking, consider a named network:

  ```yaml
  networks:
    my_network:
      driver: bridge

  services:
    dev-db:
      networks:
        - my_network
    test-db:
      networks:
        - my_network
  ```

• In Docker Compose v2.4+, you can define profiles that let you selectively spin up dev-db or test-db. For instance:

  ```yaml
  profiles:
    - dev
    - test

  services:
    dev-db:
      profiles: ["dev"]
    test-db:
      profiles: ["test"]
  ```

This helps avoid accidentally running both dev-db and test-db when you only need one.

---

## 7. Roadmap

Below is a tentative roadmap to guide ongoing infrastructure improvements:

1. Optimize Local Dev & CI  
   - Streamline Docker Compose configurations (dev vs. test).  
   - Add efficient database seeding for test environments.  

2. Enhance Production Resilience  
   - Investigate multi-AZ deployments of RDS.  
   - Configure Terraform for zero-downtime upgrades.  

3. Security & Compliance  
   - Integrate AWS Secrets Manager for automated credential rotation.  
   - Add more robust monitoring and alerts (e.g., CPU usage, slow queries).  

4. Advanced Automation & Observability  
   - Implement Infrastructure as Code linting and testing (e.g., checkov, Terraform validate).  
   - Explore centralized logging and metrics with tools like Datadog or Grafana.

---

# Final Takeaways

• Use Docker Compose for local development and CI, ensuring consistent images and environment variables.  
• Keep dev and test databases separate to reduce data collisions and ensure each environment is fresh.  
• In production, rely on Terraform to provision an AWS RDS instance, storing credentials and endpoint details securely.  
• Incorporate the feedback items—like ephemeral vs. persistent volumes, clarifying your Terraform backend, and adopting best practices for migrations—to ensure a robust, production-ready setup.  

This approach provides local/CI consistency via Docker while leveraging AWS best practices (RDS + Terraform) for a highly available, secure production database.
