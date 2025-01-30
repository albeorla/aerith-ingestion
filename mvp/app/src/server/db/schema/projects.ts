import { relations, sql } from "drizzle-orm";
import {
  boolean,
  index,
  text,
  timestamp,
  uniqueIndex,
  uuid,
  varchar,
} from "drizzle-orm/pg-core";
import { areas } from "./areas";
import { tasks } from "./tasks";
import { users } from "./users";
import { createTable } from "./utils";

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
    dueDate: timestamp("due_date", { withTimezone: true }),
    isActive: boolean("is_active").default(true),
  },
  (table) => ({
    userIdIdx: index("project_user_id_idx").on(table.userId),
    areaIdIdx: index("project_area_id_idx").on(table.areaId),
    statusIdx: index("project_status_idx").on(table.status),
    targetDateIdx: index("project_target_date_idx").on(table.targetDate),
    uniqueNamePerUser: uniqueIndex("project_unique_name_per_area_idx").on(
      table.areaId,
      table.name,
    ),
  }),
);

export const projectsRelations = relations(projects, ({ one, many }) => ({
  area: one(areas, {
    fields: [projects.areaId],
    references: [areas.id],
  }),
  tasks: many(tasks),
}));
