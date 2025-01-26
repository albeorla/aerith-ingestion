import { relations, sql } from "drizzle-orm";
import {
  index,
  pgTableCreator,
  text,
  timestamp,
  uuid,
  varchar,
  uniqueIndex,
} from "drizzle-orm/pg-core";
import { users } from "../schema";
import { areas } from "./goals-areas";

export const createTable = pgTableCreator((name) => `app_${name}`);

export const projects = createTable(
  "project",
  {
    id: uuid("id").primaryKey().defaultRandom(),
    userId: varchar("user_id", { length: 255 })
      .notNull()
      .references(() => users.id, { onDelete: "cascade" }),
    areaId: uuid("area_id")
      .notNull()
      .references(() => areas.id, { onDelete: "cascade" }),
    name: varchar("name", { length: 100 }).notNull(),
    description: text("description"),
    status: varchar("status", { length: 20 })
      .notNull()
      .default("active")
      .$type<"active" | "completed" | "archived">(),
    targetDate: timestamp("target_date", { withTimezone: true }),
    createdAt: timestamp("created_at", { withTimezone: true })
      .default(sql`CURRENT_TIMESTAMP`)
      .notNull(),
    updatedAt: timestamp("updated_at", { withTimezone: true })
      .default(sql`CURRENT_TIMESTAMP`)
      .notNull(),
  },
  (table) => ({
    userIdIdx: index("project_user_id_idx").on(table.userId),
    areaIdIdx: index("project_area_id_idx").on(table.areaId),
    statusIdx: index("project_status_idx").on(table.status),
    targetDateIdx: index("project_target_date_idx").on(table.targetDate),
    uniqueNamePerUser: uniqueIndex("project_unique_name_per_user_idx").on(
      table.userId,
      table.name
    ),
  })
);

export const tasks = createTable(
  "task",
  {
    id: uuid("id").primaryKey().defaultRandom(),
    userId: varchar("user_id", { length: 255 })
      .notNull()
      .references(() => users.id, { onDelete: "cascade" }),
    projectId: uuid("project_id")
      .notNull()
      .references(() => projects.id, { onDelete: "cascade" }),
    name: varchar("name", { length: 100 }).notNull(),
    description: text("description"),
    status: varchar("status", { length: 20 })
      .notNull()
      .default("active")
      .$type<"active" | "completed">(),
    dueDate: timestamp("due_date", { withTimezone: true }),
    createdAt: timestamp("created_at", { withTimezone: true })
      .default(sql`CURRENT_TIMESTAMP`)
      .notNull(),
    updatedAt: timestamp("updated_at", { withTimezone: true })
      .default(sql`CURRENT_TIMESTAMP`)
      .notNull(),
  },
  (table) => ({
    userIdIdx: index("task_user_id_idx").on(table.userId),
    projectIdIdx: index("task_project_id_idx").on(table.projectId),
    statusIdx: index("task_status_idx").on(table.status),
    dueDateIdx: index("task_due_date_idx").on(table.dueDate),
    uniqueNamePerUser: uniqueIndex("task_unique_name_per_user_idx").on(
      table.userId,
      table.name
    ),
  })
);

export const projectsRelations = relations(projects, ({ one, many }) => ({
  area: one(areas, {
    fields: [projects.areaId],
    references: [areas.id],
  }),
  tasks: many(tasks),
}));

export const tasksRelations = relations(tasks, ({ one }) => ({
  project: one(projects, {
    fields: [tasks.projectId],
    references: [projects.id],
  }),
})); 