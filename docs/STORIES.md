# MVP Development Stories - Current Sprint

## Completed
1. ✅ Authentication Setup
   - Discord OAuth integration
   - User session management
   - Environment configuration
   - Database tables for auth

2. ✅ Database Infrastructure
   - PostgreSQL setup
   - Drizzle ORM configuration
   - Basic schema setup

## Current Sprint Goals: Full GTD Hierarchy

### 1. Implement All GTD Models

#### 1.1 Core Entity Schema Setup
```typescript
// All entities follow similar pattern:
{
    id: text primary key,
    userId: text references users(id),
    parentId: text references parent_entity(id), // Specific to each level
    name: text not null,
    description: text,
    status: enum(...), // Specific to each level
    targetDate: timestamp, // For time-bound entities
    createdAt: timestamp,
    updatedAt: timestamp
}
```

Tasks:
- [ ] Create Drizzle schemas for all levels:
  - Purposes (50k ft)
  - Visions (40k ft)
  - Goals (30k ft)
  - Areas (20k ft)
  - Projects (10k ft)
  - Tasks (Ground)
- [ ] Add tRPC router for each entity
- [ ] Implement basic CRUD operations
- [ ] Add validation layer

### 2. Basic UI Components

#### 2.1 Entity Management Interface
For each entity type:
- [ ] Create form component
- [ ] Add list view with hierarchy
- [ ] Implement status toggles
- [ ] Add error handling
- [ ] Parent entity selector

#### 2.2 Hierarchy Navigation
- [ ] Implement breadcrumb navigation
- [ ] Add hierarchy view
- [ ] Create quick-add functionality
- [ ] Add filtering by status

## Testing Priority
1. Schema validation
2. CRUD operations
3. Status transitions
4. Hierarchical integrity
5. User isolation 