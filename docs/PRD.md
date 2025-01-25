# Aerith Ingestion MVP Product Requirements Document

## Primary Goal

Create a complete GTD (Getting Things Done) implementation covering all Horizons of Focus, with a modern web interface.

## Core Entities

### Common Entity Pattern
All entities share base properties:
```typescript
{
    id: text primary key,
    userId: text references users(id),
    parentId: text references parent_entity(id),
    name: text not null,
    description: text,
    status: specific_enum,
    targetDate: timestamp optional,
    createdAt: timestamp,
    updatedAt: timestamp
}
```

### Horizon 5: Purpose & Principles (50,000 ft)
```typescript
purposes {
    ...common_fields,
    status: enum('active', 'archived')
}
```
- Life purpose and core values
- No parent entity
- No target date

### Horizon 4: Vision (40,000 ft)
```typescript
visions {
    ...common_fields,
    purposeId: text references purposes(id),
    status: enum('active', 'achieved', 'archived'),
    targetDate: timestamp // 3-5 year timeframe
}
```
- Long-term outcomes

### Horizon 3: Goals (30,000 ft)
```typescript
goals {
    ...common_fields,
    visionId: text references visions(id),
    status: enum('active', 'achieved', 'archived'),
    targetDate: timestamp // 1-2 year timeframe
}
```
- Medium-term objectives

### Horizon 2: Areas (20,000 ft)
```typescript
areas {
    ...common_fields,
    goalId: text references goals(id),
    status: enum('active', 'archived', 'evergreen')
}
```
- Key life/work domains

### Horizon 1: Projects (10,000 ft)
```typescript
projects {
    ...common_fields,
    areaId: text references areas(id),
    status: enum('active', 'completed', 'archived'),
    targetDate: timestamp optional
}
```
- Specific outcomes

### Ground: Tasks (Runway)
```typescript
tasks {
    ...common_fields,
    projectId: text references projects(id),
    status: enum('active', 'completed'),
    dueDate: timestamp optional
}
```
- Next physical actions

## Validation Rules

### Common Rules (All Entities)
- Name: Required, 3-100 characters
- Description: Optional, max 500 characters
- User must be authenticated
- Names must be unique per user within same level
- Parent entity must exist and be active
- Target dates must be in future when provided

### Status Transitions
- Purpose: active ↔ archived
- Vision: active → achieved → archived
- Goals: active → achieved → archived
- Areas: active ↔ archived, active → evergreen
- Projects: active → completed → archived
- Tasks: active → completed

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
1. Complete hierarchy implementation
2. Sub-200ms response times
3. Clear parent-child relationships
4. Intuitive status workflows
5. Proper data isolation

## Future Enhancements (Deferred)
1. Rich text descriptions
2. File attachments
3. Collaboration features
4. Mobile apps
5. API access