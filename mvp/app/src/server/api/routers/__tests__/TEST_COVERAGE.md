# API Router Test Coverage

## Overview
This document outlines the behaviors and scenarios we verify through our test suite.

## Core Entity Tests

### Goal Router Tests
- **Creation**
  - ✓ Creates goals with valid data
  - ✓ Validates required fields (name, visionId)
  - ✓ Enforces future target dates
  - ✓ Prevents duplicate names within vision
  - ✓ Requires active parent vision

- **Updates**
  - ✓ Updates basic fields (name, description)
  - ✓ Validates status transitions (active -> achieved -> archived)
  - ✓ Prevents invalid status values
  - ✓ Handles non-existent goals
  - ✓ Validates target date changes

- **Deletion**
  - ✓ Deletes goals without dependencies
  - ✓ Prevents deletion with active areas
  - ✓ Cascades deletion properly

- **Queries**
  - ✓ Lists goals for vision
  - ✓ Retrieves individual goals
  - ✓ Filters by status
  - ✓ Orders by creation date

### Project Router Tests
- **Creation**
  - ✓ Creates projects with valid data
  - ✓ Validates required fields
  - ✓ Prevents duplicate names within area
  - ✓ Requires active parent area

- **Updates**
  - ✓ Updates basic fields
  - ✓ Validates status transitions
  - ✓ Prevents completion with active tasks
  - ✓ Handles non-existent projects

- **Deletion**
  - ✓ Deletes projects without dependencies
  - ✓ Prevents deletion with active tasks
  - ✓ Cascades deletion properly

- **Queries**
  - ✓ Lists projects for area
  - ✓ Retrieves individual projects
  - ✓ Filters by status
  - ✓ Orders by creation date

### Task Router Tests
- **Creation**
  - ✓ Creates tasks with valid data
  - ✓ Validates required fields
  - ✓ Prevents duplicate names within project
  - ✓ Requires active parent project

- **Updates**
  - ✓ Updates basic fields
  - ✓ Validates status transitions
  - ✓ Handles non-existent tasks

- **Deletion**
  - ✓ Deletes tasks
  - ✓ Cascades deletion properly

- **Queries**
  - ✓ Lists tasks for project
  - ✓ Retrieves individual tasks
  - ✓ Filters by status
  - ✓ Orders by creation date

## Authorization Tests
- ✓ Prevents unauthorized access to all routes
- ✓ Validates user ownership of resources
- ✓ Enforces proper session handling

## Data Integrity Tests
- ✓ Maintains referential integrity
- ✓ Handles concurrent operations
- ✓ Validates data constraints
- ✓ Enforces business rules

## Areas Needing Coverage

### Frontend Components
- [ ] Page rendering
- [ ] Component state management
- [ ] User interactions
- [ ] Form validations
- [ ] Error displays
- [ ] Loading states
- [ ] Responsive behavior
- [ ] Accessibility

### API Routes
- [ ] TRPC endpoint availability
- [ ] Request validation
- [ ] Error handling
- [ ] Rate limiting
- [ ] Authentication middleware
- [ ] Session handling

### Auth Flow
- [ ] User registration
- [ ] Login/logout
- [ ] Session persistence
- [ ] Token refresh
- [ ] Password reset
- [ ] OAuth provider integration
- [ ] Permission checks
- [ ] Role-based access 