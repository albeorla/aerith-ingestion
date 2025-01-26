# Aerith Ingestion MVP Product Requirements Document

## Project Structure
```
mvp/
  app/           # Next.js application
    src/         # Source code
      server/    # Server-side code
        db/      # Database layer
          schema/  # Database schemas
            auth.ts          # Authentication schemas ✅
            purpose-vision.ts # Purpose & Vision schemas ✅
            goals-areas.ts   # Goals & Areas schemas ✅
            projects-tasks.ts # Projects & Tasks schemas ✅
          seed.ts   # Database seeding script ✅
    dev.sh      # Database management script ✅
    drizzle/     # Database migrations
    public/      # Static assets
```

## Primary Goal

Create a complete GTD (Getting Things Done) implementation covering all Horizons of Focus, with a modern web interface.

## Core Entities

### Common Entity Pattern ✅
All entities share base properties:
```typescript
{
    id: uuid primary key,
    userId: varchar(255) references users(id) on delete cascade,
    name: varchar(100) not null,
    description: text,
    status: specific_enum,
    targetDate: timestamp with time zone optional,
    createdAt: timestamp with time zone not null default current_timestamp,
    updatedAt: timestamp with time zone not null default current_timestamp
}
```

### Horizon 5: Purpose & Principles (50,000 ft) ✅
```typescript
purposes {
    ...common_fields,
    status: enum('active', 'archived')
}
```
- Life purpose and core values
- No parent entity
- No target date
- Unique name per user

### Horizon 4: Vision (40,000 ft) ✅
```typescript
visions {
    ...common_fields,
    purposeId: uuid references purposes(id) on delete cascade,
    status: enum('active', 'achieved', 'archived'),
    targetDate: timestamp with time zone // 3-5 year timeframe
}
```
- Long-term outcomes
- Unique name per user
- Indexed by target date

### Horizon 3: Goals (30,000 ft) ✅
```typescript
goals {
    ...common_fields,
    visionId: uuid references visions(id) on delete cascade,
    status: enum('active', 'achieved', 'archived'),
    targetDate: timestamp with time zone // 1-2 year timeframe
}
```
- Medium-term objectives
- Unique name per user
- Indexed by target date

### Horizon 2: Areas (20,000 ft) ✅
```typescript
areas {
    ...common_fields,
    goalId: uuid references goals(id) on delete cascade,
    status: enum('active', 'archived', 'evergreen')
}
```
- Key life/work domains
- Unique name per user
- No target date needed

### Horizon 1: Projects (10,000 ft) ✅
```typescript
projects {
    ...common_fields,
    areaId: uuid references areas(id) on delete cascade,
    status: enum('active', 'completed', 'archived'),
    targetDate: timestamp with time zone optional
}
```
- Specific outcomes
- Unique name per user
- Optional target date

### Ground: Tasks (Runway) ✅
```typescript
tasks {
    ...common_fields,
    projectId: uuid references projects(id) on delete cascade,
    status: enum('active', 'completed'),
    dueDate: timestamp with time zone optional
}
```
- Next physical actions
- Unique name per user
- Optional due date

## Database Design

### Indexes ✅
Each entity has the following indexes:
- Primary key on `id`
- Foreign key index on `userId`
- Foreign key index on parent entity id (e.g., `purposeId`, `visionId`, etc.)
- Status index for filtering
- Date index where applicable (target/due dates)
- Unique compound index on `(userId, name)` for name uniqueness per user

### Cascading Deletes ✅
All foreign key relationships use `ON DELETE CASCADE` to maintain referential integrity:
- Deleting a user deletes all their entities
- Deleting a parent entity deletes all its children

## Validation Rules ✅

### Common Rules (All Entities)
- Name: Required, 3-100 characters
- Description: Optional, no length limit
- User must be authenticated
- Names must be unique per user within same level
- Parent entity must exist and be active
- Target dates must be in future when provided

### Status Transitions ✅
- Purpose: active ↔ archived
- Vision: active → achieved → archived
- Goals: active → achieved → archived
- Areas: active ↔ archived, active → evergreen
- Projects: active → completed → archived
- Tasks: active → completed

## Database Management ✅

### Development Workflow
The database management script (`dev.sh`) provides a complete development workflow:
1. Clean up existing resources (containers, volumes)
2. Start fresh PostgreSQL container
3. Wait for database readiness
4. Generate schema if needed
5. Run migrations
6. Seed sample data
7. Error handling and cleanup

### Sample Data Structure
The seed script provides a complete example of the GTD hierarchy:
1. Test User
2. Purpose: "Live a balanced and fulfilling life"
3. Vision: "5-Year Vision 2029"
4. Goal: "Master Software Development"
5. Area: "Full-Stack Development"
6. Project: "Build Personal Project Portfolio"
7. Tasks:
   - Setup Development Environment (completed)
   - Learn Next.js and Drizzle (active)
   - Implement Authentication (active)

### Development Commands
```bash
# Full database setup (clean, start, migrate, seed)
npm run db:start

# Individual commands
npm run db:generate  # Generate schema
npm run db:push     # Run migrations
npm run db:seed     # Seed data
npm run db:studio   # Open Drizzle Studio
```

## UI Components

### Entity Management
Each entity type gets:
1. Creation/Edit form
2. List view with hierarchy
3. Status management
4. Parent entity selector
5. Description markdown support

### Navigation
1. Breadcrumb trail showing hierarchy
2. Quick-add functionality
3. Status filters
4. Search capability
5. Hierarchy explorer

## Success Metrics
1. Complete hierarchy implementation ✅
2. Sub-200ms response times
3. Clear parent-child relationships ✅
4. Intuitive status workflows ✅
5. Proper data isolation ✅
6. Sample data seeding ✅

## Future Enhancements (Deferred)
1. Rich text descriptions
2. File attachments
3. Collaboration features
4. Mobile apps
5. API access