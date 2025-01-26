# TODO

Below are some upcoming tasks and improvements to track for our environment:

## 1. Environment Configuration
- [x] Evaluate ephemeral vs. persistent volumes for development
- [x] Create or refine seed scripts for quick local DB resets
- [x] Document volume configuration and seed workflow
- [x] Confirm Drizzle migrations run smoothly for both dev and test databases
- [x] Verify environment variables align in src/env.js
- [ ] Add environment variable validation tests
- [ ] Create environment variable templates (.env.example, .env.test.example)

## 2. Testing Infrastructure
- [x] Consolidate test configuration
- [x] Ensure proper database pool management in tests
- [x] Confirm vitest picks up TEST_DATABASE_URL correctly
- [ ] Add more thorough integration tests
- [ ] Implement test data factories
- [ ] Add performance benchmarks for database operations
- [ ] Improve test isolation and parallelization

## 3. Database Management
- [x] Implement proper connection pooling
- [x] Add connection retry logic
- [x] Ensure clean connection state between tests
- [ ] Add database health checks
- [ ] Implement query logging for development
- [ ] Add database migration rollback tests
- [ ] Create database backup/restore scripts

## 4. Documentation
- [x] Update LOCAL.md with clear environment setup instructions
- [x] Document database configuration options
- [ ] Add API documentation
- [ ] Create contributor guidelines
- [ ] Add architecture diagrams
- [ ] Document testing strategies and patterns

## 5. CI/CD Pipeline (Future)
- [ ] Set up GitHub Actions workflow
- [ ] Add automated migrations and rollback strategy
- [ ] Implement deployment previews
- [ ] Add automated environment provisioning
- [ ] Set up continuous deployment

## 6. Production Infrastructure (Future)
- [ ] Evaluate multi-AZ RDS deployment
- [ ] Implement zero-downtime deployments
- [ ] Set up monitoring and alerting
- [ ] Configure automated backups
- [ ] Implement disaster recovery procedures

## 7. Security
- [ ] Implement database connection encryption
- [ ] Add rate limiting
- [ ] Set up security scanning
- [ ] Implement audit logging
- [ ] Add database access monitoring

Feel free to add, remove, or adjust these items as priorities evolve. 